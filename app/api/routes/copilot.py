from typing import Dict, List

from fastapi import APIRouter, Depends

from app.ai.copilot import CopilotService
from app.api.dependencies import get_conversation_service, get_copilot_service
from app.models.message import MessageRole
from app.schemas.copilot import CopilotQueryRequest, CopilotQueryResponse
from app.services.conversation import ConversationService

router = APIRouter(prefix="/api/v1/copilot", tags=["copilot"])


@router.post("/query", response_model=CopilotQueryResponse)
def query_copilot(
    request: CopilotQueryRequest,
    conversation_service: ConversationService = Depends(get_conversation_service),
    copilot_service: CopilotService = Depends(get_copilot_service),
) -> CopilotQueryResponse:
    if request.conversation_id is None:
        conversation = conversation_service.create_conversation()
        history: List[Dict[str, str]] = []
    else:
        conversation = conversation_service.get_conversation(request.conversation_id)
        history_page = conversation_service.get_latest_messages(
            conversation.id, limit=20
        )
        history = [
            {"role": message.role.value, "content": message.content}
            for message in history_page.messages
        ]

    conversation_service.add_message(
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content=request.query,
    )
    conversation_service.commit()

    result = copilot_service.answer(request.query, history=history)

    conversation_service.add_message(
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT,
        content=result["answer"],
    )
    conversation_service.commit()

    result["conversation_id"] = conversation.id
    return CopilotQueryResponse.model_validate(result)
