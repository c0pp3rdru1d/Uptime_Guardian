from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable, List

from .models import Endpoint
from .checks import check_many
from .reporting import build_summary, format_summary


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="uptime-guardian",
        description="Check HTTP endpoints and show a status dashboard.",
    )
    parser.add_argument(
        "config",
        type=Path,
        help="Path to JSON file describing endpoints.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Override per-endpoint timeout (seconds).",
    )
    return parser.parse_args(argv)


def load_endpoints_from_json(path: Path, override_timeout: float | None = None) -> List[Endpoint]:
    """
    Load endpoints from a JSON file.

    Expected format:
    [
      {"name": "Example", "url": "https://example.com", "timeout": 5.0},
      {"name": "API", "url": "https://api.example.com"}
    ]
    """
    text = path.read_text(encoding="utf-8")
    raw_items = json.loads(text)

    endpoints: List[Endpoint] = []
    for item in raw_items:
        name = item["name"]
        url = item["url"]
        timeout = item.get("timeout", 5.0)
        if override_timeout is not None:
            timeout = override_timeout
        endpoints.append(Endpoint(name=name, url=url, timeout=timeout))

    return endpoints


def _format_results_table(results) -> str:
    """
    Create a simple text table of individual endpoint results.
    """
    # Columns: Name, Status, Code, Latency, Error
    headers = ["NAME", "STATUS", "CODE", "LATENCY", "ERROR"]
    rows = []

    for r in results:
        status = "UP" if r.is_up else "DOWN"
        code = str(r.status_code) if r.status_code is not None else "-"
        if r.latency is not None:
            latency_str = f"{r.latency.total_seconds():.3f}s"
        else:
            latency_str = "N/A"
        error_lines = (r.error or "").splitlines()
        error = error_lines[0] if error_lines else ""
        if len(error) > 40:
            error = error[:37] + "..."
        rows.append([r.endpoint.name, status, code, latency_str, error])

    # Determine column widths
    cols = list(zip(*([headers] + rows))) if rows else [headers]
    col_widths = [max(len(str(cell)) for cell in col) for col in cols]

    def fmt_row(cells):
        return "  ".join(str(c).ljust(w) for c, w in zip(cells, col_widths))

    lines = [fmt_row(headers), fmt_row(["-" * w for w in col_widths])]
    for row in rows:
        lines.append(fmt_row(row))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if not args.config.exists():
        print(f"Error: config file not found: {args.config}", file=sys.stderr)
        return 1

    try:
        endpoints = load_endpoints_from_json(args.config, override_timeout=args.timeout)
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        print(f"Error loading config: {exc}", file=sys.stderr)
        return 1

    if not endpoints:
        print("No endpoints defined in config.", file=sys.stderr)
        return 1

    results = check_many(endpoints)
    table = _format_results_table(results)
    summary = build_summary(results)
    summary_text = format_summary(summary)

    # “CLI GUI”: table + blank line + summary block
    print(table)
    print()
    print(summary_text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

