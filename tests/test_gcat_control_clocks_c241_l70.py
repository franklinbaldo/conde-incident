"""Adversarial regression for two historical GCAT clock namespaces."""
from __future__ import annotations

import copy
import hashlib
import json
import unittest

from tools.audit_gcat_control_clocks_c241_l70 import LEDGER, ROOT, audit, day


class GcatControlClocksTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        cls.base = json.loads(
            (ROOT / cls.ledger["snapshot_ledger"]).read_text(encoding="utf-8")
        )

    def mutated(self) -> dict:
        return copy.deepcopy(self.ledger)

    def deny(self, item: dict) -> None:
        with self.assertRaises(ValueError):
            audit(item, self.base)

    def test_valid_snapshot_is_not_a_tracking_epoch(self) -> None:
        result = audit(self.mutated(), self.base)
        self.assertEqual(result["status"], "PASS_SNAPSHOT_ONLY")
        self.assertEqual(result["new_instrumental_measurements"], 0)
        self.assertIsNone(result["objects"]["637"]["terminal_epoch_utc"])
        self.assertIsNone(result["objects"]["668"]["terminal_epoch_utc"])

    def test_payload_mutation_even_with_matching_digest_fails(self) -> None:
        item = self.mutated()
        entry = item["objects"]["637"]["payload"]
        entry["line"] = entry["line"].replace("1963 Sep  1", "1963 Sep  2")
        entry["sha256"] = hashlib.sha256(entry["line"].encode()).hexdigest()
        self.deny(item)

    def test_decay_mutation_even_with_matching_digest_fails(self) -> None:
        item = self.mutated()
        entry = item["objects"]["668"]["object"]
        entry["line"] = entry["line"].replace("1963 Oct 12", "1963 Oct  4")
        entry["sha256"] = hashlib.sha256(entry["line"].encode()).hexdigest()
        self.deny(item)

    def test_forged_observation_and_sigma_are_rejected(self) -> None:
        for field, value in (
            ("terminal_epoch_utc", "1963-10-12T23:59:59Z"),
            ("sensor_id", "invented"),
            ("terminal_uncertainty_seconds", 1),
            ("impact_location", "Conde"),
        ):
            with self.subTest(field=field):
                item = self.mutated()
                item["objects"]["668"][field] = value
                self.deny(item)

    def test_parent_swapped_even_with_digest_fails(self) -> None:
        item = self.mutated()
        entry = item["objects"]["637"]["object"]
        entry["line"] = entry["line"].replace("A00384", "A00391")
        entry["sha256"] = hashlib.sha256(entry["line"].encode()).hexdigest()
        self.deny(item)

    def test_source_family_and_version_are_pinned(self) -> None:
        for field, value in (("payload", "https://example.org/psatcat.tsv"),
                             ("object", "https://example.org/currentcat.tsv")):
            with self.subTest(field=field):
                item = self.mutated()
                item["sources"][field] = value
                self.deny(item)
        item = self.mutated()
        item["snapshot_gcat_version"] = "GCAT 1.8.10"
        self.deny(item)

    def test_no_independent_instrument_or_activation(self) -> None:
        item = self.mutated()
        item["interpretation"]["extra_norad_528_constraints"] = 1
        self.deny(item)
        item = self.mutated()
        item["objects"]["637"]["physical_activation"] = True
        self.deny(item)

    def test_invalid_clock_precision_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            day("1963 Oct 12 00:00Z")

    def test_empty_or_inconsistent_controls_are_rejected(self) -> None:
        item = self.mutated()
        del item["objects"]["637"]
        self.deny(item)
        item = self.mutated()
        item["objects"]["668"]["piece"] = "1963-003B"
        self.deny(item)


if __name__ == "__main__":
    unittest.main()
