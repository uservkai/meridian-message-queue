from collections.abc import Callable

from .inventory import InventoryService
from .message import Message
from .queue import MessageQueue


class InventoryConsumer:
    """ACK only after successful processing; reject on failure."""

    def __init__(self, queue: MessageQueue, inventory: InventoryService,
                 processor: Callable[[Message], None] | None = None) -> None:
        self.queue = queue
        self.inventory = inventory
        self.processor = processor

    def process_next(self) -> bool:
        message = self.queue.receive()
        if message is None:
            return False
        message.record_attempt()
        try:
            if self.processor is not None:
                self.processor(message)
            else:
                self._process_inventory_message(message)
        except Exception:
            self.queue.reject(message.event_id)
            return True
        self.queue.acknowledge(message.event_id)
        return True

    def _process_inventory_message(self, message: Message) -> None:
        if message.event_type != "inventory.updated":
            raise ValueError(f"Unsupported event type: {message.event_type}")
        self.inventory.update_from_event(
            event_id=message.event_id,
            product_id=message.payload["product_id"],
            quantity=message.payload["quantity"],
        )
