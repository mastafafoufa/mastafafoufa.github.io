(function () {
  document.querySelectorAll('[data-news-rail]').forEach(function (section) {
    var rail = section.querySelector('.news-rail');
    var cards = Array.from(rail.querySelectorAll('.news-card'));
    if (cards.length < 2) return;

    var controls = section.querySelector('.news-controls');
    var previous = controls.querySelector('.news-previous');
    var next = controls.querySelector('.news-next');
    var position = controls.querySelector('.news-position');
    var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

    controls.hidden = false;
    rail.tabIndex = 0;
    rail.setAttribute('role', 'region');
    rail.setAttribute('aria-label', 'Featured articles, podcasts and videos');

    function currentIndex() {
      var left = rail.getBoundingClientRect().left;
      return cards.reduce(function (closest, card, index) {
        return Math.abs(card.getBoundingClientRect().left - left) <
          Math.abs(cards[closest].getBoundingClientRect().left - left) ? index : closest;
      }, 0);
    }

    function update() {
      var index = currentIndex();
      previous.disabled = index === 0;
      next.disabled = index === cards.length - 1;
      position.textContent = (index + 1) + ' / ' + cards.length;
    }

    function move(direction) {
      var index = Math.max(0, Math.min(cards.length - 1, currentIndex() + direction));
      var left = rail.scrollLeft + cards[index].getBoundingClientRect().left - rail.getBoundingClientRect().left;
      rail.scrollTo({ left: left, behavior: reducedMotion.matches ? 'instant' : 'smooth' });
    }

    previous.addEventListener('click', function () { move(-1); });
    next.addEventListener('click', function () { move(1); });
    rail.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    rail.addEventListener('keydown', function (event) {
      if (event.target !== rail || (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight')) return;
      event.preventDefault();
      move(event.key === 'ArrowLeft' ? -1 : 1);
    });
    update();
  });
})();
