from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import sys
import os
import uuid

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.studio.chatbot import graph
from langchain_core.messages import HumanMessage

app = FastAPI(title="SQL Chatbot API", version="1.0.0")

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None
    user_id: Optional[str] = None
    recursion_limit: Optional[int] = 15

class ChatResponse(BaseModel):
    response: str
    thread_id: str
    user_id: str
    summary: Optional[str] = None
    messages_count: int


# Simple dictionary for active threads (in production, use a database)
active_threads: Dict[str, Dict[str, Any]] = {}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "SQL Chatbot API is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the SQL chatbot
    """
    try:
        # Generate thread_id if not provided
        user_id = request.user_id or str(uuid.uuid4())
        thread_id = request.thread_id or str(uuid.uuid4())
        
        #easy handling - to avoid multi-user sessions for now
        combined_id = user_id + "_" + thread_id

        # Create config with thread_id for memory management
        config = {
            "configurable": {"thread_id": combined_id},
        }
        
        # Create input message
        input_message = HumanMessage(content=request.message)
        initial_state = {"messages": [input_message]}
        
        # Invoke the graph
        result = graph.invoke(
            initial_state, 
            config, 
            recursion_limit=request.recursion_limit
        )
        
        # Extract the last assistant message as response
        messages = result.get("messages", [])
        assistant_messages = [msg for msg in messages if hasattr(msg, 'content') and msg.type == 'ai']
        
        if assistant_messages:
            response_content = assistant_messages[-1].content
        else:
            response_content = "I apologize, but I couldn't generate a response."
        
        # "last_interaction": request.message, is optional as graph has memory
        active_threads[combined_id] = {
            "last_interaction": request.message,
            "message_count": len(messages)
        }
        
        return ChatResponse(
            response=response_content,
            user_id=user_id,
            thread_id=thread_id,
            summary=result.get("summary"),
            messages_count=len(messages)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)