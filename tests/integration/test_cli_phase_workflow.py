from rich.console import Console

from hlpr.cli.interactive import InteractiveSession
from hlpr.cli.rich_display import RichDisplay


def test_interactive_session_with_phases(tmp_path):
    """Test InteractiveSession.run_with_phases method."""
    console = Console(record=True)
    display = RichDisplay(console=console)

    p = tmp_path / "test.txt"
    p.write_text("test content")

    sess = InteractiveSession(display=display)
    res = sess.run_with_phases(
        str(p),
        {"provider": "local", "output_format": "md", "steps": 2},
    )

    assert res["status"] == "ok"

    # Check that console output contains phase information
    out = console.export_text()
    try:
        import hlpr.config.ui_strings as ui_strings
    except ImportError:
        class _Fallback:
            PANEL_COMPLETE = "Complete"

        ui_strings = _Fallback()

    assert ui_strings.PANEL_COMPLETE in out
    assert "Overall progress:" in out
