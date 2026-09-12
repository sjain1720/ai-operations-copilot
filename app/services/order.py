from typing import Dict, Union

from app.core.exceptions import ResourceNotFoundError
from app.models.order import Order
from app.repositories.order import OrderRepository


class OrderService:
    def __init__(self, repository: OrderRepository) -> None:
        self.repository = repository

    def get_order(self, order_number: int) -> Order:
        order = self.repository.get_by_order_number(order_number)
        if order is None:
            raise ResourceNotFoundError("Order", order_number)
        return order

    def get_summary(self, order_number: int) -> Dict[str, Union[Order, object]]:
        order = self.repository.get_summary_by_order_number(order_number)
        if order is None:
            raise ResourceNotFoundError("Order", order_number)
        return {
            "order": order,
            "customer": order.customer,
            "payment": order.payment,
            "delivery": order.delivery,
        }
