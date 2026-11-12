"""Adversarial fixtures: editorial cross-branch claims are not orbital evidence."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import gaviao_ch08_crossbranch as a

def fixture():
    old = "\n".join(a.OLD_ASSERTIONS)
    new = "Resultado: indeterminado. Documentary overview, not a verdict"
    story = "\n".join((
        *a.STORY_GUARDS, a.NASA, a.FBIS,
        a.BEFORE[0], a.AFTER[0], "NOTED - NO ACTION",
    ))
    return story, old, new

class Chapter08AuditTests(unittest.TestCase):
    def test_curated_contract(self):
        self.assertEqual([], a.audit(*fixture()))

    def test_old_verdict_must_be_verifiable(self):
        s, o, n = fixture()
        self.assertTrue(any("historical before-quote" in e for e in
                            a.audit(s, o.replace("Boato Fabricado", ""), n)))

    def test_new_code_must_abandon_probability(self):
        s, o, n = fixture()
        self.assertTrue(any("obsolete assertion" in e for e in a.audit(s, o, n + " ~0,0062%")))

    def test_new_code_must_abandon_false_verdict(self):
        s, o, n = fixture()
        self.assertTrue(any("obsolete assertion" in e for e in a.audit(s, o, n + " Boato Fabricado")))

    def test_new_summary_requires_indeterminate(self):
        s, o, n = fixture()
        self.assertTrue(any("indeterminado" in e for e in a.audit(s, o, n.replace("indeterminado", "comprovado"))))

    def test_missing_nasa_primary_reference(self):
        s, o, n = fixture()
        self.assertTrue(any("NASA image page" in e for e in a.audit(s.replace(a.NASA, ""), o, n)))

    def test_missing_fbis_primary_reference(self):
        s, o, n = fixture()
        self.assertTrue(any("FBIS image" in e for e in a.audit(s.replace(a.FBIS, ""), o, n)))

    def test_missing_old_pinned_sha(self):
        s, o, n = fixture()
        self.assertTrue(any("old source permalink" in e for e in a.audit(s.replace(a.BEFORE[0], ""), o, n)))

    def test_missing_new_pinned_sha(self):
        s, o, n = fixture()
        self.assertTrue(any("new source permalink" in e for e in a.audit(s.replace(a.AFTER[0], ""), o, n)))

    def test_draft_cannot_be_reported_as_publication(self):
        s, o, n = fixture()
        self.assertTrue(any("publicado" in e for e in
                            a.audit(s.replace("não foi demonstrado como publicado", ""), o, n)))

    def test_mirror_cannot_imply_end_of_tracking(self):
        s, o, n = fixture()
        self.assertTrue(any("rastreamento" in e for e in
                            a.audit(s.replace("não prova que o rastreamento cessou historicamente", ""), o, n)))

    def test_uncompiled_lean_is_not_proof(self):
        s, o, n = fixture()
        self.assertTrue(any("Lean 4.35.0" in e for e in
                            a.audit(s.replace("não uma prova nova em Lean 4.35.0", ""), o, n)))

    def test_false_physical_claim_rejected(self):
        s, o, n = fixture()
        self.assertTrue(any("unverified positive claim" in e for e in
                            a.audit(s + "\nNASA comprovou impacto", o, n)))

    def test_english_nonverdict_required(self):
        s, o, n = fixture()
        self.assertTrue(any("English" in e for e in
                            a.audit(s, o, n.replace("not a verdict", "confirmed"))))

    def test_blob_verification_fails_on_different_bytes(self):
        self.assertTrue(any("pinned Git blob mismatch" in e for e in a.audit(*fixture(), check_blobs=True)))

    def test_four_countermodels(self):
        worlds = a.possibilities()
        self.assertEqual(4, len(worlds))
        self.assertEqual({False, True}, {w[2] for w in worlds})
        self.assertEqual({False, True}, {w[3] for w in worlds})

    def test_independent_axes_not_radar(self):
        worlds = a.possibilities()
        self.assertIn((True, True, False, True), worlds)
        self.assertIn((True, True, True, False), worlds)

if __name__ == "__main__":
    unittest.main()
