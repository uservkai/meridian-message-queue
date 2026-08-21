import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from meridian_queue.consumer import InventoryConsumer
from meridian_queue.inventory import InventoryService
from meridian_queue.message import Message
from meridian_queue.producer import InventoryProducer
from meridian_queue.queue import MessageQueue


def main() -> None:
    queue = MessageQueue(max_attempts=3)
    inventory = InventoryService()
    producer = InventoryProducer(queue)
    consumer = InventoryConsumer(queue, inventory)

    print("=== 1. Successful message ===")
    producer.publish_inventory_update("evt-001", "SKU001", 25)
    consumer.process_next()
    print("SKU001:", inventory.get("SKU001").quantity)
    print("Pending:", queue.pending_count(), "DLQ:", queue.dead_letter_count())

    print("\n=== 2. Transient failure then success ===")
    failures_remaining = {"count": 1}

    def flaky_processor(message: Message) -> None:
        if failures_remaining["count"]:
            failures_remaining["count"] -= 1
            raise RuntimeError("Temporary downstream failure")
        inventory.update_from_event(
            message.event_id, message.payload["product_id"], message.payload["quantity"]
        )

    flaky_consumer = InventoryConsumer(queue, inventory, processor=flaky_processor)
    producer.publish_inventory_update("evt-002", "SKU002", 10)
    flaky_consumer.process_next()
    print("After failure, pending:", queue.pending_count())
    flaky_consumer.process_next()
    print("After retry, SKU002:", inventory.get("SKU002").quantity)

    print("\n=== 3. Permanent failure -> DLQ ===")
    def always_fail(_: Message) -> None:
        raise RuntimeError("Permanent processing failure")

    failing_consumer = InventoryConsumer(queue, inventory, processor=always_fail)
    producer.publish_inventory_update("evt-003", "SKU003", 7)
    for attempt in range(1, 4):
        failing_consumer.process_next()
        print(f"Attempt {attempt}: pending={queue.pending_count()} DLQ={queue.dead_letter_count()}")

    print("\n=== 4. Duplicate delivery / idempotency ===")
    queue.publish(Message("evt-001", "inventory.updated", {"product_id": "SKU001", "quantity": 999}))
    consumer.process_next()
    print("SKU001 remains:", inventory.get("SKU001").quantity)


if __name__ == "__main__":
    main()
