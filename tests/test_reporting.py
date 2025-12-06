from datetime import timedelta
import pytest

from uptime_guardian.models import Endpoint, CheckResult, Summary
from uptime_guardian.reporting import build_summary, format_summary


def make_result(name: str, is_up: bool, latency_secs: float | None) -> CheckResult:
    ep = Endpoint(name=name, url=f"https://{name}.example")
    latency = timedelta(seconds=latency_secs) if latency_secs is not None else None
    return CheckResult(
        endpoint=ep,
        is_up=is_up,
        status_code=200 if is_up else None,
        latency=latency,
        error=None if is_up else "failed",
    )


def test_build_summary_empty():
    summary = build_summary([])

    assert isinstance(summary, Summary)
    assert summary.total == 0
    assert summary.up_count == 0
    assert summary.down_count == 0
    assert summary.uptime_ratio == 0.0
    assert summary.avg_latency_up is None


def test_build_summary_mixed():
    results = [
        make_result("one", True, 0.10),
        make_result("two", True, 0.30),
        make_result("three", False, None),
    ]

    summary = build_summary(results)

    assert summary.total == 3
    assert summary.up_count == 2
    assert summary.down_count == 1
    assert summary.uptime_ratio == pytest.approx(2 / 3, rel=1e-6)

    assert summary.avg_latency_up is not None
    # Average of 0.10 and 0.30 is 0.20 seconds
    assert summary.avg_latency_up.total_seconds() == pytest.approx(0.20, rel=1e-6)


def test_format_summary_with_data():
    summary = Summary(
        total=3,
        up_count=2,
        down_count=1,
        uptime_ratio=2 / 3,
        avg_latency_up=timedelta(seconds=0.2),
    )

    text = format_summary(summary)

    assert "Total endpoints: 3" in text
    assert "Up: 2 (66.7%)" in text  # rounded display
    assert "Down: 1" in text
    assert "Average latency (up): 0.200s" in text



def test_build_summary_no_latency_for_up():
    # Endpoint is up but latency is None (e.g. incomplete data)
    ep = Endpoint(name="NoLatency", url="https://nol.example")
    result = CheckResult(
        endpoint=ep,
        is_up=True,
        status_code=200,
        latency=None,
        error=None,
    )

    summary = build_summary([result])

    assert summary.total == 1
    assert summary.up_count == 1
    assert summary.avg_latency_up is None


def test_format_summary_no_latency_but_data():
    summary = Summary(
        total=1,
        up_count=1,
        down_count=0,
        uptime_ratio=1.0,
        avg_latency_up=None,
    )

    text = format_summary(summary)
    assert "Total endpoints: 1" in text
    assert "Up: 1" in text
    assert "Down: 0" in text
    assert "Average latency (up): N/A" in text



    
def test_format_summary_empty():
    summary = Summary(
        total=0,
        up_count=0,
        down_count=0,
        uptime_ratio=0.0,
        avg_latency_up=None,
    )

    text = format_summary(summary)
    assert text.strip() == "No endpoints were checked."

