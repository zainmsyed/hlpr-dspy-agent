from pydantic import BaseModel
from typing import Any

class ModelBase(BaseModel):
    id: str
    payload: Any | None = None
