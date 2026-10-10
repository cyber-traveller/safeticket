import json
import unittest
from pathlib import Path

from benchmarks.run_baseline import validate_response


class BenchmarkContractTests(unittest.TestCase):
    def test_fixture_has_stable_question_contract(self):
        fixture = json.loads(
            (Path(__file__).parent.parent / "benchmarks/fixtures/systemone.json").read_text()
        )
        self.assertEqual(set(fixture["questions"]), {"department", "escalate", "frustration"})
        self.assertEqual(fixture["questions"]["department"]["type"], "choice")
        self.assertEqual(fixture["questions"]["escalate"]["type"], "noul")
        self.assertEqual(fixture["questions"]["frustration"]["type"], "score")

    def test_response_shape(self):
        validate_response({"answers": {"department": {}, "escalate": {}, "frustration": {}}})

    def test_missing_answer_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_response({"answers": {"department": {}, "escalate": {}}})


if __name__ == "__main__":
    unittest.main()

