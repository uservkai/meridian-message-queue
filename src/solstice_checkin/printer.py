from .models import PrintRequest


class PrinterSimulator:
    """Represents the vendor-side printer worker."""

    def print_badge(self, request: PrintRequest) -> dict[str, str]:
        return {
            "job_id": request.job_id,
            "attendee_id": request.attendee_id,
            "status": "completed",
        }