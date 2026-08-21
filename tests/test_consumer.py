from meridian_queue.consumer import InventoryConsumer
from meridian_queue.inventory import InventoryService
from meridian_queue.producer import InventoryProducer
from meridian_queue.queue import MessageQueue


def test_consumer_acknowledges_successful_processing() -> None:
    queue = MessageQueue()
    inventory = InventoryService()
    producer = InventoryProducer(queue)
    consumer = InventoryConsumer(queue, inventory)
    producer.publish_inventory_update("evt-1", "SKU001", 25)
    assert consumer.process_next() is True
    assert queue.in_flight_count() == 0
    assert queue.pending_count() == 0
    assert inventory.get("SKU001").quantity == 25


def test_consumer_requeues_failed_processing() -> None:
    queue = MessageQueue(max_attempts=3)
    inventory = InventoryService()
    def fail(_):
        raise RuntimeError("temporary failure")
    consumer = InventoryConsumer(queue, inventory, processor=fail)
    InventoryProducer(queue).publish_inventory_update("evt-1", "SKU001", 25)
    consumer.process_next()
    assert queue.pending_count() == 1
    assert queue.dead_letter_count() == 0


def test_consumer_sends_permanent_failure_to_dlq() -> None:
    queue = MessageQueue(max_attempts=1)
    inventory = InventoryService()
    def fail(_):
        raise RuntimeError("permanent failure")
    consumer = InventoryConsumer(queue, inventory, processor=fail)
    InventoryProducer(queue).publish_inventory_update("evt-1", "SKU001", 25)
    consumer.process_next()
    assert queue.pending_count() == 0
    assert queue.dead_letter_count() == 1
