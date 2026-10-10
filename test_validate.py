import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADER = ["record_id", "text", "label", "dataset_version"]


class ValidationTests(unittest.TestCase):
    def run_csv(self, rows, header=HEADER, version="1.0.0"):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "dataset.csv"
            with path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.writer(stream)
                writer.writerow(header)
                writer.writerows(rows)
            return subprocess.run(
                [sys.executable, str(ROOT / "validate.py"), str(path), "--expected-version", version],
                capture_output=True, text=True,
            )

    def row(self, **changes):
        values = dict(zip(HEADER, ["1", "Good service", "positive", "1.0.0"]))
        values.update(changes)
        return [values[key] for key in HEADER]

    def test_valid(self):
        result = self.run_csv([self.row(), self.row(record_id="2", text="Comma, within text")])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Validated 2 rows", result.stdout)

    def test_invalid_fields(self):
        cases = [
            ({"record_id": "0"}, "positive integer"),
            ({"record_id": "abc"}, "positive integer"),
            ({"record_id": "1.5"}, "positive integer"),
            ({"text": "   "}, "text is blank"),
            ({"label": "invalid"}, "invalid label"),
            ({"dataset_version": "2.0.0"}, "dataset_version"),
        ]
        for changes, message in cases:
            with self.subTest(changes=changes):
                result = self.run_csv([self.row(**changes)])
                self.assertEqual(result.returncode, 1)
                self.assertIn(message, result.stderr)

    def test_duplicate(self):
        result = self.run_csv([self.row(), self.row(record_id="01")])
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate", result.stderr)

    def test_bad_header(self):
        result = self.run_csv([], header=["wrong"])
        self.assertEqual(result.returncode, 1)
        self.assertIn("Header", result.stderr)

    def test_empty(self):
        result = self.run_csv([])
        self.assertEqual(result.returncode, 1)
        self.assertIn("no data rows", result.stderr)

    def test_field_count(self):
        for row in [self.row()[:-1], self.row() + ["extra"]]:
            result = self.run_csv([row])
            self.assertEqual(result.returncode, 1)
            self.assertIn("number of fields", result.stderr)

    def test_expected_version(self):
        result = self.run_csv([self.row()], version="2.0.0")
        self.assertEqual(result.returncode, 1)
        self.assertIn("dataset_version", result.stderr)

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run(
                [sys.executable, str(ROOT / "validate.py"), str(Path(folder) / "missing.csv")],
                capture_output=True, text=True,
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("cannot validate", result.stderr)


if __name__ == "__main__":
    unittest.main()
