from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.api.routes import router

settings=get_settings(); configure_logging(settings.log_level)
app=FastAPI(title=settings.app_name,version="1.0.0",description="Real-time customer support voice agent control plane",docs_url="/docs" if settings.app_env!="production" else None)
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origin_list,allow_credentials=True,allow_methods=["GET","POST"],allow_headers=["Authorization","Content-Type","X-Request-ID"])
app.include_router(router,prefix=settings.api_prefix)

@app.get("/")
async def root():
    return {
        "project": "VoxAssist AI",
        "message": "AI-powered customer support voice agent",
        "status": "running",
        "health": "/health",
        "api_docs": "/docs"
    }
    
@app.get("/health")
async def health(): return {"status":"ok","service":"voxassist-api","environment":settings.app_env}
