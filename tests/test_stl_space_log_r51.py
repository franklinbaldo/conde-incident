"""Adversarial R51 checks; run identically under python and python -O."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('audit_stl_r51', BASE / 'tools/audit_stl_space_log_r51.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class R51Tests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(mod.SOURCE.read_text())

    def test_genuine_manifest(self):
        self.assertEqual('EDITORIAL_REPRODUCTION_MILES_PRINTED_SUBTYPE_PENDING_ZERO_CONSTRAINTS', mod.audit(self.data))

    def test_binary_replay(self):
        p = Path('/workspace/.lontra-r51-nasa-databook.pdf')
        if p.exists():
            self.assertEqual('EDITORIAL_REPRODUCTION_MILES_PRINTED_SUBTYPE_PENDING_ZERO_CONSTRAINTS', mod.audit(self.data,p))

    def reject(self, path, value):
        data = copy.deepcopy(self.data)
        parent = data
        for key in path[:-1]:
            parent = parent[key]
        parent[path[-1]] = value
        with self.assertRaises(ValueError):
            mod.audit(data)

    def test_reject_merged_period_values(self):
        self.reject(['printed_row', 'period_minutes_in_printed_order'], [94.7])

    def test_reject_web_transcription_of_inclination(self):
        self.reject(['printed_row', 'inclinations_degrees_in_printed_order'], [82.9])

    def test_accept_documented_miles_without_subtype(self):
        row = self.data['printed_row']
        self.assertEqual(row['perigee_apogee_unit_on_b12'], 'miles')
        self.assertIsNone(row['mile_variant_as_printed'])

    def test_reject_missing_or_fabricated_miles(self):
        self.reject(['printed_row', 'perigee_apogee_unit_on_b12'], None)
        self.reject(['printed_row', 'mile_variant_as_printed'], 'statute')
        self.reject(['printed_row', 'unit_legend_location'], 'B-11')
        self.reject(['scientific_interpretation', 'miles_as_printed_confirmed'], False)

    def test_reject_unverified_km_claim(self):
        self.reject(['printed_row', 'perigee_apogee_unit_on_b12'], 'km')

    def test_reject_extra_sensor(self):
        self.reject(['scientific_interpretation', 'independent_instrumental_sensors_added'], 1)

    def test_reject_november_measurements(self):
        self.reject(['scientific_interpretation', 'new_1963_11_07_09_measurements'], 1)

    def test_reject_new_constraint(self):
        self.reject(['scientific_interpretation', 'new_physical_constraints_activated'], 1)

    def test_reject_unread_original_as_read(self):
        self.reject(['stl_original_issue_retrieved'], True)

    def test_reject_unsupported_parentage(self):
        self.reject(['scientific_interpretation', 'candidate_upstream_proven'], True)

    def test_reject_wrong_page(self):
        self.reject(['pdf_critical_page_one_based'], 104)

    def test_reject_unapproved_contact(self):
        self.reject(['scientific_interpretation', 'archive_external_contact_sent'], True)


if __name__ == '__main__':
    unittest.main()
