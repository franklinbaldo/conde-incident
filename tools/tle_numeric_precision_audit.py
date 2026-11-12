#!/usr/bin/env python3
"""C241-L7 (extraido de C241-T6): fidelidade numerica do Parquet 1963, sem fabricar linhas TLE.

Audita tipos efetivos do arquivo pinado e se seus campos numericos podem ser
codificados por UMA grafia TLE de precisao fixa. Isso NAO recupera os bytes
line1/line2, seus checksums, frame instrumental ou observacoes de radar.
"""
import argparse
import hashlib
import json
import math
import struct
from collections import Counter
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path

PARQUET_SHA256 = "c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09"
MIRROR_SHA256 = "18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd"
IDS = (527, 528, 529)
# pyarrow tipos REAIS apresentados pelo dataset, conferidos no arquivo pinado.
EXPECTED_TYPES = {
    "norad_id": "int32",
    "epoch": "timestamp[us, tz=UTC]",
    "inclination": "float", "raan": "float", "eccentricity": "float",
    "arg_perigee": "float", "mean_anomaly": "float",
    "mean_motion": "double", "mean_motion_dot": "double",
    "bstar": "double", "intl_designator": "string", "altitude_km": "float",
}
# O movimento medio nao e float32. Angulos float32 usam 4 casas no TLE;
# excentricidade float32 tem 7; movimento medio float64 tem 8.
TLE_FIELDS = {
    "inclination": ("float", 4, False),
    "raan": ("float", 4, False),
    "eccentricity": ("float", 7, False),
    "arg_perigee": ("float", 4, False),
    "mean_anomaly": ("float", 4, False),
    "mean_motion": ("double", 8, False),
}
NOT_IN_NUMERIC_MIRROR = (
    "line1_literal", "line2_literal", "classification_flag",
    "nddot_tle_lexeme", "ephemeris_type", "element_set_number",
    "revolution_number_at_epoch", "line1_checksum_digit", "line2_checksum_digit",
    "historical_sensor_ID", "tracking_frame_certification",
)


def cast_stored(value, dtype):
    if not math.isfinite(value):
        raise ValueError("campo nao finito")
    if dtype == "float":
        return struct.unpack(">f", struct.pack(">f", value))[0]
    if dtype == "double":
        return float(value)
    raise ValueError("tipo numerico desconhecido")


def candidate_token(value, dtype, places):
    """Verifica existencia e unicidade local na grade decimal TLE; sem forjar TLE.

    O arredondamento e para a grafia mais proxima. Compara a recodificacao
    binaria da grafia e de ambas vizinhas, evitando alegar apenas proximidade.
    """
    v = float(value)
    if not math.isfinite(v):
        raise ValueError("campo nao finito")
    if cast_stored(v, dtype) != v:
        raise ValueError("campo nao corresponde ao dtype efetivo alegado")
    step = Decimal(1).scaleb(-places)
    decimal = Decimal.from_float(v)
    nearest = decimal.quantize(step, rounding=ROUND_HALF_EVEN)
    normalized = cast_stored(v, dtype)
    encoded = cast_stored(float(nearest), dtype)
    same = encoded == normalized
    aliases = [int(cast_stored(float(nearest + (step * offset)), dtype) == normalized)
               for offset in (-1, 1)]
    return {
        "grid_roundtrip": same,
        "nearest_grid_value": format(nearest, f".{places}f"),
        "adjacent_grid_collision": any(aliases),
        "decimal_places": places,
        "dtype": dtype,
        "absolute_rounding_residual": float(abs(decimal - nearest)),
    }


def verify_schema(schema):
    # Recebe mapeamento nome->representacao textual do tipo PyArrow, testavel sem PyArrow.
    missing = sorted(set(EXPECTED_TYPES) - set(schema))
    mismatched = {k: {"expected": expected, "observed": schema[k]}
                  for k, expected in EXPECTED_TYPES.items()
                  if k in schema and schema[k] != expected}
    if missing or mismatched:
        raise ValueError("schema Parquet mudou: missing=" + str(missing) +
                         "; mismatched=" + str(mismatched))
    return True


def audit_numeric_table(table, source_sha256):
    observed_schema = {field.name: str(field.type) for field in table.schema}
    verify_schema(observed_schema)
    rows = table.select(list(EXPECTED_TYPES)).to_pylist()
    detail = []
    counters = Counter()
    for source_row, row in enumerate(rows):
        if row["norad_id"] not in IDS:
            continue
        counters[row["norad_id"]] += 1
        fields = {}
        for key, (dtype, places, _) in TLE_FIELDS.items():
            fields[key] = candidate_token(row[key], dtype, places)
        detail.append({
            "source_row": source_row, "norad_id": row["norad_id"],
            "epoch_utc": row["epoch"].isoformat(),
            "precision": fields,
        })
    if not detail or any(counters[i] == 0 for i in IDS):
        raise ValueError("objeto NORAD sem registros")
    inconsistent = [
        {"source_row": x["source_row"], "norad_id": x["norad_id"],
         "field": k, "roundtrip": f["grid_roundtrip"],
         "adjacent_collision": f["adjacent_grid_collision"]}
        for x in detail for k, f in x["precision"].items()
        if not f["grid_roundtrip"] or f["adjacent_grid_collision"]
    ]
    field_counts = {k: {
        "roundtrip_on_grid": sum(1 for x in detail if x["precision"][k]["grid_roundtrip"]),
        "unique_near_grid": sum(1 for x in detail if
                                x["precision"][k]["grid_roundtrip"] and
                                not x["precision"][k]["adjacent_grid_collision"]),
    } for k in TLE_FIELDS}
    return {
        "classification": "SECONDARY_MIRROR_NUMERIC_STORAGE_NOT_PRIMARY_TLE",
        "source_sha256": source_sha256,
        "schema": observed_schema,
        "counts": {str(i): counters[i] for i in IDS},
        "rows": len(detail),
        "field_counts": field_counts,
        "inconsistent_or_ambiguous_fields": inconsistent,
        "per_row": detail,
        "not_preserved_by_this_schema": list(NOT_IN_NUMERIC_MIRROR),
        "independence": "ONE_SECONDARY_INSTRUMENTAL_LINEAGE_NOT_NEW_RADAR",
        "original_line1_line2_checksums": "NOT_AVAILABLE",
        "frame_1963": "NOT_VERIFIED",
        "legacy_RAAN_284_1520_vs_198_5261": "UNRESOLVED_PRIMARY_PROVENANCE",
        "legacy_RAAN_284_1520_active_observation": False,
        "constraint_link": {
            "id": "C241-L7",
            "state": "CONNECTED_PENDING_CALIBRATION",
            "typed_observables": ["norad_id", "epoch_utc", "inclination_deg",
                                  "raan_deg", "eccentricity_dimensionless",
                                  "arg_perigee_deg", "mean_anomaly_deg",
                                  "mean_motion_rev_per_day"],
            "reference_frame_1963": None,
            "source_sensor": None,
            "measurement_sigma": None,
            "covariance": None,
            "condition": "numeric_tle_decimal_grid_roundtrip_only",
            "candidate_Lean_4_35_0_predicate": "NOT_PROMOTED",
            "physical_parameter_domain_reduced": False,
            "terminal_holdout": "NOT_RUN",
            "conde_impact": "INDETERMINATE",
        },
        "conclusion": (
            "Mesmo quando a grafia decimal de seis campos e numericamente "
            "recuperavel, metadata e bytes originais de linha1/linha2 nao "
            "estao no Parquet. Nao emitir checksums ou TLEs supostamente primarios. "
            "Nenhuma restricao fisica, hora/local de reentrada ou impacto decorre."
        ),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--parquet", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    payload = args.parquet.read_bytes()
    sha = hashlib.sha256(payload).hexdigest()
    if sha != PARQUET_SHA256:
        raise SystemExit("FALHA: Parquet sem hash fixado: " + sha)
    if not payload.startswith(b"PAR1") or not payload.endswith(b"PAR1"):
        raise SystemExit("FALHA: assinatura fisica Parquet invalida")
    import pyarrow.parquet as pq
    report = audit_numeric_table(pq.read_table(args.parquet), sha)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2)
                           + "\n", encoding="utf-8")
    print(json.dumps({"classification": report["classification"],
                      "rows": report["rows"], "counts": report["counts"],
                      "field_counts": report["field_counts"],
                      "inconsistent_count": len(report["inconsistent_or_ambiguous_fields"]),
                      "original_line_checksums": report["original_line1_line2_checksums"]},
                     sort_keys=True))
    if report["inconsistent_or_ambiguous_fields"]:
        raise SystemExit("FALHA: campo sem roundtrip unico; preservar JSON forense")


if __name__ == "__main__":
    main()
