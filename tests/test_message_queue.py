from meridian_queue.message import Message
from meridian_queue.queue import MessageQueue


def make_message(event_id: str = "evt-1") -> Message:
    return Message(event_id, "inventory.updated", {"product_id": "SKU001", "quantity": 10})


def test_publish_and_receive() -> None:
    queue = MessageQueue()
    message = make_message()
    queue.publish(message)
    received = queue.receive()
    assert received is message
    assert queue.pending_count() == 0
    assert queue.in_flight_count() == 1


def test_ack_removes_in_flight_message() -> None:
    queue = MessageQueue()
    message = make_message()
    queue.publish(message)
    received = queue.receive()
    queue.acknowledge(received.event_id)
    assert queue.in_flight_count() == 0


def test_failed_message_is_requeued_before_max_attempts() -> None:
    queue = MessageQueue(max_attempts=3)
    message = make_message()
    queue.publish(message)
    received = queue.receive()
    received.record_attempt()
    queue.reject(received.event_id)
    assert queue.pending_count() == 1
    assert queue.dead_letter_count() == 0


def test_message_moves_to_dlq_after_max_attempts() -> None:
    queue = MessageQueue(max_attempts=2)
    message = make_message()
    queue.publish(message)
    for _ in range(2):
        received = queue.receive()
        received.record_attempt()
        queue.reject(received.event_id)
    assert queue.pending_count() == 0
    assert queue.dead_letter_count() == 1
