"""Regression checks for Conde official 1953/2017 legal boundary custody."""
from __future__ import annotations

import copy
from decimal import Decimal
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from conde_legal_boundary import (
    CONTRACT, date_eligibility, read_contract, signed_dms_to_degrees, verify_pdf_file
)


class LegalBoundaryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = read_contract()

    def patched(self, obj):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        file = Path(tmp.name) / "contract.json"
        file.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
        return file

    def test_sources_have_two_distinct_primary_and_compiled_lineages(self):
        self.assertEqual(len(self.c["sources"]), 2)
        self.assertEqual(self.c["sources"][0]["kind"], "OFFICIAL_STATE_STATISTICAL_COMPILATION")
        self.assertEqual(self.c["sources"][1]["kind"], "OFFICIAL_LAW_FACSIMILE")
        self.assertTrue(all(x["occurrence"] for x in self.c["sources"]))

    def test_1963_municipal_boundary_remains_unknown(self):
        e = date_eligibility("1963-11-08", self.c)
        self.assertEqual(e["temporal_status"], "UNRESOLVED_NO_1963_BOUNDARY")
        self.assertIsNone(e["boundary_polygon_for_date"])
        self.assertFalse(e["can_constrain_reentry_1963"])

    def test_2017_legal_text_is_not_usable_GIS_polygon(self):
        for d in ("2017-04-27", "2017-04-28", "2025-01-01"):
            e = date_eligibility(d, self.c)
            self.assertIsNone(e["coordinates_datum"])
            self.assertFalse(e["can_constrain_reentry_1963"])
            self.assertIsNone(e["boundary_polygon_for_date"])
        self.assertEqual(date_eligibility("2017-04-27", self.c)["temporal_status"],
                         "LATER_STATUTE_NOT_APPLICABLE")

    def test_literal_dms_conversion_does_not_provide_datum(self):
        x = self.c["legal_2017"]["vertices"][0]
        self.assertEqual(signed_dms_to_degrees(x["latitude_dms"], 90),
                         -(Decimal(11) + Decimal(39) / 60 + Decimal("45.89") / 3600))
        self.assertIsNone(self.c["legal_2017"]["coordinate_reference_system"])

    def test_out_of_bounds_dms_rejected(self):
        for s in ("-11° 60' 00,00\"", "-11° 00' 60,00\"", "-11 00 00", "-91° 00' 00,00\""):
            with self.assertRaises(ValueError):
                signed_dms_to_degrees(s, 90)

    def test_endpoint_chain_exactly_preserved(self):
        legs = self.c["legal_2017"]["legs"]
        self.assertEqual([x["adjacent_unit"] for x in legs],
                         ["Jandaíra", "Oceano Atlântico", "Esplanada", "Rio Real"])
        for i in range(4):
            self.assertEqual(legs[i]["to"], legs[(i+1) % 4]["from"])
            self.assertTrue(legs[i]["intermediate_controls_omitted"])

    def test_altered_legal_coords_not_accepted(self):
        bad = copy.deepcopy(self.c)
        bad["legal_2017"]["vertices"][0]["longitude_dms"] = "-37° 44' 50,26\""
        with self.assertRaisesRegex(ValueError, "alteration"):
            read_contract(self.patched(bad))

    def test_1963_fake_polygon_fails_closed(self):
        bad = copy.deepcopy(self.c)
        bad["historical_1953_reference"]["valid_geometry_on_1963_11_08"] = []
        with self.assertRaisesRegex(ValueError, "unproven"):
            read_contract(self.patched(bad))
        bad = copy.deepcopy(self.c)
        bad["constraint_graph"]["can_constrain_reentry_1963"] = True
        with self.assertRaisesRegex(ValueError, "cannot constrain"):
            read_contract(self.patched(bad))

    def test_fake_epsg_or_fabricated_accuracy_rejected(self):
        for key,val in [("coordinate_reference_system","EPSG:4674"),
                        ("published_positional_accuracy_m",1.0)]:
            bad = copy.deepcopy(self.c)
            bad["legal_2017"][key] = val
            with self.assertRaisesRegex(ValueError, "null"):
                read_contract(self.patched(bad))

    def test_source_hash_and_id_validation(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "fake.pdf"
            p.write_bytes(b"%PDF-1.5 fake")
            with self.assertRaisesRegex(ValueError, "checksum"):
                verify_pdf_file(self.c, self.c["sources"][1]["id"], p)
            with self.assertRaisesRegex(ValueError, "unknown source ID"):
                verify_pdf_file(self.c, "OTHER_SOURCE", p)

    def test_2017_fabricated_complete_boundary_rejected(self):
        bad = copy.deepcopy(self.c)
        bad["legal_2017"]["complete_described_boundary_reconstructed"] = True
        with self.assertRaisesRegex(ValueError, "not a verified"):
            read_contract(self.patched(bad))


if __name__ == "__main__":
    unittest.main()
