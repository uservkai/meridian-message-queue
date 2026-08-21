from collections import deque
from dataclasses import dataclass
from typing import Optional

from .message import Message


@dataclass
class QueueStats:
    queued: int
    dead_lettered: int


class MessageQueue:
    """Small in-process queue exposing ACK, retry and DLQ semantics."""

    def __init__(self, max_attempts: int = 3) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        self._pending: deque[Message] = deque()
        self._in_flight: dict[str, Message] = {}
        self._dead_letter: deque[Message] = deque()
        self.max_attempts = max_attempts

    def publish(self, message: Message) -> None:
        self._pending.append(message)

    def receive(self) -> Optional[Message]:
        if not self._pending:
            return None
        message = self._pending.popleft()
        self._in_flight[message.event_id] = message
        return message

    def acknowledge(self, event_id: str) -> None:
        self._in_flight.pop(event_id, None)

    def reject(self, event_id: str) -> None:
        message = self._in_flight.pop(event_id, None)
        if message is None:
            raise KeyError(f"Message {event_id!r} is not in flight")
        if message.attempts >= self.max_attempts:
            self._dead_letter.append(message)
        else:
            self._pending.append(message)

    def pending_count(self) -> int:
        return len(self._pending)

    def in_flight_count(self) -> int:
        return len(self._in_flight)

    def dead_letter_count(self) -> int:
        return len(self._dead_letter)

    def dead_letters(self) -> list[Message]:
        return list(self._dead_letter)

    def stats(self) -> QueueStats:
        return QueueStats(self.pending_count(), self.dead_letter_count())
