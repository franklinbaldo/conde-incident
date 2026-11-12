/**
 * Conditional cross-epoch covariance score for coupled r/v holdouts (527/529).
 * C197#1 NASA/Goddard SSR 15 Nov 1963 p.8 is only a decay DAY:
 * https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf
 * C179/C180 are secondary TLE lineage, not original Cartesian measurements.
 * All matrices and records here are DECLARED, not historically authenticated.
 */
import { stageDocumentedChronologicalSplit } from './orbitObservationIntake.ts';
import { auditFutureOrbitScore } from './orbitHoldoutAudit.ts';
import type { DocumentaryOrbitDatum } from './orbitObservationIntake.ts';
import type { CovarianceRecord } from './orbitCovarianceGate.ts';
import type { PreCutoffOrbitFit, Vec3 } from './orbitPhysics.ts';
import type { ConvergenceControls } from './orbitConvergence.ts';

export type JointCovarianceMatrix = readonly (readonly number[])[];
export interface JointCovarianceRecord {
  readonly covarianceSourceUrl: string;
  /** Must match the withheld observations in chronological order exactly. */
  readonly observations: readonly {
    readonly matrixOccurrence: string;
    readonly instrumentRecordId: string;
    readonly documentUrl: string;
    readonly observationEpochUtc: string;
  }[];
  /** 3N-by-3N Cartesian covariance in km², including interepoch blocks. */
  readonly covarianceKm2: JointCovarianceMatrix;
}
export type JointCovarianceStatus =
  | 'BLOCKED_DOCUMENTATION' | 'BLOCKED_JOINT_COVARIANCE'
  | 'BLOCKED_NUMERICAL_AUDIT' | 'INSUFFICIENT_NUMERICAL_RESOLUTION'
  | 'REFINEMENT_RANK_CONFLICT' | 'CONDITIONAL_INDISTINGUISHABLE'
  | 'CONDITIONAL_FITTED_BETTER' | 'CONDITIONAL_BASELINE_BETTER';
export interface JointCovarianceAudit {
  readonly status: JointCovarianceStatus;
  readonly levels: readonly {
    stepS: number; baselineRmsSigma: number; fittedRmsSigma: number;
    deltaRmsSigma: number;
  }[];
  readonly refinementSigma: number | null;
  readonly resolutionBudgetSigma: number | null;
  readonly declaredJointCovarianceUsed: boolean;
  readonly covarianceCalibrationVerified: false;
  readonly originalObservationsAuthenticated: false;
  readonly crossEpochCorrelationEmpiricallyVerified: false;
  readonly likelihoodComputed: false;
  readonly impactInference: 'NOT_SUPPORTED';
}
type Whiten = (v: readonly number[]) => number[];
const near = (a: number, b: number) =>
  Number.isFinite(a) && Number.isFinite(b) && Math.abs(a-b) <=
    1e-9*Math.max(1,Math.abs(a),Math.abs(b));
/**
 * Build a dimensionless lower-triangular whitening transform from a
 * declared 3N-by-3N matrix. The diagonal is normalized using documented
 * per-coordinate sigma, never filled or estimated from the residual.
 * This computes a numerical metric only, NOT a posterior or p-value.
 */
function jointWhiten(c: JointCovarianceMatrix, sigmas: readonly Vec3[]): Whiten | null {
  if (!Array.isArray(sigmas) || sigmas.length < 2 || sigmas.length > 12 ||
      !sigmas.every(v => Array.isArray(v) && v.length===3 &&
        v.every(x=>Number.isFinite(x) && x>0))) return null;
  const s=sigmas.flat(), n=s.length;
  if (!Array.isArray(c) || c.length!==n) return null;
  const a:number[][]=[];
  for (let i=0;i<n;i++) {
    if (!Array.isArray(c[i]) || c[i].length!==n) return null;
    const row=c[i].map((x:number,j:number)=>x/s[i]/s[j]);
    if (!row.every(Number.isFinite) || !near(row[i],1)) return null;
    a.push(row);
  }
  for(let i=0;i<n;i++) for(let j=0;j<i;j++)
    if(!near(a[i][j],a[j][i])) return null;
  const l:number[][]=Array.from({length:n},()=>Array(n).fill(0));
  for(let i=0;i<n;i++) for(let j=0;j<=i;j++) {
    let v=a[i][j];
    for(let k=0;k<j;k++) v-=l[i][k]*l[j][k];
    if (i===j) {
      if(!(v>1e-10) || !Number.isFinite(v)) return null;
      l[i][j]=Math.sqrt(v);
    } else {
      l[i][j]=v/l[j][j];
      if(!Number.isFinite(l[i][j])) return null;
    }
  }
  return (r:readonly number[])=>{
    if(!Array.isArray(r) || r.length!==n || !r.every(Number.isFinite))
      return Array(n).fill(NaN);
    const z:number[]=[];
    for(let i=0;i<n;i++) {
      let v=r[i]/s[i];
      for(let j=0;j<i;j++) v-=l[i][j]*z[j];
      z.push(v/l[i][i]);
    }
    return z;
  };
}
export function normalizedJointCartesianResidual(
  residuals:readonly Vec3[], sigmas:readonly Vec3[], c:JointCovarianceMatrix,
):number|null {
  if(residuals.length!==sigmas.length || !residuals.every(
    v=>Array.isArray(v) && v.length===3 && v.every(Number.isFinite))) return null;
  const w=jointWhiten(c,sigmas);
  if(!w) return null;
  const n=Math.hypot(...w(residuals.flat()));
  return Number.isFinite(n)?n:null;
}
function matchesEvidence(
  obs:readonly DocumentaryOrbitDatum[], perEpoch:readonly CovarianceRecord[],
  joint:JointCovarianceRecord,
): boolean {
  if(!joint || !/^https:\/\/\S+$/.test(joint.covarianceSourceUrl) ||
      !Array.isArray(joint.observations) ||
      joint.observations.length!==obs.length ||
      perEpoch.length!==obs.length) return false;
  const n=obs.length;
  const full=joint.covarianceKm2;
  if(!Array.isArray(full) || full.length!==3*n) return false;
  for(let i=0;i<n;i++) {
    const d=obs[i], ref=joint.observations[i];
    const matches=perEpoch.filter(c=>c.matrixOccurrence===d.matrixOccurrence &&
      c.instrumentRecordId===d.instrumentRecordId && c.documentUrl===d.documentUrl);
    if(!ref || ref.matrixOccurrence!==d.matrixOccurrence ||
        ref.instrumentRecordId!==d.instrumentRecordId ||
        ref.documentUrl!==d.documentUrl ||
        ref.observationEpochUtc!==d.observationEpochUtc ||
        matches.length!==1 || !/^https:\/\/\S+$/.test(matches[0].covarianceSourceUrl) ||
        !d.sigmaKm || !matches[0].covarianceKm2) return false;
    const c=matches[0].covarianceKm2;
    for(let j=0;j<3;j++) for(let k=0;k<3;k++) {
      if(!Number.isFinite(c[j][k]) ||
          !near(full[3*i+j]?.[3*i+k]/d.sigmaKm[j]/d.sigmaKm[k],
            c[j][k]/d.sigmaKm[j]/d.sigmaKm[k])) return false;
    }
  }
  return true;
}
const diff=(a:Vec3,b:Vec3):Vec3=>[a[0]-b[0],a[1]-b[1],a[2]-b[2]];
/**
 * Both r/v candidates were fitted before cutoff; future points are withheld.
 * A full interepoch matrix may reverse a diagonal-only ranking. This function
 * refuses to label the result as historical validation or calibrated likelihood.
 */
export function auditDocumentedJointCovarianceHoldout(
  fit:PreCutoffOrbitFit, training:readonly DocumentaryOrbitDatum[],
  holdout:readonly DocumentaryOrbitDatum[], perEpoch:readonly CovarianceRecord[],
  joint:JointCovarianceRecord, controls:ConvergenceControls,
  maxNumericalFractionOfSigma:number,
):JointCovarianceAudit {
  if(!Number.isFinite(maxNumericalFractionOfSigma) ||
      maxNumericalFractionOfSigma<=0 || maxNumericalFractionOfSigma>1)
    throw new RangeError('Predeclare numerical fraction of sigma in (0,1]');
  const report=(status:JointCovarianceStatus,
    levels:JointCovarianceAudit['levels']=[], refinementSigma:number|null=null,
    resolutionBudgetSigma:number|null=null, declaredJointCovarianceUsed=false)
      :JointCovarianceAudit=>({
        status,levels,refinementSigma,resolutionBudgetSigma,declaredJointCovarianceUsed,
        covarianceCalibrationVerified:false,originalObservationsAuthenticated:false,
        crossEpochCorrelationEmpiricallyVerified:false,likelihoodComputed:false,
        impactInference:'NOT_SUPPORTED',
      });
  const split=stageDocumentedChronologicalSplit(training,holdout,{
    objectNorad:fit.objectNorad,initialEpochUtc:fit.initialEpochUtc,
    cutoffEpochUtc:fit.cutoffEpochUtc,inertialFrame:fit.inertialFrame,
  });
  if(split.status!=='CONDITIONAL_UNWEIGHTED_INPUTS' ||
      !Number.isSafeInteger(fit.trainingCount) ||
      fit.trainingCount!==split.trainingPositions.length)
    return report('BLOCKED_DOCUMENTATION');
  if(!matchesEvidence(holdout,perEpoch,joint))
    return report('BLOCKED_JOINT_COVARIANCE');
  const sigmas=holdout.map(x=>x.sigmaKm!);
  const w=jointWhiten(joint.covarianceKm2,sigmas);
  if(!w) return report('BLOCKED_JOINT_COVARIANCE');
  const numeric=auditFutureOrbitScore(fit,split.holdoutPositions,controls);
  if(!['NUMERICALLY_INDISTINGUISHABLE','APPARENT_FITTED_BETTER',
    'APPARENT_BASELINE_BETTER'].includes(numeric.status))
    return report('BLOCKED_NUMERICAL_AUDIT');
  const count=numeric.points[0]?.baseline.levels.length??0;
  if(count<3 || numeric.points.some(p=>p.baseline.levels.length!==count ||
      p.fitted.levels.length!==count)) return report('BLOCKED_NUMERICAL_AUDIT');
  const vector=(i:number,model:'baseline'|'fitted')=>numeric.points.flatMap(
    (p,j)=>diff(p[model].levels[i].result.state.rKm,
      split.holdoutPositions[j].rKm));
  const score=(i:number,model:'baseline'|'fitted')=>
    Math.hypot(...w(vector(i,model)))/Math.sqrt(holdout.length);
  const levels=Array.from({length:count},(_,i)=>{
    const baselineRmsSigma=score(i,'baseline'),fittedRmsSigma=score(i,'fitted');
    return {stepS:numeric.points[0].baseline.levels[i].stepS,
      baselineRmsSigma,fittedRmsSigma,
      deltaRmsSigma:fittedRmsSigma-baselineRmsSigma};
  });
  if(levels.some(l=>!Number.isFinite(l.baselineRmsSigma) ||
      !Number.isFinite(l.fittedRmsSigma) || !Number.isFinite(l.deltaRmsSigma)))
    return report('BLOCKED_NUMERICAL_AUDIT');
  let refinement=0;
  for(const model of ['baseline','fitted'] as const)
    for(let i=count-2;i<count;i++) {
      const between=numeric.points.flatMap(p=>diff(
        p[model].levels[i].result.state.rKm,
        p[model].levels[i-1].result.state.rKm));
      refinement=Math.max(refinement,Math.hypot(...w(between)));
    }
  const dimension=3*holdout.length;
  let squaredNorm=0;
  for(let i=0;i<dimension;i++) {
    const basis=Array(dimension).fill(0);basis[i]=1;
    const norm=Math.hypot(...w(basis));
    squaredNorm+=norm*norm;
  }
  const budget=Math.max(refinement,
    controls.tolerance.positionKm*Math.sqrt(squaredNorm));
  if(!Number.isFinite(budget)) return report('BLOCKED_NUMERICAL_AUDIT');
  if(budget>maxNumericalFractionOfSigma)
    return report('INSUFFICIENT_NUMERICAL_RESOLUTION',levels,refinement,budget,true);
  const recent=levels.slice(-3),last=recent[2].deltaRmsSigma;
  if(recent.some(l=>Math.sign(l.deltaRmsSigma)!==Math.sign(last)))
    return report('REFINEMENT_RANK_CONFLICT',levels,refinement,budget,true);
  const sensitivity=Math.max(...recent.slice(0,2).map(l=>
    Math.abs(l.deltaRmsSigma-last)));
  if(Math.abs(last)<=Math.max(sensitivity,2*budget))
    return report('CONDITIONAL_INDISTINGUISHABLE',levels,refinement,budget,true);
  return report(last<0?'CONDITIONAL_FITTED_BETTER':'CONDITIONAL_BASELINE_BETTER',
    levels,refinement,budget,true);
}
