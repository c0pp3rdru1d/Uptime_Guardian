from __future__ import annotations

from datetime import timedelta
from typing import Iterable, Optional

from .models import CheckResult, Summary


def build_summary(results: Iterable[CheckResult]) -> Summary:
    """
    Compute basic statistics over a collection of CheckResult objects.

    - total endpoints checked
    - how many are up / down
    - uptime ratio (up / total)
    - average latency for endpoints that are up (if any)
    """
    results = list(results)
    total = len(results)

    if total == 0:
        return Summary(
            total=0,
            up_count=0,
            down_count=0,
            uptime_ratio=0.0,
            avg_latency_up=None,
        )

    up_results = [r for r in results if r.is_up]
    down_results = [r for r in results if not r.is_up]

    up_count = len(up_results)
    down_count = len(down_results)
    uptime_ratio = up_count / total

    # Compute average latency for successful checks that have latency
    latencies = [
        r.latency
        for r in up_results
        if r.latency is not None
    ]

    if latencies:
        # Sum of timedeltas: start from zero
        total_latency = sum(latencies, timedelta(0))
        avg_latency_up: Optional[timedelta] = total_latency / len(latencies)
    else:
        avg_latency_up = None

    return Summary(
        total=total,
        up_count=up_count,
        down_count=down_count,
        uptime_ratio=uptime_ratio,
        avg_latency_up=avg_latency_up,
    )


def format_summary(summary: Summary) -> str:
    """
    Produce a human-readable multi-line summary string.

    Example:

        Total endpoints: 3
        Up: 2 (66.7%)
        Down: 1
        Average latency (up): 0.123s
    """
    if summary.total == 0:
        return "No endpoints were checked."

    percent_up = summary.uptime_ratio * 100.0

    if summary.avg_latency_up is not None:
        # Represent latency in seconds with milliseconds precision
        seconds = summary.avg_latency_up.total_seconds()
        latency_str = f"{seconds:.3f}s"
    else:
        latency_str = "N/A"

    lines = [
        f"Total endpoints: {summary.total}",
        f"Up: {summary.up_count} ({percent_up:.1f}%)",
        f"Down: {summary.down_count}",
        f"Average latency (up): {latency_str}",
    ]
    return "\n".join(lines)

