from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.message import MessageRole


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    role: MessageRole
    content: str
    created_at: datetime
