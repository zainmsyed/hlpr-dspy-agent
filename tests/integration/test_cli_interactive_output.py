from rich.console import Console

from hlpr.cli.interactive import InteractiveSession
from hlpr.cli.rich_display import ProgressTracker, RichDisplay


def test_interactive_output_shows_panels(tmp_path):
    console = Console(record=True)
    display = RichDisplay(console=console)
    progress = ProgressTracker(console=console)

    p = tmp_path / "ok.txt"
    p.write_text("x")

    sess = InteractiveSession(display=display, progress=progress)
    res = sess.run(str(p), {"provider": "local", "output_format": "md", "steps": 2})

    assert res["status"] == "ok"

    out = console.export_text()
    # basic assertions: panels should contain the strings (use centralized constants when available)
    try:
        import hlpr.config.ui_strings as ui_strings
    except ImportError:
        class _Fallback:
            PANEL_STARTING = "Starting"
            PANEL_COMPLETE = "Complete"
            PROCESSING_FINISHED = "Processing finished successfully"

        ui_strings = _Fallback()

    assert ui_strings.PANEL_STARTING in out or "Processing:" in out
    assert ui_strings.PANEL_COMPLETE in out or ui_strings.PROCESSING_FINISHED in out
