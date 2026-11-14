"""Adversarial chain-of-custody tests for the 1963 NORAD Cold Lake report."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from tle_norad_janjun_cold_lake_c241_l57 import (  # noqa: E402
    audit, read_manifest, verify_pdf,
)


class NoradJanJun1963Tests(unittest.TestCase):
    def setUp(self):
        self.source = read_manifest()

    def reject(self, mutate):
        candidate = copy.deepcopy(self.source)
        mutate(candidate)
        with self.assertRaises(ValueError):
            audit(candidate)

    def test_original_valid_but_noninstrumental(self):
        v = audit(self.source)
        self.assertEqual(v["institutional_events"], 4)
        self.assertEqual(v["individual_observations"], 0)
        self.assertEqual(v["target_page_visual_review"], "PENDING")

    def test_pdf_sha_cannot_be_replaced(self):
        self.reject(lambda a: a["source"].update(pdf_sha256="0" * 64))

    def test_pdf_length_cannot_be_replaced(self):
        self.reject(lambda a: a["source"].update(pdf_bytes=2))

    def test_pdf_mirror_url_cannot_drift(self):
        self.reject(lambda a: a["source"].update(accessed_pdf_url="https://example.test/a.pdf"))

    def test_printed_page_not_claimed_as_pdf_page(self):
        self.reject(lambda a: a["source"].update(pdf_page_indices_zero_based=[33, 34]))

    def test_unverified_page_not_promoted_to_visual(self):
        self.reject(lambda a: a["source"].update(reading_status="VISUALLY_VERIFIED"))

    def test_report_date_not_observation_date(self):
        self.reject(lambda a: a["source"].update(publication_date="1963-05-09"))

    def test_do_not_create_new_sensor(self):
        self.reject(lambda a: a["source"].update(source_class="PRIMARY_RADAR_LOG"))

    def test_event_not_measurement(self):
        self.reject(lambda a: a["events"][0].update(instrumental_observation=True))

    def test_event_date_not_fabricated(self):
        self.reject(lambda a: a["events"][2].update(date="1963-11-08"))

    def test_event_not_duplicated(self):
        self.reject(lambda a: a["events"][1].update(date="1963-01-09", kind="PLAN_REVIEW"))

    def test_cold_lake_not_prince_albert(self):
        self.reject(lambda a: a["cold_lake"].update(place="Prince Albert, Canada"))

    def test_cold_lake_not_sao_operator(self):
        self.reject(lambda a: a["cold_lake"].update(operator="Smithsonian Astrophysical Observatory"))

    def test_direct_control_not_precise_start_date(self):
        self.reject(lambda a: a["cold_lake"].update(exact_effective_date="1963-01-01"))

    def test_direct_control_not_528_log(self):
        self.reject(lambda a: a["cold_lake"].update(report_for_528="confirmed"))

    def test_direct_control_not_528_receipt(self):
        self.reject(lambda a: a["cold_lake"].update(spadats_528_receipt="received"))

    def test_do_not_fabricate_528_utc(self):
        self.reject(lambda a: a.update(norad_528_observation_utc="1963-11-08T12:00:00Z"))

    def test_do_not_fabricate_528_station(self):
        self.reject(lambda a: a.update(norad_528_observation_station="Cold Lake"))

    def test_do_not_fabricate_error(self):
        self.reject(lambda a: a.update(norad_528_sigma=0.001))

    def test_do_not_fabricate_terminal_time(self):
        self.reject(lambda a: a.update(terminal_event_utc="1963-11-08T15:00:00Z"))

    def test_do_not_fabricate_orbit(self):
        self.reject(lambda a: a.update(orbital_parameters={"raan": 284.152}))

    def test_do_not_activate_physics(self):
        self.reject(lambda a: a.update(physical_constraint_active=True))

    def test_no_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bad.json"
            p.write_text('{"evidence_id":"C241-L57","evidence_id":"fake"}', encoding="utf-8")
            with self.assertRaises(ValueError):
                read_manifest(p)

    def test_wrong_pdf_is_rejected(self):
        with self.assertRaises(ValueError):
            verify_pdf(b"%PDF-1.4\nfake\n")


if __name__ == "__main__":
    unittest.main()
