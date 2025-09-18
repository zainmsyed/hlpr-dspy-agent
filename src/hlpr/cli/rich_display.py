"""Rich display utilities for the CLI TUI feature.

This module provides a minimal, testable wrapper around Rich's Console and
Progress so the rest of the CLI code can remain decoupled from Rich. The
Console may be injected for unit tests (for example using a `Console` with
`record=True`).
"""

import logging

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
)

logger = logging.getLogger(__name__)

__all__ = ["PhaseTracker", "ProgressTracker", "RichDisplay"]


class RichDisplay:
    """Wrapper around Rich Console for displaying panels and results.

    Panels are rendered via `console.print(Panel(...))`. A custom `Console`
    instance can be passed for testing (e.g., Console(record=True)).
    """

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    def show_panel(
        self,
        title: str,
        body: str,
        *,
        style: str | None = None,
        border_style: str | None = None,
    ) -> None:
        """Render a titled panel to the console.

        Args:
            title: Panel title
            body: Panel body text
            style: optional text style for the panel body
            border_style: optional border style
        """
        kwargs = {}
        if style is not None:
            kwargs["style"] = style
        if border_style is not None:
            kwargs["border_style"] = border_style
        panel = Panel(body, title=title, **kwargs)
        self.console.print(panel)

    def show_error_panel(self, title: str, error_msg: str) -> None:
        """Convenience helper to display an error panel using red styles."""
        self.show_panel(title, error_msg, style="red", border_style="red")


class ProgressTracker:
    """Progress tracker abstraction over Rich.Progress.

    Exposes start/advance/stop so callers can be decoupled from Rich in unit
    tests. The tracker manages a single task and uses a sane default set of
    progress columns appropriate for CLI feedback.
    """

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()
        self._progress: Progress | None = None
        self._task_id: TaskID | None = None
        self._description: str | None = None
        # store the last known completion percentage (0-100) so callers can
        # inspect the final state even after the Rich Progress instance is
        # stopped and cleaned up.
        self._last_percentage: float = 0.0

    def start(self, total: int, description: str = "Working") -> None:
        """Start a progress context for the given total units.

        Calling start when a progress is already active is a no-op.
        """
        if self._progress is not None:
            return

        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("{task.description}"),
            BarColumn(),
            TimeRemainingColumn(),
            console=self.console,
            transient=True,
        )
        self._progress.start()
        self._task_id = self._progress.add_task(description, total=total)
        self._description = description

    def advance(self, steps: int = 1) -> None:
        """Advance the internal task by `steps` units.

        Raises:
            RuntimeError: if called before `start()`
        """
        if self._progress is None or self._task_id is None:
            msg = "ProgressTracker not started"
            raise RuntimeError(msg)
        self._progress.update(self._task_id, advance=steps)

    def stop(self) -> None:
        """Stop and clean up the progress instance."""
        if self._progress is None:
            return
        try:
            # capture final percentage before stopping the progress so the
            # value can still be accessed after cleanup.
            try:
                if self._task_id is not None:
                    task = self._progress.tasks[self._task_id]
                    if task.total and task.total > 0:
                        ratio = task.completed / task.total
                        self._last_percentage = float(ratio) * 100.0
            except (KeyError, AttributeError, IndexError, TypeError) as e:
                # defensive: if Rich internals changed or indexing fails,
                # leave _last_percentage unchanged.
                logger.warning("Rich progress API issue during cleanup: %s", e)

            self._progress.stop()
        finally:
            self._progress = None
            self._task_id = None
            self._description = None

    def is_started(self) -> bool:
        """Return True if a progress task is currently active."""
        return self._progress is not None and self._task_id is not None

    @property
    def description(self) -> str | None:
        """Return the current progress description."""
        return self._description

    def reset(self) -> None:
        """Reset the progress tracker to initial state."""
        if self.is_started():
            self.stop()
        self._last_percentage = 0.0
        self._description = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    @property
    def percentage(self) -> float:
        """Return current completion percentage (0-100)."""
        # If progress is not active, return the last captured percentage.
        if self._progress is None or self._task_id is None:
            return float(self._last_percentage)

        try:
            task = self._progress.tasks[self._task_id]
            if task.total and task.total > 0:
                val = float(task.completed / task.total) * 100.0
                # keep _last_percentage up-to-date while progress is running
                self._last_percentage = val
                return val
        except (KeyError, AttributeError, IndexError):
            return float(self._last_percentage)

        return float(self._last_percentage)


class PhaseTracker:
    """Multi-phase progress tracker with descriptive labels.

    Extends the concept of progress tracking to handle workflows with
    distinct phases, each with their own progress tracking.
    """

    def __init__(self, phases: list[str], console: Console | None = None) -> None:
        self.phases = phases
        self.current_phase_index = 0
        self.console = console or Console()
        self._progress_tracker = ProgressTracker(console=console)
        self._phase_complete: list[bool] = [False] * len(phases)

    @property
    def current_phase(self) -> str | None:
        """Get the name of the current phase."""
        if 0 <= self.current_phase_index < len(self.phases):
            return self.phases[self.current_phase_index]
        return None

    @property
    def overall_percentage(self) -> float:
        """Calculate overall completion percentage across all phases."""
        if not self.phases:
            return 0.0

        completed_phases = sum(self._phase_complete)

        # Only add current phase progress if we're actively in a phase
        if (self.current_phase_index < len(self.phases) and
            self._progress_tracker.is_started()):
            current_phase_progress = self._progress_tracker.percentage / 100.0
        else:
            current_phase_progress = 0.0

        total_progress = completed_phases + current_phase_progress
        return (total_progress / len(self.phases)) * 100.0

    def start_phase(self, phase_steps: int, description: str = "") -> None:
        """Start the current phase with specified steps."""
        if self.current_phase is None:
            return

        phase_name = self.current_phase
        full_description = (
            f"[{phase_name}] {description}" if description else phase_name
        )

        self._progress_tracker.start(total=phase_steps, description=full_description)

    def advance_phase_step(self, steps: int = 1) -> None:
        """Advance the current phase by specified steps."""
        self._progress_tracker.advance(steps)

    def complete_phase(self) -> bool:
        """Mark current phase as complete and move to next phase.

        Returns True if there are more phases, False if all phases complete.
        """
        if self.current_phase_index < len(self.phases):
            self._phase_complete[self.current_phase_index] = True

        self._progress_tracker.stop()
        self.current_phase_index += 1

        return self.current_phase_index < len(self.phases)

    def stop(self) -> None:
        """Stop all phase tracking."""
        self._progress_tracker.stop()

    def is_started(self) -> bool:
        """Check if phase tracking is currently active."""
        return self._progress_tracker.is_started()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
