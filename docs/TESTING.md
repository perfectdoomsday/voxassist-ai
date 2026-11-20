# Testing Plan

## Automated
- Unit: intent routing, chunking, retrieval threshold, order lookup, appointment validation/idempotency.
- API: health, chat schema, upload size/type, knowledge search, 404 and validation responses.
- Integration: Qdrant upsert/search, Groq response contract, PostgreSQL persistence (run in CI with service containers).
- Frontend: component tests and Playwright flows for dashboard, call filters and KB upload.

## Manual voice test matrix
| Scenario | Expected behavior |
|---|---|
| FAQ with indexed policy | Concise answer grounded in the correct policy |
| Unknown policy question | Agent says it cannot verify and offers human support |
| Valid order ID | Returns only the matched order status |
| Missing order ID | Asks for order ID once |
| Invalid order ID | Does not invent status; offers retry/handoff |
| Caller interrupts TTS | Current speech stops and listens to new turn |
| Silence / background noise | Reprompt politely, then end or route per policy |
| Caller asks for human | Immediate escalation path and concise summary |
| Groq unavailable | Safe fallback, no fabricated business facts |
| Qdrant unavailable | Safe fallback or handoff; no unsupported policy answer |
| Tool timeout / duplicate request | Explain issue; idempotency prevents duplicate booking |
| PII / card details spoken | Do not repeat secrets; redact from stored transcript |
| Recording consent declined | Follow configured no-recording/no-transcript policy |

## Load and quality metrics
Measure concurrent calls, turn latency p50/p95/p99, STT word error rate, answer groundedness, retrieval precision@k, tool success, escalation rate, dropped calls and cost per resolved call. Use a curated evaluation set and review transcripts with consent.
