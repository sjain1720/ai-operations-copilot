from typing import Any, Dict, List

from pydantic import BaseModel, Field


class CopilotQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)


class CopilotQueryResponse(BaseModel):
    answer: str
    tools_used: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
