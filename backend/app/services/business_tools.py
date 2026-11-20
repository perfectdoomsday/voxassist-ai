from datetime import datetime, timezone
from typing import Any

DEMO_ORDERS = {
    "VH-1001": {"order_id": "VH-1001", "status": "Out for delivery", "eta": "Today, 6–8 PM", "items": ["Wireless headphones"]},
    "VH-1002": {"order_id": "VH-1002", "status": "Processing", "eta": "Ships in 1–2 business days", "items": ["USB-C hub"]},
}
_APPOINTMENTS: dict[str, dict[str, Any]] = {}

def get_order(order_id: str) -> dict[str, Any] | None:
    return DEMO_ORDERS.get(order_id.strip().upper())

def create_appointment(payload: dict[str, Any]) -> dict[str, Any]:
    key = payload["idempotency_key"]
    if key in _APPOINTMENTS:
        return _APPOINTMENTS[key]
    when = payload["requested_at"]
    if isinstance(when, str):
        when = datetime.fromisoformat(when.replace("Z", "+00:00"))
    if when.tzinfo is None:
        raise ValueError("requested_at must include a timezone")
    if when <= datetime.now(timezone.utc):
        raise ValueError("Appointment must be in the future")
    result = {"appointment_id": f"APT-{len(_APPOINTMENTS)+1:04d}", "status": "requested", "requested_at": when.isoformat(), "customer_name": payload["customer_name"]}
    _APPOINTMENTS[key] = result
    return result
