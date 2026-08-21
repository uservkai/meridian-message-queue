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
