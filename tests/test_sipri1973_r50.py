"""Adversarial tests for chronology, identity, custody and zero-sensor promotion."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audit_sipri1973_r50 import audit, load


class Sipri1973R50(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = load()

    def reject(self, mutate):
        v = copy.deepcopy(self.sources)
        mutate(v)
        with self.assertRaises(ValueError):
            audit(*v)

    def test_valid_source(self):
        self.assertEqual(audit(*self.sources), 'LATER_IDENTIFIED_ROW_NOT_INDEPENDENT_SENSOR')

    def test_changed_soviet_value(self):
        self.reject(lambda x: x[1]['printed_table_row'].__setitem__('period_minutes_printed', 94.65))

    def test_changed_sipri_value(self):
        self.reject(lambda x: x[0]['printed_row'].__setitem__('perigee_km', 458))

    def test_false_soviet_id(self):
        self.reject(lambda x: x[1]['printed_table_row'].__setitem__('norad_identifier_printed', 527))

    def test_false_soviet_sipri_copy(self):
        self.reject(lambda x: x[0]['comparison'].__setitem__('soviet_1964_derived_from_sipri_1973_possible', True))

    def test_false_soviet_sensor(self):
        self.reject(lambda x: x[0]['comparison'].__setitem__('independent_instrumental_sources_count_added', 1))

    def test_false_528_orbit(self):
        self.reject(lambda x: x[0]['printed_row'].__setitem__('designation', 'USAF (1963-03B)'))

    def test_false_observation_epoch(self):
        self.reject(lambda x: x[0]['printed_row'].__setitem__('observation_epoch_utc', '1963-11-08T00:00:00Z'))

    def test_wrong_book_date(self):
        self.reject(lambda x: x[0]['source'].__setitem__('publication_year', 1963))

    def test_fake_visual_check(self):
        self.reject(lambda x: x[0]['source'].__setitem__('critical_page_visually_inspected', True))

    def test_fake_pdf_digest(self):
        self.reject(lambda x: x[0]['source'].__setitem__('pdf_sha256', '0'*64))

    def test_fake_constraints(self):
        self.reject(lambda x: x[0]['comparison'].__setitem__('new_physical_constraints_activated', 1))

    def test_fake_external_contact(self):
        self.reject(lambda x: x[0]['source'].__setitem__('archive_external_contact_sent', True))

    def test_corrupt_pdf_replay(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / 'fake.pdf'
            p.write_bytes(b'%PDF-1.6\n%%EOF')
            with self.assertRaises(ValueError):
                audit(*self.sources, pdf_path=p)


if __name__ == '__main__':
    unittest.main()
