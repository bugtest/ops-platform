"""聊天API"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import AsyncGenerator

from nanobot.core.agent import get_agent_manager

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    session_id: str = "web:default"


class ChatResponse(BaseModel):
    response: str
    session_id: str


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """发送消息，返回完整响应"""
    agent = get_agent_manager()
    response = await agent.chat(request.message, request.session_id)
    return ChatResponse(response=response, session_id=request.session_id)


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """流式对话"""
    agent = get_agent_manager()
    
    async def generate() -> AsyncGenerator[str, None]:
        async for chunk in agent.chat_stream(request.message, request.session_id):
            yield f"data: {chunk}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
