"""Confronto dos parâmetros operacionais legados com a fonte rastreável do NORAD 528.

Este teste certifica fidelidade a UM espelho secundário. Não autentica TLE de 1963
nem estima local de reentrada; 527/529 continuam sem par orbital autenticado.
"""
import re
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PAIR = ROOT / "research/tle_custody/mirror_528_1963-10-27.tle"


def between(text, before, after):
    return text.split(before, 1)[1].split(after, 1)[0]


class LegacySourceAlignment(unittest.TestCase):
    def test_528_app_uses_traceable_literal_pair(self):
        line1, line2 = PAIR.read_text(encoding="ascii").splitlines()
        source = (ROOT / "src/lib/constants.ts").read_text(encoding="utf-8")
        block = between(source, "  528: {", "  527: {")
        self.assertIn("line1: '" + line1 + "'", block)
        self.assertIn("line2: '" + line2 + "'", block)
        for fragment in (
            "raanDeg: 198.5261",
            "eccentricity: 0.0017147",
            "argPerigeeDeg: 104.7477",
            "meanAnomalyDeg: 255.4423",
            "meanMotionRevDay: 15.74901460",
            "1963-10-27T14:40:16.132Z",
            "63300.61129783",
            "classification: 'FONTE_SECUNDARIA'",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, block)
        self.assertNotIn("284.1520", block)
        self.assertNotIn("63300.61111111", block)

    def test_python_explorations_same_sourced_epoch_and_elements(self):
        for path in ("norad528_reconstruction.py", "src/lib/pythonScriptExport.ts"):
            body = (ROOT / path).read_text(encoding="utf-8")
            with self.subTest(path=path):
                self.assertRegex(body, r"RAAN_528_DEG\s*=\s*198\.5261")
                self.assertRegex(body, r"ECCENTRICITY_528\s*=\s*0\.0017147")
                self.assertRegex(body, r"MEAN_MOTION_528_REV_DAY\s*=\s*15\.74901460")
                self.assertRegex(body, r"EPOCH_528\s*=\s*datetime\(1963,\s*10,\s*27,\s*14,\s*40,\s*16,\s*132512")
                self.assertNotIn("RAAN_528_DEG = 284.1520", body)

    def test_527_529_unverified_vectors_are_not_presented_as_primary(self):
        source = (ROOT / "src/lib/constants.ts").read_text(encoding="utf-8")
        block_527 = between(source, "  527: {", "  529: {")
        block_529 = between(source, "  529: {", "\n};")
        for block in (block_527, block_529):
            self.assertIn("classification: 'HIPOTESE'", block)
            self.assertIn("sem tle primário", block.lower())
            self.assertNotIn("DOCUMENTO_PRIMARIO_VERIFICADO", block)


    def test_timeline_does_not_pretend_to_know_decay_hour(self):
        source = (ROOT / "src/lib/constants.ts").read_text(encoding="utf-8")
        block = between(source, "id: 'OBS-08'", "id: 'OBS-09'")
        self.assertIn("time unknown", block)
        self.assertIn("horário local não observado", block)
        self.assertNotIn("23:59:00", block)
        self.assertIn("DOCUMENTO_PRIMARIO_VERIFICADO", block)

    def test_528_timeline_is_secondary_with_exact_epoch(self):
        source = (ROOT / "src/lib/constants.ts").read_text(encoding="utf-8")
        block = between(source, "id: 'OBS-06'", "id: 'OBS-07'")
        self.assertIn("63300.61129783", block)
        self.assertIn("198,5261", block)
        self.assertIn("14:40:16.132512", block)
        self.assertIn("FONTE_SECUNDARIA", block)


if __name__ == "__main__":
    unittest.main()
