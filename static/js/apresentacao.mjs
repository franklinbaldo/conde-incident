const deck = document.querySelector('.conde-deck');

if (deck) {
  const slides = Array.from(deck.querySelectorAll('.deck-slide'));
  const controls = deck.querySelector('.deck-controls');
  const steps = Array.from(controls.querySelectorAll('a'));
  const previous = controls.querySelector('[data-previous]');
  const next = controls.querySelector('[data-next]');
  const fullscreen = deck.querySelector('[data-fullscreen]');
  let current = 0;

  function showSlide(index, focus = false) {
    current = index;
    slides.forEach((slide, i) => {
      slide.hidden = i !== index;
      if (i === index) steps[i].setAttribute('aria-current', 'step');
      else steps[i].removeAttribute('aria-current');
    });
    previous.disabled = index === 0;
    next.disabled = index === slides.length - 1;
    if (focus) {
      slides[index].querySelector('h2').focus({ preventScroll: true });
      if (document.fullscreenElement === deck) deck.scrollTop = 0;
      else window.scrollTo(0, 0);
    }
  }

  function readLocation(focus = false) {
    const index = slides.findIndex(slide => '#' + slide.id === location.hash);
    showSlide(index < 0 ? 0 : index, focus);
  }

  function goTo(index) {
    if (index === current || index < 0 || index >= slides.length) return;
    history.pushState(null, '', '#' + slides[index].id);
    showSlide(index, true);
  }

  controls.addEventListener('click', event => {
    const step = event.target.closest('a');
    if (!step || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    goTo(steps.indexOf(step));
  });
  previous.addEventListener('click', () => goTo(current - 1));
  next.addEventListener('click', () => goTo(current + 1));
  window.addEventListener('hashchange', () => readLocation(true));

  document.addEventListener('keydown', event => {
    if (event.target !== document.body && !deck.contains(event.target)) return;
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    const target = { ArrowLeft: current - 1, ArrowRight: current + 1,
      Home: 0, End: slides.length - 1 }[event.key];
    if (target === undefined) return;
    event.preventDefault();
    goTo(target);
  });
  if (document.fullscreenEnabled && deck.requestFullscreen) {
    fullscreen.hidden = false;
    fullscreen.addEventListener('click', async () => {
      try {
        if (document.fullscreenElement === deck) await document.exitFullscreen();
        else await deck.requestFullscreen();
      } catch {
        fullscreen.hidden = true;
      }
    });
    document.addEventListener('fullscreenchange', () => {
      fullscreen.textContent = document.fullscreenElement === deck ? 'Sair da tela cheia' : 'Tela cheia';
    });
  }

  readLocation();
  controls.hidden = false;
}
