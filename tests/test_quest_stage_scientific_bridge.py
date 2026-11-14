"""Adversarial contract checks for C241-L50 label versus physical identity."""
import copy
import json
import pathlib
import shutil
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import export_quest_stage_scientific_bridge as b


class TestStageIdentityBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = b.sources()

    def test_byte_reproducibility_and_inactive_domain(self):
        raw = b.render()
        self.assertEqual(raw, b.OUT.read_bytes())
        record = json.loads(raw)
        self.assertEqual(record["source_occurrences"], ["C241-L50", "C241-L15", "C241-L48", "C241-L40"])
        self.assertEqual(record["related_matrix_occurrence"], "C197#1")
        self.assertEqual(len(record["dependency_graph"]), 14)
        self.assertEqual(len(record["simulator_latent_parameters"]), 8)
        self.assertEqual(record["physical_domain_effect"], "THETA_UNCHANGED")
        self.assertFalse(record["activation"])
        self.assertEqual(record["new_528_instrumental_observations"], 0)
        for edge in record["dependency_graph"]:
            self.assertFalse(edge["independent_instrumental_observation"])
            self.assertFalse(edge["activation"])
        for latent in record["simulator_latent_parameters"]:
            self.assertIsNone(latent["value"])
            self.assertFalse(latent["activation"])

    def reject(self, source, change):
        changed = copy.deepcopy(self.inputs)
        change(changed[source])
        with self.assertRaises(ValueError):
            b.build(changed)

    def test_label_conflicts_are_preserved(self):
        self.reject(b.Q, lambda d: d["rows"][1].update(stage="Thor Agena B"))
        self.reject(b.N, lambda d: d["annual_row_extracted_text"].update(vehicle_printed="Thor Agena B"))
        self.reject(b.G, lambda d: d["rows"]["A00324"].update(name="Agena D 2313"))

    def test_group_label_cannot_become_528_hardware(self):
        self.reject(b.N, lambda d: d["annual_row_extracted_text"].update(child_piece_identifier="1963-003B"))
        self.reject(b.N, lambda d: d["inference_guard"].update(physical_identity_528="D"))
        self.reject(b.R, lambda d: d["identity"].update(debris_identity_verified_by_nro_history=True))
        self.reject(b.Q, lambda d: d["norad528"].update(object_hardware="Agena D"))

    def test_catalogue_is_not_instrumental_measurement(self):
        self.reject(b.R, lambda d: d["source"].update(pdf_sha256="0" * 64))
        self.reject(b.R, lambda d: d["mission"].update(orbit_decay_timestamp_utc="1963-11-08T12:00Z"))
        self.reject(b.G, lambda d: d["rows"]["S00528"].update(mass_kg=0))
        self.reject(b.Q, lambda d: d["norad528"].update(observation_utc="1963-11-08T01:00Z"))

    def test_source_bytes_are_pinned_not_just_json_semantics(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            for rel in b.PINS:
                dest = root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, dest)
            self.assertEqual(b.render(root), b.render())
            with (root / b.N).open("ab") as handle:
                handle.write(b"\n")
            with self.assertRaisesRegex(ValueError, "source hash drift"):
                b.render(root)

    def test_duplicate_json_source_key_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate key"):
            json.loads('{"schema":"good","schema":"forged"}', object_pairs_hook=b.unique_keys)


if __name__ == "__main__":
    unittest.main()

