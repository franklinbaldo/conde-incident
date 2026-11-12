import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import gaviao_chapter07_audit as a

LEDGER = json.loads((Path(__file__).resolve().parents[1] / "research" / "gaviao_chapter07_ledger.json").read_text(encoding="utf-8"))

def fixture():
    lines = ['chapter: "07"', "**“on November 8, 1964”**",
             "hipóteses concorrentes H-ARQ e H-SEG podem ter produzido registros próprios"]
    lines += list(a.GUARDS)
    lines += [s["url"] for s in LEDGER["sources"]]
    lines += [c["anchor"] for c in LEDGER["claims"]]
    return "\n".join(lines)

class AdversarialTests(unittest.TestCase):
    def setUp(self):
        self.d = copy.deepcopy(LEDGER)
        self.s = fixture()

    def errors(self):
        return a.check(self.s, self.d, verify_blob=False)

    def test_curated_consistency(self):
        self.assertEqual([], self.errors())

    def test_audit_finds_hypothesis_nonexclusivity(self):
        self.assertEqual(["false-exclusive-H-ARQ-H-SEG"], a.critical_findings(self.s))

    def test_edit_requires_new_review(self):
        self.s = self.s.replace("hipóteses concorrentes", "eixos distintos")
        self.assertIn("editorial finding drift", " ".join(self.errors()))

    def test_missing_source_url(self):
        self.s = self.s.replace(self.d["sources"][0]["url"], "")
        self.assertIn("source URL missing", " ".join(self.errors()))

    def test_pretend_independent_documents(self):
        self.d["sources"][1]["chain"] = "independent-claim"
        self.assertIn("falsely split", " ".join(self.errors()))

    def test_chapter_1964_typo_preserved(self):
        self.s = self.s.replace("**“on November 8, 1964”**", "")
        self.assertIn("1964 subject", " ".join(self.errors()))

    def test_missing_non_implication_about_nasa(self):
        self.s = self.s.replace(a.GUARDS[0], "")
        self.assertIn("epistemic guard", " ".join(self.errors()))

    def test_missing_orbital_limit(self):
        self.s = self.s.replace(a.GUARDS[3], "")
        self.assertIn("epistemic guard", " ".join(self.errors()))

    def test_fake_impact_evidence(self):
        self.d["sources"][2]["physical_observation"] = True
        self.assertIn("physical observation", " ".join(self.errors()))

    def test_missing_matrix_id(self):
        self.d["claims"][0]["occurrences"] = []
        self.assertIn("matrix occurrence", " ".join(self.errors()))

    def test_invalid_epistemic_class(self):
        self.d["claims"][0]["classification"] = "proven-impact"
        self.assertIn("invalid epistemic", " ".join(self.errors()))

    def test_false_government_hash_verification(self):
        self.d["source_status"] = "identical to federal originals"
        self.assertIn("not established", " ".join(self.errors()))

    def test_blob_pin_detects_synthetic_changes(self):
        self.assertIn("pinned Git blob differs", a.check(self.s, self.d))

if __name__ == "__main__":
    unittest.main()
