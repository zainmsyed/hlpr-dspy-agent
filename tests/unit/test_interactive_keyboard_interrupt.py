from hlpr.cli.interactive import InteractiveSession
from hlpr.cli.prompt_providers import DefaultPromptProvider
from hlpr.cli.rich_display import ProgressTracker


class DummyProgress(ProgressTracker):
    def __init__(self):
        super().__init__()
        self.started = False

    def start(self, total: int | None = None, description: str = "Working") -> None:
        super().start(total=total, description=description)
        self.started = True

    def advance(self, _steps: int = 1) -> None:
        # Simulate a user KeyboardInterrupt during processing
        raise KeyboardInterrupt()


def test_keyboard_interrupt_handling(monkeypatch, tmp_path):
    session = InteractiveSession(
        prompt_provider=DefaultPromptProvider({}), progress=DummyProgress()
    )

    # Run with a small simulate_work to ensure it enters the progress loop
    res = session.run(
        file_path=str(tmp_path), options={"steps": 1, "simulate_work": True}
    )

    assert res["status"] in ("interrupted", "error")
    # If interrupted, error_type should indicate keyboard_interrupt
    if res.get("status") == "interrupted":
        assert res.get("error_type") == "keyboard_interrupt"
