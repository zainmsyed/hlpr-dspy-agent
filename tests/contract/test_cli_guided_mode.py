import pytest


def test_cli_guided_mode_entrypoint_exists():
    """T004: Contract test for guided mode command `hlpr summarize`.

    Verify the InteractiveSession class exists and its run method raises
    NotImplementedError until implemented.
    """
    from hlpr.cli.interactive import InteractiveSession

    assert hasattr(InteractiveSession, "run")
    session = InteractiveSession()
    with pytest.raises(NotImplementedError):
        session.run()
