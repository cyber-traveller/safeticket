import unittest
from safeticket.support import decide


def answers(p=0.8, urgent=0.1):
    return {"team": {"probabilities": {"billing": p, "shipping": (1-p)/4, "returns": (1-p)/4, "access": (1-p)/4, "review": (1-p)/4}}, "urgent": {"noul": urgent}}


class SupportTests(unittest.TestCase):
    def test_confident_routing(self):
        self.assertEqual(decide(answers())["team"], "billing")

    def test_uncertainty_abstains(self):
        self.assertEqual(decide(answers(0.4))["action"], "human_review")

    def test_incident_overrides_confident_route(self):
        self.assertEqual(decide(answers(0.99, 0.7))["action"], "human_review")

    def test_bad_evidence_fails_closed(self):
        for data in ({}, answers(float("nan")), answers(0.8, float("inf"))):
            self.assertEqual(decide(data)["action"], "human_review")
