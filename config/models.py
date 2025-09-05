from pydantic import BaseModel

class BaseConfig(BaseModel):
    name: str
    version: str = "0.1.0"
    description: str | None = None
