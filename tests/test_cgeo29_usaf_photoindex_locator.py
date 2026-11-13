"""Adversarial source-to-claim checks for the SGB USAF 63-32 MI-1850 node."""
import copy
import unittest

from tools.cgeo29_usaf_photoindex_locator import (
    C26, C27, MANIFEST, NODE, load, validate, verify_full_html,
)


class UsaPhotoIndexNodeTests(unittest.TestCase):
    def setUp(self):
        self.record = load(MANIFEST)
        self.c26 = load(C26)
        self.c27 = load(C27)
        self.source = NODE.read_bytes()

    def test_actual_institutional_tree_node_is_new_archival_lead(self):
        self.assertEqual(validate(self.record, self.c26, self.c27, self.source),
                         'OFFICIAL_USAF_63_32_MI1850_TREE_NODE_REPLAY_PASS')

    def test_replay_original_full_response_if_available(self):
        from pathlib import Path
        path = Path('/workspace/caranguejo-r27-evidence/FotoUSAF_root.html')
        if path.is_file():
            self.assertEqual(verify_full_html(self.record, path.read_bytes()),
                             'FULL_ORIGINAL_OFFICIAL_HTML_REPLAY_PASS')

    def test_modified_real_node_excerpt_is_rejected(self):
        for old, new in ((b'1850', b'1851'), (b'63-32', b'53 D')):
            with self.subTest(old=old), self.assertRaises(ValueError):
                validate(self.record, self.c26, self.c27, self.source.replace(old, new))

    def test_project_family_is_not_same_flight_as_pet53d(self):
        for key, value in (
            ('same_aerial_flight_or_photoindex_as_pet53d', True),
            ('same_observational_lineage', False),
            ('index_file_is_pre_incident', True),
            ('printed_project_code_is_a_capture_date', True)):
            bad = copy.deepcopy(self.record)
            bad['crosswalk'][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate(bad, self.c26, self.c27, self.source)

    def test_no_imagined_frame_date_coordinate_or_reentry(self):
        for key, val in (
            ('original_photoindex_image_acquired', True),
            ('individual_aerial_frame_acquired', True),
            ('date_of_individual_capture_verified', True),
            ('historical_center_geometry', [-37.7, -11.7]),
            ('event_position_1963', [-37.7, -11.7]),
            ('horizontal_error_m', 20),
            ('can_constrain_orbital_reentry', True)):
            bad = copy.deepcopy(self.record)
            bad['scientific_limits'][key] = val
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate(bad, self.c26, self.c27, self.source)

    def test_wrong_sheet_or_reader_rejected(self):
        for field, val in (('sheet_mi', 38), ('usaf_cim_literal', 'SC.24-Z-D-VI')):
            bad = copy.deepcopy(self.record)
            bad['crosswalk'][field] = val
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate(bad, self.c26, self.c27, self.source)

    def test_false_target_absence_and_graph_loss_rejected(self):
        bad = copy.deepcopy(self.record)
        bad['evidence_state'] = 'TARGET_IMAGE_UNAVAILABLE'
        with self.assertRaises(ValueError):
            validate(bad, self.c26, self.c27, self.source)
        bad = copy.deepcopy(self.record)
        bad['graph_edges'].pop()
        with self.assertRaises(ValueError):
            validate(bad, self.c26, self.c27, self.source)


if __name__ == '__main__':
    unittest.main()
