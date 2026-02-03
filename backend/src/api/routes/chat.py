"""Chat API routes for AI-powered task management"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from ...auth import get_current_user
from ...models.todo_models import User
from ...agents.task_agent import TaskManagementAgent

router = APIRouter()

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    user_id: int

class ChatResponse(BaseModel):
    response: str
    action_performed: Optional[str] = None
    task_result: Optional[dict] = None

@router.post("/chat", tags=["chat"])
async def chat_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Process natural language requests and perform task operations
    """
    try:
        # Ensure the user_id matches the authenticated user
        if current_user.id != request.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: user ID mismatch"
            )

        # Initialize the AI agent only when needed (lazy initialization)
        # This avoids import-time errors with dummy API keys
        agent = TaskManagementAgent()

        # Process the request with the AI agent
        # Convert Pydantic models to dictionaries as the agent expects dicts
        messages_data = [msg.model_dump() for msg in request.messages]
        result = await agent.chat(messages_data, current_user.id)

        return ChatResponse(
            response=result["response"],
            action_performed=result.get("action_performed"),
            task_result=result.get("task_result")
        )


    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except Exception as e:
        import traceback
        print("DEBUG: Exception caught in chat_endpoint:")
        traceback.print_exc()
        print(f"DEBUG: Exception type: {type(e)}, message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )