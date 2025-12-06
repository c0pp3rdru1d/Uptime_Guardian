from __future__ import annotations

import time
from datetime import timedelta
from typing import Iterable, List

import requests

from .models import Endpoint, CheckResult


def check_endpoint(endpoint: Endpoint) -> CheckResult:
    """
    Perform an HTTP GET to endpoint.url and return a CheckResult.

    This function is PURE from the caller's perspective: it returns
    data with no side effects outside HTTP, so it is easy to unit test
    via mocking requests.get.
    """
    start = time.perf_counter()
    try:
        resp = requests.get(endpoint.url, timeout=endpoint.timeout)
        latency = timedelta(seconds=time.perf_counter() - start)
        is_up = 200 <= resp.status_code < 400
        return CheckResult(
            endpoint=endpoint,
            is_up=is_up,
            status_code=resp.status_code,
            latency=latency,
            error=None,
        )
    except requests.RequestException as exc:
        latency = timedelta(seconds=time.perf_counter() - start)
        return CheckResult(
            endpoint=endpoint,
            is_up=False,
            status_code=None,
            latency=latency,
            error=str(exc),
        )


def check_many(endpoints: Iterable[Endpoint]) -> List[CheckResult]:
    """
    Check multiple endpoints and return a list of CheckResult objects.
    """
    return [check_endpoint(ep) for ep in endpoints]

