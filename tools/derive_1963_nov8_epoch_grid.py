#!/usr/bin/env python3
"""Reproducible 1963-11-08 UTC 3h geomagnetic inputs; NOT an observed reentry."""
import datetime as dt
import json
import sys
from pathlib import Path

SOURCE = Path("research/meteorology/space_weather_msise_inputs_1963_11_07_09.json")
OUTPUT = Path("research/meteorology/space_weather_nov08_3h_epoch_grid.json")
DATE = dt.date(1963,11,8)

def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")

def derive(source):
    assert source["schema"] == "conde.1963-conditional-msise-drivers/v1"
    assert source["physical_constraint_status"] == "CONNECTED_PENDING_CALIBRATION"
    raw = source["raw_series"]
    daily = raw["F107_observed_daily"]
    ap = raw["ap"]
    kp = raw["Kp"]
    ap_daily = raw["Ap"][f"{DATE}T00:00:00Z"]
    f107_previous = daily[str(DATE-dt.timedelta(days=1))]["observed_sfu"]
    f107a = sum(daily[str(DATE+dt.timedelta(days=i))]["observed_sfu"] for i in range(-40,41))/81
    rows=[]
    for hour in range(0,24,3):
        start=dt.datetime(1963,11,8,hour,tzinfo=dt.timezone.utc)
        end=start+dt.timedelta(hours=3)
        value=lambda lag:ap[iso(start-dt.timedelta(hours=lag))]
        vector=[ap_daily,value(0),value(3),value(6),value(9),
                sum(value(h) for h in range(12,34,3))/8,
                sum(value(h) for h in range(36,58,3))/8]
        rows.append({
            "utc_interval_start_inclusive":iso(start),
            "utc_interval_end_exclusive":iso(end),
            "sampling_role":"UTC_INDEX_BIN_START_NOT_OBSERVED_REENTRY",
            "F107_previous_day_observed_sfu":f107_previous,
            "F107A_81day_centered_observed_sfu":round(f107a,6),
            "Ap_daily_planetary":ap_daily,
            "ap_current_3h":value(0),
            "Kp_current_3h":kp[iso(start)],
            "ap_history_planetary":[round(v,6) for v in vector],
            "location":None,
            "altitude_km":None,
            "local_solar_time_hours":None,
            "density_kg_m3":None,
            "wind_east_m_s":None,
            "wind_north_m_s":None,
            "propagator_error":None,
        })
    assert len(rows)==8
    return {
        "schema":"conde.1963-nov08-3h-space-weather-grid/v1",
        "historical_day_utc":str(DATE),
        "source_snapshot":SOURCE.as_posix(),
        "source_urls":{
            "GFZ_Kp_ap_Ap":"https://kp.gfz.de/en/data",
            "NRCan_F107":source["source_documents"]["F107"]["url"],
            "NRLMSISE_00_input_contract":"https://github.com/magnific0/nrlmsise-00/blob/master/nrlmsise-00.h",
        },
        "provenance":{
            "GFZ_3h_Kp_ap_daily_Ap":"single dependent geomagnetic index family; definitives",
            "Canada_F107_observed":"one solar flux family distinct from GFZ; not local density",
            "CelesTrak":"republication, not independent corroboration",
        },
        "measurement_uncertainty":None,
        "index_range_on_nov08_not_density_range":{
            "ap_3h_min":min(r["ap_current_3h"] for r in rows),
            "ap_3h_max":max(r["ap_current_3h"] for r in rows),
            "Kp_3h_min":min(r["Kp_current_3h"] for r in rows),
            "Kp_3h_max":max(r["Kp_current_3h"] for r in rows),
        },
        "epoch_or_reentry_location_observed":False,
        "interpretation":"Eight 3h index interval starts are conditional model inputs, NOT an event-time posterior, eight independent reentry observations, or a density/drag bound.",
        "physical_constraint_status":"CONNECTED_PENDING_CALIBRATION",
        "candidate_3h_inputs":rows,
    }

def validate_grid(source,grid):
    expected=derive(source)
    assert grid==expected,"offline grid differs from source snapshot"
    rows=grid["candidate_3h_inputs"]
    assert [r["utc_interval_start_inclusive"][11:13] for r in rows]==[f"{h:02d}" for h in range(0,24,3)]
    assert all(r["F107_previous_day_observed_sfu"]==76.6 for r in rows)
    assert all(r["Ap_daily_planetary"]==46 for r in rows)
    assert all(r["F107A_81day_centered_observed_sfu"]==82.265432 for r in rows)
    assert [r["ap_current_3h"] for r in rows]==[56,67,80,32,32,39,32,27]
    assert [r["Kp_current_3h"] for r in rows]==[5.333,5.667,6.0,4.333,4.333,4.667,4.333,4.0]
    assert grid["epoch_or_reentry_location_observed"] is False
    assert grid["measurement_uncertainty"] is None
    assert grid["physical_constraint_status"]=="CONNECTED_PENDING_CALIBRATION"
    for r in rows:
        assert len(r["ap_history_planetary"])==7
        assert all(r[key] is None for key in ("location","altitude_km","local_solar_time_hours",
                                             "density_kg_m3","wind_east_m_s","wind_north_m_s",
                                             "propagator_error"))
def main(args):
    src=Path(args[0]) if args and args[0]!="--check" else SOURCE
    source=json.loads(src.read_text(encoding="utf-8"))
    if "--check" in args:
        p=OUTPUT if args[0]=="--check" else Path(args[1])
        validate_grid(source,json.loads(p.read_text(encoding="utf-8")))
        print("PASS eight GFZ 3h bins, solar flux, 7-ap drivers; no place, epoch or density inferred")
    else:
        print(json.dumps(derive(source),ensure_ascii=False,indent=2))
if __name__=="__main__":
    main(sys.argv[1:])
