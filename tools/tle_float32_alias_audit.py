#!/usr/bin/env python3
"""C241-T6: prova de perda de informacao no espelho numerico 1963.

O Parquet/CSV nao e um boletim primario NORAD. Este programa demonstra
quantas grafias de movimento medio TLE com oito casas decimais sao
indistinguiveis depois de arredondamento para binary32. NAO fabrica TLE,
nao verifica checksums de 1963 e nao propaga orbitas.
"""
import argparse
import csv
import hashlib
import json
import math
import struct
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
from pathlib import Path

SOURCE_PARQUET_SHA256 = "c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09"
SOURCE_CSV_SHA256 = "3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231"
LITERAL_528_SHA256 = "18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd"
STEP = Decimal("0.00000001")
SCALE = Decimal(100000000)
IDS = (527, 528, 529)


def binary32_bits(value):
    if not math.isfinite(value) or value <= 0 or value >= 100:
        raise ValueError("mean_motion nao finito/positivo ou fora de duas casas inteiras")
    return int.from_bytes(struct.pack(">f", value), "big")


def bits_to_float(bits):
    return struct.unpack(">f", bits.to_bytes(4, "big"))[0]


def tle_mean_motion_token(tick):
    """Campo TLE linha 2 de largura 11: '15.74901460'."""
    if not 0 < tick < 10_000_000_000:
        raise ValueError("mean_motion fora do intervalo TLE numerico")
    return f"{tick // 100000000:02d}.{tick % 100000000:08d}"


def aliases_binary32(value):
    """Enumera TODOS os tokens TLE de 8 decimais que arredondam ao mesmo float32.

    Limites obtidos de pontos medios de floats adjacentes. Recheca cada
    candidato por pack/unpack IEEE-754; inclusive desempates de ponto medio.
    Nao presume que a fonte original usou esses tokens.
    """
    bits = binary32_bits(value)
    if bits <= 1 or bits >= 0x7F7FFFFE:
        raise ValueError("binary32 fora de regiao finita positiva utilizavel")
    center = bits_to_float(bits)
    if center != value:
        raise ValueError("CSV nao contem valor binary32 exato; linhagem de dtype nao comprovada")
    previous = Decimal.from_float(bits_to_float(bits - 1))
    current = Decimal.from_float(center)
    following = Decimal.from_float(bits_to_float(bits + 1))
    low = (previous + current) * SCALE / 2
    high = (current + following) * SCALE / 2
    start = max(1, int(low.to_integral_value(rounding=ROUND_FLOOR)) - 1)
    stop = min(9_999_999_999, int(high.to_integral_value(rounding=ROUND_CEILING)) + 1)
    # Evitar loop incontrolado se o esquema receber grandezas incompatíveis.
    if stop - start > 100_000:
        raise ValueError("intervalo de candidatos excessivo")
    aliases = [tick for tick in range(start, stop + 1)
               if binary32_bits(float(Decimal(tick) * STEP)) == bits]
    if not aliases:
        raise ValueError("nenhum token de oito decimais compativel com binary32")
    return {
        "binary32_bits_hex": f"{bits:08x}",
        "binary32_value": center,
        "count": len(aliases),
        "minimum_token": tle_mean_motion_token(aliases[0]),
        "maximum_token": tle_mean_motion_token(aliases[-1]),
        "aliases_int": aliases,
    }


def read_csv(path, *, enforce_sha=True):
    payload = Path(path).read_bytes()
    sha = hashlib.sha256(payload).hexdigest()
    if enforce_sha and sha != SOURCE_CSV_SHA256:
        raise ValueError(f"CSV de custodia divergente do SHA256 fixado: {sha}")
    with Path(path).open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"source_row", "norad_id", "epoch", "mean_motion"}
        if not required.issubset(reader.fieldnames or ()):
            raise ValueError("CSV sem colunas obrigatorias")
        rows = list(reader)
    seen = set()
    output = []
    for row in rows:
        norad = int(row["norad_id"])
        if norad not in IDS:
            raise ValueError("CSV de custodia contem objeto fora do escopo")
        source_row = int(row["source_row"])
        if source_row in seen:
            raise ValueError("indices source_row duplicados")
        seen.add(source_row)
        stamp = datetime.fromisoformat(row["epoch"].replace("Z", "+00:00"))
        if stamp.tzinfo is None or stamp.utcoffset().total_seconds() != 0 or stamp.year != 1963:
            raise ValueError("epoch fora de 1963 UTC")
        motion = float(row["mean_motion"])
        if not math.isfinite(motion):
            raise ValueError("mean_motion nao finito")
        output.append({"source_row": source_row, "norad_id": norad,
                       "epoch_utc": stamp.isoformat().replace("+00:00", "Z"),
                       "mean_motion": motion})
    if any(not any(row["norad_id"] == n for row in output) for n in IDS):
        raise ValueError("ausencia de um dos NORAD 527,528,529")
    return output, sha


def audit(rows, csv_sha, literal_pair):
    pair_payload = Path(literal_pair).read_bytes()
    if hashlib.sha256(pair_payload).hexdigest() != LITERAL_528_SHA256:
        raise ValueError("par literal 528 alterado")
    lines = pair_payload.decode("ascii").splitlines()
    if len(lines) != 2 or any(len(line) != 69 for line in lines):
        raise ValueError("par literal nao possui duas linhas de 69 colunas")
    from audit_norad_1963 import tle_epoch_utc, validate_raw_tle
    validate_raw_tle(lines[0], lines[1], 528)
    literal_epoch = tle_epoch_utc(lines[0]).isoformat().replace("+00:00", "Z")
    literal_token = lines[1][52:63]
    literal_tick = int(Decimal(literal_token) * SCALE)
    if tle_mean_motion_token(literal_tick) != literal_token:
        raise ValueError("campo literal de mean_motion nao tem oito decimais")
    detail = []
    for row in rows:
        aliases = aliases_binary32(row["mean_motion"])
        item = {k: row[k] for k in ("source_row", "norad_id", "epoch_utc")}
        item.update({k: v for k, v in aliases.items() if k != "aliases_int"})
        detail.append(item)
    literal_matches = [x for x in detail
                       if x["norad_id"] == 528 and x["epoch_utc"] == literal_epoch]
    if len(literal_matches) != 1:
        raise ValueError("epoca literal 528 nao corresponde univocamente ao espelho")
    target = literal_matches[0]
    candidate_ticks = aliases_binary32(next(
        row["mean_motion"] for row in rows
        if row["source_row"] == target["source_row"]))["aliases_int"]
    if literal_tick not in candidate_ticks:
        raise ValueError("texto do par literal nao gera o mesmo binary32 da epoca 528")
    counts = Counter(row["norad_id"] for row in rows)
    ambiguous = Counter(x["norad_id"] for x in detail if x["count"] > 1)
    return {
        "classification": "DIGITAL_NON_INJECTIVITY_NOT_PRIMARY_TLE_OBSERVATION",
        "source": {
            "csv_sha256": csv_sha,
            "parquet_sha256_from_upstream_custody": SOURCE_PARQUET_SHA256,
            "secondary_literal_pair_sha256": LITERAL_528_SHA256,
            "instrumental_origin": "NOT_VERIFIED",
            "float32_dtype": "VERIFIED_EXACT_VALUE_PER_ROW_NOT_ORIGINAL_SCHEMA_FACSIMILE",
        },
        "field": "TLE line2 mean_motion in rev/day, 8 decimal places",
        "rounding": "IEEE754 binary32 round-to-nearest-even",
        "counts": {str(i): counts[i] for i in IDS},
        "ambiguous_mean_motion_rows": {str(i): ambiguous[i] for i in IDS},
        "literal_528": {
            "source_row": target["source_row"],
            "epoch_utc": literal_epoch,
            "verbatim_mean_motion_token": literal_token,
            "reencoded_binary32_bits": target["binary32_bits_hex"],
            "possible_tokens_after_float32": target["count"],
            "minimum_token": target["minimum_token"],
            "maximum_token": target["maximum_token"],
            "literal_token_in_candidates": True,
        },
        "per_source_row": detail,
        "conclusion": (
            "Uma ou mais grafias TLE podem codificar o mesmo binary32. "
            "Nao e possivel recuperar univocamente os 45 campos literais nem os "
            "checksums TLE originais a partir desse CSV; isto nao decide "
            "RAAN 198.5261 vs 284.1520, frame, origem nem local de reentrada."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--pair", type=Path, default=Path(__file__).resolve().parents[1] /
                        "research/tle_custody/mirror_528_1963-10-27.tle")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows, csv_sha = read_csv(args.csv)
    report = audit(rows, csv_sha, args.pair)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False)
                           + "\n", encoding="utf-8")
    print(json.dumps({"classification": report["classification"],
                      "counts": report["counts"],
                      "ambiguous_mean_motion_rows": report["ambiguous_mean_motion_rows"],
                      "literal_528": report["literal_528"]}, sort_keys=True))


if __name__ == "__main__":
    main()
