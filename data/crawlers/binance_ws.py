"""Binance 实时价格爬虫。"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import aiohttp
import websockets
from websockets.exceptions import ConnectionClosedError, WebSocketException

from redis_client import RedisClient

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class BinanceConfig:
    """Binance 连接配置。"""

    ws_url: str = os.getenv(
        "BINANCE_WS_URL",
        "wss://stream.binance.com:9443/ws/btcusdt@trade/ethusdt@trade/solusdt@trade",
    )
    rest_base_url: str = os.getenv("BINANCE_REST_URL", "https://api.binance.com")
    symbols: tuple[str, ...] = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
    reconnect_delay_seconds: int = 5
    change_refresh_interval_seconds: int = 30


@dataclass
class BinancePriceCrawler:
    """从 Binance WebSocket 获取价格并写入 Redis。"""

    redis_client: RedisClient
    config: BinanceConfig = field(default_factory=BinanceConfig)
    change_map: dict[str, float] = field(default_factory=dict)
    _running: bool = field(default=True, repr=False)

    async def _fetch_24h_change(self, session: aiohttp.ClientSession, symbol: str) -> float:
        """调用 REST API 获取单个币种 24h 涨跌幅。"""
        url = f"{self.config.rest_base_url}/api/v3/ticker/24hr"
        params = {"symbol": symbol}

        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            resp.raise_for_status()
            payload = await resp.json()
            return round(float(payload.get("priceChangePercent", 0.0)), 2)

    async def _refresh_24h_changes(self) -> None:
        """定时刷新所有币种 24h 涨跌幅。"""
        while self._running:
            try:
                async with aiohttp.ClientSession() as session:
                    tasks = [self._fetch_24h_change(session, symbol) for symbol in self.config.symbols]
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                for symbol, result in zip(self.config.symbols, results, strict=True):
                    base_symbol = symbol.replace("USDT", "")
                    if isinstance(result, Exception):
                        LOGGER.warning("获取 %s 24h 涨跌幅失败: %s", symbol, result)
                        continue
                    self.change_map[base_symbol] = result

                LOGGER.info("24h 涨跌幅刷新完成: %s", self.change_map)
            except Exception as exc:  # noqa: BLE001
                LOGGER.exception("刷新 24h 涨跌幅任务异常: %s", exc)

            await asyncio.sleep(self.config.change_refresh_interval_seconds)

    @staticmethod
    def _extract_trade_message(message: dict[str, Any]) -> dict[str, Any] | None:
        """兼容标准 trade 消息和 combined stream 消息。"""
        # combined stream: {"stream":"...","data":{...}}
        trade_data = message.get("data", message)

        if trade_data.get("e") != "trade":
            return None

        symbol = str(trade_data.get("s", "")).upper()
        if not symbol.endswith("USDT"):
            return None

        try:
            price = round(float(trade_data["p"]), 2)
        except (KeyError, ValueError, TypeError):
            return None

        return {
            "symbol": symbol.replace("USDT", ""),
            "price": price,
            "timestamp": int(datetime.now(timezone.utc).timestamp()),
        }

    async def _consume_ws(self) -> None:
        """消费 WebSocket 行情并实时更新 Redis。"""
        while self._running:
            try:
                LOGGER.info("连接 Binance WebSocket: %s", self.config.ws_url)
                async with websockets.connect(self.config.ws_url, ping_interval=20, ping_timeout=20) as ws:
                    LOGGER.info("Binance WebSocket 已连接")
                    async for raw_message in ws:
                        try:
                            payload = json.loads(raw_message)
                        except json.JSONDecodeError:
                            LOGGER.warning("收到无法解析的消息: %s", raw_message)
                            continue

                        trade = self._extract_trade_message(payload)
                        if not trade:
                            continue

                        symbol = trade["symbol"]
                        data = {
                            "symbol": symbol,
                            "price": trade["price"],
                            "change24h": self.change_map.get(symbol, 0.0),
                            "timestamp": trade["timestamp"],
                        }
                        await self.redis_client.set_price(symbol, data)
            except (ConnectionClosedError, WebSocketException) as exc:
                LOGGER.warning("WebSocket 连接中断，准备重连: %s", exc)
            except Exception as exc:  # noqa: BLE001
                LOGGER.exception("WebSocket 消费异常: %s", exc)

            await asyncio.sleep(self.config.reconnect_delay_seconds)

    async def run(self) -> None:
        """启动价格爬虫。"""
        change_task = asyncio.create_task(self._refresh_24h_changes())
        ws_task = asyncio.create_task(self._consume_ws())

        try:
            await asyncio.gather(change_task, ws_task)
        finally:
            self._running = False
            for task in (change_task, ws_task):
                task.cancel()
            await asyncio.gather(change_task, ws_task, return_exceptions=True)
