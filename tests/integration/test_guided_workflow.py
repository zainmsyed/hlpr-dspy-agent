import pytest


def test_guided_workflow_integration():
    """T008: Integration test for guided mode workflow.

    Basic integration check: InteractiveSession exists and pick_file is present.
    """
    from hlpr.cli.interactive import InteractiveSession, pick_file

    assert hasattr(InteractiveSession, "run")
    assert callable(pick_file)
