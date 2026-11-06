(function () {
  var header = document.querySelector('.site-header');
  if (!header) return;

  var nav = header.querySelector('.site-nav');
  var toggle;
  var mobile = window.matchMedia('(max-width: 768px)');
  if (nav) {
    nav.id = nav.id || 'site-navigation';
    nav.setAttribute('aria-label', document.documentElement.lang === 'fr' ? 'Navigation principale' : 'Main navigation');
    toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'nav-toggle';
    toggle.textContent = 'Menu';
    toggle.setAttribute('aria-controls', nav.id);
    toggle.setAttribute('aria-expanded', 'false');
    header.insertBefore(toggle, nav);
    header.classList.add('nav-ready');

    function setMenu(open, restoreFocus) {
      header.classList.toggle('nav-open', open);
      toggle.setAttribute('aria-expanded', String(open));
      if (open) header.classList.remove('nav-hidden');
      if (restoreFocus) toggle.focus({ preventScroll: true });
    }

    toggle.addEventListener('click', function () {
      setMenu(toggle.getAttribute('aria-expanded') !== 'true', false);
    });
    header.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && header.classList.contains('nav-open')) {
        setMenu(false, true);
      }
    });
    nav.addEventListener('click', function (event) {
      if (mobile.matches && event.target.closest('a')) setMenu(false, true);
    });
    document.addEventListener('pointerdown', function (event) {
      if (!header.contains(event.target)) setMenu(false, false);
    });
    mobile.addEventListener('change', function () { setMenu(false, false); });
    header.addEventListener('focusin', function () { header.classList.remove('nav-hidden'); });
  }

  var lastScroll    = 0;
  var atTopLimit    = 60;   // below this scroll position → transparent
  var hideThreshold = 120;  // above this, hiding on downscroll kicks in
  var deadZone      = 4;    // ignore micro-jitter

  function update() {
    var y = window.pageYOffset;
    header.classList.toggle('scrolled', y > 24);

    if (y < atTopLimit) {
      header.classList.add('at-top');
      header.classList.remove('nav-hidden');
    } else {
      header.classList.remove('at-top');
      if (header.classList.contains('nav-open') || header.contains(document.activeElement)) {
        header.classList.remove('nav-hidden');
      } else if (y > hideThreshold && y > lastScroll + deadZone) {
        header.classList.add('nav-hidden');
      } else if (y < lastScroll - deadZone) {
        header.classList.remove('nav-hidden');
      }
    }

    lastScroll = y;
  }

  update();
  window.addEventListener('scroll', update, { passive: true });
})();
