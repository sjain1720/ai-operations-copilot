from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.delivery import DeliveryStatus


class DeliveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    status: DeliveryStatus
    scheduled_at: Optional[datetime]
    tracking_reference: Optional[str]
    delivered_at: Optional[datetime]
    failure_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
