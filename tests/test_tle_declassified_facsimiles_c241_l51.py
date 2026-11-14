"""Negative controls for documentary custody without physical claims."""
import copy
import importlib.util
import json
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("turtle_l51", ROOT / "tools/tle_declassified_facsimiles_c241_l51.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class Tests(unittest.TestCase):
    def setUp(self):
        self.data = mod.load()

    def mutation(self, target):
        trial = copy.deepcopy(self.data)
        target(trial)
        with self.assertRaises(ValueError):
            mod.audit(trial)

    def test_current_manifest(self):
        self.assertTrue(mod.audit(self.data))

    def test_wrong_nsa_variant(self):
        self.mutation(lambda x: x["documents"][0]["readout"].update(launch_vehicle="Thor-Agena B"))

    def test_wrong_nsa_page(self):
        self.mutation(lambda x: x["documents"][0].update(pdf_page_1_based=12))

    def test_wrong_nro_claim(self):
        self.mutation(lambda x: x["documents"][1]["readout"].update(launch_vehicle_wording="Agena D"))

    def test_wrong_sha(self):
        self.mutation(lambda x: x["documents"][1].update(sha256="0" * 64))

    def test_false_instrument_station(self):
        self.mutation(lambda x: x["norad528"].update(station="Cold Lake"))

    def test_false_breakup_date(self):
        self.mutation(lambda x: x["norad528"].update(decay_hour="1963-11-08T12:00Z"))

    def test_false_hardware_identity(self):
        self.mutation(lambda x: x["norad528"].update(hardware_identity="Agena D stage"))

    def test_premature_constraint(self):
        self.mutation(lambda x: x.update(physical_constraint_active=True))

    def test_false_independence(self):
        self.mutation(lambda x: x["conflict"].update(same_observation_family_claim=True))

    def test_premature_stage_resolution(self):
        self.mutation(lambda x: x["conflict"].update(result="AGENA_D_PROVEN"))

    def test_extra_document(self):
        self.mutation(lambda x: x["documents"].append(copy.deepcopy(x["documents"][0])))

    def test_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "duplicate.json"
            raw = (ROOT / "research/tle_custody/declassified_facsimiles_C241-L51.json").read_text("utf-8")
            p.write_text(raw.replace('"physical_constraint_active": false,',
                           '"physical_constraint_active": false, "physical_constraint_active": true,'), "utf-8")
            with self.assertRaises(ValueError):
                mod.load(p)

    def test_reject_fake_pdf_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / mod.EXPECTED[0]["filename"]
            p.write_bytes(b"%PDF-1.7\n%%EOF")
            with self.assertRaises(ValueError):
                mod.verify_file(mod.EXPECTED[0], p)

    def test_reject_truncated_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / mod.EXPECTED[0]["filename"]
            p.write_bytes(b"%PDF-1.7\n" + b"\x00" * 4096)
            with self.assertRaises(ValueError):
                mod.verify_file(mod.EXPECTED[0], p)


if __name__ == "__main__":
    unittest.main()
