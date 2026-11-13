"""Adversarial CGEO-34 provenance and anti-anachronism checks."""
import copy
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from tools.cgeo34_uwm_jp2 import ROOT,MANIFEST,read,verify_manifest,verify_original

class JP2CustodyTests(unittest.TestCase):
    def setUp(self):
        self.record=read(MANIFEST)
        self.parent=read(ROOT/self.record['parent_file'])
        self.header=bytes.fromhex((ROOT/self.record['asset']['header_fixture']).read_text())

    def mutate(self,change):
        d=copy.deepcopy(self.record)
        change(d)
        with self.assertRaises(ValueError):verify_manifest(d,self.parent,self.header)

    def test_real_header_and_real_parent(self):
        self.assertEqual(verify_manifest(self.record,self.parent,self.header),
                         'CGEO34_JP2_HEADER_AND_CUSTODY_PASS')

    def test_sha_and_size_tampering(self):
        self.mutate(lambda d:d['asset'].update(sha256='0'*64))
        self.mutate(lambda d:d['asset'].update(bytes=100))
        self.mutate(lambda d:d['asset'].update(header_sha256='0'*64))

    def test_false_raster_inspection(self):
        self.mutate(lambda d:d['asset'].update(full_image_visual_inspection_performed=True))

    def test_no_new_independent_measurement(self):
        self.mutate(lambda d:d.update(same_physical_map_as_parent=False))
        self.mutate(lambda d:d['scientific_limits'].update(source_survey_independent_of_parent=True))

    def test_no_fabricated_historical_coordinates(self):
        self.mutate(lambda d:d['scientific_limits'].update(urban_center_geometry_1963=[-37.6,-11.8]))
        self.mutate(lambda d:d['scientific_limits'].update(municipal_boundary_1963={'type':'Polygon'}))
        self.mutate(lambda d:d['scientific_limits'].update(observed_reentry_location=[0,0]))
        self.mutate(lambda d:d['scientific_limits'].update(horizontal_error_m=1))

    def test_change_history_not_historical_survey_date(self):
        self.mutate(lambda d:d['asset']['embedded_xml'].update(change_history_date='1963-11-08'))
        self.mutate(lambda d:d['asset']['embedded_xml'].update(bitsperpixel_consistent_with_ihdr=True))
        self.mutate(lambda d:d['asset']['embedded_xml'].update(bitsperpixel_literal='8'))

    def test_no_fabricated_aerial_date(self):
        self.mutate(lambda d:d['scientific_limits'].update(date_of_original_aerial_capture='1961-01-01'))
        self.mutate(lambda d:d['scientific_limits'].update(can_constrain_orbital_reentry=True))

    def test_edited_header_rejected(self):
        changed=bytearray(self.header);changed[8]^=1
        with self.assertRaises(ValueError):verify_manifest(self.record,self.parent,bytes(changed))

    def test_short_fake_original_rejected(self):
        with TemporaryDirectory() as tmp:
            x=Path(tmp)/'false.jp2';x.write_bytes(self.header)
            with self.assertRaises(ValueError):verify_original(x,self.record,self.header)

if __name__=='__main__':unittest.main()
