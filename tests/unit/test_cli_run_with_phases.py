from hlpr.cli.interactive import InteractiveSession
from hlpr.cli.rich_display import RichDisplay


def test_run_with_phases_happy_path(tmp_path):
    # Create a valid file
    p = tmp_path / "ok.txt"
    p.write_text("hello")

    session = InteractiveSession(display=RichDisplay())
    res = session.run_with_phases(
        str(p), {"provider": "local", "output_format": "txt", "steps": 2}
    )

    assert res["status"] == "ok"
    assert res["error_type"] is None
