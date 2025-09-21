import pytest

from hlpr.models.interactive import ProcessingOptions


def test_requires_output_path_when_save_true():
    with pytest.raises(ValueError):
        ProcessingOptions(save=True, output_path=None)


def test_temperature_normalization():
    opts = ProcessingOptions(temperature=0.123456)
    assert abs(opts.temperature - 0.123) < 1e-6

