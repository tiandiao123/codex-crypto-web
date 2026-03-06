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
