"""Progress tracking system for document processing operations.

This module provides a standardized way to track progress through document
processing pipelines with support for callbacks, phases, and detailed metrics.
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal

# Try to import Rich components once at module load; if unavailable, code will
# fall back to console progress. We keep these at top-level to satisfy linter
# rules while preserving optional dependency behavior.
try:
    from rich.progress import (
        BarColumn,
        Progress,
        SpinnerColumn,
        TextColumn,
        TimeElapsedColumn,
    )

    _RICH_AVAILABLE = True
except Exception:  # noqa: BLE001
    _RICH_AVAILABLE = False

logger = logging.getLogger(__name__)


class ProcessingPhase(Enum):
    """Enumeration of document processing phases."""

    PARSING = "parsing"
    CHUNKING = "chunking"
    SUMMARIZING = "summarizing"
    VALIDATING = "validating"
    SAVING = "saving"


@dataclass
class ProgressMetrics:
    """Metrics for tracking processing progress."""

    phase: ProcessingPhase
    start_time: float
    end_time: float | None = None
    items_processed: int = 0
    items_total: int = 0
    bytes_processed: int = 0
    bytes_total: int = 0
    current_item: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> int | None:
        """Get duration in milliseconds."""
        if self.end_time is None:
            return None
        return int((self.end_time - self.start_time) * 1000)

    @property
    def progress_percentage(self) -> float:
        """Get progress as percentage (0-100)."""
        if self.items_total == 0:
            return 0.0
        return min(100.0, (self.items_processed / self.items_total) * 100.0)

    @property
    def is_complete(self) -> bool:
        """Check if this phase is complete."""
        return self.end_time is not None


class ProgressCallback(ABC):
    """Abstract base class for progress callbacks."""

    @abstractmethod
    def on_phase_start(self, metrics: ProgressMetrics):
        """Called when a processing phase starts."""

    @abstractmethod
    def on_phase_progress(self, metrics: ProgressMetrics):
        """Called during processing phase progress updates."""

    @abstractmethod
    def on_phase_complete(self, metrics: ProgressMetrics):
        """Called when a processing phase completes."""

    @abstractmethod
    def on_error(self, phase: ProcessingPhase, error: Exception):
        """Called when an error occurs in a processing phase."""


class ConsoleProgressCallback(ProgressCallback):
    """Console-based progress callback using print statements."""

    def on_phase_start(self, metrics: ProgressMetrics):
        """Log phase start to console."""
        logger.info("Starting %s phase...", metrics.phase.value)

    def on_phase_progress(self, metrics: ProgressMetrics):
        """Log progress updates to console."""
        if metrics.items_total > 0:
            progress = metrics.progress_percentage
            logger.info(
                "%s: %.1f%% complete (%d/%d)",
                metrics.phase.value,
                progress,
                metrics.items_processed,
                metrics.items_total,
            )

    def on_phase_complete(self, metrics: ProgressMetrics):
        """Log phase completion to console."""
        duration = metrics.duration_ms or 0
        logger.info("Completed %s phase in %dms", metrics.phase.value, duration)

    def on_error(self, phase: ProcessingPhase, error: Exception):
        """Log errors to console."""
        logger.error("Error in %s phase: %s", phase.value, error)


class RichProgressCallback(ProgressCallback):
    """Rich-based progress callback for terminal UI."""

    def __init__(self):
        """Initialize Rich progress callback."""
        # Initialize Rich progress if available; otherwise fallback to console
        if _RICH_AVAILABLE:
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=None,  # Will be set when used
                disable=False,
            )
            self.tasks = {}
        else:
            logger.debug("Rich not available; using ConsoleProgressCallback")
            self.fallback = ConsoleProgressCallback()

    def on_phase_start(self, metrics: ProgressMetrics):
        """Start a Rich progress task."""
        if hasattr(self, "fallback"):
            self.fallback.on_phase_start(metrics)
            return

        task_desc = metrics.phase.value.title()
        if metrics.items_total > 0:
            self.tasks[metrics.phase] = self.progress.add_task(
                task_desc,
                total=metrics.items_total,
                completed=metrics.items_processed,
            )

    def on_phase_progress(self, metrics: ProgressMetrics):
        """Update Rich progress task."""
        if hasattr(self, "fallback"):
            self.fallback.on_phase_progress(metrics)
            return

        if metrics.phase in self.tasks:
            desc = "{}: {}".format(
                metrics.phase.value.title(),
                metrics.current_item or "",
            )
            self.progress.update(
                self.tasks[metrics.phase],
                completed=metrics.items_processed,
                description=desc,
            )

    def on_phase_complete(self, metrics: ProgressMetrics):
        """Complete Rich progress task."""
        if hasattr(self, "fallback"):
            self.fallback.on_phase_complete(metrics)
            return

        if metrics.phase in self.tasks:
            desc = f"{metrics.phase.value.title()} complete"
            self.progress.update(
                self.tasks[metrics.phase],
                completed=metrics.items_total,
                description=desc,
            )

    def on_error(self, phase: ProcessingPhase, error: Exception):
        """Handle errors in Rich progress."""
        if hasattr(self, "fallback"):
            self.fallback.on_error(phase, error)
            return

        if phase in self.tasks:
            desc = f"{phase.value.title()} failed: {error}"
            self.progress.update(
                self.tasks[phase],
                description=desc,
            )


class ProgressTracker:
    """Main progress tracking service for document processing."""

    def __init__(self, callback: ProgressCallback | None = None):
        """Initialize progress tracker.

        Args:
            callback: Progress callback implementation
        """
        self.callback = callback or ConsoleProgressCallback()
        self.active_phases: dict[ProcessingPhase, ProgressMetrics] = {}
        self.completed_phases: list[ProgressMetrics] = []
        self.errors: list[tuple[ProcessingPhase, Exception]] = []

    def start_phase(
        self,
        phase: ProcessingPhase,
        items_total: int = 0,
        bytes_total: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> ProgressMetrics:
        """Start tracking a processing phase.

        Args:
            phase: The processing phase
            items_total: Total number of items to process
            bytes_total: Total bytes to process
            metadata: Additional metadata for the phase

        Returns:
            ProgressMetrics instance for the phase
        """
        if phase in self.active_phases:
            logger.warning("Phase %s already active, restarting", phase.value)

        metrics = ProgressMetrics(
            phase=phase,
            start_time=time.time(),
            items_total=items_total,
            bytes_total=bytes_total,
            metadata=metadata or {},
        )

        self.active_phases[phase] = metrics
        self.callback.on_phase_start(metrics)

        return metrics

    def update_progress(
        self,
        phase: ProcessingPhase,
        items_processed: int | None = None,
        bytes_processed: int | None = None,
        current_item: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """Update progress for an active phase.

        Args:
            phase: The processing phase
            items_processed: Number of items processed so far
            bytes_processed: Number of bytes processed so far
            current_item: Description of current item being processed
            metadata: Additional metadata to update
        """
        if phase not in self.active_phases:
            logger.warning("Phase %s not active, cannot update progress", phase.value)
            return

        metrics = self.active_phases[phase]

        if items_processed is not None:
            metrics.items_processed = items_processed
        if bytes_processed is not None:
            metrics.bytes_processed = bytes_processed
        if current_item is not None:
            metrics.current_item = current_item
        if metadata:
            metrics.metadata.update(metadata)

        self.callback.on_phase_progress(metrics)

    def complete_phase(self, phase: ProcessingPhase) -> ProgressMetrics | None:
        """Complete a processing phase.

        Args:
            phase: The processing phase to complete

        Returns:
            Completed ProgressMetrics or None if phase wasn't active
        """
        if phase not in self.active_phases:
            logger.warning("Phase %s not active, cannot complete", phase.value)
            return None

        metrics = self.active_phases[phase]
        metrics.end_time = time.time()

        self.callback.on_phase_complete(metrics)
        self.completed_phases.append(metrics)
        del self.active_phases[phase]

        return metrics

    def report_error(self, phase: ProcessingPhase, error: Exception):
        """Report an error in a processing phase.

        Args:
            phase: The processing phase where error occurred
            error: The exception that occurred
        """
        self.errors.append((phase, error))
        self.callback.on_error(phase, error)

        # Complete the phase with error status
        if phase in self.active_phases:
            metrics = self.active_phases[phase]
            metrics.end_time = time.time()
            metrics.metadata["error"] = str(error)
            self.completed_phases.append(metrics)
            del self.active_phases[phase]

    def get_phase_metrics(self, phase: ProcessingPhase) -> ProgressMetrics | None:
        """Get metrics for a specific phase.

        Args:
            phase: The processing phase

        Returns:
            ProgressMetrics if phase exists, None otherwise
        """
        if phase in self.active_phases:
            return self.active_phases[phase]

        for metrics in self.completed_phases:
            if metrics.phase == phase:
                return metrics

        return None

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of all processing phases.

        Returns:
            Dictionary with processing summary
        """
        total_duration = 0
        phase_summaries = []

        for metrics in self.completed_phases:
            duration = metrics.duration_ms or 0
            total_duration += duration

            phase_summaries.append(
                {
                    "phase": metrics.phase.value,
                    "duration_ms": duration,
                    "items_processed": metrics.items_processed,
                    "progress_percentage": metrics.progress_percentage,
                    "error": metrics.metadata.get("error"),
                }
            )

        return {
            "total_duration_ms": total_duration,
            "phases": phase_summaries,
            "errors": [
                {"phase": phase.value, "error": str(error)}
                for phase, error in self.errors
            ],
            "active_phases": [phase.value for phase in self.active_phases],
        }


# Context manager for automatic progress tracking
class ProgressContext:
    """Context manager for automatic progress phase management."""

    def __init__(self, tracker: ProgressTracker, phase: ProcessingPhase, **kwargs):
        """Initialize progress context.

        Args:
            tracker: ProgressTracker instance
            phase: Processing phase
            **kwargs: Arguments for start_phase
        """
        self.tracker = tracker
        self.phase = phase
        self.kwargs = kwargs
        self.metrics = None

    def __enter__(self):
        """Start the progress phase."""
        self.metrics = self.tracker.start_phase(self.phase, **self.kwargs)
        return self.metrics

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Complete the progress phase."""
        if exc_type is not None:
            # An exception occurred
            self.tracker.report_error(self.phase, exc_val)
        else:
            # Normal completion
            self.tracker.complete_phase(self.phase)


# Convenience functions
_USE_RICH_DEFAULT = True


def create_progress_tracker(
    use_rich: Literal["auto", "yes", "no"] = "auto",
) -> ProgressTracker:
    """Create a progress tracker with appropriate callback.

    Args:
        use_rich: "auto" uses Rich if available (default), "yes" forces Rich,
            "no" forces console output.

    Returns:
        Configured ProgressTracker instance
    """
    # Determine desire for Rich based on mode
    if use_rich == "yes" or (use_rich == "auto" and _RICH_AVAILABLE):
        try:
            return ProgressTracker(RichProgressCallback())
        except ImportError:
            pass

    return ProgressTracker(ConsoleProgressCallback())
