import os
import unittest
from unittest.mock import patch

from safeticket.serve import _resolve_mode


class ServeModeTests(unittest.TestCase):
    def test_safe_is_default(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(_resolve_mode(), "safe")

    def test_fast_mode_is_explicit(self):
        with patch.dict(os.environ, {"SAFETICKET_MODE": "fast"}, clear=True):
            self.assertEqual(_resolve_mode(), "fast")

    def test_legacy_switch_remains_supported(self):
        with patch.dict(os.environ, {"SAFETICKET_CONSISTENCY_CHECK": "0"}, clear=True):
            self.assertEqual(_resolve_mode(), "fast")
        with patch.dict(os.environ, {"SAFETICKET_CONSISTENCY_CHECK": "1"}, clear=True):
            self.assertEqual(_resolve_mode(), "safe")

    def test_invalid_mode_fails_fast(self):
        with patch.dict(os.environ, {"SAFETICKET_MODE": "unsafe"}, clear=True):
            with self.assertRaisesRegex(ValueError, "SAFETICKET_MODE"):
                _resolve_mode()


if __name__ == "__main__":
    unittest.main()
