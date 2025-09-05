from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseComponent(ABC):
    """Abstract base for core components."""

    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """Execute the component's primary behavior."""
        raise NotImplementedError()

class HealthCheckComponent(BaseComponent):
    def run(self, *args, **kwargs) -> Dict[str, str]:
        return {"status": "ok"}
