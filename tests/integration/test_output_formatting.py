import pytest


def test_output_formatting_integration():
    """T010: Integration test for output formatting (md/json/txt).

    Verify renderer classes inherit from BaseRenderer and raise until implemented.
    """
    from hlpr.cli.renderers import BaseRenderer, JsonRenderer

    assert issubclass(JsonRenderer, BaseRenderer)
    jr = JsonRenderer()
    with pytest.raises(NotImplementedError):
        jr.render({})
