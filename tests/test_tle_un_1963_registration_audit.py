"""C241-L33 adversarial UN 1963 original-registration and decay-status checks."""
import copy
import json
import unittest
from pathlib import Path
from tools.tle_un_1963_registration_audit import validate, check_pdf_bytes, NASA77, NASA63, MODEL

ROOT=Path(__file__).resolve().parents[1]
def load(path): return json.loads((ROOT/path).read_text(encoding="utf-8"))
SOURCES=[load(MODEL),load(NASA77),load(NASA63)]

class UN1963Primary(unittest.TestCase):
    def reject(self,index,edit):
        x=copy.deepcopy(SOURCES)
        edit(x[index])
        with self.assertRaises((ValueError,TypeError,KeyError)):
            validate(*x)

    def test_four_verified_pdfs_and_nonphysical_graph(self):
        r=validate(*SOURCES)
        self.assertEqual(r["source_count"],4)
        self.assertEqual(r["jan31_registered_objects"],[527,528,529])
        self.assertEqual(r["528_period_jan31_printed_minutes"],"94.5")
        self.assertTrue(r["nov15_528_no_longer_in_orbit_reported"])
        self.assertEqual(r["physical_constraints_activated"],0)

    def test_wrong_30_sha(self):
        self.reject(0,lambda m:m["docs"][0].update(sha256="0"*64))

    def test_wrong_53_bytes(self):
        self.reject(0,lambda m:m["docs"][1].update(bytes=850471))

    def test_missing_october_control(self):
        self.reject(0,lambda m:m["docs"].pop(2))

    def test_wrong_day_printed_for_nov15(self):
        self.reject(0,lambda m:m["docs"][1].update(report_cutoff_printed="2400Z 08 NOVEMBER 1963"))

    def test_wrong_publication_day(self):
        self.reject(0,lambda m:m["docs"][1].update(document_day="1963-11-15"))

    def test_jan31_period_changed(self):
        self.reject(0,lambda m:m["docs"][0]["printed_rows"][1].update(nodal_period_min_printed="94.1"))

    def test_jan31_528_inclination_changed(self):
        self.reject(0,lambda m:m["docs"][0]["printed_rows"][1].update(inclination_deg_printed="81.87"))

    def test_jan31_528_perigee_changed(self):
        self.reject(0,lambda m:m["docs"][0]["printed_rows"][1].update(perigee_km_printed="476.5"))

    def test_confuses_primary_registration_with_raw_tle(self):
        self.reject(0,lambda m:m["interpretation"].update(raw_line1_line2_528="1 00528U ..."))

    def test_1977_crosswalk_swapped(self):
        self.reject(1,lambda m:m["row"].update(catalog_number_printed=529))

    def test_1963_decay_day_swapped(self):
        self.reject(2,lambda m:m["sources"][0]["human_table_observation"].update(decay_day="1963-11-15"))

    def test_53_not_3b(self):
        self.reject(0,lambda m:m["docs"][1].update(printed_no_longer_in_orbit=["1963-3A","1963-35A"]))

    def test_october_incremental_omission_as_survival(self):
        self.reject(0,lambda m:m["interpretation"].update(controls_54_55_constrain_survival=True))

    def test_utc_cutoff_is_not_sensor_epoch(self):
        self.reject(0,lambda m:m["interpretation"].update(un_cutoff_is_sensor_epoch=True))

    def test_cutoff_is_not_exact_decay(self):
        self.reject(0,lambda m:m["interpretation"].update(un_cutoff_is_verified_decay_time=True))

    def test_no_invented_sigma(self):
        self.reject(0,lambda m:m["interpretation"].update(decay_time_uncertainty_528=3600))

    def test_no_invented_station(self):
        self.reject(0,lambda m:m["interpretation"].update(historical_sensor_528="SHEMYA"))

    def test_no_independent_sensor_count(self):
        self.reject(0,lambda m:m["interpretation"].update(independent_sensor_observations_added=2))

    def test_no_premature_lean(self):
        self.reject(0,lambda m:m["interpretation"].update(lean_activated=True))

    def test_no_premature_domain(self):
        self.reject(0,lambda m:m["graph_extension"].update(physical_domain_reduced=True))

    def test_cannot_activate_utc_interval_from_reporting(self):
        self.reject(0,lambda m:m["interpretation"].update(conditional_physical_interval_activated=True))

    def test_wrong_graph_parent(self):
        self.reject(0,lambda m:m["graph_extension"].update(parent="UN_RETROPROPAGATION"))

    def test_reject_corrupted_pdfs(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as d:
            for x in SOURCES[0]["docs"]:
                (Path(d)/f"inf{int(x['number']):03d}E.pdf").write_bytes(b"%PDF-1.4\nforged\n")
            with self.assertRaisesRegex(ValueError,"bytes changed"):
                check_pdf_bytes(SOURCES[0],d)

if __name__=="__main__":
    unittest.main()
