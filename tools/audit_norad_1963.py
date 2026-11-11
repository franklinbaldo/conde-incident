#!/usr/bin/env python3
"""Custódia de ESPELHO NUMÉRICO. Não autentica linhas TLE de 1963.

O Parquet não inclui line1/line2: checksum de TLE original fica NOT_RUN.
Este script não fabrica TLE a partir de floats nem produz órbitas/queda.
"""
import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

EXPECTED_SHA256 = "c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09"
SOURCE_URL = (
    "https://huggingface.co/datasets/oxzoid/space-track-tle-history/"
    "resolve/4b4fb3a/data/tle_1963.parquet"
)
IDS = (527, 528, 529)
COLUMNS = (
    "norad_id", "epoch", "inclination", "raan", "eccentricity",
    "arg_perigee", "mean_anomaly", "mean_motion", "mean_motion_dot",
    "bstar", "intl_designator", "altitude_km",
)


def tle_checksum(line: str) -> int:
    """NORAD 69 colunas: dígitos + sinais '-'; apenas integridade sintática."""
    if len(line) != 69 or line[0] not in "12":
        raise ValueError("linha TLE sem 69 colunas/identificador")
    return sum(int(c) if c.isdigit() else 1 if c == "-" else 0 for c in line[:68]) % 10


def validate_raw_tle(first: str, second: str, expected_sat: int) -> dict:
    """Para linhas futuras obtidas da fonte; NÃO criar linhas com o Parquet."""
    if first[0] != "1" or second[0] != "2":
        raise ValueError("par TLE exige linhas 1 e 2")
    if any(tle_checksum(line) != int(line[-1]) for line in (first, second)):
        raise ValueError("checksum TLE inválido")
    a, b = int(first[2:7]), int(second[2:7])
    if a != b or a != expected_sat:
        raise ValueError("NORAD inconsistente")
    if first[18:20] != "63":
        raise ValueError("ano inesperado")
    doy = float(first[20:32])
    if not 1 <= doy < 366:
        raise ValueError("dia de época inválido")
    return {"norad_id": a, "epoch_year": 1963, "epoch_day": doy,
            "raan_deg": float(second[17:25]),
            "eccentricity": float("0." + second[26:33]),
            "mean_motion_rev_day": float(second[52:63]),
            "checksum": "PASS_syntax_only"}


def digest(payload: bytes) -> dict[str, str]:
    return {"sha1": hashlib.sha1(payload).hexdigest(), "sha256": hashlib.sha256(payload).hexdigest()}


def verified_bytes(path: Path) -> bytes:
    payload = path.read_bytes()
    checks = digest(payload)
    if checks["sha256"] != EXPECTED_SHA256:
        raise ValueError(f"parquet SHA256 divergente: {checks['sha256']}")
    if not payload.startswith(b"PAR1") or not payload.endswith(b"PAR1"):
        raise ValueError("assinatura física Parquet inválida")
    return payload


def get_parquet(path: Path, *, download: bool) -> bytes:
    if download:
        if not SOURCE_URL.startswith("https://huggingface.co/"):
            raise ValueError("origem não autorizada")
        # Uma leitura HTTPS sem retry/fallback. A SHA256 impede deriva de conteúdo.
        with urlopen(SOURCE_URL, timeout=45) as response:
            payload = response.read()
        if digest(payload)["sha256"] != EXPECTED_SHA256:
            raise ValueError("download divergente do SHA256 fixado")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    return verified_bytes(path)


def epoch_utc(value: object) -> str:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise ValueError("epoch sem fuso UTC explícito")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def check_numeric(row: dict) -> list[str]:
    failures = []
    for key in COLUMNS[2:10] + ("altitude_km",):
        n = row.get(key)
        if not isinstance(n, (int, float)) or not math.isfinite(n):
            failures.append(key + " não finito/não numérico")
    if failures:
        return failures
    for key, low, high in (("inclination", 0, 180), ("raan", 0, 360),
                           ("eccentricity", 0, 1), ("arg_perigee", 0, 360),
                           ("mean_anomaly", 0, 360)):
        valid = low <= row[key] <= high if key == "inclination" else low <= row[key] < high
        if not valid:
            failures.append(key + " fora de intervalo")
    if row["mean_motion"] <= 0:
        failures.append("mean_motion não positivo")
    return failures


def extract_rows(table) -> tuple[list[dict], dict]:
    missing = set(COLUMNS) - set(table.column_names)
    if missing:
        raise ValueError("colunas ausentes: " + ", ".join(sorted(missing)))
    rows, problems = [], []
    for src_index, raw in enumerate(table.select(COLUMNS).to_pylist()):
        if raw["norad_id"] not in IDS:
            continue
        item = dict(raw)
        item["epoch"] = epoch_utc(item["epoch"])
        if not item["epoch"].startswith("1963-"):
            problems.append({"source_row": src_index, "problem": "época fora de 1963"})
        errors = check_numeric(item)
        if errors:
            problems.append({"source_row": src_index, "norad_id": item["norad_id"], "problems": errors})
        item["source_row"] = src_index
        rows.append(item)
    # Duplicatas e número da linha do Parquet preservados.
    rows.sort(key=lambda r: (r["norad_id"], r["epoch"], r["source_row"]))
    counts = Counter(r["norad_id"] for r in rows)
    unique = {str(i): len({r["epoch"] for r in rows if r["norad_id"] == i}) for i in IDS}
    dups = {str(i): counts[i] - unique[str(i)] for i in IDS}
    oct27 = [r for r in rows if r["norad_id"] == 528 and r["epoch"].startswith("1963-10-27")]
    raan = [{"epoch": r["epoch"], "raan_deg": r["raan"],
             "eccentricity": r["eccentricity"], "mean_motion_rev_day": r["mean_motion"]} for r in oct27]
    report = {
        "counts": {str(i): counts[i] for i in IDS},
        "unique_epochs": unique, "duplicate_epochs": dups,
        "norad_528_oct27_rows": raan,
        "reported_site_raan_deg": 284.1520,
        "reported_mirror_raan_deg": 198.5261,
        "reported_difference_deg": 85.6259,
        "original_tle_line_checksums": "NOT_RUN: colunas line1/line2 indisponíveis",
        "frame_status": "NOT_VERIFIED: colunas numéricas não autenticam frame histórico",
        "primary_tracking_validation": "NOT_RUN: sem arquivo NORAD/AFSPC primário de 1963",
        "problems": problems,
    }
    return rows, report


def write_outputs(rows: list[dict], report: dict, target: Path, checks: dict[str, str]):
    target.mkdir(parents=True, exist_ok=True)
    cols = ("source_row",) + COLUMNS
    with (target / "norad_527_528_529_1963_numeric.csv").open("w", newline="", encoding="utf-8") as fd:
        writer = csv.DictWriter(fd, fieldnames=cols, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in cols})
    report["source"] = {
        "url": SOURCE_URL, "source_format": "Parquet numérico espelhado",
        "hashes": checks, "original_tle_lines_available": False,
        "derived_from": "alegado Space-Track bulk export; origem primária não auditada",
        "float_precision_warning": "float32 do espelho não restaura dígitos TLE originais",
    }
    (target / "audit.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--parquet", type=Path, required=True)
    p.add_argument("--download", action="store_true")
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    payload = get_parquet(args.parquet, download=args.download)
    import pyarrow.parquet as pq
    rows, report = extract_rows(pq.read_table(args.parquet))
    write_outputs(rows, report, args.output, digest(payload))
    print(json.dumps({"sha": digest(payload), "counts": report["counts"],
                      "unique": report["unique_epochs"], "issues": len(report["problems"]),
                      "oct27": report["norad_528_oct27_rows"],
                      "raw_TLE_checksum": report["original_tle_line_checksums"]}, sort_keys=True))
    if any(report["counts"][str(i)] == 0 for i in IDS):
        raise SystemExit("FALHA: objeto sem registros no espelho")
    if report["problems"]:
        raise SystemExit("FALHA: anomalias detectadas; preservar CSV e relatório")


if __name__ == "__main__":
    main()
