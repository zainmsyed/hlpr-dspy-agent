from datetime import datetime

from hlpr.models.templates import CommandTemplate


def test_command_template_defaults():
    t = CommandTemplate.from_options(id="x", command_template="cmd", options={})
    assert t.id == "x"
    assert t.command_template == "cmd"
    assert isinstance(t.created, datetime)
    # ensure timezone-aware
    assert t.created.tzinfo is not None
