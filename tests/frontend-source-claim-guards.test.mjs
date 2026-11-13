import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const read = (path) => readFileSync(new URL(`../${path}`, import.meta.url), 'utf8');
const summary = read('src/components/ExecutiveSummary.tsx');
const tle = read('src/components/TleAuditViewer.tsx');
const constants = read('src/lib/constants.ts');
const app = read('src/App.tsx');

test('visible summary distinguishes secondary TLE from primary observations, PT/EN', () => {
  assert.match(summary, /C179#1 registra um TLE do 528 obtido de espelho secundário/);
  assert.match(summary, /C179#1 records a 528 TLE from a secondary mirror/);
  assert.doesNotMatch(summary, /284[,.]1520/);
  assert.match(summary, /matrixLine: 839/);
  assert.match(summary, /C197#1 \/ C198#1/);
});

test('TLE auditor keeps model vectors but does not present their RAAN as authenticated', () => {
  assert.match(app, /<TleAuditViewer lang={lang}/);
  assert.match(tle, /selectedId === 528 \? `\$\{sat\.raanDeg\.toFixed\(4\)\}°` : t\.unverified/);
  assert.match(tle, /Não autenticado \(cenário\)/);
  assert.match(tle, /Unauthenticated \(scenario\)/);
  assert.doesNotMatch(tle, /284[,.]1520/);
  assert.match(tle, /19640019314\/downloads\/19640019314\.pdf#page=7/);
  assert.match(tle, /C179#1/);
});

test('unverified observation chronology remains in research-era constants, not imported by public UI', () => {
  assert.match(constants, /id: 'OBS-02'/);
  assert.match(constants, /id: 'OBS-04'/);
  assert.doesNotMatch(app, /NORAD_OBSERVATION_EVENTS|EPISTEMIC_AUDIT_LOG/);
  // This test is intentionally narrow: further UI routes must undergo separate provenance audit.
});
