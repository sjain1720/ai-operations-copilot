from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.customer import Customer


class CustomerRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        return self.session.scalar(
            select(Customer).where(Customer.id == customer_id)
        )
