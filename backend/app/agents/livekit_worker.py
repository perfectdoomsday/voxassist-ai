"""LiveKit worker integration boundary. Install/pin the LiveKit Agents SDK and provider plugins.

This intentionally fails with an actionable message if optional voice dependencies or credentials
are absent; the FastAPI text simulation remains usable without them.
"""
import asyncio
from app.core.config import get_settings

async def entrypoint(ctx):
    settings=get_settings()
    if not (settings.livekit_url and settings.livekit_api_key and settings.livekit_api_secret):
        raise RuntimeError("Set LIVEKIT_URL, LIVEKIT_API_KEY and LIVEKIT_API_SECRET before starting the voice worker")
    # Wire a livekit.agents.AgentServer / AgentSession here using your selected provider plugins.
    # Keep provider-specific STT/TTS classes in this adapter, not in the business workflow.
    await ctx.connect()
    raise RuntimeError("Voice provider plugins are not configured yet. Follow README real phone-call setup and docs/DEPLOYMENT.md")

if __name__ == "__main__":
    try:
        from livekit.agents import cli, WorkerOptions
    except ImportError as exc:
        raise SystemExit("Install LiveKit Agents and the chosen provider plugins first.") from exc
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
