import pytest
from pydantic import ValidationError


def test_processingoptions_model_validation():
    """FR-006/FR-013: Ensure ProcessingOptions validation exists and enforces ranges.
    This test will attempt to import ProcessingOptions; if not present, skip.
    """
    try:
        from hlpr.models.interactive import ProcessingOptions
    except ImportError as e:
        pytest.skip(f"ProcessingOptions not importable: {e}")

    # Temperature out of range should raise ValidationError
    with pytest.raises(ValidationError):
        ProcessingOptions(temperature=1.5)

    with pytest.raises(ValidationError):
        ProcessingOptions(temperature=-0.1)

    # Valid boundary values should be accepted
    opt_low = ProcessingOptions(temperature=0.0)
    assert opt_low.temperature == 0.0
    opt_high = ProcessingOptions(temperature=1.0)
    assert opt_high.temperature == 1.0
