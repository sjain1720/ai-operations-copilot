from fastapi import FastAPI, Request

from app.api.routes.copilot import router as copilot_router
from app.api.routes.customers import router as customers_router
from app.api.routes.health import router as health_router
from app.api.routes.orders import router as orders_router
from app.core.config import get_settings
from app.core.exceptions import (
	LLMConfigurationError,
	LLMProviderError,
	ResourceNotFoundError,
	ToolExecutionError,
)
from fastapi.responses import JSONResponse

settings = get_settings()
app = FastAPI(title=settings.app_name)
app.include_router(health_router)
app.include_router(customers_router)
app.include_router(orders_router)
app.include_router(copilot_router)


@app.exception_handler(ResourceNotFoundError)
def resource_not_found_handler(
	request: Request, exc: ResourceNotFoundError
) -> JSONResponse:
	return JSONResponse(
		status_code=404,
		content={
			"detail": {
				"code": "resource_not_found",
				"message": str(exc),
			}
		},
	)


@app.exception_handler(LLMConfigurationError)
def llm_configuration_handler(
	request: Request, exc: LLMConfigurationError
) -> JSONResponse:
	return JSONResponse(
		status_code=503,
		content={"detail": {"code": "llm_not_configured", "message": str(exc)}},
	)


@app.exception_handler(LLMProviderError)
def llm_provider_handler(
	request: Request, exc: LLMProviderError
) -> JSONResponse:
	return JSONResponse(
		status_code=502,
		content={"detail": {"code": "llm_provider_error", "message": str(exc)}},
	)


@app.exception_handler(ToolExecutionError)
def tool_execution_handler(
	request: Request, exc: ToolExecutionError
) -> JSONResponse:
	return JSONResponse(
		status_code=502,
		content={"detail": {"code": "tool_execution_error", "message": str(exc)}},
	)
