from ...workflows.base_workflow import BaseWorkflow
from dataclasses import dataclass
from typing import List

@dataclass
class CategorizationResult:
    label: str
    confidence: float

class EmailCategorizer(BaseWorkflow):
    """Simple email categorizer stub."""
    def run(self, input_data: str) -> List[CategorizationResult]:
        # trivial rule-based placeholder
        text = input_data.lower()
        if "invoice" in text or "bill" in text:
            return [CategorizationResult(label="finance", confidence=0.9)]
        if "meeting" in text or "schedule" in text:
            return [CategorizationResult(label="meeting", confidence=0.85)]
        return [CategorizationResult(label="general", confidence=0.6)]
