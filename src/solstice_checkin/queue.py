from collections import deque

from .models import PrintRequest


class PrintQueue:
    """In-memory queue representing the vendor's asynchronous print queue."""

    def __init__(self) -> None:
        self._items: deque[PrintRequest] = deque()

    def publish(self, request: PrintRequest) -> None:
        """Add a print request to the queue."""
        self._items.append(request)

    def get(self) -> PrintRequest | None:
        """Remove and return the next print request."""
        if not self._items:
            return None

        return self._items.popleft()

    def pending(self) -> int:
        """Return the number of requests waiting in the queue."""
        return len(self._items)