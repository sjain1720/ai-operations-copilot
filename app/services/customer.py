from app.core.exceptions import ResourceNotFoundError
from app.models.customer import Customer
from app.repositories.customer import CustomerRepository


class CustomerService:
    def __init__(self, repository: CustomerRepository) -> None:
        self.repository = repository

    def get_customer(self, customer_id: int) -> Customer:
        customer = self.repository.get_by_id(customer_id)
        if customer is None:
            raise ResourceNotFoundError("Customer", customer_id)
        return customer
