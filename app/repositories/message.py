from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import InvalidPaginationCursorError
from app.models.message import Message, MessageRole


MessageCursor = Tuple[datetime, int]


@dataclass(frozen=True)
class MessagePage:
    messages: List[Message]
    has_more: bool
    next_cursor: Optional[MessageCursor]


class MessageRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        conversation_id: int,
        role: MessageRole,
        content: str,
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )
        self.session.add(message)
        self.session.flush()
        return message

    def get_latest(
        self,
        conversation_id: int,
        limit: int = 20,
    ) -> MessagePage:
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc(), Message.id.desc())
            .limit(limit + 1)
        )
        messages = list(self.session.scalars(statement))
        has_more = len(messages) > limit
        messages = messages[:limit]
        messages.reverse()

        next_cursor = None
        if has_more and messages:
            first_message = messages[0]
            next_cursor = (first_message.created_at, first_message.id)

        return MessagePage(
            messages=messages,
            has_more=has_more,
            next_cursor=next_cursor,
        )

    def get_older(
        self,
        conversation_id: int,
        before: MessageCursor,
        limit: int = 20,
    ) -> MessagePage:
        before_created_at, before_id = before
        cursor_message = self.session.scalar(
            select(Message.id).where(
                Message.id == before_id,
                Message.conversation_id == conversation_id,
                Message.created_at == before_created_at,
            )
        )
        if cursor_message is None:
            raise InvalidPaginationCursorError(
                "The pagination cursor does not belong to this conversation"
            )

        statement = (
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
                (
                    (Message.created_at < before_created_at)
                    | (
                        (Message.created_at == before_created_at)
                        & (Message.id < before_id)
                    )
                ),
            )
            .order_by(Message.created_at.desc(), Message.id.desc())
            .limit(limit + 1)
        )
        messages = list(self.session.scalars(statement))
        has_more = len(messages) > limit
        messages = messages[:limit]
        messages.reverse()

        next_cursor = None
        if has_more and messages:
            first_message = messages[0]
            next_cursor = (first_message.created_at, first_message.id)

        return MessagePage(
            messages=messages,
            has_more=has_more,
            next_cursor=next_cursor,
        )
