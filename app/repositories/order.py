from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.order import Order


class OrderRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_order_number(self, order_number: int) -> Optional[Order]:
        return self.session.scalar(
            select(Order).where(Order.order_number == order_number)
        )

    def get_summary_by_order_number(self, order_number: int) -> Optional[Order]:
        statement = (
            select(Order)
            .options(
                joinedload(Order.customer),
                joinedload(Order.payment),
                joinedload(Order.delivery),
            )
            .where(Order.order_number == order_number)
        )
        return self.session.scalar(statement)
