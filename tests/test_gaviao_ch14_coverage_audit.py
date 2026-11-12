"""Synthetic adversarial tests, not historical tracking observations."""
import math, sys, unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from gaviao_ch14_coverage_audit import audit,forecast,rmse,verify
T=datetime(1963,1,1,tzinfo=timezone.utc)
def data(days=(0,2,5,10,20,34),values=None):
    values=values or [15+.1*d for d in days]
    return [(s,T+timedelta(days=d),14. if s!=529 else v)
            for s in (527,528,529) for d,v in zip(days,values)]
class Ch14Tests(unittest.TestCase):
    def test_model_specific_universes(self):
        r=audit(data())
        self.assertEqual(r["counts"],{"persistence":5,"secant_2":4,"ols_3":3})
        self.assertEqual(r["joint_count"],3)
        self.assertEqual([len(r["extra_epochs"][k]) for k in
                          ("persistence","secant_2","ols_3")],[2,1,0])
    def test_irregular_utc_seconds(self):
        r=audit(data())
        self.assertLess(r["own_rmse"]["secant_2"],1e-12)
        self.assertLess(r["own_rmse"]["ols_3"],1e-12)
    def test_no_donor_history_still_scores_target_only(self):
        rows=[r for r in data() if r[0]==529 or r[1]==T]
        r=audit(rows)
        self.assertEqual(r["counts"]["secant_2"],4)
        self.assertEqual(r["joint_count"],0)
    def test_missing_object(self):
        with self.assertRaisesRegex(ValueError,"missing"):
            audit([r for r in data() if r[0]!=527])
    def test_future_value_does_not_leak(self):
        x=audit(data())
        changed=[(s,t,v+8 if s==529 and t==T+timedelta(days=34) else v)
                 for s,t,v in data()]
        y=audit(changed)
        self.assertEqual(x["details"][-1]["forecasts"],y["details"][-1]["forecasts"])
        self.assertNotEqual(x["details"][-1]["errors"],y["details"][-1]["errors"])
    def test_identical_duplicate_not_counted_twice(self):
        rows=data()
        self.assertEqual(audit(rows+rows)["counts"],audit(rows)["counts"])
    def test_conflicting_duplicate_rejected(self):
        rows=data()
        with self.assertRaisesRegex(ValueError,"conflicting"):
            audit(rows+[(529,rows[-1][1],999.)])
    def test_invalid_epoch_and_nan_rejected(self):
        with self.assertRaisesRegex(ValueError,"invalid"):
            audit(data()+[(529,T.replace(tzinfo=None),15.)])
        with self.assertRaisesRegex(ValueError,"invalid"):
            audit(data()+[(529,T+timedelta(days=90),math.nan)])
    def test_strict_past(self):
        with self.assertRaisesRegex(ValueError,"strictly prior"):
            forecast([(T,1.)],T)
    def test_sse_identity(self):
        r=audit(data(values=[15,15.3,15.4,15.5,15.7,15.8]))
        v=r["single_extra_influence"]
        self.assertIsNotNone(v)
        self.assertAlmostEqual(v["SSE_identity_error"],0.,places=12)
        self.assertTrue(0<=v["share_of_52_secant_SSE"]<=1)
    def test_unpaired_rmse_distinct(self):
        r=audit(data(values=[15,15.3,15.4,15.5,15.7,15.8]))
        self.assertNotEqual(r["own_rmse"]["secant_2"],r["joint_rmse"]["secant_2"])
    def test_wrong_history_fails_published_gate(self):
        with self.assertRaisesRegex(ValueError,"catalog"):
            verify(audit(data()))
    def test_no_physical_conclusion(self):
        r=audit(data())
        self.assertEqual(r["conde"],"INDETERMINATE")
        self.assertFalse(r["physical_domain_reduced"])
        self.assertEqual(r["terminal_simulation"],"NOT_RUN")
    def test_single_prior_and_empty(self):
        self.assertEqual(forecast([(T,1.)],T+timedelta(days=1)),{"persistence":1.})
        self.assertIsNone(rmse([]))
if __name__=="__main__":
    unittest.main()
