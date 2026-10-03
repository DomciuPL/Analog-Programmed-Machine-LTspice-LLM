"""Regression checks for LTspice log handling; fixtures are synthetic."""
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import run_ltspice


class LogHandling(unittest.TestCase):
    def test_scalar_measurements_and_failed_measurement(self):
        text = """LTspice log fixture
gain_value: v(gain)=4 at 0.001
tau_error: abs(t_tau-1/450)=1.2e-9
Measurement "missing" FAIL'ed
"""
        result = run_ltspice.parse_log(text)
        self.assertEqual(result["gain_value"], [4])
        self.assertEqual(result["tau_error"], [1.2e-9])
        self.assertNotIn("missing", result)

    def test_step_tables_keep_all_runs_and_distinct_names(self):
        text = """Measurement: nominal
  step  PARAM
  1 -2
  2 2
  3 -2.0e+00
Measurement: error
  step  abs(x) FROM TO
  1 1e-9 0 1
  2 2e-9 0 1
  3 3e-9 0 1
"""
        result = run_ltspice.parse_log(text)
        self.assertEqual(result["nominal"], [-2, 2, -2])
        self.assertEqual(result["error"], [1e-9, 2e-9, 3e-9])
        case = {"runs": 3, "limits": {"error": [0, 1e-8]}}
        self.assertEqual(run_ltspice.acceptance(case, result), [])

    def test_missing_extra_and_out_of_range_runs_fail(self):
        case = {"runs": 2, "limits": {"error": [0, 1e-5]}}
        for values in ({}, {"error": [0]}, {"error": [0, 0, 0]},
                       {"error": [0, 2e-5]}, {"error": [0, math.nan]},
                       {"error": [0, math.inf]}):
            with self.subTest(values=values):
                self.assertTrue(run_ltspice.acceptance(case, values))

    def test_windows_log_encodings(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "case.log"
            for encoding in ("utf-8-sig", "utf-16", "cp1252"):
                expected = "gain: v(gain)=4\nDuration: 1 \u00b5s\n"
                path.write_bytes(expected.encode(encoding))
                self.assertEqual(run_ltspice.read_log(path), expected)

    def test_manifest_coverage_and_list_mode(self):
        manifest = json.loads((ROOT / "tests/acceptance.json").read_text())
        self.assertEqual(len(manifest["cases"]), 20)
        self.assertEqual(sum(case["runs"] for case in manifest["cases"]), 31)
        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(run_ltspice.main(["--suite", "all", "--list"]), 0)
        self.assertEqual(len(output.getvalue().splitlines()), 20)

    def test_missing_simulator_is_not_reported_as_success(self):
        with patch.object(run_ltspice, "find_executable", return_value=None):
            with redirect_stderr(io.StringIO()) as output:
                self.assertEqual(run_ltspice.main([]), 2)
        self.assertIn("No simulations were performed", output.getvalue())


if __name__ == "__main__":
    unittest.main()

