def test_run_guided_workflow_default(tmp_path):
    """Ensure run_guided_workflow is callable and returns expected types for a small file."""
    try:
        from hlpr.cli.interactive import InteractiveSession
    except ImportError:
        import pytest
        pytest.skip("InteractiveSession not importable")

    sample = tmp_path / "sample.md"
    sample.write_text("# Test\n\nSimple document for guided mode smoke test.")

    session = InteractiveSession()
    assert hasattr(session, "run_guided_workflow")

    result = session.run_guided_workflow(str(sample))
    # Accept None (interactive flow may display and return None) or dict/result-like
    assert result is None or isinstance(result, dict) or hasattr(result, "summary")
