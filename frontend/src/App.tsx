import { useMemo, useState } from 'react';
import { ConnectionStatus } from './components/ConnectionStatus';
import { MarketMetrics } from './components/MarketMetrics';
import { NewsFeed } from './components/NewsFeed';
import { PriceCard } from './components/PriceCard';
import { PriceChart } from './components/PriceChart';
import { useMarketMetrics } from './hooks/useMarketMetrics';
import { useWebSocket } from './hooks/useWebSocket';
import type { CryptoSymbol } from './types';

// Main dashboard page.
function App() {
  const [selectedSymbol, setSelectedSymbol] = useState<CryptoSymbol>('BTC');
  const { connectionState, prices, priceHistory, news } = useWebSocket();
  const { metrics, loading: metricsLoading } = useMarketMetrics();

  const cards = useMemo<CryptoSymbol[]>(() => ['BTC', 'ETH', 'SOL'], []);

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-7xl p-4 md:p-6">
        <header className="mb-6 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white md:text-3xl">Crypto 实时价格面板</h1>
            <p className="text-sm text-slate-400">BTC / ETH / SOL · WebSocket 实时更新</p>
          </div>
          <ConnectionStatus state={connectionState} />
        </header>

        <div className="mb-6">
          <MarketMetrics data={metrics} loading={metricsLoading} />
        </div>

        <div className="grid grid-cols-1 gap-6 xl:grid-cols-12">
          <section className="space-y-6 xl:col-span-8">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              {cards.map((symbol) => (
                <PriceCard
                  key={symbol}
                  symbol={symbol}
                  data={prices[symbol]}
                  isSelected={symbol === selectedSymbol}
                  onSelect={setSelectedSymbol}
                />
              ))}
            </div>

            <PriceChart
              selectedSymbol={selectedSymbol}
              onSelectSymbol={setSelectedSymbol}
              points={priceHistory[selectedSymbol]}
            />
          </section>

          <section className="xl:col-span-4">
            <NewsFeed news={news} />
          </section>
        </div>
      </div>
    </main>
  );
}

export default App;
