import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { auditSsrPrintedPeriod } from '../src/lib/orbitSsrPeriodAudit.ts';
import { EARTH } from '../src/lib/orbitPhysics.ts';

const source = JSON.parse(readFileSync(new URL('../research/constraints/C241-P11_november_historical_printings.json', import.meta.url)));
const link = JSON.parse(readFileSync(new URL('../research/statistics/ssr_post528_print_contrasts_C241.json', import.meta.url)));
const rows = source.objects.flatMap(object => object.printed_values_scaled.map((values, i) => ({
  sourceOccurrence: source.source_ids[i] ?? 'C241-P11',
  sourcePdfSha256: source.source_sha256[i],
  reportDateUtc: source.publication_dates[i],
  designator: object.designator,
  perigeeHalfKm: values.perigee_km,
  apogeeHalfKm: values.apogee_km,
  periodCentimin: values.period_min,
})));

test('NASA compiled 527/529 October-November values are in half-km and centiminute ledger units', () => {
  assert.equal(rows.length, 6);
  assert.equal(source.quantization_units.apogee_km, 'half-kilometer');
  assert.equal(source.same_compilation_not_independent_sensors, true);
  assert.equal(link.limits.instrumental_epoch, null);
  for (const row of rows) {
    const result = auditSsrPrintedPeriod(row);
    assert.equal(result.classification, 'DOCUMENTARY_UNIT_AND_KEPLER_DIAGNOSTIC');
    assert.equal(result.historicalHoldout, 'NOT_RUN');
    assert.equal(result.originalObservationEpochUtc, null);
    assert.equal(result.originalInstrumentCovariance, null);
    assert.equal(result.impactInference, 'NOT_SUPPORTED');
    // 6 printings: two-body differences 3-5 s. This is a plausibility check,
    // NOT a test of J2 or instrumental orbit fit.
    assert.ok(result.printedMinusKeplerSec > 3 && result.printedMinusKeplerSec < 5);
    assert.ok(result.printRoundingResidualSec[0] <= result.printedMinusKeplerSec);
    assert.ok(result.printRoundingResidualSec[1] >= result.printedMinusKeplerSec);
    assert.ok(result.wrongUnitResidualSec < -450);
  }
});

test('half-km mistake is visible even though an unrelated Kepler formula remains executable', () => {
  const row = rows[0];
  const result = auditSsrPrintedPeriod(row);
  assert.equal(result.semiMajorAxisKm, EARTH.radiusKm + (row.perigeeHalfKm + row.apogeeHalfKm) / 4);
  assert.ok(Math.abs(result.wrongUnitResidualSec) > 100 * Math.abs(result.printedMinusKeplerSec));
});

test('quantization interval widens when altitude rises, never becomes a sensor covariance', () => {
  const low = auditSsrPrintedPeriod(rows.find(r => r.designator === '1963-003C' && r.reportDateUtc === '1963-11-30'));
  const high = auditSsrPrintedPeriod(rows.find(r => r.designator === '1963-003A' && r.reportDateUtc === '1963-11-30'));
  assert.ok(high.semiMajorAxisKm > low.semiMajorAxisKm);
  assert.ok(high.printRoundingResidualSec[1] - high.printRoundingResidualSec[0] >
            low.printRoundingResidualSec[1] - low.printRoundingResidualSec[0]);
});

test('missing custody or impossible printed units fail closed', () => {
  for (const variant of [
    { sourcePdfSha256: 'none' }, { sourceOccurrence: '' }, { reportDateUtc: '1963-02-31' },
    { designator: '1963-003B' }, { perigeeHalfKm: -1 },
    { apogeeHalfKm: -1 }, { apogeeHalfKm: 1e7 },
    { periodCentimin: 0 }, { periodCentimin: Infinity },
    { perigeeHalfKm: 10001.5 },
  ]) assert.throws(() => auditSsrPrintedPeriod({ ...rows[0], ...variant }), RangeError);
});
