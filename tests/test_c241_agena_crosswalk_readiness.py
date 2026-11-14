"""Counterexamples for provenance, wet/dry epoch and object mapping."""
import copy
import unittest

from tools.c241_agena_crosswalk_readiness import (
    SOURCE, audit, qualified_mass_record,
)


def direct():
    return {
        "measurement_basis": "direct_mass",
        "catalog_object": "528",
        "catalog_identity_verified": True,
        "mass_kg": 12.0,
        "uncertainty_kg": 0.5,
        "mass_convention": "as_observed",
        "epoch_utc": "1963-11-01T00:00:00Z",
        "document_sha256": "a" * 64,
        "calibration_reference": "synthetic-calibration",
        "source_family": "synthetic-direct",
    }


def component():
    row = direct()
    row.update({
        "measurement_basis": "component_mass",
        "component": "part-X",
        "mass_convention": "dry",
    })
    row.pop("catalog_object")
    row.pop("catalog_identity_verified")
    link = {
        "catalog_object": "528",
        "component": "part-X",
        "launch": "1963-003",
        "epoch_utc": row["epoch_utc"],
        "document_sha256": "b" * 64,
        "physical_continuity_verified": True,
        "flight_specific": True,
    }
    return row, link


class HardwareCrosswalkReadiness(unittest.TestCase):
    def test_catalog_has_no_active_mass_row(self):
        result = audit()
        self.assertEqual(result["source_claim_count"], 4)
        self.assertEqual(result["historical_target_rank_gain"], 0)
        self.assertEqual(result["independent_528_mass_observations"], 0)
        self.assertFalse(result["historical_constraint_active"])
        self.assertIsNone(result["historical_mass_posterior"])
        self.assertFalse(result["domain_reduction"])
        self.assertEqual(result["historical_mcmc"], "NOT_RUN")

    def test_conflict_is_nomenclature_not_component_id(self):
        r = audit()
        self.assertIn("Thor-Agena D", r["launch_vehicle_labels"])
        self.assertIn("Thor Agena B", r["launch_vehicle_labels"])
        self.assertEqual(r["upper_stage_labels"], ["Agena B"])
        self.assertTrue(r["labels_not_same_semantic_scope"])
        self.assertEqual(r["engineering_to_catalog_crosswalk"], "MISSING")

    def test_qualified_direct_mass_is_only_synthetic_candidate(self):
        self.assertTrue(qualified_mass_record(direct()))
        self.assertFalse(audit()["historical_constraint_active"])

    def test_direct_mass_fails_without_identity_epoch_or_calibration(self):
        for patch in (
            {"catalog_object": "527"},
            {"catalog_identity_verified": False},
            {"epoch_utc": "1963-11-01"},
            {"epoch_utc": "1963-11-01T00:00:00-04:00"},
            {"calibration_reference": ""},
            {"document_sha256": "0" * 64},
            {"uncertainty_kg": 0},
            {"uncertainty_kg": float("nan")},
            {"mass_kg": -1},
            {"mass_convention": "dry"},
            {"measurement_basis": "proxy_Bstar"},
        ):
            with self.subTest(patch=patch):
                row = {**direct(), **patch}
                self.assertFalse(qualified_mass_record(row))

    def test_component_requires_exact_link_and_mass_continuity(self):
        m, link = component()
        self.assertFalse(qualified_mass_record(m))
        self.assertTrue(qualified_mass_record(m, link))
        for patch in (
            {"catalog_object": "529"},
            {"component": "part-Y"},
            {"launch": "1963-035"},
            {"epoch_utc": "1963-11-02T00:00:00Z"},
            {"physical_continuity_verified": False},
            {"flight_specific": False},
            {"document_sha256": None},
        ):
            with self.subTest(patch=patch):
                self.assertFalse(qualified_mass_record(m, {**link, **patch}))

    def test_catalog_promotions_rejected(self):
        import json
        original = json.loads(SOURCE.read_text(encoding="utf-8"))
        for edit in ("historical_mass_constraint_active", "domain_reduction"):
            d = copy.deepcopy(original)
            d[edit] = True
            with self.assertRaises(ValueError):
                audit(d)
        d = copy.deepcopy(original)
        d["claims"][0]["independent_mass_measurement"] = True
        with self.assertRaises(ValueError):
            audit(d)
        d = copy.deepcopy(original)
        d["mass_528_measurement"] = {"mass_kg": 12}
        with self.assertRaises(ValueError):
            audit(d)
        d = copy.deepcopy(original)
        d["claims"].append(d["claims"][0])
        with self.assertRaises(ValueError):
            audit(d)

    def test_result_is_reproducible_without_posterior(self):
        self.assertEqual(audit(), audit())


if __name__ == "__main__":
    unittest.main()
