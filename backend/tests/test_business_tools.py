from datetime import datetime, timedelta, timezone
import pytest
from app.services.business_tools import get_order, create_appointment

def test_order_lookup():
    assert get_order("vh-1001")["status"] == "Out for delivery"
    assert get_order("unknown") is None

def test_appointment_idempotency():
    payload={"customer_name":"Asha","phone":"9999999999","requested_at":datetime.now(timezone.utc)+timedelta(days=1),"reason":"Product consultation","idempotency_key":"request-0001"}
    first=create_appointment(payload); second=create_appointment(payload)
    assert first == second

def test_appointment_rejects_naive_time():
    payload={"customer_name":"Asha","phone":"9999999999","requested_at":datetime.now()+timedelta(days=1),"reason":"Consultation","idempotency_key":"request-0002"}
    with pytest.raises(ValueError): create_appointment(payload)
