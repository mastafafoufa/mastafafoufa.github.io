(function () {
  var header = document.querySelector('.site-header');
  if (!header) return;

  var lastScroll    = 0;
  var atTopLimit    = 60;   // below this scroll position → transparent
  var hideThreshold = 120;  // above this, hiding on downscroll kicks in
  var deadZone      = 4;    // ignore micro-jitter

  function update() {
    var y = window.pageYOffset;

    if (y < atTopLimit) {
      header.classList.add('at-top');
      header.classList.remove('nav-hidden');
    } else {
      header.classList.remove('at-top');
      if (y > hideThreshold && y > lastScroll + deadZone) {
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
