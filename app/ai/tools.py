import json
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.core.exceptions import ResourceNotFoundError, ToolExecutionError
from app.schemas.delivery import DeliveryResponse
from app.schemas.order import OrderResponse, OrderSummaryResponse
from app.schemas.payment import PaymentResponse
from app.services.delivery import DeliveryService
from app.services.order import OrderService
from app.services.payment import PaymentService


class OrderToolArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_number: int = Field(..., gt=0, description="The public order number")


TOOL_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_order",
            "description": "Get basic order details using the public order number.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_number": {
                        "type": "integer",
                        "description": "The public order number, for example 4521",
                    }
                },
                "required": ["order_number"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_payment_status",
            "description": "Get payment status and details for an order.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_number": {
                        "type": "integer",
                        "description": "The public order number, for example 4521",
                    }
                },
                "required": ["order_number"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_delivery_status",
            "description": "Get delivery status and details for an order.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_number": {
                        "type": "integer",
                        "description": "The public order number, for example 4521",
                    }
                },
                "required": ["order_number"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_order_summary",
            "description": "Get the complete order, customer, payment, and delivery summary.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_number": {
                        "type": "integer",
                        "description": "The public order number, for example 4521",
                    }
                },
                "required": ["order_number"],
                "additionalProperties": False,
            },
        },
    },
]


class BackendToolExecutor:
    def __init__(
        self,
        order_service: OrderService,
        payment_service: PaymentService,
        delivery_service: DeliveryService,
    ) -> None:
        self.order_service = order_service
        self.payment_service = payment_service
        self.delivery_service = delivery_service
        self._handlers = {
            "get_order": self._get_order,
            "get_payment_status": self._get_payment_status,
            "get_delivery_status": self._get_delivery_status,
            "get_order_summary": self._get_order_summary,
        }

    def execute(self, name: str, raw_arguments: str) -> Dict[str, Any]:
        handler = self._handlers.get(name)
        if handler is None:
            raise ToolExecutionError("The requested backend tool is not available")

        try:
            arguments = OrderToolArguments.model_validate(json.loads(raw_arguments))
        except (json.JSONDecodeError, ValidationError, TypeError) as exc:
            raise ToolExecutionError("The backend tool arguments were invalid") from exc

        try:
            return handler(arguments.order_number)
        except ResourceNotFoundError as exc:
            return {
                "error": {
                    "code": "order_not_found",
                    "message": str(exc),
                }
            }
        except Exception as exc:
            raise ToolExecutionError("The backend tool failed") from exc

    def _get_order(self, order_number: int) -> Dict[str, Any]:
        order = self.order_service.get_order(order_number)
        return OrderResponse.model_validate(order).model_dump(mode="json")

    def _get_payment_status(self, order_number: int) -> Dict[str, Any]:
        order = self.order_service.get_order(order_number)
        payment = self.payment_service.get_payment_for_order(order.id)
        return PaymentResponse.model_validate(payment).model_dump(mode="json")

    def _get_delivery_status(self, order_number: int) -> Dict[str, Any]:
        order = self.order_service.get_order(order_number)
        delivery = self.delivery_service.get_delivery_for_order(order.id)
        return DeliveryResponse.model_validate(delivery).model_dump(mode="json")

    def _get_order_summary(self, order_number: int) -> Dict[str, Any]:
        summary = self.order_service.get_summary(order_number)
        return OrderSummaryResponse.model_validate(summary).model_dump(mode="json")
