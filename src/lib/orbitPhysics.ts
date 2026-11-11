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
  readonly densityKgM3: (altitudeKm: number, tS: number) => number;
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
  if (dynamics.atmosphere) {
    const { densityKgM3, cdAreaOverMassM2Kg, source } = dynamics.atmosphere;
    if (!source.trim() || !Number.isFinite(cdAreaOverMassM2Kg) || cdAreaOverMassM2Kg < 0) {
      throw new RangeError('Atmospheric model requires source and nonnegative Cd*A/m');
    }
    const rho = densityKgM3(r - EARTH.radiusKm, s.tS);
    if (!Number.isFinite(rho) || rho < 0) throw new RangeError('Density must be finite and nonnegative');
    // Atmosphere co-rotates with Earth; relative velocity is inertial v minus omega x r.
    const vRelKmS: Vec3 = [
      s.vKmS[0] + EARTH.spinRadS * s.rKm[1],
      s.vKmS[1] - EARTH.spinRadS * s.rKm[0],
      s.vKmS[2],
    ];
    // SI drag m/s^2 divided by 1000 -> km/s^2. Multiplication by
    // (1000 m/km)^2 / (1000 m/km) = 1000.
    const dragFactor = -500 * rho * cdAreaOverMassM2Kg * norm(vRelKmS);
    acceleration = add(acceleration, scale(vRelKmS, dragFactor));
  }
  return acceleration;
}

export function rk4(s: State, dtS: number, dynamics: Dynamics = {}): State {
  if (!Number.isFinite(dtS) || dtS <= 0) throw new RangeError('RK4 step must be finite and positive');
  const derivative = (q: State) => ({ dr: q.vKmS, dv: accelerationKmS2(q, dynamics) });
  const shifted = (q: State, k: {dr: Vec3; dv: Vec3}, h: number): State => ({
    rKm: add(q.rKm, scale(k.dr, h)), vKmS: add(q.vKmS, scale(k.dv, h)), tS: q.tS + h,
  });
  const k1 = derivative(s);
  const k2 = derivative(shifted(s, k1, dtS / 2));
  const k3 = derivative(shifted(s, k2, dtS / 2));
  const k4 = derivative(shifted(s, k3, dtS));
  const sum = (key: 'dr' | 'dv'): Vec3 => scale(add(add(k1[key], scale(k2[key], 2)), add(scale(k3[key], 2), k4[key])), dtS / 6);
  return { rKm: add(s.rKm, sum('dr')), vKmS: add(s.vKmS, sum('dv')), tS: s.tS + dtS };
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
  // A threshold is a stopping convention, NOT a measured breakup or impact altitude.
  if (altitudeKm(initial) <= terminationAltitudeKm) return { state: initial, event: 'reentry-threshold', steps: 0 };
  let current = initial;
  let count = 0;
  while (current.tS - initial.tS < durationS - 1e-10) {
    const step = Math.min(stepS, durationS - (current.tS - initial.tS));
    const next = rk4(current, step, dynamics);
    count++;
    if (altitudeKm(next) <= terminationAltitudeKm) {
      // Within-step event search re-integrates from the same previous state;
      // interpolation of position alone would not preserve coupled r/v.
      let low = 0, high = step;
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
