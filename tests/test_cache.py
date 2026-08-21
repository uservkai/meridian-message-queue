import pytest

from meridian_queue.cache import InventoryCache


def test_set_and_get_stock():
    cache = InventoryCache()

    cache.set_stock("SKU001", 25)

    assert cache.get_stock("SKU001") == 25


def test_stock_can_be_updated():
    cache = InventoryCache()

    cache.set_stock("SKU001", 25)
    cache.set_stock("SKU001", 10)

    assert cache.get_stock("SKU001") == 10


def test_unknown_sku_returns_none():
    cache = InventoryCache()

    assert cache.get_stock("UNKNOWN") is None


def test_sku_with_positive_quantity_is_in_stock():
    cache = InventoryCache()

    cache.set_stock("SKU001", 25)

    assert cache.is_in_stock("SKU001") is True


def test_sku_with_zero_quantity_is_not_in_stock():
    cache = InventoryCache()

    cache.set_stock("SKU001", 0)

    assert cache.is_in_stock("SKU001") is False


def test_unknown_sku_is_not_in_stock():
    cache = InventoryCache()

    assert cache.is_in_stock("UNKNOWN") is False


def test_negative_stock_is_rejected():
    cache = InventoryCache()

    with pytest.raises(ValueError):
        cache.set_stock("SKU001", -1)


def test_has_sku_distinguishes_known_and_unknown_skus():
    cache = InventoryCache()

    cache.set_stock("SKU001", 0)

    assert cache.has_sku("SKU001") is True
    assert cache.has_sku("UNKNOWN") is False


def test_clear_removes_cached_inventory():
    cache = InventoryCache()

    cache.set_stock("SKU001", 25)
    cache.set_stock("SKU002", 10)

    cache.clear()

    assert cache.get_stock("SKU001") is None
    assert cache.get_stock("SKU002") is None