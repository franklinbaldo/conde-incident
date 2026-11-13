"""CGEO-27 tests on real observed SGB page options and unchanged prior lead."""
import copy
import unittest
from tools.cgeo27_sgb_archive_access import (C26, C27, EXCERPT, check, load,
                                             parse_options, query_url, verify_full_source)


class SgbAccessTests(unittest.TestCase):
    def setUp(self):
        self.record = load(C27)
        self.prior = load(C26)
        self.excerpt = EXCERPT.read_bytes()

    def test_institutional_access_without_document_claim(self):
        self.assertEqual(check(self.record,self.prior,self.excerpt),
                         'OFFICIAL_INSTITUTIONAL_ACCESS_VERIFIED_NO_53D_RESULT')
        self.assertEqual(len(parse_options(self.excerpt.decode())), 4)

    def test_live_acquired_page_replay_if_locally_present(self):
        from pathlib import Path
        p = Path('/workspace/cgeo27-offline-evidence/search.html')
        if p.exists():
            self.assertEqual(verify_full_source(p.read_bytes()), 'ORIGINAL_WEB_FORM_BYTES_REPLAY_PASS')
        else:
            self.assertTrue(self.record['official_source_snapshots'][0]['sha256'])

    def test_violated_archive_coverage_claim(self):
        keys = ('official_search_form_proves_target_file_exists',
                'catalogue_sheet_implies_full_photo_coverage',
                'pre_1963_individual_frame_confirmed','can_constrain_orbital_reentry')
        for key in keys:
            changed = copy.deepcopy(self.record)
            changed['scientific_limits'][key] = True
            with self.subTest(key=key), self.assertRaises(ValueError):
                check(changed,self.prior,self.excerpt)

    def test_no_invented_georeference(self):
        for key in ('center_polygon_1963','fall_point_1963','horizontal_error_m'):
            changed = copy.deepcopy(self.record)
            changed['scientific_limits'][key] = [0,0] if key != 'horizontal_error_m' else 1
            with self.subTest(key=key), self.assertRaises(ValueError):
                check(changed,self.prior,self.excerpt)

    def test_no_invented_inventory_result(self):
        changed = copy.deepcopy(self.record)
        changed['institutional_inventory']['project_53d_entry_found_in_official_online_search_results'] = False
        with self.assertRaises(ValueError):
            check(changed,self.prior,self.excerpt)

    def test_reject_modified_original_excerpt(self):
        with self.assertRaises(ValueError):
            check(self.record,self.prior,self.excerpt.replace(b'FotoDNPM',b'FotoFOO '))

    def test_reject_other_project_or_sheet(self):
        for key, value in [('project','53 E'),('nominal_year',1964),('sheet_mi',38)]:
            changed = copy.deepcopy(self.record)
            changed['target_archival_request'][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                check(changed,self.prior,self.excerpt)

    def test_query_url_escapes_spaces_but_is_not_a_catalogue_hit(self):
        self.assertIn('bib=DNPM+bk',query_url('DNPM bk','Esplanada MI-1850'))
        self.assertIn('pesq=Esplanada+MI-1850',query_url('DNPM bk','Esplanada MI-1850'))
        with self.assertRaises(ValueError):
            query_url('PETROBRAS 53 D','Esplanada')


if __name__ == '__main__':
    unittest.main()
