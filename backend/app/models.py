"""Pydantic models for API and Socket.IO payloads."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PriceData(BaseModel):
    """Single crypto price record parsed from Redis."""

    symbol: str
    price: float
    change24h: float = Field(default=0, description="24h percentage change")
    timestamp: int = Field(default=0, description="Unix timestamp")


class PriceUpdateEvent(BaseModel):
    """Socket.IO event payload for price update."""

    type: str = "price_update"
    data: PriceData


class NewsData(BaseModel):
    """Single news record parsed from Redis."""

    id: str
    title: str
    source: str
    url: str
    publishedAt: str


class NewsUpdateEvent(BaseModel):
    """Socket.IO event payload for news update."""

    type: str = "news_update"
    data: NewsData


class PriceHistoryResponse(BaseModel):
    """Response model for symbol history query."""

    symbol: str
    range: str
    history: list[dict[str, Any]]


class HealthResponse(BaseModel):
    """Health endpoint response model."""

    status: str
    redis: str


class OptionMetrics(BaseModel):
    """Aggregated crypto options metrics."""

    btc_call_open_interest: float = 0
    btc_put_open_interest: float = 0
    btc_put_call_ratio: float = 0
    eth_total_open_interest: float = 0


class MacroIndicator(BaseModel):
    """One macro indicator quote and its percentage change."""

    value: float | None = None
    change_pct: float | None = None


class MacroMetrics(BaseModel):
    """Macro and cross-market indicators."""

    dxy: MacroIndicator
    us10y: MacroIndicator
    sp500_futures: MacroIndicator
    nasdaq_futures: MacroIndicator
    btc_dominance: float | None = None
    fear_greed_index: float | None = None


class MarketMetricsResponse(BaseModel):
    """Unified market metrics payload for frontend dashboard."""

    options: OptionMetrics
    macro: MacroMetrics
    updated_at: int
