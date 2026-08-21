# Learning Plan

## Objective

Understand producer/consumer messaging, acknowledgement, retries, duplicate delivery, idempotency and dead-letter handling well enough to explain each decision without relying on a tutorial.

## Experiments

1. Happy path: Producer -> Queue -> Consumer.
2. Publish while the consumer is unavailable.
3. Force processing failure and observe requeue.
4. Repeated failure and observe DLQ.
5. Deliver a duplicate event ID and observe idempotency.
6. Send an invalid payload and decide whether it should retry or DLQ.

## Questions to answer in the journal

- Why use a queue instead of direct synchronous calls?
- When is a message successfully processed?
- Why ACK after processing?
- What does at-least-once delivery imply?
- Why is idempotency important?
- When should a failed message stop retrying?
