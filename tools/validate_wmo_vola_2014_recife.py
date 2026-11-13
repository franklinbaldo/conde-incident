"""Validate a visual transcription of WMO Volume A 2014, never infer a 1963 sounding."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/meteorology/wmo_vola_2014_recife.json"
PDF_URL = "https://old.wmo.int/extranet/pages/prog/www/ois/Operational_Information/VolumeA/VolumeA2014ed.pdf"
ROW_RE = re.compile(
    r"^(899|900) +(RECIFE(?: \(AERO\))?) +\.{4,} +"
    r"(\d{2}) +(\d{2}) +(\d{2})S +(\d{2}) +(\d{2}) +(\d{2})W +"
    r"(\d+\.\d+) +(\d+\.\d+) +(.+)$"
)
UPPER_AIR_TIMES = ("00", "06", "12", "18")


def validate(data):
    source = data["source"]
    if not (data["schema"] == "conde.wmo-volume-a-2014-recife/v1"
            and source["edition"] == "2014-12" and source["url"] == PDF_URL
            and source["pdf_page_index_zero_based"] == 248
            and source["pdf_page_number_one_based"] == 249
            and source["visual_page_verified"] is True
            and source["pdf_sha256"] is None):
        raise ValueError("unverified or misdated source")
    if len(data["rows"]) != 2:
        raise ValueError("missing or extra stations")
    decoded = {}
    for row in data["rows"]:
        m = ROW_RE.fullmatch(row["transcribed_pdf_row"])
        if m is None:
            raise ValueError("malformed excerpt")
        suffix, name, *rest = m.groups()
        if row["wmo_id"] != 82000 + int(suffix) or row["short_index"] != int(suffix):
            raise ValueError("bad expanded WMO identifier")
        lat = list(map(int, rest[:3]))
        lon = list(map(int, rest[3:6]))
        hp, elev = map(float, rest[6:8])
        cols = rest[8].split()
        if len(cols) != 14:
            raise ValueError("bad table columns")
        if (row["name"] != name or row["latitude_south_dms"] != lat
                or row["longitude_west_dms"] != lon
                or row["pressure_datum_hp_m"] != hp
                or row["terrain_or_aerodrome_elevation_m"] != elev
                or row["surface_at_utc_2014"] != cols[:8]
                or row["hourly_obs"] != cols[8]
                or row["upper_air_at_utc_2014"] != cols[9:13]
                or row["remarks"] != cols[13]):
            raise ValueError("structured field differs from excerpt")
        decoded[row["wmo_id"]] = row
    if set(decoded) != {82899, 82900}:
        raise ValueError("station pair lost")
    if not (decoded[82899]["name"] == "RECIFE (AERO)"
            and decoded[82899]["upper_air_at_utc_2014"] == ["."] * 4
            and decoded[82899]["remarks"] == "A;RBSN(S)"
            and decoded[82900]["name"] == "RECIFE"
            and decoded[82900]["upper_air_at_utc_2014"] == [".", ".", "RW", "."]
            and decoded[82900]["remarks"] == "CLIMAT(C);RBCN;RBSN(T)"):
        raise ValueError("2014 station roles changed")
    if set(data["historical_1963"]) != {
        "launch_site_wmo_id", "upper_air_schedule", "radiosonde_model",
        "pressure_temperature_height_covariance", "physical_transfer_to_conde",
        "coeval_wmo_catalogue_found"
    }:
        raise ValueError("historical gap fields missing")
    if (any(data["historical_1963"][key] is not None for key in
            ("launch_site_wmo_id", "upper_air_schedule", "radiosonde_model",
             "pressure_temperature_height_covariance", "physical_transfer_to_conde"))
            or data["historical_1963"]["coeval_wmo_catalogue_found"] is not False
            or data["admissible_domain_reduction"] is not False
            or data["independent_1963_measurements_added"] != 0
            or data["status"] != "CONNECTED_PENDING_CALIBRATION"):
        raise ValueError("2014 metadata incorrectly promoted to 1963 evidence")
    return True


if __name__ == "__main__":
    validate(json.loads(SOURCE.read_text(encoding="utf-8")))
    print("PASS WMO Volume A 2014 station lineage (2014 only)")
