#!/usr/bin/env python3
"""Verify a station locator without promoting an institutional history to astrometry."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/tle_custody/novosibirsk_station_1963_C241-L31.json"


class TextOnly(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def validate(data, html_bytes=None):
    source = data["source"]
    station = data["station"]
    assert data["schema"] == "conde.archival_station_locator/v1"
    assert data["id"] == "C241-L31"
    assert data["epistemic_level"] == "RETROSPECTIVE_INSTITUTIONAL_STATION_LOCATOR_ONLY"
    assert source["source_kind"] == "INSTITUTIONAL_RETROSPECTIVE_HISTORY"
    assert source["sha256_applies_to"] == "current institutional HTML, not historical records"
    assert source["original_1963_facsimile_retrieved"] is False
    assert source["http_status"] == 200
    assert source["bytes"] > 0 and len(source["sha256"]) == 64
    assert station["station_numbers_mentioned"] == [1035, 1090]
    assert station["specific_site_on_1963_11_08"] is None
    assert station["exact_site_coordinates"] is None
    assert station["aggregate_measurements_reported"]["measurements_in_1963_only"] is None
    assert station["photography_began_year"] == 1963
    assert station["photographic_camera_1963"] == "НАФА-21"
    assert station["later_camera"]["delivered_year"] == 1965
    assert data["target_objects"] == [527, 528, 529]
    assert data["primary_observations_for_targets_retrieved"] == 0
    assert data["orbital_constraint_activated"] is False
    assert data["historical_1963_observing_epoch_verified"] is False
    assert data["station_position_or_site_code_promoted_to_orbit"] is False
    assert data["library_contacted"] is False
    if html_bytes is not None:
        assert len(html_bytes) == source["bytes"], "HTML size changed"
        assert hashlib.sha256(html_bytes).hexdigest() == source["sha256"], "HTML digest changed"
        parser = TextOnly()
        parser.feed(html_bytes.decode("utf-8"))
        text = " ".join(" ".join(parser.parts).split())
        for token in ["НАФА-21", "УФИСЗ-25", "Интеробс", "1035", "1090", "1963", "Антонович"]:
            assert token in text, "source missing expected wording: " + token
    return True


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", type=Path)
    args = ap.parse_args()
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    validate(data, args.html.read_bytes() if args.html else None)
    print("PASS: locator qualifiers and non-promotion" + ("; HTML replay" if args.html else ""))
