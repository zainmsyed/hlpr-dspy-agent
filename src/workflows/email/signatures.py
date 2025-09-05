from pydantic import BaseModel

class CategorizerInput(BaseModel):
    text: str

class CategorizerOutput(BaseModel):
    label: str
    confidence: float
    metadata: dict | None = None
