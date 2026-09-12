from app.core.exceptions import ResourceNotFoundError
from app.models.delivery import Delivery
from app.repositories.delivery import DeliveryRepository


class DeliveryService:
    def __init__(self, repository: DeliveryRepository) -> None:
        self.repository = repository

    def get_delivery_for_order(self, order_id: int) -> Delivery:
        delivery = self.repository.get_by_order_id(order_id)
        if delivery is None:
            raise ResourceNotFoundError("Delivery for order", order_id)
        return delivery
