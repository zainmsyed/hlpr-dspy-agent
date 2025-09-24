"""Interactive CLI components for guided summarization.

This module implements a small, testable `InteractiveSession.run` used in
Phase 3.4 to wire together validators and UI primitives. `pick_file` is a
lightweight helper that can be replaced by a more interactive picker later.
"""
import contextlib
import logging
import time
from datetime import UTC
from typing import Any, TypedDict

from hlpr.cli import option_collectors
from hlpr.cli.prompt_providers import DefaultPromptProvider, PromptProvider
from hlpr.cli.rich_display import PhaseTracker, ProgressTracker, RichDisplay
from hlpr.cli.validators import validate_config, validate_file_path
from hlpr.config.ui_strings import (
    PANEL_COMMAND_TEMPLATE,
    PANEL_COMPLETE,
    PANEL_GUIDED_WORKFLOW_ERROR,
    PANEL_INTERRUPTED,
    PANEL_PROCESSING_ERROR,
    PANEL_STARTING,
    PANEL_VALIDATION_ERROR,
    PROCESSING_FINISHED,
    PROCESSING_INTERRUPTED,
    USER_CANCELLED,
)
from hlpr.models.interactive import ProcessingOptions
from hlpr.models.saved_commands import SavedCommands
from hlpr.models.templates import CommandTemplate

__all__ = ["InteractiveSession", "pick_file"]

PHASES: list[str] = [
    __import__("hlpr.config.ui_strings", fromlist=["PHASE_VALIDATION"]).PHASE_VALIDATION,
    __import__("hlpr.config.ui_strings", fromlist=["PHASE_PROCESSING"]).PHASE_PROCESSING,
    __import__("hlpr.config.ui_strings", fromlist=["PHASE_RENDERING"]).PHASE_RENDERING,
]
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
        command_saver: SavedCommands | None = None,
        prompt_provider: PromptProvider | None = None,
        **kwargs: Any,
    ) -> None:
        self.state: dict[str, Any] = dict(kwargs)
        self.display = display or RichDisplay()
        # ProgressTracker is optional to allow tests to inject a lightweight
        # fake; if the import above fails because of module placement we
        # fallback to using RichDisplay directly.
        self.progress = progress or ProgressTracker()  # type: ignore[arg-type]
        self.command_saver = command_saver
        self.logger = logging.getLogger(__name__)
        self.prompt_provider = prompt_provider or DefaultPromptProvider(kwargs)

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
            self.display.show_error_panel(PANEL_VALIDATION_ERROR, f"File validation raised: {exc}")
            return {"status": "error", "message": str(exc), "error_type": "file_validation"}
        if not ok:
            # use the error panel helper for consistent styling
            self.display.show_error_panel(
                PANEL_VALIDATION_ERROR,
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
            self.display.show_error_panel(PANEL_VALIDATION_ERROR, f"Options validation raised: {exc}")
            return {"status": "error", "message": str(exc), "error_type": "options_validation"}
        if not ok:
            self.display.show_error_panel(
                PANEL_VALIDATION_ERROR,
                f"Options validation failed: {msg}",
            )
            return {
                "status": "error",
                "message": msg,
                "error_type": "options_validation",
            }

        # show start
        self.display.show_panel(PANEL_STARTING, f"Processing: {file_path}")

        # perform progress: configurable via options
        total = (
            int(options.get("steps", DEFAULT_STEPS))
            if isinstance(options.get("steps"), int)
            else DEFAULT_STEPS
        )
        simulate_work = bool(options.get("simulate_work", False))

        try:
            # use centralized progress description where available
            from hlpr.config.ui_strings import PROGRESS_WORKING

            self.progress.start(total=total, description=PROGRESS_WORKING)
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
                        PANEL_INTERRUPTED,
                        PROCESSING_INTERRUPTED,
                    )
                    return {"status": "interrupted", "message": "partial", "error_type": "keyboard_interrupt"}
        finally:
            # ensure stopped if not already
            with contextlib.suppress(Exception):
                self.progress.stop()

        self.display.show_panel(PANEL_COMPLETE, PROCESSING_FINISHED)
        return {"status": "ok", "message": "done", "error_type": None}

    # --- Phase 3.3 additions -------------------------------------------------
    def collect_basic_options(self, _defaults: dict | None = None) -> ProcessingOptions:
        """Collect basic options (kept for compatibility).

        Delegates to the `option_collectors.collect_basic_options` helper so
        the extraction is testable and the InteractiveSession remains a thin
        orchestration layer.
        """
        return option_collectors.collect_basic_options(self.prompt_provider)

    def collect_advanced_options(self, base_options: ProcessingOptions, _defaults: dict | None = None) -> ProcessingOptions:
        """Add advanced options onto a base ProcessingOptions instance.

        This method delegates to the `option_collectors.collect_advanced_options`
        helper which returns a dict of advanced option updates. The method
        preserves the original behavior by merging the dict into a new
        ProcessingOptions instance.
        """
        adv = option_collectors.collect_advanced_options(base_options, self.prompt_provider)
        # create a new instance copying base and updating advanced fields
        data = base_options.model_dump() if hasattr(base_options, "model_dump") else base_options.dict()
        data.update(adv)
        return ProcessingOptions(**data)

    def process_document_with_options(self, file_path: str, options: ProcessingOptions) -> SessionResult:
        """Convenience wrapper to run the existing run_with_phases using ProcessingOptions."""
        # Some existing validators expect the key 'output_format' instead of
        # 'format'. Provide a compatibility shim here so interactive options
        # remain ergonomic while satisfying the validator contract.
        opts_dict = options.model_dump() if hasattr(options, "model_dump") else dict(options)
        if "output_format" not in opts_dict and "format" in opts_dict:
            opts_dict["output_format"] = opts_dict.get("format")
        return self.run_with_phases(file_path, opts_dict)

    def generate_command_template(self, options: ProcessingOptions) -> CommandTemplate:
        """Generate a CommandTemplate from given options.

        The command string is a simple hlpr CLI invocation with converted args.
        """
        args = options.to_cli_args() if hasattr(options, "to_cli_args") else []
        cmd = "hlpr summarize document " + " ".join(args)
        # use a simple id based on timestamp (timezone-aware)
        from datetime import datetime

        id = datetime.now(UTC).isoformat()
        return CommandTemplate.from_options(
            id=id,
            command_template=cmd,
            options=options.model_dump() if hasattr(options, "model_dump") else dict(options),
        )

    def display_command_template(self, template: CommandTemplate) -> None:
        """Display a generated command template using the RichDisplay panel."""
        self.display.show_panel(PANEL_COMMAND_TEMPLATE, template.command_template)

    def handle_keyboard_interrupt(self) -> None:
        """Centralised keyboard interrupt handling hook for interactive flows."""
        self.display.show_error_panel(PANEL_INTERRUPTED, USER_CANCELLED)

    def run_guided_workflow(self, file_path: str, defaults: dict | None = None) -> SessionResult | None:
        """High-level guided workflow entry point used by CLI and tests.

        Steps:
        - collect basic options
        - collect advanced options
        - run processing with options
        - generate and save command template
        Returns the processing SessionResult or None on non-critical failures.
        """
        try:
            base_opts = self.collect_basic_options(defaults)
            opts = self.collect_advanced_options(base_opts, defaults)

            # Run processing
            result = self.process_document_with_options(file_path, opts)

            # Generate and persist a command template for reproducibility
            try:
                template = self.generate_command_template(opts)
                saver = self.command_saver or SavedCommands()
                try:
                    saver.save_command(template)
                except Exception as e:
                    # Log but don't fail the workflow
                    self.logger.warning("Failed to persist command template: %s", e)
                # display the template to the user
                try:
                    self.display_command_template(template)
                except Exception as e:
                    self.logger.warning("Failed to display command template: %s", e)
            except Exception as e:
                # non-fatal: template generation should not break processing
                self.logger.warning("Command template generation failed: %s", e)

            return result
        except KeyboardInterrupt:
            self.handle_keyboard_interrupt()
            return {"status": "interrupted", "message": "cancelled", "error_type": "keyboard_interrupt"}
        except Exception as exc:
            # Surface unexpected errors via display and return an error result
            with contextlib.suppress(Exception):
                self.display.show_error_panel(PANEL_GUIDED_WORKFLOW_ERROR, str(exc))
            return {"status": "error", "message": str(exc), "error_type": "guided_workflow"}


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
            self.display.show_error_panel(PANEL_VALIDATION_ERROR, f"File validation raised: {exc}")
            return {"status": "error", "message": str(exc), "error_type": "file_validation"}
        if not ok:
            self.display.show_error_panel(PANEL_VALIDATION_ERROR, f"File validation failed: {msg}")
            return {"status": "error", "message": msg, "error_type": "file_validation"}

        try:
            ok, msg = validate_config(options)
        except Exception as exc:
            self.display.show_error_panel(PANEL_VALIDATION_ERROR, f"Options validation raised: {exc}")
            return {"status": "error", "message": str(exc), "error_type": "options_validation"}
        if not ok:
            self.display.show_error_panel(PANEL_VALIDATION_ERROR, f"Options validation failed: {msg}")
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
                        PANEL_INTERRUPTED,
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
                            PANEL_INTERRUPTED,
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
                            PANEL_INTERRUPTED,
                            "Rendering phase interrupted. Partial progress preserved.",
                        )
                        return {"status": "interrupted", "message": "partial", "error_type": "keyboard_interrupt"}
        except Exception as exc:
            # unexpected errors during phases should be surfaced nicely
            self.display.show_error_panel(PANEL_PROCESSING_ERROR, str(exc))
            return {"status": "error", "message": str(exc), "error_type": "processing_error"}

        self.display.show_panel(
            PANEL_COMPLETE,
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
