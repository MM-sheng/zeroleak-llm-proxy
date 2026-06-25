import unittest

import requests

from src.polymarket.gamma_client import (
    DEFAULT_GAMMA_BASE_URL,
    GammaClient,
    GammaClientError,
)


class FakeResponse:
    def __init__(self, payload, *, status_error=None, json_error=None):
        self.payload = payload
        self.status_error = status_error
        self.json_error = json_error

    def raise_for_status(self):
        if self.status_error is not None:
            raise self.status_error

    def json(self):
        if self.json_error is not None:
            raise self.json_error
        return self.payload


class FakeSession:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def get(self, url, *, params=None, timeout=None):
        self.calls.append({"url": url, "params": params, "timeout": timeout})
        return self.response


class GammaClientTests(unittest.TestCase):
    def test_get_markets_calls_read_only_markets_endpoint_with_timeout(self) -> None:
        session = FakeSession(FakeResponse([{"id": "1", "question": "Will BTC rise?"}]))
        client = GammaClient(session=session, timeout_seconds=7)

        markets = client.get_markets(limit=10, active=True)

        self.assertEqual(markets[0]["id"], "1")
        self.assertEqual(session.calls[0]["url"], f"{DEFAULT_GAMMA_BASE_URL}/markets")
        self.assertEqual(session.calls[0]["params"], {"limit": 10, "active": True})
        self.assertEqual(session.calls[0]["timeout"], 7)

    def test_get_markets_accepts_dict_wrapped_market_list(self) -> None:
        session = FakeSession(FakeResponse({"markets": [{"id": "wrapped"}]}))
        client = GammaClient(base_url="https://example.test/api/", session=session)

        markets = client.get_markets()

        self.assertEqual(markets, [{"id": "wrapped"}])
        self.assertEqual(session.calls[0]["url"], "https://example.test/api/markets")

    def test_get_market_fetches_single_market_object(self) -> None:
        session = FakeSession(FakeResponse({"id": "123", "question": "Will Bitcoin hit 120k?"}))
        client = GammaClient(session=session)

        market = client.get_market("123")

        self.assertEqual(market["id"], "123")
        self.assertEqual(session.calls[0]["url"], f"{DEFAULT_GAMMA_BASE_URL}/markets/123")

    def test_get_market_rejects_empty_market_id(self) -> None:
        client = GammaClient(session=FakeSession(FakeResponse({})))

        with self.assertRaises(ValueError):
            client.get_market("")

    def test_http_error_is_wrapped(self) -> None:
        error = requests.HTTPError("boom")
        client = GammaClient(session=FakeSession(FakeResponse({}, status_error=error)))

        with self.assertRaises(GammaClientError):
            client.get_markets()

    def test_invalid_json_is_wrapped(self) -> None:
        client = GammaClient(session=FakeSession(FakeResponse(None, json_error=ValueError("bad json"))))

        with self.assertRaises(GammaClientError):
            client.get_markets()

    def test_unexpected_market_list_shape_is_rejected(self) -> None:
        client = GammaClient(session=FakeSession(FakeResponse({"not_markets": []})))

        with self.assertRaises(GammaClientError):
            client.get_markets()

    def test_invalid_client_config_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            GammaClient(base_url=" ")
        with self.assertRaises(ValueError):
            GammaClient(timeout_seconds=0)


if __name__ == "__main__":
    unittest.main()
