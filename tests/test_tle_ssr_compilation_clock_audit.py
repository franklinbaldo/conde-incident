"""No-network adversarial controls for C241-L15 (not OCR of a NASA PDF)."""
import copy
import json
from pathlib import Path
import unittest

from tools.tle_ssr_compilation_clock_audit import audit, validate_ledger

LEDGER = Path(__file__).resolve().parents[1] / "research/tle_custody/nasa_ssr_compilation_asof_C241-L15.json"


class SnapshotClockAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(LEDGER.read_text(encoding="utf-8"))

    def corrupt(self, change):
        data = copy.deepcopy(self.data)
        change(data)
        with self.assertRaises((ValueError, TypeError, KeyError)):
            validate_ledger(data)

    def test_real_ledger(self):
        self.assertEqual([x["number"] for x in validate_ledger(self.data)], [20, 22, 23])

    def test_utc_compilation_not_sensor_epoch(self):
        self.assertEqual([x["compilation_as_of_utc"] for x in validate_ledger(self.data)],
                         ["1963-10-15T12:00:00Z", "1963-11-15T12:00:00Z",
                          "1963-11-30T12:00:00Z"])
        self.assertIsNone(self.data["missing"]["physical_observation_epoch"])

    def test_wrong_asof_clock(self):
        self.corrupt(lambda d: d["sources"][1].update(compilation_as_of_utc="1963-11-15T00:00:00Z"))

    def test_wrong_asof_day(self):
        self.corrupt(lambda d: d["sources"][0].update(compilation_as_of_utc="1963-10-16T12:00:00Z"))

    def test_treat_snapshot_as_physical_epoch(self):
        self.corrupt(lambda d: d["missing"].update(physical_observation_epoch="1963-11-15T12:00:00Z"))

    def test_claim_three_independent_sensors(self):
        self.corrupt(lambda d: d.update(independence="THREE_INDEPENDENT_RADARS"))

    def test_fabricated_station(self):
        self.corrupt(lambda d: d["missing"].update(sensor_station="NORAD_STATION_X"))

    def test_fabricated_frame(self):
        self.corrupt(lambda d: d["missing"].update(frame="TEME"))

    def test_fabricated_covariance(self):
        self.corrupt(lambda d: d["missing"].update(sigma=1.0))

    def test_fake_primary_tle(self):
        self.corrupt(lambda d: d["missing"].update(tle_from_ssr=True))

    def test_legacy_raan_not_activated(self):
        self.corrupt(lambda d: d["missing"].update(legacy_raan_activated=True))

    def test_edition_21_not_invented(self):
        self.corrupt(lambda d: d["sources"][0].update(number=21))

    def test_absence_of_edition_21_not_asserted(self):
        self.corrupt(lambda d: d["missing"].update(edition_21="NEVER_PUBLISHED"))

    def test_single_source_removed(self):
        self.corrupt(lambda d: d["sources"].pop())

    def test_fabricated_pdf_digest(self):
        self.corrupt(lambda d: d["sources"][2]["accepted_download_sha256_and_bytes"][0].__setitem__(0, "a" * 64))

    def test_wrong_pdf_page(self):
        self.corrupt(lambda d: d["sources"][2].update(pdf_page_index_zero_based=3))

    def test_fake_ocr(self):
        self.corrupt(lambda d: d["sources"][0].update(facsimile_reading="MACHINE_OCR"))

    def test_unsourced_terminal_location(self):
        self.corrupt(lambda d: d["missing"].update(terminal_position=[-11.8, -37.6]))

    def test_unsourced_earth_impact(self):
        self.corrupt(lambda d: d["missing"].update(earth_impact_claim=True))

    def test_graph_epoch_link_required(self):
        self.corrupt(lambda d: d["graph_edge"].update(to="PHYSICAL_EPOCH_1200Z"))

    def test_not_a_pdf(self):
        with self.assertRaisesRegex(ValueError, "not a PDF"):
            audit(self.data, {x["ntrs_id"]: b"text" for x in self.data["sources"]})

    def test_unpinned_pdf_bytes(self):
        with self.assertRaisesRegex(ValueError, "unrecognized NASA PDF bytes"):
            audit(self.data, {x["ntrs_id"]: b"%PDF-1.4\nfake\n%%EOF" for x in self.data["sources"]})

    def test_missing_input_fails(self):
        with self.assertRaisesRegex(ValueError, "missing or unexpected PDF"):
            audit(self.data, {})


if __name__ == "__main__":
    unittest.main()
