# Deployment and Telephony Runbook

## Local services
Use Docker Compose for Qdrant, Postgres and Redis. Run FastAPI and React locally as described in README.

## Deploy API
1. Build backend image from `backend/` (add a production Dockerfile and non-root user before public deployment).
2. Configure secrets through the cloud secret manager, not image build args.
3. Expose only HTTPS port 8000 through an ingress/load balancer.
4. Set `APP_ENV=production`, strict `CORS_ORIGINS`, strong `SECRET_KEY`, managed database URLs and provider keys.
5. Add `/health` liveness/readiness probes and autoscaling based on CPU/requests.

## Deploy voice worker
Voice sessions are long-running media workloads. Deploy the worker as a persistent container/VM or use the LiveKit-managed deployment path. Do not deploy a persistent audio worker as a short-lived HTTP function. Set LiveKit and selected STT/TTS provider secrets. Pin tested SDK/plugin versions in requirements before release.

## Twilio + LiveKit inbound calls
1. Purchase/verify a Twilio voice-capable number for your target region.
2. Create a Twilio Elastic SIP Trunk and associate the phone number.
3. In Twilio, configure the trunk origination URI to your LiveKit SIP endpoint, using the exact endpoint and transport recommended by the LiveKit console/docs.
4. In LiveKit, create an inbound SIP trunk with allowed numbers/authentication and a dispatch rule to route calls to the VoxAssist agent.
5. Configure outbound termination/authentication only if outbound calling is required and legally approved.
6. Test from an allowlisted number; inspect SIP logs, LiveKit room events and worker logs.

For a simpler inbound-only proof of concept, LiveKit documents Twilio Programmable Voice/TwiML routing. For broader inbound/outbound support, use Elastic SIP Trunking.

## Provider selection
- STT: Deepgram or a LiveKit-supported alternative; Whisper is suitable for batch/fallback but may not meet streaming latency requirements in every setup.
- TTS: Cartesia or ElevenLabs, selected based on latency, voice quality, languages and price.
- LLM: Groq-hosted model; verify current model IDs, context limits and rate limits before deployment.
- Embeddings: local Sentence Transformers for cost control; hosted embedding API optional.

## Production launch checklist
- [ ] Domain + TLS and secure headers
- [ ] Dashboard auth, RBAC, MFA for admins
- [ ] Tenant isolation on API, DB and vector search
- [ ] Signed Twilio webhooks and replay protection
- [ ] Call recording/transcription consent and jurisdiction review
- [ ] Data retention, export and deletion process
- [ ] Human transfer destination and staffing coverage
- [ ] Rate limits, abuse detection and spending alerts
- [ ] Database/vector backups and restore test
- [ ] Load test with expected concurrent calls
- [ ] Alerting for call failure, STT/TTS error, tool timeout and escalation rate
- [ ] Disaster fallback message and human queue procedure
