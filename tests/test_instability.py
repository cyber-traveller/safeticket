import unittest

from safeticket.serve import _decision_after_instability, _recover_clear_injection_route


def review(reason):
    return {'action': 'human_review', 'team': None, 'reason': reason}


class UnstableOptionOrderTests(unittest.TestCase):
    def test_safety_reviews_are_never_turned_into_routes(self):
        tickets = [
            ('There is a charge on my statement that I never authorized.', 'possible_security_or_payment_incident'),
            ('A fraud charge appeared on my statement.', 'possible_security_or_payment_incident'),
            ('A payment on my statement was made without my permission.', 'possible_security_or_payment_incident'),
            ('Please send my invoice, I have not authorised this payment.', 'possible_security_or_payment_incident'),
            ('Track my parcel and also reset my password.', 'multiple_unresolved_requests'),
        ]
        for ticket, reason in tickets:
            decision = _decision_after_instability(review(reason), ticket)
            self.assertEqual(decision, review(reason), ticket)

    def test_invalid_evidence_stays_in_review(self):
        decision = _decision_after_instability(review('invalid_distribution'), 'Where is my parcel?')
        self.assertEqual(decision['action'], 'human_review')
        self.assertEqual(decision['reason'], 'invalid_distribution')

    def test_incident_wording_is_never_recovered(self):
        for ticket in ['A fraud charge appeared on my statement.', 'Someone used my card for this receipt.',
                       'A hacker changed my password and my parcel is missing.']:
            self.assertIsNone(_recover_clear_injection_route(ticket), ticket)

    def test_unstable_route_without_a_clear_recovery_goes_to_review(self):
        route = {'action': 'route', 'team': 'billing', 'reason': 'eligibility_and_routing_agree'}
        decision = _decision_after_instability(route, 'Something about my order.')
        self.assertEqual((decision['action'], decision['reason']), ('human_review', 'option_order_instability'))

    def test_clear_single_intent_can_still_be_recovered(self):
        decision = _decision_after_instability(review('low_model_probability'), 'Please track my parcel, tracking number 12345 expected arrival Monday.')
        self.assertEqual((decision['action'], decision['team']), ('route', 'shipping'))


if __name__ == '__main__':
    unittest.main()
