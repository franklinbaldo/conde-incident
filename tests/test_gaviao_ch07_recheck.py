import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import gaviao_ch07_recheck as a

def fixture():
    return "\n".join([*a.REQUIRED.values(), *a.SOURCES.values(), *a.REFS, "H-ARQ H-SEG"])

class ReviewTests(unittest.TestCase):
    def test_curated_story_contract(self):
        self.assertEqual([], a.audit(fixture(), pinned=False))

    def test_falsify_old_false_dilemma(self):
        x = fixture() + "\nhipóteses concorrentes H-ARQ e H-SEG"
        self.assertTrue(any("G07-B1" in e for e in a.audit(x, pinned=False)))

    def test_exact_blob_required(self):
        self.assertTrue(any("Git blob" in e for e in a.audit(fixture())))

    def test_eight_possible_worlds(self):
        self.assertEqual(8, len(a.admissible_worlds()))

    def test_local_state_and_external_followup_both_possible(self):
        self.assertTrue(any(w[0] and w[2] for w in a.admissible_worlds()))
        self.assertTrue(any(w[0] and not w[2] for w in a.admissible_worlds()))

    def test_receipt_not_diligence(self):
        self.assertTrue(any(w[1] and not w[2] for w in a.admissible_worlds()))

    def test_followup_without_receipt_in_consulted_corpus_is_possible(self):
        self.assertTrue(any(not w[1] and w[2] for w in a.admissible_worlds()))

    def test_impact_does_not_follow_from_carimbos(self):
        self.assertEqual({False, True}, {w[3] for w in a.admissible_worlds()})

    def test_missing_fbis_source_fails(self):
        self.assertIn("primary image URL missing: FBIS03",
                      a.audit(fixture().replace(a.SOURCES["FBIS03"], ""), pinned=False))

    def test_missing_ax_state_id_fails(self):
        self.assertIn("cumulative ID omitted: AX-STATE-20261111-03",
                      a.audit(fixture().replace("AX-STATE-20261111-03", ""), pinned=False))

    def test_missing_1964_typo_fails(self):
        self.assertIn("required bounded claim missing: old_subject_typo",
                      a.audit(fixture().replace(a.REQUIRED["old_subject_typo"], ""), pinned=False))

    def test_missing_separation_receipt_activity_fails(self):
        self.assertIn("required bounded claim missing: receipt_only",
                      a.audit(fixture().replace(a.REQUIRED["receipt_only"], ""), pinned=False))

    def test_missing_hash_limit_fails(self):
        self.assertIn("required bounded claim missing: unverified_hash",
                      a.audit(fixture().replace(a.REQUIRED["unverified_hash"], ""), pinned=False))

    def test_missing_orbital_limit_fails(self):
        self.assertIn("required bounded claim missing: no_orbital_reduction",
                      a.audit(fixture().replace(a.REQUIRED["no_orbital_reduction"], ""), pinned=False))

if __name__ == "__main__":
    unittest.main()
