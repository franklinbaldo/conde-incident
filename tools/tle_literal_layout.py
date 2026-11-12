#!/usr/bin/env python3
"""Auditoria de estrutura de UM par TLE literalmente preservado num espelho.

NÃO reconstitui 45 pares de um Parquet numérico; checksum/formatos válidos
NÃO demonstram emissão NORAD em 1963, frame, objeto físico ou impacto.
"""
import argparse
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

MIRROR_URL = "https://www.itau.magnetic-declination.com/satellite/?s=528"
MIRROR_SHA256 = "18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd"
SOURCE_FORMAT = "secondary_literal_tle_not_instrumental_original"


def _field(line, start, stop, pattern, name):
    token = line[start:stop]
    if re.fullmatch(pattern, token, flags=re.ASCII) is None:
        raise ValueError("TLE field invalid: " + name)
    return token


def _checksum(line):
    if len(line) != 69 or not line.isascii() or any(ord(c) < 32 or ord(c) > 126 for c in line):
        raise ValueError("TLE must contain 69 printable ASCII columns")
    if line[-1] not in "0123456789":
        raise ValueError("TLE checksum column not an ASCII digit")
    computed = sum((ord(c) - 48 if "0" <= c <= "9" else 1 if c == "-" else 0)
                   for c in line[:68]) % 10
    if computed != ord(line[-1]) - 48:
        raise ValueError("TLE checksum mismatch")
    return {"computed": computed, "printed": ord(line[-1]) - 48}


def _angle(line, start, name, inclusive=False):
    token = _field(line, start, start + 8, r"[ 0-9]{3}\.[0-9]{4}", name)
    number = Decimal(token.strip())
    if not (Decimal(0) <= number <= Decimal(180) if inclusive else
            Decimal(0) <= number < Decimal(360)):
        raise ValueError("TLE angular field out of range: " + name)
    return str(number)


def audit_pair(first, second, expected_sat=528):
    """Valida colunas, campos, calendário, checksum e número de catálogo.

    Este gate verifica representação serializada, não frame físico ou acurácia.
    """
    checks = [_checksum(first), _checksum(second)]
    for index, line in enumerate((first, second), start=1):
        if line[:2] != str(index) + " ":
            raise ValueError("TLE line prefix invalid")
        _field(line, 2, 7, r"[0-9]{5}", "catalog")
    if first[2:7] != second[2:7] or int(first[2:7]) != expected_sat:
        raise ValueError("TLE catalog numbers differ")
    _field(first, 7, 8, r"[A-Z ]", "classification")
    _field(first, 8, 9, r" ", "line1 separator 8")
    _field(first, 9, 14, r"[0-9]{5}", "international designator launch")
    _field(first, 14, 17, r"[A-Z0-9 ]{3}", "international designator piece")
    _field(first, 17, 18, r" ", "line1 separator 17")
    year = _field(first, 18, 20, r"[0-9]{2}", "epoch year")
    if year != "63":
        raise ValueError("TLE epoch year must be 1963")
    epoch_raw = _field(first, 20, 32, r"[0-9]{3}\.[0-9]{8}", "epoch DOY")
    ordinal = int(epoch_raw[:3])
    if not 1 <= ordinal <= 365:
        raise ValueError("TLE epoch day outside 1963")
    fraction_day = int(epoch_raw[4:])
    epoch = (datetime(1963, 1, 1, tzinfo=timezone.utc) +
             timedelta(days=ordinal - 1, microseconds=fraction_day * 864))
    _field(first, 32, 33, r" ", "line1 separator 32")
    _field(first, 33, 43, r"[ +\-]\\.[0-9]{8}", "mean_motion_first_derivative_half")
    _field(first, 43, 44, r" ", "line1 separator 43")
    _field(first, 44, 52, r"[ +\-][0-9]{5}[+\-][0-9]", "mean_motion_second_derivative_sixth")
    _field(first, 52, 53, r" ", "line1 separator 52")
    _field(first, 53, 61, r"[ +\-][0-9]{5}[+\-][0-9]", "bstar")
    _field(first, 61, 62, r" ", "line1 separator 61")
    _field(first, 62, 63, r"[0-9 ]", "ephemeris type")
    _field(first, 63, 64, r" ", "line1 separator 63")
    _field(first, 64, 68, r"[ 0-9]{4}", "element set number")
    for pos in (7, 16, 25, 33, 42, 51):
        _field(second, pos, pos + 1, r" ", "line2 separator " + str(pos))
    inclination = _angle(second, 8, "inclination", inclusive=True)
    raan = _angle(second, 17, "RAAN")
    _field(second, 26, 33, r"[0-9]{7}", "eccentricity digits")
    eccentricity = str(Decimal("0." + second[26:33]))
    arg_perigee = _angle(second, 34, "argument of perigee")
    mean_anomaly = _angle(second, 43, "mean anomaly")
    motion_raw = _field(second, 52, 63, r"[ 0-9]{2}\.[0-9]{8}", "mean motion")
    mean_motion = Decimal(motion_raw.strip())
    if mean_motion <= 0:
        raise ValueError("TLE mean motion must be positive")
    _field(second, 63, 68, r"[ 0-9]{5}", "revolution number")
    return {
        "catalog": expected_sat,
        "epoch_raw": year + epoch_raw,
        "epoch_utc": epoch.isoformat(timespec="microseconds").replace("+00:00", "Z"),
        "timestamp_grid_quantum_us": 864,
        "values": {
            "inclination": {"printed": second[8:16], "decimal": inclination, "unit": "deg"},
            "raan": {"printed": second[17:25], "decimal": raan, "unit": "deg"},
            "eccentricity": {"printed": second[26:33], "decimal": eccentricity, "unit": "dimensionless"},
            "arg_perigee": {"printed": second[34:42], "decimal": arg_perigee, "unit": "deg"},
            "mean_anomaly": {"printed": second[43:51], "decimal": mean_anomaly, "unit": "deg"},
            "mean_motion": {"printed": motion_raw, "decimal": str(mean_motion), "unit": "rev/day"},
        },
        "line1_other_fields": {
            "mean_motion_first_derivative_half": first[33:43],
            "mean_motion_second_derivative_sixth": first[44:52],
            "bstar": first[53:61], "ephemeris_type": first[62],
            "element_set_number": first[64:68],
        },
        "checksums": {"line1": checks[0], "line2": checks[1]},
        "sha256_per_line_no_newline": [
            hashlib.sha256(line.encode("ascii")).hexdigest() for line in (first, second)
        ],
        "representation_status": "SYNTACTICALLY_VALID",
        "primary_norad_1963_provenance": "NOT_VERIFIED",
        "frame_historical": "NOT_VERIFIED",
        "source_instrumental_independence": "NOT_ESTABLISHED",
    }


def audit_literal_file(path):
    payload = path.read_bytes()
    sha = hashlib.sha256(payload).hexdigest()
    if sha != MIRROR_SHA256:
        raise ValueError("literal mirror file SHA256 mismatch")
    if b"\r" in payload or payload.count(b"\n") != 2 or not payload.endswith(b"\n"):
        raise ValueError("literal mirror line endings changed")
    first, second = payload.decode("ascii").splitlines()
    report = audit_pair(first, second)
    report["source"] = {
        "url": MIRROR_URL, "format": SOURCE_FORMAT, "sha256": sha,
        "line1_line2_original_1963_instrumental": False,
        "bytes_including_final_LF_preserved": True,
    }
    report["other_45_original_pairs_checksummed"] = False
    report["unverified_legacy_raan_deg"] = "284.1520"
    report["relative_to_literal_raan_deg"] = "85.6259"
    report["legacy_raan_provenance_conflict"] = "UNRESOLVED"
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pair", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit_literal_file(args.pair)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    print(json.dumps({"catalog": report["catalog"], "epoch": report["epoch_utc"],
                      "format": report["representation_status"],
                      "primary": report["primary_norad_1963_provenance"]}))


if __name__ == "__main__":
    main()
