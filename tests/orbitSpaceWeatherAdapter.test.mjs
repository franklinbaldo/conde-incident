import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dragAccelerationKmS2, rk4 } from '../src/lib/orbitPhysics.ts';
import { deriveMsiseDriversAtUtc, makeConditionalMsiseAtmosphere,
  wgs84RadiusForGeodeticKm } from '../src/lib/orbitSpaceWeatherAdapter.ts';

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
  snapshot, temporalUse: 'RETROSPECTIVE_RECONSTRUCTION',
  originEpochUtc: '1963-11-08T05:59:50Z', originStateTS: 100,
  inertialFrame: 'SYNTHETIC-INERTIAL', frameTransformSource: 'SYNTHETIC_ONLY',
  toGeodetic: state => ({
    latitudeDeg: 0, longitudeDeg: state.rKm[2] / 100,
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
      seen.push([epochUtc, drivers.apHistory[1], geodetic.longitudeDeg]);
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
      captured.push(request.geodetic.longitudeDeg);
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

test('WGS84 geodetic latitude-height radius rejects a mismatch hidden inside the broad a/b envelope', () => {
  let densityCalls = 0;
  const density = () => { densityCalls++; return 1e-12; };
  const inconsistent = makeConditionalMsiseAtmosphere(options({
    toGeodetic: () => ({latitudeDeg: 90, longitudeDeg: 0,
      altitudeKm: 500, localSolarTimeHours: 6}),
    evaluateDensityKgM3: density,
  }));
  // At a=6378.137 km, h=500 km is permitted by the G41 broad interval
  // for either latitude, but latitude=90 requires r=b+500, not a+500.
  assert.throws(() => dragAccelerationKmS2(initialState, inconsistent),
    /latitude-height pair inconsistent/);
  const middleHeight = 500 + (6378.137 - 6356.752314245) / 2;
  const middle = makeConditionalMsiseAtmosphere(options({
    toGeodetic: () => ({latitudeDeg: 0, longitudeDeg: 0,
      altitudeKm: middleHeight, localSolarTimeHours: 6}),
    evaluateDensityKgM3: density,
  }));
  assert.throws(() => dragAccelerationKmS2(initialState, middle),
    /latitude-height pair inconsistent/);
  assert.equal(densityCalls, 0, 'no inconsistent geodesy may reach density');
});

test('independent 45-degree WGS84 construction and polar/geodetic corners pass radial validation', () => {
  const a = 6378.137, b = 6356.752314245, e2 = 1 - (b / a) ** 2;
  const phi = Math.PI / 4, h = 500;
  const N = a / Math.sqrt(1 - e2 * Math.sin(phi) ** 2);
  const r = [(N + h) * Math.cos(phi), 0, (N * (1 - e2) + h) * Math.sin(phi)];
  const state = {...initialState, rKm: r};
  assert.ok(Math.abs(wgs84RadiusForGeodeticKm(45, h) - Math.hypot(...r)) < 1e-9);
  const candidate = makeConditionalMsiseAtmosphere(options({
    toGeodetic: () => ({latitudeDeg: 45, longitudeDeg: 15,
      altitudeKm: h, localSolarTimeHours: 7}),
    evaluateDensityKgM3: () => 1e-12,
  }));
  assert.ok(dragAccelerationKmS2(state, candidate).every(Number.isFinite));
  assert.equal(wgs84RadiusForGeodeticKm(0, 500), a + 500);
  assert.ok(Math.abs(wgs84RadiusForGeodeticKm(90, 500) - (b + 500)) < 1e-9);
  assert.throws(() => wgs84RadiusForGeodeticKm(91, 500), /Invalid WGS84/);
});


test('G43 caller cannot substitute a matching altitude and geodesy for another Cartesian state', () => {
  let calls = 0;
  const atmosphere = makeConditionalMsiseAtmosphere(options({
    toGeodetic: () => ({latitudeDeg: 0, longitudeDeg: 0,
      altitudeKm: 600, localSolarTimeHours: 6}),
    evaluateDensityKgM3: () => { calls++; return 1e-12; },
  }));
  assert.throws(() => atmosphere.densityKgM3(600, initialState.tS, initialState),
    /radius argument disagrees/);
  assert.throws(() => atmosphere.densityKgM3(NaN, initialState.tS, initialState),
    /radius argument disagrees/);
  assert.equal(calls, 0);
});

test('G43 sourced inertial Earth pole catches wrong latitude despite exactly matching WGS84 radius', () => {
  const h = 500, a = 6378.137, b = 6356.752314245;
  const actual = {...initialState, rKm: [a + h, 0, 0]};
  // Construct a polar geodetic pair at the same radius: the G42 scalar
  // radius check is satisfied, but its axial coordinate is impossible.
  const counterfeit = () => ({latitudeDeg: 90, longitudeDeg: 0,
    altitudeKm: a + h - b, localSolarTimeHours: 6});
  assert.ok(Math.abs(wgs84RadiusForGeodeticKm(90, a + h - b) - Math.hypot(...actual.rKm)) < 1e-9);
  let calls = 0;
  const guarded = makeConditionalMsiseAtmosphere(options({
    inertialEarthPoleAtUtc: () => [0, 0, 1], earthPoleSource: 'SYNTHETIC_POLE',
    toGeodetic: counterfeit, evaluateDensityKgM3: () => { calls++; return 1e-12; },
  }));
  assert.throws(() => dragAccelerationKmS2(actual, guarded), /latitude inconsistent with sourced Earth pole/);
  assert.equal(calls, 0);
  const radiusOnly = makeConditionalMsiseAtmosphere(options({toGeodetic: counterfeit}));
  assert.ok(dragAccelerationKmS2(actual, radiusOnly).every(Number.isFinite));
  assert.match(radiusOnly.source, /axial-pole=NOT_CHECKED/);
});

test('G43 valid oblique and rotated unit poles pass; missing or invalid provenance fails', () => {
  const a = 6378.137, b = 6356.752314245, e2 = 1 - (b / a) ** 2;
  const phi = Math.PI / 4, N = a / Math.sqrt(1 - e2 * Math.sin(phi) ** 2);
  const equatorial = (N + 500) * Math.cos(phi);
  const axial = (N * (1 - e2) + 500) * Math.sin(phi);
  const state = {...initialState, rKm: [axial, equatorial, 0]};
  const opt = {
    inertialEarthPoleAtUtc: () => [1, 0, 0], earthPoleSource: 'SYNTHETIC_ROTATED_POLE',
    toGeodetic: () => ({latitudeDeg: 45, longitudeDeg: 0,
      altitudeKm: 500, localSolarTimeHours: 6}),
  };
  assert.ok(dragAccelerationKmS2(state, makeConditionalMsiseAtmosphere(options(opt))).every(Number.isFinite));
  assert.throws(() => makeConditionalMsiseAtmosphere(options({...opt, earthPoleSource: ''})),
    /Requires explicit/);
  const invalidPole = makeConditionalMsiseAtmosphere(options({
    ...opt, inertialEarthPoleAtUtc: () => [0, 0, 2],
  }));
  assert.throws(() => dragAccelerationKmS2(state, invalidPole), /Invalid sourced unit Earth pole/);
  const wrongDirection = makeConditionalMsiseAtmosphere(options({
    ...opt, inertialEarthPoleAtUtc: () => [0, 0, 1],
  }));
  assert.throws(() => dragAccelerationKmS2(state, wrongDirection), /latitude inconsistent/);
});

test('G73 definitive index windows are retrospective and reject as-of use before density', () => {
  const atNoon = deriveMsiseDriversAtUtc(snapshot, '1963-11-08T12:00:00Z');
  assert.equal(atNoon.temporalEligibility, 'RETROSPECTIVE_ONLY_NO_ASOF_FORECAST');
  assert.equal(atNoon.f107aWindowLastUtcDay, '1963-12-18');
  assert.equal(atNoon.apDailyPeriodEndExclusiveUtc, '1963-11-09T00:00:00Z');
  assert.equal(atNoon.currentApBinEndExclusiveUtc, '1963-11-08T15:00:00Z');
  const late = deriveMsiseDriversAtUtc(snapshot, '1963-11-08T23:59:59Z');
  assert.equal(late.f107aWindowLastUtcDay, '1963-12-18');
  assert.equal(late.currentApBinEndExclusiveUtc, '1963-11-09T00:00:00Z');
  const asofAudit = JSON.parse(readFileSync(new URL(
    '../research/constraints/C241-P31_space_weather_asof.json', import.meta.url)));
  assert.equal(asofAudit.prospective_driver_status, 'PROSPECTIVE_SCORE_NOT_AUTHORIZED');
  assert.deepEqual(asofAudit.rows.map(r => r.f107a_centered_window_utc_days.last),
    ['1963-12-17', '1963-12-18', '1963-12-19']);
  let calls = 0;
  for (const temporalUse of [undefined, 'PROSPECTIVE_AS_OF', '', null]) {
    assert.throws(() => makeConditionalMsiseAtmosphere(options({
      temporalUse, evaluateDensityKgM3: () => { calls++; return 1e-12; },
    })), /retrospective mode; not an as-of forecast/);
  }
  assert.equal(calls, 0);
  const retrospective = makeConditionalMsiseAtmosphere(options());
  assert.match(retrospective.source, /RETROSPECTIVE_ONLY_NOT_ASOF_FORECAST/);
  assert.ok(dragAccelerationKmS2(initialState, retrospective).every(Number.isFinite));
});
