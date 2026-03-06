import type { ConnectionState } from '../types';

interface ConnectionStatusProps {
  state: ConnectionState;
}

// Displays current websocket connection state.
export const ConnectionStatus = ({ state }: ConnectionStatusProps) => {
  const stateConfig: Record<ConnectionState, { label: string; className: string }> = {
    connecting: { label: '连接中', className: 'text-amber-400 bg-amber-500/10 border-amber-500/30' },
    connected: { label: '已连接', className: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30' },
    disconnected: { label: '断开', className: 'text-red-400 bg-red-500/10 border-red-500/30' }
  };

  return (
    <div className={`inline-flex items-center gap-2 rounded-lg border px-3 py-1 text-sm ${stateConfig[state].className}`}>
      <span className="h-2 w-2 rounded-full bg-current" />
      <span>WebSocket: {stateConfig[state].label}</span>
    </div>
  );
};
