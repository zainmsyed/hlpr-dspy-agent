from pydantic import BaseModel

class MeetingInput(BaseModel):
    transcript: str

class MeetingOutput(BaseModel):
    highlights: list[str]
    num_lines: int
