// Detect known hosted map tile/API traffic during the local SVG-map smoke.
// Match domains on label boundaries, never URL substrings: this catches
// a.tile.openstreetmap.org without flagging docs.example.org?u=mapbox.com.
const MAP_PROVIDER_HOSTS = Object.freeze([
  'maps.googleapis.com',
  'maps.gstatic.com',
  'tile.openstreetmap.org',
  'mapbox.com',
  'maptiler.com',
  'basemaps.cartocdn.com',
  'server.arcgisonline.com',
  'tiles.stadiamaps.com',
]);

export function isRemoteMapProviderRequest(url) {
  const hostname = new URL(url).hostname.toLowerCase().replace(/\.$/, '');
  return MAP_PROVIDER_HOSTS.some(domain =>
    hostname === domain || hostname.endsWith(`.${domain}`));
}
