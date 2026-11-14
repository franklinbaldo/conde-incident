import test from 'node:test';
import assert from 'node:assert/strict';
import { isRemoteMapProviderRequest } from './map-provider-request-guard.mjs';

test('hosted map endpoints and their real XYZ/CDN subdomains are detected', () => {
  for (const url of [
    'https://maps.googleapis.com/maps/api/js',
    'https://khms.maps.googleapis.com/kh/v=1',
    'https://maps.gstatic.com/mapfiles/a.png',
    'https://tile.openstreetmap.org/4/6/7.png',
    'https://a.tile.openstreetmap.org/4/6/7.png',
    'https://b.tile.openstreetmap.org/4/6/7.png',
    'https://c.tile.openstreetmap.org/4/6/7.png',
    'https://api.mapbox.com/styles/v1',
    'https://tiles.mapbox.com/v1/tile',
    'https://api.maptiler.com/maps/',
    'https://basemaps.cartocdn.com/light_all/4/6/7.png',
    'https://server.arcgisonline.com/ArcGIS/rest/services',
    'https://tiles.stadiamaps.com/tiles/alidade_smooth',
  ]) assert.equal(isRemoteMapProviderRequest(url), true, url);
});

test('safe or deceptive lookalike hosts do not cause false positives', () => {
  for (const url of [
    'https://fonts.googleapis.com/css2?family=Inter',
    'https://fonts.gstatic.com/s/inter.woff2',
    'https://franklinbaldo.github.io/conde-incident/lab/',
    'https://example.org/docs?source=maps.googleapis.com',
    'https://maps.googleapis.com.attacker.invalid/map',
    'https://tile.openstreetmap.org.evil.invalid/tiles',
    'https://mapbox.com.evil.invalid/',
    'https://maps.googleapis.com@docs.example.org/',
  ]) assert.equal(isRemoteMapProviderRequest(url), false, url);
});

test('hostname matching is case-insensitive and anchored', () => {
  assert.equal(isRemoteMapProviderRequest('https://A.TILE.OPENSTREETMAP.ORG/tiles'), true);
  assert.equal(isRemoteMapProviderRequest('https://a.tile.openstreetmap.org./tiles'), true);
  assert.equal(isRemoteMapProviderRequest('https://notmapbox.com/'), false);
});
