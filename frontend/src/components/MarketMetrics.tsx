import type { MacroIndicator, MarketMetrics } from '../types';

interface MarketMetricsProps {
  data: MarketMetrics | null;
  loading: boolean;
}

const renderValue = (value: number | null, digits = 2) => {
  if (value === null || Number.isNaN(value)) {
    return '--';
  }
  return value.toLocaleString('en-US', { maximumFractionDigits: digits });
};

const indicatorClass = (indicator: MacroIndicator) => {
  if (indicator.change_pct === null) {
    return 'text-slate-300';
  }
  return indicator.change_pct >= 0 ? 'text-emerald-400' : 'text-red-400';
};

const renderChange = (indicator: MacroIndicator) => {
  if (indicator.change_pct === null) {
    return '--';
  }
  const sign = indicator.change_pct >= 0 ? '+' : '';
  return `${sign}${indicator.change_pct.toFixed(2)}%`;
};

export const MarketMetrics = ({ data, loading }: MarketMetricsProps) => {
  const updated = data
    ? new Date(data.updated_at * 1000).toLocaleTimeString('zh-CN', { hour12: false })
    : '--:--:--';

  return (
    <section className="rounded-xl border border-slate-800 bg-slate-900/70 p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">市场指标（期权 + 宏观）</h2>
        <span className="text-xs text-slate-400">更新: {updated}</span>
      </div>

      {loading && !data && <p className="text-sm text-slate-400">加载指标中...</p>}

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
          <div className="text-xs text-slate-400">BTC Put/Call OI</div>
          <div className="mt-1 text-xl font-semibold text-white">
            {renderValue(data?.options.btc_put_call_ratio ?? null, 3)}
          </div>
          <div className="mt-1 text-xs text-slate-400">
            Call OI {renderValue(data?.options.btc_call_open_interest ?? null, 0)} · Put OI{' '}
            {renderValue(data?.options.btc_put_open_interest ?? null, 0)}
          </div>
        </div>

        <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
          <div className="text-xs text-slate-400">ETH Total OI</div>
          <div className="mt-1 text-xl font-semibold text-white">
            {renderValue(data?.options.eth_total_open_interest ?? null, 0)}
          </div>
          <div className="mt-1 text-xs text-slate-400">Deribit Options</div>
        </div>

        <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
          <div className="text-xs text-slate-400">DXY / US10Y</div>
          <div className="mt-1 text-sm text-white">
            DXY: <span className={indicatorClass(data?.macro.dxy ?? { value: null, change_pct: null })}>{renderValue(data?.macro.dxy.value ?? null, 3)}</span>
            <span className="ml-2 text-xs text-slate-400">({renderChange(data?.macro.dxy ?? { value: null, change_pct: null })})</span>
          </div>
          <div className="mt-1 text-sm text-white">
            US10Y: <span className={indicatorClass(data?.macro.us10y ?? { value: null, change_pct: null })}>{renderValue(data?.macro.us10y.value ?? null, 3)}%</span>
            <span className="ml-2 text-xs text-slate-400">({renderChange(data?.macro.us10y ?? { value: null, change_pct: null })})</span>
          </div>
        </div>

        <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
          <div className="text-xs text-slate-400">Risk & Breadth</div>
          <div className="mt-1 text-sm text-white">BTC.D: {renderValue(data?.macro.btc_dominance ?? null, 2)}%</div>
          <div className="mt-1 text-sm text-white">Fear & Greed: {renderValue(data?.macro.fear_greed_index ?? null, 0)}</div>
          <div className="mt-1 text-xs text-slate-400">
            ES: {renderValue(data?.macro.sp500_futures.value ?? null, 2)} · NQ:{' '}
            {renderValue(data?.macro.nasdaq_futures.value ?? null, 2)}
          </div>
        </div>
      </div>
    </section>
  );
};
