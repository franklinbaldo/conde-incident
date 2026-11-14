import copy
import json
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "research/tle_custody/kettering_series_boundary_C241_LONTRA_R47.json"

def require(condition):
    if not condition:
        raise AssertionError("Archival claim violated")

def validate(payload):
    require(payload["schema"] == "conde.archival_locator_custody/v1")
    require(payload["id"] == "C241-LONTRA-R47")
    rows = payload["catalogue_records"]
    require(len(rows) == 5)
    require(len({x["shelfmark"] for x in rows}) == len(rows))
    require(all(x["url"].startswith("https://collection.sciencemuseumgroup.org.uk/documents/") for x in rows))
    require(all(not x["facsimile_retrieved"] and x["facsimile_sha256"] is None for x in rows))
    require(all(x["contains_target_in_unseen_pages"] is None for x in rows))
    dates = {x["shelfmark"]: x for x in rows}
    require(dates["KET/A/5/2/01"]["catalogue_period"] == "1965-03/1965-12")
    require(dates["KET/A/5/2/01"]["may_cover_1963"] is False)
    require(all(dates[k]["may_cover_1963"] is True for k in ["KET/A/1/09", "KET/A/2/1", "KET/A/6"]))
    require(dates["KET/C/3/11"]["catalogue_type"] == "other_spacecraft_control")
    boundary = payload["series_boundary"]
    require(boundary["first_catalogued_volume_begins"] == "1965-03")
    require(boundary["excludes_1963_from_this_identified_volume"] is True)
    for key in ("proves_no_kettering_observations_in_1963", "proves_1963_diary_or_correspondence_empty", "proves_unlisted_1963_logbooks_never_existed"):
        require(boundary[key] is False)
    t = payload["target"]
    require(t["norad"] == [527, 528, 529])
    require(t["designations"] == ["1963-003A", "1963-003B", "1963-003C"])
    require(t["window_utc"] == ["1963-11-07", "1963-11-09"])
    require(t["identified_measurements_retrieved"] == 0)
    require(t["identified_in_retrieved_folios"] is False)
    require(not t["station_clock_frame_provenance_verified"])
    require(t["new_orbital_constraints_activated"] == 0)
    c = payload["custody"]
    require(c["source_binary_sha256"] is None and c["facsimile_bytes_retrieved"] == 0)
    require(not c["external_contact_sent"])

class KetteringSeriesBoundaryR47(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(PATH.read_text(encoding="utf-8"))

    def test_real_manifest(self):
        validate(self.payload)

    def test_other_year_cannot_become_1963(self):
        bad = copy.deepcopy(self.payload)
        for row in bad["catalogue_records"]:
            if row["shelfmark"] == "KET/A/5/2/01":
                row["may_cover_1963"] = True
        with self.assertRaises(AssertionError):
            validate(bad)

    def test_no_negative_inference_from_late_series_start(self):
        bad = copy.deepcopy(self.payload)
        bad["series_boundary"]["proves_no_kettering_observations_in_1963"] = True
        with self.assertRaises(AssertionError):
            validate(bad)

    def test_unseen_folios_are_unknown_not_false(self):
        bad = copy.deepcopy(self.payload)
        bad["catalogue_records"][0]["contains_target_in_unseen_pages"] = False
        with self.assertRaises(AssertionError):
            validate(bad)

    def test_catalogue_is_not_facsimile(self):
        bad = copy.deepcopy(self.payload)
        bad["catalogue_records"][0]["facsimile_retrieved"] = True
        with self.assertRaises(AssertionError):
            validate(bad)

    def test_only_other_spacecraft_as_control(self):
        bad = copy.deepcopy(self.payload)
        bad["catalogue_records"][-1]["catalogue_type"] = "target_measurement"
        with self.assertRaises(AssertionError):
            validate(bad)

    def test_no_fictitious_original_sha(self):
        bad = copy.deepcopy(self.payload)
        bad["custody"]["source_binary_sha256"] = "0"*64
        with self.assertRaises(AssertionError):
            validate(bad)

    def test_no_orbital_claim_without_instrument(self):
        bad = copy.deepcopy(self.payload)
        bad["target"]["new_orbital_constraints_activated"] = 1
        with self.assertRaises(AssertionError):
            validate(bad)

    def test_no_fictitious_independent_measurement(self):
        bad = copy.deepcopy(self.payload)
        bad["target"]["identified_measurements_retrieved"] = 1
        with self.assertRaises(AssertionError):
            validate(bad)

    def test_unchanged_target_identity(self):
        bad = copy.deepcopy(self.payload)
        bad["target"]["norad"] = [527, 528, 683]
        with self.assertRaises(AssertionError):
            validate(bad)

if __name__ == "__main__":
    unittest.main()
