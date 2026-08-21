from meridian_queue.inventory import InventoryService


def test_inventory_update_is_stored() -> None:
    inventory = InventoryService()
    applied = inventory.update_from_event("evt-1", "SKU001", 15)
    assert applied is True
    assert inventory.get("SKU001").quantity == 15


def test_duplicate_event_is_idempotent() -> None:
    inventory = InventoryService()
    first = inventory.update_from_event("evt-1", "SKU001", 15)
    duplicate = inventory.update_from_event("evt-1", "SKU001", 99)
    assert first is True
    assert duplicate is False
    assert inventory.get("SKU001").quantity == 15
