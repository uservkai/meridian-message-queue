from .message import Message
from .queue import MessageQueue


class InventoryProducer:
    def __init__(self, queue: MessageQueue) -> None:
        self.queue = queue

    def publish_inventory_update(self, event_id: str, product_id: str, quantity: int) -> Message:
        if quantity < 0:
            raise ValueError("quantity cannot be negative")
        message = Message(
            event_id=event_id,
            event_type="inventory.updated",
            payload={"product_id": product_id, "quantity": quantity},
        )
        self.queue.publish(message)
        return message
