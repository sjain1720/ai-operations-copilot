from app.api.routes.copilot import router as copilot_router
from app.api.routes.customers import router as customers_router
from app.api.routes.health import router as health_router
from app.api.routes.orders import router as orders_router

__all__ = ["copilot_router", "customers_router", "health_router", "orders_router"]
