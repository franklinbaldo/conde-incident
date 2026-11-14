"""C241-P44 negative attribution guards, safe under python -O."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("route_p44", ROOT / "tools/audit_fragment_recovery_routes_C241_P44.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class RouteTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(mod.LEDGER.read_text(encoding="utf-8"))
    def reject(self, path, value):
        data = copy.deepcopy(self.data)
        node = data
        for p in path[:-1]:
            node = node[p]
        node[path[-1]] = value
        with self.assertRaises(ValueError):
            mod.audit(data)
    def test_verified_custody(self):
        self.assertEqual(mod.audit(self.data)["status"], "ARCHIVAL_LEADS_ONLY")
    def test_cannot_count_multiple_notes_as_sensors(self):
        self.reject(["classification", "observations_of_527_528_529_added"], 4)
    def test_1962_tanks_not_1963_003b(self):
        self.reject(["sources", 1, "identified_with_norad_528"], True)
    def test_launch_year_not_recovery_year(self):
        self.reject(["sources", 1, "launch_year"], 1963)
    def test_1968_memo_not_confirmed_case(self):
        self.reject(["archival_routes", 0, "case_1963_003_b_confirmed"], True)
    def test_unretrieved_primary_cannot_be_retrieved(self):
        self.reject(["archival_routes", 1, "item_retrieved"], True)
    def test_archival_box_is_not_swappable(self):
        self.reject(["archival_routes", 2, "box"], 17)
    def test_publisher_index_not_full_paper(self):
        self.reject(["sources", 0, "raw_article_pdf_retrieved"], True)
    def test_hash_not_invented(self):
        self.reject(["sources", 0, "source_payload_sha256"], "0" * 64)
    def test_no_lean_theta_filter(self):
        self.reject(["classification", "physical_constraints_activated"], 1)
    def test_same_2005_and_2006_not_conflated(self):
        self.reject(["sources", 0, "online_date"], "2005-01-01")
    def test_authoritative_museum_cannot_prove_target(self):
        self.reject(["sources", 1, "specific_528_or_conde_case_confirmed"], True)

if __name__ == "__main__":
    unittest.main()
