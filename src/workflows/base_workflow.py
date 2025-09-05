from abc import ABC, abstractmethod
from typing import Any

class BaseWorkflow(ABC):
    """Abstract base workflow defining the contract for all workflows."""

    @abstractmethod
    def run(self, input_data: Any) -> Any:
        """Run the workflow with provided input and return result."""
        raise NotImplementedError()
