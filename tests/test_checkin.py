import json

from fastapi.testclient import TestClient

from solstice_checkin.app import app, queue, service
from solstice_checkin.security import sign_payload


client = TestClient(app)

SECRET = "solstice-demo-secret"


def reset_state():
    service.attendees.clear()
    service.processed_events.clear()
    service.job_counter = 0

    while queue.get() is not None:
        pass


def signed_webhook(payload: dict) -> dict:
    raw = json.dumps(
        payload,
        separators=(",", ":"),
    ).encode()

    return {
        "json": payload,
        "headers": {
            "X-Solstice-Signature": sign_payload(
                raw,
                SECRET,
            )
        },
    }


def test_first_scan_is_pending():
    reset_state()

    response = client.post(
        "/check-in",
        json={"attendee_id": "ATT-001"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "PENDING"
    assert response.json()["job_id"] == "JOB-001"
    assert queue.pending() == 1


def test_webhook_changes_pending_to_checked_in():
    reset_state()

    first = client.post(
        "/check-in",
        json={"attendee_id": "ATT-001"},
    )

    job_id = first.json()["job_id"]

    payload = {
        "event_id": "EVENT-001",
        "job_id": job_id,
        "attendee_id": "ATT-001",
        "status": "completed",
    }

    response = client.post(
        "/webhooks/print-complete",
        **signed_webhook(payload),
    )

    assert response.status_code == 200
    assert response.json()["attendee_status"] == "CHECKED_IN"

    assert (
        client
        .get("/check-in/ATT-001")
        .json()["status"]
        == "CHECKED_IN"
    )


def test_duplicate_scan_does_not_create_second_print_job():
    reset_state()

    first = client.post(
        "/check-in",
        json={"attendee_id": "ATT-001"},
    )

    second = client.post(
        "/check-in",
        json={"attendee_id": "ATT-001"},
    )

    assert first.json()["job_id"] == second.json()["job_id"]
    assert second.json()["status"] == "PENDING"
    assert queue.pending() == 1


def test_duplicate_scan_after_completion_does_not_create_job():
    reset_state()

    first = client.post(
        "/check-in",
        json={"attendee_id": "ATT-001"},
    )

    job_id = first.json()["job_id"]

    payload = {
        "event_id": "EVENT-001",
        "job_id": job_id,
        "attendee_id": "ATT-001",
        "status": "completed",
    }

    client.post(
        "/webhooks/print-complete",
        **signed_webhook(payload),
    )

    third = client.post(
        "/check-in",
        json={"attendee_id": "ATT-001"},
    )

    assert third.json()["status"] == "CHECKED_IN"
    assert queue.pending() == 1


def test_duplicate_webhook_is_idempotent():
    reset_state()

    first = client.post(
        "/check-in",
        json={"attendee_id": "ATT-001"},
    )

    job_id = first.json()["job_id"]

    payload = {
        "event_id": "EVENT-001",
        "job_id": job_id,
        "attendee_id": "ATT-001",
        "status": "completed",
    }

    first_webhook = client.post(
        "/webhooks/print-complete",
        **signed_webhook(payload),
    )

    second_webhook = client.post(
        "/webhooks/print-complete",
        **signed_webhook(payload),
    )

    assert first_webhook.status_code == 200
    assert second_webhook.status_code == 200

    assert (
        client
        .get("/check-in/ATT-001")
        .json()["status"]
        == "CHECKED_IN"
    )


def test_invalid_signature_returns_403():
    reset_state()

    payload = {
        "event_id": "EVENT-001",
        "job_id": "JOB-001",
        "attendee_id": "ATT-001",
        "status": "completed",
    }

    raw = json.dumps(
        payload,
        separators=(",", ":"),
    ).encode()

    response = client.post(
        "/webhooks/print-complete",
        content=raw,
        headers={
            "X-Solstice-Signature": "invalid"
        },
    )

    assert response.status_code == 403


def test_missing_signature_returns_403():
    reset_state()

    payload = {
        "event_id": "EVENT-001",
        "job_id": "JOB-001",
        "attendee_id": "ATT-001",
        "status": "completed",
    }

    response = client.post(
        "/webhooks/print-complete",
        json=payload,
    )

    assert response.status_code == 403


def test_three_attendees_with_one_duplicate():
    reset_state()

    first = client.post(
        "/check-in",
        json={"attendee_id": "ATT-001"},
    )

    second = client.post(
        "/check-in",
        json={"attendee_id": "ATT-002"},
    )

    third = client.post(
        "/check-in",
        json={"attendee_id": "ATT-003"},
    )

    duplicate = client.post(
        "/check-in",
        json={"attendee_id": "ATT-003"},
    )

    assert first.json()["status"] == "PENDING"
    assert second.json()["status"] == "PENDING"
    assert third.json()["status"] == "PENDING"

    assert (
        duplicate.json()["job_id"]
        == third.json()["job_id"]
    )

    assert queue.pending() == 3