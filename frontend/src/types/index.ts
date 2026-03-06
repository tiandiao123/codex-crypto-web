// Supported crypto symbols in the dashboard.
export type CryptoSymbol = 'BTC' | 'ETH' | 'SOL';

// Latest price event shape from websocket.
export interface PriceUpdate {
  symbol: CryptoSymbol;
  price: number;
  change24h: number;
  timestamp: number;
}

// Single point used by the chart.
export interface PricePoint {
  timestamp: number;
  price: number;
}

// News event shape from websocket.
export interface NewsItem {
  id: string;
  title: string;
  source: string;
  url: string;
  publishedAt: string;
}

// WebSocket connection status used by UI.
export type ConnectionState = 'connecting' | 'connected' | 'disconnected';

export interface OptionMetrics {
  btc_call_open_interest: number;
  btc_put_open_interest: number;
  btc_put_call_ratio: number;
  eth_total_open_interest: number;
}

export interface MacroIndicator {
  value: number | null;
  change_pct: number | null;
}

export interface MacroMetrics {
  dxy: MacroIndicator;
  us10y: MacroIndicator;
  sp500_futures: MacroIndicator;
  nasdaq_futures: MacroIndicator;
  btc_dominance: number | null;
  fear_greed_index: number | null;
}

export interface MarketMetrics {
  options: OptionMetrics;
  macro: MacroMetrics;
  updated_at: number;
}
