const ease = t => t * t * (3 - 2 * t);
const bound = n => Math.max(0, Math.min(1, n));
const wide = { latitude: 3, longitude: -51 };
const mapPlace = place => place?.latitude === undefined ? wide : place;

export function createTravel(stage, globe, places) {
  const route = stage.querySelector('[data-route]');
  const location = route.querySelector('[data-route-place]');
  const title = route.querySelector('[data-route-title]');
  const map = route.querySelector('[data-route-map]');
  const credit = route.querySelector('[data-route-credit]');
  const images = new Map();
  for (const [key, place] of Object.entries(places)) {
    if (place.latitude === undefined) continue;
    const image = new Image();
    image.src = '/conde-incident/img/apresentacao-lugares/' + key + '.webp';
    images.set(key, image);
  }
  let frame = 0;
  let planes = [];
  let finishOutward;

  function stop() {
    if (frame) cancelAnimationFrame(frame);
    frame = 0;
    finishOutward?.(1);
    finishOutward = null;
    for (const plane of planes) {
      plane.removeAttribute('data-route-plane');
      plane.style.removeProperty('--plane-scale');
      plane.style.removeProperty('--plane-x');
      plane.style.removeProperty('--plane-y');
      plane.inert = false;
    }
    planes = [];
    route.hidden = true;
    stage.removeAttribute('data-route-active');
    stage.style.removeProperty('--route-height');
  }

  function fly({ from, to, source, destination, outward, label, titleText, after }) {
    stop();
    finishOutward = outward;
    const fromPlace = mapPlace(from);
    const toPlace = mapPlace(to);
    const longitudeDelta = ((toPlace.longitude - fromPlace.longitude + 540) % 360) - 180;
    planes = source && source !== destination ? [source, destination] : [destination];
    const stageHeight = Math.max(stage.clientHeight, Math.min(innerHeight * .66, 580));
    stage.style.setProperty('--route-height', stageHeight + 'px');
    stage.dataset.routeActive = '';
    route.hidden = false;
    location.textContent = label;
    title.textContent = titleText;
    for (const plane of planes) {
      plane.dataset.routePlane = '';
      plane.hidden = false;
      plane.inert = true;
    }
    const leaving = planes.length === 2;
    const globeScale = Math.min(stage.clientWidth, stageHeight) * .86 / (stage.clientWidth * .818);
    const started = performance.now();
    const length = outward ? 3750 : leaving ? 2550 : 1700;

    function position(plane, size, x, y) {
      plane.style.setProperty('--plane-scale', String(size));
      plane.style.setProperty('--plane-x', x + '%');
      plane.style.setProperty('--plane-y', y + '%');
    }

    function step(now) {
      const progress = Math.min(1, (now - started) / length);
      const diveLength = outward ? .36 : 0;
      const t = bound((progress - diveLength) / (1 - diveLength));
      if (outward) outward(bound(progress / diveLength));
      const away = ease(bound(t / .32));
      const approach = ease(bound((t - .66) / .34));
      const turn = ease(bound((t - .22) / .56));
      const visibleStart = leaving ? 1 + 2.2 * (1 - away) : 1;
      globe.position(
        fromPlace.latitude + (toPlace.latitude - fromPlace.latitude) * turn,
        fromPlace.longitude + longitudeDelta * turn,
        globeScale * (visibleStart + 2.55 * approach),
        t < .5 ? from?.key : to?.key,
      );
      const photo = images.get(t < .5 ? from?.key : to?.key);
      const mapDepth = t < .5 ? (leaving ? 1 - away : 0) : ease(bound((t - .52) / .48));
      const mapSize = Math.exp(-7.8 * (1 - mapDepth)) * 1.9;
      map.hidden = !photo?.naturalWidth || mapSize < .011;
      credit.hidden = map.hidden;
      if (!map.hidden) {
        if (map.src !== photo.src) map.src = photo.src;
        map.style.setProperty('--geography-scale', String(mapSize));
      }
      if (leaving) position(source, Math.exp(-7.4 * away), 50, 50);
      position(destination, Math.exp(-7.4 * (1 - approach)), 50, 50);
      if (progress < 1) frame = requestAnimationFrame(step);
      else {
        stop();
        after();
      }
    }

    step(started);
  }

  return { fly, stop, get active() { return !!planes.length; } };
}
