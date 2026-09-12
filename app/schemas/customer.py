from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    phone: Optional[str]
    created_at: datetime
    updated_at: datetime
