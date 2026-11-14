"""CGEO-64 adversarial preregistration tests, including intentional failures."""
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("cgeo64", ROOT / "tools/cgeo64_prereg_validate.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class NarrativePreregTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prereg = module.load_and_verify()

    def reject(self, edit):
        d = copy.deepcopy(self.prereg)
        edit(d)
        with self.assertRaises(ValueError):
            module.validate(d)

    def test_frozen_contract(self):
        self.assertEqual(module.validate(self.prereg), 50)

    def test_exact_frozen_git_blob(self):
        self.assertEqual(module.git_blob_sha(module.DATA.read_bytes()), module.FROZEN_GIT_BLOB)

    def test_extra_posthoc_fragment_rejected(self):
        self.reject(lambda d: d["frozen_fbis_fragments"].append({"id": "F09_AFTER_SEARCH"}))

    def test_removed_negative_fragment_rejected(self):
        self.reject(lambda d: d["frozen_fbis_fragments"].pop())

    def test_source_language_not_rewritten(self):
        self.reject(lambda d: d["source_lineage"].update(literal_portuguese_quote_authenticated=True))

    def test_wrong_week_rejected(self):
        self.reject(lambda d: d["sampling"]["weeks"][1]["dates"].pop())

    def test_post_event_controls_rejected(self):
        self.reject(lambda d: d["sampling"]["weeks"][1].update(role="post_event_sensitivity_only"))

    def test_invented_edition_rejected(self):
        self.reject(lambda d: d["sampling"]["publications"][0].update(issue_number_for_unknown_dates="00401"))

    def test_result_inserted_before_search_rejected(self):
        self.reject(lambda d: d["result_template"]["observations"].append({"found": True}))

    def test_missing_data_cannot_be_zero(self):
        self.reject(lambda d: d["result_template"].update(baseline_rates=0))

    def test_historical_centroid_not_inferred(self):
        self.reject(lambda d: d["causal_scope"].update(historical_center_1963=[-11.8, -37.6]))

    def test_no_orbital_constraint(self):
        self.reject(lambda d: d["causal_scope"].update(active_orbital_constraint=True))

    def test_no_accusation_from_word_overlap(self):
        self.reject(lambda d: d["causal_scope"].update(accusation_of_fraud=True))


if __name__ == "__main__":
    unittest.main()
