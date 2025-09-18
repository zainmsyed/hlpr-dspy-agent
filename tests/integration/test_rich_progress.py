import pytest


def test_rich_progress_integration():
    """T009: Integration test for Rich progress bars.

    Assert ProgressTracker exposes start and advance methods.
    """
    from hlpr.cli.rich_display import ProgressTracker

    pt = ProgressTracker()
    assert hasattr(pt, "start")
    assert hasattr(pt, "advance")
    with pytest.raises(NotImplementedError):
        pt.start()
