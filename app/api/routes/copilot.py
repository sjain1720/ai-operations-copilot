from fastapi import APIRouter, Depends

from app.ai.copilot import CopilotService
from app.api.dependencies import get_copilot_service
from app.schemas.copilot import CopilotQueryRequest, CopilotQueryResponse

router = APIRouter(prefix="/api/v1/copilot", tags=["copilot"])


@router.post("/query", response_model=CopilotQueryResponse)
def query_copilot(
    request: CopilotQueryRequest,
    service: CopilotService = Depends(get_copilot_service),
) -> CopilotQueryResponse:
    return CopilotQueryResponse.model_validate(service.answer(request.query))
