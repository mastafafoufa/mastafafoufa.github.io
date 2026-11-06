(function () {
  // BEGIN GENERATED POSTS
  var fr = [
  {
    "url": "/fr/blog/passivite-organique-power-users.html",
    "title": "De la commande \u00e0 la consultation"
  },
  {
    "url": "/fr/blog/pourquoi-paresse-de-penser.html",
    "title": "Le tiret cadratin et la fin de l\u2019intention"
  },
  {
    "url": "/fr/blog/raccourcis-cognitifs.html",
    "title": "Ce que les LLMs nous apprennent sur nos raccourcis cognitifs"
  },
  {
    "url": "/fr/blog/eloge-de-la-friction.html",
    "title": "L\u2019\u00e9loge de la friction"
  },
  {
    "url": "/fr/blog/poids-du-silence.html",
    "title": "Le poids du silence"
  }
];

  var en = [
  {
    "url": "/en/blog/laziness-of-thinking-book.html",
    "title": "The em dash and the end of intention"
  },
  {
    "url": "/en/blog/llm-mental-laziness.html",
    "title": "What LLMs taught me about human mental laziness"
  },
  {
    "url": "/en/blog/designing-for-friction.html",
    "title": "Designing for friction"
  }
];
  // END GENERATED POSTS

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
