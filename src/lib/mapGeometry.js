/**
 * Geometry-only helpers for the quota-free orbital illustration.
 * Neither these projections nor source TLE scenarios validate historical observations.
 */
export const clampZoom = (value) => Math.min(6, Math.max(1, Number.isFinite(value) ? value : 1));
export const wrapLongitude = (lon) => ((lon + 180) % 360 + 360) % 360 - 180;

/** The date line must not be joined by an artificial stroke across the world map. */
export function splitDateline(points) {
  const segments = [];
  let current = [];
  for (const p of points) {
    if (!Number.isFinite(p.longitude) || !Number.isFinite(p.latitude) ||
      Math.abs(p.latitude) > 90) {
      if (current.length) segments.push(current);
      current = [];
      continue;
    }
    // Projectors normalize longitude. Split using those same display
    // coordinates, otherwise 179° -> 181° paints a false 955px line.
    const wrapped = { ...p, longitude: wrapLongitude(p.longitude) };
    if (current.length && Math.abs(wrapped.longitude - current[current.length - 1].longitude) > 180) {
      segments.push(current);
      current = [];
    }
    current.push(wrapped);
  }
  if (current.length) segments.push(current);
  return segments;
}

/** Suppress a scenario connector that would jump across the flat-map seam.
 * Compare DISPLAY longitudes, not raw inputs: 179 -> 181 crosses the seam.
 * This is a rendering guard, never a geographic or orbital inference.
 */
export function canDrawFlatConnection(one, two) {
  return [one, two].every(point => Number.isFinite(point.longitude) &&
    Number.isFinite(point.latitude) && Math.abs(point.latitude) <= 90) &&
    Math.abs(wrapLongitude(one.longitude) - wrapLongitude(two.longitude)) <= 180;
}

/** Full-continent, deterministic equirectangular display; x/y in a 960x480 viewBox. */
export const projectFlat = (lon, lat) => ({
  x: (wrapLongitude(lon) + 180) * (960 / 360),
  y: (90 - lat) * (480 / 180),
  visible: true,
});

/** Orthographic display, with back hemisphere explicitly hidden. */
export function projectGlobe(lon, lat, rotationDeg = 0) {
  const phi = lat * Math.PI / 180;
  const lambda = (wrapLongitude(lon) - rotationDeg) * Math.PI / 180;
  const z = Math.cos(phi) * Math.cos(lambda);
  return {
    x: 480 + 210 * Math.cos(phi) * Math.sin(lambda),
    y: 240 - 210 * Math.sin(phi),
    visible: z >= 0,
  };
}

/** Split at both the date line and the globe horizon rather than connecting invisible arcs. */
export function projectedSegments(points, project) {
  const result = [];
  for (const segment of splitDateline(points)) {
    let visible = [];
    for (const pt of segment) {
      const xy = project(pt.longitude, pt.latitude);
      if (!xy.visible) {
        if (visible.length > 1) result.push(visible);
        visible = [];
      } else {
        visible.push(xy);
      }
    }
    if (visible.length > 1) result.push(visible);
  }
  return result;
}
