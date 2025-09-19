from __future__ import annotations

import concurrent.futures
import logging
from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional

from rich.console import Console

from hlpr.cli.models import FileSelection, ProcessingResult
from hlpr.cli.rich_display import PhaseTracker, ProgressTracker, RichDisplay

LOGGER = logging.getLogger(__name__)


@dataclass
class BatchOptions:
    max_workers: int = 4
    console: Optional[Console] = None


class BatchProcessor:
    """Process multiple files concurrently and return ProcessingResult list.

    The processor accepts a `summarize_fn` callable which takes a `FileSelection`
    and returns a `ProcessingResult`. This keeps the class testable and decoupled
    from provider implementations.
    """

    def __init__(self, options: Optional[BatchOptions] = None):
        self.options = options or BatchOptions()
        self.console = self.options.console or Console()

    def process_files(
        self,
        files: Iterable[FileSelection],
        summarize_fn: Callable[[FileSelection], ProcessingResult],
    ) -> List[ProcessingResult]:
        files_list = list(files)
        results: List[ProcessingResult] = []

        phase_tracker = PhaseTracker(["validate", "summarize", "render"])

        # Start the overall phase tracker: validation phase will have one step
        # per input file so the progress bar can reflect validation work.
        phase_tracker.start_phase(phase_steps=len(files_list), description="validation")

        # Quick validation pass
        valid_files = []
        for f in files_list:
            # keep simple: consider exists check done by validators elsewhere
            if not f.path:
                LOGGER.warning("Skipping file with empty path: %s", f)
                continue
            valid_files.append(f)

        phase_tracker.complete_phase()
        # Summarize phase: one step per valid file
        phase_tracker.start_phase(phase_steps=len(valid_files), description="summarize")

        prog = ProgressTracker(console=self.console)
        prog.start(total=len(valid_files), description="Summarizing files")

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.options.max_workers
        ) as exc:
            future_to_file = {exc.submit(summarize_fn, f): f for f in valid_files}
            for i, fut in enumerate(concurrent.futures.as_completed(future_to_file)):
                f = future_to_file[fut]
                try:
                    res = fut.result()
                except Exception as excp:  # pragma: no cover - defensive
                    LOGGER.exception("Error summarizing %s", f.path)
                    # Create a minimal ProcessingResult capturing error
                    res = ProcessingResult(file=f)
                    res.error = str(excp)
                results.append(res)
                prog.advance(1)

        prog.stop()

        # Complete summarize phase and mark render phase (one step) complete.
        phase_tracker.complete_phase()
        phase_tracker.start_phase(phase_steps=1, description="render")
        phase_tracker.complete_phase()

        return results
