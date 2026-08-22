from dataclasses import dataclass

from .models import PrintRequest
from .queue import PrintQueue


@dataclass
class AttendeeState:
    attendee_id: str
    status: str
    job_id: str | None = None


class CheckInService:
    def __init__(self, queue: PrintQueue) -> None:
        self.queue = queue
        self.attendees: dict[str, AttendeeState] = {}
        self.processed_events: set[str] = set()
        self.job_counter = 0

    def check_in(self, attendee_id: str) -> AttendeeState:
        existing = self.attendees.get(attendee_id)

        if existing and existing.status in {"PENDING", "CHECKED_IN"}:
            return existing

        self.job_counter += 1
        job_id = f"JOB-{self.job_counter:03d}"

        state = AttendeeState(
            attendee_id=attendee_id,
            status="PENDING",
            job_id=job_id,
        )

        self.attendees[attendee_id] = state

        self.queue.publish(
            PrintRequest(
                job_id=job_id,
                attendee_id=attendee_id,
            )
        )

        return state

    def complete_print(
        self,
        *,
        event_id: str,
        job_id: str,
        attendee_id: str,
        status: str,
    ) -> AttendeeState | None:
        if event_id in self.processed_events:
            return self.attendees.get(attendee_id)

        state = self.attendees.get(attendee_id)

        if state is None:
            return None

        if state.job_id != job_id:
            return state

        self.processed_events.add(event_id)

        if status == "completed":
            state.status = "CHECKED_IN"

        return state