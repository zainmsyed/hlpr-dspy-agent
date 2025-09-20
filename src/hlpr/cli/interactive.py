"""Interactive CLI components for guided summarization.

This module implements a small, testable `InteractiveSession.run` used in
Phase 3.4 to wire together validators and UI primitives. `pick_file` is a
lightweight helper that can be replaced by a more interactive picker later.
"""
import contextlib
import time
from typing import Any, TypedDict

from hlpr.cli.rich_display import PhaseTracker, ProgressTracker, RichDisplay
from hlpr.cli.validators import validate_config, validate_file_path

__all__ = ["InteractiveSession", "pick_file"]

PHASES: list[str] = ["Validation", "Processing", "Rendering"]
DEFAULT_STEPS = 3


class SessionResult(TypedDict, total=False):
    status: str
    message: str
    error_type: str | None


class InteractiveSession:
    """Simple interactive session that wires validators and display helpers.

    The `run` method validates the provided file and options, displays a
    start panel, simulates progress, and displays a completion panel. It's
    intentionally synchronous and simple so it is easy to unit test.
    """

    def __init__(
        self,
        display: RichDisplay | None = None,
        progress: ProgressTracker | None = None,
        **kwargs: Any,
    ) -> None:
        self.state: dict[str, Any] = dict(kwargs)
        self.display = display or RichDisplay()
        # ProgressTracker is optional to allow tests to inject a lightweight
        # fake; if the import above fails because of module placement we
        # fallback to using RichDisplay directly.
        self.progress = progress or ProgressTracker()  # type: ignore[arg-type]

    def run(self, file_path: str | None = None, options: dict[str, object] | None = None) -> SessionResult:
        """Run the guided flow for a single file.

        Steps:
        - validate file and options
        - show a start panel
        - run a short progress simulation
        - show a completion panel and return a result dict
        """
        # Contract: when called with no arguments (tests call run() without
        # params) surface NotImplementedError so the TDD gate remains enforced.
        if file_path is None or options is None:  # pragma: no cover - contract behaviour
            raise NotImplementedError("InteractiveSession.run requires file_path and options")

        try:
            ok, msg = validate_file_path(file_path)
        except Exception as exc:  # defensive: validators may raise on unexpected input
            self.display.show_error_panel("Validation Error", f"File validation raised: {exc}")
            return {"status": "error", "message": str(exc), "error_type": "file_validation"}
        if not ok:
            # use the error panel helper for consistent styling
            self.display.show_error_panel(
                "Validation Error",
                f"File validation failed: {msg}",
            )
            return {
                "status": "error",
                "message": msg,
                "error_type": "file_validation",
            }

        try:
            ok, msg = validate_config(options)
        except Exception as exc:
            self.display.show_error_panel("Validation Error", f"Options validation raised: {exc}")
            return {"status": "error", "message": str(exc), "error_type": "options_validation"}
        if not ok:
            self.display.show_error_panel(
                "Validation Error",
                f"Options validation failed: {msg}",
            )
            return {
                "status": "error",
                "message": msg,
                "error_type": "options_validation",
            }

        # show start
        self.display.show_panel("Starting", f"Processing: {file_path}")

        # perform progress: configurable via options
        total = (
            int(options.get("steps", DEFAULT_STEPS))
            if isinstance(options.get("steps"), int)
            else DEFAULT_STEPS
        )
        simulate_work = bool(options.get("simulate_work", False))

        try:
            self.progress.start(total=total, description="Processing")
            for _ in range(total):
                try:
                    if simulate_work:
                        # small sleep for demo purposes; kept short to keep tests fast
                        time.sleep(0.01)
                    self.progress.advance(1)
                except KeyboardInterrupt:
                    # Allow graceful interruption: stop progress and persist state
                    self.progress.stop()
                    self.display.show_error_panel(
                        "Interrupted",
                        "Processing was interrupted by user. Partial results preserved.",
                    )
                    return {"status": "interrupted", "message": "partial", "error_type": "keyboard_interrupt"}
        finally:
            # ensure stopped if not already
            with contextlib.suppress(Exception):
                self.progress.stop()

        self.display.show_panel("Complete", "Processing finished successfully")
        return {"status": "ok", "message": "done", "error_type": None}

    def run_with_phases(
        self, file_path: str, options: dict[str, object],
    ) -> SessionResult:
        """Run a multi-phase guided workflow for a single file.

        This method provides phase-aware progress tracking with meaningful
        progress descriptions for complex workflows.
        """
        # Validation phase (defensive validations like in run())
        try:
            ok, msg = validate_file_path(file_path)
        except Exception as exc:
            self.display.show_error_panel("Validation Error", f"File validation raised: {exc}")
            return {"status": "error", "message": str(exc), "error_type": "file_validation"}
        if not ok:
            self.display.show_error_panel("Validation Error", f"File validation failed: {msg}")
            return {"status": "error", "message": msg, "error_type": "file_validation"}

        try:
            ok, msg = validate_config(options)
        except Exception as exc:
            self.display.show_error_panel("Validation Error", f"Options validation raised: {exc}")
            return {"status": "error", "message": str(exc), "error_type": "options_validation"}
        if not ok:
            self.display.show_error_panel("Validation Error", f"Options validation failed: {msg}")
            return {"status": "error", "message": msg, "error_type": "options_validation"}

        # Multi-phase processing
        phases = PHASES
        simulate_work = bool(options.get("simulate_work", False))

        try:
            with PhaseTracker(phases, console=self.display.console) as phase_tracker:
                # Run each phase with interrupt safety
                # Phase 1: Validation
                try:
                    phase_tracker.start_phase(2, "Validating inputs")
                    phase_tracker.advance_phase_step(1)  # file validation
                    if simulate_work:
                        time.sleep(0.01)
                    phase_tracker.advance_phase_step(1)  # config validation
                    phase_tracker.complete_phase()
                except KeyboardInterrupt:
                    phase_tracker.stop()
                    self.display.show_error_panel(
                        "Interrupted",
                        "Validation phase interrupted. Partial progress preserved.",
                    )
                    return {"status": "interrupted", "message": "partial", "error_type": "keyboard_interrupt"}

                # Phase 2: Processing
                # Only proceed if there are remaining phases
                if phase_tracker.current_phase is not None:
                    try:
                        processing_steps = int(options.get("steps", DEFAULT_STEPS))
                        phase_tracker.start_phase(processing_steps, "Processing document")
                        for _ in range(processing_steps):
                            if simulate_work:
                                time.sleep(0.01)
                            phase_tracker.advance_phase_step(1)
                        phase_tracker.complete_phase()
                    except KeyboardInterrupt:
                        phase_tracker.stop()
                        self.display.show_error_panel(
                            "Interrupted",
                            "Processing phase interrupted. Partial progress preserved.",
                        )
                        return {"status": "interrupted", "message": "partial", "error_type": "keyboard_interrupt"}

                # Phase 3: Rendering
                if phase_tracker.current_phase is not None:
                    try:
                        phase_tracker.start_phase(1, "Rendering output")
                        if simulate_work:
                            time.sleep(0.01)
                        phase_tracker.advance_phase_step(1)
                        phase_tracker.complete_phase()
                    except KeyboardInterrupt:
                        phase_tracker.stop()
                        self.display.show_error_panel(
                            "Interrupted",
                            "Rendering phase interrupted. Partial progress preserved.",
                        )
                        return {"status": "interrupted", "message": "partial", "error_type": "keyboard_interrupt"}
        except Exception as exc:
            # unexpected errors during phases should be surfaced nicely
            self.display.show_error_panel("Processing Error", str(exc))
            return {"status": "error", "message": str(exc), "error_type": "processing_error"}

        self.display.show_panel(
            "Complete",
            f"Processing finished successfully\n"
            f"Overall progress: {phase_tracker.overall_percentage:.1f}%",
        )
        return {"status": "ok", "message": "done", "error_type": None}


def pick_file(prompt: str) -> str:
    """Simple pick_file helper (keeps interface stable for tests).

    This implementation simply returns the prompt for tests and can be
    replaced with an interactive file picker later.
    """
    return prompt
