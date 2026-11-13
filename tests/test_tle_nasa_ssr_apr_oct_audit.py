"""C241-L16 adversarial source provenance tests without network."""
import copy
import json
import unittest
from pathlib import Path
from tools.tle_nasa_ssr_apr_oct_audit import audit, validate

ROOT = Path(__file__).resolve().parents[1]
APR = json.loads((ROOT / "research/tle_custody/nasa_ssr_apr_oct_1963_C241-L16.json").read_text())
OCT = json.loads((ROOT / "research/tle_custody/nasa_ssr_1963_oct15_C241-L12.json").read_text())


class AuditTest(unittest.TestCase):
    def reject(self, mutate):
        a, o = copy.deepcopy(APR), copy.deepcopy(OCT)
        mutate(a, o)
        with self.assertRaises((ValueError, KeyError, TypeError)):
            validate(a, o)

    def test_three_verified_editorial_deltas(self):
        rows = validate(APR, OCT)
        self.assertEqual([x["designator"] for x in rows], ["1963-003A", "1963-003B", "1963-003C"])
        self.assertEqual([x["published_delta_period_min_not_physical_rate"] for x in rows],
                         ["0.0", "-1.7", "-1.0"])
        self.assertEqual([x["published_delta_apogee_km"] for x in rows], [-6, -104, -73])
        self.assertEqual([x["published_delta_perigee_km"] for x in rows], [2, -59, -29])
        self.assertTrue(all(x["epoch_of_elements"] is None for x in rows))

    def test_wrong_ntrs(self):
        self.reject(lambda a, o: a["april"].update(ntrs="19630012129"))

    def test_wrong_sha(self):
        self.reject(lambda a, o: a["april"].update(sha256="0" * 64))

    def test_wrong_pdf_page(self):
        self.reject(lambda a, o: a["april"].update(pdf_page_index_zero_based=7))

    def test_wrong_as_of(self):
        self.reject(lambda a, o: a["april"].update(data_as_of="EPOCH OF SENSOR"))

    def test_different_printed_period(self):
        self.reject(lambda a, o: a["april_rows"][1].update(nodal_period_min="94.0"))

    def test_forged_precision(self):
        self.reject(lambda a, o: a["april_rows"][1].update(nodal_period_min="94.10"))

    def test_different_perigee(self):
        self.reject(lambda a, o: a["april_rows"][2].update(perigee_km=436))

    def test_cross_object_swap(self):
        self.reject(lambda a, o: a["april_rows"][1].update(designator="1963-003C"))

    def test_october_source_tampered(self):
        self.reject(lambda a, o: o["catalog_rows"][1].update(nodal_period_min_printed="92.2"))

    def test_false_sensor_epoch(self):
        self.reject(lambda a, o: a["limits"].update(date_is_orbital_epoch=True))

    def test_fake_derivative(self):
        self.reject(lambda a, o: a["limits"].update(delta_is_time_derivative=True))

    def test_synthetic_frame(self):
        self.reject(lambda a, o: a["limits"].update(frame="TEME"))

    def test_synthetic_raan(self):
        self.reject(lambda a, o: a["limits"].update(raan_deg="284.1520"))

    def test_synthetic_sigma(self):
        self.reject(lambda a, o: a["limits"].update(sigma=0.1))

    def test_invented_terminal_time(self):
        self.reject(lambda a, o: a["limits"].update(terminal_time="1963-11-08T23:59Z"))

    def test_fake_intermediate_report(self):
        self.reject(lambda a, o: a["limits"].update(issue_21="FOUND"))

    def test_false_independence(self):
        self.reject(lambda a, o: a["limits"].update(source_independence="INDEPENDENT"))

    def test_not_a_pdf(self):
        with self.assertRaisesRegex(ValueError, "not PDF"):
            audit(APR, OCT, b"fake")

    def test_forged_pdf(self):
        with self.assertRaisesRegex(ValueError, "SHA-256/bytes mismatch"):
            audit(APR, OCT, b"%PDF-1.4\nFAKE\n%%EOF")


if __name__ == "__main__":
    unittest.main()
