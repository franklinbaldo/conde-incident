const deck = document.querySelector('.conde-deck');

if (deck) {
  const slides = Array.from(deck.querySelectorAll('.deck-slide'));
  const controls = deck.querySelector('.deck-controls');
  const stage = deck.querySelector('.deck-stage');
  const steps = Array.from(controls.querySelectorAll('a'));
  const previous = controls.querySelector('[data-previous]');
  const next = controls.querySelector('[data-next]');
  const fullscreen = deck.querySelector('[data-fullscreen]');
  const worldToggle = deck.querySelector('[data-world]');
  const world = deck.querySelector('#globo');
  const itinerary = world.querySelector('[data-itinerary]');
  const placeName = world.querySelector('[data-place-name]');
  const placeDetail = world.querySelector('[data-place-detail]');
  const headings = slides.map(slide => slide.querySelector('h2'));
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  let current = 0;
  let overview = false;
  let globe;
  let places;
  let travel;
  let opening;

  const destinations = slides.map((slide, index) => {
    const item = document.createElement('li');
    const link = document.createElement('a');
    link.setAttribute('href', '#' + slide.id);
    const number = document.createElement('span');
    number.textContent = steps[index].textContent;
    number.setAttribute('aria-hidden', 'true');
    link.append(number, headings[index].textContent);
    item.append(link);
    itinerary.append(item);
    return link;
  });

  function setCurrent(index) {
    current = index;
    slides.forEach((_, i) => {
      for (const link of [steps[i], destinations[i]]) {
        if (i === current) link.setAttribute('aria-current', 'step');
        else link.removeAttribute('aria-current');
      }
    });
    previous.disabled = index === 0;
    next.disabled = index === slides.length - 1;
  }

  function focusTarget(target) {
    target.focus({ preventScroll: true });
    if (document.fullscreenElement === deck) deck.scrollTop = 0;
    else window.scrollTo(0, 0);
  }

  function setOverview(value) {
    overview = value;
    worldToggle.setAttribute('aria-pressed', String(value));
    worldToggle.textContent = value ? 'Voltar ao slide' : 'Ver globo';
  }

  function showSlide(index, focus = false) {
    setOverview(false);
    setCurrent(index);
    world.hidden = true;
    slides.forEach((slide, i) => { slide.hidden = i !== index; });
    if (focus) focusTarget(headings[index]);
  }

  function showWorld(index, flying) {
    setOverview(!flying);
    setCurrent(index);
    slides.forEach(slide => { slide.hidden = true; });
    world.toggleAttribute('data-flying', flying);
    world.hidden = false;
    placeName.textContent = places[slides[index].dataset.place].label;
    placeDetail.textContent = headings[index].textContent;
  }

  function stopMotion() {
    globe?.stop();
    if (travel?.active) {
      travel.stop();
      showSlide(current);
    }
  }

  function openWorld(push, focus = true) {
    if (!globe) return;
    const origin = world.hidden ? slides[current].dataset.place : null;
    stopMotion();
    if (push) history.pushState({ slide: current }, '', '#globo');
    showWorld(current, false);
    globe.move(origin, slides[current].dataset.place, true, reducedMotion.matches ? 0 : 520);
    if (focus) focusTarget(world.querySelector('h2'));
  }

  function readLocation(focus = false) {
    if (location.hash === '#globo' && globe) {
      const saved = history.state?.slide;
      if (Number.isInteger(saved) && slides[saved]) current = saved;
      openWorld(false, focus);
      return;
    }
    const found = slides.findIndex(slide => '#' + slide.id === location.hash);
    const index = found < 0 ? 0 : found;
    if (focus && (index !== current || overview)) {
      goTo(index, false);
      return;
    }
    stopMotion();
    showSlide(index, focus);
  }

  function goTo(index, push = true) {
    if (!slides[index] || (index === current && !overview)) return;
    stopMotion();
    const source = overview ? null : slides[current];
    const destination = slides[index];
    const fromKey = source?.dataset.place;
    const toKey = destination.dataset.place;
    if (push) history.pushState(null, '', '#' + destination.id);
    if (!travel || reducedMotion.matches) {
      showSlide(index, true);
      return;
    }
    const outward = source === slides[0] ? opening?.departure() : null;
    setCurrent(index);
    setOverview(false);
    world.hidden = true;
    travel.fly({
      source, destination, outward,
      from: fromKey ? { ...places[fromKey], key: fromKey } : null,
      to: { ...places[toKey], key: toKey },
      label: places[toKey].label,
      titleText: headings[index].textContent,
      after: () => showSlide(index, true),
    });
  }

  function useLinks(container, links) {
    container.addEventListener('click', event => {
      const link = event.target.closest('a');
      if (!link || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      goTo(links.indexOf(link));
    });
  }

  useLinks(controls, steps);
  useLinks(itinerary, destinations);
  previous.addEventListener('click', () => goTo(current - 1));
  function advance() {
    if (current === 0 && world.hidden && opening?.advance()) return;
    goTo(current + 1);
  }

  next.addEventListener('click', advance);
  worldToggle.addEventListener('click', () => {
    if (overview) goTo(current);
    else openWorld(true);
  });
  window.addEventListener('hashchange', () => readLocation(true));

  document.addEventListener('keydown', event => {
    if (event.target !== document.body && !deck.contains(event.target)) return;
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    if (event.target.closest?.('[data-desk-reader]')) return;
    if (globe && (event.key.toLowerCase() === 'g' || (event.key === 'Escape' && overview))) {
      event.preventDefault();
      if (overview) goTo(current);
      else openWorld(true);
      return;
    }
    const target = new Map([
      ['ArrowLeft', current - 1], ['ArrowRight', current + 1],
      ['Home', 0], ['End', slides.length - 1],
    ]).get(event.key);
    if (target === undefined) return;
    event.preventDefault();
    if (event.key === 'ArrowRight') advance();
    else goTo(target);
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
  import('./apresentacao-globo.mjs').then(async module => {
    places = module.places;
    globe = module.createGlobe(world.querySelector('[data-earth]'));
    if (!globe) return;
    worldToggle.hidden = false;
    if (location.hash === '#globo') readLocation();
    const [{ createTravel }, { mountDescent }] = await Promise.all([
      import('./apresentacao-voo.mjs'), import('./apresentacao-descida.mjs'),
    ]);
    const flightGlobe = module.createGlobe(stage.querySelector('[data-route-earth]'));
    if (flightGlobe) travel = createTravel(stage, flightGlobe, places);
    opening = await mountDescent(slides[0], module.createGlobe);
  }).catch(error => {
    console.warn('Globo da apresentação indisponível.', error);
  });
}
