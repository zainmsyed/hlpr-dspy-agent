from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic
from pydantic import BaseModel
import dspy
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Type variables for generic workflow handling
InputType = TypeVar('InputType', bound=BaseModel)
OutputType = TypeVar('OutputType', bound=BaseModel)

class WorkflowInput(BaseModel):
    """Base class for all workflow inputs"""
    id: Optional[str] = None
    timestamp: datetime = datetime.now()
    metadata: Dict[str, Any] = {}

class WorkflowOutput(BaseModel):
    """Base class for all workflow outputs"""
    id: Optional[str] = None
    timestamp: datetime = datetime.now()
    confidence: Optional[float] = None
    processing_time: Optional[float] = None
    metadata: Dict[str, Any] = {}

class BaseWorkflow(ABC, Generic[InputType, OutputType]):
    """Abstract base class for all workflows"""
    
    def __init__(self, model_name: str = "llama3.1", **kwargs):
        self.model_name = model_name
        self.config = kwargs
        self._setup_dspy()
        
    def _setup_dspy(self):
        """Initialize DSPy with Ollama"""
        # This will be implemented in the Ollama integration
        pass
    
    @abstractmethod
    def process(self, input_data: InputType) -> OutputType:
        """Process the input and return output"""
        pass
    
    @abstractmethod
    def get_signature(self) -> dspy.Signature:
        """Return the DSPy signature for this workflow"""
        pass
    
    def validate_input(self, input_data: InputType) -> bool:
        """Validate input data before processing"""
        return True
    
    def validate_output(self, output_data: OutputType) -> bool:
        """Validate output data after processing"""
        return True

class OptimizableWorkflow(BaseWorkflow[InputType, OutputType]):
    """Extended workflow class with optimization support"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.examples = []
        self.metrics = {}
    
    def add_example(self, input_data: InputType, expected_output: OutputType):
        """Add training example for optimization"""
        self.examples.append((input_data, expected_output))
    
    def evaluate(self, test_data: List[tuple]) -> Dict[str, float]:
        """Evaluate workflow performance"""
        # This will be implemented with specific metrics
        pass
    
    def optimize(self, optimizer_type: str = "mipro"):
        """Optimize the workflow using specified optimizer"""
        # Future implementation for MIPRO and other optimizers
        pass

class BaseComponent(ABC):
    """Abstract base for core components."""

    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """Execute the component's primary behavior."""
        raise NotImplementedError()

class HealthCheckComponent(BaseComponent):
    def run(self, *args, **kwargs) -> Dict[str, str]:
        return {"status": "ok"}
