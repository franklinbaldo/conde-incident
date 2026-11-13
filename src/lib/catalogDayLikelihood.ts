/**
 * C241: two-sided reporting uncertainty about the calendar day in the NASA
 * Satellite Situation Report (15 Nov 1963, "1963 3B: 8 NOV 63").
 *
 * NO calibrated 1963 NASA/NORAD temporal sigma is available for 528.
 * This is a family of ASSUMED measurement-error models for screening and
 * sensitivity, not an observation of physical reentry time or an impact time.
 *
 * Important distinction:
 * - likelihood: P(reported CALENDAR DAY = 8 Nov | terminal UTC t, model);
 * - normalized time density under a flat unbounded prior: convolution of
 *   Uniform(8 Nov 00Z..9 Nov 00Z) and Normal(0,sigma);
 * - posterior of an actual orbital model needs its own prior, orbit dynamics,
 *   error correlations and reentry/fragment-survival model.
 */
export const CATALOGUE_528 = Object.freeze({
  evidence: 'C197#1',
  source: 'https://ntrs.nasa.gov/citations/19640001198',
  reportedDay: '1963-11-08',
  startUtc: '1963-11-08T00:00:00.000Z',
  endExclusiveUtc: '1963-11-09T00:00:00.000Z',
  sourceDocumentEstablishesUtcTerminalInstant: false,
  sourceDocumentEstablishesTemporalSigma: false,
  sourceDocumentEstablishesImpactTime: false,
} as const);

const DAY_MS = 86_400_000;
const START_MS = Date.parse(CATALOGUE_528.startUtc);
const END_MS = Date.parse(CATALOGUE_528.endExclusiveUtc);
const ROOT_TWO = Math.SQRT2;
const ROOT_TWO_PI = Math.sqrt(2*Math.PI);
const MAX_SIGMA_HOURS = 240;

/** Numerical approximation with error ~1.5e-7 absolute for erf.
 * Two-tailed likelihood has 2* this error at most, not an instrument sigma.
 */
function erf(x: number): number {
  if (x === 0) return 0; // exact center; avoid approximation offset at calendar boundaries
  const sign = x < 0 ? -1 : 1;
  const y = Math.abs(x);
  const t = 1/(1+0.3275911*y);
  const a = ((((1.061405429*t-1.453152027)*t)+1.421413741)*t
      -0.284496736)*t+0.254829592;
  return sign*(1-a*t*Math.exp(-y*y));
}
function cdf(z: number): number {
  return (1+erf(z/ROOT_TWO))/2;
}
function pdf(z: number): number {
  return Math.exp(-z*z/2)/ROOT_TWO_PI;
}
function validSigma(sigmaHours: number): number {
  if (!Number.isFinite(sigmaHours) || sigmaHours <= 0 ||
      sigmaHours > MAX_SIGMA_HOURS)
    throw new RangeError('Explicit scenario sigma must be within (0,240] hours');
  return sigmaHours*3_600_000;
}

/** Under a hypothetical additive Normal(0,sigma) error, integrates over
 * the full printed calendar day. No assumption that the physical event
 * occurred exactly at 00:00Z or exactly at noon.
 */
export function catalogueDayLikelihood(
  eventEpochMs: number, sigmaHours: number,
): number {
  const sigmaMs=validSigma(sigmaHours);
  if (!Number.isFinite(eventEpochMs) ||
      eventEpochMs < Date.UTC(1900,0,1) || eventEpochMs > Date.UTC(2100,0,1))
    throw new RangeError('Finite event UTC epoch required');
  const upper=(END_MS-eventEpochMs)/sigmaMs;
  const lower=(START_MS-eventEpochMs)/sigmaMs;
  // Rounding errors on extreme tails must not create negative weights.
  return Math.max(0,Math.min(1,cdf(upper)-cdf(lower)));
}

export interface CalendarSpreadScenario {
  readonly sigmaHoursAssumed: number;
  readonly probabilityBeforeNov8: number;
  readonly probabilityDuringNov8: number;
  readonly probabilityAfterNov8: number;
  readonly errorDistribution: 'ASSUMED_GAUSSIAN_SYMMETRIC';
  readonly historicalPrecisionCalibrated: false;
  readonly physicalImpactInferred: false;
}

/** Exact Gaussian-uniform convolution mass: U(day8) + N(0,sigma).
 * The density is symmetric about 1963-11-08 12Z. This is NOT a posterior
 * without an explicit flat prior or a model of event/reporting selection.
 */
export function calendarSpreadScenario(sigmaHours: number): CalendarSpreadScenario {
  validSigma(sigmaHours);
  const a=24/sigmaHours;
  const tail=(sigmaHours/24)*(pdf(0)-pdf(a)+a*(1-cdf(a)));
  const before=Math.max(0,Math.min(.5,tail));
  const during=1-2*before;
  return {
    sigmaHoursAssumed:sigmaHours,
    probabilityBeforeNov8:before,
    probabilityDuringNov8:during,
    probabilityAfterNov8:before,
    errorDistribution:'ASSUMED_GAUSSIAN_SYMMETRIC',
    historicalPrecisionCalibrated:false,
    physicalImpactInferred:false,
  };
}

export const PREDECLARED_DAY_SCENARIOS = [6,12,24] as const;

/** Update geographical cell probabilities by the NASA-day likelihood, not
 * by a hard 7-9 Nov indicator and not by the distance to Conde itself.
 * Priors are from the caller, and they MUST represent independent coherent
 * candidate trajectories. Passing a legacy exploratory sampler does not
 * upgrade its output into a historical posterior.
 */
export interface TerminalCandidate {
  readonly eventEpochMs: number;
  readonly cellId: string;
  readonly priorWeight: number;
}
export function scenarioWeightedCells(
  candidates: readonly TerminalCandidate[], sigmaHours: number,
): {
  readonly totalPriorWeight: number;
  readonly weightedMass: number;
  readonly effectiveSampleSize: number | null;
  readonly cellProbabilities: Readonly<Record<string,number>>;
  readonly interpretedAsHistoricalPosterior: false;
} {
  validSigma(sigmaHours);
  if (!candidates.length)
    throw new RangeError('Candidate trajectories required');
  const weights=new Map<string,number>();
  let priorTotal=0, sum=0, sumSquares=0;
  for (const sample of candidates) {
    if (!sample.cellId?.trim() ||
        !Number.isFinite(sample.priorWeight) || sample.priorWeight<0)
      throw new RangeError('Each sample needs a cell ID and nonnegative prior weight');
    priorTotal+=sample.priorWeight;
    const w=sample.priorWeight*catalogueDayLikelihood(sample.eventEpochMs,sigmaHours);
    sum+=w;sumSquares+=w*w;
    weights.set(sample.cellId,(weights.get(sample.cellId)??0)+w);
  }
  if (priorTotal<=0)
    throw new RangeError('All candidate prior weights zero');
  return {
    totalPriorWeight:priorTotal,
    weightedMass:sum,
    effectiveSampleSize:sum>0&&sumSquares>0 ? (sum*sum)/sumSquares : null,
    cellProbabilities:sum>0 ?
      Object.fromEntries([...weights].map(([key,w])=>[key,w/sum])) : {},
    interpretedAsHistoricalPosterior:false,
  };
}
