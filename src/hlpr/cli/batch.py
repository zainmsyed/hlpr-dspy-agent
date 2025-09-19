from __future__ import annotations

import concurrent.futures
import contextlib
import logging
from collections.abc import Callable, Iterable
from dataclasses import dataclass

from rich.console import Console

from hlpr.cli.models import FileSelection, ProcessingError, ProcessingResult
from hlpr.cli.rich_display import PhaseTracker, ProgressTracker

LOGGER = logging.getLogger(__name__)


@dataclass
class BatchOptions:
    max_workers: int = 4
    console: Console | None = None
    save_partial_on_interrupt: bool = True


class BatchProcessor:
    """Process multiple files concurrently and return ProcessingResult list.

    The processor accepts a `summarize_fn` callable which takes a `FileSelection`
    and returns a `ProcessingResult`. This keeps the class testable and decoupled
    from provider implementations.
    """

    def __init__(self, options: BatchOptions | None = None):
        self.options = options or BatchOptions()
        self.console = self.options.console or Console()
        self.interrupted: bool = False

    def process_files(
        self,
        files: Iterable[FileSelection],
        summarize_fn: Callable[[FileSelection], ProcessingResult] | None = None,
    ) -> list[ProcessingResult]:
        # If no summarize function is provided the caller didn't implement
        # the integration yet — surface this as NotImplementedError so the
        # contract tests can assert the TODO state.
        if summarize_fn is None:
            msg = "summarize_fn must be provided"
            raise NotImplementedError(msg)

        files_list = list(files)
        results: list[ProcessingResult] = []

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

        try:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.options.max_workers,
            ) as executor:
                future_to_file = {
                    executor.submit(summarize_fn, f): f
                    for f in valid_files
                }
                for fut in concurrent.futures.as_completed(future_to_file):
                    f = future_to_file[fut]
                    try:
                        res = fut.result()
                    except Exception as excp:  # pragma: no cover - defensive
                        # We catch BaseException here to ensure that KeyboardInterrupt
                        # raised inside worker threads is captured and converted to a
                        # ProcessingResult so the caller can see partial failures.
                        # This is narrow and intentional: we re-raise later for
                        # non-recoverable signals at the outer level.
                        LOGGER.exception("Error summarizing %s", f.path)
                        res = ProcessingResult(file=f)
                        res.error = ProcessingError(
                            message=str(excp), details={"type": type(excp).__name__},
                        )
                    results.append(res)
                    prog.advance(1)
        except BaseException as excp:
            # Handle KeyboardInterrupt specially to allow partial results
            if isinstance(excp, KeyboardInterrupt):
                # mark interrupted so callers can persist partials
                self.interrupted = True
                if not self.options.save_partial_on_interrupt:
                    raise
                LOGGER.info("KeyboardInterrupt received: cancelling remaining tasks")
                # Cancel outstanding futures if any (best-effort)
                # Best-effort cancellation of outstanding futures. We intentionally
                # suppress all exceptions here because cancellation is best-effort
                # and must not mask the original KeyboardInterrupt handling.
                with contextlib.suppress(Exception):
                    for fut in list(future_to_file):
                        if not fut.done():
                            fut.cancel()
                # Collect any completed futures (best-effort)
                # Collect results from any futures that completed before the
                # interrupt. Again this is best-effort; we convert any errors
                # into ProcessingResult instances so callers can inspect them.
                with contextlib.suppress(Exception):
                    for fut, f in list(future_to_file.items()):
                        if fut.done():
                            try:
                                res = fut.result()
                            except Exception as excp2:  # pragma: no cover - defensive
                                res = ProcessingResult(file=f)
                                res.error = ProcessingError(
                                    message=str(excp2),
                                    details={"type": type(excp2).__name__},
                                )
                            results.append(res)
                prog.stop()
                return results
            # Re-raise other BaseExceptions (e.g., SystemExit)
            raise

        prog.stop()

        # Complete summarize phase and mark render phase (one step) complete.
        phase_tracker.complete_phase()
        phase_tracker.start_phase(phase_steps=1, description="render")
        phase_tracker.complete_phase()

        return results
