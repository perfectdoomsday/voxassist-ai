# Threat Model and Security Controls

| Threat | Mitigation |
|---|---|
| Prompt injection in uploaded KB | Treat retrieved chunks as untrusted data; strip active content; never execute instructions from docs |
| Unauthorized order lookup | Authenticate customer or verify an approved low-risk factor before exposing order data |
| Malicious tool arguments | Pydantic validation, allowlisted tools, server-side authorization, idempotency |
| Twilio webhook spoofing | Verify Twilio request signature, HTTPS, timestamp/replay protection |
| API abuse / cost exhaustion | Per-IP and per-tenant rate limits, quotas, concurrency caps, spend alerts |
| PII leakage in logs | Structured redaction, no raw secrets, access-controlled audit logs |
| Cross-tenant retrieval | Tenant metadata filters in every vector query and SQL query |
| Malicious file upload | Size/type validation, parser isolation, malware scanning, no macro execution |
| Dashboard compromise | OIDC/JWT, RBAC, MFA, CSRF protection where cookie auth is used |
| Call recording misuse | Explicit consent, jurisdiction-specific policy, retention/deletion controls |
| Provider outage | Timeouts, bounded retries, circuit breakers, fallback prompt and human handoff |

The included starter code is a development scaffold. It does not yet implement production authentication, tenant isolation, webhook signature verification, or durable persistence. Do not expose it to real customer traffic until those controls are implemented and reviewed.
