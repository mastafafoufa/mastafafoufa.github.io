import argparse
from dataclasses import dataclass
from datetime import date
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from string import Template
import sys
import unicodedata
import xml.etree.ElementTree as ET

import markdown
import yaml

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://mastafafoufa.com"
MARKER = "<!-- Generated blog page; edit Markdown and run blog.ps1 build. -->"
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
RESERVED_SLUGS = {"index", "con", "prn", "aux", "nul"} | {
    f"{prefix}{number}" for prefix in ("com", "lpt") for number in range(1, 10)
}
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
XHTML_NS = "http://www.w3.org/1999/xhtml"
LABELS = {
    "en": {
        "home": "Home", "press": "Press", "heading": "Writing",
        "eyebrow": "Essays & Reflections", "read": "Read",
        "description": "On artificial intelligence, cognition, philosophy of technology, and the questions that don't fit in a research paper.",
        "picker": "Choose a reading language",
        "note": "Two independent collections. Posts are written in English or French; not every post has a translation.",
        "technology": "Technology & Cognition", "reflections": "Philosophy & Reflections",
        "back": "← Back to Blog", "working": "Working note",
        "draft": "Draft preview — not published",
        "empty": "No posts published in this language yet.",
        "months": ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"),
    },
    "fr": {
        "home": "Accueil", "press": "Presse", "heading": "Le Blog",
        "eyebrow": "Écrits & Réflexions", "read": "Lire",
        "description": "Sur l'intelligence artificielle, la cognition, la philosophie de la technique, et les questions qui ne tiennent pas dans un article de recherche.",
        "picker": "Choisir la langue de lecture",
        "note": "Deux collections indépendantes. J’écris en français ou en anglais ; chaque article n’a pas nécessairement de traduction.",
        "technology": "Technologie & Cognition", "reflections": "Philosophie & Pensées",
        "back": "← Retour au Blog", "working": "Note en cours",
        "draft": "Aperçu du brouillon — non publié",
        "empty": "Aucun article publié dans cette langue pour le moment.",
        "months": ("janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"),
    },
}


class PlainText(HTMLParser):
    def __init__(self, value):
        super().__init__()
        self.parts = []
        self.feed(value)

    def handle_data(self, data):
        self.parts.append(data)

    @property
    def text(self):
        return " ".join(" ".join(self.parts).split())


@dataclass(frozen=True)
class Post:
    language: str
    slug: str
    title: str
    summary: str
    published_on: date
    category: str
    draft: bool
    working_note: bool
    short_title: str
    translation: str | None
    body: str

    @property
    def id(self):
        return f"{self.language}/{self.slug}"

    @property
    def route(self):
        return f"/{self.language}/blog/{self.slug}.html"


def read_post(source):
    language = source.parent.name
    slug = source.stem
    if language not in LABELS or not SLUG.fullmatch(slug) or slug in RESERVED_SLUGS:
        raise ValueError(f"{source}: use an en/fr folder and a lowercase, hyphenated filename; index and device names are reserved.")
    text = source.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---(?:\n|$)", text, re.S)
    if not match:
        raise ValueError(f"{source}: missing YAML front matter.")
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        raise ValueError(f"{source}: front matter must contain named fields.")
    draft = data.get("draft", False)
    working = data.get("working_note", False)
    if not isinstance(draft, bool) or not isinstance(working, bool):
        raise ValueError(f"{source}: draft and working_note must be true or false.")
    title, summary = data.get("title"), data.get("summary", "")
    if not isinstance(title, str) or not title.strip():
        raise ValueError(f"{source}: title must be nonempty text.")
    if not isinstance(summary, str) or (not draft and not summary.strip()):
        raise ValueError(f"{source}: published posts need a nonempty summary.")
    category = data.get("category", "technology")
    if category not in ("technology", "reflections"):
        raise ValueError(f"{source}: category must be technology or reflections.")
    published_on = data.get("date")
    if isinstance(published_on, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", published_on):
        published_on = date.fromisoformat(published_on)
    if type(published_on) is not date:
        raise ValueError(f"{source}: date must use YYYY-MM-DD.")
    short_title = data.get("short_title", title)
    if not isinstance(short_title, str) or not short_title.strip():
        raise ValueError(f"{source}: short_title must be nonempty text.")
    translation = data.get("translation")
    if translation is not None and (
        not isinstance(translation, str) or
        not re.fullmatch(r"(en|fr)/[a-z0-9]+(?:-[a-z0-9]+)*", translation)
    ):
        raise ValueError(f"{source}: translation must be an existing post ID such as fr/mon-article.")
    body = markdown.markdown(text[match.end():], extensions=["extra", "sane_lists"], output_format="html5")
    if not draft and not PlainText(body).text:
        raise ValueError(f"{source}: a published post cannot have an empty body.")
    return Post(language, slug, title, summary, published_on, category, draft,
                working, short_title, translation, body)


def display_date(post):
    month = LABELS[post.language]["months"][post.published_on.month - 1]
    if post.language == "fr":
        return f"{post.published_on.day} {month} {post.published_on.year}"
    return f"{month} {post.published_on.day}, {post.published_on.year}"


def translation_pairs(posts):
    published = {post.id: post for post in posts if not post.draft}
    pairs = {}
    for post in published.values():
        if post.translation is None:
            continue
        target = published.get(post.translation)
        if target is None or target.language == post.language:
            raise ValueError(f"{post.id}: translation must reference a published post in the other language.")
        for current, other in ((post.id, target.id), (target.id, post.id)):
            if current in pairs and pairs[current] != other:
                raise ValueError(f"{current}: conflicting translation links.")
            pairs[current] = other
    return {key: published[value] for key, value in pairs.items()}


def language_picker(language):
    links = []
    for target, label in (("en", "English"), ("fr", "Français")):
        current = ' aria-current="page"' if target == language else ""
        links.append(f'<a class="btn-outline" href="/{target}/blog/" lang="{target}" hreflang="{target}"{current}>{label}</a>')
    return f'<nav class="blog-language-switch" aria-label="{escape(LABELS[language]["picker"])}">' + "".join(links) + "</nav>"


def render_index(root, language, posts):
    labels = LABELS[language]
    other = "fr" if language == "en" else "en"
    groups = []
    for category in ("technology", "reflections"):
        cards = []
        for post in posts:
            if post.category != category:
                continue
            working = f' &nbsp;·&nbsp; {escape(labels["working"])}' if post.working_note else ""
            cards.append(f"""        <article class="post-preview">
          <div class="post-date"><time datetime="{post.published_on.isoformat()}">{escape(display_date(post))}</time>{working}</div>
          <h2><a href="{post.route}">{escape(post.title)}</a></h2>
          <p class="post-excerpt">{escape(post.summary)}</p>
          <a href="{post.route}" class="post-read-more">{labels["read"]} &nbsp;→</a>
        </article>""")
        if cards:
            groups.append(f'      <section>\n        <h2 class="category-label">{escape(labels[category])}</h2>\n' + "\n".join(cards) + "\n      </section>")
    content = "\n".join(groups) if groups else f'<p>{escape(labels["empty"])}</p>'
    return MARKER + "\n" + Template((root / "templates" / "blog-index.html").read_text(encoding="utf-8")).substitute(
        lang=language, other_lang=other, other_language="Français" if other == "fr" else "English",
        home_label=labels["home"], press_label=labels["press"], heading=escape(labels["heading"]),
        eyebrow=escape(labels["eyebrow"]), page_title="Blog — Mastafa Foufa | MHF",
        canonical=f"{SITE}/{language}/blog/", description=escape(labels["description"], quote=True),
        language_picker=language_picker(language), language_note=escape(labels["note"]),
        column_class="single-category" if len(groups) < 2 else "", post_groups=content,
    )


def render_post(root, post, translation=None, preview=False):
    labels = LABELS[post.language]
    other = "fr" if post.language == "en" else "en"
    metadata = []
    link = ""
    if preview:
        metadata.append('<meta name="robots" content="noindex">')
    else:
        metadata.extend((
            f'<link rel="canonical" href="{SITE}{post.route}">',
            f'<link rel="alternate" hreflang="{post.language}" href="{SITE}{post.route}">',
        ))
        if translation:
            metadata.append(f'<link rel="alternate" hreflang="{translation.language}" href="{SITE}{translation.route}">')
            label = "Lire cet article en français →" if translation.language == "fr" else "Read this article in English →"
            link = f'<p class="article-translation"><a href="{translation.route}" hreflang="{translation.language}" lang="{translation.language}">{label}</a></p>'
        schema = {
            "@context": "https://schema.org", "@type": "BlogPosting", "headline": post.title,
            "datePublished": post.published_on.isoformat(),
            "author": {"@type": "Person", "name": "Mastafa Foufa"},
            "publisher": {"@type": "Organization", "name": "mastafafoufa.com"},
            "inLanguage": post.language, "url": SITE + post.route, "description": post.summary,
        }
        encoded = json.dumps(schema, ensure_ascii=True).replace("<", "\\u003c")
        metadata.append(f'<script type="application/ld+json">{encoded}</script>')
    return MARKER + "\n" + Template((root / "templates" / "blog-post.html").read_text(encoding="utf-8")).substitute(
        lang=post.language, other_lang=other, title=escape(post.title),
        page_title=escape(post.title + " | MHF"), summary=escape(post.summary, quote=True),
        metadata="\n  ".join(metadata), home_label=labels["home"],
        other_posts_label="Articles en français" if other == "fr" else "English posts",
        back_label=labels["back"], category_label=escape(labels[post.category]),
        date=post.published_on.isoformat(), display_date=escape(display_date(post)),
        working_note=f' &nbsp;·&nbsp; {labels["working"]}' if post.working_note else "",
        draft_notice=f'<p class="draft-notice">{labels["draft"]}</p>' if preview else "",
        translation_link=link, article_body=post.body,
        article_nav_script='<script src="/assets/js/article-nav.js"></script>' if not preview else "",
    )


def render_redirect(language, route=None):
    route = route or f"/{language}/blog/"
    label = "Browse published posts" if language == "en" else "Parcourir les articles publiés"
    return f"""{MARKER}
<!DOCTYPE html>
<html lang="{language}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Blog — Mastafa Foufa</title>
  <meta name="robots" content="noindex">
  <link rel="canonical" href="{SITE}{route}">
  <meta http-equiv="refresh" content="0; url={route}">
</head>
<body><p><a href="{route}">{label}</a>.</p></body>
</html>
"""


def render_sitemap(root, published, pairs):
    ET.register_namespace("", SITEMAP_NS)
    ET.register_namespace("xhtml", XHTML_NS)
    tree = ET.parse(root / "sitemap.xml")
    urlset = tree.getroot()
    if urlset.tag != f"{{{SITEMAP_NS}}}urlset":
        raise ValueError("sitemap.xml must contain a standard sitemap urlset.")
    for node in list(urlset):
        loc = node.find(f"{{{SITEMAP_NS}}}loc")
        if loc is not None and re.fullmatch(re.escape(SITE) + r"/(en|fr)/blog/[^/]+\.html", loc.text or ""):
            urlset.remove(node)
    for post in published:
        node = ET.SubElement(urlset, f"{{{SITEMAP_NS}}}url")
        ET.SubElement(node, f"{{{SITEMAP_NS}}}loc").text = SITE + post.route
        for alternate in (post, pairs.get(post.id)):
            if alternate:
                ET.SubElement(node, f"{{{XHTML_NS}}}link", {
                    "rel": "alternate", "hreflang": alternate.language, "href": SITE + alternate.route,
                })
        ET.SubElement(node, f"{{{SITEMAP_NS}}}changefreq").text = "yearly"
        ET.SubElement(node, f"{{{SITEMAP_NS}}}priority").text = "0.8"
    ET.indent(urlset, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(urlset, encoding="unicode") + "\n"


def build_outputs(root, preview=False):
    source_root = root / "content" / "blog"
    if not source_root.is_dir():
        raise ValueError("Missing content/blog Markdown sources.")
    sources = sorted(source_root.rglob("*.md"))
    for source in sources:
        parts = source.relative_to(source_root).parts
        if len(parts) != 2 or parts[0] not in LABELS:
            raise ValueError(f"{source}: posts must live directly in content/blog/en or content/blog/fr.")
    posts = [read_post(source) for source in sources]
    posts.sort(key=lambda post: (post.published_on, post.slug), reverse=True)
    published = [post for post in posts if not post.draft]
    pairs = translation_pairs(posts)
    outputs = {}
    for language in LABELS:
        directory = root / language / "blog"
        outputs[directory / "index.html"] = render_index(root, language, [post for post in published if post.language == language])
        for existing in directory.glob("*.html"):
            if existing.name == "index.html":
                continue
            text = existing.read_text(encoding="utf-8")
            post_id = f"{language}/{existing.stem}"
            if MARKER in text and not any(post.id == post_id for post in published):
                outputs[existing] = render_redirect(language)
            elif 'class="article-body"' in text and MARKER not in text and not any(post.id == post_id for post in posts):
                raise ValueError(f"{existing}: migrate this HTML article to Markdown before rebuilding.")
    for post in posts:
        if not post.draft:
            outputs[root / post.language / "blog" / f"{post.slug}.html"] = render_post(root, post, pairs.get(post.id))
        elif preview:
            outputs[root / "_preview" / post.language / "blog" / f"{post.slug}.html"] = render_post(root, post, preview=True)
    nav_file = root / "assets" / "js" / "article-nav.js"
    nav = nav_file.read_text(encoding="utf-8")
    definitions = []
    for language in ("fr", "en"):
        entries = [{"url": post.route, "title": escape(post.short_title)} for post in published if post.language == language]
        definitions.append(f"  var {language} = " + json.dumps(entries, ensure_ascii=True, indent=2) + ";")
    block = "  // BEGIN GENERATED POSTS\n" + "\n\n".join(definitions) + "\n  // END GENERATED POSTS"
    nav, count = re.subn(r"  // BEGIN GENERATED POSTS.*?  // END GENERATED POSTS", lambda match: block, nav, flags=re.S)
    if count != 1:
        raise ValueError("article-nav.js must contain exactly one generated-posts marker pair.")
    outputs[nav_file] = nav
    outputs[root / "sitemap.xml"] = render_sitemap(root, published, pairs)
    return outputs


def build(root=ROOT, preview=False, check=False):
    outputs = build_outputs(root, preview)
    changed = [target for target, text in outputs.items() if not target.exists() or target.read_text(encoding="utf-8") != text]
    if check and changed:
        raise ValueError("Generated blog files are out of date. Run .\\blog.ps1 build:\n" +
                         "\n".join(str(target.relative_to(root)) for target in changed))
    if not check:
        for target in changed:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(outputs[target], encoding="utf-8", newline="\n")
    return changed


def new_post(root, language, title, slug=None, summary="", category="technology", published_on=None):
    if language not in LABELS or not title.strip() or category not in ("technology", "reflections"):
        raise ValueError("Choose en/fr, a nonempty title, and a supported category.")
    if slug is None:
        plain = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii").lower()
        slug = re.sub(r"[^a-z0-9]+", "-", plain).strip("-")
    if not SLUG.fullmatch(slug) or slug in RESERVED_SLUGS:
        raise ValueError("Use a lowercase, hyphenated slug; index and device names are reserved.")
    published_on = date.fromisoformat(published_on) if published_on else date.today()
    source = root / "content" / "blog" / language / f"{slug}.md"
    data = {
        "title": title, "date": published_on.isoformat(), "summary": summary,
        "category": category, "draft": True,
    }
    text = "---\n" + yaml.safe_dump(data, allow_unicode=True, sort_keys=False) + "---\n\n<!-- Write your post here. Set draft: false when ready. -->\n"
    source.parent.mkdir(parents=True, exist_ok=True)
    with source.open("x", encoding="utf-8", newline="\n") as output:
        output.write(text)
    return source


def main():
    parser = argparse.ArgumentParser(description="Write and publish independent English or French Markdown posts.")
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("new", help="Create one unpublished Markdown draft.")
    create.add_argument("--lang", choices=LABELS, required=True)
    create.add_argument("--title", required=True)
    create.add_argument("--slug")
    create.add_argument("--summary", default="")
    create.add_argument("--category", choices=("technology", "reflections"), default="technology")
    create.add_argument("--date")
    rebuild = commands.add_parser("build", help="Generate static pages, listings, navigation and sitemap.")
    rebuild.add_argument("--preview-drafts", action="store_true")
    commands.add_parser("check", help="Check that generated publication files match the Markdown sources.")
    args = parser.parse_args()
    try:
        if args.command == "new":
            source = new_post(ROOT, args.lang, args.title, args.slug, args.summary, args.category, args.date)
            print(f"Created {source.relative_to(ROOT)}. No translation was created.")
        else:
            changed = build(preview=getattr(args, "preview_drafts", False), check=args.command == "check")
            print(f"Blog {args.command} complete: {len(changed)} file(s) " + ("updated." if args.command == "build" else "out of date."))
            for target in changed:
                print(target.relative_to(ROOT))
    except (ValueError, OSError, yaml.YAMLError, ET.ParseError) as error:
        parser.exit(1, f"Blog error: {error}\n")


if __name__ == "__main__":
    main()
