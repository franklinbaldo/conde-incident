"""CGEO-12: exact planar topology, independence and 1963 exclusion guard."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from tools.conde_ibge_1960_topology import compute, native_topology, validate
from tools.conde_ibge_1960 import load_contract

class CondeIBGE1960TopologyTest(unittest.TestCase):
    def setUp(self):
        self.audit = validate()
        self.ring = load_contract()["native_geometry"]["coordinates_xy_m"][0]

    def test_exact_reconstruction_and_provenance(self):
        self.assertEqual(self.audit, compute())
        self.assertEqual(self.audit["id"], "CGEO-12")
        self.assertEqual(self.audit["source"]["polygon_id"], "CGEO-10")
        self.assertEqual(self.audit["source"]["source_ring_sha256"],
                         load_contract()["native_geometry"]["ring_xy_sha256"])

    def test_46_edges_no_self_intersections(self):
        t = self.audit["calculation"]
        self.assertEqual(t["vertices_with_closure"], 47)
        self.assertEqual(t["edges"], 46)
        self.assertEqual(t["nonadjacent_self_intersections"], 0)
        self.assertEqual(t["ring_orientation_native_xy"], "CLOCKWISE")
        self.assertEqual(t["absolute_native_planar_area_m2"], "983184047.3046875")

    def test_1963_and_geodetic_accuracy_still_unknown(self):
        s = self.audit["scope"]
        for name in ("historic_1963_legal_polygon", "1963_event_position",
                     "1963_point_membership", "1963_position_error_m"):
            self.assertIsNone(s[name])
        self.assertFalse(s["can_restrict_historical_reentry"])
        self.assertFalse(self.audit["source"]["independent_geographical_observation"])
        self.assertIsNone(self.audit["calculation"]["reported_positional_accuracy_m"])
        self.assertTrue(s["cannot_infer_boundary_change_from_area"])

    def test_graph_is_derivation_not_historical_bridge(self):
        edges = self.audit["dependency_graph"]["edges"]
        self.assertEqual({e["kind"] for e in edges},
                         {"COMPUTED_FROM_SAME_PINNED_VERTICES_NOT_NEW_SOURCE",
                          "LIMITS_HISTORICAL_ACCURACY_INTERPRETATION",
                          "NOT_A_VALIDATED_TEMPORAL_BRIDGE"})

    def test_detect_nonclosed_ring(self):
        ring = copy.deepcopy(self.ring)
        ring[-1][0] += 1
        with self.assertRaisesRegex(ValueError, "close"):
            native_topology(ring)

    def test_detect_repeated_vertex(self):
        ring = copy.deepcopy(self.ring)
        ring[4] = ring[3][:]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            native_topology(ring)

    def test_detect_self_intersection_in_source_variant(self):
        ring = [[0, 0], [2, 2], [0, 2], [2, 0], [0, 0]]
        with self.assertRaisesRegex(ValueError, "intersect"):
            native_topology(ring)

    def test_tampered_audit_fails_closed(self):
        tampered = copy.deepcopy(self.audit)
        tampered["scope"]["can_restrict_historical_reentry"] = True
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "fake.json"
            path.write_text(json.dumps(tampered), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "differs"):
                validate(path)

    def test_rejects_nan_geometry(self):
        ring = copy.deepcopy(self.ring)
        ring[2][1] = float("nan")
        with self.assertRaisesRegex(ValueError, "non-finite"):
            native_topology(ring)

if __name__ == "__main__":
    unittest.main()
