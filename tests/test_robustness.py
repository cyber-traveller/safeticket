import unittest

from safeticket.robustness import brier_score, expected_calibration_error, option_order_stability


class RobustnessTests(unittest.TestCase):
    def test_option_order_instability_is_detected(self):
        result = option_order_stability([
            {"choice": "billing", "probabilities": {"billing": .8, "shipping": .2}},
            {"choice": "shipping", "probabilities": {"billing": .3, "shipping": .7}},
        ])
        self.assertFalse(result["argmax_stable"])
        self.assertAlmostEqual(result["max_probability_spread"], .5)

    def test_brier_score(self):
        self.assertAlmostEqual(brier_score({"yes": .8, "no": .2}, "yes"), .08)

    def test_calibration_error(self):
        self.assertAlmostEqual(expected_calibration_error([
            {"confidence": .9, "correct": True},
            {"confidence": .9, "correct": False},
        ]), .4)


if __name__ == "__main__":
    unittest.main()
