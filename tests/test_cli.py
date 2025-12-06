import json
from datetime import timedelta
from pathlib import Path

import pytest

from uptime_guardian.models import Endpoint, CheckResult
from uptime_guardian import cli


def make_fake_results(endpoints):
    results = []
    for i, ep in enumerate(endpoints):
        is_up = (i % 2 == 0)
        status_code = 200 if is_up else None
        latency = timedelta(seconds=0.1 + 0.05 * i)
        error = None if is_up else "connection failed"
        results.append(
            CheckResult(
                endpoint=ep,
                is_up=is_up,
                status_code=status_code,
                latency=latency,
                error=error,
            )
        )
    return results


def test_cli_happy_path(monkeypatch, tmp_path, capsys):
    # Arrange: create a temporary config file
    config_path: Path = tmp_path / "endpoints.json"
    payload = [
        {"name": "Example", "url": "https://example.com"},
        {"name": "API", "url": "https://api.example.com"},
    ]
    config_path.write_text(json.dumps(payload), encoding="utf-8")

    # Monkeypatch check_many to avoid real HTTP calls
    captured_endpoints = {}

    def fake_check_many(endpoints):
        # Save endpoints for assertions
        captured_endpoints["eps"] = list(endpoints)
        return make_fake_results(captured_endpoints["eps"])

    monkeypatch.setattr(cli, "check_many", fake_check_many)

    # Act
    exit_code = cli.main([str(config_path)])
    out = capsys.readouterr().out

    # Assert
    assert exit_code == 0
    eps = captured_endpoints["eps"]
    assert len(eps) == 2
    assert eps[0].name == "Example"
    assert eps[1].url == "https://api.example.com"

    # Check that table and summary are present
    assert "NAME" in out
    assert "Example" in out
    assert "API" in out
    assert "Total endpoints: 2" in out
    # One up, one down (since we alternated)
    assert "Up: 1" in out
    assert "Down: 1" in out


def test_cli_missing_config(tmp_path, capsys):
    missing = tmp_path / "nope.json"

    exit_code = cli.main([str(missing)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "config file not found" in captured.err


def test_cli_empty_config(monkeypatch, tmp_path, capsys):
    config_path = tmp_path / "empty.json"
    config_path.write_text("[]", encoding="utf-8")

    exit_code = cli.main([str(config_path)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "No endpoints defined" in captured.err



def test_cli_bad_json(tmp_path, capsys):
    config_path = tmp_path / "bad.json"
    config_path.write_text("{ not valid json", encoding="utf-8")

    exit_code = cli.main([str(config_path)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Error loading config" in captured.err



def test_cli_missing_required_key(tmp_path, capsys):
    config_path = tmp_path / "missing_key.json"
    data = [{"url": "https://example.com"}]  # no 'name'
    config_path.write_text(json.dumps(data), encoding="utf-8")

    exit_code = cli.main([str(config_path)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Error loading config" in captured.err



def test_cli_timeout_override(monkeypatch, tmp_path, capsys):
    config_path = tmp_path / "endpoints.json"
    data = [{"name": "One", "url": "https://one.example"}]
    config_path.write_text(json.dumps(data), encoding="utf-8")

    captured_endpoints = {}

    def fake_check_many(endpoints):
        eps = list(endpoints)
        captured_endpoints["eps"] = eps
        # minimal fake result
        ep = eps[0]
        return [
            CheckResult(
                endpoint=ep,
                is_up=True,
                status_code=200,
                latency=timedelta(seconds=0.1),
                error=None,
            )
        ]

    monkeypatch.setattr(cli, "check_many", fake_check_many)

    exit_code = cli.main([str(config_path), "--timeout", "9.5"])
    out = capsys.readouterr().out

    assert exit_code == 0
    assert captured_endpoints["eps"][0].timeout == 9.5
    assert "Total endpoints: 1" in out



def test_cli_error_message_truncation():
    ep = Endpoint(name="Erry", url="https://err.example")
    long_error = "X" * 80  # very long

    results = [
        CheckResult(
            endpoint=ep,
            is_up=False,
            status_code=None,
            latency=timedelta(seconds=0.2),
            error=long_error,
        )
    ]

    table = cli._format_results_table(results)

    # Ensure the long error was truncated
    assert "XXX" in table  # some part of the Xs
    assert "..." in table
    assert long_error not in table  # full string should not appear

