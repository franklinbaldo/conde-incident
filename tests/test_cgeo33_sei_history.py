"""Adversarial tests: geospatial and temporal overclaims must fail."""
import copy
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from tools.cgeo33_sei_history import SOURCE,PARENTS,read,verify,verify_pdf


class CGEO33Tests(unittest.TestCase):
    def setUp(self):
        self.d=read(SOURCE)
        self.parents=[read(p) for p in PARENTS]

    def mutate(self, f):
        d=copy.deepcopy(self.d)
        f(d)
        with self.assertRaises(ValueError):
            verify(d,self.parents)

    def test_real_source_and_existing_parents(self):
        self.assertEqual(verify(self.d,self.parents),"CGEO33_REAL_PDF_PROVENANCE_CONTRACT_PASS")

    def test_fabricated_prior_to_1963_publication(self):
        self.mutate(lambda d:d["source"].update(year=1963))
        self.mutate(lambda d:d["source"].update(source_type="OBSERVATION_1963"))

    def test_visual_not_performed(self):
        self.mutate(lambda d:d["source"].update(visual_pages_rendered=True))

    def test_pdf_hash_and_size_mutations(self):
        self.mutate(lambda d:d["source"].update(pdf_sha256="0"*64))
        self.mutate(lambda d:d["source"].update(pdf_bytes=1))

    def test_unknown_250k_coverage(self):
        self.mutate(lambda d:d["archival_claims"][0].update(conde_sheet_identified="Esplanada"))
        self.mutate(lambda d:d["interpretive_limits"].update(ica_pre1963_250k_sheet_covers_conde=True))

    def test_fabricated_cartographic_editions(self):
        self.mutate(lambda d:d["archival_claims"][1].update(esplanada_edition_before_november_1963_confirmed=True))
        self.mutate(lambda d:d["archival_claims"][1].update(multiple_agencies_and_editions=False))

    def test_invalid_1998_to_1961_retroprojection(self):
        self.mutate(lambda d:d["archival_claims"][2].update(second_mapping_partial_sheets=False))
        self.mutate(lambda d:d["interpretive_limits"].update(post1998_partial_sheet_proves_1961_footprint=True))
        self.mutate(lambda d:d["archival_claims"][2].update(actual_1961_photo_footprint="FULL_MI1850"))

    def test_unproven_petrobras_53d_identity(self):
        self.mutate(lambda d:d["archival_claims"][2].update(project_53d_same_program_confirmed=True))
        self.mutate(lambda d:d["interpretive_limits"].update(project_53d_identified_with_regional_petrobras_program=True))

    def test_fabricated_orbital_and_city_centroid(self):
        self.mutate(lambda d:d["interpretive_limits"].update(historical_center_1963=[-37.6,-11.8]))
        self.mutate(lambda d:d["interpretive_limits"].update(can_constrain_orbital_reentry=True))

    def test_parent_or_dependency_missing(self):
        with self.assertRaises(ValueError):
            verify(self.d,self.parents[:-1])
        self.mutate(lambda d:d["dependencies"].pop())

    def test_fake_pdf_replay_fails(self):
        with TemporaryDirectory() as t:
            p=Path(t)/"fake.pdf"
            p.write_bytes(b"%PDF-1.7\n")
            with self.assertRaises(ValueError):
                verify_pdf(p,self.d)


if __name__ == "__main__":
    unittest.main()
