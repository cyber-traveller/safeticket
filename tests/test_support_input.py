import unittest
from pydantic import ValidationError
from safeticket.serve import SupportRequest


class SupportInputTests(unittest.TestCase):
    def test_blank_and_invalid_input_rejected(self):
        for value in ['', '   ', '\n\t', '\u2003', 12, None, 'x'*16001]:
            with self.assertRaises(ValidationError):
                SupportRequest(ticket=value)

    def test_original_text_preserved(self):
        self.assertEqual(SupportRequest(ticket=' Invoice please. ').ticket, ' Invoice please. ')
