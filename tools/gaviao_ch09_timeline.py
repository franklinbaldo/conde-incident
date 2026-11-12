#!/usr/bin/env python3
"""Independent C241-T7 calendar audit: never a physical orbit fit or impact forecast."""
import argparse
import hashlib
import io
import math
from datetime import datetime, timedelta, timezone
from urllib.request import urlopen

SOURCE = "https://huggingface.co/datasets/oxzoid/space-track-tle-history/resolve/4b4fb3a/data/tle_1963.parquet"
SOURCE_SHA = "c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09"
STORY_SHA = "77f7faad20d839863e1b3650ebe63f8dae9801f8"
STORY_BLOB = "abefabf2dbf942bafd56ca83da25e1506f9e3e65"
STORY_URL = "https://raw.githubusercontent.com/franklinbaldo/conde-incident/" + STORY_SHA + "/stories/2026-11-12-o-rastro-que-pulava-semanas.md"
UTC = timezone.utc
DAY_US = 86400000000

def delta_us(a, b):
    d = b - a
    return ((d.days * 86400 + d.seconds) * 1000000 + d.microseconds)

def git_blob_sha1(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def get_bytes(url):
    if url not in (SOURCE, STORY_URL):
        raise ValueError("non-pinned URL")
    with urlopen(url, timeout=50) as r:
        return r.read()

def select_rows(records):
    chosen = []
    for i, record in enumerate(records):
        if record.get("norad_id") != 528:
            continue
        ep, angle = record.get("epoch"), record.get("raan")
        if not isinstance(ep, datetime) or ep.tzinfo is None:
            raise ValueError("missing timezone")
        ep = ep.astimezone(UTC)
        if ep.year != 1963:
            raise ValueError("wrong year")
        if isinstance(angle, bool) or not isinstance(angle, (float, int)) or not math.isfinite(angle) or not 0 <= angle < 360:
            raise ValueError("invalid RAAN")
        chosen.append((i, ep, float(angle)))
    return chosen

def calculate(rows, required_count=None):
    if required_count is not None and len(rows) != required_count:
        raise ValueError("record count changed")
    if len(rows) < 2:
        raise ValueError("insufficient epochs")
    if len({x[0] for x in rows}) != len(rows):
        raise ValueError("reused source row")
    for _, ep, angle in rows:
        if not isinstance(ep, datetime) or ep.tzinfo is None or ep.utcoffset() != timedelta(0) or ep.year != 1963:
            raise ValueError("invalid UTC epoch")
        if not math.isfinite(angle) or not 0 <= angle < 360:
            raise ValueError("invalid RAAN")
    ordered = sorted(rows, key=lambda x: (x[1], x[0]))
    gaps = [(delta_us(a[1], b[1]), a, b) for a, b in zip(ordered, ordered[1:])]
    if any(d <= 0 for d, _, _ in gaps):
        raise ValueError("duplicate/conflicting epoch")
    maximum = max(gaps, key=lambda x: x[0])
    last = ordered[-1][1]
    november8 = datetime(1963, 11, 8, tzinfo=UTC)
    if last >= november8:
        raise ValueError("secondary source not October-ending")
    return {
        "samples": len(ordered),
        "intervals": len(gaps),
        "over72h": sum(d > 72 * 3600000000 for d, _, _ in gaps),
        "atmost24h": sum(d <= 24 * 3600000000 for d, _, _ in gaps),
        "maxgap_us": maximum[0],
        "max_from": maximum[1][0],
        "max_to": maximum[2][0],
        "max_from_epoch": maximum[1][1],
        "max_to_epoch": maximum[2][1],
        "last_epoch": last,
        "calendar_start_us": delta_us(last, november8),
        "calendar_end_us": delta_us(last, november8 + timedelta(days=1)),
    }

def editorial_guards(text):
    required = (
        'chapter: "09"', "C241-T7", "32 ultrapassam três dias", "23,53529262",
        "27 de outubro de 1963", "11,38870217", "12,38870217",
        "fonte secundária", "não a cratera ou a queda",
        "não é uma janela física", "não oferece uma premissa física autenticada",
        "H-arquivo", "H-cobertura limitada",
        "nenhum domínio histórico de parâmetros foi reduzido",
        "19640001198.pdf", "EOP-UAP-D001_NASC-Inquiry-into-Bahia",
    )
    return ["missing statement: " + phrase for phrase in required if phrase.casefold() not in text.casefold()]

def audit_online():
    payload = get_bytes(SOURCE)
    if hashlib.sha256(payload).hexdigest() != SOURCE_SHA:
        raise ValueError("Parquet SHA-256 changed")
    import pyarrow.parquet as pq
    table = pq.read_table(io.BytesIO(payload), columns=["norad_id", "epoch", "raan"])
    r = calculate(select_rows(table.to_pylist()), required_count=45)
    for k, v in (("samples", 45), ("intervals", 44), ("over72h", 32),
                 ("atmost24h", 3), ("max_from", 2978), ("max_to", 2979)):
        if r[k] != v:
            raise ValueError("independent counter mismatch: " + k + ": " + str(r[k]))
    if round(r["maxgap_us"] / DAY_US, 8) != 23.53529262:
        raise ValueError("max gap mismatch")
    if r["max_from_epoch"].date().isoformat() != "1963-02-06" or r["max_to_epoch"].date().isoformat() != "1963-03-01":
        raise ValueError("largest gap endpoints mismatch")
    if r["last_epoch"].isoformat() != "1963-10-27T14:40:16.132512+00:00":
        raise ValueError("last catalog epoch mismatch")
    if round(r["calendar_start_us"] / DAY_US, 8) != 11.38870217 or round(r["calendar_end_us"] / DAY_US, 8) != 12.38870217:
        raise ValueError("calendar bounds mismatch")
    story = get_bytes(STORY_URL)
    if git_blob_sha1(story) != STORY_BLOB:
        raise ValueError("Git story blob changed")
    missed = editorial_guards(story.decode("utf-8"))
    if missed:
        raise ValueError("; ".join(missed))
    return r

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pinned", action="store_true", required=True)
    p.parse_args()
    r = audit_online()
    print("PASS C241-T7 independent secondary-calendar reproduction")
    print({k: v for k, v in r.items() if not isinstance(v, datetime)})
    print("WARNING: NASA day lacks verified clock/zone; UTC day endpoints are a calculation convention, not a decay window")
    print("UNVERIFIED: primary NORAD custody, physical frame/error, Lean orbital domain, trajectory, impact")

if __name__ == "__main__":
    main()
