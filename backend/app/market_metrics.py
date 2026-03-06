"""Aggregate options and macro market metrics from public APIs."""

from __future__ import annotations

import logging
import time

import httpx

from app.models import MacroIndicator, MacroMetrics, MarketMetricsResponse, OptionMetrics

logger = logging.getLogger(__name__)


class MarketMetricsClient:
    """Fetch and normalize market metrics from multiple data sources."""

    def __init__(self) -> None:
        self.timeout = httpx.Timeout(8.0)

    async def get_market_metrics(self) -> MarketMetricsResponse:
        """Return aggregated options and macro indicators."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            options = await self._get_options_metrics(client)
            macro = await self._get_macro_metrics(client)

        return MarketMetricsResponse(
            options=options,
            macro=macro,
            updated_at=int(time.time()),
        )

    async def _get_options_metrics(self, client: httpx.AsyncClient) -> OptionMetrics:
        """Fetch BTC/ETH options open interest from Deribit."""
        btc_url = "https://www.deribit.com/api/v2/public/get_book_summary_by_currency"
        params_btc = {"currency": "BTC", "kind": "option"}
        params_eth = {"currency": "ETH", "kind": "option"}

        btc_call_oi = 0.0
        btc_put_oi = 0.0
        eth_total_oi = 0.0

        try:
            btc_resp = await client.get(btc_url, params=params_btc)
            btc_resp.raise_for_status()
            btc_result = btc_resp.json().get("result", [])

            for row in btc_result:
                name = str(row.get("instrument_name", ""))
                open_interest = float(row.get("open_interest") or 0.0)
                if name.endswith("-C"):
                    btc_call_oi += open_interest
                elif name.endswith("-P"):
                    btc_put_oi += open_interest
        except Exception:
            logger.exception("Failed to fetch BTC options metrics from Deribit")

        try:
            eth_resp = await client.get(btc_url, params=params_eth)
            eth_resp.raise_for_status()
            eth_result = eth_resp.json().get("result", [])
            for row in eth_result:
                eth_total_oi += float(row.get("open_interest") or 0.0)
        except Exception:
            logger.exception("Failed to fetch ETH options metrics from Deribit")

        put_call_ratio = round(btc_put_oi / btc_call_oi, 4) if btc_call_oi > 0 else 0.0

        return OptionMetrics(
            btc_call_open_interest=round(btc_call_oi, 2),
            btc_put_open_interest=round(btc_put_oi, 2),
            btc_put_call_ratio=put_call_ratio,
            eth_total_open_interest=round(eth_total_oi, 2),
        )

    async def _get_macro_metrics(self, client: httpx.AsyncClient) -> MacroMetrics:
        """Fetch macro indicators from Yahoo Finance, CoinGecko and Alternative.me."""
        dxy = MacroIndicator()
        us10y = MacroIndicator()
        sp500_futures = MacroIndicator()
        nasdaq_futures = MacroIndicator()
        btc_dominance: float | None = None
        fear_greed: float | None = None

        try:
            quote_url = "https://query1.finance.yahoo.com/v7/finance/quote"
            params = {"symbols": "DX-Y.NYB,^TNX,ES=F,NQ=F"}
            quote_resp = await client.get(quote_url, params=params)
            quote_resp.raise_for_status()
            items = quote_resp.json().get("quoteResponse", {}).get("result", [])

            by_symbol: dict[str, dict] = {str(item.get("symbol")): item for item in items}

            dxy = self._to_indicator(by_symbol.get("DX-Y.NYB"))

            us10y_raw = self._to_indicator(by_symbol.get("^TNX"))
            if us10y_raw.value is not None:
                normalized = us10y_raw.value / 10 if us10y_raw.value > 20 else us10y_raw.value
                us10y = MacroIndicator(value=round(normalized, 3), change_pct=us10y_raw.change_pct)
            else:
                us10y = us10y_raw

            sp500_futures = self._to_indicator(by_symbol.get("ES=F"))
            nasdaq_futures = self._to_indicator(by_symbol.get("NQ=F"))
        except Exception:
            logger.exception("Failed to fetch Yahoo macro quotes")

        # Fallback source for DXY / ES / NQ when Yahoo is rate-limited.
        if (
            dxy.value is None
            or sp500_futures.value is None
            or nasdaq_futures.value is None
        ):
            stooq_quotes = await self._get_stooq_quotes(client, ["dx.f", "es.f", "nq.f"])
            dxy = dxy if dxy.value is not None else stooq_quotes.get("dx.f", MacroIndicator())
            sp500_futures = (
                sp500_futures
                if sp500_futures.value is not None
                else stooq_quotes.get("es.f", MacroIndicator())
            )
            nasdaq_futures = (
                nasdaq_futures
                if nasdaq_futures.value is not None
                else stooq_quotes.get("nq.f", MacroIndicator())
            )

        # Fallback source for US10Y when Yahoo is rate-limited.
        if us10y.value is None:
            us10y = await self._get_fred_us10y(client)

        try:
            gecko_url = "https://api.coingecko.com/api/v3/global"
            gecko_resp = await client.get(gecko_url)
            gecko_resp.raise_for_status()
            gecko_data = gecko_resp.json().get("data", {})
            btc_dominance = float(
                gecko_data.get("market_cap_percentage", {}).get("btc") or 0.0
            )
        except Exception:
            logger.exception("Failed to fetch BTC dominance from CoinGecko")

        try:
            fng_url = "https://api.alternative.me/fng/"
            fng_resp = await client.get(fng_url, params={"limit": 1})
            fng_resp.raise_for_status()
            latest = (fng_resp.json().get("data") or [{}])[0]
            fear_greed = float(latest.get("value") or 0.0)
        except Exception:
            logger.exception("Failed to fetch fear/greed index")

        return MacroMetrics(
            dxy=dxy,
            us10y=us10y,
            sp500_futures=sp500_futures,
            nasdaq_futures=nasdaq_futures,
            btc_dominance=round(btc_dominance, 2) if btc_dominance is not None else None,
            fear_greed_index=fear_greed,
        )

    async def _get_stooq_quotes(
        self, client: httpx.AsyncClient, symbols: list[str]
    ) -> dict[str, MacroIndicator]:
        """Fetch quote snapshots from stooq CSV endpoint."""
        result: dict[str, MacroIndicator] = {}
        for symbol in symbols:
            try:
                url = "https://stooq.com/q/l/"
                resp = await client.get(url, params={"s": symbol, "i": "d"})
                resp.raise_for_status()

                line = resp.text.strip().splitlines()[0]
                parts = line.split(",")
                # SYMBOL,DATE,TIME,OPEN,HIGH,LOW,CLOSE,VOLUME,...
                close_raw = parts[6] if len(parts) > 6 else "N/D"
                open_raw = parts[3] if len(parts) > 3 else "N/D"

                if close_raw == "N/D":
                    continue

                close_value = float(close_raw)
                change_pct: float | None = None
                if open_raw != "N/D":
                    open_value = float(open_raw)
                    if open_value != 0:
                        change_pct = ((close_value - open_value) / open_value) * 100

                result[symbol] = MacroIndicator(
                    value=round(close_value, 4),
                    change_pct=round(change_pct, 4) if change_pct is not None else None,
                )
            except Exception:
                logger.exception("Failed to fetch stooq quote for %s", symbol)

        return result

    async def _get_fred_us10y(self, client: httpx.AsyncClient) -> MacroIndicator:
        """Fetch US10Y daily yield from FRED public CSV."""
        try:
            url = "https://fred.stlouisfed.org/graph/fredgraph.csv"
            resp = await client.get(url, params={"id": "DGS10"})
            resp.raise_for_status()

            lines = [line.strip() for line in resp.text.splitlines() if line.strip()]
            # skip header and find latest available observation
            for line in reversed(lines[1:]):
                _, value = line.split(",", 1)
                if value != ".":
                    return MacroIndicator(value=round(float(value), 3), change_pct=None)
        except Exception:
            logger.exception("Failed to fetch US10Y from FRED")

        return MacroIndicator()

    @staticmethod
    def _to_indicator(payload: dict | None) -> MacroIndicator:
        """Convert Yahoo quote payload to MacroIndicator."""
        if not payload:
            return MacroIndicator()

        value = payload.get("regularMarketPrice")
        change_pct = payload.get("regularMarketChangePercent")

        return MacroIndicator(
            value=round(float(value), 4) if value is not None else None,
            change_pct=round(float(change_pct), 4) if change_pct is not None else None,
        )


market_metrics_client = MarketMetricsClient()
