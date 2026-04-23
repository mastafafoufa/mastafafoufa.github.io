(function () {
  var fr = [
    { url: '/fr/blog/pourquoi-paresse-de-penser.html', title: 'Le tiret cadratin et la fin de l\u2019intention' },
    { url: '/fr/blog/raccourcis-cognitifs.html',        title: 'Ce que les LLMs nous apprennent sur nos raccourcis cognitifs' },
    { url: '/fr/blog/eloge-de-la-friction.html',        title: 'L\u2019\u00e9loge de la friction' },
    { url: '/fr/blog/crise-des-benchmarks.html',        title: 'La crise des benchmarks' },
    { url: '/fr/blog/mur-des-donnees.html',             title: 'Le mur des donn\u00e9es' },
    { url: '/fr/blog/agents-vs-copilotes.html',         title: 'De l\u2019assistant \u00e0 l\u2019agent autonome' },
    { url: '/fr/blog/open-source-vs-ferme.html',        title: 'La guerre de l\u2019open source' },
    { url: '/fr/blog/scaling-laws-vs-world-models.html',title: 'Faut-il juste \u00ab\u00a0plus de serveurs\u00a0\u00bb\u00a0?' },
    { url: '/fr/blog/vision-ellulienne.html',           title: 'Ce que je comprends de la vision ellulienne' },
    { url: '/fr/blog/dernier-homme-nietzsche.html',     title: 'Le dernier homme de Nietzsche \u00e0 l\u2019\u00e8re de la technique' },
    { url: '/fr/blog/histoire-embeddings.html',         title: 'De Word2Vec aux espaces latents des transformers' },
    { url: '/fr/blog/passivite-organique-power-users.html', title: 'De la commande \u00e0 la consultation' },
    { url: '/fr/blog/vie-jeu-resultat-serieux.html',    title: 'La vie est un jeu dont le r\u00e9sultat est s\u00e9rieux' },
    { url: '/fr/blog/poids-du-silence.html',            title: 'Le poids du silence' },
  ];

  var en = [
    { url: '/en/blog/laziness-of-thinking-book.html',   title: 'The em dash and the end of intention' },
    { url: '/en/blog/llm-mental-laziness.html',         title: 'What LLMs taught me about human mental laziness' },
    { url: '/en/blog/designing-for-friction.html',      title: 'Designing for friction' },
    { url: '/en/blog/benchmark-crisis.html',            title: 'The benchmark crisis' },
    { url: '/en/blog/data-wall.html',                   title: 'The data wall' },
    { url: '/en/blog/agents-vs-copilots.html',          title: 'From Copilot to autonomous agent' },
    { url: '/en/blog/open-source-vs-closed.html',       title: 'The open source war' },
    { url: '/en/blog/scaling-laws-vs-world-models.html',title: 'Just more servers?' },
    { url: '/en/blog/ellul-technology.html',            title: 'What Ellul understood about technology' },
    { url: '/en/blog/nietzsche-last-man.html',          title: 'Nietzsche\u2019s last man in the age of AI' },
    { url: '/en/blog/history-of-embeddings.html',       title: 'From Word2Vec to transformer latent spaces' },
  ];

  var path = window.location.pathname;
  var isFr = path.indexOf('/fr/') === 0;
  var list = isFr ? fr : en;
  var idx  = list.findIndex(function (a) { return a.url === path; });
  if (idx === -1) return;

  var footer = document.querySelector('.article-footer');
  if (!footer) return;

  var prev = list[idx - 1];
  var next = list[idx + 1];
  var prevLbl = isFr ? '\u2190 Pr\u00e9c\u00e9dent' : '\u2190 Previous';
  var nextLbl = isFr ? 'Suivant \u2192' : 'Next \u2192';

  var html = '<nav class="article-nav">';
  if (prev) {
    html += '<a href="' + prev.url + '" class="article-nav-prev">'
          + '<span class="article-nav-label">' + prevLbl + '</span>'
          + '<span class="article-nav-title">' + prev.title + '</span>'
          + '</a>';
  } else {
    html += '<span></span>';
  }
  if (next) {
    html += '<a href="' + next.url + '" class="article-nav-next">'
          + '<span class="article-nav-label">' + nextLbl + '</span>'
          + '<span class="article-nav-title">' + next.title + '</span>'
          + '</a>';
  }
  html += '</nav>';

  footer.insertAdjacentHTML('afterend', html);
})();
