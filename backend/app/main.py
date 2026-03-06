"""Application entrypoint: FastAPI + Socket.IO + Redis integration."""

from __future__ import annotations

import logging
import os

import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router as api_router
from app.redis_client import redis_client
from app.socket_server import sio, start_socket_background_tasks, stop_socket_background_tasks

# Basic logging config for app-wide logs.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# FastAPI app provides REST endpoints.
fastapi_app = FastAPI(title="CryptoWeb Backend", version="1.0.0")

def _load_allowed_origins() -> list[str]:
    """Load CORS origins from env, fallback to sane defaults."""
    env_value = os.getenv("CORS_ORIGINS", "").strip()
    if env_value:
        return [origin.strip() for origin in env_value.split(",") if origin.strip()]

    return [
        "http://localhost:5173",
        "http://localhost:4173",
        "http://118.26.39.18:5173",
        "http://118.26.39.18:8080",
        "http://118.26.39.18",
    ]


ALLOWED_ORIGINS = _load_allowed_origins()

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fastapi_app.include_router(api_router)


@fastapi_app.on_event("startup")
async def on_startup() -> None:
    """Connect Redis and start Socket.IO polling workers."""
    logger.info("Starting application")
    await redis_client.connect()
    await start_socket_background_tasks()


@fastapi_app.on_event("shutdown")
async def on_shutdown() -> None:
    """Stop workers and close Redis connections."""
    logger.info("Shutting down application")
    await stop_socket_background_tasks()
    await redis_client.close()


# Wrap FastAPI with Socket.IO ASGI app to expose /socket.io/ endpoint.
app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app, socketio_path="socket.io")
