class InventoryCache:
    """In-memory cache containing the latest known stock quantity for each SKU."""

    def __init__(self):
        self._stock = {}

    def set_stock(self, sku: str, quantity: int) -> None:
        """Store or update the latest stock quantity for an SKU."""
        if quantity < 0:
            raise ValueError("Stock quantity cannot be negative.")

        self._stock[sku] = quantity

    def get_stock(self, sku: str) -> int | None:
        """Return the cached stock quantity for an SKU."""
        return self._stock.get(sku)

    def is_in_stock(self, sku: str) -> bool:
        """Return True when the SKU exists and has stock available."""
        quantity = self.get_stock(sku)
        return quantity is not None and quantity > 0

    def has_sku(self, sku: str) -> bool:
        """Return True when the SKU exists in the cache."""
        return sku in self._stock

    def clear(self) -> None:
        """Remove all cached inventory data."""
        self._stock.clear()