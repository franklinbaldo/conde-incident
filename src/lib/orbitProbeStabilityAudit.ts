/**
 * Multiple-amplitude falsification gate for LOCAL orbit-velocity rank.
 * Only reuses predeclared training epochs, bounded premises and the original
 * coupled r/v J2 (optional sourced drag) numerical-convergence audit.
 *
 * Rank agreement over three probes is NOT a verified Jacobian, empirical
 * identifiability, a Lean theorem, or a global inverse uniqueness claim.
 */
import { auditLocalVelocitySensitivity } from './orbitSensitivityAudit.ts';
import type {
  SensitivityAudit, SensitivityControls, ScheduledTrainingEpoch,
} from './orbitSensitivityAudit.ts';
import type { ConditionalOrbitScenario, VelocityAxis } from './orbitAdmissibility.ts';
import type { Dynamics } from './orbitPhysics.ts';

export type ProbeScale = 0.5 | 1 | 2;
export interface ProbeCheck {
  readonly factor: ProbeScale;
  readonly requestedProbeKmS: number;
  readonly audit: SensitivityAudit;
}
export interface ProbeSpan {
  readonly axis: VelocityAxis;
  /** Actual applied speed difference at each probe, in km/s. */
  readonly appliedWidthsKmS: readonly [number, number, number];
}
export interface MultiProbeSensitivityAudit {
  readonly status: 'CONSISTENT_AT_THREE_PROBES' |
    'RANK_CHANGES_WITH_PROBE' | 'NOT_RESOLVED_SATURATED_PROBE' |
    'NOT_RUN_A_PROBE' | 'NO_FREE_VELOCITY_DIRECTIONS';
  readonly checks: readonly ProbeCheck[];
  readonly spans: readonly ProbeSpan[];
  readonly rankAtEachProbe: readonly (number | null)[];
  /** Only set when three independent probe amplitudes agree. */
  readonly conditionallyConsistentRank: number | null;
  /** A switch of pivot axes does not prove a physical basis switch. */
  readonly pivotSelectionChanged: boolean | null;
  readonly historicalHoldout: 'NOT_RUN';
  readonly proofVerification: 'NOT_RUN';
  readonly observationAuthenticity: 'NOT_VERIFIED';
  readonly globalIdentifiability: 'NOT_ESTABLISHED';
  readonly geographicInference: 'NOT_SUPPORTED';
}

const FACTORS: readonly ProbeScale[] = [0.5, 1, 2];
const VEL_AXES: readonly VelocityAxis[] = ['vx', 'vy', 'vz'];

/**
 * Fails closed if any of the three independently step-refined physical
 * propagations fails. Also rejects intervals clipped to the SAME width at
 * two different probe scales: repeating an identical finite difference
 * cannot count as an amplitude-stability test.
 */
export function auditVelocityProbeStability(
  scenario: ConditionalOrbitScenario,
  scheduledEpochs: readonly ScheduledTrainingEpoch[],
  controls: SensitivityControls,
  dynamics: Dynamics = {},
): MultiProbeSensitivityAudit {
  const probe = controls.probeKmS;
  if (!Number.isFinite(probe) || probe <= 0 ||
      !Number.isFinite(probe * 2) || probe * 0.5 <= 0 ||
      probe * 0.5 === probe || probe * 2 === probe)
    throw new RangeError('Probe must support three distinct finite positive amplitudes');
  const checks: ProbeCheck[] = FACTORS.map(factor => ({
    factor,
    requestedProbeKmS: probe * factor,
    audit: auditLocalVelocitySensitivity(
      scenario, scheduledEpochs, { ...controls, probeKmS: probe * factor }, dynamics),
  }));
  const ranks = checks.map(c => c.audit.localRankAtProbeAndThreshold);
  const result = (
    status: MultiProbeSensitivityAudit['status'],
    spans: readonly ProbeSpan[] = [],
    rank: number | null = null,
    pivotSelectionChanged: boolean | null = null,
  ): MultiProbeSensitivityAudit => ({
    status, checks, spans, rankAtEachProbe: ranks,
    conditionallyConsistentRank: rank, pivotSelectionChanged,
    historicalHoldout: 'NOT_RUN', proofVerification: 'NOT_RUN',
    observationAuthenticity: 'NOT_VERIFIED',
    globalIdentifiability: 'NOT_ESTABLISHED',
    geographicInference: 'NOT_SUPPORTED',
  });

  if (checks.some(c => c.audit.status !== 'ASSESSED_CONDITIONALLY'))
    return result('NOT_RUN_A_PROBE');
  const free = checks[0].audit.freeInPremise;
  if (free.length === 0) return result('NO_FREE_VELOCITY_DIRECTIONS');
  const spans: ProbeSpan[] = [];
  for (const axis of VEL_AXES) {
    if (!free.includes(axis)) continue;
    const widths = checks.map(c => {
      const pair = c.audit.axes.find(a => a.axis === axis)?.velocitiesKmS;
      return pair === null || pair === undefined ? Number.NaN : pair[1] - pair[0];
    });
    if (widths.some(w => !Number.isFinite(w) || w <= 0))
      return result('NOT_RUN_A_PROBE', spans);
    spans.push({ axis, appliedWidthsKmS:
      widths as unknown as [number, number, number] });
  }
  // All three scale levels need distinct representable intervals along EACH
  // declared free dimension; otherwise equal ranks may reuse identical probes.
  if (spans.some(s => !(s.appliedWidthsKmS[0] < s.appliedWidthsKmS[1] &&
                         s.appliedWidthsKmS[1] < s.appliedWidthsKmS[2])))
    return result('NOT_RESOLVED_SATURATED_PROBE', spans);

  // The chosen pivot axis is a numerical basis choice, not a causal claim.
  const signatures = checks.map(c => c.audit.axes
    .filter(a => a.entersNumericalBasis).map(a => a.axis).join(','));
  const pivotChanged = signatures.some(s => s !== signatures[0]);
  if (!ranks.every(r => r === ranks[0]))
    return result('RANK_CHANGES_WITH_PROBE', spans, null, pivotChanged);
  return result('CONSISTENT_AT_THREE_PROBES', spans, ranks[0], pivotChanged);
}
