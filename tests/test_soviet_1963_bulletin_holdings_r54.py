"""Adversarial record checks, run under Python normal and optimized modes."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("bulletin_r54", ROOT / "tools/audit_soviet_1963_bulletin_holdings_r54.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class BulletinR54(unittest.TestCase):
    def setUp(self):
        self.base = json.loads(mod.SOURCE.read_text(encoding="utf-8"))

    def mutate(self, path, new):
        data = copy.deepcopy(self.base)
        item = data
        for field in path[:-1]:
            item = item[field]
        item[path[-1]] = new
        with self.assertRaises(ValueError):
            mod.audit(data)

    def test_locator_only(self):
        self.assertEqual(mod.audit(self.base), "SIX_1963_ISSUES_INDEXED_ONLY")

    def test_wrong_year(self):
        self.mutate(["subject", "catalog_year"], 1964)

    def test_wrong_fascicles(self):
        self.mutate(["subject", "issue_numbers_in_ukrainian_catalog"], [32, 33, 34])

    def test_no_november_coverage(self):
        self.mutate(["subject", "november_1963_coverage_verified"], True)

    def test_no_target_identification(self):
        self.mutate(["subject", "target_designations_in_contents_verified"], True)

    def test_no_contents_read(self):
        self.mutate(["subject", "issue_contents_read"], True)

    def test_no_facsimile_sha(self):
        self.mutate(["subject", "facsimile_pdf_sha256"], "a" * 64)

    def test_no_page_or_utc(self):
        self.mutate(["subject", "pages_or_observation_utc_verified"], "1963-11-08")

    def test_no_new_sensor(self):
        self.mutate(["epistemic_limits", "independent_instrumental_sensors"], 1)

    def test_no_new_constraint(self):
        self.mutate(["epistemic_limits", "new_orbital_constraints_activated"], 1)

    def test_no_norad_observation(self):
        self.mutate(["epistemic_limits", "new_527_528_529_observations_1963_11_07_to_09"], 1)

    def test_duplicate_ukrainian_records(self):
        self.mutate(["locators", 1, "same_catalog_as"], None)

    def test_no_download(self):
        self.mutate(["locators", 0, "retrieved_facsimile"], True)

    def test_tls_failure_not_200(self):
        self.mutate(["locators", 0, "direct_jatoba_http_status"], 200)

    def test_japan_not_sensor(self):
        self.mutate(["locators", 2, "independent_instrumental_observation"], True)

    def test_japan_id(self):
        self.mutate(["locators", 2, "catalog_id"], "unknown")

    def test_index_not_observation_date(self):
        self.mutate(["epistemic_limits", "bibliographic_issue_number_establishes_observation_date"], True)

    def test_no_outreach(self):
        self.mutate(["epistemic_limits", "external_institution_contact_sent"], True)


if __name__ == "__main__":
    unittest.main()
