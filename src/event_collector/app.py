from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from event_collector.api.router import api_router
from event_collector.api.routes.health import router as health_router
from event_collector.config import Settings, get_settings
from event_collector.observability import configure_logging, configure_observability


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
        configure_logging(settings)
        observability_providers = configure_observability(settings)
        try:
            yield
        finally:
            observability_providers.shutdown()

    app = FastAPI(
        title=settings.name,
        version=settings.version,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
        lifespan=lifespan,
    )

    app.include_router(health_router)
    app.include_router(api_router, prefix=settings.api_prefix)

    return app


app = create_app()
