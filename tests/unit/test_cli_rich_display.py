from rich.console import Console

from hlpr.cli.rich_display import ProgressTracker, RichDisplay


def test_show_panel_renders_to_console() -> None:
    console = Console(record=True)
    rd = RichDisplay(console=console)
    rd.show_panel("Title", "Hello world")

    # The recorded console should contain the panel text
    output_text = console.export_text()
    assert "Hello world" in output_text
    assert "Title" in output_text


def test_progress_tracker_start_advance_stop() -> None:
    console = Console(record=True)
    tracker = ProgressTracker(console=console)

    # start a small task and advance it
    tracker.start(total=3, description="Testing")
    tracker.advance(1)
    tracker.advance(2)
    tracker.stop()

    # The tracker should report started/then stopped correctly
    assert not tracker.is_started()

    # Start again to check is_started becomes True
    tracker.start(total=1, description="Testing")
    assert tracker.is_started()
    tracker.advance(1)
    tracker.stop()
    assert not tracker.is_started()
