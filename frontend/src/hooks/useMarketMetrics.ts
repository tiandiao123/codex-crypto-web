import { useEffect, useState } from 'react';
import type { MarketMetrics } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8000`;
const POLL_INTERVAL_MS = 30_000;

export const useMarketMetrics = () => {
  const [metrics, setMetrics] = useState<MarketMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    const fetchMetrics = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/market-metrics`);
        if (!response.ok) {
          return;
        }

        const data = (await response.json()) as MarketMetrics;
        if (mounted) {
          setMetrics(data);
        }
      } catch {
        // Keep previous data on temporary fetch failures.
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    void fetchMetrics();
    const timer = window.setInterval(fetchMetrics, POLL_INTERVAL_MS);

    return () => {
      mounted = false;
      window.clearInterval(timer);
    };
  }, []);

  return { metrics, loading };
};
