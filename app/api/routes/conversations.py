from typing import Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from app.api.dependencies import get_conversation_service
from app.api.pagination import decode_cursor, encode_cursor
from app.core.exceptions import InvalidPaginationCursorError
from app.repositories.message import MessageCursor
from app.schemas.conversation import (
    ConversationCreateRequest,
    ConversationPageResponse,
    ConversationResponse,
    MessagePageResponse,
)
from app.schemas.message import MessageResponse
from app.services.conversation import ConversationService

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


def parse_cursor(cursor: Optional[str]) -> Optional[MessageCursor]:
    if cursor is None:
        return None
    try:
        return decode_cursor(cursor)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("", response_model=ConversationResponse, status_code=201)
def create_conversation(
    request: ConversationCreateRequest,
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationResponse:
    conversation = service.create_conversation(title=request.title)
    try:
        service.commit()
    except Exception:
        service.rollback()
        raise
    return ConversationResponse.model_validate(conversation)


@router.get("", response_model=ConversationPageResponse)
def list_conversations(
    limit: int = Query(default=20, ge=1, le=100),
    before: Optional[str] = Query(default=None),
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationPageResponse:
    cursor = parse_cursor(before)
    conversations, has_more = service.list_conversations(limit=limit, before=cursor)
    next_cursor = None
    if has_more and conversations:
        oldest = conversations[-1]
        next_cursor = encode_cursor(oldest.updated_at, oldest.id)
    return ConversationPageResponse(
        items=[ConversationResponse.model_validate(item) for item in conversations],
        next_cursor=next_cursor,
        has_more=has_more,
    )


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: int = Path(..., gt=0),
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationResponse:
    conversation = service.get_conversation(conversation_id)
    return ConversationResponse.model_validate(conversation)


@router.get("/{conversation_id}/messages", response_model=MessagePageResponse)
def get_conversation_messages(
    conversation_id: int = Path(..., gt=0),
    limit: int = Query(default=20, ge=1, le=100),
    before: Optional[str] = Query(default=None),
    service: ConversationService = Depends(get_conversation_service),
) -> MessagePageResponse:
    cursor = parse_cursor(before)
    if cursor is None:
        page = service.get_latest_messages(conversation_id, limit=limit)
    else:
        try:
            page = service.get_older_messages(
                conversation_id=conversation_id,
                before=cursor,
                limit=limit,
            )
        except InvalidPaginationCursorError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    next_cursor = None
    if page.has_more and page.next_cursor is not None:
        next_cursor = encode_cursor(*page.next_cursor)
    return MessagePageResponse(
        conversation_id=conversation_id,
        items=[MessageResponse.model_validate(item) for item in page.messages],
        next_cursor=next_cursor,
        has_more=page.has_more,
    )