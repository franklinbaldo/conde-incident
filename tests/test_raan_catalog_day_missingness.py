"""Status day, missingness and retained-epoch audit, with no inferred impact."""
import copy
from fractions import Fraction
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from raan_catalog_day_missingness import (  # noqa: E402
    SERIES, IDENTITY, SPLIT, OUTPUT, build, day, timestamp,
)


def source_bytes():
    return tuple((ROOT / x).read_bytes() for x in (SERIES, IDENTITY, SPLIT))


def mutate_json(raw, function):
    payload = json.loads(raw)
    function(payload)
    return json.dumps(payload).encode()


class CatalogDayMissingnessTests(unittest.TestCase):
    def test_report_replay_exact(self):
        self.assertEqual(build(*source_bytes()), json.loads((ROOT / OUTPUT).read_text()))

    def test_528_primary_document_versus_mirror_last_epoch(self):
        out = build(*source_bytes())
        r = out['objects']['528']
        self.assertEqual(r['catalog_designator'], '1963-003B')
        self.assertEqual(r['catalog_status_day'], '1963-11-08')
        self.assertEqual(r['catalog_status_source_kind'], 'NASA_PRIMARY_DAY_ONLY_REPORT')
        self.assertEqual(r['unique_1963_epochs'], 45)
        self.assertEqual(r['last_mirror_epoch_utc'], '1963-10-27T14:40:16.132512Z')
        self.assertEqual(Fraction(r['gap_last_mirror_epoch_to_status_day_start_days_exact']),
                         Fraction(1138870217, 100000000))
        self.assertFalse(r['status_day_is_observed_terminal_time'])
        self.assertFalse(r['status_day_is_observed_non_detection_time'])
        self.assertFalse(r['gap_is_surveillance_interval'])

    def test_no_527_528_529_entity_collapse(self):
        r = build(*source_bytes())['objects']
        self.assertEqual([r[str(i)]['unique_1963_epochs'] for i in (527, 528, 529)],
                         [20, 45, 54])
        self.assertEqual([r[str(i)]['excluded_same_object_same_epoch_duplicates']
                          for i in (527, 528, 529)], [1, 0, 3])
        self.assertEqual(r['527']['catalog_status_day'], '1969-01-09')
        self.assertIsNone(r['527']['gap_last_mirror_epoch_to_status_day_start_days_exact'])
        self.assertEqual(r['527']['gap_not_computed_reason'], 'SOURCE_EXCERPT_ONLY_1963')
        self.assertEqual(r['529']['catalog_status_source_kind'], 'MODERN_SECONDARY_CATALOG_DAY')

    def test_missingness_likelihood_is_not_inferred(self):
        out = build(*source_bytes())
        gates = out['inference_gates']
        for name in ('historical_surveillance_schedule', 'detection_probability_by_epoch',
                     'catalog_retention_and_selection_model',
                     'status_label_to_physical_event_model'):
            self.assertIsNone(gates[name])
        self.assertEqual(gates['historical_missingness_likelihood'], 'NOT_IDENTIFIED')
        self.assertEqual(gates['terminal_utc_time'], 'NOT_IDENTIFIED')
        self.assertEqual(gates['historical_posterior'], 'NOT_RUN')
        self.assertFalse(gates['active_constraint'])

    def test_duplication_does_not_increase_independent_epochs(self):
        series, identity, split = source_bytes()
        extra = mutate_json(series, lambda s: s['records'].append(copy.deepcopy(s['records'][0])))
        out = build(extra, identity, split)
        self.assertEqual(out['objects']['527']['unique_1963_epochs'], 20)
        self.assertEqual(out['objects']['527']['excluded_same_object_same_epoch_duplicates'], 2)
        self.assertEqual(out['inference_gates']['historical_missingness_likelihood'],
                         'NOT_IDENTIFIED')

    def test_mutated_after_label_epoch_is_flag_not_survival_estimate(self):
        series, identity, split = source_bytes()
        payload = json.loads(series)
        original = max((r['epoch_utc'] for r in payload['records'] if r['norad'] == 528))
        alternate = '1963-11-09T14:40:16.132512Z'
        for r in payload['records']:
            if r['norad'] == 528 and r['epoch_utc'] == original:
                r['epoch_utc'] = alternate
        frozen = json.loads(split)
        frozen['memberships']['528']['evaluation'] = [
            alternate if t == original else t
            for t in frozen['memberships']['528']['evaluation']]
        out = build(json.dumps(payload).encode(), identity, json.dumps(frozen).encode())
        self.assertEqual(out['objects']['528']['mirror_epochs_on_or_after_status_day_start'], 1)
        self.assertIsNone(out['objects']['528']['gap_last_mirror_epoch_to_status_day_start_days_exact'])
        self.assertFalse(out['inference_gates']['active_constraint'])
        self.assertEqual(out['inference_gates']['terminal_utc_time'], 'NOT_IDENTIFIED')

    def test_primary_designator_and_date_mismatch_fails(self):
        series, identity, split = source_bytes()
        for field, value in [('catalog_designator_printed', '1963 3A'),
                             ('decay_day', '1963-11-09')]:
            changed = mutate_json(identity, lambda i: i['primary_date_only_record'].__setitem__(field, value))
            with self.assertRaises(ValueError):
                build(series, changed, split)

    def test_mismatched_frozen_holdout_rejected(self):
        series, identity, split = source_bytes()
        changed = mutate_json(split, lambda p: p['memberships']['528']['fit'].pop())
        with self.assertRaises(ValueError):
            build(series, identity, changed)

    def test_bad_timestamp_and_day_inputs(self):
        for t in ('1963-11-08T00:00:00', '1963-11-08T00:00:00+01:00', 'fooZ'):
            with self.assertRaises(ValueError):
                timestamp(t)
        for t in ('1963-11-8', '1963-02-29', '1963-11-08Z'):
            with self.assertRaises(ValueError):
                day(t)

    def test_foreign_year_source_rejected(self):
        series, identity, split = source_bytes()
        changed = mutate_json(series, lambda s: s['records'][0].__setitem__('epoch_utc',
                                                                              '1964-01-01T00:00:00Z'))
        with self.assertRaises(ValueError):
            build(changed, identity, split)


if __name__ == '__main__':
    unittest.main()
