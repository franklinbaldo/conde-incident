"""Synthetic adverse cases only; live dataset is checked by GitHub Actions."""
import hashlib
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from tle_secondary_1963_ledger import (SOURCE_SHA256, checked_source_bytes,
    utc_epoch, extract, summarize, compare_literal, csv_bytes, sha256)

STAMP = datetime(1963, 10, 27, 14, 40, 16, 132512, tzinfo=timezone.utc)


def example(norad=528, stamp=STAMP, raan=198.52610778808594):
    return {'norad_id': norad, 'epoch': stamp, 'inclination': 81.8615036,
            'raan': raan, 'eccentricity': 0.0017147,
            'arg_perigee': 104.7477036, 'mean_anomaly': 255.4423065,
            'mean_motion': 15.74901460, 'mean_motion_dot': 0.00686563,
            'bstar': 0.0, 'intl_designator': '63003 B', 'altitude_km': 300.0}


def literal():
    return {'epoch_utc': '1963-10-27T14:40:16.132512Z',
            'values': {name: {'decimal': value} for name, value in (
                ('inclination', '81.8615'), ('raan','198.5261'),
                ('eccentricity','0.0017147'), ('arg_perigee','104.7477'),
                ('mean_anomaly','255.4423'), ('mean_motion','15.74901460'))}}


class Secondary1963Ledger(unittest.TestCase):
    def test_primary_fingerprint_is_explicit(self):
        self.assertEqual(SOURCE_SHA256,
                         'c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09')
        with self.assertRaisesRegex(ValueError,'SHA-256'):
            checked_source_bytes(b'PAR1synthetic-not-observationPAR1')

    def test_original_row_positions_survive_interleaved_non_targets(self):
        rows = extract([example(600), example(529), example(527), example(528)])
        self.assertEqual([(r['norad_id'], r['source_row']) for r in rows],
                         [(527,2), (528,3), (529,1)])

    def test_utc_microseconds_are_exact_and_quantized(self):
        self.assertEqual(utc_epoch(STAMP), '1963-10-27T14:40:16.132512Z')
        self.assertEqual(utc_epoch(STAMP+timedelta(microseconds=864)),
                         '1963-10-27T14:40:16.133376Z')
        for altered in (STAMP+timedelta(microseconds=1),
                        STAMP+timedelta(microseconds=432),
                        STAMP+timedelta(microseconds=433)):
            with self.assertRaisesRegex(ValueError,'864-us'):
                utc_epoch(altered)

    def test_reject_naive_non_utc_and_wrong_year(self):
        for stamp in (datetime(1963,10,27),
                      STAMP.replace(tzinfo=timezone(timedelta(hours=-4))),
                      STAMP.replace(year=1964)):
            with self.subTest(stamp=stamp):
                with self.assertRaises(ValueError):
                    utc_epoch(stamp)

    def test_invalid_fields_fail_closed(self):
        for field,value in [('raan',360),('raan',-1),('inclination',181),
                            ('eccentricity',1),('mean_motion',0),
                            ('bstar',float('nan')),('altitude_km',float('inf')),
                            ('mean_motion_dot',None)]:
            with self.subTest(field=field):
                rec=example()
                rec[field]=value
                with self.assertRaises(ValueError):
                    extract([rec])
        rec=example()
        rec['intl_designator']='  '
        with self.assertRaisesRegex(ValueError,'designator'):
            extract([rec])

    def test_conflicting_duplicates_not_collapsed(self):
        rows = extract([example(), example(raan=284.152)])
        out = summarize(rows)
        self.assertEqual(out['per_object']['528']['rows'],2)
        self.assertEqual(out['per_object']['528']['unique_epochs'],1)
        self.assertEqual(out['conflicting_duplicate_epochs'][0]['source_rows'],[0,1])
        self.assertFalse(out['legacy_raan_284_1520_active_observation'])

    def test_equal_duplicates_are_preserved_without_conflict(self):
        rows = extract([example(), example()])
        out = summarize(rows)
        self.assertEqual(out['per_object']['528']['duplicate_epoch_rows'],1)
        self.assertEqual(out['conflicting_duplicate_epochs'],[])

    def test_secondary_same_epoch_match_is_not_primary_evidence(self):
        rows=extract([example()])
        out=compare_literal(rows,literal())
        self.assertEqual(out['status'],'AGREES_WITHIN_NUMERIC_ROUNDING')
        self.assertEqual(out['matched_source_rows'],[0])
        self.assertEqual(out['independent_primary_observations'],0)
        self.assertFalse(out['unproven_site_raan_284_1520_active'])

    def test_legacy_raan_or_bad_field_does_not_match(self):
        for bad in (284.152, 198.6):
            with self.subTest(raan=bad):
                r=compare_literal(extract([example(raan=bad)]),literal())
                self.assertEqual(r['status'],'FIELD_CONFLICT')

    def test_absent_and_ambiguous_epoch_are_distinct(self):
        self.assertEqual(compare_literal([],literal())['status'],'NO_MATCH')
        rows=extract([example(),example()])
        self.assertEqual(compare_literal(rows,literal())['status'],'AMBIGUOUS_EPOCH')
        self.assertEqual(compare_literal(extract([example(stamp=STAMP+timedelta(microseconds=864))]),literal())['status'],'NO_MATCH')

    def test_csv_deterministic_lf_and_digests(self):
        rows=extract([example(529), example(528), example(527)])
        result=csv_bytes(rows)
        self.assertEqual(sha256(result),hashlib.sha256(result).hexdigest())
        self.assertEqual(result.count(b'\n'),4)
        self.assertNotIn(b'\r',result)
        self.assertTrue(result.startswith(b'source_row,norad_id,epoch,'))
        self.assertEqual(result, csv_bytes(list(rows)))

    def test_secondary_matrix_not_a_physical_impact_constraint(self):
        a=summarize(extract([example()]))
        self.assertFalse(a['original_tle_line1_line2_present'])
        self.assertFalse(a['original_tle_checksums_verified'])
        self.assertFalse(a['physical_identity_528_verified'])
        self.assertEqual(a['physical_orbital_constraint'],'NOT_PROMOTED')
        self.assertEqual(a['field_units_and_cautions']['mean_motion'], 'revolutions/day')
        self.assertIn('NOT an independent', a['field_units_and_cautions']['altitude_km'])
        self.assertIn('NOT_VERIFIED', a['field_units_and_cautions']['raan'])
        self.assertEqual(a['conde_impact'],'INDETERMINATE')


if __name__ == '__main__':
    unittest.main()
