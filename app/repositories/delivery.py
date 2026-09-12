from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.delivery import Delivery


class DeliveryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_order_id(self, order_id: int) -> Optional[Delivery]:
        return self.session.scalar(
            select(Delivery).where(Delivery.order_id == order_id)
        )
