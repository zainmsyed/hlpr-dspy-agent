"""Output renderers (stubs) for CLI TUI feature."""
from typing import Any


class RichRenderer:
    def render(self, data: Any) -> str:
        return str(data)


class JsonRenderer:
    def render(self, data: Any) -> str:
        import json

        return json.dumps(data)


class MarkdownRenderer:
    def render(self, data: Any) -> str:
        return str(data)


class PlainTextRenderer:
    def render(self, data: Any) -> str:
        return str(data)
