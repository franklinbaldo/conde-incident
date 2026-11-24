const degrees = { latitude: 38.89767, longitude: -77.03655 };
const earthDiameter = 12_742_000;
// The USGS exports share the White House as their center in EPSG:3857.
const widths = { region: 160_000, metro: 32_000, city: 7000, district: 1700, roof: 570, close: 125, room: 20 };
const globeDiameterFraction = .818; // diameter drawn by createGlobe
const layerBase = 680;
const duration = 5800;

export async function mountDescent(cover, createGlobe) {
  const view = cover.querySelector('[data-descent]');
  const hud = cover.querySelector('[data-descent-hud]');
  const button = hud.querySelector('[data-descent-action]');
  const place = hud.querySelector('[data-descent-place]');
  const source = hud.querySelector('[data-descent-source]');
  const pin = view.querySelector('[data-descent-pin]');
  const layers = Object.fromEntries(Array.from(view.querySelectorAll('[data-descent-layer]'),
    element => [element.dataset.descentLayer, element]));
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const narrow = matchMedia('(max-width: 680px)');

  try {
    await Promise.all(Array.from(view.querySelectorAll('img'), image => {
      image.loading = 'eager';
      return image.decode();
    }));
  } catch {
    return null; // The authored cover and its original document link remain available.
  }
  const globe = createGlobe(layers.earth.querySelector('canvas'));
  if (!globe) return null;

  let progress = 0;
  let target = 0;
  let frame = 0;

  function paint() {
    const { clientWidth: width, clientHeight: height } = cover;
    if (!width || !height) return;
    const compact = narrow.matches;
    const drift = progress * progress;
    const x = width * (compact ? .5 : .67 - .11 * drift);
    const y = height * (compact ? .28 + .15 * drift : .5);
    const start = Math.min(width, height) * (compact ? .72 : .79) / earthDiameter;
    const finish = Math.max(width * 1.34, height * 2.17) / widths.room;
    const zoom = start * Math.pow(finish / start, progress);
    const coverDiagonal = 2.25 * Math.hypot(width, height);
    const documentWidth = Math.min(width * (compact ? .59 : .31), height * .56 * 340 / 440);
    const sizes = {
      earth: earthDiameter * zoom / globeDiameterFraction,
      ...Object.fromEntries(Object.entries(widths).map(([key, metres]) => [key, metres * zoom])),
      document: Math.min(documentWidth, documentWidth * zoom / finish),
    };
    let covered = false;
    for (const name of ['document', ...Object.keys(widths).reverse(), 'earth']) {
      const layer = layers[name];
      const size = sizes[name];
      layer.style.visibility = covered || size < .6 ? 'hidden' : 'visible';
      if (!covered && size >= .6) {
        layer.style.transform = 'translate3d(' + x + 'px,' + y + 'px,0) translate(-50%,-50%) scale('
          + size / layerBase + ')';
      }
      if (name !== 'document' && size >= coverDiagonal) covered = true;
    }
    pin.style.transform = 'translate3d(' + x + 'px,' + y + 'px,0) translate(-50%,-50%)';
    pin.hidden = sizes.room > 75;
    const label = progress === 1 ? 'Aerograma A-628 · 20 de novembro de 1963'
      : sizes.room > width * .38 ? 'Escritório · cena ilustrativa'
        : sizes.roof > width * .47 ? 'Casa Branca, Washington, D.C.'
          : 'Washington, D.C.';
    if (place.textContent !== label) place.textContent = label;
  }

  function settle(at) {
    progress = at;
    cover.dataset.descentPhase = at === 1 ? 'desk' : 'globe';
    source.hidden = at !== 1;
    button.textContent = at === 1 ? 'Voltar ao globo' : 'Aproximar da Casa Branca';
    paint();
  }

  function travel(to) {
    if (frame) cancelAnimationFrame(frame);
    frame = 0;
    target = to;
    if (motion.matches || progress === to) {
      settle(to);
      return;
    }
    const from = progress;
    const span = duration * Math.abs(to - from);
    const start = performance.now();
    cover.dataset.descentPhase = 'moving';
    button.textContent = to === 1 ? 'Ir direto ao aerograma' : 'Ir direto ao globo';
    source.hidden = true;

    function tick(now) {
      const t = Math.min(1, (now - start) / span);
      const eased = t - .78 * Math.sin(2 * Math.PI * t) / (2 * Math.PI);
      progress = from + (to - from) * eased;
      if (t < 1) {
        paint();
        frame = requestAnimationFrame(tick);
      } else {
        frame = 0;
        settle(to);
      }
    }
    frame = requestAnimationFrame(tick);
  }

  button.addEventListener('click', () => {
    if (frame) {
      cancelAnimationFrame(frame);
      frame = 0;
      settle(target);
    } else {
      travel(progress === 1 ? 0 : 1);
    }
  });
  motion.addEventListener('change', () => {
    if (motion.matches && frame) {
      cancelAnimationFrame(frame);
      frame = 0;
      settle(target);
    }
  });

  cover.dataset.descentReady = '';
  view.hidden = hud.hidden = false;
  globe.centerOn(degrees.latitude, degrees.longitude);
  settle(0);
  new ResizeObserver(paint).observe(cover);

  return {
    advance() {
      if (progress === 1 && !frame) return false;
      if (!frame || target === 0) travel(1);
      return true;
    },
  };
}
