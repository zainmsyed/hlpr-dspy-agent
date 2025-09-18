"""Output renderers (stubs) for CLI TUI feature."""
from abc import ABC, abstractmethod
from typing import Any
import json

__all__ = ["BaseRenderer", "RichRenderer", "JsonRenderer", "MarkdownRenderer", "PlainTextRenderer"]


class BaseRenderer(ABC):
    @abstractmethod
    def render(self, data: Any) -> str:
        raise NotImplementedError


class RichRenderer(BaseRenderer):
    def render(self, data: Any) -> str:
        raise NotImplementedError("RichRenderer.render not implemented")


class JsonRenderer(BaseRenderer):
    def render(self, data: Any) -> str:
        # Use json.dumps at implementation time
        raise NotImplementedError("JsonRenderer.render not implemented")


class MarkdownRenderer(BaseRenderer):
    def render(self, data: Any) -> str:
        raise NotImplementedError("MarkdownRenderer.render not implemented")


class PlainTextRenderer(BaseRenderer):
    def render(self, data: Any) -> str:
        raise NotImplementedError("PlainTextRenderer.render not implemented")
