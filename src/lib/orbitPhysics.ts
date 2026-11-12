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
  const rho = densityKgM3(r - EARTH.radiusKm, s.tS);
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
