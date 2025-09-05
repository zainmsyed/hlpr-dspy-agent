from typing import Any

class EmailClient:
    def send(self, to: str, subject: str, body: str) -> dict[str, Any]:
        # stub: pretend to send
        return {"to": to, "subject": subject, "status": "sent"}
