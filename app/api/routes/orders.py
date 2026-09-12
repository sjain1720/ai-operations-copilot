from fastapi import APIRouter, Depends, Path

from app.api.dependencies import (
    get_delivery_service,
    get_order_service,
    get_payment_service,
)
from app.models.delivery import Delivery
from typing import Any, Dict

from app.models.order import Order
from app.models.payment import Payment
from app.schemas.delivery import DeliveryResponse
from app.schemas.order import OrderResponse, OrderSummaryResponse
from app.schemas.payment import PaymentResponse
from app.services.delivery import DeliveryService
from app.services.order import OrderService
from app.services.payment import PaymentService

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


@router.get("/{order_number}", response_model=OrderResponse)
def get_order(
    order_number: int = Path(..., gt=0),
    service: OrderService = Depends(get_order_service),
) -> Order:
    return service.get_order(order_number)


@router.get("/{order_number}/payment", response_model=PaymentResponse)
def get_payment(
    order_number: int = Path(..., gt=0),
    order_service: OrderService = Depends(get_order_service),
    payment_service: PaymentService = Depends(get_payment_service),
) -> Payment:
    order = order_service.get_order(order_number)
    return payment_service.get_payment_for_order(order.id)


@router.get("/{order_number}/delivery", response_model=DeliveryResponse)
def get_delivery(
    order_number: int = Path(..., gt=0),
    order_service: OrderService = Depends(get_order_service),
    delivery_service: DeliveryService = Depends(get_delivery_service),
) -> Delivery:
    order = order_service.get_order(order_number)
    return delivery_service.get_delivery_for_order(order.id)


@router.get("/{order_number}/summary", response_model=OrderSummaryResponse)
def get_order_summary(
    order_number: int = Path(..., gt=0),
    service: OrderService = Depends(get_order_service),
) -> Dict[str, Any]:
    return service.get_summary(order_number)
