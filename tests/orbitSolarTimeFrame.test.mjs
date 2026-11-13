import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dragAccelerationKmS2 } from '../src/lib/orbitPhysics.ts';
import { validateSourcedLocalSolarTimeHours } from '../src/lib/orbitGeodeticFrame.ts';
import { makeConditionalMsiseAtmosphere } from '../src/lib/orbitSpaceWeatherAdapter.ts';

// All directions and states below are SYNTHETIC. No 1963 Sun ephemeris,
// EOP, Earth orientation or NORAD instrumental data is implied.
const pole = [0, 0, 1], prime = [1, 0, 0];
const X = [1, 0, 0], Y = [0, 1, 0];
const snapshot = JSON.parse(readFileSync(new URL(
  '../research/meteorology/space_weather_msise_inputs_1963_11_07_09.json', import.meta.url)));
const state = {rKm: [6878.137, 0, 0], vKmS: [0, 7.6, 0], tS: 100};
const opts = (overrides = {}) => ({
  snapshot, originEpochUtc: '1963-11-08T12:00:00Z', originStateTS: 100,
  inertialFrame: 'SYNTHETIC-ECI', frameTransformSource: 'SYNTHETIC_GEODESY',
  toGeodetic: () => ({latitudeDeg: 0, longitudeDeg: 0,
    altitudeKm: 500, localSolarTimeHours: 12}),
  inertialEarthPoleAtUtc: () => pole, earthPoleSource: 'SYNTHETIC_POLE',
  inertialPrimeMeridianAtUtc: () => prime, primeMeridianSource: 'SYNTHETIC_PRIME',
  inertialSunDirectionAtUtc: () => X, sunDirectionSource: 'SYNTHETIC_SUN',
  densityModelSource: 'SYNTHETIC_DENSITY', evaluateDensityKgM3: () => 1e-12,
  cdAreaOverMassM2Kg: 0.01, ...overrides,
});

test('G45 source-identified Sun detects forged solar hour even when full geodesy passes', () => {
  let calls = 0;
  const wrong = makeConditionalMsiseAtmosphere(opts({
    toGeodetic: () => ({latitudeDeg: 0, longitudeDeg: 0,
      altitudeKm: 500, localSolarTimeHours: 6}),
    evaluateDensityKgM3: () => { calls++; return 1e-12; },
  }));
  assert.throws(() => dragAccelerationKmS2(state, wrong), /Local solar time inconsistent/);
  assert.equal(calls, 0, 'density must not be sampled with inconsistent local solar time');
  const good = makeConditionalMsiseAtmosphere(opts({
    evaluateDensityKgM3: () => { calls++; return 1e-12; },
  }));
  assert.ok(dragAccelerationKmS2(state, good).every(Number.isFinite));
  assert.equal(calls, 1);
  assert.match(good.source, /local-solar-time=SYNTHETIC_SUN \(CHECK_ONLY\)/);
});

test('G45 east-positive hour-angle, sunrise/sunset, midnight and 24-hour wrap', () => {
  assert.doesNotThrow(() => validateSourcedLocalSolarTimeHours(0, 12, pole, prime, X));
  assert.doesNotThrow(() => validateSourcedLocalSolarTimeHours(90, 18, pole, prime, X));
  assert.doesNotThrow(() => validateSourcedLocalSolarTimeHours(-90, 6, pole, prime, X));
  assert.doesNotThrow(() => validateSourcedLocalSolarTimeHours(180, 0, pole, prime, X));
  assert.doesNotThrow(() => validateSourcedLocalSolarTimeHours(-180, 23.9999, pole, prime, X));
  assert.doesNotThrow(() => validateSourcedLocalSolarTimeHours(0, 6, pole, prime, Y));
  assert.throws(() => validateSourcedLocalSolarTimeHours(0, 6, pole, prime, X), /inconsistent/);
  assert.throws(() => validateSourcedLocalSolarTimeHours(0, 0, pole, prime, X), /inconsistent/);
});

test('G45 Sun callback is UTC-sensitive at every density invocation', () => {
  const seen = [];
  const atm = makeConditionalMsiseAtmosphere(opts({
    inertialSunDirectionAtUtc: utc => {
      seen.push(utc);
      return utc.endsWith('00.000Z') ? X : Y;
    },
  }));
  assert.ok(dragAccelerationKmS2(state, atm).every(Number.isFinite));
  assert.throws(() => dragAccelerationKmS2({...state, tS: 101}, atm), /Local solar time inconsistent/);
  assert.deepEqual(seen, ['1963-11-08T12:00:00.000Z', '1963-11-08T12:00:01.000Z']);
});

test('G45 source coupling and invalid Sun direction fail closed', () => {
  assert.throws(() => makeConditionalMsiseAtmosphere(opts({sunDirectionSource: ''})),
    /Requires explicit/);
  assert.throws(() => makeConditionalMsiseAtmosphere(opts({
    inertialPrimeMeridianAtUtc: undefined, primeMeridianSource: undefined,
  })), /Requires explicit/);
  assert.throws(() => makeConditionalMsiseAtmosphere(opts({
    inertialSunDirectionAtUtc: undefined,
  })), /Requires explicit/);
  for (const sun of [[0, 0, 0], [0, 0, 1], [NaN, 0, 1], [2, 0, 0]]) {
    const atm = makeConditionalMsiseAtmosphere(opts({inertialSunDirectionAtUtc: () => sun}));
    assert.throws(() => dragAccelerationKmS2(state, atm), /Invalid sourced|undefined equatorial/);
  }
  const unchecked = makeConditionalMsiseAtmosphere(opts({
    inertialSunDirectionAtUtc: undefined, sunDirectionSource: undefined,
  }));
  assert.match(unchecked.source, /local-solar-time=NOT_CHECKED/);
});
