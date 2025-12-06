import builtins
from datetime import timedelta

import pytest
import requests

from uptime_guardian.models import Endpoint
from uptime_guardian.checks import check_endpoint, check_many


class DummyResponse:
    def __init__(self, status_code: int):
        self.status_code = status_code


def test_check_endpoint_success(monkeypatch):
    # Arrange
    endpoint = Endpoint(name="Example", url="https://example.com")

    def fake_get(url, timeout):
        assert url == endpoint.url
        assert timeout == endpoint.timeout
        return DummyResponse(status_code=200)

    monkeypatch.setattr("uptime_guardian.checks.requests.get", fake_get)

    # Act
    result = check_endpoint(endpoint)

    # Assert
    assert result.endpoint == endpoint
    assert result.is_up is True
    assert result.status_code == 200
    assert result.error is None
    assert isinstance(result.latency, timedelta)


def test_check_endpoint_failure(monkeypatch):
    endpoint = Endpoint(name="Bad", url="https://bad.example")

    def fake_get(url, timeout):
        raise requests.ConnectionError("Connection failed")

    monkeypatch.setattr("uptime_guardian.checks.requests.get", fake_get)

    result = check_endpoint(endpoint)

    assert result.endpoint == endpoint
    assert result.is_up is False
    assert result.status_code is None
    assert "Connection failed" in (result.error or "")


def test_check_many(monkeypatch):
    endpoints = [
        Endpoint(name="One", url="https://one.test"),
        Endpoint(name="Two", url="https://two.test"),
    ]

    # Keep a simple counter to verify we called GET twice
    called_urls = []

    def fake_get(url, timeout):
        called_urls.append(url)
        return DummyResponse(status_code=200)

    monkeypatch.setattr("uptime_guardian.checks.requests.get", fake_get)

    results = check_many(endpoints)

    assert len(results) == 2
    assert {r.endpoint.name for r in results} == {"One", "Two"}
    assert all(r.is_up for r in results)
    assert set(called_urls) == {e.url for e in endpoints}

