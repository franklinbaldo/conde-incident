"""Checksum e época de UM par de um espelho secundário. Não autentica 1963."""
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from audit_norad_1963 import tle_checksum, validate_raw_tle

MIRROR_URL = "https://www.itau.magnetic-declination.com/satellite/?s=528"
MIRROR_PAIR_SHA256 = "18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd"


class Secondary528(unittest.TestCase):
    def test_secondary_pair_byte_hash_and_original_format(self):
        payload = (ROOT / "research/tle_custody/mirror_528_1963-10-27.tle").read_bytes()
        self.assertEqual(sha256(payload).hexdigest(), MIRROR_PAIR_SHA256)
        first, second = payload.decode("ascii").splitlines()
        observed = validate_raw_tle(first, second, 528)
        self.assertEqual(observed["checksum"], "PASS_syntax_only")
        self.assertEqual((tle_checksum(first), tle_checksum(second)), (0, 4))
        self.assertEqual(observed["raan_deg"], 198.5261)
        self.assertEqual(observed["eccentricity"], 0.0017147)
        self.assertAlmostEqual(observed["mean_motion_rev_day"], 15.7490146)

    def test_epoch_from_tle_fraction_and_not_rounded_local_clock(self):
        first = (ROOT / "research/tle_custody/mirror_528_1963-10-27.tle").read_text().splitlines()[0]
        epoch_year, epoch_doy = int(first[18:20]), float(first[20:32])
        self.assertEqual(epoch_year, 63)
        exact = datetime(1963, 1, 1, tzinfo=timezone.utc) + timedelta(days=epoch_doy - 1)
        self.assertEqual(exact.isoformat(), "1963-10-27T14:40:16.132512+00:00")
        self.assertNotEqual(exact.second, 0)


if __name__ == "__main__":
    unittest.main()
