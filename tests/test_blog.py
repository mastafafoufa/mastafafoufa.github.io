from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import blog


class BlogPublishingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="mhf-blog-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for relative in ("templates", "assets/js", "content/blog/en", "content/blog/fr", "en/blog", "fr/blog"):
            self.root.joinpath(*relative.split("/")).mkdir(parents=True)
        for name in ("blog-index.html", "blog-post.html"):
            shutil.copyfile(blog.ROOT / "templates" / name, self.root / "templates" / name)
        shutil.copyfile(blog.ROOT / "assets" / "js" / "article-nav.js", self.root / "assets" / "js" / "article-nav.js")
        shutil.copyfile(blog.ROOT / "sitemap.xml", self.root / "sitemap.xml")

    def post(self, language, slug, extra="", body="A useful **independent** essay."):
        source = self.root / "content" / "blog" / language / f"{slug}.md"
        source.write_text(
            f'---\ntitle: "{slug}"\ndate: "2026-11-06"\nsummary: "An independent essay."\ncategory: technology\ndraft: false\n{extra}---\n\n{body}\n',
            encoding="utf-8",
        )
        return source

    def test_single_language_publication_and_draft_preview(self):
        self.post("fr", "francais-seulement")
        draft = blog.new_post(self.root, "en", "An English draft", summary="Not published yet")
        blog.build(self.root, preview=True)
        french = (self.root / "fr" / "blog" / "francais-seulement.html").read_text(encoding="utf-8")
        self.assertIn("<strong>independent</strong>", french)
        self.assertNotIn('rel="alternate" hreflang="en"', french)
        self.assertIn('href="/en/blog/"', french)
        self.assertFalse((self.root / "en" / "blog" / "francais-seulement.html").exists())
        self.assertFalse((self.root / "en" / "blog" / f"{draft.stem}.html").exists())
        self.assertNotIn("francais-seulement", (self.root / "en" / "blog" / "index.html").read_text(encoding="utf-8"))
        self.assertIn("francais-seulement", (self.root / "fr" / "blog" / "index.html").read_text(encoding="utf-8"))
        sitemap = (self.root / "sitemap.xml").read_text(encoding="utf-8")
        self.assertIn("/fr/blog/francais-seulement.html", sitemap)
        self.assertNotIn("/en/blog/francais-seulement.html", sitemap)
        self.assertNotIn(draft.stem, sitemap)
        preview = (self.root / "_preview" / "en" / "blog" / f"{draft.stem}.html").read_text(encoding="utf-8")
        self.assertIn('name="robots" content="noindex"', preview)
        self.assertIn("Draft preview", preview)
        self.assertNotIn("BlogPosting", preview)
        self.assertEqual(blog.build(self.root, check=True), [])

    def test_english_only_publication_does_not_create_french_copy(self):
        self.post("en", "english-only")
        blog.build(self.root)
        self.assertTrue((self.root / "en" / "blog" / "english-only.html").exists())
        self.assertFalse((self.root / "fr" / "blog" / "english-only.html").exists())
        english = (self.root / "en" / "blog" / "index.html").read_text(encoding="utf-8")
        self.assertIn('aria-current="page">English</a>', english)
        self.assertIn('href="/fr/blog/" lang="fr"', english)
        self.assertNotIn("english-only", (self.root / "fr" / "blog" / "index.html").read_text(encoding="utf-8"))

    def test_translations_are_explicit_and_missing_translations_fail_before_writing(self):
        source = self.post("en", "original", 'translation: fr/traduction\n')
        with self.assertRaisesRegex(ValueError, "published post in the other language"):
            blog.build(self.root)
        self.assertFalse((self.root / "en" / "blog" / "original.html").exists())
        self.post("fr", "traduction")
        blog.build(self.root)
        original = (self.root / "en" / "blog" / "original.html").read_text(encoding="utf-8")
        translation = (self.root / "fr" / "blog" / "traduction.html").read_text(encoding="utf-8")
        self.assertIn('hreflang="fr" href="https://mastafafoufa.com/fr/blog/traduction.html"', original)
        self.assertIn('hreflang="en" href="https://mastafafoufa.com/en/blog/original.html"', translation)
        self.assertIn("Lire cet article en français", original)
        self.assertIn("Read this article in English", translation)
        source.write_text(source.read_text(encoding="utf-8").replace("draft: false", "draft: true"), encoding="utf-8")
        blog.build(self.root)
        retired = (self.root / "en" / "blog" / "original.html").read_text(encoding="utf-8")
        self.assertIn('http-equiv="refresh"', retired)
        self.assertNotIn("An independent essay", retired)
        self.assertNotIn("original.html", (self.root / "assets" / "js" / "article-nav.js").read_text(encoding="utf-8"))

    def test_empty_publication_and_duplicate_draft_are_rejected(self):
        self.post("fr", "vide", body="<!-- Empty draft -->")
        with self.assertRaisesRegex(ValueError, "empty body"):
            blog.build(self.root)
        self.assertFalse((self.root / "fr" / "blog" / "vide.html").exists())
        blog.new_post(self.root, "fr", "Un brouillon")
        with self.assertRaises(FileExistsError):
            blog.new_post(self.root, "fr", "Un brouillon")

    def test_reserved_routes_and_misplaced_sources_cannot_replace_or_hide_the_blog(self):
        for slug in ("index", "con"):
            with self.assertRaisesRegex(ValueError, "reserved"):
                blog.new_post(self.root, "en", "Reserved route", slug=slug)
        self.post("fr", "index")
        with self.assertRaisesRegex(ValueError, "reserved"):
            blog.build(self.root)
        self.assertFalse((self.root / "fr" / "blog" / "index.html").exists())
        (self.root / "content" / "blog" / "fr" / "index.md").unlink()
        source = self.post("en", "misplaced")
        source.rename(self.root / "content" / "blog" / source.name)
        with self.assertRaisesRegex(ValueError, "directly"):
            blog.build(self.root)
        self.assertFalse((self.root / "en" / "blog" / "index.html").exists())


if __name__ == "__main__":
    unittest.main()
