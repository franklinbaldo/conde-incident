import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT/'tools/tle_1963_tracking_precision_audit.py'
spec=importlib.util.spec_from_file_location('precision', PATH)
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
DATA=json.loads(audit.LEDGER.read_text())


class TrackingCapabilityTests(unittest.TestCase):
    def test_original(self):
        v=audit.validate(DATA)
        self.assertEqual((v['catalog_decay_day_528'],v['physical_bounds_activated']),('1963-11-08',0))

    def reject(self, mutation):
        d=copy.deepcopy(DATA)
        mutation(d)
        with self.assertRaises(ValueError): audit.validate(d)

    def test_launder_publication_as_epoch(self):
        self.reject(lambda d:d['sources'][0].__setitem__('observation_epoch_known',True))

    def test_launder_camera_precision_as_528_sigma(self):
        self.reject(lambda d:d['documentary_observables'][1].__setitem__('measurement_sigma',0.00001))

    def test_invent_terminal_hour(self):
        self.reject(lambda d:d['documentary_observables'][0].__setitem__('time_utc','1963-11-08T23:59:00Z'))

    def test_launder_other_object_observation(self):
        self.reject(lambda d:d['documentary_observables'][3].__setitem__('linked_to_528',True))

    def test_retag_norad(self):
        self.reject(lambda d:d['documentary_observables'][0].__setitem__('object_norad',527))

    def test_fake_station(self):
        self.reject(lambda d:d['object_measurement_custody'][1].__setitem__('station_id','Diyarbakir'))

    def test_skip_dependency_edge(self):
        self.reject(lambda d:d['links'].pop())

    def test_source_digest_replacement(self):
        self.reject(lambda d:d['sources'][0].__setitem__('sha256','0'*64))

    def test_false_activation(self):
        self.reject(lambda d:d['links'][0].__setitem__('status','ACTIVE_REENTRY_CONSTRAINT'))

    def test_local_source_tamper(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as t:
            for n in audit.RAW_FILENAMES.values(): (Path(t)/n).write_bytes(b'x')
            with self.assertRaises(ValueError): audit.validate(DATA,t)


if __name__=='__main__': unittest.main()
