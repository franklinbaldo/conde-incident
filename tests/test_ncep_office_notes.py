"""Offline catalog parser tests: historical note != decoded ON20 report."""
import unittest

from tools.audit_ncep_office_notes import extract_notes

BASE = "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}<br><a href='{}'>PDF</a></td></tr>"
LINK = "http://www.ncep.noaa.gov/officenotes/NOAA-NPM-NCEPON-0001/{}.pdf"
ITEMS = [
    (16, "1960 1963*", "Dent G. R.", "Hydrostatic and Wind Check in the ADP Program (1963)", "013FD4C3"),
    (20, "1964", "Neilon J.", "Upper Air ADP Records Format (revision beginning on page 12)", "013FD4DB"),
    (22, "1964", "NMC staff", "ADP 3rd Word", "013FD4E4"),
    (26, "1968", "Loman L.", "Structure of the NMC B3 Data Tape", "013FD507"),
]


def fixture(items=ITEMS):
    return ("<table>" + "".join(BASE.format(n, y, a, t, LINK.format(f))
                                for n, y, a, t, f in items) + "</table>").encode()


class OfficeNoteLocatorTests(unittest.TestCase):
    def test_four_locators_and_original_year(self):
        notes = extract_notes(fixture())
        self.assertEqual([n["number"] for n in notes], [16, 20, 22, 26])
        self.assertEqual(notes[1]["year_as_catalogued"], "1964")
        self.assertFalse(notes[1]["pdf_downloaded"])
        self.assertIsNone(notes[1]["pdf_sha256"])

    def test_reject_missing_note(self):
        with self.assertRaisesRegex(ValueError, "missing Office Notes"):
            extract_notes(fixture(ITEMS[:-1]))

    def test_reject_duplicate_note(self):
        with self.assertRaisesRegex(ValueError, "duplicate Office Note 20"):
            extract_notes(fixture(ITEMS + [ITEMS[1]]))

    def test_reject_unfounded_backdating(self):
        changed = list(ITEMS)
        changed[1] = (20, "1963", changed[1][2], changed[1][3], changed[1][4])
        with self.assertRaisesRegex(ValueError, "title/year"):
            extract_notes(fixture(changed))

    def test_reject_missing_pdf_locator(self):
        html = fixture().replace(b"013FD4DB.pdf", b"013FD4DB.txt")
        with self.assertRaisesRegex(ValueError, "one PDF catalog link"):
            extract_notes(html)


if __name__ == "__main__":
    unittest.main()
