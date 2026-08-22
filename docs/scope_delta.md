# Scope Delta Analysis

## Dropped

The synchronous printer REST call is dropped. The check-in flow no longer waits for an immediate printer response, and the attendee is no longer marked `CHECKED_IN` immediately after scanning.

## Modified

The check-in state now moves from a pending state to `CHECKED_IN` only after successful printer confirmation. Duplicate-scan protection must also operate while a print job is still pending.

## Added

The solution adds an asynchronous print message queue, printer worker simulation, webhook receiver, HMAC-SHA256 signature verification, webhook event idempotency, job correlation, and explicit pending-state handling.

## Trade-offs

The asynchronous model prevents the kiosk from blocking on the printer and decouples the kiosk from the printer's response time. The trade-off is eventual consistency: the application must explicitly represent pending work and safely process delayed, duplicate, or invalid webhook events.

## Regression Checks

The implementation tests first scans, duplicate scans while pending, duplicate scans after completion, successful webhook confirmation, duplicate webhooks, invalid signatures, missing signatures, and three attendees including a duplicate scan.

The complete test suite was also executed successfully with:


26 passed, 1 warning
