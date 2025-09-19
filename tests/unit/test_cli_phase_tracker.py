from rich.console import Console

from hlpr.cli.rich_display import PhaseTracker


def test_phase_tracker_basic_workflow():
    """Test basic phase tracking workflow."""
    console = Console(record=True)
    phases = ["Validation", "Processing", "Rendering"]

    with PhaseTracker(phases, console=console) as tracker:
        # Phase 1: Validation
        assert tracker.current_phase == "Validation"
        tracker.start_phase(2, "Checking inputs")

        tracker.advance_phase_step(1)
        tracker.advance_phase_step(1)
        has_more = tracker.complete_phase()
        assert has_more is True

        # Phase 2: Processing
        assert tracker.current_phase == "Processing"
        tracker.start_phase(3, "Processing document")

        for _ in range(3):
            tracker.advance_phase_step(1)
        has_more = tracker.complete_phase()
        assert has_more is True

        # Phase 3: Rendering
        assert tracker.current_phase == "Rendering"
        tracker.start_phase(1, "Generating output")

        tracker.advance_phase_step(1)
        has_more = tracker.complete_phase()
        assert has_more is False  # No more phases


def test_phase_tracker_overall_percentage():
    """Test overall percentage calculation across phases."""
    phases = ["Phase1", "Phase2"]
    tracker = PhaseTracker(phases)

    # Initially 0%
    assert tracker.overall_percentage == 0.0

    # Complete first phase (should be 50%)
    tracker.start_phase(2)
    tracker.advance_phase_step(2)  # Complete phase 1
    tracker.complete_phase()

    # After completing first of two phases, should be around 50%
    # (exact value depends on implementation)
    overall = tracker.overall_percentage
    assert 45.0 <= overall <= 55.0  # Allow some tolerance


def test_phase_tracker_properties():
    """Test phase tracker property access."""
    phases = ["Test1", "Test2"]
    tracker = PhaseTracker(phases)

    assert tracker.current_phase == "Test1"
    assert not tracker.is_started()

    tracker.start_phase(1)
    assert tracker.is_started()

    tracker.complete_phase()
    assert tracker.current_phase == "Test2"

    tracker.complete_phase()
    assert tracker.current_phase is None  # No more phases
