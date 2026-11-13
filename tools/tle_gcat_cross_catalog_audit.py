#!/usr/bin/env python3
"""C241-L14: cross-check mutable GCAT catalog wording; no raw tracking data."""
import argparse
import hashlib
import json
import re
from pathlib import Path

URLS = {
    "currentcat": "https://planet4589.org/space/gcat/data/derived/currentcat.html",
    "satcat": "https://planet4589.org/space/gcat/data/cat/satcat.html",
}
PIECES = {"00527": "1963-003A", "00528": "1963-003B", "00529": "1963-003C"}
LABEL = "deb USAF satellite/Agena D"


def unique_rows(raw, source):
    """Read source bytes, require one explicit NORAD/COSPAR pairing per target."""
    if source not in URLS:
        raise ValueError("unsupported catalog")
    text = raw.decode("utf-8")
    if not text.lstrip().startswith("<") and "JCAT" not in text[:5000]:
        raise ValueError("catalog header missing")
    rows = {}
    for number, cospar in PIECES.items():
        matched = []
        for line in text.splitlines():
            if not re.match(r"^\s*S" + number + r"\s+" + number + r"\s+", line):
                continue
            if re.search(r"\b" + re.escape(cospar) + r"\b", line):
                matched.append(line.strip())
        if len(matched) != 1:
            raise ValueError(f"{source}:{number}: expected one row, got {len(matched)}")
        rows[number] = matched[0]
    return rows


def audit(catalog_bytes):
    """No independence assumption: both tables are GCAT, not two sensors."""
    if set(catalog_bytes) != set(URLS):
        raise ValueError("both catalog inputs required")
    rows = {kind: unique_rows(raw, kind) for kind, raw in catalog_bytes.items()}
    for kind, entries in rows.items():
        if not re.search(r"\bA00324\b", entries["00527"]):
            raise ValueError(f"{kind}:527 missing Agena B parent A00324")
        for number in ("00528", "00529"):
            row = entries[number]
            if not re.search(r"\bC\b", row):
                raise ValueError(f"{kind}:{number}:component class absent")
            if LABEL not in row:
                raise ValueError(f"{kind}:{number}:debris label changed")
            if not re.search(r"\bS00527\b", row):
                raise ValueError(f"{kind}:{number}:parent 527 absent")
    if "Agena B 2313" not in rows["currentcat"]["00527"]:
        raise ValueError("527 currentcat missing Agena B parent description")
    if not re.search(r"\b1963\s+Nov\s+8\b", rows["currentcat"]["00528"]):
        raise ValueError("528 civil catalog decay date changed")
    return {
        "record_id": "C241-L14",
        "source_capture": {
            kind: {"url": URLS[kind], "sha256": hashlib.sha256(raw).hexdigest(),
                   "bytes": len(raw), "jcat_rows": rows[kind]}
            for kind, raw in catalog_bytes.items()
        },
        "pairs": [{"norad": k, "cospar": v} for k, v in PIECES.items()],
        "catalogue_527_parent": "A00324 / Agena B 2313",
        "catalogue_528_529_text": LABEL,
        "catalogue_name_mismatch": True,
        "proves_wrong_hardware": False,
        "physical_component_528": None,
        "physical_component_529": None,
        "raw_tle_527_529": None,
        "historical_tle_checksums": None,
        "instrument_frame": None,
        "instrument_sigma": None,
        "tracking_independence": "NOT_ESTABLISHED",
        "catalog_decay_day_is_terminal_time": False,
        "raan_2841520_primary": False,
        "raan_1985261_primary": False,
        "graph_state": "CONNECTED_PENDING_CALIBRATION",
        "lean_physical_constraint": "NOT_PROMOTED",
        "conde_outcome": "INDETERMINATE",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--currentcat", required=True, type=Path)
    parser.add_argument("--satcat", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    a = parser.parse_args()
    output = audit({
        "currentcat": a.currentcat.read_bytes(),
        "satcat": a.satcat.read_bytes(),
    })
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) +
                        "\n", encoding="utf-8")
    print("C241-L14: dual GCAT catalog labels verified; identity and orbit remain unknown")


if __name__ == "__main__":
    main()
