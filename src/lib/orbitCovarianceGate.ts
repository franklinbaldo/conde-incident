/**
 * Covariance-aware diagnostic for withheld 527/529 Cartesian observations.
 * C197#1 NASA/Goddard 15 Nov 1963 p.8 gives a decay DAY only:
 * https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf
 * C179#1 is secondary TLE lineage, not an original position measurement.
 * Matrices here are DECLARED, never authenticated, and are not likelihoods.
 */
import { stageDocumentedChronologicalSplit } from './orbitObservationIntake.ts';
import { auditFutureOrbitScore } from './orbitHoldoutAudit.ts';
import type { DocumentaryOrbitDatum } from './orbitObservationIntake.ts';
import type { PreCutoffOrbitFit, Vec3 } from './orbitPhysics.ts';
import type { ConvergenceControls } from './orbitConvergence.ts';

export type Matrix3 = readonly [Vec3, Vec3, Vec3];
export interface CovarianceRecord {
  readonly matrixOccurrence: string;
  readonly instrumentRecordId: string;
  readonly documentUrl: string;
  readonly covarianceSourceUrl: string;
  readonly covarianceKm2: Matrix3;
}
export type ConditionalCovarianceStatus =
  | 'BLOCKED_DOCUMENTATION' | 'BLOCKED_COVARIANCE'
  | 'BLOCKED_NUMERICAL_AUDIT' | 'INSUFFICIENT_NUMERICAL_RESOLUTION'
  | 'REFINEMENT_RANK_CONFLICT' | 'CONDITIONAL_INDISTINGUISHABLE'
  | 'CONDITIONAL_FITTED_BETTER' | 'CONDITIONAL_BASELINE_BETTER';
export interface ConditionalCovarianceAudit {
  readonly status: ConditionalCovarianceStatus;
  readonly levels: readonly { stepS: number; baselineRmsSigma: number;
    fittedRmsSigma: number; deltaRmsSigma: number }[];
  readonly refinementSigma: number | null;
  readonly resolutionBudgetSigma: number | null;
  readonly rejectedOccurrences: readonly string[];
  readonly authenticatedHistoricalObservations: false;
  readonly covarianceCalibrationVerified: false;
  readonly crossEpochCorrelationsResolved: false;
  readonly likelihoodComputed: false;
  readonly impactInference: 'NOT_SUPPORTED';
}
type Whiten = (v: Vec3) => Vec3;
const diff = (a: Vec3, b: Vec3): Vec3 =>
  [a[0]-b[0], a[1]-b[1], a[2]-b[2]];
const near = (a: number, b: number) =>
  Number.isFinite(a) && Number.isFinite(b) &&
  Math.abs(a-b) <= 1e-9 * Math.max(Math.abs(a), Math.abs(b));
/**
 * Cholesky of correlation matrix, normalized by original 1-sigma km.
 * Rejects non-SPD, nearly singular or inconsistent covariance matrices.
 * No diagonal covariance is invented from sigma.
 */
function whiten(c: Matrix3, s: Vec3): Whiten | null {
  if (!Array.isArray(c) || c.length !== 3 || !Array.isArray(s) ||
      s.length !== 3 || !s.every(x => Number.isFinite(x) && x > 0))
    return null;
  const a: number[][] = [];
  for (let i=0;i<3;i++) {
    if (!Array.isArray(c[i]) || c[i].length !== 3) return null;
    const row = c[i].map((x: number, j: number) => x/s[i]/s[j]);
    if (!row.every(Number.isFinite)) return null;
    a.push(row);
  }
  if (![0,1,2].every(i => near(a[i][i],1)) ||
      !near(a[0][1],a[1][0]) || !near(a[0][2],a[2][0]) ||
      !near(a[1][2],a[2][1])) return null;
  const l10=a[1][0], l20=a[2][0], p11=a[1][1]-l10*l10;
  if (!(p11>1e-10)) return null;
  const l11=Math.sqrt(p11), l21=(a[2][1]-l20*l10)/l11;
  const p22=a[2][2]-l20*l20-l21*l21;
  if (!(p22>1e-10)) return null;
  const l22=Math.sqrt(p22);
  return (r:Vec3):Vec3 => {
    const z0=r[0]/s[0], z1=(r[1]/s[1]-l10*z0)/l11;
    return [z0,z1,(r[2]/s[2]-l20*z0-l21*z1)/l22];
  };
}
/** Dimensionless squared-covariance-distance norm, NOT a p-value. */
export function normalizedCartesianResidual(r:Vec3, c:Matrix3, sigma:Vec3):number|null {
  const w=whiten(c,sigma);
  if (!w || r.length!==3 || !r.every(Number.isFinite)) return null;
  const n=Math.hypot(...w(r));
  return Number.isFinite(n) ? n : null;
}
/**
 * Frozen pre-cutoff fit; independent refinement of both r/v predictions.
 * Each HOLDOUT record needs its OWN matrix, provenance and consistent sigma.
 * Missing temporal cross-covariance forbids likelihood/posterior claims.
 */
export function auditDocumentedCovarianceHoldout(
  fit:PreCutoffOrbitFit, training:readonly DocumentaryOrbitDatum[],
  holdout:readonly DocumentaryOrbitDatum[], covariance:readonly CovarianceRecord[],
  controls:ConvergenceControls, maxNumericalFractionOfSigma:number,
):ConditionalCovarianceAudit {
  if (!Number.isFinite(maxNumericalFractionOfSigma) ||
      maxNumericalFractionOfSigma<=0 || maxNumericalFractionOfSigma>1)
    throw new RangeError('Predeclare numerical fraction of sigma in (0,1]');
  const report=(status:ConditionalCovarianceStatus,
    levels:ConditionalCovarianceAudit['levels']=[], refinementSigma:number|null=null,
    resolutionBudgetSigma:number|null=null, rejectedOccurrences:readonly string[]=[])
      :ConditionalCovarianceAudit=>({
        status,levels,refinementSigma,resolutionBudgetSigma,rejectedOccurrences,
        authenticatedHistoricalObservations:false,covarianceCalibrationVerified:false,
        crossEpochCorrelationsResolved:false,likelihoodComputed:false,
        impactInference:'NOT_SUPPORTED',
      });
  const split=stageDocumentedChronologicalSplit(training,holdout,{
    objectNorad:fit.objectNorad,initialEpochUtc:fit.initialEpochUtc,
    cutoffEpochUtc:fit.cutoffEpochUtc,inertialFrame:fit.inertialFrame,
  });
  if (split.status!=='CONDITIONAL_UNWEIGHTED_INPUTS' ||
      !Number.isSafeInteger(fit.trainingCount) ||
      fit.trainingCount!==split.trainingPositions.length)
    return report('BLOCKED_DOCUMENTATION');
  const whitener:Whiten[]=[];
  const rejected:string[]=[];
  let whiteningNormBound=0;
  for (const d of holdout) {
    const matches=covariance.filter(c=>c.matrixOccurrence===d.matrixOccurrence &&
      c.instrumentRecordId===d.instrumentRecordId && c.documentUrl===d.documentUrl);
    const c=matches[0], w=matches.length===1 && /^https:\/\/\S+$/.test(c.covarianceSourceUrl) &&
      d.sigmaKm!==null ? whiten(c.covarianceKm2,d.sigmaKm) : null;
    if (!w) {rejected.push(d.matrixOccurrence);continue;}
    whitener.push(w);
    // Frobenius norm bounds whitened discrepancy for an Euclidean km norm.
    const norm=Math.hypot(...([[1,0,0],[0,1,0],[0,0,1]] as Vec3[]).flatMap(x=>w(x)));
    whiteningNormBound=Math.max(whiteningNormBound,norm);
    if (!Number.isFinite(norm)) rejected.push(d.matrixOccurrence);
  }
  if (covariance.length!==holdout.length || rejected.length ||
      whitener.length!==holdout.length)
    return report('BLOCKED_COVARIANCE',[],null,null,rejected);
  const numeric=auditFutureOrbitScore(fit,split.holdoutPositions,controls);
  if (!['NUMERICALLY_INDISTINGUISHABLE','APPARENT_FITTED_BETTER',
        'APPARENT_BASELINE_BETTER'].includes(numeric.status))
    return report('BLOCKED_NUMERICAL_AUDIT');
  const count=numeric.points[0]?.baseline.levels.length ?? 0;
  if (count<3 || numeric.points.some(p=>p.baseline.levels.length!==count ||
      p.fitted.levels.length!==count)) return report('BLOCKED_NUMERICAL_AUDIT');
  const score=(i:number,model:'baseline'|'fitted')=>
    Math.hypot(...numeric.points.flatMap((p,j)=>whitener[j](diff(
      p[model].levels[i].result.state.rKm,split.holdoutPositions[j].rKm
    ))))/Math.sqrt(holdout.length);
  const levels=Array.from({length:count},(_,i)=>{
    const baselineRmsSigma=score(i,'baseline'),fittedRmsSigma=score(i,'fitted');
    return {stepS:numeric.points[0].baseline.levels[i].stepS,
      baselineRmsSigma,fittedRmsSigma,deltaRmsSigma:fittedRmsSigma-baselineRmsSigma};
  });
  if (levels.some(l=>!Number.isFinite(l.baselineRmsSigma) ||
      !Number.isFinite(l.fittedRmsSigma) || !Number.isFinite(l.deltaRmsSigma)))
    return report('BLOCKED_NUMERICAL_AUDIT');
  let refinement=0;
  for (const [j,p] of numeric.points.entries())
    for (const model of ['baseline','fitted'] as const)
      for (let i=count-2;i<count;i++)
        refinement=Math.max(refinement,Math.hypot(...whitener[j](diff(
          p[model].levels[i].result.state.rKm,
          p[model].levels[i-1].result.state.rKm))));
  const budget=Math.max(refinement,controls.tolerance.positionKm*whiteningNormBound);
  if (!Number.isFinite(budget)) return report('BLOCKED_NUMERICAL_AUDIT');
  if (budget>maxNumericalFractionOfSigma)
    return report('INSUFFICIENT_NUMERICAL_RESOLUTION',levels,refinement,budget);
  const recent=levels.slice(-3), last=recent[2].deltaRmsSigma;
  if (recent.some(l=>Math.sign(l.deltaRmsSigma)!==Math.sign(last)))
    return report('REFINEMENT_RANK_CONFLICT',levels,refinement,budget);
  const sensitivity=Math.max(...recent.slice(0,2).map(l=>
    Math.abs(l.deltaRmsSigma-last)));
  if (Math.abs(last)<=Math.max(sensitivity,2*budget))
    return report('CONDITIONAL_INDISTINGUISHABLE',levels,refinement,budget);
  return report(last<0?'CONDITIONAL_FITTED_BETTER':'CONDITIONAL_BASELINE_BETTER',
    levels,refinement,budget);
}
