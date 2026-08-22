import os

from fastapi import FastAPI, Header, HTTPException, Request

from .models import CheckInRequest, CheckInResponse, PrintWebhook
from .queue import PrintQueue
from .security import verify_signature
from .service import CheckInService


app = FastAPI(
    title="Solstice Async Badge Check-In"
)

WEBHOOK_SECRET = os.getenv(
    "SOLSTICE_WEBHOOK_SECRET",
    "solstice-demo-secret",
)

queue = PrintQueue()
service = CheckInService(queue)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/check-in", response_model=CheckInResponse)
def check_in(request: CheckInRequest) -> CheckInResponse:
    state = service.check_in(request.attendee_id)

    if state.status == "CHECKED_IN":
        message = "Attendee already checked in"
    else:
        message = "Badge print request is pending"

    return CheckInResponse(
        attendee_id=state.attendee_id,
        status=state.status,
        message=message,
        job_id=state.job_id,
    )


@app.get(
    "/check-in/{attendee_id}",
    response_model=CheckInResponse,
)
def get_check_in(attendee_id: str) -> CheckInResponse:
    state = service.attendees.get(attendee_id)

    if state is None:
        raise HTTPException(
            status_code=404,
            detail="Attendee not found",
        )

    return CheckInResponse(
        attendee_id=state.attendee_id,
        status=state.status,
        message="Current check-in status",
        job_id=state.job_id,
    )


@app.get("/queue")
def queue_status() -> dict[str, int]:
    return {"pending": queue.pending()}


@app.post("/webhooks/print-complete")
async def print_complete(
    request: Request,
    x_solstice_signature: str | None = Header(default=None),
) -> dict[str, str]:

    raw_body = await request.body()

    if not x_solstice_signature:
        raise HTTPException(
            status_code=403,
            detail="Missing signature",
        )

    if not verify_signature(
        raw_body,
        x_solstice_signature,
        WEBHOOK_SECRET,
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid signature",
        )

    try:
        payload = PrintWebhook.model_validate_json(raw_body)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid webhook payload",
        ) from exc

    state = service.complete_print(
        event_id=payload.event_id,
        job_id=payload.job_id,
        attendee_id=payload.attendee_id,
        status=payload.status,
    )

    if state is None:
        raise HTTPException(
            status_code=404,
            detail="Attendee not found",
        )

    return {
        "status": "accepted",
        "attendee_status": state.status,
    }