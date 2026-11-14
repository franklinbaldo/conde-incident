/**
 * Experimental osculating Cartesian dynamics in an Earth-centred inertial frame.
 * Coordinates: km, km/s, elapsed s. NOT a SGP4/TLE propagator. An SGP4 mean
 * element set cannot be passed as Cartesian osculating data without conversion.
 * WGS-84-like constants below are mathematical model inputs, not 1963 observations.
 */
export type Vec3 = readonly [number, number, number];
export interface State { readonly rKm: Vec3; readonly vKmS: Vec3; readonly tS: number }
export interface Atmosphere {
  /** Source-identified density supplied by the caller. No historical defaults. */
  readonly densityKgM3: (altitudeKm: number, tS: number, state: State) => number;
  /** Cd*A/m, m^2/kg. Cannot be inferred from a NORAD identifier. */
  readonly cdAreaOverMassM2Kg: number;
  readonly source: string;
}
export interface Dynamics {
  readonly j2?: boolean;
  readonly atmosphere?: Atmosphere;
}
export interface Propagation {
  readonly state: State;
  readonly event: 'elapsed' | 'reentry-threshold';
  readonly steps: number;
}
export const EARTH = Object.freeze({ muKm3S2: 398600.4418, radiusKm: 6378.137, j2: 1.08262668e-3, spinRadS: 7.2921150e-5 });

/** Numerical RK4 failure, not evidence that an admissible physical scenario is false. */
export class NumericalIntegrationBreakdown extends RangeError {
  constructor() {
    super('RK4 trajectory left the representable finite phase space');
    this.name = 'NumericalIntegrationBreakdown';
  }
}

const add = (a: Vec3, b: Vec3): Vec3 => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const scale = (a: Vec3, q: number): Vec3 => [a[0] * q, a[1] * q, a[2] * q];
const dot = (a: Vec3, b: Vec3): number => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const norm = (v: Vec3): number => Math.sqrt(dot(v, v));
const finiteVec = (v: Vec3): boolean => v.length === 3 && v.every(Number.isFinite);
export const altitudeKm = (s: State): number => norm(s.rKm) - EARTH.radiusKm;
export const angularMomentumZ = (s: State): number => s.rKm[0] * s.vKmS[1] - s.rKm[1] * s.vKmS[0];

export function potentialKm2S2(s: State, j2 = false): number {
  const r = norm(s.rKm);
  const z2 = (s.rKm[2] / r) ** 2;
  return -EARTH.muKm3S2 / r * (1 - (j2 ? EARTH.j2 * (EARTH.radiusKm / r) ** 2 * (3 * z2 - 1) / 2 : 0));
}
export function specificEnergyKm2S2(s: State, j2 = false): number {
  return dot(s.vKmS, s.vKmS) / 2 + potentialKm2S2(s, j2);
}
export function rotatingFrameIntegralKm2S2(s: State, j2 = false): number {
  return specificEnergyKm2S2(s, j2) - EARTH.spinRadS * angularMomentumZ(s);
}

export function accelerationKmS2(s: State, dynamics: Dynamics = {}): Vec3 {
  const r = norm(s.rKm);
  if (!finiteVec(s.rKm) || !finiteVec(s.vKmS) || !Number.isFinite(s.tS) || !(r > EARTH.radiusKm * 0.5)) {
    throw new RangeError('Nonfinite or invalid osculating state');
  }
  const central = -EARTH.muKm3S2 / r ** 3;
  let acceleration = scale(s.rKm, central);
  if (dynamics.j2) {
    const z2OverR2 = (s.rKm[2] / r) ** 2;
    const factor = 1.5 * EARTH.j2 * EARTH.muKm3S2 * EARTH.radiusKm ** 2 / r ** 5;
    acceleration = add(acceleration, [
      factor * s.rKm[0] * (5 * z2OverR2 - 1),
      factor * s.rKm[1] * (5 * z2OverR2 - 1),
      factor * s.rKm[2] * (5 * z2OverR2 - 3),
    ]);
  }
  if (dynamics.atmosphere) acceleration = add(acceleration, dragAccelerationKmS2(s, dynamics.atmosphere));
  return acceleration;
}

/**
 * Co-rotating atmospheric drag isolated for a physical-work audit. The same
 * term is used by the RK4 force, so an audit cannot silently use another drag
 * law. Density and ballistic parameter are ALWAYS explicit source inputs.
 */
export function dragAccelerationKmS2(s: State, atmosphere: Atmosphere): Vec3 {
  const r = norm(s.rKm);
  if (!finiteVec(s.rKm) || !finiteVec(s.vKmS) || !Number.isFinite(s.tS) || !(r > EARTH.radiusKm * 0.5))
    throw new RangeError('Nonfinite or invalid osculating state');
  const { densityKgM3, cdAreaOverMassM2Kg, source } = atmosphere;
  if (typeof source !== 'string' || !source.trim() ||
      !Number.isFinite(cdAreaOverMassM2Kg) || cdAreaOverMassM2Kg < 0)
    throw new RangeError('Atmospheric model requires source and nonnegative Cd*A/m');
  const rho = densityKgM3(r - EARTH.radiusKm, s.tS, s);
  if (!Number.isFinite(rho) || rho < 0) throw new RangeError('Density must be finite and nonnegative');
  const relative: Vec3 = [
    s.vKmS[0] + EARTH.spinRadS * s.rKm[1],
    s.vKmS[1] - EARTH.spinRadS * s.rKm[0],
    s.vKmS[2],
  ];
  // SI drag -> km/s²: (1/2)*rho*(Cd*A/m)*(1000*vKmS)^2/1000.
  return scale(relative, -500 * rho * cdAreaOverMassM2Kg * norm(relative));
}

/** Drag power on the Jacobi-like E - omega*Lz integral (km²/s³).
 * For any admissible nonnegative density/Cd*A/m it must be <= 0.
 */
export function dragJacobiPowerKm2S3(s: State, atmosphere: Atmosphere): number {
  const relative: Vec3 = [
    s.vKmS[0] + EARTH.spinRadS * s.rKm[1],
    s.vKmS[1] - EARTH.spinRadS * s.rKm[0],
    s.vKmS[2],
  ];
  return dot(dragAccelerationKmS2(s, atmosphere), relative);
}

export function rk4(s: State, dtS: number, dynamics: Dynamics = {}): State {
  if (!Number.isFinite(dtS) || dtS <= 0) throw new RangeError('RK4 step must be finite and positive');
  const derivative = (q: State) => {
    // A finite domain endpoint does NOT guarantee numerically representable
    // intermediate states. Keep a distinct error from invalid force inputs.
    if (!finiteVec(q.rKm) || !finiteVec(q.vKmS) || !Number.isFinite(q.tS) ||
        !Number.isFinite(norm(q.rKm)) || !Number.isFinite(norm(q.vKmS)))
      throw new NumericalIntegrationBreakdown();
    const dv = accelerationKmS2(q, dynamics);
    if (!finiteVec(dv)) throw new NumericalIntegrationBreakdown();
    return { dr: q.vKmS, dv };
  };
  const shifted = (q: State, k: {dr: Vec3; dv: Vec3}, h: number): State => ({
    rKm: add(q.rKm, scale(k.dr, h)), vKmS: add(q.vKmS, scale(k.dv, h)), tS: q.tS + h,
  });
  const k1 = derivative(s);
  const k2 = derivative(shifted(s, k1, dtS / 2));
  const k3 = derivative(shifted(s, k2, dtS / 2));
  const k4 = derivative(shifted(s, k3, dtS));
  const sum = (key: 'dr' | 'dv'): Vec3 => scale(add(add(k1[key], scale(k2[key], 2)), add(scale(k3[key], 2), k4[key])), dtS / 6);
  const next: State = { rKm: add(s.rKm, sum('dr')),
    vKmS: add(s.vKmS, sum('dv')), tS: s.tS + dtS };
  if (!finiteVec(next.rKm) || !finiteVec(next.vKmS) ||
      !Number.isFinite(next.tS) || !Number.isFinite(norm(next.rKm)) ||
      !Number.isFinite(norm(next.vKmS)))
    throw new NumericalIntegrationBreakdown();
  return next;
}

export function propagate(
  initial: State,
  durationS: number,
  stepS: number,
  terminationAltitudeKm: number,
  dynamics: Dynamics = {},
): Propagation {
  if (!Number.isFinite(durationS) || durationS < 0 || !Number.isFinite(stepS) || stepS <= 0 ||
      !Number.isFinite(terminationAltitudeKm) || terminationAltitudeKm < 0 ||
      !Number.isSafeInteger(Math.ceil(durationS / stepS)) || Math.ceil(durationS / stepS) > 1_000_000) {
    throw new RangeError('Invalid duration, step or explicit reentry threshold');
  }
  // Validate before the zero-duration or below-threshold fast paths. Otherwise
  // an invalid state can be returned as a seemingly successful physical result.
  // The guard matches the finite phase-space domain used by RK4 itself.
  if (!initial || !Array.isArray(initial.rKm) || !finiteVec(initial.rKm) ||
      !Array.isArray(initial.vKmS) || !finiteVec(initial.vKmS) ||
      !Number.isFinite(initial.tS) ||
      !Number.isFinite(norm(initial.rKm)) ||
      !Number.isFinite(norm(initial.vKmS)) ||
      !(norm(initial.rKm) > EARTH.radiusKm * 0.5))
    throw new RangeError('Invalid initial osculating state');
  // A threshold is a stopping convention, NOT a measured breakup or impact altitude.
  if (altitudeKm(initial) <= terminationAltitudeKm) return { state: initial, event: 'reentry-threshold', steps: 0 };
  let current = initial;
  let count = 0;
  while (current.tS - initial.tS < durationS - 1e-10) {
    const step = Math.min(stepS, durationS - (current.tS - initial.tS));
    const next = rk4(current, step, dynamics);
    count++;
    // The endpoint can be ABOVE the threshold even though the orbit passed
    // BELOW it at perigee inside this step. A plain endpoint check misses that
    // *first* descending crossing and can falsely report elapsed.
    let eventUpperS: number | null = altitudeKm(next) <= terminationAltitudeKm ? step : null;
    if (eventUpperS === null &&
        dot(current.rKm, current.vKmS) < 0 && dot(next.rKm, next.vKmS) >= 0) {
      // A negative-to-positive radial derivative brackets perigee. As with
      // RK4 itself, the chosen step must resolve a SINGLE radial turning point.
      let low = 0, high = step;
      for (let i = 0; i < 42; i++) {
        const mid = (low + high) / 2;
        const sample = rk4(current, mid, dynamics);
        if (dot(sample.rKm, sample.vKmS) < 0) low = mid;
        else high = mid;
      }
      if (altitudeKm(rk4(current, high, dynamics)) <= terminationAltitudeKm) eventUpperS = high;
    }
    if (eventUpperS !== null) {
      // The event is bracketed on the DESCENDING arc, even if the step ends
      // above the threshold. Reintegrate r AND v from the same prior state.
      let low = 0, high = eventUpperS;
      for (let i = 0; i < 42; i++) {
        const mid = (low + high) / 2;
        if (altitudeKm(rk4(current, mid, dynamics)) > terminationAltitudeKm) low = mid;
        else high = mid;
      }
      return { state: rk4(current, high, dynamics), event: 'reentry-threshold', steps: count };
    }
    current = next;
  }
  return { state: current, event: 'elapsed', steps: count };
}

/** Observable positions must be in the SAME inertial frame and units as initial state. */
export interface PositionObservation {
  readonly elapsedS: number;
  readonly rKm: Vec3;
  readonly source: string;
}
export function positionResidualRmsKm(
  initial: State, observations: readonly PositionObservation[], stepS: number,
  terminationAltitudeKm: number, dynamics: Dynamics = {},
): number {
  if (!observations.length) throw new RangeError('No observations');
  let error2 = 0;
  for (const o of observations) {
    if (!o.source.trim() || !finiteVec(o.rKm) || !Number.isFinite(o.elapsedS) || o.elapsedS < 0)
      throw new RangeError('Observation needs provenance, inertial position, elapsed time');
    const predicted = propagate(initial, o.elapsedS, stepS, terminationAltitudeKm, dynamics);
    if (predicted.event !== 'elapsed') return Infinity;
    const residual = add(predicted.state.rKm, scale(o.rKm, -1));
    error2 += dot(residual, residual);
  }
  return Math.sqrt(error2 / observations.length);
}

/** Coarse-to-fine deterministic inverse fit: initial velocity only, not a historical orbit solution. */
export function fitInitialVelocity(
  initial: State, observations: readonly PositionObservation[], stepS: number,
  terminationAltitudeKm: number, initialGridStepKmS: number, rounds = 8,
  dynamics: Dynamics = {},
): { state: State; rmsKm: number; evaluations: number } {
  if (!Number.isFinite(initialGridStepKmS) || initialGridStepKmS <= 0 || !Number.isInteger(rounds) || rounds < 1 || rounds > 30)
    throw new RangeError('Invalid inverse fit controls');
  let state = initial;
  let best = positionResidualRmsKm(state, observations, stepS, terminationAltitudeKm, dynamics);
  let evaluations = 1;
  let delta = initialGridStepKmS;
  for (let round = 0; round < rounds; round++) {
    for (let axis = 0; axis < 3; axis++) {
      let improved = true;
      while (improved) {
        improved = false;
        for (const sign of [-1, 1]) {
          const v = [...state.vKmS] as [number, number, number];
          v[axis] += sign * delta;
          const candidate = { ...state, vKmS: v as Vec3 };
          const score = positionResidualRmsKm(candidate, observations, stepS, terminationAltitudeKm, dynamics);
          evaluations++;
          if (score + 1e-12 < best) { state = candidate; best = score; improved = true; break; }
        }
      }
    }
    delta /= 2;
  }
  return { state, rmsKm: best, evaluations };
}

/** xorshift32: reproducible sampling, neither calibrated nor a posterior distribution. */
export function seededUniform(seed: number): () => number {
  if (!Number.isSafeInteger(seed) || seed < 1 || seed > 0xffffffff) throw new RangeError('Seed must be a positive uint32');
  let x = seed >>> 0;
  return () => {
    x ^= x << 13; x ^= x >>> 17; x ^= x << 5;
    return (x >>> 0) / 0x100000000;
  };
}
export function propagateEnsemble(
  initial: State, seed: number, count: number,
  velocityPerturbationKmS: number, durationS: number, stepS: number,
  terminationAltitudeKm: number, dynamics: Dynamics = {},
): readonly Propagation[] {
  if (!Number.isInteger(count) || count < 1 || count > 10000 ||
      !Number.isFinite(velocityPerturbationKmS) || velocityPerturbationKmS < 0)
    throw new RangeError('Invalid ensemble controls');
  const rng = seededUniform(seed);
  return Array.from({ length: count }, () => {
    const perturbation = [rng(), rng(), rng()].map(x => (2 * x - 1) * velocityPerturbationKmS) as [number, number, number];
    return propagate({ ...initial, vKmS: add(initial.vKmS, perturbation) }, durationS, stepS, terminationAltitudeKm, dynamics);
  });
}


/** Chronological *Cartesian* positions for a predeclared 527/529 validation split.
 * A source label is necessary for provenance but does not prove independence.
 * The caller must establish that the same frame/epochs are scientifically valid.
 */
export interface TimedOrbitPosition extends PositionObservation {
  readonly objectNorad: 527 | 529;
  readonly epochUtc: string;
  readonly inertialFrame: string;
}
export interface PreCutoffOrbitFit {
  readonly objectNorad: 527 | 529;
  readonly initialEpochUtc: string;
  readonly cutoffEpochUtc: string;
  readonly inertialFrame: string;
  readonly initialState: State;
  readonly fittedState: State;
  readonly trainingBaselineRmsKm: number;
  readonly trainingFittedRmsKm: number;
  readonly evaluations: number;
  readonly trainingCount: number;
  readonly stepS: number;
  readonly terminationAltitudeKm: number;
  readonly dynamics: Dynamics;
}
export interface FutureOrbitScore {
  readonly baselineRmsKm: number;
  readonly fittedRmsKm: number;
  /** Positive means fitted model did WORSE than the unfitted control. */
  readonly deltaRmsKm: number | null;
  readonly observationCount: number;
}

export function utcMilliseconds(iso: string): number {
  // Explicit UTC only: no local-time conversions and no guessed historical timezone.
  if (typeof iso !== 'string' || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?Z$/.test(iso))
    throw new RangeError('Observation epochs must be explicit ISO-8601 UTC timestamps');
  const ms = Date.parse(iso);
  if (!Number.isFinite(ms) || new Date(ms).toISOString().slice(0, 19) !== iso.slice(0, 19))
    throw new RangeError('Invalid calendar date in observation UTC epoch');
  return ms;
}

export function validateTimedPositions(
  observations: readonly TimedOrbitPosition[],
  objectNorad: 527 | 529,
  inertialFrame: string,
  initialEpochMs: number,
  cutoffEpochMs: number,
  side: 'training' | 'holdout',
): void {
  let previousEpochMs = initialEpochMs;
  for (const observation of observations) {
    const epochMs = utcMilliseconds(observation.epochUtc);
    if (observation.objectNorad !== objectNorad || observation.inertialFrame !== inertialFrame ||
        typeof observation.source !== 'string' || !observation.source.trim() ||
        !finiteVec(observation.rKm) || !Number.isFinite(observation.elapsedS) ||
        Math.abs(observation.elapsedS - (epochMs - initialEpochMs) / 1000) > 0.001 ||
        epochMs <= previousEpochMs ||
        (side === 'training' ? epochMs > cutoffEpochMs : epochMs <= cutoffEpochMs)) {
      throw new RangeError('Mixed target/frame, missing provenance, inconsistent UTC, or chronological leakage');
    }
    previousEpochMs = epochMs;
  }
}

/** Fit stage: accepts ONLY observations at or before a predeclared UTC cutoff.
 * No held-out observations enter this function or its inverse solver.
 */
export function fitPreCutoffOrbit(
  initial: State, objectNorad: 527 | 529,
  initialEpochUtc: string, cutoffEpochUtc: string, inertialFrame: string,
  training: readonly TimedOrbitPosition[], stepS: number,
  terminationAltitudeKm: number, initialGridStepKmS: number,
  rounds = 8, dynamics: Dynamics = {},
): PreCutoffOrbitFit {
  if ((objectNorad !== 527 && objectNorad !== 529) ||
      typeof inertialFrame !== 'string' || !inertialFrame.trim() ||
      training.length < 2) throw new RangeError('Require NORAD 527/529, a named inertial frame, and >=2 training positions');
  const initialMs = utcMilliseconds(initialEpochUtc);
  const cutoffMs = utcMilliseconds(cutoffEpochUtc);
  if (cutoffMs <= initialMs) throw new RangeError('Training cutoff must follow initial epoch');
  validateTimedPositions(training, objectNorad, inertialFrame, initialMs, cutoffMs, 'training');
  const trainingBaselineRmsKm = positionResidualRmsKm(initial, training, stepS, terminationAltitudeKm, dynamics);
  const fit = fitInitialVelocity(initial, training, stepS, terminationAltitudeKm, initialGridStepKmS, rounds, dynamics);
  return {
    objectNorad, initialEpochUtc, cutoffEpochUtc, inertialFrame, initialState: initial,
    fittedState: fit.state, trainingBaselineRmsKm, trainingFittedRmsKm: fit.rmsKm,
    evaluations: fit.evaluations, trainingCount: training.length,
    stepS, terminationAltitudeKm, dynamics,
  };
}

/** Scoring stage: evaluates future positions without updating the fitted state.
 * This is only a *blind* test if the source observations were withheld during fit.
 * Infinity means a model reached its numerical threshold before an observation.
 */
export function scoreFutureOrbit(
  fit: PreCutoffOrbitFit, heldout: readonly TimedOrbitPosition[],
): FutureOrbitScore {
  if (!heldout.length) throw new RangeError('No future observations to score');
  validateTimedPositions(heldout, fit.objectNorad, fit.inertialFrame,
    utcMilliseconds(fit.initialEpochUtc), utcMilliseconds(fit.cutoffEpochUtc), 'holdout');
  const baselineRmsKm = positionResidualRmsKm(
    fit.initialState, heldout, fit.stepS, fit.terminationAltitudeKm, fit.dynamics);
  const fittedRmsKm = positionResidualRmsKm(
    fit.fittedState, heldout, fit.stepS, fit.terminationAltitudeKm, fit.dynamics);
  return {
    baselineRmsKm, fittedRmsKm,
    deltaRmsKm: Number.isFinite(baselineRmsKm) && Number.isFinite(fittedRmsKm)
      ? fittedRmsKm - baselineRmsKm : null,
    observationCount: heldout.length,
  };
}
