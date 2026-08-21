
# Learning & Blocker Journal

## The Meridian Pivot — Phase 1: Message Queue

## Tool Selected

Message Queue

## Project

Meridian Message Queue — Phase 1 Solo Recon

## Programming Language

Python 3.12

---

## Morning — Project Setup

### Time

Morning

### Problem

I needed to build a mini message queue prototype for the Meridian Pivot Phase 1
assignment using a tool that I was learning independently.

The prototype needed to demonstrate message production, queueing, consumption,
acknowledgement, retry handling, dead-letter queue behavior, and duplicate
delivery handling.

### Expected Behavior

The system should follow:

```text
Producer -> Message Queue -> Consumer -> Inventory Service
                 |                |
                 |                +-> ACK after success
                 |
                 +-> retry on failure -> DLQ after max attempts
````

A successful message should be processed and acknowledged. A failed message
should be retried, and a message that continues to fail should eventually be
moved to the dead-letter queue.

### Actual Behavior

The initial project structure was created with the implementation separated
into message, queue, producer, consumer, and inventory components.

The intended structure was:

```text
src/
└── meridian_queue/
    ├── __init__.py
    ├── message.py
    ├── queue.py
    ├── producer.py
    ├── consumer.py
    └── inventory.py
```

### Investigation

I first focused on understanding the message lifecycle rather than using a
production message broker. The prototype was designed as an in-memory queue
so that the states of messages could be observed directly.

The main lifecycle identified was:

```text
Pending -> In-Flight -> ACK
              |
              +-> Failure -> Retry -> Pending
                                |
                                +-> Max attempts -> DLQ
```

### Result

The basic architecture and project structure were established.

### Lesson Learned

A message queue is not simply storage for messages. It controls the delivery
lifecycle and provides mechanisms for acknowledgement, retry, and handling
messages that cannot be successfully processed.

---

## Initial Architecture Understanding

### Time

Morning

### Problem

I needed to determine how the individual components should interact without
tightly coupling the business logic to the queue.

### Expected Behavior

Each component should have a clear responsibility.

### Actual Behavior

The system was separated into:

```text
message.py
queue.py
producer.py
consumer.py
inventory.py
```

The producer creates and publishes messages. The queue manages message state.
The consumer retrieves and processes messages. The inventory service performs
the business operation.

### Investigation

I considered the message lifecycle from the perspective of both successful
and failed processing.

A successful message follows:

```text
Producer
   |
   v
Queue
   |
   v
Consumer
   |
   v
Inventory
   |
   v
ACK
```

A failed message follows:

```text
Consumer
   |
   v
Failure
   |
   v
Retry
   |
   +-> Success -> ACK
   |
   +-> Maximum attempts -> DLQ
```

### Result

The responsibilities of the components were separated before testing.

### Lesson Learned

Keeping queue infrastructure separate from inventory business logic makes the
system easier to understand, test, and replace with a production broker later.

---

## ACK Experiment and Understanding

### Time

Morning

### Problem

I needed to understand when a message should be acknowledged.

### Expected Behavior

A message should only be acknowledged after successful processing.

```text
receive -> process -> ACK
```

### Actual Behavior

The architecture was designed so that acknowledgement occurs only after the
consumer successfully processes the message.

### Investigation

I considered what would happen if the consumer acknowledged the message
before processing it.

The failure scenario would be:

```text
receive
   |
   v
ACK
   |
   v
process
   |
   X crash
```

In that situation the queue would believe that processing had succeeded even
though the business operation had not completed.

### Result

The ACK rule was established as:

```text
receive -> process successfully -> ACK
```

### Lesson Learned

ACK represents successful processing, not simply successful message receipt.
Acknowledging too early can cause data loss.

---

## Retry and DLQ Understanding

### Time

Morning

### Problem

I needed to determine what should happen when message processing fails.

### Expected Behavior

A temporary failure should allow another processing attempt. A message that
continues to fail should eventually be removed from normal processing and
placed into the DLQ.

### Actual Behavior

The queue was designed to return failed messages for another attempt until the
maximum number of attempts is reached.

```text
Attempt 1 -> Failure -> Retry
Attempt 2 -> Failure -> Retry
Attempt 3 -> Failure -> DLQ
```

### Investigation

I separated failure handling into two possible outcomes.

A temporary failure can recover:

```text
Failure -> Retry -> Success -> ACK
```

A permanent failure eventually becomes:

```text
Failure -> Retry -> Failure -> Retry -> Max Attempts -> DLQ
```

### Result

The queue supports controlled retry behavior and a dead-letter queue.

### Lesson Learned

Retrying indefinitely is not a safe failure strategy. A maximum attempt limit
is needed so that permanently failing messages do not remain in the normal
processing path forever.

---

## At-Least-Once Delivery and Duplicate Processing

### Time

Morning

### Problem

A message that fails can be delivered again, meaning the same event may reach
the consumer more than once.

### Expected Behavior

Duplicate delivery should not cause the same inventory event to be applied
twice.

### Actual Behavior

The inventory processing design uses an event ID to identify messages that
have already been processed.

For example:

```text
Event ID: evt-001
SKU: SKU001
Quantity: 25
```

First delivery:

```text
evt-001 -> process -> SKU001 = 25
```

Duplicate delivery:

```text
evt-001 -> already processed -> ignore
```

### Investigation

The duplicate scenario was considered as a direct consequence of retry and
at-least-once delivery.

If a consumer processes an event successfully but the delivery state is not
updated as expected, the same event can potentially be delivered again.

### Result

The inventory service was designed to use event identity to make repeated
delivery idempotent.

### Lesson Learned

At-least-once delivery requires downstream processing to tolerate duplicates.
Retry reliability and idempotency therefore need to be considered together.

---

## Package Structure Blocker

### Time

Afternoon

### Problem

I ran the message queue tests using:

```text
python -m pytest tests/test_message_queue.py -v
```

The tests failed during collection with:

```text
ModuleNotFoundError: No module named 'meridian_queue'
```

### Expected Behavior

The test contained:

```python
from meridian_queue.message import Message
```

Pytest should have been able to locate the `meridian_queue` package through the
`src` directory.

### Actual Behavior

The package could not be imported.

### Investigation

I checked the project structure instead of immediately changing the pytest
configuration.

The source directory was found to contain:

```text
src/
├── consumer.py
├── inventory.py
├── message.py
├── producer.py
├── queue.py
├── __init__.py
└── meridian_queue/
```

The implementation files were directly inside `src` instead of inside the
`meridian_queue` package.

The test expected:

```text
src/meridian_queue/message.py
```

but the actual file was:

```text
src/message.py
```

### What I Tried

I inspected the source directory and identified the incorrect package layout.

The implementation files were then moved into:

```text
src/meridian_queue/
```

The final structure became:

```text
src/
└── meridian_queue/
    ├── __init__.py
    ├── consumer.py
    ├── inventory.py
    ├── message.py
    ├── producer.py
    └── queue.py
```

### Result

The package structure was corrected.

The existing `pyproject.toml` configuration was retained:

```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
addopts = "-ra"
```

No unnecessary configuration change was made.

### Lesson Learned

Python package structure matters when using a `src` layout. The source modules
must be located inside the actual package directory that the tests are
importing.

This was an actual project blocker rather than a theoretical issue, and
resolving it required inspecting the filesystem and tracing the import path.

---

## Direct Python Import Investigation

### Time

Afternoon

### Problem

After correcting the package structure, I tested the package directly using:

```text
python -c "from meridian_queue.message import Message; print(Message)"
```

It still returned:

```text
ModuleNotFoundError: No module named 'meridian_queue'
```

### Expected Behavior

The package should be importable from Python.

### Actual Behavior

The direct Python command could not locate the package.

### Investigation

The difference between pytest configuration and a direct Python invocation was
examined.

The `pyproject.toml` contains:

```toml
pythonpath = ["src"]
```

This configuration is used by pytest. A direct `python -c` command does not
automatically apply pytest's configured Python path.

Therefore, the direct import failure did not mean that the package structure
was still incorrect.

### What I Tried

I returned to the actual project test command:

```text
python -m pytest tests/test_message_queue.py -v
```

### Result

Pytest successfully located the package and collected the tests.

### Lesson Learned

A direct Python invocation and pytest do not necessarily use the same import
path configuration. The correct way to verify the test environment was to use
the configured pytest command.

---

## First Successful Test Run

### Time

Afternoon

### Problem

The package structure had been corrected, so the next objective was to verify
the queue behavior.

### Expected Behavior

The queue tests should verify publishing, receiving, acknowledgement, retry,
and DLQ behavior.

### Actual Behavior

The test suite successfully collected four tests.

### Investigation

The following command was executed:

```text
python -m pytest tests/test_message_queue.py -v
```

### Result

All four tests passed:

```text
tests/test_message_queue.py::test_publish_and_receive PASSED [ 25%]
tests/test_message_queue.py::test_ack_removes_in_flight_message PASSED [ 50%]
tests/test_message_queue.py::test_failed_message_is_requeued_before_max_attempts PASSED [ 75%]
tests/test_message_queue.py::test_message_moves_to_dlq_after_max_attempts PASSED [100%]

4 passed in 0.07s
```

### Lesson Learned

The core queue implementation is functioning according to the expected
message lifecycle.

The successful tests provide evidence that the implementation can publish and
receive messages, acknowledge successfully processed messages, retry failed
messages, and move permanently failing messages to the DLQ.

---

## Test: Publish and Receive

### Time

Afternoon

### Problem

The first behavior to verify was whether messages could successfully move
through the basic queue path.

### Expected Behavior

A published message should become available to the consumer.

```text
Producer -> Queue -> Consumer
```

### Actual Behavior

The test passed.

### Investigation

The test was executed as part of:

```text
python -m pytest tests/test_message_queue.py -v
```

### Result

```text
test_publish_and_receive PASSED
```

### Lesson Learned

The basic producer-to-queue-to-consumer message flow is working.

---

## Test: ACK Removes In-Flight Message

### Time

Afternoon

### Problem

The next behavior to verify was whether successful processing removes the
message from active processing.

### Expected Behavior

A successfully processed message should be acknowledged and removed from the
in-flight state.

```text
receive -> process -> ACK
```

### Actual Behavior

The test passed.

### Investigation

The test verified the state of the message after acknowledgement.

### Result

```text
test_ack_removes_in_flight_message PASSED
```

### Lesson Learned

The queue correctly treats acknowledgement as completion of successful
processing.

---

## Test: Failed Message Is Requeued

### Time

Afternoon

### Problem

I needed to verify that a failed message would not immediately disappear.

### Expected Behavior

A failed message should be returned to the pending state while it still has
remaining attempts.

```text
In-Flight -> Failure -> Retry -> Pending
```

### Actual Behavior

The test passed.

### Investigation

The test verified that the failed message remained available for another
delivery attempt.

### Result

```text
test_failed_message_is_requeued_before_max_attempts PASSED
```

### Lesson Learned

The retry mechanism protects messages from being lost after temporary
processing failures.

---

## Test: Message Moves to DLQ

### Time

Afternoon

### Problem

I needed to verify what happens when a message fails repeatedly.

### Expected Behavior

Once the maximum number of attempts is reached, the message should no longer
remain in the normal queue and should instead be placed in the DLQ.

```text
Attempt 1 -> Failure
Attempt 2 -> Failure
Attempt 3 -> Failure
              |
              v
             DLQ
```

### Actual Behavior

The test passed.

### Investigation

The test verified the pending and DLQ states after the maximum number of
attempts.

### Result

```text
test_message_moves_to_dlq_after_max_attempts PASSED
```

### Lesson Learned

The queue correctly isolates permanently failing messages instead of retrying
them indefinitely.

---

## Current Status

### Time

Afternoon

### Problem

The Phase 1 message queue prototype needed to demonstrate the core messaging
patterns required by the assignment.

### Expected Behavior

The prototype should demonstrate a complete message lifecycle including
successful processing, acknowledgement, retry handling, DLQ handling, and
duplicate protection.

### Actual Behavior

The core queue tests are passing.

```text
4 passed in 0.07s
```

The verified queue behavior currently includes message publishing and
receiving, acknowledgement, retry handling, and dead-letter handling.

### Investigation

The implementation was tested through pytest after correcting the package
structure.

### Result

The core message queue functionality is working.

The architecture has also been documented separately in:

```text
docs/architecture.md
```

The architecture document focuses on how the message queue works, while this
journal records the actual learning process, blockers, investigation, and
results.

### Lesson Learned

The main technical learning from the prototype is that reliable messaging
requires more than moving a message from one component to another. The system
must explicitly handle acknowledgement, failure, retries, maximum attempts,
dead-letter handling, and duplicate delivery.

The troubleshooting process also demonstrated that package structure and
Python import paths can cause test failures even when the application logic
itself is correct.

---

## Assignment 1 Evidence

### Time

End of current work session

### Problem

The Meridian Pivot assignment requires evidence of independent learning,
functional correctness, troubleshooting autonomy, documentation, and
time-to-completion.

### Expected Behavior

The journal should show the actual learning process rather than only presenting
the final successful state.

### Actual Behavior

The project contains a working message queue prototype, documented
architecture, automated queue tests, and a record of the package-structure
blocker and its resolution.

### Investigation

The work progressed from understanding the message queue lifecycle to
implementing the components, testing them, diagnosing the import failure,
correcting the package structure, and rerunning the tests successfully.

### Result

The current verified result is:

```text
4 passed in 0.07s
```

The core Phase 1 message queue functionality is therefore working.

### Lesson Learned

The most important learning from this phase is that message queue reliability
comes from combining several mechanisms rather than relying on the queue alone.

The queue controls message delivery, acknowledgement confirms successful
processing, retries provide recovery from temporary failures, the DLQ isolates
permanent failures, and idempotency protects the business operation from
duplicate delivery.

The package-structure blocker also provided a practical troubleshooting
experience. Instead of changing configuration blindly, the source layout was
inspected, the import path was traced, the incorrect structure was identified,
and the implementation was moved into the correct Python package.

The prototype now provides a working foundation for demonstrating the message
queue concept required by the Meridian Pivot Phase 1 assignment.


# Blockers

## Requirements Development File Naming

### Problem

I initially created the development requirements file with the wrong filename:

```text
requiements-dev.txt
````

The intended filename was:

```text
requirements-dev.txt
```

### Expected Behavior

The development requirements file should use the standard filename:

```text
requirements-dev.txt
```

so that it can be clearly identified as containing development and testing
dependencies.

### Actual Behavior

The filename contained a typo.

### Investigation

I checked the project files and identified that the filename itself was
incorrect rather than there being a problem with the requirements content.

### Fix

The file was renamed to:

```text
requirements-dev.txt
```

### Lesson Learned

Small naming errors can create unnecessary confusion in a project. Standard
filenames should be checked carefully, particularly for configuration and
dependency files.

---

## Log: Resolving Test Collection Failures

### Problem

Running pytest initially produced:

```text
ModuleNotFoundError: No module named 'meridian_queue'
```

The testing framework could not correctly locate the source package.

### Goal

I needed pytest to recognize the modern `src/` project layout so that tests
could import the application package using:

```python
from meridian_queue.message import Message
```

I also wanted the Python path configuration to be stored permanently in the
project configuration instead of relying on manual terminal flags.

### Failure

The intended pytest configuration was placed in a file named:

```text
project.toml
```

instead of the standardized:

```text
pyproject.toml
```

Because pytest looks for project configuration in `pyproject.toml`, it did not
load the intended `tool.pytest.ini_options` settings.

As a result, the configured `src` Python path was ignored.

### Fix

The configuration file was renamed to:

```text
pyproject.toml
```

After the filename was corrected, pytest recognized the configuration.

### Verified Configuration

The relevant configuration is:

```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
```

This allows pytest to locate the package inside the `src/` directory without
requiring a manual Python path argument every time the tests are run.

### Verification

The test command was then run again:

```text
python -m pytest tests/test_message_queue.py -v
```

The tests were successfully collected and executed:

```text
collected 4 items

tests/test_message_queue.py::test_publish_and_receive PASSED
tests/test_message_queue.py::test_ack_removes_in_flight_message PASSED
tests/test_message_queue.py::test_failed_message_is_requeued_before_max_attempts PASSED
tests/test_message_queue.py::test_message_moves_to_dlq_after_max_attempts PASSED

4 passed in 0.07s
```

### Lesson Learned

Configuration filenames are part of the tooling contract. A technically
correct configuration is ineffective if the tool cannot find it.

The incident also reinforced the importance of reading the exact error,
checking the project structure, and verifying configuration loading before
changing application code.

```
```
