"""Adversarial custody tests for 1953 law text hosted in modern official portal."""
import copy
import hashlib
import json
from pathlib import Path
import unittest

from tools.verify_conde_lei628_official import verify_manifest, verify_doc, verify_html

MANIFEST = json.loads((Path(__file__).resolve().parents[1] /
                       "research/archive/conde_lei628_official_1953_20261113.json")
                      .read_text(encoding="utf-8"))


class Official1953TranscriptionTests(unittest.TestCase):
    def test_manifest(self):
        self.assertEqual(verify_manifest(MANIFEST), [])

    def test_no_original_facsimile_or_1963_polygon_claim(self):
        for container, key in (("official_annex_attachment", "attachment_is_1953_printed_facsimile"),
                               ("official_annex_attachment", "internal_creation_date_is_1953_publication_proof"),
                               ("constraint_graph", "1963_legal_polygon_proven"),
                               ("constraint_graph", "orbital_constraint_activated"),
                               ("constraint_graph", "no_intervening_acts_proven"),
                               ("annex_vi_portal_transcription", "full_boundary_perimeter_described")):
            bad = copy.deepcopy(MANIFEST)
            bad[container][key] = True
            self.assertTrue(verify_manifest(bad), key)

    def test_no_third_neighbour_inserted_as_if_in_annex_vi(self):
        bad = copy.deepcopy(MANIFEST)
        bad["annex_vi_portal_transcription"]["neighbours_explicitly_described_in_section"].append("Esplanada")
        self.assertTrue(verify_manifest(bad))

    def test_custody_digest_and_magic_both_required(self):
        raw = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1mock"
        bad = copy.deepcopy(MANIFEST)
        bad["official_annex_attachment"]["bytes"] = len(raw)
        bad["official_annex_attachment"]["sha256"] = hashlib.sha256(raw).hexdigest()
        self.assertEqual(verify_doc(raw, bad), [])
        self.assertTrue(verify_doc(raw[:-1], bad))
        self.assertTrue(verify_doc(b"\0" * 8 + raw[8:], bad))

    def test_portal_section_and_corrupt_phrase_guard(self):
        prefix = "LEI Nº 628 DE 30 DE DEZEMBRO DE 1953 ANEXO VI "
        section = "MUNICÍPIO DE CONDE LIMITES MUNICIPAIS: COM O MUNICÍPIO DE RIO REAL: "
        section += " COM O MUNICÍPIO DE JANDAÍRA: "
        section += " ".join(MANIFEST["annex_vi_portal_transcription"]["landmark_strings"])
        section += " " + MANIFEST["annex_vi_portal_transcription"]["textual_corruption_example"]
        good = ("<body>" + prefix + section + " MUNICÍPIO DE CONDEÚBA</body>").encode()
        self.assertEqual(verify_html(good, MANIFEST), [])
        self.assertTrue(verify_html(good.replace(b"ANEXO VI", b"ANEXO VII"), MANIFEST))
        self.assertTrue(verify_html(good.replace("JANDAÍRA".encode(), b"JABUTI"), MANIFEST))
        self.assertTrue(verify_html(good.replace("CONDEÚBA".encode(), b"CONDEEX"), MANIFEST))


if __name__ == "__main__":
    unittest.main()
