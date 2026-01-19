from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from datetime import datetime

Role = Literal["user", "assistant"]


class CreateSessionResponse(BaseModel):
    session_id: str = Field(..., description="The ID of the session")

class AddMessageRequest(BaseModel):
    session_id: str = Field(..., description="The ID of the session")
    role: Role = Field(..., description="The role of the message")
    content: str = Field(..., description="The content of the message")

class MessageOut(BaseModel):
    id: int = Field(..., description="The ID of the message")
    session_id: str = Field(..., description="The ID of the session")
    role: Role = Field(..., description="The role of the message")
    content: str = Field(..., description="The content of the message")
    created_at: datetime = Field(..., description="The timestamp of the message")

class HistoryResponse(BaseModel):
    session_id: str = Field(..., description="The ID of the session")
    messages: List[MessageOut] = Field(..., description="The messages in the session")


