"""Adversarial audit of 1963 exclusion from only the named dated collections."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('zven_dates',ROOT/'tools/verify_zvenigorod_collection_dates.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class DateAudit(unittest.TestCase):
    def setUp(self):self.d=json.loads(module.MANIFEST.read_text())
    def reject(self,path,value):
        doc=copy.deepcopy(self.d);p=doc
        for key in path[:-1]:p=p[key]
        p[path[-1]]=value
        with self.assertRaises(AssertionError):module.validate(doc)
    def test_manifest(self):self.assertTrue(module.validate(self.d))
    def test_pdf_hash_and_size(self):
        self.reject(['sources',0,'sha256'],'0'*64)
        self.reject(['sources',1,'bytes'],8854647)
        self.reject(['sources',0,'url'],'https://fake.example/pdf')
    def test_printed_page_and_visual_confidence(self):
        self.reject(['sources',0,'printed_pages'],'1-3')
        self.reject(['sources',0,'page_checked_visually'],True)
        self.reject(['sources',1,'checked_pdf_pages_1based'],[125,126])
    def test_instrument_dates_and_counts(self):
        self.reject(['inventory_as_reported_in_2012',1,'from_year'],1963)
        self.reject(['inventory_as_reported_in_2012',2,'to_year'],1963)
        self.reject(['inventory_as_reported_in_2014','AFU_film_count'],2800)
    def test_archive_ids(self):
        self.reject(['inventory_as_reported_in_2014','WFPDB_AFU_instrument_code'],'040')
        self.reject(['inventory_as_reported_in_2014','AFU_scanning_planned'],True)
    def test_no_universal_negative_or_orbit(self):
        self.reject(['scope'],'all_soviet_observations_1963')
        self.reject(['does_not_establish','any_other_1963_AFU_archive_absent'],False)
        self.reject(['orbits','new_independent_measurements'],1)
        self.reject(['orbits','orbital_constraints_activated'],1)
        self.reject(['outreach_sent'],True)
    def test_replay_real_pdfs_if_present(self):
        d=Path('/workspace/lontra-r36-sources')
        if not all((d/n).exists() for n in ['VIIBSAC.pdf','astroplate_2014_proceedings.pdf']):
            self.skipTest('Primary PDFs not stored in Git or CI')
        module.validate(self.d,[d/'VIIBSAC.pdf',d/'astroplate_2014_proceedings.pdf'])

if __name__=='__main__':unittest.main()
