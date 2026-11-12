"""Hypsometric audit: independently checked arithmetic and adversarial source guards."""
import json
import math
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import audit_igra_recife_hypsometry as audit
from audit_igra_recife_dry_density import extract
from audit_igra_recife_window import DAYS,load_original

class HypsometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profiles=[audit.build(day) for day in DAYS]

    def test_replay_every_original_source_and_json(self):
        audit.check()
        for day,profile in zip(DAYS,self.profiles):
            self.assertEqual(json.loads(audit.target(day).read_text()),profile)

    def test_81_levels_and_78_real_adjacent_layers(self):
        self.assertEqual([x['source_levels'] for x in self.profiles],[29,26,26])
        self.assertEqual([x['adjacent_layers'] for x in self.profiles],[28,25,25])
        for d in self.profiles:
            for lo,hi in zip(d['layers'],d['layers'][1:]):
                self.assertEqual(lo['upper_level_index'],hi['lower_level_index'])
            self.assertEqual(len(d['layers']),d['source_levels']-1)

    def test_independent_reference_equation_in_si_units(self):
        for profile in self.profiles:
            for r in profile['layers']:
                self.assertGreater(r['lower_pressure_hpa'],r['upper_pressure_hpa'])
                self.assertGreater(r['upper_geopotential_m'],r['lower_geopotential_m'])
                ln=math.log(r['lower_pressure_hpa']/r['upper_pressure_hpa'])
                t=(r['lower_temperature_c']+r['upper_temperature_c'])/2+273.15
                predicted=287.05/9.80665*t*ln
                self.assertAlmostEqual(predicted,r['conditional_dry_thickness_m'],places=6)
                self.assertAlmostEqual(r['observed_geopotential_thickness_m']-predicted,
                                       r['conditional_residual_observed_minus_dry_m'],places=6)
                self.assertAlmostEqual(9.80665*r['observed_geopotential_thickness_m']/(287.05*ln),
                                       r['hypsometric_implied_layer_mean_virtual_k'],places=6)

    def test_not_independent_nor_a_geographic_constraint(self):
        self.assertEqual(len(set(x['source']['upstream'] for x in self.profiles)),1)
        self.assertEqual(len(set(x['source']['excerpt_sha256'] for x in self.profiles)),3)
        for p in self.profiles:
            self.assertFalse(p['source']['historical_location_verified'])
            self.assertIsNone(p['epoch']['actual_release_utc'])
            self.assertEqual(p['epoch']['missing_time_code'],9999)
            m=p['interpretation']
            self.assertFalse(m['active_theta_constraint'])
            self.assertFalse(m['inference_of_conde'])
            self.assertFalse(m['inference_of_norad528_thermosphere'])
            self.assertFalse(m['residual_is_measurement_error'])
            for field in ('unknown_instrumental_uncertainty_m','unknown_virtual_temperature_correction_k',
                          'unknown_recife_conde_transfer_error_m','unknown_time_transfer_error_m'):
                self.assertIsNone(m[field])

    def test_reject_malformed_pairs(self):
        a,b=extract('08')['levels'][:2]
        for field,value in (('pressure_hpa',b['pressure_hpa']),('pressure_hpa',-10),
                            ('geopotential_height_m_asl',b['geopotential_height_m_asl']),
                            ('temperature_deg_c',float('nan')),('temperature_deg_c',-300)):
            bad=dict(a);bad[field]=value
            with self.subTest(field=field,value=value),self.assertRaises(ValueError):
                audit.pair(bad,b)

    def test_reject_tampered_date_and_archival_bytes(self):
        original=load_original('08')
        with self.assertRaises(ValueError):
            extract('07',raw=original)
        tampered=original.replace(b'BRM00082900',b'BRM00082901',1)
        self.assertNotEqual(tampered,original)
        with self.assertRaises(ValueError):
            extract('08',raw=tampered)

    def test_missing_humidity_is_not_synthesized(self):
        for p in self.profiles:
            source=extract(p['epoch']['nominal_utc_date'][-2:])
            for layer in p['layers']:
                a=source['levels'][layer['lower_level_index']]
                b=source['levels'][layer['upper_level_index']]
                expected=a['reported_rh_percent'] is not None and b['reported_rh_percent'] is not None
                self.assertEqual(expected,layer['rh_available_both_endpoints'])

if __name__=='__main__':unittest.main()
