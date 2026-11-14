"""Joint NASA-day × orbital confidence has per-draw, not aggregate, weights."""
import copy
import json
import math
import tempfile
import unittest
from pathlib import Path

import numpy as np

from tools.c241_joint_orbit_day_heatmap import (
    DAY8, DAY9, MODES, ORBIT_SIGMAS, PHASE, NDOT, TIME_SIGMAS,
    aeqd, compute, gmst_rad, likelihood_orbit, likelihood_time,
    load_sources, shortest_phase, subpoint, weights_for_sample,
)

class JointProbability(unittest.TestCase):
    def test_secondary_tle_and_nasa_day_source_locked(self):
        state=load_sources()
        self.assertAlmostEqual(state["node"],198.5261)
        self.assertAlmostEqual(state["anomaly"],255.4423)
        self.assertAlmostEqual(state["ndot"],.01373126,places=10)

    def test_bilateral_time_likelihood_positive_on_both_days(self):
        times=np.array([DAY8-6*3600,DAY8+12*3600,DAY9+6*3600])
        for sigma in TIME_SIGMAS:
            w=likelihood_time(times,sigma)
            self.assertTrue(np.all(w>0))
            self.assertAlmostEqual(w[0],w[2],places=12)
            self.assertGreater(w[1],w[0])

    def test_timing_sigma_missing_or_unlisted_never_defaults(self):
        with self.assertRaisesRegex(ValueError,"time sigma"):
            likelihood_time(np.array([DAY8]),3)

    def test_phase_circular_wrap(self):
        ids=np.arange(12,dtype=np.int16)
        self.assertTrue(np.array_equal(shortest_phase(ids[:4]),
            np.array([0.,90.,-180.,-90.])))
        self.assertTrue(np.all(np.isfinite(likelihood_orbit(ids,"middle"))))

    def test_orbit_error_penalties_produce_different_sharpness(self):
        ids=np.array([1,2,6],dtype=np.int16)
        tight=likelihood_orbit(ids,"tight")
        broad=likelihood_orbit(ids,"broad")
        self.assertTrue(np.all(tight < broad))

    def test_same_draw_joint_equals_product_of_likelihoods(self):
        ids=np.array([0,1,7,10,11],dtype=np.int16)
        t=np.array([DAY8,DAY9,DAY8+3*3600,DAY8-48*3600,DAY8])
        w=weights_for_sample(ids,t)
        self.assertIn("joint_middle_12h",MODES)
        np.testing.assert_allclose(w["joint_middle_12h"],
            w["orbital_middle"]*w["temporal_12h"],rtol=0,atol=1e-16)

    def test_independent_aggregate_percentage_product_is_wrong(self):
        ids=np.array([0,2,4,10],dtype=np.int16)
        t=np.array([DAY8+3600,DAY9+2*3600,DAY8-30*3600,DAY8+20*3600])
        w=weights_for_sample(ids,t)
        mask=np.array([True,False,True,False])
        p_joint=w["joint_middle_12h"][mask].sum()/w["joint_middle_12h"].sum()
        p_orb=w["orbital_middle"][mask].sum()/w["orbital_middle"].sum()
        p_time=w["temporal_12h"][mask].sum()/w["temporal_12h"].sum()
        self.assertGreater(abs(p_joint-p_orb*p_time),.001)

    def test_ground_subpoint_finite_and_periodic_gmst(self):
        state=load_sources()
        times=np.array([DAY8,DAY8+3*3600,DAY9])
        ids=np.array([0,5,11],dtype=np.int16)
        lat,lon=subpoint(times,ids,state)
        self.assertTrue(np.all(np.abs(lat)<90))
        self.assertTrue(np.all(np.abs(lon)<=180))
        self.assertTrue(np.all(np.isfinite(gmst_rad(times))))

    def test_spherical_azimuthal_equidistant_exact_centre(self):
        x,y,r=aeqd(np.array([-11.8139]),np.array([-37.6108]))
        self.assertLess(abs(x[0]),1e-7)
        self.assertLess(abs(y[0]),1e-7)
        self.assertLess(abs(r[0]),1e-7)

    def test_spherical_distance_approx_111km_per_latitude(self):
        x,y,r=aeqd(np.array([-10.8139]),np.array([-37.6108]))
        self.assertTrue(110 < y[0] < 112)
        self.assertLess(abs(x[0]),1e-7)
        self.assertAlmostEqual(r[0],abs(y[0]),places=6)

    def test_invalid_draw_options_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            for n,seed,batch in [(99,19631108,1000),(100,0,1000),
                                 (100,100,0),(100,100,200001)]:
                with self.subTest(n=n,seed=seed,batch=batch):
                    with self.assertRaises(ValueError):
                        compute(n,seed,batch,Path(folder))

    def test_same_samples_generate_four_coherent_maps_and_normalized_bands(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            x=compute(6000,19631108,6000,root,save_draws=True)
            self.assertIsNone(x["historical_Conde_impact_posterior"])
            self.assertIsNone(x["historical_reentry_probability"])
            self.assertFalse(x["assumptions"]["sensor_sigma_historically_calibrated"])
            self.assertEqual(len(x["results"]),len(MODES))
            self.assertEqual(x["sample"]["n"],6000)
            for mode in MODES:
                row=x["results"][mode]
                self.assertTrue(0<=row["probability_within_2000km"]<=1)
                self.assertTrue(0<row["effective_sample_size"]<=6000.00001)
            with (root/"cells_200km.csv").open() as f:
                rows=list(__import__("csv").DictReader(f))
            self.assertEqual(len(rows),400)
            for mode in ("baseline","orbital_middle","temporal_12h","joint_middle_12h"):
                total=sum(float(r[mode+"_global_probability"]) for r in rows)
                self.assertAlmostEqual(total,x["results"][mode][
                    "probability_within_2000km"],places=10)
                conditional=sum(float(r[mode+"_conditional_within_circle"]) for r in rows)
                self.assertAlmostEqual(conditional,1,places=10)
            d=np.load(root/"individual_candidates.npy",mmap_mode="r")
            self.assertEqual(len(d),6000)
            self.assertEqual(set(d.dtype.names),{
                "unix_utc_seconds","scenario_id","latitude_deg",
                "longitude_deg","x_east_km","y_north_km",
                "distance_from_conde_km"})
            self.assertTrue(np.all((d["scenario_id"]>=0)&(d["scenario_id"]<12)))
            self.assertTrue(np.all(np.isfinite(d["distance_from_conde_km"])))

    def test_reproducible_on_same_seed_and_batch(self):
        with tempfile.TemporaryDirectory() as d:
            first=compute(4000,19631108,4000,Path(d)/"a")
            second=compute(4000,19631108,4000,Path(d)/"b")
            self.assertEqual(first["results"],second["results"])
            self.assertEqual((Path(d)/"a"/"cells_200km.csv").read_bytes(),
                             (Path(d)/"b"/"cells_200km.csv").read_bytes())

    def test_time_prior_not_mistaken_for_nasa_provenance(self):
        with tempfile.TemporaryDirectory() as d:
            s=compute(3000,19631108,3000,Path(d))
        self.assertTrue(s["assumptions"]["uniform_utc_prior_not_a_NASA_assertion"]
                        if "uniform_utc_prior_not_a_NASA_assertion" in s["assumptions"]
                        else s["assumptions"]["time_prior"].startswith("UNIFORM_"))
        self.assertTrue(s["assumptions"]["not_SGP4_or_reentry_dynamics"])
        self.assertFalse(s["assumptions"]["fragment_ablation_or_survival_modeled"])

if __name__=="__main__":
    unittest.main()
