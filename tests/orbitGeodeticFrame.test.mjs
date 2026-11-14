import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dragAccelerationKmS2 } from '../src/lib/orbitPhysics.ts';
import { makeConditionalMsiseAtmosphere } from '../src/lib/orbitSpaceWeatherAdapter.ts';
import { validateSourcedGeodeticFrameKm } from '../src/lib/orbitGeodeticFrame.ts';

// Synthetic geometry, NOT an EOP or a NORAD observation.
const point = {latitudeDeg: 0, longitudeDeg: 0, altitudeKm: 500};
const r = [6878.137, 0, 0], pole = [0, 0, 1], x = [1, 0, 0];
const snapshot = JSON.parse(readFileSync(new URL(
  '../research/meteorology/space_weather_msise_inputs_1963_11_07_09.json', import.meta.url)));
const state = {rKm: r, vKmS: [0, 7.6, 0], tS: 100};
const options = overrides => ({
  snapshot, temporalUse: 'RETROSPECTIVE_RECONSTRUCTION', originEpochUtc: '1963-11-08T12:00:00Z', originStateTS: 100,
  inertialFrame: 'SYNTHETIC-INERTIAL', frameTransformSource: 'SYNTHETIC_ONLY',
  toGeodetic: () => ({...point, localSolarTimeHours: 12}),
  inertialEarthPoleAtUtc: () => pole, earthPoleSource: 'SYNTHETIC_POLE',
  inertialPrimeMeridianAtUtc: () => x, primeMeridianSource: 'SYNTHETIC_X_AXIS',
  densityModelSource: 'SYNTHETIC_ONLY', evaluateDensityKgM3: () => 1e-12,
  cdAreaOverMassM2Kg: 0.01, ...overrides,
});

test('G44 full-frame guard rejects false longitude invisible to G42/G43', () => {
  // Radius and axial coordinate are unchanged by rotating ECEF longitude.
  assert.doesNotThrow(() => validateSourcedGeodeticFrameKm(r, point, pole, x));
  assert.throws(() => validateSourcedGeodeticFrameKm(r,
    {...point, longitudeDeg: 90}, pole, x), /longitude\/latitude\/height/);
  assert.throws(() => validateSourcedGeodeticFrameKm(r,
    {...point, longitudeDeg: 180}, pole, x), /longitude\/latitude\/height/);
  let densityCalls = 0;
  const falseLongitude = makeConditionalMsiseAtmosphere(options({
    toGeodetic: () => ({...point, longitudeDeg: 90, localSolarTimeHours: 12}),
    evaluateDensityKgM3: () => { densityCalls++; return 1e-12; },
  }));
  assert.throws(() => dragAccelerationKmS2(state, falseLongitude), /longitude\/latitude\/height/);
  assert.equal(densityCalls, 0);
  // Removing sourced meridian must disclose the unchecked dimension.
  const axialOnly = makeConditionalMsiseAtmosphere(options({
    inertialPrimeMeridianAtUtc: undefined, primeMeridianSource: undefined,
    toGeodetic: () => ({...point, longitudeDeg: 90, localSolarTimeHours: 12}),
  }));
  assert.match(axialOnly.source, /full-geodesy=NOT_CHECKED/);
  assert.doesNotThrow(() => dragAccelerationKmS2(state, axialOnly));
});

test('G44 right-handed axes, rotated frame and longitude wrap have positive controls', () => {
  assert.doesNotThrow(() => validateSourcedGeodeticFrameKm([0, 6878.137, 0],
    {...point, longitudeDeg: 90}, pole, x));
  assert.doesNotThrow(() => validateSourcedGeodeticFrameKm([-6878.137, 0, 0],
    {...point, longitudeDeg: -180}, pole, x));
  // Rotate Earth-fixed x-axis by 90 deg in inertial space. The point at
  // longitude zero must rotate by 90 deg as well.
  assert.doesNotThrow(() => validateSourcedGeodeticFrameKm([0, 6878.137, 0],
    point, pole, [0, 1, 0]));
  assert.doesNotThrow(() => dragAccelerationKmS2(
    {...state, rKm: [0, 6878.137, 0]},
    makeConditionalMsiseAtmosphere(options({
      inertialPrimeMeridianAtUtc: () => [0, 1, 0],
    }))));
  const a=6378.137, b=6356.752314245, phi=Math.PI/4, h=500, e2=1-(b/a)**2;
  const N=a/Math.sqrt(1-e2*Math.sin(phi)**2);
  const horizontal=(N+h)*Math.cos(phi), vertical=(N*(1-e2)+h)*Math.sin(phi);
  assert.doesNotThrow(() => validateSourcedGeodeticFrameKm(
    [horizontal/Math.sqrt(2), horizontal/Math.sqrt(2), vertical],
    {latitudeDeg: 45, longitudeDeg: 45, altitudeKm: h}, pole, x));
});

test('G44 missing or distorted ECEF meridian cannot silently produce density', () => {
  assert.throws(() => makeConditionalMsiseAtmosphere(options({
    primeMeridianSource: '',
  })), /Requires explicit/);
  assert.throws(() => makeConditionalMsiseAtmosphere(options({
    inertialEarthPoleAtUtc: undefined, earthPoleSource: undefined,
  })), /Requires explicit/);
  assert.throws(() => dragAccelerationKmS2(state,
    makeConditionalMsiseAtmosphere(options({
      inertialPrimeMeridianAtUtc: () => [0, 0, 1],
    }))), /unit and perpendicular/);
  assert.throws(() => dragAccelerationKmS2(state,
    makeConditionalMsiseAtmosphere(options({
      inertialPrimeMeridianAtUtc: () => [2, 0, 0],
    }))), /unit and perpendicular/);
  assert.throws(() => dragAccelerationKmS2(state,
    makeConditionalMsiseAtmosphere(options({
      inertialPrimeMeridianAtUtc: () => [NaN, 0, 0],
    }))), /Invalid sourced WGS84 frame inputs/);
  assert.throws(() => dragAccelerationKmS2(state,
    makeConditionalMsiseAtmosphere(options({
      inertialPrimeMeridianAtUtc: () => [0, -1, 0],
    }))), /longitude\/latitude\/height/);
});

test('G44 rotation is queried at each RK4 substage epoch, not cached', () => {
  const seen = [];
  const atmosphere = makeConditionalMsiseAtmosphere(options({
    inertialPrimeMeridianAtUtc: epoch => {
      seen.push(epoch);
      return epoch === '1963-11-08T12:00:00.000Z' ? [1, 0, 0] : [0, 1, 0];
    },
  }));
  assert.doesNotThrow(() => dragAccelerationKmS2(state, atmosphere));
  assert.throws(() => dragAccelerationKmS2({...state, tS: 101}, atmosphere),
    /longitude\/latitude\/height/);
  assert.deepEqual(seen, ['1963-11-08T12:00:00.000Z',
    '1963-11-08T12:00:01.000Z']);
});
