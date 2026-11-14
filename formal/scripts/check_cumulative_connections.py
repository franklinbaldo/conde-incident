#!/usr/bin/env python3
"""Validate accumulated evidence -> observable -> model links.

This is a provenance and dimension check, NOT a physical orbital fit.
Unknown epochs, covariance or reference conventions remain missing. Connected
pending edges are scientific progress even if they do not narrow Theta today.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ROOT / "research/constraints/ssr_1963_observable_graph.json"
CANONICAL = {
    "min": ("s", 60.0), "deg": ("rad", math.pi / 180), "km": ("m", 1000.0),
    "dimensionless": ("1", 1.0), "rev/day": ("rad/s", 2 * math.pi / 86400),
}
PENDING = "CANDIDATE_NOT_ACTIVATED"

# SSR columns cannot become independent observations by relabeling.
NASA_SSR_FIELDS = {
    "nodal_period": ("nodal_period_model", "min"),
    "inclination": ("inclination_model", "deg"),
    "apogee": ("apogee_model", "km"),
    "perigee": ("perigee_model", "km"),
}

# These two historical report editions are specific documentary objects.
# Reclassifying a compiled table as an independent sensor (or as a newly
# verified facsimile) must require a separately evidenced source update.
PINNED_NASA_SSR_SOURCES = {
    "NASA-SSR-1963-11-15": (
        "https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf",
        "1963-11-15",
    ),
    "NASA-SSR-1963-11-30": (
        "https://ntrs.nasa.gov/api/citations/19640002493/downloads/19640002493.pdf",
        "1963-11-30",
    ),
}
NASA_SSR_FAMILY = "NASA_GODDARD_COMPILED_FROM_TRACKING"
SHARED_TRACKING = "NORAD_AFS_SHARED_TRACKING_NOT_INDEPENDENT"
SSR_TABLE_VERIFICATION = "TABLE_FROM_PRIOR_INVESTIGATION_NOT_REVERIFIED_THIS_COMMIT"


def validate_528_tle_bridge(graph: dict, sources: dict, observations: list[dict]) -> list[dict]:
    """Connect 528 to 527/529 without interpreting TLE checksums as 1963 sensors."""
    bridges = graph.get("physical_bridges", [])
    if len(bridges) != 1 or bridges[0].get("id") != "C179-528-Kepler-J2-proxy":
        raise ValueError("missing C179 physical bridge")
    bridge = bridges[0]
    source = sources.get(bridge["source_id"])
    if not source or source.get("evidence_occurrence") != "C179#1":
        raise ValueError("untraced C179 source")
    if source.get("upstream_tracking_family") != "NORAD_AFS_SHARED_TRACKING_NOT_INDEPENDENT":
        raise ValueError("invalid C179 shared source lineage")
    # The original 1963 NORAD tracking data is NOT the mirror. This checker
    # compares a pinned literal source against the graph's six typed fields.
    sys.path.insert(0, str(ROOT))
    from tools.tle_literal_layout import audit_literal_file
    from physical_observable_bridge import orbital_observables, audit, parse_rows
    literal = audit_literal_file(ROOT / "research/tle_custody/mirror_528_1963-10-27.tle")
    if source.get("literal_sha256") != literal["source"]["sha256"]:
        raise ValueError("C179 source hash mismatch")
    data = (ROOT / "research/evidence_matrix_C001-C238_2026-11-11.md").read_bytes()
    rows = parse_rows(data)
    audit(data, rows)
    if len([r for r in rows if r["number"] == 179]) != 1:
        raise ValueError("C179 matrix occurrence missing")
    records = [o for o in observations if o["source_id"] == bridge["source_id"]]
    byname = {o["observable"]: o for o in records}
    if set(byname) != set(literal["values"]) or len(records) != len(byname):
        raise ValueError("incomplete or duplicate C179 TLE fields")
    for label, field in literal["values"].items():
        o = byname[label]
        if (o["object_id"] != 528 or o["matrix_local_id"] != "C179#1" or
            o["unit"] != field["unit"] or
            o.get("element_epoch_utc") != literal["epoch_utc"] or
            o.get("observed_at_utc") is not None or
            "observed_epoch" not in o["pending"] or
            "error_interval" not in o["pending"] or
            "frame_conversion_and_fit_covariance" not in o["pending"] or
            o["constraint_status"] != PENDING or
            float(field["decimal"]) != o["value"]):
            raise ValueError("C179 TLE value/epoch/unit/custody mismatch: " + label)
    legacy = graph.get("legacy_candidates", [])
    if len(legacy) != 1 or legacy[0].get("status") != "SOURCELESS_SYNTHETIC_RETRACTED_NOT_IN_MEASUREMENT_SET":
        raise ValueError("legacy unsourced candidate cannot be measured constraint")
    if (legacy[0].get("origin_commit") != "807a118939fac50b48d649b1045461bfcc79b140" or
        not math.isclose(legacy[0]["value_deg"] - byname["raan"]["value"],
                         legacy[0]["difference_from_C179_deg"], abs_tol=1e-9)):
        raise ValueError("legacy RAAN source conflict lost")
    if (set(bridge["input_observations"]) !=
        {byname[k]["id"] for k in ("mean_motion", "eccentricity", "inclination")} or
        bridge["physical_domain"] != "NOT_NARROWED_UNCALIBRATED_SOURCE" or
        bridge["validation"] != "NUMERICALLY_RECOMPUTED_FROM_HASH_PINNED_TLE_WITHOUT_PROPAGATION"):
        raise ValueError("unjustified C179 physical fit")
    # Both independent arithmetic and the existing Polvo physical operator
    # use a fixed Kepler/J2 proxy. No SGP4/drag/terminal location is inferred.
    n = byname["mean_motion"]["value"] * 2 * math.pi / 86400
    e = byname["eccentricity"]["value"]
    inclination = math.radians(byname["inclination"]["value"])
    mu, radius, j2 = 398600.4418, 6378.137, 1.08262668e-3
    a = (mu / n**2)**(1/3)
    hp = a * (1-e) - radius
    omega = -1.5*j2*n * (radius/(a*(1-e*e)))**2 * math.cos(inclination) * 86400 * 180/math.pi
    previous = orbital_observables()
    for name, computed in (
        ("derived_kepler_proxy_semimajor_km", a),
        ("derived_kepler_proxy_perigee_altitude_km", hp),
        ("derived_first_order_j2_raan_rate_deg_per_day", omega),
    ):
        if not math.isclose(computed, previous[name], abs_tol=1e-8):
            raise ValueError("C179 two orbital operators diverged: " + name)
    return [{
        "id": bridge["id"], "source_occurrence": "C179#1",
        "source_sha256": literal["source"]["sha256"],
        "element_epoch_utc": literal["epoch_utc"],
        "observed_tracking_epoch": "UNKNOWN_NOT_SAME_AS_ELEMENT_REFERENCE_EPOCH",
        "semimajor_km_kepler_proxy": a,
        "perigee_altitude_km_kepler_proxy": hp,
        "raan_rate_deg_per_day_first_order_j2_proxy": omega,
        "legacy_raan_delta_deg": legacy[0]["difference_from_C179_deg"],
        "physical_domain": bridge["physical_domain"],
        "missing": bridge["requires"],
        "upstream_tracking_family": source["upstream_tracking_family"],
    }]

def validate(graph: dict) -> dict:
    if graph.get("schema") != "conde.cumulative-constraint-graph/v1":
        raise ValueError("unknown cumulative-constraint graph schema")
    sources = {s["id"]: s for s in graph.get("sources", [])}
    params = {p["id"]: p for p in graph.get("parameters", [])}
    ops = {op["id"]: op for op in graph.get("operators", [])}
    obs = graph.get("observations", [])
    if (not sources or not params or not ops or not obs or
        len(sources) != len(graph["sources"]) or
        len(params) != len(graph["parameters"]) or
        len(ops) != len(graph["operators"])):
        raise ValueError("graph missing elements or duplicate source/parameter/operator IDs")
    # IDs and URL fragments must not turn one facsimile into new sources.
    source_documents = set()
    upstream_by_family = {}
    for source in graph["sources"]:
        url = source.get("url")
        if not isinstance(url, str) or not url.strip():
            raise ValueError("missing source document URL")
        # Query parameters and fragments do not establish an independent
        # documentary object. A genuinely different version needs an explicit
        # independent identifier, custody record and review.
        parsed = urlsplit(url.strip())
        document_url = urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(),
                                   parsed.path, "", ""))
        if document_url in source_documents:
            raise ValueError("duplicate source document URL")
        source_documents.add(document_url)
        pinned = PINNED_NASA_SSR_SOURCES.get(source["id"])
        if pinned and (
            source.get("url") != pinned[0]
            or source.get("published_on") != pinned[1]
            or source.get("source_family") != NASA_SSR_FAMILY
            or source.get("upstream_tracking_family") != SHARED_TRACKING
            or source.get("verification") != SSR_TABLE_VERIFICATION
        ):
            raise ValueError("pinned NASA SSR source identity/lineage/verification mismatch")
        family = source.get("source_family")
        origin = source.get("upstream_tracking_family")
        if not family or not origin:
            raise ValueError("missing source family or upstream lineage")
        if family in upstream_by_family and upstream_by_family[family] != origin:
            raise ValueError("conflicting upstream tracking lineage within source family")
        upstream_by_family[family] = origin
        if family == NASA_SSR_FAMILY and source["id"] not in PINNED_NASA_SSR_SOURCES:
            raise ValueError("unregistered NASA SSR document requires custody review")
    output = []
    ids = set()
    model_variables = set()
    observation_signatures = set()
    families = set()
    upstream = set()
    for o in obs:
        oid = o["id"]
        if oid in ids:
            raise ValueError(f"duplicate observation ID: {oid}")
        ids.add(oid)
        var = o.get("variable_id")
        if not isinstance(var, str) or not var.strip() or var in model_variables:
            raise ValueError(f"duplicate or invalid model variable: {oid}")
        model_variables.add(var)
        # Two IDs for the same source/table field are not independent samples.
        # A distinct measurement must have a distinct traced source or epoch.
        signature = (
            o["source_id"], o["object_id"], o["observable"],
            o.get("published_on"), o.get("observed_at_utc"),
            o.get("element_epoch_utc"),
        )
        if signature in observation_signatures:
            raise ValueError(f"duplicate source/table observation with new ID: {oid}")
        observation_signatures.add(signature)
        if o["source_id"] not in sources:
            raise ValueError(f"orphan observation source: {oid}")
        src = sources[o["source_id"]]
        if o["source_independence_family"] != src["source_family"]:
            raise ValueError(f"source lineage mismatch: {oid}")
        if o.get("published_on") != src.get("published_on"):
            raise ValueError(f"observation/source publication mismatch: {oid}")
        if o.get("link_status") != "CONNECTED_PENDING_CALIBRATION":
            raise ValueError(f"unvalidated evidence link status: {oid}")
        families.add(src["source_family"])
        upstream.add(src.get("upstream_tracking_family", src["source_family"]))
        if o["forward_operator_id"] not in ops:
            raise ValueError(f"unmapped forward operator: {oid}")
        if o["unit"] not in CANONICAL:
            raise ValueError(f"unknown physical unit: {oid}")
        if src["source_family"] == "NASA_GODDARD_COMPILED_FROM_TRACKING":
            # The four SSR columns have distinct units/operators. A relabeled
            # column or a state/epoch borrowed from another object/date must
            # not count as a new model-connected measurement.
            expected = NASA_SSR_FIELDS.get(o["observable"])
            if expected is None or (o["forward_operator_id"], o["unit"]) != expected:
                raise ValueError(f"mismatched SSR observable/operator/unit: {oid}")
            if o["object_id"] not in (527, 529):
                raise ValueError(f"invalid SSR object link: {oid}")
            expected_inputs = [
                f"state_{o['object_id']}_at_t",
                f"t_observed_{o['object_id']}_{src['published_on']}",
            ]
            if o.get("input_parameters") != expected_inputs:
                raise ValueError(f"cross-object or cross-publication SSR parameter link: {oid}")
        if not o.get("input_parameters") or any(p not in params for p in o["input_parameters"]):
            raise ValueError(f"orphan parameter link: {oid}")
        number = o["value"]
        if isinstance(number, bool) or not isinstance(number, (int, float)) or not math.isfinite(number):
            raise ValueError(f"non-finite reported measurement: {oid}")
        if o["observed_at_utc"] is None and "observed_epoch" not in o["pending"]:
            raise ValueError(f"missing epoch not tracked: {oid}")
        if o["measurement_error"] is None and "error_interval" not in o["pending"]:
            raise ValueError(f"unknown uncertainty not tracked: {oid}")
        if src["source_family"] == NASA_SSR_FAMILY:
            if o.get("observed_at_utc") is not None or o.get("measurement_error") is not None:
                raise ValueError(f"unverified SSR epoch/error promoted: {oid}")
            if (o.get("reference_definition") != "UNRESOLVED_FROM_SOURCE_TABLE" or
                not {"observed_epoch", "error_interval", "forward_model_validation",
                     "source_row_facsímile_recheck"}.issubset(o.get("pending", []))):
                raise ValueError(f"missing unresolved SSR caveats: {oid}")
        if not o.get("matrix_local_id") or not o.get("source_independence_family"):
            raise ValueError(f"missing evidence lineage: {oid}")
        if o["constraint_status"] != PENDING:
            if o["observed_at_utc"] is None or o["measurement_error"] is None or o["pending"]:
                raise ValueError(f"cannot activate an underdetermined constraint: {oid}")
            raise ValueError(f"active scientific constraints require a separately validated physical solver: {oid}")
        canonical_unit, factor = CANONICAL[o["unit"]]
        canonical_value = number * factor
        if not math.isfinite(canonical_value):
            raise ValueError(f"non-finite canonical converted measurement: {oid}")
        output.append({
            "observation": oid,
            "evidence": o["matrix_local_id"],
            "source": o["source_id"],
            "independence_family": src["source_family"],
            "model_variable": o["variable_id"],
            "operator": o["forward_operator_id"],
            "input_parameters": o["input_parameters"],
            "reported_value": number,
            "reported_unit": o["unit"],
            "canonical_value": canonical_value,
            "canonical_unit": canonical_unit,
            "observed_at_utc": o["observed_at_utc"],
            "element_epoch_utc": o.get("element_epoch_utc"),
            "measurement_error": o["measurement_error"],
            "pending": o["pending"],
            "status": PENDING,
        })
    # Accumulate comparisons between published records without treating
    # publication timestamps as physical observation epochs.
    derived_ids = set()
    compared_pairs = set()
    for edge in graph.get("derived_connections", []):
        edge_id = edge.get("id")
        if not isinstance(edge_id, str) or not edge_id or edge_id in ids or edge_id in derived_ids:
            raise ValueError(f"duplicate or invalid derived edge ID: {edge_id}")
        derived_ids.add(edge_id)
        if edge.get("operator_id") != "difference_between_published_values":
            raise ValueError(f"unexpected derived operator: {edge_id}")
        inputs = edge.get("inputs", [])
        if len(inputs) != 2 or any(item not in ids for item in inputs):
            raise ValueError(f"orphan derived edge: {edge_id}")
        pair = frozenset(inputs)
        if len(pair) != 2 or pair in compared_pairs:
            raise ValueError(f"duplicate derived observation pair: {edge_id}")
        compared_pairs.add(pair)
        left, right = (next(o for o in obs if o["id"] == item) for item in inputs)
        if left["object_id"] != right["object_id"] or left["observable"] != right["observable"]:
            raise ValueError(f"mixed comparison: {edge_id}")
        if left["unit"] != right["unit"] or edge.get("unit") != left["unit"]:
            raise ValueError(f"mixed units in derived comparison: {edge_id}")
        reported_delta = edge.get("derived_arithmetic")
        if (isinstance(reported_delta, bool) or not isinstance(reported_delta, (int, float))
                or not math.isfinite(reported_delta)):
            raise ValueError(f"non-finite or nonnumeric derived arithmetic: {edge_id}")
        delta = right["value"] - left["value"]
        if abs(delta - reported_delta) > 1e-8:
            raise ValueError(f"invalid arithmetic or unit: {edge_id}")
        if edge.get("status") != "CONNECTED_PENDING_EPOCH_AND_COVARIANCE":
            raise ValueError(f"comparison prematurely turned into a physical trend: {edge.get('id')}")
        if "source_specific_observation_epochs" not in edge.get("missing", []):
            raise ValueError(f"missing time caveat in comparison: {edge.get('id')}")
        if not {"correlated_source_errors", "validated_forward_model"}.issubset(edge.get("missing", [])):
            raise ValueError(f"missing covariance/model caveat: {edge_id}")
        if edge.get("physical_interpretation") != (
            "Difference between published tabulated values, NOT a measured time derivative or causal atmospheric trend."
        ):
            raise ValueError(f"derived comparison claimed physical trend: {edge_id}")
    for edge in graph.get("couplings", []):
        if not edge["parameters"] or any(p not in params for p in edge["parameters"]):
            raise ValueError(f"orphan coupling: {edge['id']}")
        if edge.get("hard_constraint_active"):
            raise ValueError(f"unvalidated coupling active: {edge['id']}")
    checked_bridges = validate_528_tle_bridge(graph, sources, obs)
    from texugo_ssr_facsimile_erratum import reconcile_handoff
    return reconcile_handoff(graph, {
        "schema": "conde.cumulative-constraint-handoff/v1",
        "input_observations": len(obs),
        "connected_observations": len(output),
        "unique_source_families": len(families),
        "upstream_tracking_families": len(upstream),
        "latent_parameters": len(params),
        "candidate_constraints_recorded": len(output),
        "derived_connections_recorded": len(graph.get("derived_connections", [])),
        "physical_bridges_recorded": len(checked_bridges),
        "physical_bridges": checked_bridges,
        "constraints_activated": 0,
        "physical_domain_status": "PENDING_CALIBRATION_NOT_DISCARDED",
        "observations": output,
        "couplings": graph.get("couplings", []),
        "derived_connections": graph.get("derived_connections", []),
        "next_action": "Resolve epochs/error/forward operators; then activate interval constraints and cross-check independent 527/529 holdouts.",
    })


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=DEFAULT)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    validated = validate(json.loads(args.input.read_text(encoding="utf-8")))
    result = json.dumps(validated, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8")
    print(json.dumps({
        "connected": validated["connected_observations"],
        "candidate": validated["candidate_constraints_recorded"],
        "derived_connections": validated["derived_connections_recorded"],
        "activated": validated["constraints_activated"],
        "status": validated["physical_domain_status"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
