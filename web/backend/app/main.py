"""FastAPI entrypoint for web proxy backend."""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .deps import close_proxy_client
from .routers import health, sales, stores


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        version="0.1.0",
    )

    if settings.allowed_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(health.router)
    app.include_router(stores.router)
    app.include_router(sales.router)

    @app.on_event("startup")
    async def startup_event() -> None:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        await close_proxy_client()

    return app


app = create_app()

