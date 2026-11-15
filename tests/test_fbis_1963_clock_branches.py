"""C241-P48: hostile clock-branch and provenance tests; synthetic anchors are never facts."""
import copy
import json
import unittest
from datetime import datetime

from tools import fbis_1963_clock_branches as f


def synthetic_anchor(index, utc="1963-11-08T23:30Z"):
    """Only a negative/algorithm test fixture; NOT an observed broadcast."""
    return {
        "item_id": "SYNTHETIC-" + str(index),
        "fbis_document_url": "https://invalid.example/fbis-" + str(index),
        "fbis_sha256": format(index + 10, "064x"),
        "fbis_page": str(index + 1),
        "independent_source_url": "https://invalid.example/radio-" + str(index),
        "independent_source_sha256": format(index + 2000, "064x"),
        "independent_page": "1",
        "fbis_heading_verbatim": (
            f"RIO DE JANEIRO RADIO SYNTHETIC{index} IN PORTUGUESE "
            "2330 8 NOV 63 W"
        ),
        "header_local_text": "2330 8 NOV 63",
        "external_broadcast_utc": utc,
        "independence_rationale": (
            "Synthetic adversarial proof fixture, no external evidence."
        ),
    }


class FBISClockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(f.MANIFEST.read_text(encoding="utf-8"))
        cls.report = f.build(cls.manifest)

    def test_manifest_contains_zero_independent_calibrators(self):
        self.assertEqual(f.anchors_from_manifest(self.manifest), [])
        self.assertEqual(self.report["verification_status"], "UNRESOLVED")
        self.assertEqual(self.report["anchor_rule"]["decision"]["qualifying_anchors"], 0)

    def test_1963_summer_time_converts_gmt_branch(self):
        gmt = self.report["conditional_branches"]["GMT"]
        self.assertEqual(gmt["broadcast_utc_if_assumption_holds"],
                         "1963-11-08T23:30Z")
        self.assertEqual(gmt["broadcast_bahia_civil_if_assumption_holds"],
                         "1963-11-08T20:30")
        self.assertEqual(gmt["plane_crossing_nominal_minutes_after_broadcast"], 14)

    def test_guanabara_dst_is_not_bahia_time(self):
        rio = self.report["conditional_branches"]["RIO_LOCAL"]
        self.assertEqual(rio["broadcast_utc_if_assumption_holds"],
                         "1963-11-09T01:30Z")
        self.assertEqual(rio["broadcast_bahia_civil_if_assumption_holds"],
                         "1963-11-08T22:30")
        self.assertEqual(rio["plane_crossing_nominal_minutes_after_broadcast"], -106)
        self.assertEqual(self.report["civil_time_basis"]
                         ["guanabara_utc_offset_on_1963_11_08_minutes"], -120)
        self.assertEqual(self.report["civil_time_basis"]
                         ["bahia_utc_offset_on_1963_11_08_minutes"], -180)

    def test_no_orbital_exclusion_for_either_clock_branch(self):
        self.assertEqual(self.report["limits"]["physical_domain_effect"],
                         "THETA_UNCHANGED")
        self.assertEqual(self.report["limits"]["active_physical_lean_predicates"], 0)
        for branch in self.report["conditional_branches"].values():
            self.assertFalse(branch["orbit_exclusion_licensed"])

    def test_unknown_branch_has_no_fake_upper_bound(self):
        other = self.report["conditional_branches"]["OTHER_UNVERIFIED"]
        self.assertIsNone(other["broadcast_utc_if_assumption_holds"])
        self.assertIsNone(other["reported_event_latest_possible_utc_if_report_precedes_broadcast"])

    def test_footer_does_not_become_a_time(self):
        source = self.report["source"]
        self.assertEqual(source["fbis_footer_verbatim_unparsed"], f.FOOTER)
        self.assertIsNone(source["footer_clock_meaning"])
        self.assertIsNone(source["reported_phenomenon_time"])
        self.assertFalse(source["header_timezone_verified"])

    def test_broadcast_stamp_is_not_event_epoch(self):
        self.assertEqual(f.stamp_from_header(),
                         datetime(1963, 11, 8, 23, 30))
        with self.assertRaises(ValueError):
            f.stamp_from_header(f.HEADER.replace("2330", "2450"))
        with self.assertRaises(ValueError):
            f.stamp_from_header(f.HEADER.replace("8 NOV 63", "9 NOV 63 END"))

    def test_nine_synthetic_anchors_do_not_select_a_clock(self):
        anchors = [synthetic_anchor(i) for i in range(9)]
        self.assertEqual(f.qualification(f.anchors_from_manifest(
            {"schema": "conde.fbis-clock-anchors/v1",
             "independent_anchors": anchors}))["status"], "UNRESOLVED")

    def test_ten_synthetic_gmt_anchors_prove_algorithm_only(self):
        anchors = [synthetic_anchor(i) for i in range(10)]
        decision = f.qualification(f.anchors_from_manifest(
            {"schema": "conde.fbis-clock-anchors/v1",
             "independent_anchors": anchors}))
        self.assertEqual(decision["status"], "GMT")
        self.assertEqual(decision["votes"]["GMT"], 10)
        # This is a fixture and never part of the real manifest/output.

    def test_ten_synthetic_rio_anchors_prove_second_branch_only(self):
        anchors = [synthetic_anchor(i, "1963-11-09T01:30Z")
                   for i in range(10)]
        self.assertEqual(f.qualification(anchors)["status"], "RIO_LOCAL")

    def test_mixed_synthetic_anchors_stay_unresolved(self):
        anchors = [synthetic_anchor(i) for i in range(10)]
        anchors[9]["external_broadcast_utc"] = "1963-11-09T01:30Z"
        self.assertEqual(f.qualification(anchors)["status"], "UNRESOLVED")

    def test_invalid_anchors_are_rejected(self):
        good = synthetic_anchor(0)
        variants = []
        same_source = copy.deepcopy(good)
        same_source["independent_source_sha256"] = good["fbis_sha256"]
        variants.append([same_source])
        same_url = copy.deepcopy(good)
        same_url["independent_source_url"] = good["fbis_document_url"]
        variants.append([same_url])
        short_reason = copy.deepcopy(good)
        short_reason["independence_rationale"] = "same broadcast"
        variants.append([short_reason])
        variants.append([good, copy.deepcopy(good)])
        variants.append([{"item_id": "fabricated"}])
        for rows in variants:
            with self.subTest(rows=rows):
                with self.assertRaises(ValueError):
                    f.anchors_from_manifest({
                        "schema": "conde.fbis-clock-anchors/v1",
                        "independent_anchors": rows,
                    })

    def test_malformed_single_anchor_rejected_below_quorum(self):
        variants = [
            ("header_local_text", "2561 8 NOV 63"),
            ("header_local_text", "2330 31 NOV 63"),
            ("external_broadcast_utc", "1963-11-35T23:30Z"),
            ("external_broadcast_utc", "1963-12-02T01:30Z"),
        ]
        for key, bad in variants:
            with self.subTest(key=key, bad=bad):
                row = synthetic_anchor(0)
                row[key] = bad
                with self.assertRaises(ValueError):
                    f.qualification([row])
                with self.assertRaises(ValueError):
                    f.anchors_from_manifest({
                        "schema": "conde.fbis-clock-anchors/v1",
                        "independent_anchors": [row],
                    })

    def test_duplicate_fbis_occurrence_cannot_be_rebranded_as_second_item(self):
        a = synthetic_anchor(0)
        b = synthetic_anchor(1)
        b["fbis_sha256"] = a["fbis_sha256"]
        b["fbis_page"] = a["fbis_page"]
        b["header_local_text"] = a["header_local_text"]
        with self.assertRaisesRegex(ValueError, "duplicate FBIS occurrence"):
            f.anchors_from_manifest({
                "schema": "conde.fbis-clock-anchors/v1",
                "independent_anchors": [a, b],
            })

    def test_november_30_rio_header_may_have_december_1_utc_anchor(self):
        rows = [synthetic_anchor(i, "1963-12-01T01:30Z")
                for i in range(10)]
        for row in rows:
            row["header_local_text"] = "2330 30 NOV 63"
            row["fbis_heading_verbatim"] = (
                row["fbis_heading_verbatim"].replace("2330 8 NOV 63",
                                                    "2330 30 NOV 63")
            )
        self.assertEqual(f.qualification(rows)["status"], "RIO_LOCAL")
        # All examples are synthetic. This is a boundary-of-calendar test only.

    def test_independent_source_cannot_be_another_fbis_facsimile(self):
        a, b = synthetic_anchor(0), synthetic_anchor(1)
        b["independent_source_sha256"] = a["fbis_sha256"]
        b["independent_source_url"] = a["fbis_document_url"]
        with self.assertRaisesRegex(ValueError, "other FBIS"):
            f.anchors_from_manifest({
                "schema": "conde.fbis-clock-anchors/v1",
                "independent_anchors": [a, b],
            })

    def test_syndicated_same_broadcast_cannot_make_two_independent_votes(self):
        # Two separate scans/hashes/pages, but the same station and time.
        a, b = synthetic_anchor(0), synthetic_anchor(1)
        b["fbis_heading_verbatim"] = a["fbis_heading_verbatim"]
        with self.assertRaisesRegex(ValueError, "same broadcast reissued"):
            f.anchors_from_manifest({
                "schema": "conde.fbis-clock-anchors/v1",
                "independent_anchors": [a, b],
            })

    def test_ten_reprints_of_one_broadcast_cannot_form_gmt_quorum(self):
        rows = [synthetic_anchor(i) for i in range(10)]
        for row in rows:
            row["fbis_heading_verbatim"] = rows[0]["fbis_heading_verbatim"]
        with self.assertRaisesRegex(ValueError, "same broadcast reissued"):
            f.anchors_from_manifest({
                "schema": "conde.fbis-clock-anchors/v1",
                "independent_anchors": rows,
            })

    def test_clock_must_match_verbatim_heading_not_a_second_guess(self):
        bad = synthetic_anchor(0)
        bad["header_local_text"] = "2331 8 NOV 63"
        with self.assertRaisesRegex(ValueError, "differs"):
            f.anchors_from_manifest({
                "schema": "conde.fbis-clock-anchors/v1",
                "independent_anchors": [bad],
            })

    def test_wrong_city_or_missing_original_heading_rejected(self):
        for heading in (
            "SAO PAULO RADIO TEST IN PORTUGUESE 2330 8 NOV 63 W",
            "RIO DE JANEIRO RADIO TEST IN PORTUGUESE 2330 8 NOV 63",
            "",
        ):
            bad = synthetic_anchor(0)
            bad["fbis_heading_verbatim"] = heading
            with self.subTest(heading=heading):
                with self.assertRaises(ValueError):
                    f.anchors_from_manifest({
                        "schema": "conde.fbis-clock-anchors/v1",
                        "independent_anchors": [bad],
                    })

    def test_page_numbers_are_positive_printed_page_indices(self):
        for key in ("fbis_page", "independent_page"):
            for wrong in ("0", "-1", "not-a-page", "1.0", " 1"):
                with self.subTest(field=key, value=wrong):
                    a = synthetic_anchor(0)
                    a[key] = wrong
                    with self.assertRaisesRegex(ValueError, "positive page"):
                        f.anchors_from_manifest({
                            "schema": "conde.fbis-clock-anchors/v1",
                            "independent_anchors": [a],
                        })

    def test_hash_and_source_lineage_are_pinned(self):
        self.assertEqual(self.report["source"]["facsimile_sha256"],
                         "63654bcd90c0515f30e31ed511a12a05f170ff4470e3d8a6f40fca12012a1adb")
        self.assertTrue(self.report["source"]["same_broadcast_lineage_as_C01"])
        self.assertTrue(self.report["modern_proxy_plane_comparison"]
                        ["not_a_dynamically_fitted_orbit"])

    def test_checked_output_matches_canonical_procedure(self):
        committed = f.OUTPUT.read_text(encoding="utf-8")
        self.assertEqual(committed, f.render())


if __name__ == "__main__":
    unittest.main()
