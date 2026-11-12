import test from 'node:test';
import assert from 'node:assert/strict';
import { EARTH } from '../src/lib/orbitPhysics.ts';
import { auditVelocityDomain, runConditionalVelocityDomain } from '../src/lib/orbitAdmissibility.ts';
import { bridgeDeclaredAlternatives } from '../src/lib/orbitDeclaredDomainBridge.ts';

// Contract sample modeled on PR #43 output. Every observation, trace,
// domain and position here is SYNTHETIC. The #43 branch is not imported.
const epoch = '1963-10-27T00:00:00.000Z';
const frame = 'SYNTHETIC_CARTESIAN_INERTIAL';
const v = Math.sqrt(EARTH.muKm3S2 / (EARTH.radiusKm + 500));
const initial = { tS: 0, rKm: [EARTH.radiusKm + 500, 0, 0], vKmS: [0, v, 0] };
const axes = ['vx','vy','vz'];
const trace = (axis, id) => ({
  parameter: axis, evidence_id: id, occurrence: 'synthetic ' + axis,
  source_uri: 'synthetic:' + id, independence_group_declared: 'generated-' + id,
  lean_ref_declared: 'Synthetic.' + axis, lean_status_declared: 'NOT_RUN',
});
const parameter = (name, min, max) => ({
  name, status: 'REDUCED', initial: { min: '-1000', max: '1000' },
  admissible: { min, max },
});
const branch = (id, lo, hi) => ({
  id, domain_status: 'REDUCED', declared_evidence: 'SYNTHETIC_ONLY',
  lean_proofs: 'NOT_VERIFIED', numerical_holdout: 'NOT_RUN',
  parameters: [
    parameter('vx', lo, hi),
    parameter('vy', '760/100', '780/100'),
    parameter('vz', '-1/100', '1/100'),
  ],
  trace: axes.map(axis => trace(axis, id + '-' + axis)),
});
const baseline = () => ({
  status: 'MULTIPLE_DECLARED_FEASIBLE',
  scenarios: [branch('first','0','4/1000'),branch('second','8/100','9/100')],
  scenarios_declared: 2,
  scenarios_with_nonempty_intervals: 2,
  scenario_set_exhaustive: 'NOT_VERIFIED',
  matrix_occurrences: 'NOT_VERIFIED',
  source_authenticity: 'NOT_VERIFIED',
  source_independence_between_scenarios: 'NOT_VERIFIED',
  lean_proofs: 'NOT_VERIFIED',
  physical_feasibility: 'NOT_VERIFIED',
  numerical_holdouts: 'NOT_RUN',
  location_and_impact: 'NOT_INFERRED',
});
const context = (ids = ['first','second']) => ({
  objectNorad: 529, epochUtc: epoch, inertialFrame: frame,
  assumedUnit: 'km/s',
  initials: ids.map(id => ({
    id, initial, initialDomainSource: 'synthetic declared initial range ' + id,
  })),
});
const run = (audit = baseline(), ctx = context()) => bridgeDeclaredAlternatives(audit,ctx);
const setVx = (audit, interval) => {
  const p = audit.scenarios[0].parameters[0];
  // A real PR #37/#43 output includes the ORIGINAL interval. For extreme
  // Float64 test boxes, declare it equal instead of forging an expansion.
  p.initial = { ...interval };
  p.admissible = { ...interval };
  p.status = 'UNCHANGED';
};

test('separate exact rational source branches convert to two bounded Cartesian scenarios', () => {
  const out = run();
  assert.deepEqual(out.records.map(x => x.status),
    ['READY_CONDITIONALLY','READY_CONDITIONALLY']);
  assert.equal(out.alternatives.length,2);
  assert.deepEqual(out.alternatives.map(x => auditVelocityDomain(x.scenario).status),
    ['BOUNDED','BOUNDED']);
  assert.ok(out.alternatives[0].scenario.bounds[0].upperKmS <= 0.004);
  assert.ok(out.alternatives[1].scenario.bounds[0].lowerKmS >= 0.08);
  assert.equal(out.alternatives[0].scenario.bounds[0].premiseStatus,'SYNTHETIC');
  assert.match(out.alternatives[0].scenario.bounds[0].evidenceOccurrence,/first-vx/);
  assert.equal(out.unitFromAuditor,'NOT_PRESENT');
  assert.equal(out.leanProof,'NOT_VERIFIED');
  assert.equal(out.sourceAuthenticity,'NOT_VERIFIED');
  assert.equal(out.frameTransformation,'NOT_RUN');
  assert.equal(out.geographicInference,'NOT_SUPPORTED');
  assert.equal(out.exhaustiveEnclosure,false);
});

test('Float64 velocity endpoints are rounded INWARD, not overconfidently outward', () => {
  const audit = baseline();
  setVx(audit, {min:'3/10',max:'4/5'});
  const out = run(audit);
  const x = out.alternatives[0].scenario.bounds[0];
  assert.ok(x.lowerKmS > 0.3, '0.3 binary float is below exact 3/10');
  assert.ok(x.upperKmS < 0.8, '0.8 binary float is above exact 4/5');
  assert.ok(x.lowerKmS <= x.upperKmS);
});

test('a tiny exact rational interval with NO Float64 sample is rejected, not widened', () => {
  const audit = baseline();
  setVx(audit, {
    min:'100000000000000000001/1000000000000000000000',
    max:'100000000000000000002/1000000000000000000000',
  });
  const out = run(audit);
  assert.equal(out.alternatives.length,1);
  assert.equal(out.records[0].status,'NOT_RUN_FLOAT64_PRECISION');
  assert.equal(out.records[1].status,'READY_CONDITIONALLY');
});

test('exact singleton with representable Float64 survives, but inexact singleton does not', () => {
  const audit = baseline();
  setVx(audit, {min:'1/2',max:'1/2'});
  assert.deepEqual(run(audit).alternatives[0].scenario.bounds[0].lowerKmS,0.5);
  setVx(audit, {min:'1/10',max:'1/10'});
  assert.equal(run(audit).records[0].status,'NOT_RUN_FLOAT64_PRECISION');
});

test('declared contradiction remains local; never claim historical exclusion', () => {
  const audit = baseline();
  audit.scenarios[0].domain_status = 'CONTRADICTORY';
  audit.scenarios[0].parameters[0].admissible = null;
  audit.scenarios[0].parameters[0].status = 'EMPTY';
  audit.status = 'ONE_DECLARED_FEASIBLE';
  audit.scenarios_with_nonempty_intervals = 1;
  const out = run(audit);
  assert.equal(out.records[0].status,'NOT_RUN_CONTRADICTORY');
  assert.equal(out.records[1].status,'READY_CONDITIONALLY');
  assert.equal(out.alternatives.length,1);
  assert.equal(out.geographicInference,'NOT_SUPPORTED');
});

test('missing trace or velocity coordinate blocks just that branch', () => {
  const audit = baseline();
  audit.scenarios[0].trace = audit.scenarios[0].trace.filter(t => t.parameter !== 'vz');
  assert.equal(run(audit).records[0].status,'NOT_RUN_UNTRACED');
  audit.scenarios[0].parameters.pop();
  assert.equal(run(audit).records[0].status,'NOT_RUN_INCOMPLETE');
});

test('no pretending that a claimed Lean label, units or frame conversion was verified', () => {
  const audit = baseline();
  audit.lean_proofs='VERIFIED';
  assert.throws(() => run(audit),/falsely certified/);
  audit.lean_proofs='NOT_VERIFIED';
  audit.scenarios[0].trace[0].lean_status_declared='PASS';
  assert.throws(() => run(audit),/falsely certified restriction/);
  audit.scenarios[0].trace[0].lean_status_declared='NOT_RUN';
  const ctx=context();ctx.assumedUnit='m/s';
  assert.throws(() => run(audit,ctx),/Explicit Cartesian unit/);
});

test('no silent mapping from another parameter or another initial lineage', () => {
  const audit=baseline();
  audit.scenarios[0].parameters[0].name='RAAN';
  assert.throws(() => run(audit),/unsupported audit parameter/);
  audit.scenarios[0].parameters[0].name='vx';
  const ctx=context();ctx.initials.pop();
  assert.throws(() => run(audit,ctx),/Exactly one initial state/);
});

test('seeded, explicitly CONDiTIONAL physical propagation of rational branches is repeatable', () => {
  const out=run();
  const controls={
    seed:19763,interiorDraws:1,durationS:120,stepS:30,
    terminationAltitudeKm:80,
    convergence:{halvings:2,tolerance:{
      positionKm:0.5,velocityKmS:0.0005,epochS:0.05,
    }},
  };
  const one=runConditionalVelocityDomain(out.alternatives[0].scenario,controls,{j2:true});
  const again=runConditionalVelocityDomain(out.alternatives[0].scenario,controls,{j2:true});
  assert.deepEqual(one,again);
  assert.equal(one.status,'SAMPLED_CONDITIONALLY');
  assert.ok(one.samples.length>=9);
  assert.equal(one.proofVerification,'NOT_RUN');
  assert.equal(one.historicalHoldout,'NOT_RUN');
  assert.equal(one.geographicInference,'NOT_SUPPORTED');
  assert.deepEqual(one.samples.map(x=>x.vKmS),again.samples.map(x=>x.vKmS));
});


test('rational endpoints with huge numerator AND denominator retain exact representable singleton', () => {
  const audit=baseline();
  const huge='1'+'0'.repeat(400); // each BigInt exceeds finite Number
  setVx(audit, {min:huge+'/'+huge,max:huge+'/'+huge});
  let out=run(audit);
  assert.equal(out.records[0].status,'READY_CONDITIONALLY');
  assert.deepEqual([
    out.alternatives[0].scenario.bounds[0].lowerKmS,
    out.alternatives[0].scenario.bounds[0].upperKmS,
  ],[1,1]);
  setVx(audit, {min:'-'+huge+'/'+huge,max:huge+'/'+huge});
  out=run(audit);
  assert.equal(out.records[0].status,'READY_CONDITIONALLY');
  assert.deepEqual([
    out.alternatives[0].scenario.bounds[0].lowerKmS,
    out.alternatives[0].scenario.bounds[0].upperKmS,
  ],[-1,1]);
});

test('exact subnormal singleton survives; unrepresentable half-ulp singleton does NOT', () => {
  const audit=baseline();
  const minDen=(1n<<1074n).toString();
  setVx(audit, {min:'1/'+minDen,max:'1/'+minDen});
  let out=run(audit);
  assert.equal(out.records[0].status,'READY_CONDITIONALLY');
  const x=out.alternatives[0].scenario.bounds[0];
  assert.equal(x.lowerKmS,Number.MIN_VALUE);
  assert.equal(x.upperKmS,Number.MIN_VALUE);
  const halfDen=(1n<<1075n).toString();
  setVx(audit, {min:'1/'+halfDen,max:'1/'+halfDen});
  out=run(audit);
  assert.equal(out.records[0].status,'NOT_RUN_FLOAT64_PRECISION');
});

test('exact rational intersection clips beyond both finite Float64 extremes without inventing witnesses', () => {
  const audit=baseline(), huge='1'+'0'.repeat(400);
  setVx(audit, {min:'2',max:huge});
  let out=run(audit);
  assert.equal(out.records[0].status,'READY_CONDITIONALLY');
  assert.deepEqual([
    out.alternatives[0].scenario.bounds[0].lowerKmS,
    out.alternatives[0].scenario.bounds[0].upperKmS,
  ],[2,Number.MAX_VALUE]);
  setVx(audit, {min:'-'+huge,max:'-2'});
  out=run(audit);
  assert.equal(out.records[0].status,'READY_CONDITIONALLY');
  assert.deepEqual([
    out.alternatives[0].scenario.bounds[0].lowerKmS,
    out.alternatives[0].scenario.bounds[0].upperKmS,
  ],[-Number.MAX_VALUE,-2]);
  setVx(audit, {min:huge,max:huge});
  out=run(audit);
  assert.equal(out.records[0].status,'NOT_RUN_FLOAT64_PRECISION');
  setVx(audit, {min:'-'+huge,max:'-'+huge});
  assert.equal(run(audit).records[0].status,'NOT_RUN_FLOAT64_PRECISION');
});

test('an ultra-narrow signed rational box containing zero has only the zero Float64 witness', () => {
  const audit=baseline(),den='1'+'0'.repeat(400);
  setVx(audit, {min:'-1/'+den,max:'1/'+den});
  let out=run(audit);
  assert.equal(out.records[0].status,'READY_CONDITIONALLY');
  assert.deepEqual([
    out.alternatives[0].scenario.bounds[0].lowerKmS,
    out.alternatives[0].scenario.bounds[0].upperKmS,
  ],[0,0]);
  setVx(audit, {min:'1/'+den,max:'2/'+den});
  out=run(audit);
  assert.equal(out.records[0].status,'NOT_RUN_FLOAT64_PRECISION');
  assert.equal(out.records[1].status,'READY_CONDITIONALLY');
});

test('Float64 endpoint search preserves exact negative fractional boundaries', () => {
  const audit=baseline();
  setVx(audit, {min:'-4/5',max:'-3/10'});
  const out=run(audit);
  assert.equal(out.records[0].status,'READY_CONDITIONALLY');
  const b=out.alternatives[0].scenario.bounds[0];
  assert.ok(b.lowerKmS >= -0.8 && b.upperKmS <= -0.3);
  assert.ok(b.lowerKmS < b.upperKmS);
});


test('tampered admissible range may NOT grow beyond declared exact starting domain', () => {
  const audit=baseline();
  audit.scenarios[0].parameters[0].admissible={min:'-1001',max:'1/1000'};
  assert.throws(()=>run(audit),/expands its original exact domain/);
  // A tiny decimal growth invisible in typical Float64 endpoints remains forbidden.
  audit.scenarios[0].parameters[0].admissible={min:'-1000000000000000000001/1000000000000000000',max:'1/1000'};
  assert.throws(()=>run(audit),/expands its original exact domain/);
});

test('tampered REDUCED/UNCHANGED or contradictory scenario labels fail before propagation', () => {
  const audit=baseline();
  audit.scenarios[0].parameters[0].status='UNCHANGED';
  assert.throws(()=>run(audit),/Inconsistent declared rational parameter status/);
  audit.scenarios[0].parameters[0].status='REDUCED';
  audit.scenarios[0].domain_status='UNCHANGED';
  assert.throws(()=>run(audit),/Inconsistent declared scenario domain status/);
  audit.scenarios[0].domain_status='CONTRADICTORY';
  audit.status='ONE_DECLARED_FEASIBLE';
  audit.scenarios_with_nonempty_intervals=1;
  assert.throws(()=>run(audit),/Inconsistent declared scenario domain status/);
});

test('forged feasible-scenario count or global status is rejected', () => {
  const audit=baseline();
  audit.scenarios_with_nonempty_intervals=1;
  assert.throws(()=>run(audit),/Unsupported or falsely certified/);
  audit.scenarios_with_nonempty_intervals=2;
  audit.status='NO_DECLARED_FEASIBLE';
  assert.throws(()=>run(audit),/Unsupported or falsely certified/);
  audit.status='MULTIPLE_DECLARED_FEASIBLE';
  audit.scenarios_declared=3;
  assert.throws(()=>run(audit),/Unsupported or falsely certified/);
});

test('missing, inverted or inconsistent original exact interval never becomes Float64 witness', () => {
  const audit=baseline();
  audit.scenarios[0].parameters[0].initial=null;
  assert.throws(()=>run(audit),/Missing exact rational interval/);
  audit.scenarios[0].parameters[0].initial={min:'1',max:'0'};
  assert.throws(()=>run(audit),/Inverted exact rational interval/);
  audit.scenarios[0].parameters[0].initial={min:'0',max:'1/10000'};
  assert.throws(()=>run(audit),/expands its original exact domain/);
});

test('trace of unrelated axis or invented historical certification is rejected', () => {
  const audit=baseline();
  audit.scenarios[0].trace.push({...trace('RAAN','bogus'),parameter:'RAAN'});
  assert.throws(()=>run(audit),/Trace cites unsupported velocity parameter/);
  audit.scenarios[0].trace.pop();
  audit.scenarios[0].declared_evidence='DECLARED_NOT_AUDITED';
  assert.throws(()=>run(audit),/Invalid or falsely certified restriction trace/);
});
