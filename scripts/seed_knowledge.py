import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"backend"))
from app.services.rag import knowledge

SAMPLE="""VoxAssist Demo Company — Customer Support Guide
Returns: Customers may request a return within 30 calendar days of delivery. Items must be unused and in original packaging. Refunds are initiated after inspection and usually take 5–7 business days to appear, depending on the bank.
Shipping: Standard delivery usually takes 3–5 business days. Orders marked Out for delivery are expected on the date shown by the tracking system.
Appointments: Customers can request a product consultation. A booking is not confirmed until a support specialist confirms availability.
Support hours: Monday to Saturday, 9:00 AM to 6:00 PM IST. The support team is closed on public holidays.
Payments: Never ask customers to disclose card numbers, CVV, passwords or OTPs over a call.
"""
print(f"Indexed {knowledge.ingest(SAMPLE,'demo-support-guide.md')} chunks")
