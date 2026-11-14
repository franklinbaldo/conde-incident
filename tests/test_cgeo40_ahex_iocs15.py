"""Adversarial controls for the third archival custody of IOCS 15."""
import copy
import unittest
from tools.cgeo40_ahex_iocs15 import load_contract, validate_contract

class CGEO40Tests(unittest.TestCase):
    def setUp(self):
        self.c = load_contract()

    def reject(self, field, key, value):
        changed = copy.deepcopy(self.c)
        changed[field][key] = value
        with self.assertRaises(ValueError):
            validate_contract(changed)

    def test_contract(self):
        self.assertEqual(validate_contract(self.c), "CGEO40_AHEX_CATALOGUE_CONTRACT_PASS")

    def test_precise_shelfmark(self):
        for key, wrong in (("record_id","05.36.335"),("module",6),
                           ("drawer",35),("map_number",335)):
            with self.subTest(key=key):
                self.reject("source", key, wrong)

    def test_catalogue_not_original(self):
        for key in ("source_bytes_acquired","facsimile_acquired"):
            with self.subTest(key=key):
                self.reject("source", key, True)
        self.reject("source","source_sha256","0"*64)
        self.reject("source","verification_channel","MAP_IMAGE_INSPECTED")

    def test_catalogue_date_not_flight_date(self):
        self.reject("source","catalogue_generated_on","1912-04-04")
        self.reject("limits","flight_date","1912-01-01")

    def test_distinct_size_does_not_prove_edition(self):
        self.reject("source","dimensions_cm",[89,64])
        self.reject("comparison","dimensions_prove_distinct_edition",True)
        self.reject("comparison","edition_identity_verified",True)

    def test_copies_not_surveys(self):
        self.reject("comparison","copy_identity_verified",True)
        self.reject("comparison","independent_topographic_survey_proven",True)
        self.reject("comparison","relation","THREE_INDEPENDENT_SURVEYS")

    def test_event_geometry_remains_unknown(self):
        for key, invented in (("center_1963",[-37,-12]),
                              ("reported_fall",[-37,-12]),
                              ("horizontal_uncertainty_m",50),
                              ("spatial_coverage_1912",{"city":"Conde"}),
                              ("original_map_image","file.pdf")):
            with self.subTest(key=key):
                self.reject("limits",key,invented)
        self.reject("limits","can_constrain_orbital_reentry",True)

    def test_provenance_transport_is_not_authenticated(self):
        self.reject("source","transport_status","PDF_SHA_VERIFIED")
        self.reject("source","source_kind","IMAGE")

    def test_reference_is_not_coordinate(self):
        self.reject("source","record_id","-37.5,-12.0")

if __name__=="__main__":
    unittest.main()
