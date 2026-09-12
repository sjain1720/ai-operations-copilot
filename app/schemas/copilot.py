from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CopilotQueryRequest(BaseModel):
    conversation_id: Optional[int] = Field(default=None, gt=0)
    query: str = Field(..., min_length=1, max_length=4000)


class CopilotQueryResponse(BaseModel):
    conversation_id: int
    answer: str
    tools_used: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
