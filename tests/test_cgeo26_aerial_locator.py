"""CGEO-26 regression tests: preserve archival lead and scientific uncertainty."""
import copy
import unittest
from tools.cgeo26_aerial_locator import check, load, C24, C25, C26


class AerialLocatorTests(unittest.TestCase):
    def setUp(self):
        self.record = load(C26)
        self.sheet = load(C24)
        self.edition = load(C25)

    def test_real_prior_contracts_and_catalogue_entry(self):
        self.assertIn('CONTRACT_ONLY_PASS', check(self.record, self.sheet, self.edition))
        self.assertEqual(self.record['catalogue_occurrence']['observed_entry']['project_nominal_year'], 1961)

    def test_nominal_1961_does_not_date_individual_frames(self):
        for key, value in [('each_frame_proven_pre_incident', True), ('center_point_1963', [0, 0]),
                           ('can_constrain_orbital_reentry', True), ('separate_independent_1963_witness', True)]:
            edited = copy.deepcopy(self.record)
            edited['temporal_and_independence'][key] = value
            with self.subTest(field=key), self.assertRaises(ValueError):
                check(edited, self.sheet, self.edition)

    def test_no_index_to_flight_footprint_promotion(self):
        for key in ('full_sheet_aerial_coverage_verified', 'individual_flight_line_or_photo_footprint_known',
                    'historical_urban_center_inside_flight_footprint_verified'):
            edited = copy.deepcopy(self.record)
            edited['nominal_coverage_crosswalk'][key] = True
            with self.subTest(field=key), self.assertRaises(ValueError):
                check(edited, self.sheet, self.edition)

    def test_cannot_invent_artifact_custody(self):
        for key in ('catalogue_original_pdf_acquired', 'catalogue_page_verified'):
            edited = copy.deepcopy(self.record)
            edited['catalogue_occurrence'][key] = True
            with self.subTest(field=key), self.assertRaises(ValueError):
                check(edited, self.sheet, self.edition)
        for key in ('original_photo_index_acquired', 'original_negative_acquired', 'original_aerial_frames_acquired'):
            edited = copy.deepcopy(self.record)
            edited['artifact_status'][key] = True
            with self.subTest(field=key), self.assertRaises(ValueError):
                check(edited, self.sheet, self.edition)

    def test_photo_scale_not_index_scale(self):
        edited = copy.deepcopy(self.record)
        edited['catalogue_occurrence']['observed_entry']['aerial_photo_nominal_scale_denominator'] = 100000
        with self.assertRaises(ValueError):
            check(edited, self.sheet, self.edition)

    def test_wrong_municipality_or_sheet(self):
        edited = copy.deepcopy(self.record)
        edited['municipality']['state'] = 'PB'
        with self.assertRaises(ValueError):
            check(edited, self.sheet, self.edition)
        edited = copy.deepcopy(self.record)
        edited['catalogue_occurrence']['observed_entry']['sheet_mi'] = 38
        with self.assertRaises(ValueError):
            check(edited, self.sheet, self.edition)

    def test_crosswalk_rejects_changed_bbox_and_camera(self):
        edited = copy.deepcopy(self.record)
        edited['nominal_coverage_crosswalk']['sheet_bbox_w_s_e_n'][2] = -37.9
        with self.assertRaises(ValueError):
            check(edited, self.sheet, self.edition)
        changed_parent = copy.deepcopy(self.sheet)
        changed_parent['camera_observations'][0]['lon'] = -36.9
        with self.assertRaises(ValueError):
            check(self.record, changed_parent, self.edition)

    def test_independent_source_claim_is_unknown_not_true(self):
        edited = copy.deepcopy(self.record)
        edited['temporal_and_independence']['same_observational_lineage_as_1956_1963_sacs_geofoto_sheets'] = False
        with self.assertRaises(ValueError):
            check(edited, self.sheet, self.edition)

    def test_cannot_upgrade_mirror_to_source_pdf(self):
        edited = copy.deepcopy(self.record)
        edited['catalogue_occurrence']['source_grade'] = 'PRIMARY_PDF_VERIFIED'
        with self.assertRaises(ValueError):
            check(edited, self.sheet, self.edition)


if __name__ == '__main__':
    unittest.main()
