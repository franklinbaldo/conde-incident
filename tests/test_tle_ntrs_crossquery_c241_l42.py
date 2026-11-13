"""Adversarial checks on NASA metadata projections, never synthetic tracking."""
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.tle_ntrs_crossquery_c241_l42 import L12, L25, L42, audit


class CrossQueryAudit(unittest.TestCase):
    def setUp(self):
        self.l25 = json.loads(L25.read_text())
        self.l12 = json.loads(L12.read_text())
        self.l42 = json.loads(L42.read_text())
        self.rows = [{
            'id': r['ntrs_id'], 'title': r['title_as_indexed'],
            'otherReportNumbers': r['report_numbers_as_indexed'],
            'publications': [{'publicationDate': r['published_on']}],
        } for r in self.l25['known_records']
            if r['ntrs_id'] in self.l42['captured_1963_source_ids']]
        self.rows += [{'id': -i, 'title': 'UNRELATED_METADATA',
                       'otherReportNumbers': [],
                       'publications': [{'publicationDate': '1964-01-01'}]}
                      for i in range(1, 17)]

    def check(self):
        return audit(self.rows, len(self.rows), self.l25, self.l12, self.l42)

    def test_real_anchor_projection(self):
        result = self.check()
        self.assertEqual(result['crossquery_report_id_count'], 10)
        self.assertEqual(result['october_id_absent_from_report_number_query'], 19640000428)
        self.assertTrue(result['issue_21_not_located_in_this_query'])
        self.assertTrue(result['no_proof_of_absence'])
        self.assertIsNone(result['terminal_location'])
        self.assertFalse(result['physical_constraint_activated'])

    def test_missing_known_anchor_fails(self):
        self.rows.pop(0)
        with self.assertRaisesRegex(ValueError, 'source missing'):
            self.check()

    def test_duplicate_result_fails(self):
        self.rows.append(copy.deepcopy(self.rows[0]))
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.check()

    def test_wrong_october_meta_fails(self):
        self.l12['source']['ntrs_metadata_report_number'] = 'X-533-63-1'
        with self.assertRaisesRegex(ValueError, 're-inspect'):
            self.check()

    def test_october_returned_triggers_review(self):
        self.rows[-1]['id'] = 19640000428
        self.rows[-1]['publications'][0]['publicationDate'] = '1963-10-15'
        with self.assertRaisesRegex(ValueError, 'newly indexed'):
            self.check()

    def test_metadata_title_drift_fails(self):
        self.rows[0]['title'] = 'Different object'
        with self.assertRaisesRegex(ValueError, 'title drift'):
            self.check()

    def test_mutated_source_url_rejected(self):
        self.l42['source_url'] = 'https://example.org/fake'
        with self.assertRaisesRegex(ValueError, 'incomplete or unpinned'):
            self.check()

    def test_possible_issue21_is_candidate_not_instrument(self):
        self.rows[-1]['title'] = 'Satellite Situation Report, Vol. 3, No. 21'
        self.rows[-1]['publications'][0]['publicationDate'] = '1963-11-01'
        r = self.check()
        self.assertEqual(r['candidate_21_ids'], [-16])
        self.assertFalse(r['issue_21_not_located_in_this_query'])
        self.assertEqual(r['additional_1963_ids_pending_review'], [-16])
        self.assertEqual(r['instrumental_528_observations'], 0)

    def test_non_snapshot_raw_bytes_detected(self):
        with self.assertRaisesRegex(ValueError, 'raw response'):
            audit(self.rows, len(self.rows), self.l25, self.l12, self.l42,
                  raw=b'fabricated snapshot')


if __name__ == '__main__':
    unittest.main()
