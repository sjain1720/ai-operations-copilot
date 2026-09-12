from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.order import OrderStatus
from app.schemas.customer import CustomerResponse
from app.schemas.delivery import DeliveryResponse
from app.schemas.payment import PaymentResponse


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: int
    customer_id: int
    status: OrderStatus
    total_amount: Decimal
    currency: str
    created_at: datetime
    updated_at: datetime


class OrderSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order: OrderResponse
    customer: CustomerResponse
    payment: Optional[PaymentResponse] = Field(default=None)
    delivery: Optional[DeliveryResponse] = Field(default=None)
