"""R66: normal and optimized checks with hostile source/semantic mutations."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from c241_un_omega_registry_alias_r66 import assess

DATA=json.loads((ROOT/"research/tle_custody/c241_un_omega_registry_leads_r66.json").read_text(encoding="utf-8"))

class OmegaRegistryTests(unittest.TestCase):
    def test_original_transcription(self):
        x=assess(DATA)
        self.assertEqual(x["registration_roles"]["1962 Omega 2"],"FRAGMENT")
        self.assertEqual(x["un_omega1_decay_report"]["field_heading"],"Decay before")
        self.assertTrue(x["nominal_calendar_labels_consistent"])

    def test_un_1962_orbit_is_not_orbital_epoch(self):
        x=assess(DATA)
        self.assertEqual(x["un_omega1_initial_orbit"]["period_min"],92.4)
        self.assertIsNone(x["un_omega1_initial_orbit"]["epoch_instrumental_utc"])

    def test_no_identity_or_terminal_probability(self):
        x=assess(DATA)
        self.assertFalse(x["same_name_implies_same_object_across_editions"])
        self.assertFalse(x["date_alignment_is_calibrated_utc_interval"])
        self.assertEqual(x["independent_terminal_holdouts_added"],0)
        self.assertIsNone(x["identity_probability"])
        self.assertIsNone(x["terminal_sigma_hours"])
        self.assertIsNone(x["nasa_1963"]["norad_id_printed"])
        self.assertFalse(x["active_constraint_528"])
        self.assertEqual(x["historical_mcmc"],"NOT_RUN")

    def mutate(self,path,value,error):
        r=copy.deepcopy(DATA)
        dest=r
        for k in path[:-1]:
            dest=dest[k]
        dest[path[-1]]=value
        with self.assertRaisesRegex(ValueError,error):
            assess(r)

    def test_fragment_relabel_rejected(self):
        self.mutate(["transcribed_rows",1,"role"],"PAYLOAD","transcript")
        self.mutate(["transcribed_rows",2,"role"],"ROCKET","transcript")

    def test_un_bound_not_decay_event(self):
        self.mutate(["transcribed_rows",3,"field_heading"],"Decay at","transcript")
        self.mutate(["transcribed_rows",3,"reported_before_date"],"1963-10-30","transcript")

    def test_source_independence_not_inferred(self):
        self.mutate(["sources","original_un_document_scans_verified"],True,"custody")
        self.mutate(["sources","instrumental_independence_from_nasa_catalog_verified"],True,"custody")

    def test_forbid_direct_norad_crosswalk(self):
        self.mutate(["boundaries","direct_un_to_norad_308_crosswalk"],True,"promotion")
        self.mutate(["nasa_1963_row","norad_id_printed"],308,"NASA")

    def test_forbid_probabilistic_promotion(self):
        self.mutate(["boundaries","identity_probability"],0.99,"promotion")
        self.mutate(["boundaries","terminal_sigma_hours"],12,"promotion")
        self.mutate(["boundaries","active_constraint_528"],True,"promotion")

    def test_forbid_utc_invention(self):
        self.mutate(["nasa_1963_row","utc_convention_established"],True,"NASA")
        self.mutate(["boundaries","terminal_instant_utc"],"1963-10-30T00:00:00Z","promotion")

    def test_wrong_era_collision_rejected(self):
        self.mutate(["transcribed_rows",0,"cospar_1962"],"1963 Omega 1","transcript")

if __name__=="__main__":
    unittest.main()
