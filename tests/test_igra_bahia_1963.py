"""Independent negative controls for historical IGRA coverage near Conde/BA."""
import copy
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile
from unittest import TestCase
from unittest.mock import patch
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import audit_igra_bahia_1963 as audit


class TestBahia1963(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(audit.REPORT.read_text())

    def test_pinned_sources_and_ibge_bbox(self):
        audit.validate_report(self.report)
        self.assertEqual(self.report['reference']['coordinates_valid_for_1963'], None)
        self.assertEqual(self.report['catalogue']['within_1500_km'], 31)
        self.assertEqual(self.report['catalogue']['year_1963_in_catalogue_bounds'], 4)

    def test_year_overlap_is_not_an_observation(self):
        rows = self.report['catalogue']['rows']
        eligible = {r['station_id']:r['approx_bbox_center_km'] for r in rows if r['year_1963_inside_inventory_bounds']}
        self.assertEqual(set(eligible), set(audit.ARCHIVES))
        self.assertAlmostEqual(eligible['BRM00082900'],521.6,delta=1)
        archives = {r['station_id']:r for r in self.report['audited_archives']}
        self.assertEqual({x:archives[x]['sounding_headers_1963'] for x in archives},
                         {'BRM00082400':0,'BRM00082599':0,'BRM00082900':346,'BRM00083746':72})
        self.assertEqual(archives['BRM00082900']['dates_nov_07_09_1963'], {x:1 for x in audit.NOV_DATES})
        self.assertEqual(archives['BRM00083746']['months_1963'].get('11',0),0)

    def test_false_physical_promotion_rejected(self):
        for field, wrong in [('independent_conde_wind_observation_1963_11_08', 10),
                             ('spatiotemporal_transfer_uncertainty', 0),
                             ('instrumental_covariance', []),
                             ('geographic_constraint_activated',True)]:
            candidate = copy.deepcopy(self.report)
            candidate['result'][field] = wrong
            with self.subTest(field=field), self.assertRaises(ValueError):
                audit.validate_report(candidate)

    def test_false_station_coverage_rejected(self):
        candidate = copy.deepcopy(self.report)
        next(x for x in candidate['audited_archives'] if x['station_id']=='BRM00083746')['dates_nov_07_09_1963']={'1963-11-08':1}
        with self.assertRaises(ValueError):
            audit.validate_report(candidate)
        candidate = copy.deepcopy(self.report)
        candidate['catalogue']['rows'][0]['year_1963_inside_inventory_bounds'] = True
        with self.assertRaises(ValueError):
            audit.validate_report(candidate)

    def test_mismatched_catalogue_hash_rejected(self):
        with self.assertRaises(ValueError):
            audit.catalogue_rows(b'BRM00082900 malformed and untrusted')

    def test_archive_hash_and_header_protection(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'BRM00082900-data.txt.zip'
            p.write_bytes(b'fabricated')
            with self.assertRaises(ValueError):
                audit.archive_dates(p, 'BRM00082900')
            with ZipFile(p,'w') as z:
                z.writestr('BRM00082900-data.txt',b'#BRM00082599 1963 11 08 12\n')
            raw=p.read_bytes()
            with patch.dict(audit.ARCHIVES,{'BRM00082900':(len(raw),sha256(raw).hexdigest(),1,{})}):
                with self.assertRaisesRegex(ValueError,'station mismatch'):
                    audit.archive_dates(p,'BRM00082900')

    def test_bbox_distance_does_not_claim_historical_coordinates(self):
        r=self.report['reference']
        self.assertEqual(r['type'],'midpoint_of_IBGE_2022_municipality_bbox_not_centroid')
        self.assertIsNone(r['historical_site_distance_error_km'])
        self.assertEqual(self.report['result']['status'],'CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION')


if __name__ == '__main__':
    import unittest
    unittest.main()
