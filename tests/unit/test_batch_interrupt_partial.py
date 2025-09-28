import os
import signal
import threading
import time

from rich.console import Console

from hlpr.cli.batch import BatchOptions, BatchProcessor
from hlpr.cli.models import FileSelection


def test_batch_handles_keyboard_interrupt():
    console = Console()
    options = BatchOptions(
        max_workers=2, console=console, save_partial_on_interrupt=True
    )
    bp = BatchProcessor(options)

    files = [
        FileSelection(path="a.txt"),
        FileSelection(path="b.txt"),
        FileSelection(path="c.txt"),
    ]

    # Summarize function: sleep for a short time to allow SIGINT to arrive
    def summarize_fn(file_sel):
        time.sleep(0.05)
        pr = type("PR", (), {"file": file_sel, "summary": "ok"})()
        return pr

    # Send SIGINT to this process shortly after starting process_files
    def send_sigint_later(delay: float = 0.02):
        time.sleep(delay)
        os.kill(os.getpid(), signal.SIGINT)

    t = threading.Thread(target=send_sigint_later)
    t.start()

    results = bp.process_files(files, summarize_fn)

    # Ensure thread finished
    t.join()

    # Expect partial results returned and no exception bubbled
    assert isinstance(results, list)
    assert len(results) >= 1
    assert any(getattr(r, "summary", None) == "ok" for r in results)
