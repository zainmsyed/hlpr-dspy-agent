"""Output renderers (stubs) for CLI TUI feature."""
from abc import ABC, abstractmethod
from typing import Any

__all__ = [
    "BaseRenderer",
    "JsonRenderer",
    "MarkdownRenderer",
    "PlainTextRenderer",
    "RichRenderer",
]


class BaseRenderer(ABC):
    @abstractmethod
    def render(self, data: Any) -> str:
        raise NotImplementedError


class RichRenderer(BaseRenderer):
    def render(self, data: Any) -> str:
        msg = "RichRenderer.render not implemented"
        raise NotImplementedError(msg)


class JsonRenderer(BaseRenderer):
    def render(self, data: Any) -> str:
        # Use json.dumps at implementation time
        msg = "JsonRenderer.render not implemented"
        raise NotImplementedError(msg)


class MarkdownRenderer(BaseRenderer):
    def render(self, data: Any) -> str:
        msg = "MarkdownRenderer.render not implemented"
        raise NotImplementedError(msg)


class PlainTextRenderer(BaseRenderer):
    def render(self, data: Any) -> str:
        msg = "PlainTextRenderer.render not implemented"
        raise NotImplementedError(msg)
