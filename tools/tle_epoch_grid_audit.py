#!/usr/bin/env python3
"""Auditoria de quantizacao de epocas NUMERICAS secundarias (nao TLE primarios).

Um carimbo compativel com o quantum de 8 decimais do dia TLE (864 us)
NAO autentica NORAD, sensor, frame ou qualquer elemento orbital.
"""
import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from audit_norad_1963 import TLE_EPOCH_QUANTUM_US

EXPECTED_CSV_SHA256 = "3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231"
IDS = (527, 528, 529)


def assess_epoch_grid(rows):
    """Sem float: compara cada hora UTC com a grade inteira de 864 us do dia."""
    counts = Counter()
    exact = Counter()
    distinct = {sat: set() for sat in IDS}
    source_rows = set()
    failures = []
    residual_max = 0
    for item in rows:
        source_row = int(item["source_row"])
        if source_row in source_rows:
            raise ValueError("source_row duplicado no CSV custodiado")
        source_rows.add(source_row)
        sat = int(item["norad_id"])
        if sat not in IDS:
            raise ValueError("NORAD fora do escopo")
        stamp = item["epoch"]
        if not stamp.endswith("Z"):
            raise ValueError("epoca sem indicador UTC Z")
        dt = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        if dt.tzinfo != timezone.utc or dt.year != 1963:
            raise ValueError("epoca fora do escopo UTC/1963")
        midnight = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        micros = (dt - midnight) // timedelta(microseconds=1)
        tick, remainder = divmod(micros, TLE_EPOCH_QUANTUM_US)
        # 864 us divides exactly one day (100 million ticks), sem arredondamento.
        nearest_residual = min(remainder, TLE_EPOCH_QUANTUM_US - remainder)
        residual_max = max(residual_max, nearest_residual)
        counts[sat] += 1
        distinct[sat].add(stamp)
        if nearest_residual == 0:
            exact[sat] += 1
        else:
            failures.append({
                "source_row": source_row,
                "norad_id": sat,
                "epoch_utc": stamp,
                "residual_to_nearest_tle_epoch_grid_microseconds": nearest_residual,
                "preceding_grid_tick": tick,
            })
    return {
        "status": "ALL_ON_8_DECIMAL_DAY_GRID" if not failures else "OFF_GRID_EPOCHS_PRESENT",
        "classification": "SECONDARY_NUMERIC_REPRESENTATION_TEST_ONLY",
        "epoch_quantum_microseconds": TLE_EPOCH_QUANTUM_US,
        "all_epochs_original_norad_verified": False,
        "source_instrumental_independence": "NOT_VERIFIED",
        "per_object": {
            str(sat): {
                "rows": counts[sat],
                "distinct_utc_epochs": len(distinct[sat]),
                "exact_grid_rows": exact[sat],
                "off_grid_rows": counts[sat] - exact[sat],
            } for sat in IDS
        },
        "max_residual_microseconds": residual_max,
        "off_grid_details": failures,
        "caution": ("Representabilidade em 864 us nao comprova os bytes line1/line2, "
                    "checksum individual, sensor, observacao fisica, TEME, "
                    "identidade de componente ou lugar de reentrada."),
    }


def audit_file(path, expected_sha256=EXPECTED_CSV_SHA256):
    payload = path.read_bytes()
    actual = hashlib.sha256(payload).hexdigest()
    if actual != expected_sha256:
        raise ValueError("hash SHA-256 do CSV fonte divergente: " + actual)
    with path.open(newline="", encoding="utf-8") as fd:
        reader = csv.DictReader(fd)
        if not {"source_row", "norad_id", "epoch"}.issubset(reader.fieldnames or []):
            raise ValueError("colunas obrigatorias ausentes")
        rows = list(reader)
    report = assess_epoch_grid(rows)
    if not rows or any(report["per_object"][str(i)]["rows"] == 0 for i in IDS):
        raise ValueError("CSV nao cobre os tres objetos")
    report["source_csv_sha256"] = actual
    report["source_file"] = path.name
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit_file(args.csv)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    # Um OFF_GRID e resultado observacional NEGATIVO: o JSON permanece
    # disponivel como artefato, mas o gate impede assumir compatibilidade.
    if report["status"] != "ALL_ON_8_DECIMAL_DAY_GRID":
        raise SystemExit("epocas fora da grade de 8 decimais: verificar fonte")


if __name__ == "__main__":
    main()
