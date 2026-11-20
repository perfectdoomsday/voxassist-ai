from datetime import datetime
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=4000)
    caller_id: str | None = Field(default=None, max_length=64)

class ChatResponse(BaseModel):
    session_id: str
    response: str
    intent: str
    confidence: float
    escalated: bool = False
    escalation_reason: str | None = None
    sources: list[str] = []
    tool_result: dict | None = None

class KnowledgeSearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=1000)
    limit: int = Field(default=4, ge=1, le=10)

class AppointmentRequest(BaseModel):
    customer_name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=7, max_length=20)
    requested_at: datetime
    reason: str = Field(min_length=3, max_length=500)
    idempotency_key: str = Field(min_length=8, max_length=128)
