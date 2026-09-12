from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.ai.client import GeminiClient
from app.ai.copilot import CopilotService
from app.ai.tools import BackendToolExecutor
from app.core.config import get_settings
from app.db.session import get_db
from app.repositories.customer import CustomerRepository
from app.repositories.conversation import ConversationRepository
from app.repositories.delivery import DeliveryRepository
from app.repositories.message import MessageRepository
from app.repositories.order import OrderRepository
from app.repositories.payment import PaymentRepository
from app.services.customer import CustomerService
from app.services.conversation import ConversationService
from app.services.delivery import DeliveryService
from app.services.order import OrderService
from app.services.payment import PaymentService


def get_customer_service(
    session: Session = Depends(get_db),
) -> CustomerService:
    return CustomerService(CustomerRepository(session))


def get_order_service(session: Session = Depends(get_db)) -> OrderService:
    return OrderService(OrderRepository(session))


def get_payment_service(session: Session = Depends(get_db)) -> PaymentService:
    return PaymentService(PaymentRepository(session))


def get_delivery_service(session: Session = Depends(get_db)) -> DeliveryService:
    return DeliveryService(DeliveryRepository(session))


def get_conversation_service(
    session: Session = Depends(get_db),
) -> ConversationService:
    return ConversationService(
        conversation_repository=ConversationRepository(session),
        message_repository=MessageRepository(session),
    )


def get_copilot_service(session: Session = Depends(get_db)) -> CopilotService:
    settings = get_settings()
    order_service = OrderService(OrderRepository(session))
    return CopilotService(
        llm_client=GeminiClient(settings),
        tool_executor=BackendToolExecutor(
            order_service=order_service,
            payment_service=PaymentService(PaymentRepository(session)),
            delivery_service=DeliveryService(DeliveryRepository(session)),
        ),
        max_tool_rounds=settings.llm_max_tool_rounds,
    )
