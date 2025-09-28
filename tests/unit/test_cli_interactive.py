from hlpr.cli.interactive import InteractiveSession


class FakeProgress:
    def __init__(self):
        self.started = False
        self.advanced = 0
        self.stopped = False

    def start(self, total: int, description: str = ""):
        self.started = True
        self.total = total
        self.description = description

    def advance(self, amount: int = 1):
        self.advanced += amount

    def stop(self):
        self.stopped = True


def test_interactive_run_file_validation_failure(tmp_path):
    sess = InteractiveSession(display=None, progress=None)
    # nonexistent file should return error
    res = sess.run(
        str(tmp_path / "nope.txt"),
        {"provider": "local", "output_format": "md"},
    )
    assert res["status"] == "error"


def test_interactive_run_config_validation_failure(tmp_path):
    # create a valid file
    p = tmp_path / "ok.txt"
    p.write_text("x")

    sess = InteractiveSession(display=None, progress=None)
    res = sess.run(str(p), {"provider": "unknown", "output_format": "md"})
    assert res["status"] == "error"


def test_interactive_run_success(tmp_path):
    p = tmp_path / "ok.txt"
    p.write_text("x")

    fake_progress = FakeProgress()
    sess = InteractiveSession(display=None, progress=fake_progress)
    res = sess.run(str(p), {"provider": "local", "output_format": "md", "steps": 2})

    assert res["status"] == "ok"
    assert fake_progress.started is True
    assert fake_progress.advanced == 2
    assert fake_progress.stopped is True
