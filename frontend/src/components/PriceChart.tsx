import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from 'recharts';
import type { CryptoSymbol, PricePoint } from '../types';

interface PriceChartProps {
  selectedSymbol: CryptoSymbol;
  onSelectSymbol: (symbol: CryptoSymbol) => void;
  points: PricePoint[];
}

const symbols: CryptoSymbol[] = ['BTC', 'ETH', 'SOL'];

// 24h area chart for selected symbol.
export const PriceChart = ({ selectedSymbol, onSelectSymbol, points }: PriceChartProps) => {
  const chartData = points.map((point) => ({
    time: new Date(point.timestamp).toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    }),
    price: Number(point.price.toFixed(2))
  }));

  return (
    <section className="rounded-xl border border-slate-800 bg-slate-900/70 p-4">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-white">24小时价格走势</h2>
        <div className="flex gap-2">
          {symbols.map((symbol) => (
            <button
              key={symbol}
              type="button"
              onClick={() => onSelectSymbol(symbol)}
              className={`rounded-md px-3 py-1 text-sm ${
                selectedSymbol === symbol
                  ? 'bg-cyan-500 text-slate-950'
                  : 'bg-slate-800 text-slate-200 hover:bg-slate-700'
              }`}
            >
              {symbol}
            </button>
          ))}
        </div>
      </div>

      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 10, right: 10, bottom: 0, left: 0 }}>
            <defs>
              <linearGradient id="priceFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.6} />
                <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="time" stroke="#94a3b8" minTickGap={28} />
            <YAxis stroke="#94a3b8" domain={['auto', 'auto']} tickFormatter={(value) => `$${value}`} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0f172a',
                borderColor: '#334155',
                borderRadius: '0.5rem'
              }}
              formatter={(value: number) => [`$${value.toLocaleString('en-US')}`, '价格']}
            />
            <Area type="monotone" dataKey="price" stroke="#22d3ee" fillOpacity={1} fill="url(#priceFill)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {chartData.length === 0 && <p className="mt-3 text-sm text-slate-400">等待实时价格数据...</p>}
    </section>
  );
};
