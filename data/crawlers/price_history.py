"""价格历史快照任务。"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from redis_client import RedisClient

LOGGER = logging.getLogger(__name__)


class PriceHistoryRecorder:
    """每分钟从实时价格 Hash 生成历史快照。"""

    def __init__(self, redis_client: RedisClient) -> None:
        self.redis_client = redis_client

    async def run_once(self) -> int:
        """执行一次快照保存。"""
        all_prices = await self.redis_client.get_all_prices()
        if not all_prices:
            LOGGER.info("暂无实时价格，跳过历史快照")
            return 0

        now_ts = int(datetime.now(timezone.utc).timestamp())
        saved_count = 0

        for symbol, raw in all_prices.items():
            try:
                payload = json.loads(raw)
                price = round(float(payload["price"]), 2)
            except (json.JSONDecodeError, KeyError, ValueError, TypeError):
                LOGGER.warning("跳过异常价格数据: %s=%s", symbol, raw)
                continue

            # 历史数据按约定保存 JSON 字符串。
            history_payload = {
                "symbol": symbol,
                "price": price,
                "timestamp": now_ts,
            }
            await self.redis_client.add_history(symbol, now_ts, json.dumps(history_payload, ensure_ascii=False))
            saved_count += 1

        LOGGER.info("历史快照保存完成，共 %s 条", saved_count)
        return saved_count
