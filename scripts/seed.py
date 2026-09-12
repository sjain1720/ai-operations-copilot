from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.customer import Customer
from app.models.delivery import Delivery, DeliveryStatus
from app.models.order import Order, OrderStatus
from app.models.payment import Payment, PaymentStatus


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

    session.commit()


def main() -> None:
    with SessionLocal() as session:
        seed_database(session)
    print(f"Seeded {len(SEED_ORDERS)} deterministic operational scenarios.")


if __name__ == "__main__":
    main()
