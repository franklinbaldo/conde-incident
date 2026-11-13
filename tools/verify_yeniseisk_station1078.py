#!/usr/bin/env python3
"""Audit an undated Soviet-station institutional history without promoting it to measurements."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/tle_custody/yeniseisk_station1078_journals_C241-L38.json"

def validate(d, html_bytes=None):
    assert d["schema"] == "conde.archival_station_locator/v1"
    assert d["id"] == "C241-L38"
    a = d["institutional_history"]
    assert a["url"] == "https://www.lpi.sfu-kras.ru/node/286"
    assert a["station_identifier"] == "1078" and a["observed_station_name"] == "Енисейск, Красноярский край"
    assert a["station_founded_year_stated"] == 1961
    assert a["period_of_operation_described_as_years"] == 25
    assert a["date_of_web_publication"] is None
    assert a["kind"] == "UNDATED_INSTITUTIONAL_RETROSPECTIVE"
    assert a["states_original_journals_kept_at_station_at_time_of_writing"] is True
    assert a["journal_years_individually_itemized"] is False
    assert a["journal_november_1963_confirmed"] is False
    assert a["present_day_holding_confirmed"] is False
    assert a["catalogue_call_number"] is None
    assert a["source_original_observation_facsimile"] is False
    s = d["retrieved_transport_copy"]
    assert s["retrieved"] is True and s["bytes"] == 321424
    assert s["sha256"] == "4df12d13cef3bcec550c0d53c34d0a8080f2b292080ebb51b7b0d9d66eab1721"
    assert s["tls_certificate_validated"] is False
    assert s["http_status"] == 200
    assert "curl --insecure" in s["retrieval_caveat"]
    r = d["route"]
    assert r["target_norad_ids"] == [527, 528, 529]
    assert r["candidate_observation_dates"] == ["1963-11-07", "1963-11-08", "1963-11-09"]
    for k in ("catalogue_or_inventory_available", "target_objects_explicitly_identified",
              "station_logs_retrieved", "station_coordinates_confirmed_for_1963", "archive_contacted"):
        assert r[k] is False, k
    assert d["independent_target_measurements"] == 0
    assert d["new_numeric_observables"] == 0
    assert d["orbital_constraints_activated"] == 0
    assert d["epistemic_status"] == "INSTITUTIONAL_HISTORY_ARCHIVAL_LEAD_NOT_TARGET_OBSERVATION"
    if html_bytes is not None:
        assert len(html_bytes) == s["bytes"], "transport copy byte length differs"
        assert hashlib.sha256(html_bytes).hexdigest() == s["sha256"], "transport copy hash differs"
        text = html_bytes.decode("utf-8")
        for phrase in ("Справка о станции наблюдений ИСЗ", "СОН ИЗС № 1078",
                       "По журналам наблюдений за 25 лет работы, которые хранятся на станции"):
            assert phrase in text, "history text missing: " + phrase
    return True

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--html", type=Path, help="original downloaded HTML transport copy")
    args = p.parse_args()
    validate(json.loads(MANIFEST.read_text(encoding="utf-8")),
             args.html.read_bytes() if args.html else None)
    print("PASS: station-1078 archival lead, without target observation promotion")
