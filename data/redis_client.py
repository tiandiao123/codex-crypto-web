"""Redis 客户端封装。"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import redis.asyncio as redis

LOGGER = logging.getLogger(__name__)

PRICE_HASH_KEY = "crypto:prices"
NEWS_LIST_KEY = "crypto:news"


@dataclass(slots=True)
class RedisConfig:
    """Redis 配置。"""

    url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")


class RedisClient:
    """负责 Redis 读写的异步客户端。"""

    def __init__(self, config: RedisConfig | None = None) -> None:
        self.config = config or RedisConfig()
        self.redis = redis.from_url(self.config.url, decode_responses=True)

    async def ping(self) -> bool:
        """检查 Redis 连通性。"""
        return bool(await self.redis.ping())

    async def close(self) -> None:
        """关闭 Redis 连接池。"""
        await self.redis.aclose()

    async def set_price(self, symbol: str, payload: dict[str, Any]) -> None:
        """写入实时价格到 Hash。"""
        await self.redis.hset(PRICE_HASH_KEY, symbol, json.dumps(payload, ensure_ascii=False))

    async def get_all_prices(self) -> dict[str, str]:
        """读取全部实时价格。"""
        return await self.redis.hgetall(PRICE_HASH_KEY)

    async def add_history(self, symbol: str, timestamp: int, price_json: str) -> None:
        """写入价格快照并清理 24 小时之前数据。"""
        history_key = f"crypto:history:{symbol}"
        cutoff = int((datetime.now(timezone.utc) - timedelta(hours=24)).timestamp())

        pipe = self.redis.pipeline(transaction=False)
        pipe.zadd(history_key, {price_json: timestamp})
        pipe.zremrangebyscore(history_key, 0, cutoff)
        await pipe.execute()

    async def get_recent_news_ids(self, limit: int = 50) -> set[str]:
        """获取现有新闻 ID 用于去重。"""
        records = await self.redis.lrange(NEWS_LIST_KEY, 0, limit - 1)
        ids: set[str] = set()

        for raw in records:
            try:
                item = json.loads(raw)
                item_id = item.get("id")
                if item_id:
                    ids.add(item_id)
            except json.JSONDecodeError:
                LOGGER.warning("发现无法解析的新闻记录: %s", raw)

        return ids

    async def push_news(self, news_items: list[dict[str, Any]], max_items: int = 50) -> int:
        """批量写入新闻并仅保留最新 N 条。"""
        if not news_items:
            return 0

        pipe = self.redis.pipeline(transaction=False)
        for item in news_items:
            pipe.lpush(NEWS_LIST_KEY, json.dumps(item, ensure_ascii=False))
        pipe.ltrim(NEWS_LIST_KEY, 0, max_items - 1)
        await pipe.execute()

        return len(news_items)
