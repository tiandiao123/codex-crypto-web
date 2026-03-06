import type { CryptoSymbol, PriceUpdate } from '../types';

interface PriceCardProps {
  symbol: CryptoSymbol;
  data: PriceUpdate | null;
  isSelected: boolean;
  onSelect: (symbol: CryptoSymbol) => void;
}

const SYMBOL_ICON: Record<CryptoSymbol, string> = {
  BTC: '₿',
  ETH: '◆',
  SOL: '◎'
};

// Card for one cryptocurrency with realtime values.
export const PriceCard = ({ symbol, data, isSelected, onSelect }: PriceCardProps) => {
  const priceText = data ? `$${data.price.toLocaleString('en-US', { maximumFractionDigits: 2 })}` : '--';
  const change = data?.change24h ?? 0;
  const changeClass = change >= 0 ? 'text-emerald-400' : 'text-red-400';
  const lastUpdated = data
    ? new Date(data.timestamp).toLocaleTimeString('zh-CN', { hour12: false })
    : '--:--:--';

  return (
    <button
      type="button"
      onClick={() => onSelect(symbol)}
      className={`w-full rounded-xl border p-4 text-left transition ${
        isSelected
          ? 'border-cyan-400/70 bg-cyan-500/10 shadow-lg shadow-cyan-900/30'
          : 'border-slate-800 bg-slate-900/70 hover:border-slate-700'
      }`}
    >
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2 text-white">
          <span className="text-lg">{SYMBOL_ICON[symbol]}</span>
          <span className="font-semibold">{symbol}</span>
        </div>
        <span className="text-xs text-slate-400">更新: {lastUpdated}</span>
      </div>

      <div className="text-2xl font-bold text-white">{priceText}</div>
      <div className={`mt-2 text-sm font-medium ${changeClass}`}>
        24H: {change >= 0 ? '+' : ''}
        {change.toFixed(2)}%
      </div>
    </button>
  );
};
