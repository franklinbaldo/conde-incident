import test from 'node:test';
import assert from 'node:assert/strict';
import { EARTH, propagate } from '../src/lib/orbitPhysics.ts';
import { evaluateAlternativeOrbitFits } from '../src/lib/orbitAlternativeFits.ts';

// ALL premisses, states, epochs and observations here are SYNTHETIC.
// "Alternatives" are not reconstructed RAANs, original 1963 TLEs, or Lean proofs.
const epoch = '1963-10-27T00:00:00.000Z';
const cutoff = '1963-10-27T00:28:00.000Z';
const frame = 'SYNTHETIC_INERTIAL_CARTESIAN';
const v = Math.sqrt(EARTH.muKm3S2 / (EARTH.radiusKm + 500));
const initial = { rKm: [EARTH.radiusKm + 500, 0, 0], vKmS: [0, v, 0], tS: 0 };
const syntheticTruth = { ...initial, vKmS: [0.002, v + 0.004, -0.002] };
const dynamics = { j2: true };
const bound = (axis, low, high, tag) => ({
  axis, lowerKmS: low, upperKmS: high,
  evidenceOccurrence: 'SYNTHETIC-' + tag, sourceLineage: 'generated test ' + tag,
  leanPredicate: 'NOT_AVAILABLE', premiseStatus: 'SYNTHETIC',
  epochUtc: epoch, inertialFrame: frame,
});
const box = (tag, vxLo, vxHi, vyLo = v, vyHi = v + 0.007) => [
  bound('vx', vxLo, vxHi, tag), bound('vy', vyLo, vyHi, tag),
  bound('vz', -0.004, 0, tag),
];
const alternative = (id, bounds, state = initial) => ({
  alternativeId: id, sourceLineage: 'synthetic branch ' + id,
  scenario: { objectNorad: 529, epochUtc: epoch, inertialFrame: frame,
    initial: state, bounds },
});
const obs = (state, seconds) => ({
  objectNorad: 529, inertialFrame: frame, elapsedS: seconds,
  epochUtc: new Date(Date.parse(epoch) + seconds * 1000).toISOString(),
  source: 'SYNTHETIC generator, no independent historical observation',
  rKm: propagate(state, seconds, 2, 80, dynamics).state.rKm,
});
const training = [600, 1200, 1500].map(s => obs(syntheticTruth, s));
const future = [2400, 2800].map(s => obs(initial, s));
const controls = {
  stepS: 40, terminationAltitudeKm: 80, gridStepKmS: 0.003, rounds: 9,
  convergence: { halvings: 3, tolerance: {
    positionKm: 0.1, velocityKmS: 0.0001, epochS: 0.02,
  } },
};
const run = (cases, train = training, heldout = future) =>
  evaluateAlternativeOrbitFits(cases, cutoff, train, heldout, controls, dynamics);

test('two disjoint SYNTHETIC velocity branches remain separate and bounded', () => {
  const a = alternative('SYNTHETIC_A', box('A', 0, 0.004));
  const b = alternative('SYNTHETIC_B', box('B', 0.08, 0.09));
  const result = run([a, b]);
  assert.equal(result.evaluations.length, 2);
  assert.deepEqual(result.evaluations.map(x => x.calibration.domain.status),
    ['BOUNDED', 'BOUNDED'], 'intersection across A and B would be EMPTY');
  for (const [i, item] of result.evaluations.entries()) {
    const vx = item.calibration.fit.fittedState.vKmS[0];
    assert.ok(vx >= [0, 0.08][i] && vx <= [0.004, 0.09][i]);
  }
  assert.equal(result.evaluations[0].calibration.status, 'CALIBRATED_CONDITIONALLY');
  assert.ok(result.evaluations[0].calibration.holdout.levels.at(-1).deltaRmsKm > 0,
    'negative future holdout survives despite better synthetic training');
  assert.equal(result.selectedAlternativeId, null, 'never pick a branch from future scores');
  assert.equal(result.branchSetExhaustive, false);
  assert.equal(result.historicLocation, 'INDETERMINATE');
  assert.equal(result.groundImpact, 'NOT_SUPPORTED');
  assert.equal(result.leanHistoricalProof, 'NOT_RUN');
  assert.equal(result.sgp4Baseline, 'NOT_RUN');
});

test('one contradictory premise does not poison another viable branch', () => {
  const invalid = alternative('CONTRADICTORY', [
    ...box('conflict', 0, 0.001), bound('vx', 0.02, 0.03, 'conflict'),
  ]);
  const viable = alternative('VIABLE', box('viable', 0, 0.004));
  const r = run([invalid, viable]);
  assert.equal(r.evaluations[0].calibration.status, 'NOT_RUN_EMPTY');
  assert.equal(r.evaluations[0].calibration.fit, null);
  assert.equal(r.evaluations[1].calibration.domain.status, 'BOUNDED');
  assert.equal(r.selectedAlternativeId, null,
    'a remaining viable mathematical branch is not automatically historically true');
});

test('no invented prior or solution when one branch has an unbounded velocity', () => {
  const partial = alternative('PARTIAL', box('p', 0, 0.001).slice(0, 2));
  const r = run([partial]);
  assert.equal(r.evaluations[0].calibration.status, 'NOT_RUN_UNBOUNDED');
  assert.equal(r.evaluations[0].calibration.fit, null);
  assert.equal(r.independentObservationsVerified, false);
});

test('reject duplicate IDs and missing documentary lineage before fitting', () => {
  const a = alternative('A', box('a', 0, 0));
  assert.throws(() => run([a, a]), /Duplicate/);
  assert.throws(() => run([{ ...a, sourceLineage: '' }]), /lineage/);
  assert.throws(() => run([{ ...a, alternativeId: 'bad id' }]), /alternative/);
  assert.throws(() => run([]), /1–12/);
});

test('reject mixing incompatible epoch, frame and object, rather than comparing numbers', () => {
  const a = alternative('A', box('a', 0, 0.004));
  assert.throws(() => run([a, {
    ...a, alternativeId: 'B', scenario: { ...a.scenario, inertialFrame: 'TEME' },
  }]), /mixed target\/epoch\/frame/);
  assert.throws(() => run([a, {
    ...a, alternativeId: 'B', scenario: { ...a.scenario, objectNorad: 527 },
  }]), /mixed target\/epoch\/frame/);
  assert.throws(() => run([a, {
    ...a, alternativeId: 'B', scenario: { ...a.scenario,
      epochUtc: '1963-10-28T00:00:00.000Z' },
  }]), /mixed target\/epoch\/frame/);
});

test('shared predeclared future is rejected if it leaks into training or uses wrong frame', () => {
  const a = alternative('A', box('a', 0, 0.004));
  assert.throws(() => run([a], [training[0], future[0]]), /leakage/);
  assert.throws(() => run([a], training, [{ ...future[0],
    inertialFrame: 'TEME' }]), /Mixed target/);
  assert.throws(() => run([a], training, [{ ...future[0],
    source: '' }]), /provenance/);
});
