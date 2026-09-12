from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.conversation import Conversation


ConversationCursor = Tuple[datetime, int]


class ConversationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, title: Optional[str] = None) -> Conversation:
        conversation = Conversation(title=title)
        self.session.add(conversation)
        self.session.flush()
        return conversation

    def get_by_id(self, conversation_id: int) -> Optional[Conversation]:
        return self.session.scalar(
            select(Conversation).where(Conversation.id == conversation_id)
        )

    def list_recent(
        self,
        limit: int = 20,
        before: Optional[ConversationCursor] = None,
    ) -> Tuple[List[Conversation], bool]:
        statement = select(Conversation).order_by(
            Conversation.updated_at.desc(), Conversation.id.desc()
        )
        if before is not None:
            before_updated_at, before_id = before
            statement = statement.where(
                (Conversation.updated_at < before_updated_at)
                | (
                    (Conversation.updated_at == before_updated_at)
                    & (Conversation.id < before_id)
                )
            )

        conversations = list(self.session.scalars(statement.limit(limit + 1)))
        has_more = len(conversations) > limit
        return conversations[:limit], has_more

    def touch_updated_at(self, conversation_id: int, updated_at: datetime) -> None:
        self.session.execute(
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(updated_at=updated_at)
        )

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
