"""C241-P22 exact nine-source jackknife, independent contrast and mutation guards."""
from __future__ import annotations

import copy
import json
import unittest
from formal.scripts import compile_ssr_jackknife as m
from formal.scripts import compile_ssr_nine_editions as parent
from tools import tle_ssr_editions_precision_audit as audit


class JackknifeTests(unittest.TestCase):
    def test_all_nine_exact_minima_and_witnesses(self):
        r = m.build()
        cells, sources = parent.source_rows()
        self.assertEqual(r['baseline_all_nine_centiminute'], 128)
        self.assertEqual(len(r['delete_one']), 9)
        expected = [120, 128, 128, 128, 128, 128, 128, 128, 68]
        self.assertEqual([x['minimum_residual_centiminute'] for x in r['delete_one']], expected)
        for row, doc in zip(r['delete_one'], sources):
            removed = row['removed_publication']
            self.assertEqual(removed, doc['publication'])
            reduced = m.without_date(cells, removed)
            self.assertEqual(len(reduced), row['retained_printed_cells'])
            self.assertTrue(all(d != removed for _, d in reduced))
            w = row['attaining_witness']
            residuals = [v - w['object_baselines'][str(obj)] - w['publication_offsets'][d]
                         for (obj, d), v in reduced.items()]
            self.assertEqual(max(map(abs, residuals)), w['max_abs_residual'])
            self.assertLessEqual(max(map(abs, residuals)), row['minimum_residual_centiminute'])
            self.assertIsNone(parent.feasible(reduced, row['minimum_residual_centiminute'] - 1))
        self.assertEqual(r['physical_domain'], 'THETA_UNCHANGED')
        self.assertIsNone(r['instrument_error_sigma'])
        self.assertFalse(r['publication_is_instrument_epoch'])

    def test_necessary_contrast_independent_of_bellman_ford(self):
        cells, _ = parent.source_rows()
        for row in m.build()['delete_one']:
            pair = row['lower_bound_contrast']
            first, last = pair['publications']
            removed = row['removed_publication']
            self.assertNotIn(removed, pair['publications'])
            self.assertEqual(m.bound_from_contrast(cells, first, last),
                             row['minimum_residual_centiminute'])
            self.assertEqual(pair['gap_change_centiminute'],
                             abs(pair['gap_centiminute'][0] - pair['gap_centiminute'][1]))

    def test_adversarial_source_and_instrument_mutations_fail(self):
        model = audit.read(audit.MODEL)
        ledgers = {d['ledger']: audit.read(d['ledger']) for d in model['docs']}
        decay = audit.read(audit.DECAY)
        mutations = (
            lambda d: d['docs'][8].update(pdf_sha256='0' * 64),
            lambda d: d['docs'][0].update(published='1963-04-29'),
            lambda d: d.update(raw_instrument_528_sigma='0.05'),
            lambda d: d['graph'].update(physical_constraints_active=True),
        )
        for mutation in mutations:
            modified = copy.deepcopy(model)
            mutation(modified)
            with self.assertRaises(ValueError):
                m.build(modified, copy.deepcopy(ledgers), decay)

    def test_outputs_are_pinned_and_proofs_cover_every_deletion(self):
        result = m.build()
        self.assertEqual(json.loads(m.REPORT.read_text()), result)
        lean = m.render_lean(result)
        self.assertEqual(m.LEAN.read_text(), lean)
        for entry in result['delete_one']:
            name = entry['removed_publication'][5:].replace('-', '')
            self.assertIn(f'without_{name}_lower_bound', lean)
            self.assertIn(f'without_{name}_witness', lean)
        self.assertNotIn('sorry', lean)
        self.assertNotIn('axiom ', lean)


if __name__ == '__main__':
    unittest.main()
