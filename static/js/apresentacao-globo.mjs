import { coastline110mPart1 } from './coastline110mPart1.js';
import { coastline110mPart2 } from './coastline110mPart2.js';
import { coastline110mPart3 } from './coastline110mPart3.js';

export const places = {
  arlington: { label: 'Arlington, EUA', latitude: 38.87, longitude: -77.06 },
  'sao-paulo': { label: 'São Paulo, Brasil', latitude: -23.55, longitude: -46.63 },
  internet: { label: 'Internet · sem local único' },
  rio: { label: 'Rio de Janeiro, Brasil', latitude: -22.91, longitude: -43.17 },
  greenbelt: { label: 'Greenbelt, EUA · Centro Goddard da NASA', latitude: 39.00, longitude: -76.84 },
  salvador: { label: 'Salvador, Brasil', latitude: -12.97, longitude: -38.50 },
  washington: { label: 'Washington, EUA · Arquivo Smithsonian', latitude: 38.89, longitude: -77.02 },
  maracaibo: { label: 'Maracaibo, Venezuela · local do avistamento relatado', latitude: 10.65, longitude: -71.64 },
  conde: { label: 'Conde, Bahia · local citado no relato', latitude: -11.81, longitude: -37.61 },
};

const atlantic = { latitude: 3, longitude: -51 };
const radians = Math.PI / 180;

function vector(longitude, latitude) {
  const phi = latitude * radians;
  const lambda = longitude * radians;
  return [Math.cos(phi) * Math.cos(lambda), Math.cos(phi) * Math.sin(lambda), Math.sin(phi)];
}

function axis(first, last, step) {
  return Array.from({ length: (last - first) / step + 1 }, (_, i) => first + i * step);
}

const coasts = [...coastline110mPart1, ...coastline110mPart2, ...coastline110mPart3]
  .map(line => line.map(([lon, lat]) => vector(lon, lat)));
const grid = [
  ...axis(-75, 75, 15).map(lat => axis(-180, 180, 5).map(lon => vector(lon, lat))),
  ...axis(-180, 165, 15).map(lon => axis(-90, 90, 5).map(lat => vector(lon, lat))),
];
const markers = Object.fromEntries(Object.entries(places)
  .filter(([, place]) => place.latitude !== undefined)
  .map(([key, place]) => [key, vector(place.longitude, place.latitude)]));

function dot(a, b) {
  return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}

function camera(place, overview = false) {
  if (overview || place.latitude === undefined) return { ...atlantic, scale: 1 };
  return { latitude: place.latitude * .86, longitude: place.longitude + 6, scale: 1.24 };
}

function mix(a, b, t) {
  return a + (b - a) * t;
}

export function createGlobe(canvas) {
  const ctx = canvas.getContext('2d');
  if (!ctx) return null;

  let frame = 0;
  let selected;
  let view = camera(places.internet, true);

  function draw() {
    const side = canvas.clientWidth;
    if (!side) return;
    const density = Math.min(devicePixelRatio, 2, 1700 / side);
    const pixels = Math.ceil(side * density);
    if (canvas.width !== pixels || canvas.height !== pixels) {
      canvas.width = pixels;
      canvas.height = pixels;
    }
    ctx.setTransform(pixels / side, 0, 0, pixels / side, 0, 0);
    ctx.clearRect(0, 0, side, side);

    const phi = view.latitude * radians;
    const lambda = view.longitude * radians;
    const forward = vector(view.longitude, view.latitude);
    const right = [-Math.sin(lambda), Math.cos(lambda), 0];
    const up = [-Math.sin(phi) * Math.cos(lambda), -Math.sin(phi) * Math.sin(lambda), Math.cos(phi)];
    const center = side / 2;
    const radius = side * .409 * view.scale;
    const project = point => [
      center + radius * dot(point, right),
      center - radius * dot(point, up),
      dot(point, forward),
    ];

    ctx.save();
    ctx.beginPath();
    ctx.arc(center, center, radius, 0, Math.PI * 2);
    const ocean = ctx.createRadialGradient(center - radius * .24, center - radius * .34,
      radius * .03, center, center, radius);
    ocean.addColorStop(0, '#204b57');
    ocean.addColorStop(.68, '#14323e');
    ocean.addColorStop(1, '#0b1a27');
    ctx.fillStyle = ocean;
    ctx.shadowColor = '#5abae361';
    ctx.shadowBlur = Math.min(36, side * .07);
    ctx.fill();
    ctx.shadowBlur = 0;
    ctx.strokeStyle = '#70b1b8a8';
    ctx.lineWidth = 1.4;
    ctx.stroke();
    ctx.clip();

    function drawLines(lines, color, width) {
      ctx.strokeStyle = color;
      ctx.lineWidth = width;
      ctx.beginPath();
      for (const line of lines) {
        let a = project(line[0]);
        for (let i = 1; i < line.length; i++) {
          const b = project(line[i]);
          if (a[2] >= 0 && b[2] >= 0) {
            ctx.moveTo(a[0], a[1]);
            ctx.lineTo(b[0], b[1]);
          } else if ((a[2] >= 0) !== (b[2] >= 0)) {
            const t = a[2] / (a[2] - b[2]);
            const visible = a[2] >= 0 ? a : b;
            ctx.moveTo(visible[0], visible[1]);
            ctx.lineTo(mix(a[0], b[0], t), mix(a[1], b[1], t));
          }
          a = b;
        }
      }
      ctx.stroke();
    }

    drawLines(grid, '#85b7c33d', .65);
    drawLines(coasts, '#a9d6c8db', side < 360 ? .8 : 1.15);

    function drawMarker(point, active) {
      const [x, y, visible] = project(point);
      if (visible < 0) return;
      if (active) {
        ctx.strokeStyle = '#ffc174a0';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(x, y, 11, 0, Math.PI * 2);
        ctx.stroke();
      }
      ctx.fillStyle = active ? '#ffd493' : '#adc7cc';
      ctx.beginPath();
      ctx.arc(x, y, active ? 5 : 2.6, 0, Math.PI * 2);
      ctx.fill();
    }

    for (const [key, point] of Object.entries(markers)) {
      if (key !== selected) drawMarker(point, false);
    }
    if (markers[selected]) drawMarker(markers[selected], true);
    ctx.restore();
  }

  function move(fromKey, toKey, overview, duration, finished) {
    if (frame) cancelAnimationFrame(frame);
    const from = fromKey ? camera(places[fromKey]) : view;
    const to = camera(places[toKey], overview);
    const delta = ((to.longitude - from.longitude + 540) % 360) - 180;
    selected = toKey;
    if (!duration) {
      view = to;
      draw();
      finished?.();
      return;
    }
    const start = performance.now();
    function tick(now) {
      const phase = Math.min(1, (now - start) / duration);
      const eased = phase * phase * (3 - 2 * phase);
      view = {
        latitude: mix(from.latitude, to.latitude, eased),
        longitude: from.longitude + delta * eased,
        scale: mix(from.scale, to.scale, eased) - .32 * Math.sin(Math.PI * phase),
      };
      draw();
      if (phase < 1) frame = requestAnimationFrame(tick);
      else {
        frame = 0;
        finished?.();
      }
    }
    frame = requestAnimationFrame(tick);
  }

  function stop() {
    if (frame) cancelAnimationFrame(frame);
    frame = 0;
  }

  new ResizeObserver(draw).observe(canvas);
  function centerOn(latitude, longitude) {
    stop();
    selected = undefined;
    view = { latitude, longitude, scale: 1 };
    draw();
  }

  function position(latitude, longitude, scale, key) {
    view = { latitude, longitude, scale };
    selected = key;
    draw();
  }

  return { move, stop, centerOn, position };
}
