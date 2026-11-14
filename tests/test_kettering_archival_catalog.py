"""Conservative catalogue-to-observation barrier for C241-LONTRA-R43."""
import copy
import json
import unittest
from pathlib import Path

FILE = (Path(__file__).resolve().parents[1] / "research/tle_custody" /
        "kettering_1963_catalog_C241-LONTRA-R43.json")


def _require(condition):
    if not condition:
        raise ValueError("unverified catalogue promoted to observation")


def validate(d):
    _require(d["id"] == "C241-LONTRA-R43")
    _require(d["status"].startswith("ARCHIVAL_CATALOGUE_IDENTIFIED_ONLY"))
    _require(d["repository"]["collection_identifier"] == "KET")
    ids = {item["id"] for item in d["items"]}
    _require({"KET/A/1/09", "KET/A/2/1", "KET/A/4"} <= ids)
    for item in d["items"]:
        _require(item["catalog_url"].startswith("https://collection.sciencemuseumgroup.org.uk/documents/"))
        _require(item["november_7_to_9_entries_read"] is False)
    by_id = {i["id"]: i for i in d["items"]}
    _require(by_id["KET/A/1/09"]["date_coverage"] == "1963")
    _require(by_id["KET/A/2/1"]["date_coverage"] == "1960-1964")
    _require(by_id["KET/C/3/11"]["catalogue_claim"].find("1963-003") >= 0)
    r = d["retrieval"]
    _require(r["html_bytes_sha256"] is None)
    _require(r["original_diary_facsimile_downloaded"] is False)
    _require(r["original_1963_observation_log_read"] is False)
    _require(r["catalogue_is_primary_instrumental_source"] is False)
    _require(r["november_1963_content_verified"] is False)
    _require("first three" in r["direct_get_scope_note"])
    t = d["targets"]
    _require(t["norad_ids"] == [527, 528, 529])
    _require(t["target_match_confirmed"] is False)
    _require(t["target_astrometric_observations_retrieved"] == 0)
    _require(t["target_radio_observations_retrieved"] == 0)
    _require(t["new_orbital_constraints_activated"] == 0)
    _require(d["outreach_sent"] is False)


class KetteringCatalogueTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(FILE.read_text(encoding="utf-8"))

    def test_manifest(self):
        validate(self.data)

    def test_not_instrumental_source(self):
        d = copy.deepcopy(self.data)
        d["retrieval"]["catalogue_is_primary_instrumental_source"] = True
        with self.assertRaises(ValueError): validate(d)

    def test_no_invented_facsimile(self):
        d = copy.deepcopy(self.data)
        d["retrieval"]["original_diary_facsimile_downloaded"] = True
        with self.assertRaises(ValueError): validate(d)

    def test_no_pseudo_sha(self):
        d = copy.deepcopy(self.data)
        d["retrieval"]["html_bytes_sha256"] = "0" * 64
        with self.assertRaises(ValueError): validate(d)

    def test_no_november_1963_claim(self):
        d = copy.deepcopy(self.data)
        d["retrieval"]["november_1963_content_verified"] = True
        with self.assertRaises(ValueError): validate(d)

    def test_no_wrong_target_promotion(self):
        d = copy.deepcopy(self.data)
        d["targets"]["target_match_confirmed"] = True
        with self.assertRaises(ValueError): validate(d)

    def test_no_orbital_constraint(self):
        d = copy.deepcopy(self.data)
        d["targets"]["new_orbital_constraints_activated"] = 1
        with self.assertRaises(ValueError): validate(d)

    def test_no_unverified_outreach(self):
        d = copy.deepcopy(self.data)
        d["outreach_sent"] = True
        with self.assertRaises(ValueError): validate(d)

    def test_reject_invented_diary_entry(self):
        d = copy.deepcopy(self.data)
        d["items"][0]["november_7_to_9_entries_read"] = True
        with self.assertRaises(ValueError): validate(d)


if __name__ == "__main__":
    unittest.main()
