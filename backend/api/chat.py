import time 
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from backend.dependencies.auth import get_current_user
from backend.models.chat import ChatRequest
from backend.memory.working_memory import WorkingMemory
from backend.memory.context_builder import ContextBuilder
from backend.agent.agent import Agent 
from backend.stores.session_store import SessionStore
from backend.core.dependencies import PLANNER , REGISTRY
import asyncio


agent_semaphore = asyncio.Semaphore(5)
router = APIRouter(tags=["Chat"])
session_store = SessionStore()

class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(min_length=1, max_length=10000)

class ChatResponse(BaseModel):
    session_id: str
    user_id: str
    message: str

@router.post("/chat", response_model=ChatResponse)

async def chat(
    request: ChatRequest,
    current_user=Depends(get_current_user),
):
    
    start_time = time.perf_counter()

    user_id = str(current_user.id)

    session = session_store.get_session(
        user_id=user_id,
        session_id=request.session_id,
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    working_memory = WorkingMemory(
        session_id=request.session_id,
        max_tokens=2000,
    )

    context_builder = ContextBuilder(
        working_memory=working_memory,
        total_budget=3000,
    )

    agent = Agent(
        user_id=user_id,
        session_id=request.session_id,
        working_memory=working_memory,
        context_builder=context_builder,
        planner=PLANNER,
        registry=REGISTRY,
    )

    #async with agent_semaphore:
    final_ans = await agent.run(request.message)

    total_time = time.perf_counter() - start_time

    print(f" Total request time: {total_time:.2f} seconds")

    return ChatResponse(
        session_id=request.session_id,
        user_id=user_id,
        message=final_ans,
    )