from pydantic import BaseModel
from typing import Any, List

class CategorizerInput(BaseModel):
    text: str

class CategorizerOutput(BaseModel):
    label: str
    confidence: float
    metadata: dict | None = None
