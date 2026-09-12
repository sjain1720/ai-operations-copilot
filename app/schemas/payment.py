from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.payment import PaymentStatus


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    status: PaymentStatus
    amount: Decimal
    payment_method: Optional[str]
    transaction_reference: Optional[str]
    paid_at: Optional[datetime]
    failure_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
