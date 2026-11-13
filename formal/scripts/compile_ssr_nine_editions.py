#!/usr/bin/env python3
"""C241-P20: exact minimax of a *publication-offset* nuisance model.

Nine NASA Goddard SSR compilations, not nine tracking epochs or sensors. Reuse
C241-L27's cross-ledger checks, independently lock every published cell and
compute a certificate for all 23 entries; never filter orbital domain Theta.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from decimal import Decimal

from tools import tle_ssr_editions_precision_audit as audit

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = audit.ROOT / audit.MODEL
DECAY_PATH = audit.ROOT / audit.DECAY
REPORT = ROOT / "research/constraints/C241-P20_ssr_nine_edition_minimax.json"
LEAN = ROOT / "formal/Conde1963/SsrNineEditions.lean"
# Publication, NTRS, PDF hash (claimed by custodial ledger), 527/528/529 printed
# periods in centiminutes. Explicit locks reject a coordinated ledger mutation.
LOCKS = (
    ("1963-04-30", "19630012128", "87b8c1be1d074dff4b605b422f6a8836c2ebdf80ca4ac0568373b168cc457a38", (9460, 9410, 9430)),
    ("1963-06-30", "19630012130", "8add4b46734e992a213088ef58ba9d58b6385df7b89bb504f79fe8715ec418f3", (9460, 9370, 9400)),
    ("1963-07-31", "19630012290", "9b00bf8323b1de80a34920f73c658f70f766a51632a13473a408679f0e5a03d9", (9460, 9360, 9390)),
    ("1963-08-15", "19630012289", "4e5cb0205577bc1b0959088db9ca3ae7a05f8de480b5ece9b86c385437636968", (9460, 9330, 9380)),
    ("1963-10-15", "19640000428", "fe5183940081fbbfe1e791b8cf47c1ac2c08ecad0c17f5d54d7cac83fb5992b2", (9460, 9240, 9330)),
    ("1963-11-15", "19640001198", "0f27ed20f8428e44e8dd1f5d4e932661b01a0f8188aaddcae1360ea128336674", (9460, None, 9260)),
    ("1963-11-30", "19640002493", "9f2b6973117bb709bd26893a90e42b170e58f245c0fa11370ab26cfda3b0d94d", (9460, None, 9220)),
    ("1963-12-15", "19640003479", "d31a064f8e03fd39be6fe75b88cd5852c0b74c9101fa635cb40ac25c77ef474f", (9460, None, 9160)),
    ("1963-12-31", "19640005618", "d9504a8641baa65c208e41034e77b0e9b1cc01b4acb2a4f95541bd9e75d3783d", (9460, None, 8920)),
)
OBJECTS = (527, 528, 529)


def source_rows(model=None, ledgers=None, decay=None):
    if model is None:
        model = audit.read(audit.MODEL)
    if ledgers is None:
        ledgers = {d["ledger"]: audit.read(d["ledger"]) for d in model["docs"]}
    if decay is None:
        decay = audit.read(audit.DECAY)
    result = audit.validate(model, ledgers, decay)
    if len(model["docs"]) != len(LOCKS):
        raise ValueError("nine editions required")
    cells = {}
    sources = []
    for doc, (date, ntrs, sha, periods) in zip(model["docs"], LOCKS):
        if (doc["published"], doc["ntrs"], doc["pdf_sha256"]) != (date, ntrs, sha):
            raise ValueError("edited publication, NTRS or source SHA")
        sources.append({"publication": date, "ntrs": ntrs, "pdf_sha256_from_ledger": sha,
                        "source_ledger": doc["ledger"], "page": doc["printed_page"]})
        for obj, value in zip(OBJECTS, periods):
            if value is not None:
                cells[(obj, date)] = value
    if len(cells) != 23 or len(result["rows"]) != 23:
        raise ValueError("unexpected cell membership")
    for row in result["rows"]:
        obj, date = row["norad_id_secondary_crosswalk"], row["publication_day_NOT_sensor_epoch"]
        key = (obj, date)
        got = int(Decimal(row["printed"]["nodal_period_min"]) * 100)
        if key not in cells or cells[key] != got:
            raise ValueError("printed cell or identity changed")
        if (row["instrument_observation_epoch"] is not None
            or row["instrument_sigma"] is not None
            or row["instrument_sensor"] is not None
            or row["printed_precision_is_instrument_accuracy"]):
            raise ValueError("instrumental claim leaked into print-only model")
    return cells, sources


def feasible(cells: dict[tuple[int, str], int], radius: int):
    """Bellman-Ford difference constraints: p_ij=B_i+H_j+e_ij, |e|<=E.

    Let u_i=B_i, v_j=-H_j. Each printed cell yields two directed edges;
    negative cycles refute radius E. Distances give an exact integer witness.
    """
    if not cells or radius < 0:
        return None
    objs = sorted({o for o, _ in cells})
    dates = sorted({d for _, d in cells})
    ids_obj = {o: i for i, o in enumerate(objs)}
    ids_date = {d: i + len(objs) for i, d in enumerate(dates)}
    edges = []
    for (o, d), y in sorted(cells.items()):
        if type(y) is not int:
            raise ValueError("printed period must be integral centiminutes")
        i, j = ids_obj[o], ids_date[d]
        edges.extend(((j, i, y + radius), (i, j, radius - y)))
    dist = [0] * (len(objs) + len(dates))
    for _ in range(len(dist)):
        changed = False
        for u, v, weight in edges:
            if dist[v] > dist[u] + weight:
                dist[v] = dist[u] + weight
                changed = True
        if not changed:
            # Gauge fix for readable numbers. All residuals are invariant.
            shift = cells[(objs[0], dates[0])] - dist[ids_obj[objs[0]]]
            bases = {o: dist[ids_obj[o]] + shift for o in objs}
            biases = {d: -dist[ids_date[d]] - shift for d in dates}
            residuals = {(o, d): y - bases[o] - biases[d]
                         for (o, d), y in cells.items()}
            assert all(abs(v) <= radius for v in residuals.values())
            return bases, biases, residuals
    return None


def minimize(cells):
    lo, hi = 0, max(cells.values()) - min(cells.values())
    if feasible(cells, hi) is None:
        raise ValueError("unexpected inconsistent constraint graph")
    while lo < hi:
        mid = (lo + hi) // 2
        if feasible(cells, mid) is None:
            lo = mid + 1
        else:
            hi = mid
    result = feasible(cells, lo)
    assert result is not None and (lo == 0 or feasible(cells, lo - 1) is None)
    return lo, result


def build(model=None, ledgers=None, decay=None):
    cells, sources = source_rows(model, ledgers, decay)
    radius, (bases, biases, residuals) = minimize(cells)
    # Independent lower-bound certificate: gap(527-529) Apr=30, Dec=540,
    # so 4E >= 510; for integral centiminutes E >= ceil(510/4)=128.
    first, last = LOCKS[0][0], LOCKS[-1][0]
    if (cells[527, first] - cells[529, first],
        cells[527, last] - cells[529, last], radius) != (30, 540, 128):
        raise ValueError("sharp two-publication contrast changed")
    if len(cells) != 23 or len(sources) != 9:
        raise ValueError("source set changed")
    return {
        "schema": "conde.ssr-nine-edition-additive-minimax/v1", "id": "C241-P20",
        "parent_evidence": ["C241-L27", "C241-P16", "C241-P19"],
        "sources": sources,
        "model": "printed_p(obj,publication) = baseline_obj + offset_publication + residual",
        "unit": "centiminute (0.01 minute)", "printed_rows": [
            {"object": obj, "publication": day, "period_centiminute": value,
             "residual_centiminute": residuals[obj, day]}
            for (obj, day), value in sorted(cells.items())],
        "minimum_uniform_error_centiminute": radius,
        "minimum_uniform_error_seconds": "76.8",
        "certifying_contrast": {"objects": [527, 529], "publications": [first, last],
                               "printed_gap_centiminute": [30, 540],
                               "gap_change_centiminute": 510,
                               "certificate": "4*E >= 510; integer E >= 128"},
        "attaining_witness": {"object_baselines_centiminute": bases,
                              "edition_offsets_centiminute": biases},
        "print_half_step_if_nearest_rounding_centiminute": 5,
        "independent_instrument_observations_added": 0,
        "tracking_epochs": None, "sensor_sigma": None, "physical_domain": "THETA_UNCHANGED",
        "interpretation": "Rejects ONLY the shared additive editorial offset with residual <=1.27 min; not real instrument error, decay physics or location.",
        "dec31_528_absent_not_zero": True,
    }


def render_lean(r):
    rows = r["printed_rows"]
    bases = r["attaining_witness"]["object_baselines_centiminute"]
    offsets = r["attaining_witness"]["edition_offsets_centiminute"]
    dates = [item[0] for item in LOCKS]
    hnames = {d: "h" + d[5:].replace("-", "") for d in dates}
    terms = []
    for c in rows:
        val, obj, d = c["period_centiminute"], c["object"], c["publication"]
        expr = f"({val} - b{obj} - {hnames[d]})"
        terms.append(f"(-128 ≤ {expr} ∧ {expr} ≤ 128)")
    types = " ".join(f"{n}" for n in ["b527", "b528", "b529", *hnames.values()])
    witness = ", ".join(map(str, [*[bases[o] for o in OBJECTS], *[offsets[d] for d in dates]]))
    joined = " ∧\n      ".join(terms)
    return f'''import Lean

namespace Conde1963.SsrNineEditions

/-! C241-P20: 23 printed period cells of nine compiled NASA SSR publications.
Publication date is NOT instrument epoch, and no error below is sensor σ.
The 528 is absent from four late in-orbit lists, never assigned zero.
This proof is conditional on the explicit common-additive editorial model;
it does not restrict any physical orbit or location (Theta unchanged). -/

/-- April and December 527-minus-529 printed gaps differ by 510 centimin.
Four bounded residual terms must absorb that difference; E is integral. -/
theorem nine_edition_lower_bound
    (b527 b529 hApr hDec eaApr eaDec ecApr ecDec E : Int)
    (aApr : 9460 = b527 + hApr + eaApr)
    (aDec : 9460 = b527 + hDec + eaDec)
    (cApr : 9430 = b529 + hApr + ecApr)
    (cDec : 8920 = b529 + hDec + ecDec)
    (aAprLo : -E ≤ eaApr) (aAprHi : eaApr ≤ E)
    (aDecLo : -E ≤ eaDec) (aDecHi : eaDec ≤ E)
    (cAprLo : -E ≤ ecApr) (cAprHi : ecApr ≤ E)
    (cDecLo : -E ≤ ecDec) (cDecHi : ecDec ≤ E)
    : 128 ≤ E := by
  omega

/-- The exact bound is attained *simultaneously* by all 23 printed cells,
with one baseline per object and one shared bias per edition. -/
theorem nine_edition_witness :
    ∃ ({types} : Int),
      {joined} := by
  refine ⟨{witness}, ?_⟩
  omega

end Conde1963.SsrNineEditions
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build()
    payload = json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    lean = render_lean(report)
    if args.check:
        if not REPORT.exists() or REPORT.read_text() != payload:
            raise SystemExit("C241-P20 report differs from source locks")
        if not LEAN.exists() or LEAN.read_text() != lean:
            raise SystemExit("C241-P20 Lean differs from source locks")
        print("C241-P20 checked: 9 editions, 23 cells, E=128, no Theta activation")
    else:
        REPORT.write_text(payload)
        LEAN.write_text(lean)
        print("C241-P20 generated: 9 editions, 23 cells, E=128")


if __name__ == "__main__":
    main()
