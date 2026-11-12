#!/usr/bin/env python3
"""Decode an authentic, pinned IGRA profile. No spatial transfer or meteor trajectory."""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "research/meteorology/igra_recife_19631108_raw.txt.b64"
OUTPUT = ROOT / "research/meteorology/igra_recife_19631108_wind_observables.json"
ARCHIVE_SHA256 = "0655b3ea80312abe888a5474f82233affc0a2496ee1fd8bc678162924f52ecdc"
ARCHIVE_BYTES = 7834492
EXPECTED_FIXTURE_SHA256 = "577224172e19552f5ce87081897479255596dc44debacc674dfd9d9ec418207e"
SOURCE_URL = "https://www.ncei.noaa.gov/pub/data/igra/data/data-por/BRM00082900-data.txt.zip"
FORMAT_URL = "https://www.ncei.noaa.gov/pub/data/igra/data/igra2-data-format.txt"
STATION_URL = "https://www.ncei.noaa.gov/pub/data/igra/igra2-station-list.txt"


def number(line: str, start: int, end: int) -> int | None:
    value = int(line[start:end])
    return None if value in (-9999, -8888) else value


def read_profile(raw: bytes) -> dict:
    # ASCII payload copied verbatim from an IGRA 2.2 period-of-record station ZIP.
    lines = raw.decode("ascii").splitlines()
    if len(lines) < 2 or not lines[0].startswith("#"):
        raise ValueError("IGRA header absent")
    head = lines[0]
    if head[1:12] != "BRM00082900" or head[13:17] != "1963" or head[18:20] != "11" or head[21:23] != "08":
        raise ValueError("wrong IGRA station/day")
    nominal_hour = int(head[24:26])
    release_time = int(head[27:31])
    n_levels = int(head[32:36])
    if nominal_hour != 12 or release_time != 9999:
        raise ValueError("expected nominal 12Z with missing launch time")
    if n_levels != 26 or len(lines) != n_levels+1:
        raise ValueError("IGRA level count truncated or shifted")
    if head[37:45].strip() != "ncdc6301":
        raise ValueError("IGRA P_SRC changed; reassess custody")
    lat = int(head[55:62])/10000
    lon = int(head[63:71])/10000
    if (lat,lon) != (-8.05,-34.9167):
        raise ValueError("station coordinates changed; reassess metadata")
    levels = []
    winds = []
    for i,ln in enumerate(lines[1:]):
        if len(ln) < 51 or ln[0] not in "123" or ln[1] not in "012":
            raise ValueError("malformed IGRA level")
        p_pa = number(ln,9,15)
        gph = number(ln,16,21)
        wdir = number(ln,40,45)
        wspd10 = number(ln,46,51)
        if (wdir is None) != (wspd10 is None):
            raise ValueError("incomplete wind vector")
        if wdir is not None and not (0 <= wdir <= 360 and wspd10 >= 0):
            raise ValueError("out-of-range wind")
        if p_pa is not None and p_pa <= 0:
            raise ValueError("non-positive pressure")
        row = {
            "level_index_zero_based":i,
            "level_type":int(ln[0]),
            "pressure_hpa":None if p_pa is None else p_pa/100,
            "geopotential_height_m_asl":gph,
            "geopotential_height_quality_flag":ln[21].strip() or None,
            "wind_from_deg":wdir,
            "wind_speed_m_s":None if wspd10 is None else wspd10/10,
        }
        levels.append(row)
        if wdir is not None:
            theta=math.radians(wdir)
            winds.append({
                **row,
                "eastward_u_m_s":round(-(wspd10/10)*math.sin(theta),6),
                "northward_v_m_s":round(-(wspd10/10)*math.cos(theta),6),
            })
    if not winds or len(winds) >= len(levels):
        raise ValueError("unexpected no/missing wind arrangement")
    return {
        "schema":"conde.igra-recife-c151-wind-profile/v1",
        "source": {
            "custodian":"NOAA/NCEI IGRA2.2 full-period-of-record archive",
            "full_station_zip_url":SOURCE_URL,
            "full_station_zip_sha256":ARCHIVE_SHA256,
            "full_station_zip_bytes":ARCHIVE_BYTES,
            "format_url":FORMAT_URL,
            "format_sha256":"dfd7b4d2dd18a255477455a7caefd12cb21c30549a1e70cbc3a51db9f41c1dfe",
            "station_list_url":STATION_URL,
            "station_list_sha256":"5a277ba4036544cb79d07e3f503f7ca1aaa2d81a304dbea5f79ac24808d2dc34",
            "verbatim_1963_profile_sha256":hashlib.sha256(raw).hexdigest(),
            "archive_access_utc_date":"2026-11-12",
            "upstream_pressure_source_code":"ncdc6301",
            "provenance_family":"ONE sounding, NOT independent of archive repackagings using the same rawindsonde",
            "instrumental_measurement_error":"UNKNOWN; reported 0.1 m/s wind-speed increments are not error bounds",
        },
        "station":{
            "id":"BRM00082900",
            "station_list_name":"RECIFE (82900-0)",
            "archive_latitude_deg":lat,
            "archive_longitude_deg_east":lon,
            "station_elevation_m_asl":7.0,
            "coordinates_historical_reconstruction":"NOT VERIFIED; IGRA fixed-station coordinates do not reconstruct 1963 relocations",
        },
        "sounding":{
            "date_nominal_utc":"1963-11-08",
            "nominal_hour_utc":12,
            "release_time_hhmm":None,
            "release_time_raw_missing_code":9999,
            "source_level_count":n_levels,
            "levels_with_reported_wind":len(winds),
            "max_reported_wind_height_m_asl":max(x["geopotential_height_m_asl"] for x in winds if x["geopotential_height_m_asl"] is not None),
            "wind_direction_convention":"meteorological degrees FROM north; u=-speed*sin(dir); v=-speed*cos(dir)",
        },
        "wind_observables_at_recife":winds,
        "missing_wind_levels": [
            {"level_index_zero_based":r["level_index_zero_based"],"pressure_hpa":r["pressure_hpa"]}
            for r in levels if r["wind_from_deg"] is None
        ],
        "physical_links":{
            "C149_C150_C151":"same archived Recife sounding; not three independent observations",
            "balloon_fragment_drift":"CONDITIONAL_ONLY; requires launch location/time, vertical trajectory, descent/drag, spatiotemporal wind transfer and errors",
            "density_drag_satellite":"NOT_A_THERMOSPHERIC_DENSITY_OBSERVATION; no constraint on NORAD 528 without independent transfer model",
            "C144_C146":"independent CHM surface pressure maps; NOT same vertical wind measurement",
            "C193":"Explorer XVII April–June 1963 thermospheric observations, different altitude/month and cannot calibrate these winds directly",
            "physical_constraint_status":"CONNECTED_PENDING_SPATIOTEMPORAL_TRANSFER",
        }
    }


def build():
    payload = base64.b64decode(FIXTURE.read_bytes())
    if hashlib.sha256(payload).hexdigest() != EXPECTED_FIXTURE_SHA256:
        raise ValueError("original verified IGRA excerpt altered")
    return read_profile(payload)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    expected=build()
    if args.check:
        actual=json.loads(OUTPUT.read_text(encoding="utf-8"))
        if actual!=expected:
            raise SystemExit("FAIL: raw IGRA fixture and published observables differ")
        print("PASS pinned NOAA Recife 1963 sounding: 26 levels, wind directions/components, no place/launch time inferred")
    else:
        print(json.dumps(expected,ensure_ascii=False,indent=2)+"\n",end="")


if __name__=="__main__": main()
