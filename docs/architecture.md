# Architecture Notes

## Message Queue

The message queue is the central component responsible for managing message delivery between the producer and consumer. It maintains messages that are waiting to be processed, messages currently being processed, and messages that have failed permanently.

```text
Producer
   |
   | publish
   v
Message Queue
   |
   | receive
   v
Consumer
```

The queue deliberately exposes the message lifecycle so that publishing, receiving, acknowledgement, retry, and dead-letter behavior can be observed and tested without relying on a production message broker.

## Message States

A message moves through the queue according to its processing result:

```text
Pending -> In-Flight -> ACK
              |
              +-> Failure -> Retry -> Pending
                                |
                                +-> Max attempts -> DLQ
```

A message enters the pending state when it is published. When a consumer receives it, the message becomes in-flight. Successful processing results in acknowledgement and removes the message from active delivery.

## ACK Rule

A message is acknowledged only after successful processing:

```text
receive -> process -> ACK
```

Acknowledging before processing could cause data loss if the consumer crashes after the ACK but before completing the operation.

## Retry and DLQ

When processing fails, the message is returned for another attempt rather than being discarded.

```text
Attempt 1 -> Failure -> Retry
Attempt 2 -> Failure -> Retry
Attempt 3 -> Failure -> DLQ
```

The maximum-attempt limit prevents a permanently failing message from being retried indefinitely. Once the limit is reached, the message is moved to the dead-letter queue.

## At-Least-Once Delivery

Because failed messages can be delivered again, the consumer must tolerate duplicate delivery. The message contains an event ID so that downstream processing can identify whether an event has already been handled.

The queue therefore provides controlled at-least-once delivery with retry and dead-letter handling, while duplicate protection is handled by the consuming business logic.