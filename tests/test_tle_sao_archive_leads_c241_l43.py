"""Adversarial controls on original Smithsonian finding-aid metadata."""
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.tle_sao_archive_leads_c241_l43 import LEDGER, check_claims, replay

EAD = Path('/workspace/tartaruga-r34-archive-sources/SIA.FARU0171-ead.xml')


class ArchiveControls(unittest.TestCase):
    def setUp(self):
        self.lock = json.loads(LEDGER.read_text(encoding='utf-8'))

    def test_archive_provenance_contract(self):
        self.assertEqual(len(check_claims(self.lock)), 4)

    def test_replay_actual_ead_when_available(self):
        if not EAD.exists():
            self.skipTest('historical EAD source is not bundled; CI performs live replay')
        result = replay(EAD.read_bytes(), self.lock)
        self.assertEqual(result['file_level_locator_count'], 4)
        self.assertEqual(result['domain_restrictions_activated'], 0)

    def test_hash_tampering(self):
        self.lock['source_sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            replay(EAD.read_bytes() if EAD.exists() else b'known wrong bytes', self.lock)

    def test_spurious_station_identity(self):
        self.lock['sensor_or_station'] = 'SPADATS 528 station invented'
        with self.assertRaises(ValueError): check_claims(self.lock)

    def test_spurious_epoch(self):
        self.lock['instrument_epoch_utc'] = '1963-11-08T00:00:00Z'
        with self.assertRaises(ValueError): check_claims(self.lock)

    def test_spurious_uncertainty(self):
        self.lock['instrument_uncertainty'] = 0
        with self.assertRaises(ValueError): check_claims(self.lock)

    def test_spurious_object_match(self):
        self.lock['object_match_verified'] = True
        with self.assertRaises(ValueError): check_claims(self.lock)

    def test_changed_box(self):
        self.lock['archive_entries'][0]['box'] = 23
        with self.assertRaises(ValueError): check_claims(self.lock)

    def test_duplicate_entry(self):
        self.lock['archive_entries'][0] = copy.deepcopy(self.lock['archive_entries'][1])
        with self.assertRaises(ValueError): check_claims(self.lock)

    def test_no_unauthorized_archive_contact(self):
        self.lock['contact_status'] = 'REQUEST_SENT'
        with self.assertRaises(ValueError): check_claims(self.lock)

    def test_no_unjustified_physics(self):
        self.lock['domain_restrictions_activated'] = 1
        with self.assertRaises(ValueError): check_claims(self.lock)

    def test_no_invented_reentry(self):
        self.lock['conde_reentry_location'] = 'Conde, BA'
        with self.assertRaises(ValueError): check_claims(self.lock)


if __name__ == '__main__':
    unittest.main()
