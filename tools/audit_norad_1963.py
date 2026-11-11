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
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
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
    if len(first) != 69 or len(second) != 69 or first[0] != "1" or second[0] != "2":
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
    tle_epoch_utc(first)  # também rejeita dia inválido para ano não bissexto
    return {"norad_id": a, "epoch_year": 1963, "epoch_day": doy,
            "raan_deg": float(second[17:25]),
            "eccentricity": float("0." + second[26:33]),
            "mean_motion_rev_day": float(second[52:63]),
            "checksum": "PASS_syntax_only"}


def tle_epoch_utc(line: str) -> datetime:
    """A fração DOY de 8 dígitos do TLE é decimal, não float nem hora arredondada."""
    if len(line) != 69 or line[0] != "1" or line[18:20] != "63":
        raise ValueError("linha 1/ano 1963 inválidos")
    try:
        doy = Decimal(line[20:32])
    except InvalidOperation as exc:
        raise ValueError("dia TLE não decimal") from exc
    ordinal = int(doy)
    if not 1 <= ordinal <= 365:  # 1963 não foi bissexto
        raise ValueError("dia TLE fora do calendário de 1963")
    usec = int(((doy - ordinal) * Decimal("86400000000")).to_integral_value())
    if not 0 <= usec < 86400000000:
        raise ValueError("fração TLE fora do dia")
    return datetime(1963, 1, 1, tzinfo=timezone.utc) + timedelta(days=ordinal - 1, microseconds=usec)


def angular_distance_deg(a: float, b: float) -> float:
    """Distância angular módulo 360°, não uma diferença linear indevida."""
    return abs(((a - b + 180.0) % 360.0) - 180.0)


def compare_secondary_528(rows: list[dict], mirror_path: Path) -> dict:
    """Reconciliar DOIS ESPELHOS da MESMA família de rastreamento, sem forçar acordo.

    A comparação não autentica observações de 1963, não escolhe RAAN e
    NÃO substitui os bytes de linha1/linha2 primários ausentes.
    """
    payload = mirror_path.read_bytes()
    if digest(payload)["sha256"] != "18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd":
        raise ValueError("par secundário 528 alterado: SHA256 divergente")
    first, second = payload.decode("ascii").splitlines()
    observed = validate_raw_tle(first, second, 528)
    target_epoch = tle_epoch_utc(first)
    pairs = []
    for row in rows:
        if row["norad_id"] != 528:
            continue
        stamp = datetime.fromisoformat(row["epoch"].replace("Z", "+00:00"))
        delta = abs((stamp - target_epoch).total_seconds())
        if delta <= 1.0:
            pairs.append((row, delta))
    fields = {
        "inclination": (float(second[8:16]), 0.00006, True),
        "raan": (observed["raan_deg"], 0.00006, True),
        "eccentricity": (observed["eccentricity"], 0.00000008, False),
        "arg_perigee": (float(second[34:42]), 0.00006, True),
        "mean_anomaly": (float(second[43:51]), 0.00006, True),
        "mean_motion": (observed["mean_motion_rev_day"], 0.00000005, False),
    }
    compared = []
    for row, seconds in pairs:
        deltas = {
            name: (angular_distance_deg(row[name], expected) if circular
                   else abs(row[name] - expected))
            for name, (expected, _, circular) in fields.items()
        }
        agree = all(deltas[name] <= tolerance for name, (_, tolerance, _) in fields.items())
        compared.append({
            "source_row": row["source_row"], "epoch_utc": row["epoch"],
            "epoch_delta_seconds": seconds, "field_absolute_deltas": deltas,
            "parquet_raan_deg": row["raan"],
            "within_float32_rounding": agree,
        })
    status = ("NO_MATCHING_EPOCH" if not compared else
              "AMBIGUOUS_DUPLICATE_EPOCH" if len(compared) > 1 else
              "MATCH_WITHIN_ROUNDING" if compared[0]["within_float32_rounding"]
              else "FIELD_DIVERGENCE")
    return {
        "status": status,
        "same_instrumental_lineage": True,
        "source_url": "https://www.itau.magnetic-declination.com/satellite/?s=528",
        "sha": digest(payload), "line_sha256": [digest(x.encode("ascii"))["sha256"] for x in (first, second)],
        "tle_epoch_utc": target_epoch.isoformat().replace("+00:00", "Z"),
        "tle_raan_deg": observed["raan_deg"],
        "site_raan_deg_unproven": 284.1520,
        "site_vs_tle_angular_distance_deg": angular_distance_deg(284.1520, observed["raan_deg"]),
        "match_criterion": "epoch <=1 second; float32 tolerance on orbital fields",
        "matched_records": compared,
        "primary_1963_tle_provenance": "NOT_VERIFIED",
    }


def digest(payload: bytes) -> dict[str, str>:
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

    groups = {}
    for r in rows:
        groups.setdefault((r["norad_id"], r["epoch"]), []).append(r)
    conflicts = [
        {"norad_id": satellite, "epoch": stamp,
         "source_rows": [v["source_row"] for v in group],
         "values_raan_deg": [v["raan"] for v in group],
         "values_mean_motion_rev_day": [v["mean_motion"] for v in group]}
        for (satellite, stamp), group in sorted(groups.items())
        if len(group) > 1 and any(
            tuple(g.get(k) for k in COLUMNS) != tuple(group[0].get(k) for k in COLUMNS)
            for g in group[1:])
    ]
    report = {
        "duplicate_epoch_conflicts": conflicts,
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

    ledger = target / "norad_528_epochs_1963.csv"
    with ledger.open("w", newline="", encoding="utf-8") as fd:
        writer = csv.DictWriter(fd, fieldnames=("source_row",) + COLUMNS, lineterminator="\\n")
        writer.writeheader()
        for row in rows:
            if row["norad_id"] == 528:
                writer.writerow({k: row.get(k) for k in ("source_row",) + COLUMNS})
    report["derived_file_hashes"] = {
        filename: digest((target / filename).read_bytes())
        for filename in ("norad_527_528_529_1963_numeric.csv", "norad_528_epochs_1963.csv")
    }
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
    p.add_argument("--mirror-pair", type=Path, default=Path(__file__).resolve().parents[1] / "research/tle_custody/mirror_528_1963-10-27.tle")
    args = p.parse_args()
    payload = get_parquet(args.parquet, download=args.download)
    import pyarrow.parquet as pq
    rows, report = extract_rows(pq.read_table(args.parquet))
    report["mirror_comparison_528"] = compare_secondary_528(rows, args.mirror_pair)
    write_outputs(rows, report, args.output, digest(payload))
    print(json.dumps({"sha": digest(payload), "counts": report["counts"],
                      "unique": report["unique_epochs"], "issues": len(report["problems"]),
                      "oct27": report["norad_528_oct27_rows"],
                      "mirror_reconciliation": report["mirror_comparison_528"]["status"],
                      "raw_TLE_checksum": report["original_tle_line_checksums"]}, sort_keys=True))
    if any(report["counts"][str(i)] == 0 for i in IDS):
        raise SystemExit("FALHA: objeto sem registros no espelho")
    if report["problems"]:
        raise SystemExit("FALHA: anomalias detectadas; preservar CSV e relatório")


if __name__ == "__main__":
    main()
