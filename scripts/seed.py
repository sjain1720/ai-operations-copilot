from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.customer import Customer
from app.models.conversation import Conversation
from app.models.delivery import Delivery, DeliveryStatus
from app.models.message import Message, MessageRole
from app.models.order import Order, OrderStatus
from app.models.payment import Payment, PaymentStatus


SEEDED_CONVERSATION_A_TITLE = "Seed Conversation A - Order 4521 Support"
SEEDED_CONVERSATION_B_TITLE = "Seed Conversation B - Order 1289 Delivery"
SEEDED_CONVERSATION_C_TITLE = "Seed Conversation C - Pagination Demo"
SEED_CONVERSATION_START = datetime(2026, 9, 12, 12, 0, tzinfo=timezone.utc)


SEED_ORDERS: Tuple[Dict[str, Any], ...] = (
    {
        "order_number": 4521,
        "customer": {
            "name": "Aarav Mehta",
            "email": "aarav.mehta@example.com",
            "phone": "+91-9876500001",
        },
        "order_status": OrderStatus.CONFIRMED,
        "amount": Decimal("185000.00"),
        "payment_status": PaymentStatus.SUCCESSFUL,
        "payment_method": "upi",
        "transaction_reference": "PAY-4521-SUCCESS",
        "paid_at": datetime(2026, 9, 2, 10, 30, tzinfo=timezone.utc),
        "delivery_status": DeliveryStatus.SCHEDULED,
        "scheduled_at": datetime(2026, 9, 15, 9, 0, tzinfo=timezone.utc),
        "tracking_reference": "DEL-4521-SCHEDULED",
    },
    {
        "order_number": 1289,
        "customer": {
            "name": "Priya Sharma",
            "email": "priya.sharma@example.com",
            "phone": "+91-9876500002",
        },
        "order_status": OrderStatus.CONFIRMED,
        "amount": Decimal("92000.00"),
        "payment_status": PaymentStatus.SUCCESSFUL,
        "payment_method": "card",
        "transaction_reference": "PAY-1289-SUCCESS",
        "paid_at": datetime(2026, 9, 3, 12, 15, tzinfo=timezone.utc),
        "delivery_status": DeliveryStatus.NOT_SCHEDULED,
        "scheduled_at": None,
        "tracking_reference": None,
    },
    {
        "order_number": 3340,
        "customer": {
            "name": "Rohan Desai",
            "email": "rohan.desai@example.com",
            "phone": "+91-9876500003",
        },
        "order_status": OrderStatus.CREATED,
        "amount": Decimal("76000.00"),
        "payment_status": PaymentStatus.PENDING,
        "payment_method": "net_banking",
        "transaction_reference": None,
        "paid_at": None,
        "delivery_status": DeliveryStatus.NOT_SCHEDULED,
        "scheduled_at": None,
        "tracking_reference": None,
    },
    {
        "order_number": 5678,
        "customer": {
            "name": "Neha Kapoor",
            "email": "neha.kapoor@example.com",
            "phone": "+91-9876500004",
        },
        "order_status": OrderStatus.CREATED,
        "amount": Decimal("134500.00"),
        "payment_status": PaymentStatus.FAILED,
        "payment_method": "card",
        "transaction_reference": None,
        "paid_at": None,
        "payment_failure_reason": "Bank declined the transaction",
        "delivery_status": DeliveryStatus.NOT_SCHEDULED,
        "scheduled_at": None,
        "tracking_reference": None,
    },
    {
        "order_number": 2231,
        "customer": {
            "name": "Vikram Singh",
            "email": "vikram.singh@example.com",
            "phone": "+91-9876500005",
        },
        "order_status": OrderStatus.CONFIRMED,
        "amount": Decimal("210000.00"),
        "payment_status": PaymentStatus.SUCCESSFUL,
        "payment_method": "bank_transfer",
        "transaction_reference": "PAY-2231-SUCCESS",
        "paid_at": datetime(2026, 8, 28, 8, 45, tzinfo=timezone.utc),
        "delivery_status": DeliveryStatus.IN_TRANSIT,
        "scheduled_at": datetime(2026, 9, 10, 9, 0, tzinfo=timezone.utc),
        "tracking_reference": "DEL-2231-IN-TRANSIT",
    },
    {
        "order_number": 7812,
        "customer": {
            "name": "Ishita Rao",
            "email": "ishita.rao@example.com",
            "phone": "+91-9876500006",
        },
        "order_status": OrderStatus.COMPLETED,
        "amount": Decimal("158000.00"),
        "payment_status": PaymentStatus.SUCCESSFUL,
        "payment_method": "upi",
        "transaction_reference": "PAY-7812-SUCCESS",
        "paid_at": datetime(2026, 8, 20, 14, 0, tzinfo=timezone.utc),
        "delivery_status": DeliveryStatus.DELIVERED,
        "scheduled_at": datetime(2026, 8, 25, 10, 0, tzinfo=timezone.utc),
        "tracking_reference": "DEL-7812-DELIVERED",
        "delivered_at": datetime(2026, 8, 25, 16, 30, tzinfo=timezone.utc),
    },
    {
        "order_number": 9044,
        "customer": {
            "name": "Kabir Malhotra",
            "email": "kabir.malhotra@example.com",
            "phone": "+91-9876500007",
        },
        "order_status": OrderStatus.CANCELLED,
        "amount": Decimal("68000.00"),
        "payment_status": PaymentStatus.REFUNDED,
        "payment_method": "card",
        "transaction_reference": "PAY-9044-REFUNDED",
        "paid_at": datetime(2026, 8, 12, 11, 20, tzinfo=timezone.utc),
        "delivery_status": DeliveryStatus.CANCELLED,
        "scheduled_at": None,
        "tracking_reference": None,
        "payment_failure_reason": "Order cancelled by customer",
        "delivery_failure_reason": "Order cancelled by customer",
    },
    {
        "order_number": 6150,
        "customer": {
            "name": "Ananya Iyer",
            "email": "ananya.iyer@example.com",
            "phone": "+91-9876500008",
        },
        "order_status": OrderStatus.CONFIRMED,
        "amount": Decimal("112000.00"),
        "payment_status": PaymentStatus.SUCCESSFUL,
        "payment_method": "upi",
        "transaction_reference": "PAY-6150-SUCCESS",
        "paid_at": datetime(2026, 9, 1, 9, 10, tzinfo=timezone.utc),
        "delivery_status": DeliveryStatus.FAILED,
        "scheduled_at": datetime(2026, 9, 8, 9, 0, tzinfo=timezone.utc),
        "tracking_reference": "DEL-6150-FAILED",
        "delivery_failure_reason": "Address verification failed",
    },
)


CONVERSATION_A_MESSAGES: Tuple[Tuple[MessageRole, str], ...] = (
    (MessageRole.USER, "What's the payment status for order 4521?"),
    (MessageRole.ASSISTANT, "Payment for order 4521 was successful."),
    (MessageRole.USER, "When was it paid?"),
    (
        MessageRole.ASSISTANT,
        "Payment was completed on 2026-09-02 at 10:30 UTC.",
    ),
    (MessageRole.USER, "Is delivery scheduled?"),
    (
        MessageRole.ASSISTANT,
        "Yes. Delivery is scheduled for 2026-09-15 at 09:00 UTC.",
    ),
)


CONVERSATION_B_MESSAGES: Tuple[Tuple[MessageRole, str], ...] = (
    (MessageRole.USER, "Has the payment for order 1289 been received?"),
    (MessageRole.ASSISTANT, "Payment for order 1289 was successful."),
    (MessageRole.USER, "Why is delivery not scheduled?"),
    (
        MessageRole.ASSISTANT,
        "Delivery for order 1289 is not scheduled yet, despite the successful payment.",
    ),
)


CONVERSATION_C_EXCHANGES: Tuple[Tuple[str, str], ...] = (
    (
        "Give me the current status of order 4521.",
        "Order 4521 is confirmed, paid successfully, and delivery is scheduled.",
    ),
    (
        "What payment method was used for that order?",
        "The payment method for order 4521 was UPI.",
    ),
    (
        "What is the delivery date for order 4521?",
        "Delivery for order 4521 is scheduled for 2026-09-15 at 09:00 UTC.",
    ),
    (
        "Now check order 1289.",
        "Order 1289 has a successful card payment and no scheduled delivery.",
    ),
    (
        "When was order 1289 paid?",
        "Order 1289 was paid on 2026-09-03 at 12:15 UTC.",
    ),
    (
        "What operational gap should the team investigate?",
        "The payment succeeded, but delivery for order 1289 is still not scheduled.",
    ),
    (
        "Can you check the pending payment case?",
        "Order 3340 has a pending payment and delivery is not scheduled.",
    ),
    (
        "Does it have a transaction reference?",
        "No transaction reference or paid timestamp is recorded for order 3340.",
    ),
    (
        "What happened with order 5678?",
        "Payment for order 5678 failed because the bank declined the transaction.",
    ),
    (
        "Should delivery proceed for that order?",
        "Delivery for order 5678 is not scheduled while payment remains failed.",
    ),
    (
        "Give me the delivery status for order 2231.",
        "Order 2231 is in transit with tracking reference DEL-2231-IN-TRANSIT.",
    ),
    (
        "Was order 2231 paid successfully?",
        "Yes. Order 2231 has a successful bank-transfer payment.",
    ),
    (
        "Which order has already been delivered?",
        "Order 7812 has been delivered.",
    ),
    (
        "When was that delivery completed?",
        "Order 7812 was delivered on 2026-08-25 at 16:30 UTC.",
    ),
    (
        "What is the status of cancelled order 9044?",
        "Order 9044 is cancelled, its payment is refunded, and its delivery is cancelled.",
    ),
    (
        "Is there a delivery issue for order 6150?",
        "Delivery for order 6150 failed because address verification failed.",
    ),
    (
        "Was payment successful for order 6150?",
        "Yes. Payment for order 6150 was successful.",
    ),
    (
        "Summarize the operational cases reviewed so far.",
        "The examples include scheduled, unscheduled, pending, failed, in-transit, delivered, cancelled, and failed-delivery cases.",
    ),
    (
        "Which case shows payment succeeded but delivery was not scheduled?",
        "Order 1289 shows a successful payment with delivery not scheduled.",
    ),
    (
        "Which case is currently in transit?",
        "Order 2231 is currently in transit.",
    ),
    (
        "Which case has a refunded payment?",
        "Order 9044 has a refunded payment because the order was cancelled.",
    ),
    (
        "Which case needs address follow-up?",
        "Order 6150 needs address follow-up because delivery failed address verification.",
    ),
    (
        "Are all reviewed orders in the same lifecycle state?",
        "No. The reviewed orders span created, confirmed, cancelled, and completed states.",
    ),
)


def build_pagination_messages() -> Tuple[Tuple[MessageRole, str], ...]:
    messages: List[Tuple[MessageRole, str]] = []
    for user_message, assistant_message in CONVERSATION_C_EXCHANGES:
        messages.extend(
            (
                (MessageRole.USER, user_message),
                (MessageRole.ASSISTANT, assistant_message),
            )
        )
    return tuple(messages)


def get_or_create_customer(session: Session, data: Dict[str, str]) -> Customer:
    customer = session.scalar(
        select(Customer).where(Customer.email == data["email"])
    )
    if customer is None:
        customer = Customer(email=data["email"])
        session.add(customer)

    customer.name = data["name"]
    customer.phone = data["phone"]
    return customer


def get_or_create_order(
    session: Session, order_number: int, customer: Customer
) -> Order:
    order = session.scalar(
        select(Order).where(Order.order_number == order_number)
    )
    if order is None:
        order = Order(order_number=order_number)
        session.add(order)

    order.customer = customer
    return order


def get_or_create_payment(session: Session, order: Order) -> Payment:
    session.flush()
    payment = session.scalar(select(Payment).where(Payment.order_id == order.id))
    if payment is None:
        payment = Payment(order=order)
        session.add(payment)
    return payment


def get_or_create_delivery(session: Session, order: Order) -> Delivery:
    session.flush()
    delivery = session.scalar(select(Delivery).where(Delivery.order_id == order.id))
    if delivery is None:
        delivery = Delivery(order=order)
        session.add(delivery)
    return delivery


def seed_database(session: Session) -> None:
    for data in SEED_ORDERS:
        customer = get_or_create_customer(session, data["customer"])
        order = get_or_create_order(session, data["order_number"], customer)
        order.status = data["order_status"]
        order.total_amount = data["amount"]
        order.currency = "INR"

        payment = get_or_create_payment(session, order)
        payment.status = data["payment_status"]
        payment.amount = data["amount"]
        payment.payment_method = data["payment_method"]
        payment.transaction_reference = data.get("transaction_reference")
        payment.paid_at = data.get("paid_at")
        payment.failure_reason = data.get("payment_failure_reason")

        delivery = get_or_create_delivery(session, order)
        delivery.status = data["delivery_status"]
        delivery.scheduled_at = data.get("scheduled_at")
        delivery.tracking_reference = data.get("tracking_reference")
        delivery.delivered_at = data.get("delivered_at")
        delivery.failure_reason = data.get("delivery_failure_reason")

    seed_conversations(session)

    session.commit()


def seed_conversations(session: Session) -> None:
    seed_conversation(
        session,
        title=SEEDED_CONVERSATION_A_TITLE,
        messages=CONVERSATION_A_MESSAGES,
        start_time=SEED_CONVERSATION_START,
    )
    seed_conversation(
        session,
        title=SEEDED_CONVERSATION_B_TITLE,
        messages=CONVERSATION_B_MESSAGES,
        start_time=SEED_CONVERSATION_START + timedelta(hours=1),
    )
    seed_conversation(
        session,
        title=SEEDED_CONVERSATION_C_TITLE,
        messages=build_pagination_messages(),
        start_time=SEED_CONVERSATION_START + timedelta(hours=2),
    )


def seed_conversation(
    session: Session,
    title: str,
    messages: Tuple[Tuple[MessageRole, str], ...],
    start_time: datetime,
) -> Conversation:
    conversation = session.scalar(
        select(Conversation).where(Conversation.title == title)
    )
    if conversation is None:
        conversation = Conversation(title=title)
        session.add(conversation)
        session.flush()
    else:
        session.query(Message).filter(
            Message.conversation_id == conversation.id
        ).delete(synchronize_session=False)

    conversation.created_at = start_time
    conversation.updated_at = start_time + timedelta(minutes=len(messages) - 1)

    for offset, (role, content) in enumerate(messages):
        session.add(
            Message(
                conversation_id=conversation.id,
                role=role,
                content=content,
                created_at=start_time + timedelta(minutes=offset),
            )
        )
    return conversation


def main() -> None:
    with SessionLocal() as session:
        seed_database(session)
    print(f"Seeded {len(SEED_ORDERS)} deterministic operational scenarios.")


if __name__ == "__main__":
    main()
