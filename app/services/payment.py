from app.core.exceptions import ResourceNotFoundError
from app.models.payment import Payment
from app.repositories.payment import PaymentRepository


class PaymentService:
    def __init__(self, repository: PaymentRepository) -> None:
        self.repository = repository

    def get_payment_for_order(self, order_id: int) -> Payment:
        payment = self.repository.get_by_order_id(order_id)
        if payment is None:
            raise ResourceNotFoundError("Payment for order", order_id)
        return payment
