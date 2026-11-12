#!/usr/bin/env python3
"""Inspect only COS/CRAY physical record blocking; NOT an ON20 station decoder.

All offsets are byte offsets in the untouched NCAR binary (big-endian 64-bit).
The output does not imply station, level, UTC day or quality-control content.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

WORD = 8
SECTOR_WORDS = 512
SECTOR_BYTES = WORD * SECTOR_WORDS
VALID_RCW = {8: "EOR", 14: "EOF", 15: "EOD"}


class BlockingError(ValueError):
    """Malformed or incomplete COS control-word chain."""


def digest_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def inspect(path, expected_sha256=None, expected_size=None):
    path = Path(path)
    size = path.stat().st_size
    if not size or size % SECTOR_BYTES:
        raise BlockingError("file size must be a nonzero multiple of 4096")
    if expected_size is not None and size != expected_size:
        raise BlockingError("byte count mismatch against manifest")
    sha = digest_file(path)
    if expected_sha256 is not None and sha != expected_sha256:
        raise BlockingError("SHA-256 mismatch against verified custodian")
    words = size // WORD
    index = 0
    counts = Counter()
    eor_sample = []
    eof_offsets = []
    eod_offset = None
    bad_data_flags = 0
    with path.open("rb") as file:
        while index < words:
            file.seek(index * WORD)
            raw = file.read(WORD)
            if len(raw) != WORD:
                raise BlockingError("short read at word %d" % index)
            value = int.from_bytes(raw, "big")
            mode = value >> 60
            fwi = value & 0x1FF
            offset = index * WORD
            if index % SECTOR_WORDS == 0:
                if mode != 0:
                    raise BlockingError("expected BCW at byte %d" % offset)
                block_number = (value >> 9) & 0xFFFFFF
                if block_number != index // SECTOR_WORDS % (1 << 24):
                    raise BlockingError("BCW block number mismatch at byte %d" % offset)
                counts["BCW"] += 1
            else:
                if mode not in VALID_RCW:
                    raise BlockingError("unrecognized RCW mode %d at byte %d" % (mode, offset))
                counts[VALID_RCW[mode]] += 1
                if mode == 8 and len(eor_sample) < 5:
                    eor_sample.append(offset)
                if mode == 14:
                    eof_offsets.append(offset)
                if mode == 15:
                    eod_offset = offset
            if (value >> 52) & 1:
                bad_data_flags += 1
            if mode == 15:
                if fwi:
                    raise BlockingError("EOD with nonzero FWI")
                file.seek(offset + WORD)
                padding = file.read()
                if len(padding) >= SECTOR_BYTES or any(padding):
                    raise BlockingError("nonzero or oversized trailing EOD padding")
                break
            following = index + fwi + 1
            next_sector = ((index // SECTOR_WORDS) + 1) * SECTOR_WORDS
            if following > next_sector:
                raise BlockingError("FWI skips mandatory sector BCW at byte %d" % offset)
            if following >= words:
                raise BlockingError("missing next control word after byte %d" % offset)
            index = following
    if eod_offset is None:
        raise BlockingError("missing EOD")
    if counts["BCW"] != size // SECTOR_BYTES:
        raise BlockingError("not all sector BCWs were visited")
    if counts["EOF"] < 1 or counts["EOR"] < 1:
        raise BlockingError("no complete COS file or record")
    return {
        "schema": "conde.nmc-y20175-cos-structure/v1",
        "archive_bytes": size,
        "archive_sha256": sha,
        "word_endianness": "big",
        "sector_bytes": SECTOR_BYTES,
        "controls": dict(sorted(counts.items())),
        "control_words_total": sum(counts.values()),
        "eor_first_five_byte_offsets": eor_sample,
        "eof_byte_offsets": eof_offsets,
        "eod_byte_offset": eod_offset,
        "trailing_zero_padding_bytes": size - eod_offset - WORD,
        "control_bad_data_flag_count": bad_data_flags,
        "structural_status": "COS_CONTROL_CHAIN_VERIFIED",
        "on20_station_record_decoding": "NOT_RUN",
        "station_day_matches": None,
        "station_day_absences": None,
        "physical_orbital_constraint": "NOT_ACTIVATED",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--manifest", type=Path, help="JSON manifest with archive_bytes and archive_sha256")
    args = parser.parse_args()
    expected = json.loads(args.manifest.read_text(encoding="utf8")) if args.manifest else {}
    try:
        report = inspect(args.file, expected.get("archive_sha256"), expected.get("archive_bytes"))
    except BlockingError as exc:
        parser.exit(2, "COS_BLOCKING_FAIL: %s\n" % exc)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
