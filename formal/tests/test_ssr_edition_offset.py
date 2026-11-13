"""C241-P12: primary-source mutations and negative model controls."""
import copy
import json
import unittest

from formal.scripts.compile_ssr_edition_offset import (
    NOV, OCT, SUR, DEC, GRAPH, G34, G34AUD, G34LED, G34LOCK,
    REPORT, LEAN, build, contrast, render_lean,
)

N, O, S, D, G = [json.loads(x.read_text()) for x in (NOV, OCT, SUR, DEC, GRAPH)]
K = json.loads(G34.read_text())
KA = [json.loads(x.read_text()) for x in (G34LED, G34AUD, G34LOCK)]


class TestEditionOffset(unittest.TestCase):
    def test_three_printed_publications_falsify_common_edition_bias(self):
        r = build(N, O, S, D, G)
        self.assertEqual(r['printed_period_centimin']['527'], [9460]*3)
        self.assertEqual(r['printed_period_centimin']['529'], [9260, 9220, 9160])
        self.assertEqual(r['printed_527_minus_529_centimin'], [200, 240, 300])
        self.assertEqual([x['nearest_tenth_conditional_interval_centimin']
                          for x in r['printed_contrasts']],
                         [[20, 60], [40, 80], [80, 120]])
        self.assertFalse(r['physical_constraint_active'])
        self.assertIsNone(r['observation_epoch_utc'])
        self.assertIsNone(r['instrument_covariance'])
        self.assertEqual(r['admissible_domain'], 'THETA_UNCHANGED')
        self.assertEqual(len(r['g34_documentary_diagnostics']['cell_keys']), 6)
        self.assertFalse(r['g34_documentary_diagnostics']['independent_sensor_provenance_established'])

    def test_shared_offset_negative_control(self):
        self.assertFalse(contrast(9460, 9260, 9460, 9260)
                         ['common_additive_edition_offset_rejected'])
        self.assertFalse(contrast(9460, 9260, 9470, 9270)
                         ['common_additive_edition_offset_rejected'])
        self.assertTrue(contrast(9460, 9260, 9460, 9160)
                        ['common_additive_edition_offset_rejected'])

    def test_custody_cell_and_unknown_epoch_mutations_fail(self):
        mutations = [
            (0, lambda x: x['documents'][0]['rows'][1].update(period_min='92.8')),
            (0, lambda x: x['documents'][0].update(sha256='0'*64)),
            (2, lambda x: x['sources'][1]['rows'][1].update(period_min='92.7')),
            (3, lambda x: x['rows'][1].update(period_min='91.8')),
            (3, lambda x: x['source'].update(sha256='a'*64)),
            (3, lambda x: x['limits'].update(instrumental_epoch_utc='1963-12-15T12:00:00Z')),
            (4, lambda x: x['observables'][1].update(measurement_sigma=0.05)),
        ]
        for pos, change in mutations:
            docs = copy.deepcopy([N, O, S, D, G])
            change(docs[pos])
            with self.subTest(pos=pos, change=change), self.assertRaises(ValueError):
                build(*docs)

    def test_g34_six_cell_identity_and_sensor_mutations_fail(self):
        for mutation in (
            lambda k: k['cells'][0].update(source_pdf_sha256='f'*64),
            lambda k: k['cells'][1].update(object='1963-003B'),
            lambda k: k['cells'][2].update(report_publication_date_not_epoch='1963-12-15'),
            lambda k: k['cells'][2].update(instrument_epoch='1963-11-30T12:00:00Z'),
            lambda k: k['cells'][3].update(covariance=0),
            lambda k: k['cells'].append(copy.deepcopy(k['cells'][0])),
            lambda k: k.update(publication_dates_are_sensor_epochs=True),
        ):
            bad = copy.deepcopy(K)
            mutation(bad)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                build(N, O, S, D, G, g34_bundle=bad)
        bad = copy.deepcopy(KA)
        bad[1]['cross_field_diagnostics'][0]['sensor_sigma'] = 4.0
        with self.assertRaises(ValueError):
            build(N, O, S, D, G, g34_inputs=tuple(bad))

    def test_deterministic_source_locked_lean_and_report(self):
        report = build(N, O, S, D, G)
        self.assertEqual(json.loads(REPORT.read_text()), report)
        self.assertEqual(LEAN.read_text(), render_lean(report))
        self.assertIn('theorem no_shared_additive_edition_offset', LEAN.read_text())
        self.assertNotIn('sorry', LEAN.read_text())


if __name__ == '__main__':
    unittest.main()
