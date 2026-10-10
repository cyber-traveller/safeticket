import unittest

from safeticket.client import SystemOneClient


class ClientTests(unittest.TestCase):
    def test_requires_absolute_http_url(self):
        with self.assertRaises(ValueError):
            SystemOneClient("127.0.0.1:8008")

    def test_builds_client_without_network_access(self):
        client = SystemOneClient("http://127.0.0.1:8008")
        self.assertIsNone(client._connection)
        client.close()

    def test_custom_headers_are_retained_without_network_access(self):
        client = SystemOneClient("https://example.invalid", headers={"authorization": "Bearer test"})
        self.assertEqual(client._headers["authorization"], "Bearer test")
        client.close()


if __name__ == "__main__":
    unittest.main()
