"""NASA 1963 SSR facsimile QA: corrected handoff, frozen legacy source preserved.

Original NASA pages: 15 Nov https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=7
30 Nov https://ntrs.nasa.gov/api/citations/19640002493/downloads/19640002493.pdf#page=7
Both: printed page 5, PDF zero-index 6. 3A/3C -> NORAD 527/529 is
the existing catalogue crosswalk, NOT a NORAD number printed on either page.
NASA editions share upstream NORAD/AFS tracking, not independent sensors.
"""
import math

TABLE = {
    ("NASA-SSR-1963-11-15", 527): (94.6, 81.88, 536, 455),
    ("NASA-SSR-1963-11-15", 529): (92.6, 81.87, 420, 376),
    ("NASA-SSR-1963-11-30", 527): (94.6, 81.88, 533, 459),
    ("NASA-SSR-1963-11-30", 529): (92.2, 81.86, 390, 368),
}
FIELDS = ("nodal_period", "inclination", "apogee", "perigee")
ERRATUM = ("NASA-SSR-1963-11-30", 527, "nodal_period")
DELTA_ID = "SSR-PUBLICATIONS-DELTA-527-nodal_period"
ROW_ID = "SSR-1963-11-30-NORAD527-nodal_period"


def reconcile_handoff(graph: dict, handoff: dict) -> dict:
    """Validate sixteen scanned table cells and correct ONLY the derived handoff.

    The 38-kB input JSON is frozen by the 20-kB immutable-legacy rule.
    Its 94.8 and +0.2 were transcription errors, not measurements.
    """
    expected = {(src, obj, col): val for (src, obj), vals in TABLE.items()
                for col, val in zip(FIELDS, vals)}
    found = {}
    for o in graph["observations"]:
        if o["source_id"] not in {k[0] for k in TABLE}:
            continue
        key = (o["source_id"], o["object_id"], o["observable"])
        if key in found:
            raise ValueError("NASA facsimile duplicate table cell")
        found[key] = o["value"]
    if set(found) != set(expected):
        raise ValueError("NASA facsimile incomplete table")
    # A renamed source row must not evade the erratum while still appearing
    # as a new, uncorrected historical observation in the exported handoff.
    for o in graph["observations"]:
        if o["source_id"] not in {key[0] for key in TABLE}:
            continue
        edition = o["source_id"].removeprefix("NASA-SSR-")
        pinned_id = f"SSR-{edition}-NORAD{o['object_id']}-{o['observable']}"
        if o["id"] != pinned_id:
            raise ValueError("NASA facsimile row identity mismatch: " + str(o["id"]))
    for key, value in found.items():
        frozen_value = 94.8 if key == ERRATUM else expected[key]
        if type(value) not in (int, float) or not math.isfinite(value) or value != frozen_value:
            raise ValueError("NASA facsimile source-value mismatch: " + str(key))
    delta = [d for d in graph["derived_connections"] if d["id"] == DELTA_ID]
    if len(delta) != 1 or delta[0]["derived_arithmetic"] != 0.2:
        raise ValueError("NASA facsimile legacy difference mismatch")
    # The corrected export must contain all sixteen inspected cells exactly
    # once, plus the edited delta; otherwise its audit status is misleading.
    pinned_rows = {
        f"SSR-{src.removeprefix('NASA-SSR-')}-NORAD{obj}-{col}"
        for src, obj, col in expected
    }
    actual_rows = [r["observation"] for r in handoff["observations"]
                   if r.get("source") in {key[0] for key in TABLE}]
    if set(actual_rows) != pinned_rows or len(actual_rows) != len(pinned_rows):
        raise ValueError("NASA facsimile handoff row set mismatch")
    if sum(edge.get("id") == DELTA_ID for edge in handoff["derived_connections"]) != 1:
        raise ValueError("NASA facsimile handoff delta missing or duplicated")
    result = dict(handoff)
    result["observations"] = []
    for row in handoff["observations"]:
        if row["observation"] == ROW_ID:
            row = dict(row, reported_value=94.6, canonical_value=5676.0)
        result["observations"].append(row)
    result["derived_connections"] = [
        dict(edge, derived_arithmetic=0.0) if edge["id"] == DELTA_ID else edge
        for edge in handoff["derived_connections"]
    ]
    result["facsimile_audit"] = {
        "id": "QA-TX-20261112-07", "directly_inspected_rows": 16,
        "primary_document_pages": "both PDF index 6, printed p.5",
        "correction": "30-Nov 1963 3A 94.8 -> 94.6 min; delta +0.2 -> 0",
        "legacy_input_blob_preserved": True,
        "tracking_epoch_and_covariance": "UNKNOWN",
        "independence": "SHARED_NORAD_AFS_UPSTREAM",
        "physical_domain_reduction": "NONE",
    }
    return result
