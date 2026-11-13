"""NOAA station history: reject retrospective instrument/coordinate attribution to 1963."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'tools'/'audit_igra_recife_station_history.py'
BASE=ROOT/'research'/'meteorology'
SPEC=importlib.util.spec_from_file_location('recife_station_history',SRC)
MODULE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class RecifeStationHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.card=json.loads((BASE/'igra_recife_1963_station_history_gap.json').read_text())

    def test_reproducible_offline_card(self):
        self.assertEqual(self.card,MODULE.derive())
        p=subprocess.run([sys.executable,str(SRC),'--check'],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)

    def test_original_stations_and_epochs(self):
        events=self.card['event_records']
        self.assertEqual(len(events),12)
        self.assertEqual({r['wmo_id'] for r in events},{82899,82900})
        self.assertEqual({r['event_year'] for r in events},{1982,1986,1989,1992})
        self.assertEqual(len(self.card['sonde_code_intervals']),12)
        self.assertEqual(min(int(r['from_utc'][:4]) for r in self.card['sonde_code_intervals']),2000)
        self.assertTrue(all(r['uncertain_date_flag']==1 for r in events if r['event_year']<1992))
        self.assertTrue(all(r['event_month']==99 and r['event_day']==99 for r in events if r['event_year']<1992))

    def test_archive_and_excerpt_hashes(self):
        x=self.card['source']
        self.assertEqual(x['metadata_full_sha256'],MODULE.METADATA_SHA)
        self.assertEqual(x['sonde_full_sha256'],MODULE.SONDE_SHA)
        self.assertEqual(x['metadata_excerpt_sha256'],MODULE.sha(MODULE.META_EXCERPT.read_bytes()))
        self.assertEqual(x['sonde_excerpt_sha256'],MODULE.sha(MODULE.SONDE_EXCERPT.read_bytes()))
        self.assertFalse(x['independent_sounding_measurement'])
        with self.assertRaises(AssertionError):
            MODULE.verify_original(MODULE.META_EXCERPT,MODULE.META_EXCERPT,MODULE.METADATA_SHA)

    def test_no_retrospective_1963_claims(self):
        q=self.card['conclusions']
        for f in ['documented_1963_instrument','documented_1963_height_processing',
                  'documented_1963_station_coordinates','documented_1963_station_elevation_m',
                  'instrumental_sigma_1963','recife_to_conde_error']:
            self.assertIsNone(q[f],f)
        for f in ['can_backdate_1982_sonde_to_1963',
                  'can_use_later_coordinates_as_1963_observation',
                  'can_activate_geographic_constraint']:
            self.assertFalse(q[f],f)

    def test_invalid_station_year_and_type_rejected(self):
        raw=MODULE.META_EXCERPT.read_bytes().splitlines()[0].decode('ascii')
        for row in ('OTHER000000'+raw[11:], raw[:84]+'1963'+raw[88:], raw[:100]+'USING FALSE DEVICE '+raw[119:]):
            with self.subTest(row=row[:25]), self.assertRaises(AssertionError):
                MODULE.parse_metadata(row)

if __name__=='__main__': unittest.main()
