"""Adversarial tests for J2 proxy; actual SHA-pinned 1963 data run in CI."""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT / "formal/scripts"))
sys.path.insert(0,str(ROOT))
from audit_secondary_j2_raan import FIELDS, audit, j2_nodal_deg_day

T=datetime(1963,10,1,tzinfo=timezone.utc)


def sample(sid,t,raan,i=81.8615,motion=15.74901460,e=0.0017147):
    fields=["0"] * len(FIELDS)
    for name,value in (("raan",raan),("inclination",i),
                       ("mean_motion",motion),("eccentricity",e)):
        fields[FIELDS.index(name)]=str(value)
    return {"epoch":t, "source_rows":[sid], "state":tuple(fields)}


class SecondaryJ2Tests(unittest.TestCase):
    def test_c179_proxy_units_sign(self):
        self.assertAlmostEqual(j2_nodal_deg_day(sample(528,T,198.5261)["state"]),
                               -1.173124071,places=6)
        self.assertGreater(j2_nodal_deg_day(sample(528,T,198,i=100)["state"]),0)

    def test_12h_and_negative_short_arc(self):
        data={527:[sample(527,T,22)],
              528:[sample(528,T,359.8),sample(528,T+timedelta(hours=12),359.2)],
              529:[sample(529,T,0.1)]}
        record=audit(data)
        pair=record["objects"]["528"]["pairs"][0]
        self.assertAlmostEqual(pair["gap_hours"],12)
        self.assertAlmostEqual(pair["observed_delta_deg"],-0.6)
        self.assertLess(abs(pair["j2_signed_residual_deg"]),1)
        self.assertEqual(record["objects"]["527"]["status"],"NO_SHORT_GAP_PAIRS")

    def test_long_gap_not_interpolated(self):
        data={527:[sample(527,T,22)],
              528:[sample(528,T,359),sample(528,T+timedelta(days=2),350)],
              529:[sample(529,T,0.1)]}
        self.assertEqual(audit(data)["objects"]["528"]["adjacent_pairs_at_most_24h"],0)

    def test_bad_inputs_fail_closed(self):
        for changed in ({"i":-1},{"e":1},{"motion":-1},{"motion":float("nan")}):
            kwargs={"i":81.8615,"e":0.0017147,"motion":15.75}
            kwargs.update(changed)
            with self.subTest(changed=changed), self.assertRaisesRegex(ValueError,"invalid J2"):
                j2_nodal_deg_day(sample(528,T,198,**kwargs)["state"])

    def test_duplicate_epoch_rejected(self):
        with self.assertRaisesRegex(ValueError,"duplicate"):
            audit({527:[sample(527,T,1)],
                   528:[sample(528,T,198),sample(528,T,199)],
                   529:[sample(529,T,1)]})

    def test_180_degree_ambiguity_rejected(self):
        with self.assertRaisesRegex(ValueError,"ambiguous"):
            audit({527:[sample(527,T,1)],
                   528:[sample(528,T,10),sample(528,T+timedelta(hours=3),190)],
                   529:[sample(529,T,1)]})

    def test_non_utc_rejected(self):
        with self.assertRaisesRegex(ValueError,"UTC"):
            audit({527:[sample(527,T,1)],
                   528:[sample(528,T,198),sample(528,T.replace(tzinfo=None)+timedelta(hours=5),197)],
                   529:[sample(529,T,1)]})

    def test_no_sensor_error_or_physical_domain_shrinkage(self):
        report=audit({527:[sample(527,T,1)],528:[sample(528,T,198)],529:[sample(529,T,1)]})
        self.assertIn("NONE_NO_AUTHENTICATED",report["admissible_domain_change"])
        self.assertFalse(report["method"]["max_gap_is_sensor_sigma"])


if __name__=="__main__":
    unittest.main()
