import unittest

from safeticket.banking_taxonomy import classify, legacy_team


class BankingTaxonomyTests(unittest.TestCase):
    def test_security_fails_closed(self):
        result = classify('Someone else changed my recovery email.')
        self.assertEqual(result['action'], 'human_review')
        self.assertEqual(result['domain'], 'security')

    def test_transfer_domain(self):
        result = classify('Why is my bank transfer still pending?')
        self.assertEqual((result['action'], result['domain']), ('route', 'transfers'))

    def test_topup_domain(self):
        result = classify('My top-up failed.')
        self.assertEqual((result['action'], result['domain']), ('route', 'topups'))

    def test_ambiguous_review(self):
        self.assertEqual(classify('Something is wrong.')['action'], 'human_review')

    def test_legacy_team_mapping(self):
        self.assertEqual(legacy_team('transfers'), 'billing')
        self.assertEqual(legacy_team('card_lifecycle'), 'shipping')

    def test_policy_and_wording_coverage(self):
        self.assertEqual(classify('Can you help me with proving my identity?')['domain'], 'identity_access')
        self.assertEqual(classify('Why is my cheque deposit taking so long?')['domain'], 'payments')
        self.assertEqual(classify("Why isn't my disposable virtual card working?")['action'], 'human_review')
        self.assertEqual(classify("Why won't you let me get money out of the ATM?")['domain'], 'cash')
        self.assertEqual(classify('What proof do you need for my identification?')['domain'], 'identity_access')
        self.assertEqual(legacy_team(classify('What is the fee for topping up a US card?')['domain']), 'billing')
        self.assertEqual(legacy_team(classify('The gas station payment is still pending.')['domain']), 'billing')


if __name__ == '__main__':
    unittest.main()
