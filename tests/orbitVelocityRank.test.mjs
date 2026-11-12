import test from 'node:test';
import assert from 'node:assert/strict';
import { pivotVelocityResponseRank } from '../src/lib/orbitVelocityRank.ts';

// These are SYNTHETIC Euclidean response columns in km, NOT NORAD tracking.

test('pivoting removes false extra rank from a weak first Cartesian response', () => {
  const weak = [1, 0, 0];
  const strong = [10, 0.11, 0];
  const result = pivotVelocityResponseRank([weak, strong], 0.1);
  assert.equal(result.rankAtThreshold, 1);
  assert.deepEqual(result.pivotOrder, [1],
    'strong near-parallel response must be chosen before the weak one');
  assert.ok(result.columns[0].independentNormKm < 0.1);
  assert.equal(result.columns[0].entersBasis, false);
  assert.equal(result.columns[1].entersBasis, true);
});

test('permuting axes must not change numerical rank in a near-degenerate case', () => {
  const weak = [1, 0, 0];
  const strong = [10, 0.11, 0];
  const transverse = [0, 0, 2];
  const a = pivotVelocityResponseRank([weak, strong, transverse], 0.1);
  const b = pivotVelocityResponseRank([transverse, weak, strong], 0.1);
  assert.equal(a.rankAtThreshold, 2);
  assert.equal(b.rankAtThreshold, 2);
  assert.equal(a.columns[0].entersBasis, false);
  assert.equal(b.columns[1].entersBasis, false);
  assert.deepEqual(new Set(a.pivotOrder), new Set([1, 2]));
  assert.deepEqual(new Set(b.pivotOrder), new Set([0, 2]));
});

test('three independent directions still produce rank three and reproduce exactly', () => {
  const responses = [[2, 0, 0], [0, 3, 0], [0, 0, 4]];
  const a = pivotVelocityResponseRank(responses, 0.1);
  const b = pivotVelocityResponseRank(responses, 0.1);
  assert.deepEqual(a, b);
  assert.equal(a.rankAtThreshold, 3);
  assert.deepEqual(a.pivotOrder, [2, 1, 0]);
  assert.ok(a.columns.every(c => c.entersBasis));
});

test('two perfectly collinear probes and a zero response cannot fabricate rank', () => {
  const result = pivotVelocityResponseRank(
    [[1, 0, 0], [-4, 0, 0], [0, 0, 0]], 0.01);
  assert.equal(result.rankAtThreshold, 1);
  assert.equal(result.pivotOrder[0], 1);
  assert.ok(result.columns.filter(c => c.entersBasis).length === 1);
  const atStart = pivotVelocityResponseRank([[0, 0, 0]], 0.01);
  assert.equal(atStart.rankAtThreshold, 0);
  assert.equal(atStart.columns[0].independentNormKm, 0);
  assert.equal(pivotVelocityResponseRank([], 0.01).rankAtThreshold, 0);
});

test('the declared km threshold changes the local rank, not historical evidence', () => {
  const responses = [[1, 0, 0], [0, 0.05, 0], [0, 0, 0.005]];
  assert.equal(pivotVelocityResponseRank(responses, 0.1).rankAtThreshold, 1);
  assert.equal(pivotVelocityResponseRank(responses, 0.01).rankAtThreshold, 2);
  assert.equal(pivotVelocityResponseRank(responses, 0.001).rankAtThreshold, 3);
});

test('invalid response shapes and nonfinite arithmetic refuse a rank', () => {
  assert.throws(() => pivotVelocityResponseRank([[1, 2]], 0.01), /3D position/);
  assert.throws(() => pivotVelocityResponseRank([[1, 0, 0], [1, 0, 0, 1, 0, 0]], 0.01),
    /same nonempty/);
  assert.throws(() => pivotVelocityResponseRank([[1, 0, 0]], 0), /positive finite/);
  assert.equal(pivotVelocityResponseRank([[Number.NaN, 0, 0]], 0.01), null);
  assert.equal(pivotVelocityResponseRank([[Number.MAX_VALUE, Number.MAX_VALUE, 0]], 0.01), null);
});
