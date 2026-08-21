from dataclasses import dataclass


@dataclass
class InventoryItem:
    product_id: str
    quantity: int


class InventoryService:
    """Inventory store with event-ID based idempotency."""

    def __init__(self) -> None:
        self._items: dict[str, InventoryItem] = {}
        self._processed_event_ids: set[str] = set()

    def update_from_event(self, event_id: str, product_id: str, quantity: int) -> bool:
        if event_id in self._processed_event_ids:
            return False
        if quantity < 0:
            raise ValueError("quantity cannot be negative")
        self._items[product_id] = InventoryItem(product_id, quantity)
        self._processed_event_ids.add(event_id)
        return True

    def get(self, product_id: str) -> InventoryItem | None:
        return self._items.get(product_id)
