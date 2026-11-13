/**
 * C241-L12 primary NASA/Goddard 1963-10-15 compiled apogee, perigee and
 * inclination supply a physical CONDITIONING SCENARIO, not a tracking epoch,
 * osculating state, RAAN or historical orbit. Unlike SGP4 TEME, the RK4/J2
 * state below is constructed explicitly in an axis-aligned inertial scenario.
 *
 * First-order secular nodal regression is compared to an independently
 * integrated Cartesian r/v state under the SAME Earth constants. Osculating
 * phase is intentionally varied; agreement is a model benchmark, not a fit
 * or instrumental 527/529 holdout. C197#1 1963-11-15 supplies decay day only.
 */
import {
  EARTH, propagate,
} from './orbitPhysics.ts';
import type { State } from './orbitPhysics.ts';

export interface NodalScenario {
  /** Exact matrix or ledger occurrence; existence is not authenticated here. */
  readonly sourceOccurrence: string;
  readonly perigeeAltitudeKm: number;
  readonly apogeeAltitudeKm: number;
  readonly inclinationDeg: number;
  /** Arbitrary scenario phase, never an observed true anomaly. */
  readonly trueAnomalyDeg: number;
  readonly durationS: number;
  readonly stepS: number;
}
export interface NodalBenchmark {
  readonly classification: 'CONDITIONAL_J2_MODEL_BENCHMARK';
  readonly sourceOccurrence: string;
  readonly scenarioRaanDeg: 0;
  readonly scenarioArgumentOfPerigeeDeg: 0;
  readonly scenarioTrueAnomalyDeg: number;
  readonly semiMajorAxisKm: number;
  readonly eccentricity: number;
  readonly firstOrderJ2DegPerDay: number;
  readonly integratedJ2DegPerDay: number;
  readonly integratedTwoBodyDegPerDay: number;
  readonly refinementDifferenceDegPerDay: number;
  readonly differenceFromFirstOrderDegPerDay: number;
  readonly historicalHoldout: 'NOT_RUN';
  readonly historicNodalLongitude: null;
  readonly condeImpact: 'NOT_EVALUABLE';
}

const degrees = (rad: number): number => rad * 180 / Math.PI;
const radians = (deg: number): number => deg * Math.PI / 180;
const periodDays = 86400;
const norm3 = (v: readonly number[]): number => Math.hypot(v[0], v[1], v[2]);

/** Ascending-node longitude from k cross (r cross v) in axis-aligned ECI. */
export function ascendingNodeDeg(state: State): number {
  const [x, y, z] = state.rKm;
  const [vx, vy, vz] = state.vKmS;
  const nx = x * vz - z * vx; // -h_y
  const ny = y * vz - z * vy; // +h_x
  if (!Number.isFinite(nx) || !Number.isFinite(ny) ||
      norm3([nx, ny, 0]) <= 1e-12) {
    throw new RangeError('Ascending node undefined (equatorial or nonfinite state)');
  }
  return degrees(Math.atan2(ny, nx));
}
const signedAngleDeg = (end: number, start: number): number => {
  const d = radians(end - start);
  return degrees(Math.atan2(Math.sin(d), Math.cos(d)));
};

/** Explicit Kepler-to-Cartesian SCENARIO; no inverse TLE or historical fitting. */
export function scenarioOsculatingState(input: NodalScenario): State {
  const {
    perigeeAltitudeKm: hp, apogeeAltitudeKm: ha, inclinationDeg: i,
    trueAnomalyDeg: f, durationS, stepS, sourceOccurrence,
  } = input;
  if (!sourceOccurrence?.trim() ||
      ![hp, ha, i, f, durationS, stepS].every(Number.isFinite) ||
      hp < 150 || ha < hp || ha > 50000 ||
      i <= 1 || i >= 179 || f < 0 || f >= 360 ||
      durationS <= 0 || durationS > 3 * periodDays ||
      stepS <= 0 || stepS > 120 ||
      Math.ceil(durationS / (stepS / 2)) > 200000) {
    throw new RangeError('Invalid sourced J2 scenario or numerical controls');
  }
  const rp = EARTH.radiusKm + hp, ra = EARTH.radiusKm + ha;
  const a = (rp + ra) / 2, e = (ra - rp) / (ra + rp);
  if (e >= 0.1) throw new RangeError('First-order near-circular benchmark requires e < 0.1');
  const p = a * (1 - e * e);
  const nu = radians(f), inc = radians(i);
  const r = p / (1 + e * Math.cos(nu));
  const speed = Math.sqrt(EARTH.muKm3S2 / p);
  // Omega = 0, argument of perigee = 0, arbitrary phase true anomaly = nu.
  // Rotation about the x-axis yields an inclination i to the Earth equator.
  return {
    rKm: [r * Math.cos(nu), r * Math.sin(nu) * Math.cos(inc), r * Math.sin(nu) * Math.sin(inc)],
    vKmS: [-speed * Math.sin(nu), speed * (e + Math.cos(nu)) * Math.cos(inc),
      speed * (e + Math.cos(nu)) * Math.sin(inc)],
    tS: 0,
  };
}

/**
 * Conditional J2 secular regression vs finite-duration RK4 result (degrees/day).
 * Halving steps tests discretization; the two-body control must have ~zero
 * nodal drift. Short-period J2 oscillations and unknown true anomaly mean the
 * finite-duration result is NOT expected to equal the averaged analytic rate.
 */
export function compareJ2NodalDrift(input: NodalScenario): NodalBenchmark {
  const initial = scenarioOsculatingState(input);
  const rp = EARTH.radiusKm + input.perigeeAltitudeKm;
  const ra = EARTH.radiusKm + input.apogeeAltitudeKm;
  const a = (rp + ra) / 2, e = (ra - rp) / (ra + rp);
  const p = a * (1 - e * e);
  const meanMotionRadS = Math.sqrt(EARTH.muKm3S2 / a ** 3);
  const analytic = degrees(-1.5 * meanMotionRadS * EARTH.j2 *
    (EARTH.radiusKm / p) ** 2 * Math.cos(radians(input.inclinationDeg))) * periodDays;
  const initialNode = ascendingNodeDeg(initial);
  const rate = (step: number, j2: boolean): number => {
    const propagation = propagate(initial, input.durationS, step, 80, { j2 });
    if (propagation.event !== 'elapsed') {
      throw new RangeError('Scenario reached stopping altitude; no nodal benchmark');
    }
    return signedAngleDeg(ascendingNodeDeg(propagation.state), initialNode) *
      periodDays / input.durationS;
  };
  const coarse = rate(input.stepS, true);
  const fine = rate(input.stepS / 2, true);
  const nullControl = rate(input.stepS / 2, false);
  return {
    classification: 'CONDITIONAL_J2_MODEL_BENCHMARK',
    sourceOccurrence: input.sourceOccurrence,
    scenarioRaanDeg: 0,
    scenarioArgumentOfPerigeeDeg: 0,
    scenarioTrueAnomalyDeg: input.trueAnomalyDeg,
    semiMajorAxisKm: a,
    eccentricity: e,
    firstOrderJ2DegPerDay: analytic,
    integratedJ2DegPerDay: fine,
    integratedTwoBodyDegPerDay: nullControl,
    refinementDifferenceDegPerDay: Math.abs(coarse - fine),
    differenceFromFirstOrderDegPerDay: fine - analytic,
    historicalHoldout: 'NOT_RUN',
    historicNodalLongitude: null,
    condeImpact: 'NOT_EVALUABLE',
  };
}
