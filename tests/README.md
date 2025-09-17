Quick test guide

Fast dev workflow:

- Run unit tests only:
  PYTEST_MARKER=unit uv run pytest -m unit
- Run contract tests:
  uv run pytest -m contract
- Run integration tests (excluding perf):
  uv run pytest tests/integration -k "not performance"
- Run performance tests (explicit):
  PYTEST_PERF=1 uv run pytest -q tests/integration/test_document_performance.py

Notes:
- By default DSPy is mocked during tests (see `tests/conftest.py`).
- Set RUN_REAL_DSPY=1 to opt into real DSPy calls (only on machines with DSPy available).
- Keep perf tests gated with PYTEST_PERF to avoid slowing down regular runs.
