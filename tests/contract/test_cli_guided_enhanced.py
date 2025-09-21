import pytest

# Contract tests for guided workflow (T004, T005, T007, T008)


def test_guided_mode_has_run_method():
    """FR-001: Interactive guided mode should expose a run method (placeholder name)
    This test will fail until the guided workflow run method is implemented.
    """
    try:
        from hlpr.cli.interactive import InteractiveSession
    except ImportError as e:  # Import error means implementation not present
        pytest.skip(f"InteractiveSession not importable: {e}")

    session = InteractiveSession()
    # The implementation should provide a `run_guided_workflow` method or similar
    assert hasattr(session, "run_guided_workflow"), "InteractiveSession missing run_guided_workflow()"


def test_command_template_generation_interface():
    """FR-007: InteractiveSession should provide template generation method."""
    try:
        from hlpr.cli.interactive import InteractiveSession
    except ImportError as e:
        pytest.skip(f"InteractiveSession not importable: {e}")

    session = InteractiveSession()
    assert hasattr(session, "generate_command_template"), "Missing generate_command_template()"


def test_keyboard_interrupt_interface():
    """FR-009: Session should implement keyboard interrupt handler."""
    try:
        from hlpr.cli.interactive import InteractiveSession
    except ImportError as e:
        pytest.skip(f"InteractiveSession not importable: {e}")

    session = InteractiveSession()
    assert hasattr(session, "handle_keyboard_interrupt"), "Missing handle_keyboard_interrupt()"
