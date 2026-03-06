"""Socket.IO server setup and background broadcast workers."""

from __future__ import annotations

import asyncio
import logging
import os
from collections.abc import Iterable

import socketio

from app.redis_client import redis_client

logger = logging.getLogger(__name__)


def _load_socket_origins() -> list[str] | str:
    """Load Socket.IO allowed origins from env, fallback to defaults."""
    env_value = os.getenv("CORS_ORIGINS", "").strip()
    if env_value:
        if env_value == "*":
            return "*"
        return [origin.strip() for origin in env_value.split(",") if origin.strip()]

    return [
        "http://localhost:5173",
        "http://118.26.39.18:5173",
        "http://118.26.39.18:8080",
    ]

# Socket.IO server instance, mounted by app.main.
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=_load_socket_origins(),
    logger=True,
    engineio_logger=False,
)

_poll_task: asyncio.Task | None = None
_stop_event: asyncio.Event | None = None


@sio.event
async def connect(sid: str, environ: dict, auth: dict | None = None) -> None:
    """Handle client connection and send initial snapshots."""
    logger.info("Socket client connected: %s", sid)

    try:
        prices = await redis_client.get_all_prices()
        for price_data in prices.values():
            await sio.emit("price_update", price_data.model_dump(), to=sid)

        news_items = await redis_client.get_news(limit=20)
        # Send older first to preserve timeline rendering.
        for item in reversed(news_items):
            await sio.emit("news_update", item.model_dump(), to=sid)
    except Exception:
        logger.exception("Failed to send initial socket snapshots to %s", sid)


@sio.event
async def disconnect(sid: str) -> None:
    """Handle client disconnection."""
    logger.info("Socket client disconnected: %s", sid)


async def _emit_price_updates() -> None:
    """Poll Redis prices and emit updates only when values changed."""
    last_prices: dict[str, dict] = {}

    while _stop_event and not _stop_event.is_set():
        try:
            prices = await redis_client.get_all_prices()
            for symbol, price_data in prices.items():
                current = price_data.model_dump()
                previous = last_prices.get(symbol)
                if previous != current:
                    # Event name required by contract: price_update
                    await sio.emit("price_update", current)
                    last_prices[symbol] = current
        except Exception:
            logger.exception("Failed to publish price updates")

        await asyncio.sleep(2)


async def _emit_news_updates() -> None:
    """Poll Redis news and emit each newly seen news item."""
    seen_news_ids: set[str] = set()

    while _stop_event and not _stop_event.is_set():
        try:
            news_items = await redis_client.get_news(limit=20)
            new_items = [item for item in news_items if item.id not in seen_news_ids]

            # Keep emitted order stable: oldest first among new batch.
            for item in reversed(new_items):
                # Event name required by contract: news_update
                await sio.emit("news_update", item.model_dump())
                seen_news_ids.add(item.id)

            _trim_seen_news_ids(seen_news_ids, news_items)
        except Exception:
            logger.exception("Failed to publish news updates")

        await asyncio.sleep(3)


def _trim_seen_news_ids(seen_ids: set[str], news_items: Iterable) -> None:
    """Keep internal ID set bounded to latest list to prevent growth."""
    latest_ids = {item.id for item in news_items}
    stale_ids = seen_ids.difference(latest_ids)
    for stale_id in stale_ids:
        seen_ids.remove(stale_id)


async def _polling_worker() -> None:
    """Run price/news tasks concurrently under one lifecycle."""
    await asyncio.gather(_emit_price_updates(), _emit_news_updates())


async def start_socket_background_tasks() -> None:
    """Start Redis polling task once at app startup."""
    global _poll_task, _stop_event

    if _poll_task and not _poll_task.done():
        logger.info("Socket background task already running")
        return

    _stop_event = asyncio.Event()
    _poll_task = asyncio.create_task(_polling_worker(), name="redis-socket-poller")
    logger.info("Socket background tasks started")


async def stop_socket_background_tasks() -> None:
    """Stop Redis polling task at app shutdown."""
    global _poll_task

    if _stop_event:
        _stop_event.set()

    if _poll_task:
        _poll_task.cancel()
        try:
            await _poll_task
        except asyncio.CancelledError:
            logger.info("Socket background task cancelled")
        finally:
            _poll_task = None
