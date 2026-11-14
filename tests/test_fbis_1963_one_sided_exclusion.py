"""C241-P50: entirely synthetic veto tests; zero fabricated historical wires."""
import copy
import json
import unittest

from tools import fbis_1963_one_sided_exclusion as p


def fake_item(item_id="SYNTHETIC-01", time="1700", event="JFK_SHOTS"):
    return {
        "item_id": item_id,
        "fbis_source_type": "ORIGINAL_1963_WIRE_FACSIMILE",
        "fbis_facsimile_url": "https://invalid.example/NOT_A_REAL_FBIS_DOC.pdf",
        "fbis_sha256": format(17 + len(item_id), "064x"),
        "fbis_page": 1,
        "fbis_header": (
            f"RIO DE JANEIRO RADIO TUPI IN PORTUGUESE "
            f"{time} 22 NOV 63 W"
        ),
        "fbis_report_quote": (
            "FICTIONAL EXAMPLE FOR UNIT TEST ONLY: " +
            "the selected event has already occurred."
        ),
        "event_id": event,
        "matching_rationale": (
            "Fictional example, never authenticated or used as evidence."
        ),
        "visually_checked": True,
    }


class OneSidedFBISTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(p.MANIFEST.read_text(encoding="utf-8"))

    def manifest_with(self, *rows):
        obj = copy.deepcopy(self.manifest)
        obj["observed_fbis_items"] = list(rows)
        return obj

    def test_true_manifest_keeps_zero_fbis_observations(self):
        out = p.build(self.manifest)
        self.assertEqual(out["observed_fbis_count"], 0)
        self.assertEqual(out["status"], "UNRESOLVED_NO_ITEMS")
        self.assertFalse(out["vetoed_assumptions"])
        self.assertEqual(out["independent_same_broadcast_anchors_p48"], 0)
        self.assertFalse(out["limits"]["header_clock_calibrated"])
        self.assertEqual(out["limits"]["physical_domain_effect"],
                         "THETA_UNCHANGED")

    def test_jfk_shots_at_1830z_veto_hypothetical_1700z_gmt_only(self):
        item = p.build(self.manifest_with(fake_item()))["items"][0]
        self.assertEqual(item["candidate_broadcast_utc"]["GMT"],
                         "1963-11-22T17:00Z")
        self.assertEqual(item["candidate_broadcast_utc"]["RIO_LOCAL"],
                         "1963-11-22T19:00Z")
        self.assertEqual(item["chronologically_excluded"], ["GMT"])
        self.assertEqual(item["not_excluded_not_confirmed"], ["RIO_LOCAL"])

    def test_one_veto_never_selects_a_verified_time_zone(self):
        result = p.build(self.manifest_with(fake_item()))
        self.assertEqual(result["status"], "ONE_SIDED_EXCLUSION_ONLY")
        self.assertFalse(result["limits"]["header_clock_calibrated"])
        self.assertIsNone(result["limits"]["timestamp_of_1963_conde_event"])

    def test_death_requires_confirmation_separate_from_shooting(self):
        item = p.build(self.manifest_with(
            fake_item(event="JFK_PRONOUNCED_DEAD", time="1850")))["items"][0]
        self.assertEqual(item["event_utc"], "1963-11-22T19:00Z")
        self.assertEqual(item["chronologically_excluded"], ["GMT"])

    def test_johnson_oath_has_later_independent_lower_bound(self):
        item = p.build(self.manifest_with(
            fake_item(event="LBJ_OATH", time="1900")))["items"][0]
        self.assertEqual(item["event_utc"], "1963-11-22T20:38Z")
        self.assertEqual(item["chronologically_excluded"], ["GMT"])

    def test_exact_five_minute_safety_margin_does_not_veto(self):
        item = p.build(self.manifest_with(
            fake_item(time="1825")))["items"][0]
        self.assertEqual(item["chronologically_excluded"], [])

    def test_both_branch_times_before_event_require_inconsistency(self):
        result = p.build(self.manifest_with(fake_item(time="1500")))
        self.assertEqual(result["status"],
                         "INCONSISTENT_SOURCE_OR_CLOCK_ASSUMPTIONS")
        self.assertEqual(set(result["vetoed_assumptions"]),
                         {"GMT", "RIO_LOCAL"})
        self.assertFalse(result["non_vetoed_not_confirmed"])

    def test_both_branches_possible_does_not_vote(self):
        result = p.build(self.manifest_with(fake_item(time="2200")))
        self.assertEqual(result["status"], "UNRESOLVED_NO_BRANCH_EXCLUDED")
        self.assertFalse(result["vetoed_assumptions"])

    def test_outside_city_date_and_impossible_hours_rejected(self):
        for heading in (
            "SAO PAULO RADIO TUPI IN PORTUGUESE 1700 22 NOV 63 W",
            "RIO DE JANEIRO RADIO TUPI IN PORTUGUESE 1700 23 NOV 63 W",
            "RIO DE JANEIRO RADIO TUPI IN PORTUGUESE 2461 22 NOV 63 W",
            "RIO DE JANEIRO TV TUPI IN PORTUGUESE 1700 22 NOV 63 W",
            "RIO DE JANEIRO RADIO TUPI IN PORTUGUESE 1700 22 NOV 63",
        ):
            with self.subTest(header=heading):
                row = fake_item()
                row["fbis_header"] = heading
                with self.assertRaises(ValueError):
                    p.build(self.manifest_with(row))

    def test_custody_fields_are_mandatory_even_one_candidate(self):
        for key, bad in (
            ("fbis_sha256", "bad"),
            ("fbis_page", 0),
            ("fbis_page", "1"),
            ("fbis_facsimile_url", "http://invalid.example/x.pdf"),
            ("fbis_report_quote", "short"),
            ("matching_rationale", "weak"),
            ("visually_checked", False),
            ("fbis_source_type", "SECONDARY_REPRINT"),
            ("event_id", "FAKE_EVENT"),
        ):
            with self.subTest(key=key):
                row = fake_item()
                row[key] = bad
                with self.assertRaises(ValueError):
                    p.build(self.manifest_with(row))

    def test_renamed_fbis_occurrence_is_not_a_second_witness(self):
        a, b = fake_item("A"), fake_item("B")
        b["fbis_sha256"] = a["fbis_sha256"]
        with self.assertRaisesRegex(ValueError, "same FBIS occurrence"):
            p.build(self.manifest_with(a, b))

    def test_duplicate_item_id_rejected_even_different_pages(self):
        a, b = fake_item("A"), fake_item("A")
        b["fbis_page"] = 2
        with self.assertRaisesRegex(ValueError, "duplicate item ID"):
            p.build(self.manifest_with(a, b))

    def test_preregistered_events_and_guard_cannot_be_mutated(self):
        modifications = [
            lambda obj: obj["events"][0].update(event_utc="1963-11-22T16:30Z"),
            lambda obj: obj["events"].pop(),
            lambda obj: obj.update(guard_minutes=120),
            lambda obj: obj["events"][1].update(source_url="https://other.example"),
            lambda obj: obj.update(preregistered_date="2026-11-15"),
            lambda obj: obj.update(scope="SAO_PAULO"),
        ]
        for change in modifications:
            with self.subTest(change=repr(change)):
                manifest = self.manifest_with()
                change(manifest)
                with self.assertRaises(ValueError):
                    p.build(manifest)

    def test_artifact_is_replayed_byte_for_byte(self):
        self.assertEqual(p.OUTPUT.read_text(encoding="utf-8"),
                         p.render())

    def test_no_fake_lean_or_orbital_constraint(self):
        for row in (None, fake_item()):
            manifest = self.manifest_with(*([row] if row else []))
            result = p.build(manifest)
            self.assertFalse(result["limits"]["header_clock_calibrated"])
            self.assertEqual(result["limits"]["active_physical_lean_predicates"], 0)
            self.assertEqual(result["limits"]["physical_domain_effect"],
                             "THETA_UNCHANGED")


if __name__ == "__main__":
    unittest.main()
