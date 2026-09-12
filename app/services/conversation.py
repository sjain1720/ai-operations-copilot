from datetime import datetime, timezone
from typing import List, Optional, Tuple

from app.core.exceptions import ResourceNotFoundError
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.repositories.conversation import ConversationCursor, ConversationRepository
from app.repositories.message import MessageCursor, MessagePage, MessageRepository


class ConversationService:
    def __init__(
        self,
        conversation_repository: ConversationRepository,
        message_repository: MessageRepository,
    ) -> None:
        self.conversation_repository = conversation_repository
        self.message_repository = message_repository

    def create_conversation(self, title: Optional[str] = None) -> Conversation:
        return self.conversation_repository.create(title=title)

    def get_conversation(self, conversation_id: int) -> Conversation:
        conversation = self.conversation_repository.get_by_id(conversation_id)
        if conversation is None:
            raise ResourceNotFoundError("Conversation", conversation_id)
        return conversation

    def list_conversations(
        self,
        limit: int = 20,
        before: Optional[ConversationCursor] = None,
    ) -> Tuple[List[Conversation], bool]:
        return self.conversation_repository.list_recent(limit=limit, before=before)

    def add_message(
        self,
        conversation_id: int,
        role: MessageRole,
        content: str,
    ) -> Message:
        self.get_conversation(conversation_id)
        message = self.message_repository.create(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )
        self.conversation_repository.touch_updated_at(
            conversation_id=conversation_id,
            updated_at=datetime.now(timezone.utc),
        )
        return message

    def get_latest_messages(
        self,
        conversation_id: int,
        limit: int = 20,
    ) -> MessagePage:
        self.get_conversation(conversation_id)
        return self.message_repository.get_latest(
            conversation_id=conversation_id,
            limit=limit,
        )

    def get_older_messages(
        self,
        conversation_id: int,
        before: MessageCursor,
        limit: int = 20,
    ) -> MessagePage:
        self.get_conversation(conversation_id)
        return self.message_repository.get_older(
            conversation_id=conversation_id,
            before=before,
            limit=limit,
        )

    def commit(self) -> None:
        self.conversation_repository.commit()

    def rollback(self) -> None:
        self.conversation_repository.rollback()
