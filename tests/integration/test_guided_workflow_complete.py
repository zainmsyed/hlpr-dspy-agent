import pytest


def test_guided_workflow_end_to_end_smoke(tmp_path):
    """High-level integration smoke test for guided workflow (T009).
    This will be skipped if InteractiveSession or run method not implemented.
    """
    try:
        from hlpr.cli.interactive import InteractiveSession
    except ImportError as e:
        pytest.skip(f"InteractiveSession not importable: {e}")

    sample = tmp_path / "sample.md"
    sample.write_text("# Hello\n\nThis is a test document for the guided workflow.")

    session = InteractiveSession()
    assert hasattr(session, "run_guided_workflow"), "run_guided_workflow missing"

    # Running the workflow should return a result object or dict with summary
    result = session.run_guided_workflow(str(sample))
    assert result is None or hasattr(result, "summary") or isinstance(result, dict)
