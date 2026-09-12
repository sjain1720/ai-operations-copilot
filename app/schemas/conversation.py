from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.message import MessageResponse


class ConversationCreateRequest(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime


class ConversationPageResponse(BaseModel):
    items: List[ConversationResponse]
    next_cursor: Optional[str] = None
    has_more: bool


class MessagePageResponse(BaseModel):
    conversation_id: int
    items: List[MessageResponse]
    next_cursor: Optional[str] = None
    has_more: bool
