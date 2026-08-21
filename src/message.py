from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class Message:
    event_id: str
    event_type: str
    payload: dict[str, Any]
    attempts: int = 0
    created_at:datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    def record_attempt(self) -> None:
        self.attempts += 1
        
