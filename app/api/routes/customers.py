from fastapi import APIRouter, Depends, Path

from app.api.dependencies import get_customer_service
from app.models.customer import Customer
from app.schemas.customer import CustomerResponse
from app.services.customer import CustomerService

router = APIRouter(prefix="/api/v1/customers", tags=["customers"])


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int = Path(..., gt=0),
    service: CustomerService = Depends(get_customer_service),
) -> Customer:
    return service.get_customer(customer_id)
