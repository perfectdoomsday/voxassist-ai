from typing import TypedDict, Any
from langgraph.graph import StateGraph, START, END
from app.services.rag import knowledge
from app.services.llm import generate_reply
from app.services.business_tools import get_order

class AgentState(TypedDict, total=False):
    session_id: str
    message: str
    intent: str
    confidence: float
    context: str
    sources: list[str]
    tool_result: dict[str, Any] | None
    response: str
    escalated: bool
    escalation_reason: str | None

def classify(state: AgentState) -> dict:
    text=state["message"].lower()
    if any(w in text for w in ["human", "agent", "representative", "complaint", "supervisor", "angry"]): intent="handoff"; confidence=0.96
    elif any(w in text for w in ["order", "delivery", "tracking", "shipped", "where is"]): intent="order_status"; confidence=0.88
    elif any(w in text for w in ["appointment", "book", "schedule", "meeting"]): intent="appointment"; confidence=0.82
    else: intent="faq"; confidence=0.65
    return {"intent": intent, "confidence": confidence}

def retrieve(state: AgentState) -> dict:
    docs=knowledge.search(state["message"])
    return {"context": "\n".join(f"[{d.source}] {d.text}" for d in docs), "sources": list(dict.fromkeys(d.source for d in docs))}

def route(state: AgentState) -> str:
    if state.get("intent")=="handoff": return "handoff"
    if state.get("intent")=="order_status": return "order"
    return "answer"

def order_lookup(state: AgentState) -> dict:
    import re
    match=re.search(r"VH-\d{4}", state["message"].upper())
    order=get_order(match.group(0)) if match else None
    if not match: return {"tool_result": None, "response": "I can check that. What is your order number?"}
    if not order: return {"tool_result": None, "response": "I couldn't find that order number. Please check it, or I can connect you to a support representative."}
    return {"tool_result": order}

async def answer(state: AgentState) -> dict:
    reply=await generate_reply(state["message"], state.get("context", ""), state.get("tool_result"))
    return {"response": reply, "escalated": False}

def handoff(state: AgentState) -> dict:
    return {"response": "I’ll connect you with a support specialist. I’ll also share a short summary so you don’t have to repeat everything.", "escalated": True, "escalation_reason": "Caller requested a human or conversation requires review."}

def build_graph():
    graph=StateGraph(AgentState)
    graph.add_node("classify", classify); graph.add_node("retrieve", retrieve); graph.add_node("order", order_lookup); graph.add_node("answer", answer); graph.add_node("handoff", handoff)
    graph.add_edge(START,"classify")
    graph.add_conditional_edges("classify", route, {"handoff":"handoff", "order":"order", "answer":"retrieve"})
    graph.add_edge("retrieve","answer"); graph.add_edge("order","answer"); graph.add_edge("answer",END); graph.add_edge("handoff",END)
    return graph.compile()

agent_graph=build_graph()

async def run_agent(session_id: str, message: str) -> dict:
    return await agent_graph.ainvoke({"session_id":session_id,"message":message,"escalated":False})
