import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dragAccelerationKmS2, rk4 } from '../src/lib/orbitPhysics.ts';
import { deriveMsiseDriversAtUtc, makeConditionalMsiseAtmosphere } from '../src/lib/orbitSpaceWeatherAdapter.ts';

// Real GFZ/NRC historic *drivers* from Lagarto's declared snapshot. The
// Cartesian states, coordinate transform and density evaluator below are
// SYNTHETIC TEST DOUBLES, not NORAD/Conde 1963 observations or NRLMSISE runs.
const snapshot = JSON.parse(readFileSync(new URL(
  '../research/meteorology/space_weather_msise_inputs_1963_11_07_09.json', import.meta.url)));
const dates = ['1963-11-07T12:00:00Z', '1963-11-08T12:00:00Z', '1963-11-09T12:00:00Z'];

test('rebuild all three documented conditional 12 UTC reference vectors from raw GFZ/NRC series', () => {
  assert.equal(snapshot.schema, 'conde.1963-conditional-msise-drivers/v1');
  for (let i = 0; i < dates.length; i++) {
    const result = deriveMsiseDriversAtUtc(snapshot, dates[i]);
    const row = snapshot.model_inputs[i];
    assert.equal(result.epochUtc, row.epoch_utc);
    assert.equal(result.f107PreviousDayObservedSfu, row.F107_previous_day_observed_sfu);
    assert.ok(Math.abs(result.f107aCentered81DayObservedSfu -
      row.F107A_81day_centered_observed_sfu) < 0.000001);
    assert.equal(result.apDaily, row.Ap_daily_planetary);
    assert.deepEqual(result.apHistory, row.ap_history_planetary);
    assert.equal(result.inputStatus, 'PLANETARY_DRIVERS_ONLY_NOT_DENSITY_OR_CALIBRATION');
  }
});

test('arbitrary sub-day evaluation uses true 3-hour ap bins rather than noon scenario or Kp scale', () => {
  const before = deriveMsiseDriversAtUtc(snapshot, '1963-11-08T05:59:59Z');
  const after = deriveMsiseDriversAtUtc(snapshot, '1963-11-08T06:00:01Z');
  assert.equal(before.apHistory[1], 67);
  assert.equal(after.apHistory[1], 80);
  assert.equal(after.apHistory[2], 67);
  assert.equal(after.apDaily, 46);
  assert.equal(after.f107PreviousDayObservedSfu, 76.6);
  assert.equal(after.f107aCentered81DayObservedSfu, before.f107aCentered81DayObservedSfu);
  const fakeKp = {...snapshot, raw_series: {...snapshot.raw_series, Kp: {'1963-11-08T06:00:00Z': 999}}};
  assert.deepEqual(deriveMsiseDriversAtUtc(fakeKp, '1963-11-08T06:00:01Z').apHistory,
    after.apHistory);
});

test('counterfactual loss of future 81-day records blocks centered-mean driver (no fake forecast)', () => {
  const flux = {...snapshot.raw_series.F107_observed_daily};
  delete flux['1963-12-18'];
  const damaged = {...snapshot, raw_series: {...snapshot.raw_series, F107_observed_daily: flux}};
  assert.throws(() => deriveMsiseDriversAtUtc(damaged, dates[1]), /centered 81-day/);
});

test('missing earlier ap history, wrong schema and false provenance are rejected', () => {
  assert.throws(() => deriveMsiseDriversAtUtc(snapshot, '1963-11-06T00:00:00Z'), /ap history/);
  assert.throws(() => deriveMsiseDriversAtUtc({...snapshot, schema: 'madeup'}, dates[1]), /Unsupported/);
  assert.throws(() => deriveMsiseDriversAtUtc({...snapshot, source_documents: {}}, dates[1]), /source URL/);
  assert.throws(() => deriveMsiseDriversAtUtc(snapshot, '1963-11-08'), /ISO-8601 UTC/);
  const ap = {...snapshot.raw_series.ap};
  delete ap['1963-11-08T09:00:00Z'];
  assert.throws(() => deriveMsiseDriversAtUtc(
    {...snapshot, raw_series: {...snapshot.raw_series, ap}}, dates[1]), /ap history/);
});

const initialState = {rKm: [6878.137, 0, 0], vKmS: [0, 7.6, 0], tS: 100};
const options = (overrides = {}) => ({
  snapshot,
  originEpochUtc: '1963-11-08T05:59:50Z', originStateTS: 100,
  inertialFrame: 'SYNTHETIC-INERTIAL', frameTransformSource: 'SYNTHETIC_ONLY',
  toGeodetic: state => ({
    latitudeDeg: state.rKm[2] / 100, longitudeDeg: state.rKm[1] / 100,
    altitudeKm: Math.hypot(...state.rKm) - 6378.137, localSolarTimeHours: 6,
  }),
  densityModelSource: 'SYNTHETIC_RHO_NOT_NRLMSISE',
  evaluateDensityKgM3: ({drivers}) => drivers.apHistory[1] * 1e-14,
  cdAreaOverMassM2Kg: 0.01,
  ...overrides,
});

test('full r/v drag force samples historical drivers at actual RK4 substage UTC', () => {
  const seen = [];
  const atmosphere = makeConditionalMsiseAtmosphere(options({
    evaluateDensityKgM3: ({drivers, epochUtc, geodetic}) => {
      seen.push([epochUtc, drivers.apHistory[1], geodetic.latitudeDeg]);
      return drivers.apHistory[1] * 1e-14;
    },
  }));
  const before = dragAccelerationKmS2(initialState, atmosphere);
  const after = dragAccelerationKmS2({...initialState, tS: 120}, atmosphere);
  assert.ok(before.every(Number.isFinite));
  assert.ok(after.every(Number.isFinite));
  assert.ok(Math.abs(after[1] / before[1] - 80 / 67) < 1e-12);
  assert.deepEqual(seen.map(s => s[1]), [67, 80]);
  assert.equal(seen[0][0], '1963-11-08T05:59:50.000Z');
  assert.equal(seen[1][0], '1963-11-08T06:00:10.000Z');
  assert.match(atmosphere.source, /NOT_CALIBRATED/);
  const next = rk4(initialState, 20, {j2: true, atmosphere});
  assert.equal(next.tS, 120);
  assert.ok(seen.length >= 6);
  assert.ok(seen.some(s => s[1] === 80));
  assert.ok(next.rKm.every(Number.isFinite) && next.vKmS.every(Number.isFinite));
});

test('density depends on actual state passed to transform, not recycled starting position', () => {
  const captured = [];
  const atmosphere = makeConditionalMsiseAtmosphere(options({
    evaluateDensityKgM3: request => {
      captured.push(request.geodetic.latitudeDeg);
      return 1e-12;
    },
  }));
  dragAccelerationKmS2(initialState, atmosphere);
  dragAccelerationKmS2({...initialState, rKm: [6878.137, 0, 200]}, atmosphere);
  assert.deepEqual(captured, [0, 2]);
});

test('missing coordinate/solar-time transformation cannot become invented density', () => {
  assert.throws(() => makeConditionalMsiseAtmosphere(options({
    frameTransformSource: '',
  })), /sourced transform/);
  const missingPlace = makeConditionalMsiseAtmosphere(options({
    toGeodetic: () => ({latitudeDeg: NaN, longitudeDeg: 0, altitudeKm: 500, localSolarTimeHours: 6}),
  }));
  assert.throws(() => dragAccelerationKmS2(initialState, missingPlace), /geodetic/);
  const missingSolarTime = makeConditionalMsiseAtmosphere(options({
    toGeodetic: () => ({latitudeDeg: 0, longitudeDeg: 0, altitudeKm: 500}),
  }));
  assert.throws(() => dragAccelerationKmS2(initialState, missingSolarTime), /solar time/);
  const invalidDensity = makeConditionalMsiseAtmosphere(options({evaluateDensityKgM3: () => NaN}));
  assert.throws(() => dragAccelerationKmS2(initialState, invalidDensity), /invalid kg\/m\^3/);
  assert.throws(() => dragAccelerationKmS2({...initialState, tS: 200}, {
    ...invalidDensity, densityKgM3: (_h, t, state) =>
      invalidDensity.densityKgM3(_h, t + 1, state),
  }), /inconsistent/);
});

test('outside historical driver coverage is a failed input, never assumed zero drag', () => {
  const atmosphere = makeConditionalMsiseAtmosphere(options());
  assert.throws(() => dragAccelerationKmS2({...initialState, tS: 100 + 14 * 86400}, atmosphere),
    /centered 81-day|prior-day|ap history|daily planetary/);
});


test('geodetic altitude must match a physical radius envelope before density evaluation', () => {
  let densityCalls = 0;
  const transform = (altitudeKm) => () => ({
    latitudeDeg: 0, longitudeDeg: 0, altitudeKm, localSolarTimeHours: 6,
  });
  const supplied = makeConditionalMsiseAtmosphere(options({
    toGeodetic: transform(500_000), // metres mistaken for km
    evaluateDensityKgM3: () => { densityCalls++; return 1e-12; },
  }));
  assert.throws(() => dragAccelerationKmS2(initialState, supplied), /inconsistent with inertial radius/);
  const stale = makeConditionalMsiseAtmosphere(options({
    toGeodetic: transform(500),
    evaluateDensityKgM3: () => { densityCalls++; return 1e-12; },
  }));
  assert.throws(() => dragAccelerationKmS2({
    ...initialState, rKm: [initialState.rKm[0] + 100, 0, 0],
  }, stale), /inconsistent with inertial radius/);
  assert.equal(densityCalls, 0, 'invalid geometry cannot feed the density solver');

  // Polar WGS84 radius is shorter than the equatorial radius by 21.3847 km:
  // a correct 500 km geodetic height is NOT 500 km of equatorial radial height.
  const polarState = {...initialState, rKm: [0, 0, 6356.752314245 + 500]};
  const polar = makeConditionalMsiseAtmosphere(options({
    toGeodetic: () => ({latitudeDeg: 90, longitudeDeg: 0,
      altitudeKm: 500, localSolarTimeHours: 6}),
    evaluateDensityKgM3: () => { densityCalls++; return 1e-12; },
  }));
  assert.ok(dragAccelerationKmS2(polarState, polar).every(Number.isFinite));
  assert.equal(densityCalls, 1);
});
