from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.payment import Payment


class PaymentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_order_id(self, order_id: int) -> Optional[Payment]:
        return self.session.scalar(
            select(Payment).where(Payment.order_id == order_id)
        )
