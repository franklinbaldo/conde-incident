"""Adversarial tests: catalog holdings are not observations."""
import copy
import json
import unittest
from tools.verify_soviet_1963_holdings import MANIFEST, issue_row, validate


def sample(title, year, issues):
    return "<p><strong>" + title + "</strong></p><table><tr><td>" + str(year) + "</td><td>" + issues + "</td></tr></table>"


class TestSovietHoldings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_valid(self):
        self.assertEqual(validate(self.data), [])

    def test_1963_number_ranges(self):
        for r in self.data["records"]:
            numbers = r["issues"]
            s = "N" + str(numbers[0]) + (("-" + str(numbers[-1])) if len(numbers) > 1 else "")
            self.assertEqual(issue_row(sample(r["journal"], 1963, s), r["journal"]), numbers)

    def test_other_year(self):
        self.assertIsNone(issue_row(sample("Наблюдения ИСЗ", 1964, "N2"), "Наблюдения ИСЗ"))

    def test_other_journal(self):
        html = sample("Outro", 1963, "N2") + sample("Наблюдения ИСЗ", 1964, "N3")
        self.assertIsNone(issue_row(html, "Наблюдения ИСЗ"))

    def test_wrong_range(self):
        r = self.data["records"][0]
        self.assertNotEqual(issue_row(sample(r["journal"], 1963, "N32-36"), r["journal"]), r["issues"])

    def test_forged_facsimile(self):
        altered = copy.deepcopy(self.data)
        altered["records"][0]["issue_pdf_sha256"] = "0" * 64
        self.assertIn("C241-L29#1:facsimile", validate(altered))

    def test_forged_observation(self):
        altered = copy.deepcopy(self.data)
        altered["records"][1]["primary_observation_527_528_529"] = {"norad": 528}
        self.assertIn("C241-L29#2:measurement", validate(altered))

    def test_forged_orbital_activation(self):
        altered = copy.deepcopy(self.data)
        altered["orbital_constraint_activated"] = True
        self.assertIn("orbital_constraint_activated", validate(altered))


if __name__ == "__main__":
    unittest.main()
