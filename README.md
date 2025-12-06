🛡️ Uptime Guardian

A tested, modular, Python-based service uptime checker with a clean CLI dashboard

Uptime Guardian is a lightweight network utility that checks the health of HTTP endpoints and displays the results in a formatted terminal “dashboard.” Designed with professional software practices in mind, it features a modern project layout, clear separation of concerns, and a comprehensive automated test suite.

This project demonstrates production-quality Python development, including packaging, test-driven design, mocking of external dependencies, CLI tooling, and structured reporting.

✨ Features

Check the availability of any set of HTTP endpoints

Human-friendly CLI dashboard

Per-endpoint status table

Summaries including uptime ratio & average latency

Modular and extensible architecture

Full unit test suite using pytest & pytest-cov

Modern src/ layout and clean package structure

JSON-configurable endpoint definitions

Mocked HTTP interactions for deterministic testing

📂 Project Structure
uptime_guardian/
├─ pyproject.toml
├─ README.md
├─ src/
│  └─ uptime_guardian/
│     ├─ __init__.py
│     ├─ models.py        # Dataclasses for endpoints & summaries
│     ├─ checks.py        # Core HTTP check logic
│     ├─ reporting.py     # Statistics + summary formatting
│     └─ cli.py           # CLI "dashboard" entrypoint
└─ tests/
   ├─ test_checks.py
   ├─ test_cli.py
   ├─ test_reporting.py


This follows Python’s modern packaging recommendations and ensures isolated imports and test reliability.

🚀 Installation

From the project root:

pip install -e ".[dev]"


This installs:

the uptime_guardian package

development dependencies (pytest, pytest-cov)

🧪 Running the CLI

Create a JSON config file:

endpoints.json

[
  { "name": "Example", "url": "https://example.com", "timeout": 5.0 },
  { "name": "GitHub", "url": "https://github.com" }
]


Run:

uptime-guardian endpoints.json


Example output:

NAME      STATUS  CODE  LATENCY  ERROR
---------- ------  ----  -------- -----
Example   UP      200   0.102s
GitHub    UP      200   0.088s

Total endpoints: 2
Up: 2 (100.0%)
Down: 0
Average latency (up): 0.095s


You can override timeouts:

uptime-guardian endpoints.json --timeout 10

🧪 Testing & Quality Assurance

Uptime Guardian uses pytest with pytest-cov for robust automated testing.

✨ Coverage Highlights

94% total coverage

100% coverage in key logic modules (checks.py, models.py)

CLI behavior tested using:

monkeypatch for dependency isolation

tmp_path for config file tests

capsys for capturing CLI output

Run the full suite:
pytest --cov=uptime_guardian --cov-report=term-missing

Generate HTML coverage report:
pytest --cov=uptime_guardian --cov-report=html


Open htmlcov/index.html in your browser to view detailed coverage.

🧱 Architecture Overview
1. Models (models.py)

Defines the core dataclasses:

Endpoint

CheckResult

Summary

These act as stable, testable contracts between modules.

2. Checks (checks.py)

Performs actual HTTP GET requests

Returns structured CheckResult objects

Pure logic makes it easy to mock during tests

3. Reporting (reporting.py)

Aggregates results into Summary

Computes uptime ratios, average latency, etc.

Formats readable multi-line summaries

4. CLI (cli.py)

Loads endpoints from JSON config

Runs checks and renders the dashboard

Includes graceful error handling for:

bad JSON

missing fields

unreachable config paths

🔧 Future Enhancements

Support for ping/ICMP checks

JSON/CSV export of summary data

TUI version using rich or textual

Async mode for higher concurrency

Integration with monitoring dashboards

📜 License

This project is open-source and available under the MIT License.
=======
# Uptime_Guardian
A configurable CLI uptime manager for Network Admins
>>>>>>> bcee03f15d03676000a3a8d72612042b828ad034
