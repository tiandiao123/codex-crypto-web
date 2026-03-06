"""REST API routes for crypto prices, history, news, and health."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Query
from redis.exceptions import RedisError

from app.models import HealthResponse, PriceHistoryResponse
from app.redis_client import redis_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/prices")
async def get_prices() -> dict[str, dict]:
    """Return all current symbol prices."""
    try:
        prices = await redis_client.get_all_prices()
    except RedisError as exc:
        logger.exception("Redis error on /api/prices")
        raise HTTPException(status_code=503, detail="Redis unavailable") from exc

    return {symbol: item.model_dump() for symbol, item in prices.items()}


@router.get("/prices/{symbol}")
async def get_price_by_symbol(symbol: str) -> dict:
    """Return one symbol current price."""
    try:
        price = await redis_client.get_price(symbol)
    except RedisError as exc:
        logger.exception("Redis error on /api/prices/{symbol}")
        raise HTTPException(status_code=503, detail="Redis unavailable") from exc

    if price is None:
        raise HTTPException(status_code=404, detail=f"Symbol not found: {symbol.upper()}")
    return price.model_dump()


@router.get("/prices/{symbol}/history", response_model=PriceHistoryResponse)
async def get_symbol_history(
    symbol: str, query_range: str = Query(default="24h", alias="range")
) -> PriceHistoryResponse:
    """Return history for a symbol in requested range (default 24h)."""
    try:
        history = await redis_client.get_price_history(symbol=symbol, query_range=query_range)
    except RedisError as exc:
        logger.exception("Redis error on /api/prices/{symbol}/history")
        raise HTTPException(status_code=503, detail="Redis unavailable") from exc

    return PriceHistoryResponse(symbol=symbol.upper(), range=query_range, history=history)


@router.get("/news")
async def get_news() -> list[dict]:
    """Return latest 20 news items."""
    try:
        news_list = await redis_client.get_news(limit=20)
    except RedisError as exc:
        logger.exception("Redis error on /api/news")
        raise HTTPException(status_code=503, detail="Redis unavailable") from exc

    return [item.model_dump() for item in news_list]


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health endpoint with redis ping."""
    try:
        is_ok = await redis_client.ping()
    except (RedisError, RuntimeError):
        logger.exception("Health check failed")
        return HealthResponse(status="degraded", redis="down")

    return HealthResponse(status="ok", redis="up" if is_ok else "down")
