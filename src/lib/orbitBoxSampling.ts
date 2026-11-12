/**
 * Bounded synthetic sensitivity sampling in osculating velocity space (km/s).
 * Finite points are WITNESSES of the declared box, never proof of a physical
 * enclosure, a distribution on historical states or a posterior probability.
 */
import { seededUniform } from './orbitPhysics.ts';

export type FiniteAxisInterval = readonly [number, number];
export type VelocityPoint = readonly [number, number, number];

/** Stable convex interpolation without overflow from (hi-lo) across signs. */
function convexInside(lo: number, hi: number, u: number): number {
  if (u === 0) return lo;
  if (u === 1) return hi;
  // Same-sign subtraction is finite; cross-zero products stay finite even
  // for [-MAX_VALUE,+MAX_VALUE]. Preserve subnormal singleton values.
  const value = lo <= 0 && hi >= 0
    ? lo * (1 - u) + hi * u
    : lo + (hi - lo) * u;
  if (!Number.isFinite(value) || value < lo || value > hi)
    throw new RangeError('Sample escaped the finite velocity interval');
  return Object.is(value, -0) ? 0 : value;
}

/** Midpoint, all eight corners and seeded interior draws, deduplicated.
 * Always consume three random coefficients per draw, even for singleton axes.
 * The draw count, seed and returned finite witnesses are fully reproducible.
 */
export function sampleVelocityBox(
  intervals: readonly FiniteAxisInterval[], seed: number, interiorDraws: number,
): readonly VelocityPoint[] {
  if (!Array.isArray(intervals) || intervals.length !== 3 ||
      intervals.some(range => !Array.isArray(range) || range.length !== 2 ||
        !Number.isFinite(range[0]) || !Number.isFinite(range[1]) || range[0] > range[1]))
    throw new RangeError('Expected three finite non-inverted velocity intervals');
  if (!Number.isSafeInteger(seed) || seed < 1 || seed > 0xffffffff ||
      !Number.isInteger(interiorDraws) || interiorDraws < 0 || interiorDraws > 100)
    throw new RangeError('Require uint32 seed and 0–100 synthetic interior draws');

  const unique = new Set<string>();
  const samples: VelocityPoint[] = [];
  const add = (weights: VelocityPoint): void => {
    const sample = intervals.map(([lo, hi], i) => convexInside(lo, hi, weights[i])) as
      [number, number, number];
    const key = sample.join(',');
    if (!unique.has(key)) { unique.add(key); samples.push(sample); }
  };
  add([0.5, 0.5, 0.5]);
  for (let mask = 0; mask < 8; mask++)
    add([(mask & 1) ? 1 : 0, (mask & 2) ? 1 : 0, (mask & 4) ? 1 : 0]);
  const rng = seededUniform(seed);
  for (let i = 0; i < interiorDraws; i++) add([rng(), rng(), rng()]);
  return samples;
}
