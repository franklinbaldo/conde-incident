"""Adversarial offline replay of actual SGB DocReader query-state excerpts."""
import copy
import unittest
from tools.cgeo28_docreader_query_state import (ROOT, MANIFEST, PRIOR, load,
    inspect, validate, verify_full)


class ReaderQueryStateTests(unittest.TestCase):
    def setUp(self):
        self.record = load(MANIFEST)
        self.prior = load(PRIOR)
        self.excerpts = {o['query']:(ROOT/o['excerpt']).read_bytes()
                         for o in self.record['observations']}

    def test_three_queries_share_same_unrelated_folder(self):
        self.assertEqual(validate(self.record,self.prior,self.excerpts),
                         'READER_GET_QUERY_IS_NOT_PROOF_OF_EXECUTED_SEARCH')
        self.assertEqual({inspect(x).folder_text.strip() for x in self.excerpts.values()},
                         {self.record['shared_active_folder']})

    def test_replay_four_original_http_bodies_when_available(self):
        directory = ROOT.parent/'caranguejo-r26-evidence'
        if directory.is_dir():
            raw = {'Esplanada':(directory/'Esplanada.html').read_bytes(),
                   '53 D':(directory/'53_20D.html').read_bytes(),
                   'MI 1850':(directory/'MI_201850.html').read_bytes()}
            self.assertEqual(verify_full(self.record,raw,(directory/'Esplanada_POST.html').read_bytes()),
                             'FOUR_REAL_HTTP_BODIES_REPLAY_PASS')

    def test_corrupted_actual_dom_excerpt_rejected(self):
        bad = dict(self.excerpts)
        bad['53 D'] = bad['53 D'].replace(b'53 D',b'53 E')
        with self.assertRaises(ValueError):
            validate(self.record,self.prior,bad)

    def test_fake_positive_and_fake_negative_search_results_rejected(self):
        for field,value in [('catalogue_result_status','NO_RESULTS'),
                            ('target_record_absent',True),('target_record_found',True),
                            ('conclusion','53D_FOUND')]:
            bad=copy.deepcopy(self.record)
            bad[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):
                validate(bad,self.prior,self.excerpts)

    def test_misidentified_folder_and_faked_search_execution_rejected(self):
        for target,field,value in [('observation','search_executed_confirmed',True),
                                   ('postback','search_execution_confirmed',True),
                                   ('record','shared_folder_pages','/1')]:
            bad=copy.deepcopy(self.record)
            if target=='observation':bad['observations'][0][field]=value
            elif target=='postback':bad['postback_attempt'][field]=value
            else:bad[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):
                validate(bad,self.prior,self.excerpts)

    def test_no_fake_orbital_or_historic_coordinates(self):
        for key,value in [('historical_center_geometry',[0,0]),('event_position_1963',[0,0]),
                          ('horizontal_error_m',1),('project_53d_mi1850_inventory_hit',False),
                          ('can_constrain_orbital_reentry',True)]:
            bad=copy.deepcopy(self.record)
            bad['scientific_limits'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                validate(bad,self.prior,self.excerpts)

    def test_custody_and_lineage_tampering_rejected(self):
        bad=copy.deepcopy(self.record)
        bad['observations'][0]['excerpt_sha256']='0'*64
        with self.assertRaises(ValueError):validate(bad,self.prior,self.excerpts)
        bad=copy.deepcopy(self.record)
        bad['graph_edges'].pop()
        with self.assertRaises(ValueError):validate(bad,self.prior,self.excerpts)


if __name__=='__main__':
    unittest.main()
