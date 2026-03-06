"""Redis client helpers and data access methods."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.models import NewsData, PriceData

logger = logging.getLogger(__name__)


class RedisClient:
    """Encapsulates Redis operations used by API and Socket.IO."""

    def __init__(self) -> None:
        # Default redis connection can be overridden by REDIS_URL.
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis: Redis | None = None

    async def connect(self) -> None:
        """Create async Redis connection."""
        self.redis = Redis.from_url(self.redis_url, decode_responses=True)
        try:
            await self.redis.ping()
            logger.info("Connected to Redis: %s", self.redis_url)
        except RedisError:
            logger.exception("Failed to connect to Redis")
            raise

    async def close(self) -> None:
        """Close async Redis connection cleanly."""
        if self.redis is not None:
            await self.redis.close()
            logger.info("Redis connection closed")

    def _ensure_connected(self) -> Redis:
        """Guard against usage before startup initialization."""
        if self.redis is None:
            raise RuntimeError("Redis is not connected")
        return self.redis

    async def get_all_prices(self) -> dict[str, PriceData]:
        """Read all prices from Redis hash 'crypto:prices'."""
        redis_conn = self._ensure_connected()
        raw_map = await redis_conn.hgetall("crypto:prices")

        prices: dict[str, PriceData] = {}
        for symbol, raw_json in raw_map.items():
            try:
                payload = json.loads(raw_json)
                # payload 中已包含 symbol，直接使用
                prices[symbol] = PriceData(**payload)
            except (json.JSONDecodeError, TypeError, ValueError):
                logger.warning("Skipping invalid price payload for %s", symbol)
        return prices

    async def get_price(self, symbol: str) -> PriceData | None:
        """Read one symbol price from Redis hash 'crypto:prices'."""
        redis_conn = self._ensure_connected()
        raw_json = await redis_conn.hget("crypto:prices", symbol.upper())
        if raw_json is None:
            return None

        try:
            payload = json.loads(raw_json)
            # payload 中已包含 symbol，直接使用
            return PriceData(**payload)
        except (json.JSONDecodeError, TypeError, ValueError):
            logger.warning("Invalid price payload for %s", symbol)
            return None

    async def get_price_history(self, symbol: str, query_range: str) -> list[dict[str, Any]]:
        """Read history list for a symbol/range.

        This endpoint expects producer-side history lists like:
        - crypto:history:BTC:24h
        """
        redis_conn = self._ensure_connected()
        key = f"crypto:history:{symbol.upper()}:{query_range}"
        raw_items = await redis_conn.lrange(key, 0, -1)

        history: list[dict[str, Any]] = []
        for raw in raw_items:
            try:
                history.append(json.loads(raw))
            except json.JSONDecodeError:
                logger.warning("Skipping invalid history item in %s", key)
        return history

    async def get_news(self, limit: int = 20) -> list[NewsData]:
        """Read latest news from Redis list 'crypto:news'."""
        redis_conn = self._ensure_connected()
        raw_items = await redis_conn.lrange("crypto:news", 0, max(limit - 1, 0))

        news_list: list[NewsData] = []
        for raw in raw_items:
            try:
                news_list.append(NewsData(**json.loads(raw)))
            except (json.JSONDecodeError, TypeError, ValueError):
                logger.warning("Skipping invalid news item")
        return news_list

    async def ping(self) -> bool:
        """Check redis health status."""
        redis_conn = self._ensure_connected()
        return bool(await redis_conn.ping())


# Singleton client for app-wide dependency usage.
redis_client = RedisClient()
