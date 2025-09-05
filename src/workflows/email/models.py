from pydantic import BaseModel
from typing import Optional

class Email(BaseModel):
    id: str
    subject: str
    body: str
    sender: Optional[str] = None
    recipients: Optional[list[str]] = None
