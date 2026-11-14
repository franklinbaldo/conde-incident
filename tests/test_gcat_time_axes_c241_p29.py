"""C241-P29 regression of GCAT payload-vs-orbital-date semantics."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import audit_gcat_time_axes_c241_p29 as gcat


class GcatTimeAxesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(gcat.LEDGER.read_text())

    def test_pinned_records_preserve_distinct_time_axes(self):
        result = gcat.audit(self.original)
        self.assertEqual(result['payload_end_date_527'], '1963-01-18')
        self.assertEqual(result['orbital_decay_dates'], {'527':'1969-01-09', '528':'1963-11-08', '529':'1963-12-31'})
        self.assertIsNone(result['observation_epoch_utc'])
        self.assertEqual(result['physical_domain_effect'], 'THETA_UNCHANGED')

    def mutate(self, source, number, old, new):
        d = copy.deepcopy(self.original)
        row = d['sources'][source]['rows'][str(number)]
        self.assertIn(old,row['line'])
        row['line'] = row['line'].replace(old,new)
        # Rehash: an attacker with access to ledger can forge row hash.
        import hashlib
        row['sha256'] = hashlib.sha256(row['line'].encode()).hexdigest()
        return d

    def test_wrong_527_end_of_transmission_rejected_even_with_rehashed_row(self):
        d = self.mutate('payload',527,'1963 Jan 18','1969 Jan  9')
        with self.assertRaisesRegex(ValueError,'payload operations'):
            gcat.audit(d)

    def test_527_deorbit_falsely_replaced_by_payload_silence_rejected(self):
        d = self.mutate('object',527,'1969 Jan  9 1200?','1963 Jan 18')
        with self.assertRaisesRegex(ValueError,'527 orbital decay'):
            gcat.audit(d)

    def test_wrong_satellite_identity_rejected(self):
        d = self.mutate('object',528,'1963-003B','1963-003A')
        with self.assertRaisesRegex(ValueError,'COSPAR'):
            gcat.audit(d)

    def test_wrong_parent_rejected(self):
        d = self.mutate('object',529,'S00527','S00528')
        with self.assertRaisesRegex(ValueError,'genealogy'):
            gcat.audit(d)

    def test_forced_hour_for_528_rejected(self):
        d = self.mutate('object',528,'1963 Nov  8','1963 Nov  8 1230')
        with self.assertRaisesRegex(ValueError,'invented precision'):
            gcat.audit(d)

    def test_no_fake_instrumental_claim_or_theta_reduction(self):
        for field, value in [('new_instrumental_measurements',1),('physical_domain_effect','THETA_REDUCED'),('shared_gcat_lineage_not_independent',False)]:
            d = copy.deepcopy(self.original)
            d['interpretation'][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError,'unsupported sensor'):
                gcat.audit(d)

    def test_wrong_source_or_hash_rejected(self):
        for field, value in [('url','https://example.org/not-gcat.tsv'),('sha256_full_tsv','0'*32)]:
            d = copy.deepcopy(self.original)
            d['sources']['payload'][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                gcat.audit(d)

    def test_missing_row_and_tampered_row_digest_rejected(self):
        d = copy.deepcopy(self.original)
        del d['sources']['object']['rows']['529']
        with self.assertRaisesRegex(ValueError,'missing/extra'):
            gcat.audit(d)
        d = copy.deepcopy(self.original)
        d['sources']['object']['rows']['529']['line'] += 'x'
        with self.assertRaisesRegex(ValueError,'row digest'):
            gcat.audit(d)


if __name__ == '__main__':
    unittest.main()
