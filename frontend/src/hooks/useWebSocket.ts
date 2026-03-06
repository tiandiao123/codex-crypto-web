import { useEffect, useRef, useState } from 'react';
import { io, type Socket } from 'socket.io-client';
import type { ConnectionState, CryptoSymbol, NewsItem, PricePoint, PriceUpdate } from '../types';

const SUPPORTED_SYMBOLS: CryptoSymbol[] = ['BTC', 'ETH', 'SOL'];
const DAY_MS = 24 * 60 * 60 * 1000;

// 从环境变量获取后端地址，默认使用当前主机
const WS_URL = import.meta.env.VITE_WS_URL || `ws://${window.location.hostname}:8000`;
const API_BASE_URL = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8000`;

interface WrappedEvent<T> {
  type?: string;
  data?: T;
}

// Normalize seconds/milliseconds timestamp into milliseconds.
const normalizeTimestamp = (timestamp: number): number => {
  return timestamp < 1_000_000_000_000 ? timestamp * 1000 : timestamp;
};

// Hook that owns realtime websocket data and reconnection behavior.
export const useWebSocket = () => {
  const socketRef = useRef<Socket | null>(null);
  const [connectionState, setConnectionState] = useState<ConnectionState>('connecting');
  const [prices, setPrices] = useState<Record<CryptoSymbol, PriceUpdate | null>>({
    BTC: null,
    ETH: null,
    SOL: null
  });
  const [priceHistory, setPriceHistory] = useState<Record<CryptoSymbol, PricePoint[]>>({
    BTC: [],
    ETH: [],
    SOL: []
  });
  const [news, setNews] = useState<NewsItem[]>([]);

  useEffect(() => {
    const unwrapPayload = <T,>(payload: T | WrappedEvent<T>): T | null => {
      if (payload && typeof payload === 'object' && 'data' in payload) {
        const wrapped = payload as WrappedEvent<T>;
        return wrapped.data ?? null;
      }
      return payload as T;
    };

    // Connect to WebSocket server.
    const socket = io(WS_URL, {
      reconnection: true,
      reconnectionAttempts: Infinity,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000
    });

    socketRef.current = socket;

    socket.on('connect', () => {
      setConnectionState('connected');
    });

    socket.on('disconnect', () => {
      setConnectionState('disconnected');
    });

    socket.on('connect_error', () => {
      setConnectionState('disconnected');
    });

    socket.on('reconnect_attempt', () => {
      setConnectionState('connecting');
    });

    socket.on('price_update', (payload: PriceUpdate | WrappedEvent<PriceUpdate>) => {
      const data = unwrapPayload(payload);
      if (!data || !SUPPORTED_SYMBOLS.includes(data.symbol)) {
        return;
      }

      const timestamp = normalizeTimestamp(data.timestamp);
      const normalizedData: PriceUpdate = { ...data, timestamp };

      setPrices((prev) => ({
        ...prev,
        [data.symbol]: normalizedData
      }));

      // Keep only last 24h points per symbol.
      setPriceHistory((prev) => {
        const nextPoints = [...prev[data.symbol], { timestamp, price: data.price }].filter(
          (point) => point.timestamp >= timestamp - DAY_MS
        );

        return {
          ...prev,
          [data.symbol]: nextPoints
        };
      });
    });

    socket.on('news_update', (payload: NewsItem | WrappedEvent<NewsItem>) => {
      const data = unwrapPayload(payload);
      if (!data || !data.id) {
        return;
      }

      setNews((prev) => {
        const filtered = prev.filter((item) => item.id !== data.id);
        const merged = [data, ...filtered].sort(
          (a, b) => new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime()
        );

        return merged.slice(0, 20);
      });
    });

    const loadInitialNews = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/news`);
        if (!response.ok) {
          return;
        }

        const data = (await response.json()) as NewsItem[];
        setNews((prev) => {
          const mergedMap = new Map<string, NewsItem>();
          [...data, ...prev].forEach((item) => {
            mergedMap.set(item.id, item);
          });

          return [...mergedMap.values()]
            .sort((a, b) => new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime())
            .slice(0, 20);
        });
      } catch {
        // Ignore transient fetch errors.
      }
    };

    void loadInitialNews();

    return () => {
      socket.disconnect();
      socketRef.current = null;
    };
  }, []);

  return {
    connectionState,
    prices,
    priceHistory,
    news
  };
};
