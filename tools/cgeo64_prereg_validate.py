"""CGEO-64 preregistration guard. No remote sources or claims of observed outcomes."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research/editorial/cgeo64_null_narrative_prereg_20261114.json"
FROZEN_GIT_BLOB = "0d13d9359080699e5f8402ca9b7014d7f1f6d59a"
IDS = (
    "F01_METAL_SPHERE", "F02_CITY_CENTER", "F03_FOUR_METER_HOLE",
    "F04_WINDOWS", "F05_THICK_GLASS", "F06_HUMAN_BODY",
    "F07_HEAVY_CLOTHES", "F08_INDECIPHERABLE_INSCRIPTIONS",
)
WEEKS = {
    "TARGET_NOV04": ("target", "1963-11-04"),
    "CONTROL_OCT07": ("baseline", "1963-10-07"),
    "CONTROL_OCT14": ("baseline", "1963-10-14"),
    "CONTROL_OCT21": ("baseline", "1963-10-21"),
    "CONTROL_DEC02": ("post_event_sensitivity_only", "1963-12-02"),
}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def git_blob_sha(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode("ascii")
    return hashlib.sha1(header + raw).hexdigest()


def validate(d: dict) -> int:
    require(d.get("type") == "NarrativeHypothesisPreregistration", "contract type")
    require(d.get("id") == "CGEO-64", "contract identity")
    require(d.get("status") == "FROZEN_DESIGN_NOT_SEARCHED", "pre-search status")
    require(d.get("issue") == "https://github.com/franklinbaldo/conde-incident/issues/887", "issue")
    f = d.get("frozen_fbis_fragments", [])
    require([x.get("id") for x in f] == list(IDS), "frozen fragments")
    require(all(x.get("kind") == "fbis_translated_report" for x in f), "fragment source class")
    require(all(x.get("search_anchor_pt") and x.get("search_anchor_en") for x in f), "search anchors")
    src = d.get("source_lineage", {})
    require(src.get("literal_portuguese_quote_authenticated") is False, "FBIS is English translation")
    require("EOP-UAP-D001" in src.get("fbis_facsimile_url", ""), "FBIS source")
    sampling = d.get("sampling", {})
    require(sampling.get("target_event_date") == "1963-11-08", "event day")
    pubs = sampling.get("publications", [])
    require([p.get("id") for p in pubs] == ["UH_RE", "JB_RJ"], "preselected corpus")
    require(all(p.get("issue_number_for_unknown_dates") is None for p in pubs), "invented issue number")
    weeks = sampling.get("weeks", [])
    require({w.get("id") for w in weeks} == set(WEEKS) and len(weeks) == 5, "weeks changed")
    seen = set()
    for w in weeks:
        role, start = WEEKS[w["id"]]
        dates = [(dt.date.fromisoformat(start) + dt.timedelta(days=i)).isoformat() for i in range(5)]
        require((w.get("role"), w.get("start"), w.get("end"), w.get("dates")) ==
                (role, start, dates[-1], dates), "day-slot change")
        require(dt.date.fromisoformat(start).weekday() == 0, "non-Monday start")
        require(not (seen & set(dates)), "overlapping windows")
        seen.update(dates)
        if role == "baseline":
            require(dates[-1] < "1963-11-08", "post-event baseline contamination")
    require("403" in sampling.get("predefined_access_failure", ""), "access-failure policy")
    result = d.get("result_template", {})
    require(result.get("completed_search") is False, "search cannot predate freeze")
    require(result.get("observations") == [] and result.get("coverage_by_slot") == [], "premature observations")
    require(result.get("first_pre_event_occurrence") is None and
            result.get("baseline_rates") is None and result.get("verdicts") is None,
            "invented results")
    scope = d.get("causal_scope", {})
    require(scope.get("historical_center_1963") is None and
            scope.get("physical_reentry_location") is None and
            scope.get("active_orbital_constraint") is False and
            scope.get("physical_reentry_excluded") is False and
            scope.get("accusation_of_fraud") is False, "physical claim or accusation")
    return sum(len(w["dates"]) for w in weeks) * len(pubs)


def load_and_verify() -> dict:
    raw = DATA.read_bytes()
    require(git_blob_sha(raw) == FROZEN_GIT_BLOB, "frozen JSON changed after preregistration")
    data = json.loads(raw)
    validate(data)
    return data


if __name__ == "__main__":
    data = load_and_verify()
    print(f"CGEO-64 preregistration PASS; git_blob={FROZEN_GIT_BLOB}; "
          f"slots={validate(data)}; observed=0; orbital_constraint=false")
