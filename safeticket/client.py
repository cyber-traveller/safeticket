"""Small dependency-free client for a local System One-compatible server."""

from __future__ import annotations

import http.client
import json
from collections.abc import Mapping
from urllib.parse import urlsplit


class SystemOneClient:
    """Reuse one HTTP connection for repeated decisions against one endpoint."""

    def __init__(self, base_url: str, timeout: float = 300.0, headers: Mapping[str, str] | None = None) -> None:
        parsed = urlsplit(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("base_url must include http:// or https://")
        self._scheme = parsed.scheme
        self._host = parsed.netloc
        self._prefix = parsed.path.rstrip("/")
        self._timeout = timeout
        self._headers = {"content-type": "application/json", "connection": "keep-alive", **(headers or {})}
        self._connection: http.client.HTTPConnection | http.client.HTTPSConnection | None = None

    def _get_connection(self):
        if self._connection is None:
            cls = http.client.HTTPSConnection if self._scheme == "https" else http.client.HTTPConnection
            self._connection = cls(self._host, timeout=self._timeout)
        return self._connection

    def system_one(self, payload: dict) -> dict:
        body = json.dumps(payload).encode("utf-8")
        connection = self._get_connection()
        try:
            connection.request(
                "POST",
                self._prefix + "/v1/systemone",
                body=body,
                headers=self._headers,
            )
            response = connection.getresponse()
            result = json.loads(response.read())
            if response.status >= 400:
                raise RuntimeError(f"server returned HTTP {response.status}: {result}")
            return result
        except (OSError, http.client.HTTPException):
            self.close()
            raise

    def support_decide(self, ticket: str) -> dict:
        """Call SafeTicket's policy endpoint for one support ticket."""
        body = json.dumps({'ticket': ticket}).encode('utf-8')
        connection = self._get_connection()
        try:
            connection.request(
                'POST',
                self._prefix + '/v1/support/decide',
                body=body,
                headers=self._headers,
            )
            response = connection.getresponse()
            result = json.loads(response.read())
            if response.status >= 400:
                raise RuntimeError(f'server returned HTTP {response.status}: {result}')
            return result
        except (OSError, http.client.HTTPException):
            self.close()
            raise

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def __enter__(self) -> "SystemOneClient":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()
