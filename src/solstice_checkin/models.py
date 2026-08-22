from pydantic import BaseModel, Field


class CheckInRequest(BaseModel):
    attendee_id: str = Field(min_length=1)


class CheckInResponse(BaseModel):
    attendee_id: str
    status: str
    message: str
    job_id: str | None = None


class PrintRequest(BaseModel):
    job_id: str
    attendee_id: str


class PrintWebhook(BaseModel):
    event_id: str
    job_id: str
    attendee_id: str
    status: str