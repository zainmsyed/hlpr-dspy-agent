from rich.console import Console

from hlpr.cli.interactive import InteractiveSession
from hlpr.cli.rich_display import ProgressTracker, RichDisplay


def test_progress_lifecycle_and_percentage(tmp_path):
    console = Console(record=True)
    display = RichDisplay(console=console)
    progress = ProgressTracker(console=console)

    p = tmp_path / "file.txt"
    p.write_text("content")

    sess = InteractiveSession(display=display, progress=progress)
    res = sess.run(str(p), {"provider": "local", "output_format": "md", "steps": 4})

    assert res["status"] == "ok"

    # progress percentage should be 100 after completion
    assert progress.is_started() is False
    assert progress.percentage == 100

    out = console.export_text()
    # Accept either legacy 'Processing' or the centralized progress description
    try:
        import hlpr.config.ui_strings as ui_strings
    except ImportError:

        class _Fallback:
            PROGRESS_WORKING = "Working"

        ui_strings = _Fallback()

    assert ("Processing" in out) or (ui_strings.PROGRESS_WORKING in out)
    try:
        import hlpr.config.ui_strings as ui_strings
    except ImportError:

        class _Fallback:
            PANEL_COMPLETE = "Complete"

        ui_strings = _Fallback()

    assert ui_strings.PANEL_COMPLETE in out
