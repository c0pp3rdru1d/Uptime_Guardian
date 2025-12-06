from dataclasses import dataclass
from typing import Optional
from datetime import timedelta


@dataclass(frozen=True)
class Endpoint:
    name: str
    url: str
    timeout: float = 5.0  # seconds


@dataclass(frozen=True)
class CheckResult:
    endpoint: Endpoint
    is_up: bool
    status_code: Optional[int]
    latency: Optional[timedelta]
    error: Optional[str] = None


@dataclass(frozen=True)
class Summary:
    total: int
    up_count: int
    down_count: int
    uptime_ratio: float        # 0.0–1.0
    avg_latency_up: Optional[timedelta]


