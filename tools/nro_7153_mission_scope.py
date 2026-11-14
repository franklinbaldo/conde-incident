"""C241-L48: distinguish a 1963 SIGINT mission's operational end from decay.

Offline, fail-closed source-scope contract; not an orbital propagator.
"""
import json
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "research/tle_custody/nro_7153_mission_scope_C241-L48.json"


def audit(data):
    if data.get("schema") != "c241-l48-nro-7153-mission-scope/v1":
        raise ValueError("unexpected manifest schema")
    if data.get("id") != "C241-L48":
        raise ValueError("unexpected source identifier")
    s, m, i, r = (data[k] for k in ("source", "mission", "identity", "scientific_readiness"))
    if s["institution"] != "National Reconnaissance Office" or s["authored_year"] != 1994:
        raise ValueError("wrong origin or historical contemporaneity")
    if (s["textual_page"], s["retrieval"], s["visual_verification"]) != (
        90, "WEB_TEXT_EXCERPT_ONLY", "PENDING_REMOTE_403"
    ):
        raise ValueError("visual/byte custody cannot be claimed")
    if s["pdf_sha256"] is not None or s["pdf_bytes"] is not None:
        raise ValueError("no independently downloaded authenticated PDF")
    if s["contemporaneous_1963_record"] or s["independent_orbital_measurement"]:
        raise ValueError("institutional narrative is not a contemporary track")
    if (m["vehicle"], m["number"], m["program"], m["launch_date"]) != (
        "2313", 7153, "698BK", "1963-01-16"
    ):
        raise ValueError("mission crosswalk changed")
    if m["reported_operational_duration_days"] != 2 or m["duration_precision"] != "NARRATIVE_NOT_INSTRUMENTAL":
        raise ValueError("two days was narrative duration, not a timestamp")
    if m["failure_cause"] != "BATTERY_FAILURE":
        raise ValueError("failure cause changed")
    for name in ("failure_timestamp_utc", "orbit_decay_timestamp_utc", "structural_breakup_utc"):
        if m[name] is not None:
            raise ValueError(f"unsupported timestamp: {name}")
    if not i["vehicle_catalog_link"].startswith("FTV 2313 / OPS 0180 / NORAD 527"):
        raise ValueError("wrong catalog cross-reference")
    if (i["norad_528"], i["norad_529"]) != ("1963-003B", "1963-003C"):
        raise ValueError("wrong target identities")
    if (i["debris_identity_verified_by_nro_history"]
            or i["failure_means_structural_breakup"]
            or i["mission_end_means_528_decay"]
            or i["debris_separation_epoch_utc"] is not None):
        raise ValueError("operational end promoted to debris event")
    if r["orbital_measurements_527_528_529_added"] != 0:
        raise ValueError("narrative is not an orbital measurement")
    for name in ("tracking_sensor", "observed_angular_or_range_data", "error_covariance",
                 "observation_selection", "operator_H", "historical_likelihood"):
        if r[name] is not None:
            raise ValueError(f"unmeasured physical field: {name}")
    if (r["historical_mcmc"] != "NOT_RUN" or r["physical_constraint_active"]
            or r["conde_geographic_contraction"]):
        raise ValueError("no calibrated likelihood or geographic constraint")
    needed = data["observations_needed"]
    if len(needed) < 3 or any(not isinstance(v, str) or not v for v in needed):
        raise ValueError("discriminating observations not enumerated")
    return {
        "id": data["id"],
        "independent_orbital_observations_added": 0,
        "distinct_operational_and_orbital_time_variables": True,
        "decay_or_breakup_time_from_battery_failure": None,
        "mass_528_kg": None,
        "historical_mcmc": "NOT_RUN",
        "physical_constraint_active": False,
        "geographic_domain_reduced": False,
        "pdf_binary_verified": False,
        "next_observation_count": len(needed),
    }


def main():
    print(json.dumps(audit(json.loads(SOURCE.read_text(encoding="utf-8"))),
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
