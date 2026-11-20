from fastapi import APIRouter, UploadFile, File, HTTPException
from pypdf import PdfReader
from io import BytesIO
from app.models.schemas import ChatRequest, ChatResponse, KnowledgeSearchRequest, AppointmentRequest
from app.agents.graph import run_agent
from app.services.rag import knowledge
from app.services.business_tools import get_order, create_appointment

router=APIRouter()
_CALLS: list[dict] = []

@router.post("/agent/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    result=await run_agent(payload.session_id,payload.message)
    record={"session_id":payload.session_id,"message":payload.message,"response":result.get("response",""),"intent":result.get("intent","unknown"),"escalated":result.get("escalated",False)}
    _CALLS.insert(0,record); del _CALLS[100:]
    return ChatResponse(session_id=payload.session_id,response=record["response"],intent=record["intent"],confidence=result.get("confidence",0.0),escalated=record["escalated"],escalation_reason=result.get("escalation_reason"),sources=result.get("sources",[]),tool_result=result.get("tool_result"))

@router.post("/knowledge/upload")
async def upload_knowledge(file: UploadFile=File(...)):
    if not file.filename: raise HTTPException(400,"Filename is required")
    if len(file.filename)>180 or file.content_type not in {"text/plain","text/markdown","application/pdf","application/octet-stream"}: raise HTTPException(415,"Only TXT, Markdown and PDF files are supported")
    data=await file.read(5_000_001)
    if len(data)>5_000_000: raise HTTPException(413,"File exceeds 5 MB limit")
    try:
        if file.filename.lower().endswith(".pdf"): text="\n".join(p.extract_text() or "" for p in PdfReader(BytesIO(data)).pages)
        elif file.filename.lower().endswith((".txt",".md")): text=data.decode("utf-8")
        else: raise HTTPException(415,"File extension must be .txt, .md or .pdf")
        count=knowledge.ingest(text,file.filename)
        return {"filename":file.filename,"chunks_indexed":count}
    except HTTPException: raise
    except Exception as exc: raise HTTPException(400,f"Could not process document: {type(exc).__name__}") from exc

@router.post("/knowledge/search")
async def search_knowledge(payload: KnowledgeSearchRequest):
    return {"results":[{"text":x.text,"source":x.source,"score":x.score} for x in knowledge.search(payload.query,payload.limit)]}

@router.get("/calls")
async def list_calls(): return {"calls":_CALLS}

@router.get("/analytics/summary")
async def analytics():
    total=len(_CALLS); escalated=sum(1 for c in _CALLS if c["escalated"])
    return {"total_calls":total,"escalated_calls":escalated,"automation_rate":round((total-escalated)/total*100,1) if total else 0,"intents":{k:sum(1 for c in _CALLS if c["intent"]==k) for k in {c["intent"] for c in _CALLS}}}

@router.get("/tools/orders/{order_id}")
async def order_status(order_id: str):
    result=get_order(order_id)
    if not result: raise HTTPException(404,"Order not found")
    return result

@router.post("/tools/appointments")
async def appointment(payload: AppointmentRequest):
    try: return create_appointment(payload.model_dump())
    except ValueError as exc: raise HTTPException(422,str(exc)) from exc
