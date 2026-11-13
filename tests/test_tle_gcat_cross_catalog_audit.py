"""C241-L14: manufactured rows test the parser, never historical evidence."""
import unittest

from tools.tle_gcat_cross_catalog_audit import LABEL, audit, unique_rows


def fixture(kind):
    # Deliberately synthetic minimal snippets, not source snapshots.
    if kind == "currentcat":
        prefix = "JCAT Satcat Piece"
        rows = [
            "S00527 00527 1963-003A P P A OPS 0180 Agena B 2313 A00324",
            f"S00528 00528 1963-003B C C X {LABEL} S00527 1963 Nov  8",
            f"S00529 00529 1963-003C C C X {LABEL} S00527 1963 Dec 31",
        ]
    else:
        prefix = "JCAT Satcat Piece"
        rows = [
            "S00527 00527 1963-003 1963-003A P A OPS 0180 A00324",
            f"S00528 00528 1963-003 1963-003B C X {LABEL} S00527",
            f"S00529 00529 1963-003 1963-003C C X {LABEL} S00527",
        ]
    return (prefix + "\n" + "\n".join(rows) + "\n").encode()


class CrossCatalogTests(unittest.TestCase):
    def setUp(self):
        self.data = {k: fixture(k) for k in ("currentcat", "satcat")}

    def bad(self, key, old, new):
        trial = dict(self.data)
        trial[key] = trial[key].replace(old.encode(), new.encode())
        with self.assertRaises(ValueError):
            audit(trial)

    def test_synthetic_control_only(self):
        result = audit(self.data)
        self.assertEqual(result["conde_outcome"], "INDETERMINATE")
        self.assertTrue(result["catalogue_name_mismatch"])
        self.assertIsNone(result["physical_component_528"])
        self.assertFalse(result["catalog_decay_day_is_terminal_time"])
        self.assertEqual(len(result["source_capture"]["satcat"]["sha256"]), 64)

    def test_missing_source_rejected(self):
        with self.assertRaises(ValueError):
            audit({"satcat": self.data["satcat"]})

    def test_missing_528_rejected(self):
        self.bad("currentcat", "S00528", "S00588")

    def test_duplicate_rejected(self):
        trial = dict(self.data)
        trial["satcat"] += self.data["satcat"].splitlines()[2] + b"\n"
        with self.assertRaises(ValueError):
            audit(trial)

    def test_wrong_cospar_rejected(self):
        self.bad("satcat", "1963-003B", "1963-003D")

    def test_parent_wrong_rejected(self):
        self.bad("currentcat", "S00527 1963 Nov", "S00526 1963 Nov")

    def test_mislabeled_debris_rejected(self):
        self.bad("satcat", "Agena D", "Agena B")

    def test_missing_527_agena_rejected(self):
        self.bad("currentcat", "Agena B 2313", "Agena D 2313")

    def test_changed_decay_day_rejected(self):
        self.bad("currentcat", "1963 Nov  8", "1963 Nov  7")

    def test_bad_encoding_rejected(self):
        with self.assertRaises(UnicodeDecodeError):
            unique_rows(b"\xff", "satcat")


if __name__ == "__main__":
    unittest.main()
