Phase 1 mini-prototype for **The Meridian Pivot** assignment.

## Objective

Demonstrate:

- Producer -> Queue -> Consumer
- acknowledgement after successful processing
- retry after failure
- dead-letter queue after maximum attempts
- idempotent handling of duplicate inventory events

## Why Python 3.12?

Python is the recommended language for this prototype because it keeps the focus on distributed-systems concepts rather than framework configuration. The standard library is enough for the learning prototype, and Python 3.12 is a good fit for the Northstar engineering environment.

## Repository

```text
meridian-message-queue/
├── src/meridian_queue/
│   ├── message.py
│   ├── queue.py
│   ├── producer.py
│   ├── consumer.py
│   └── inventory.py
├── tests/
├── docs/
├── journal.md
├── demo.py
├── pyproject.toml
├── requirements.txt
└── requirements-dev.txt
```

## Setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

## Run

```powershell
python demo.py
```

## Test

```powershell
python -m pytest -q
```

## Architecture

```text
Inventory Event
      |
      v
  Producer
      |
      v
 Message Queue
      |
      v
  Consumer
    /   \
 success failure
   |       |
  ACK     retry
           |
       max attempts
           |
          DLQ
```
## Phase 2 — Cache Owner

The inventory cache stores the latest known warehouse stock quantity for each
SKU during the original Day 3 inventory-sync build.

The cache is implemented in:

```text
src/meridian_queue/cache.py
````

It provides a simple in-memory store for the latest inventory state. Stock
quantities can be added or updated, retrieved by SKU, checked for availability,
and cleared when required.

The cache is intentionally kept separate from the warehouse polling logic and
the query endpoint. The poller will provide updated warehouse data to the
cache, while the query endpoint will read the cached data when answering stock
availability requests.

### Cache flow

```text
Warehouse API
      |
      v
    Poller
      |
      v
InventoryCache
      |
      v
Query Endpoint
```

### Supported operations

```text
set_stock(sku, quantity)
get_stock(sku)
is_in_stock(sku)
has_sku(sku)
clear()
```

Negative stock quantities are rejected because inventory quantities cannot be
less than zero.

### Testing

Cache behavior is tested in:

```text
tests/test_cache.py
```

The tests cover storing and retrieving stock, updating stock, unknown SKUs,
in-stock and out-of-stock states, negative quantities, SKU existence, and
clearing the cache.

Run the cache tests with:

```powershell
python -m pytest tests/test_cache.py -v
```