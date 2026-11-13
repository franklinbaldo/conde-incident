"""C241: adversarial tests of frozen-holdout effective drag and angular contrast.

Synthetic state fields in tests validate code paths, not 1963 measurements.
The CI separately replays the real SHA-pinned Parquet/CSV data.
"""
import copy
import json
import math
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path

from tools.norad528_effective_drag_screen import (
    altitude_proxy, plane_angle_deg, angular_pair_diagnostics, elapsed,
    fit, height_at, raan_at, evaluate, crossing, blocks, compute, START, END,
    THRESHOLD_KM,
)

ROOT=Path(__file__).resolve().parents[1]
SPLIT=json.loads((ROOT/"research/statistics/raan_chronological_holdout_1963.json").read_text())
PREC=json.loads((ROOT/"research/constraints/nasa_528_decay_precision_C197_20261113.json").read_text())
RAAN=json.loads((ROOT/"research/statistics/raan_527_528_529_1963.json").read_text())

def synthetic_secondary_shape():
    """Only the timestamps and RAAN are historical secondary catalog values."""
    first=datetime(1963,1,1,tzinfo=timezone.utc)
    ids={527:"1963-003A",528:"1963-003B",529:"1963-003C"}
    out=[]
    for ix,row in enumerate(RAAN["records"]):
        sid=row["norad"]
        t=datetime.fromisoformat(row["epoch_utc"].replace("Z","+00:00"))
        x=(t-first).total_seconds()/86400
        out.append({
            "norad_id":str(sid),"source_row":str(ix),
            "epoch":row["epoch_utc"],
            "inclination":"81.87","raan":str(row["raan_deg"]),
            "eccentricity":"0.005","arg_perigee":"45",
            "mean_anomaly":"25",
            "mean_motion":str(15.0+0.0001*x),
            "mean_motion_dot":"0","bstar":"0",
            "intl_designator":ids[sid],
            "altitude_km":"400",
        })
    return out

class OrbitalScreen(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fake=synthetic_secondary_shape()
        cls.data=blocks(cls.fake,SPLIT)

    def test_fixed_45_epoch_split_and_controls(self):
        self.assertEqual([sum(len(g) for g in self.data[n].values())
                          for n in (527,528,529)],[20,45,54])

    def test_kepler_proxy_monotonic(self):
        self.assertGreater(altitude_proxy(15),altitude_proxy(15.01))

    def test_reject_bad_motion(self):
        for value in (0,-1,float("nan")):
            with self.assertRaises(ValueError):
                altitude_proxy(value)

    def test_plane_angle_identical_normals(self):
        self.assertAlmostEqual(plane_angle_deg(81.87,10,81.87,10),0,places=5)

    def test_plane_angle_wrap(self):
        self.assertAlmostEqual(plane_angle_deg(81.87,359,81.87,1),
                               plane_angle_deg(81.87,-1,81.87,1),places=9)

    def test_not_force_constant_orbital_plane(self):
        close=plane_angle_deg(81.87,198,81.87,199)
        distant=plane_angle_deg(81.87,198,81.87,205)
        self.assertGreater(distant,close)

    def test_reject_invalid_plane(self):
        with self.assertRaises(ValueError):
            plane_angle_deg(181,198,81,190)

    def test_fitted_k_nonnegative(self):
        m=fit(self.data[528]["fit"],60.)
        self.assertGreaterEqual(m["k"],0)

    def test_analytic_h_at_anchor(self):
        m=fit(self.data[528]["fit"],60.)
        self.assertAlmostEqual(height_at(m,0),m["anchor"]["h"],places=7)

    def test_no_drag_keeps_proxy_altitude(self):
        m=fit(self.data[528]["fit"],60.)
        self.assertAlmostEqual(height_at(m,12,True),m["anchor"]["h"],places=7)

    def test_raan_precession_not_constant(self):
        m=fit(self.data[528]["fit"],60.)
        self.assertNotEqual(raan_at(m,1,zero_drag=True),m["anchor"]["raan"])

    def test_workflow_covers_all_source_and_proof_inputs(self):
        """A source-only PR must trigger the real Parquet/J2/Lean replay.

        The universal integration job runs synthetic tests but does not
        fetch the source-pinned numeric Parquet or emit this workflow's JSON.
        """
        import re
        workflow=(ROOT/'.github/workflows/norad528-effective-drag-screen.yml').read_text()
        required={
            'tools/norad528_effective_drag_screen.py',
            'tests/test_norad528_effective_drag_screen.py',
            'tools/cross_object_epoch_support.py',
            'tools/tle_secondary_1963_ledger.py',
            'research/statistics/raan_chronological_holdout_1963.json',
            'research/statistics/raan_527_528_529_1963.json',
            'research/constraints/nasa_528_decay_precision_C197_20261113.json',
            'research/tle_custody/mirror_528_1963-10-27.tle',
            'formal/Conde1963/Norad528DecayWindow.lean',
            'formal/Conde1963/CoreAxioms.lean',
            'formal/lean-toolchain',
            'formal/lakefile.toml',
        }
        for event in ('pull_request','push'):
            section=re.search(r'(?ms)^  '+event+r':\n(.*?)(?=^  [a-z_]+:|^permissions:|\Z)',workflow)
            self.assertIsNotNone(section, 'missing workflow event '+event)
            block=re.search(r'(?m)^    paths:\n((?:^      - [^\n]+\n)+)',section.group(1))
            self.assertIsNotNone(block,'missing path filters '+event)
            listed={line.strip().removeprefix('- ').strip('\"\'')
                    for line in block.group(1).splitlines()}
            self.assertFalse(required-listed,
                f'{event}: scientific replay will not run on source-only changes: {sorted(required-listed)}')

    def test_zero_drag_no_threshold(self):
        m=fit(self.data[528]["fit"],60.)
        m["k"]=0.
        self.assertIsNone(crossing(m))

    def test_scenario_ends_before_november_ninth(self):
        self.assertTrue(START<=datetime(1963,11,8,12,tzinfo=timezone.utc)<END)
        self.assertFalse(START<=datetime(1963,11,9,tzinfo=timezone.utc)<END)
        self.assertEqual(THRESHOLD_KM,120.)

    def test_frozen_split_rejects_temporal_leakage(self):
        bad=copy.deepcopy(SPLIT)
        bad["memberships"]["528"]["fit"].append(bad["memberships"]["528"]["evaluation"][0])
        with self.assertRaises(ValueError):
            blocks(self.fake,bad)

    def test_nasa_date_not_observation(self):
        bad=copy.deepcopy(PREC)
        bad["conditional_predicate"]["active"]=True
        with self.assertRaises(ValueError):
            compute(self.fake,SPLIT,bad)

    def test_asynchronous_pairs_are_not_sensor_error(self):
        models={sid:fit(self.data[sid]["fit"],60.) for sid in (527,528,529)}
        result=angular_pair_diagnostics(self.data,models)
        self.assertEqual(set(result),{"527","529"})
        for key,item in result.items():
            self.assertFalse(item["hard_angular_cap_active"])
            self.assertIsNone(item["historical_angular_sigma_deg"])
            self.assertFalse(item["coepoch_or_independent_sensor_measurement"])
            self.assertTrue(all(0<=row["epoch_offset_hours_NOT_sigma"]<=72
                                for row in item["records"]))

    def test_no_invented_orbit_certainty(self):
        output=compute(self.fake,SPLIT,PREC)
        self.assertEqual(output["source"]["kind"],"SECONDARY_ONE_LINEAGE")
        self.assertFalse(output["historical_fit_authenticated"])
        self.assertFalse(output["physical_domain_reduced"])
        self.assertFalse(output["terminal_scenario"]["source_proves_window"])
        self.assertIsNone(output["nasa_norad_constant_angular_sigma"])
        self.assertEqual(output["conde"],"INDETERMINATE")

if __name__=="__main__":
    unittest.main()
