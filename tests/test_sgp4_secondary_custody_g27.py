"""G27 independent-of-satellite.js documentary controls for secondary TLE 528.

A checksum is not a SHA digest; a digest verifies bytes, not NORAD provenance.
No satellite propagation, observed decay epoch or physical trajectory is inferred.
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TLE = ROOT / 'research/tle_custody/mirror_528_1963-10-27.tle'
BRIDGE = ROOT / 'research/constraints/sgp4_secondary_teme_C179.json'
PINNED_SHA = '18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd'


def checksum(line: bytes) -> bool:
    if len(line) != 69 or line[68] not in b'0123456789':
        return False
    return (sum(ch - 48 for ch in line[:68] if 48 <= ch <= 57)
            + line[:68].count(b'-')) % 10 == line[68] - 48


def epoch_from_tle(line: bytes) -> datetime:
    """Parse YYDDD.dddddddd with decimal microseconds, UTC, no SGP4 import."""
    if len(line) != 69 or line[0:1] != b'1':
        raise ValueError('TLE layout')
    year2 = int(line[18:20]); year = 2000 + year2 if year2 < 57 else 1900 + year2
    days = Decimal(line[20:32].decode('ascii'))
    maximum = (datetime(year + 1, 1, 1) - datetime(year, 1, 1)).days
    if not (Decimal(1) <= days < Decimal(maximum + 1)):
        raise ValueError('day out of year')
    micros = (days - Decimal(1)) * Decimal(86400_000_000)
    if micros != micros.to_integral_value():
        raise ValueError('epoch beyond microsecond precision')
    return datetime(year, 1, 1, tzinfo=timezone.utc) + timedelta(microseconds=int(micros))


def recompute_checksum(line: bytes) -> bytes:
    return line[:68] + bytes([(sum(ch - 48 for ch in line[:68] if 48 <= ch <= 57)
                              + line[:68].count(b'-')) % 10 + 48])


class SecondarySgp4Custody(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = TLE.read_bytes()
        cls.line1, cls.line2 = cls.raw.splitlines()
        cls.bridge = json.loads(BRIDGE.read_text(encoding='utf-8'))

    def test_literal_digest_check_and_tle_pair_identity(self):
        source = self.bridge['secondary_input']
        self.assertEqual(source['sha256'], PINNED_SHA)
        self.assertEqual(sha256(self.raw).hexdigest(), PINNED_SHA)
        self.assertTrue(self.raw.endswith(b'\n'))
        self.assertEqual(len(self.raw.splitlines()), 2)
        self.assertTrue(checksum(self.line1))
        self.assertTrue(checksum(self.line2))
        self.assertEqual(self.line1[2:7], b'00528')
        self.assertEqual(self.line2[2:7], b'00528')
        self.assertEqual(source['object_norad'], 528)
        self.assertEqual(self.line2[17:25], b'198.5261')  # secondary RAAN, not trusted RAAN of a primary TLE
        self.assertEqual(source['source_independence'], 'ONE_RETROSPECTIVE_TLE_TRACKING_LINEAGE_NOT_PRIMARY_NORAD')

    def test_tle_epoch_independent_utc_decimal_parser(self):
        epoch = epoch_from_tle(self.line1)
        self.assertEqual(epoch.isoformat(timespec='microseconds'),
                         '1963-10-27T14:40:16.132512+00:00')
        self.assertEqual(epoch.isoformat(timespec='microseconds').replace('+00:00', 'Z'),
                         self.bridge['secondary_input']['epoch_utc'])
        self.assertEqual(epoch.tzinfo, timezone.utc)
        # JS Date has millisecond precision; the .512 ms remainder must not be
        # silently presented as an independent observation or fitted epoch.
        js_millis = epoch.replace(microsecond=132000)
        self.assertEqual((epoch - js_millis).total_seconds(), 0.000512)

    def test_valid_checksum_alone_does_not_authenticate_mutated_tle(self):
        altered = self.line2.replace(b'198.5261', b'198.5262', 1)
        self.assertNotEqual(altered, self.line2)
        altered = recompute_checksum(altered)
        self.assertTrue(checksum(altered))
        self.assertEqual(altered[2:7], b'00528')
        self.assertNotEqual(sha256(self.line1 + b'\n' + altered + b'\n').hexdigest(),
                            self.bridge['secondary_input']['sha256'])

    def test_pivot_leap_and_overflow_are_synthetics_not_1963_observations(self):
        for yy, day, expected in [
            (b'56', b'366.00000000', '2056-12-31T00:00:00+00:00'),
            (b'57', b'365.00000000', '1957-12-31T00:00:00+00:00'),
        ]:
            sample = self.line1[:18] + yy + day + self.line1[32:]
            self.assertEqual(epoch_from_tle(sample).isoformat(), expected)
        invalid = self.line1[:18] + b'63' + b'366.00000000' + self.line1[32:]
        with self.assertRaises(ValueError):
            epoch_from_tle(invalid)

    def test_inference_gates_remain_closed(self):
        self.assertFalse(self.bridge['active_constraint'])
        self.assertEqual(self.bridge['historical_holdout_527_529'], 'NOT_RUN')
        self.assertEqual(self.bridge['historical_fit'], 'NOT_RUN')
        self.assertEqual(self.bridge['impact_inference'], 'NOT_SUPPORTED')
        self.assertEqual(self.bridge['geographic_domain_reduction'], 'NOT_EVALUABLE')
        self.assertEqual(self.bridge['secondary_input']['source_uncertainty'], None)


if __name__ == '__main__':
    unittest.main()
