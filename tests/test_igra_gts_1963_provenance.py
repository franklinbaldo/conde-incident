"""Adversarial metadata/date/uncertainty controls for historical GTS provenance."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import validate_igra_gts_1963_provenance as audit


class HistoricalGtsProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(audit.SOURCE.read_text())
        cls.older = json.loads(audit.OLDER.read_text())

    def reject(self, change):
        altered = copy.deepcopy(self.data)
        change(altered)
        with self.assertRaises(ValueError):
            audit.validate(altered, self.older)

    def test_valid_lineage(self):
        self.assertTrue(audit.validate(self.data, self.older))

    def test_cannot_backdate_method_to_1963(self):
        self.reject(lambda d: d["sources"]["igra_methods_2006"].update(published="1963-11-08"))

    def test_cannot_claim_original_wmo_1963_catalogue(self):
        self.reject(lambda d: d["sources"]["wmo_historical_catalogue_scope"].update(historical_1963_catalogue_obtained=True))

    def test_cannot_claim_specific_gts_message(self):
        self.reject(lambda d: d["recife_case"].update(original_gts_message_obtained=True))

    def test_cannot_fill_1963_sensor(self):
        self.reject(lambda d: d["recife_case"].update(original_1963_radiosonde_model="Vaisala RS21"))

    def test_cannot_invent_historical_position(self):
        self.reject(lambda d: d["recife_case"].update(original_1963_launch_site_coordinates=[-8.05, -34.9167]))

    def test_cannot_claim_proven_upstream_mapping(self):
        self.reject(lambda d: d["recife_case"].update(upstream_yearly_code_proven_to_be_original_recife_gts_message=True))

    def test_reject_wrong_igra_pin(self):
        self.reject(lambda d: d["recife_case"].update(original_archive_sha256="0" * 64))

    def test_reject_independent_observation(self):
        self.reject(lambda d: d["interpretation"].update(independent_measurements_added=1))

    def test_reject_domain_reduction(self):
        self.reject(lambda d: d["interpretation"].update(admissible_domain_reduction=True))

    def test_reject_claimed_1963_release_time(self):
        self.reject(lambda d: d["recife_case"].update(original_1963_release_time_utc="1963-11-08T12:00:00Z"))


if __name__ == "__main__":
    unittest.main()
