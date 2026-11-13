import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import {
  firstOrderJ2RateDegDay, auditSsrJ2PrintInterval, compareSameEditionSsrJ2Rates,
} from '../src/lib/orbitSsrJ2PrintIntervals.ts';

const ledger = JSON.parse(readFileSync(new URL(
  '../research/constraints/C241-P11_november_historical_printings.json', import.meta.url,
)));
const rows = ledger.objects.flatMap(object => object.printed_values_scaled.map((v, index) => ({
  sourceOccurrence: ledger.source_ids[index],
  sourcePdfSha256: ledger.source_sha256[index],
  reportDateUtc: ledger.publication_dates[index],
  designator: object.designator,
  perigeeHalfKm: v.perigee_km,
  apogeeHalfKm: v.apogee_km,
  periodCentimin: v.period_min,
  inclinationCentideg: v.inclination_deg,
})));

test('six source-locked 527/529 entries yield conditional rate intervals without historical epochs', () => {
  assert.equal(rows.length, 6);
  assert.equal(ledger.quantization_units.inclination_deg, 'centidegree');
  for (const row of rows) {
    const d = auditSsrJ2PrintInterval(row);
    assert.equal(d.historicalHoldout, 'NOT_RUN');
    assert.equal(d.historicalDomainReduction, false);
    assert.equal(d.observedEpochUtc, null);
    assert.equal(d.raanDeg, null);
    assert.equal(d.originalSensorSigma, null);
    assert.equal(d.impactInference, 'NOT_SUPPORTED');
    assert.ok(d.printOnlyRangeDegPerDay[0] < d.nominalDegPerDay);
    assert.ok(d.printOnlyRangeDegPerDay[1] > d.nominalDegPerDay);
    assert.ok(d.nominalDegPerDay < -1 && d.nominalDegPerDay > -1.3);
  }
});

test('same NASA SSR edition: printed 529 has faster conditional regression than 527', () => {
  for (const date of ledger.publication_dates) {
    const [a, c] = ['1963-003A', '1963-003C'].map(id =>
      auditSsrJ2PrintInterval(rows.find(r => r.designator === id && r.reportDateUtc === date)));
    const contrast = compareSameEditionSsrJ2Rates(a, c);
    assert.equal(contrast.classification, 'CONDITIONAL_SAME_EDITION_J2_CONTRAST');
    assert.equal(contrast.historicalConstraintActivated, false);
    assert.equal(contrast.disjointPrintRanges, true);
    assert.ok(contrast.aMinusCDegPerDay[0] > 0);
    assert.ok(contrast.aMinusCDegPerDay[1] < 0.1);
  }
});

test('interval encloses independently sampled interior printing-box points', () => {
  for (const row of rows) {
    const d = auditSsrJ2PrintInterval(row);
    for (const t of [0, 0.17, 0.5, 0.84, 1]) {
      const hp = row.perigeeHalfKm / 2 + (t - 0.5);
      const ha = row.apogeeHalfKm / 2 + (0.5 - t);
      const inc = row.inclinationCentideg / 100 + (t - 0.5) * 0.01;
      const rate = firstOrderJ2RateDegDay(hp, ha, inc);
      assert.ok(rate >= d.printOnlyRangeDegPerDay[0] - 1e-12);
      assert.ok(rate <= d.printOnlyRangeDegPerDay[1] + 1e-12);
    }
  }
});

test('J2 null controls: zero oblateness is not inferred; inclination weakens node rate', () => {
  const polarish = firstOrderJ2RateDegDay(400, 440, 89.5);
  const inclined = firstOrderJ2RateDegDay(400, 440, 81.87);
  assert.ok(Math.abs(polarish) < Math.abs(inclined));
  assert.ok(Math.abs(firstOrderJ2RateDegDay(500, 540, 81.87)) < Math.abs(inclined));
});

test('missing custody, fake precision, wrong units and mismatched editions fail closed', () => {
  for (const bad of [
    { inclinationCentideg: 81.87 }, { inclinationCentideg: 9000 },
    { inclinationCentideg: NaN }, { perigeeHalfKm: -5 },
    { sourcePdfSha256: '' }, { reportDateUtc: '1963-11-31' },
    { sourceOccurrence: '' },
  ]) assert.throws(() => auditSsrJ2PrintInterval({ ...rows[0], ...bad }), RangeError);
  const a = auditSsrJ2PrintInterval(rows[0]);
  const c = auditSsrJ2PrintInterval(rows[3]);
  assert.throws(() => compareSameEditionSsrJ2Rates(a, {
    ...c, reportDateUtc: '1963-11-15',
  }), RangeError);
});

test('connected C241-P13 record reproduces the six nominal and three paired print intervals', () => {
  const record = JSON.parse(readFileSync(new URL(
    '../research/constraints/C241-P13_ssr_j2_print_rates_g35.json', import.meta.url,
  )));
  assert.ok(record.depends_on.includes('C241-P11'));
  assert.equal(record.graph.edges.length, 4);
  assert.equal(record.results.length, 6);
  assert.equal(record.paired_model_contrasts.length, 3);
  assert.equal(record.limitations.original_instrument_epoch, null);
  assert.equal(record.limitations.historical_domain_reduction, 'NONE');
  for (const row of rows) {
    const calculated = auditSsrJ2PrintInterval(row);
    const pinned = record.results.find(r => r.designator === row.designator &&
      r.publication_date === row.reportDateUtc);
    assert.equal(pinned.source_pdf_sha256, row.sourcePdfSha256);
    assert.ok(Math.abs(pinned.nominal_deg_day - calculated.nominalDegPerDay) < 1e-8);
    for (let k = 0; k < 2; k++)
      assert.ok(Math.abs(pinned.print_only_signed_deg_day[k] -
        calculated.printOnlyRangeDegPerDay[k]) < 1e-8);
  }
});
