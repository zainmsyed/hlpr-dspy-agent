import pytest
from rich.console import Console

from hlpr.cli.rich_display import RichDisplay


def test_operation_progress_success_shows_panel_and_progress():
    console = Console(record=True)
    rd = RichDisplay(console=console)

    # The operation_progress context manager should show a progress and then
    # a success panel containing the provided title and success message.
    with rd.operation_progress("Parsing", total=2, success_message="Done parsing"):
        # simulate progress advancement
        rd._progress_tracker.advance(1)
        rd._progress_tracker.advance(1)

    output = console.export_text()
    assert "Parsing" in output
    assert "Done parsing" in output


def test_operation_progress_exception_shows_error_panel():
    console = Console(record=True)
    rd = RichDisplay(console=console)

    with (
        pytest.raises(RuntimeError),
        rd.operation_progress("FailingOp", total=1, success_message="Should not see"),
    ):
        # simulate an error inside the context
        raise RuntimeError("boom")

    output = console.export_text()
    assert "FailingOp" in output
    assert "boom" in output
