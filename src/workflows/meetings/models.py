from pydantic import BaseModel

class Meeting(BaseModel):
    id: str
    participants: list[str] | None = None
    transcript: str
