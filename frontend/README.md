# Crypto Realtime Dashboard (React + TypeScript)

一个基于 `React 18 + TypeScript + Tailwind CSS + Recharts + Socket.io-client + Vite` 的实时加密货币价格面板。

## 功能

- 实时显示 `BTC`、`ETH`、`SOL` 价格
- 每个币种卡片显示：图标、当前价格、24小时涨跌幅、最后更新时间
- 24小时价格趋势图（`Recharts AreaChart`），支持点击切换币种
- 右侧新闻流，显示标题、来源、发布时间，支持跳转原文
- WebSocket 连接状态展示（连接中 / 已连接 / 断开）
- 自动重连（Socket.io reconnection）

## WebSocket 契约

前端严格使用以下连接与事件：

```ts
const socket = io('ws://localhost:8000');

socket.on('price_update', (data) => {
  // data = { symbol: BTC, price: 67500.50, change24h: 2.5, timestamp: 1234567890 }
});

socket.on('news_update', (data) => {
  // data = { id: 1, title: ..., source: Cointelegraph, url: ..., publishedAt: ... }
});
```

## 安装与运行

```bash
npm install
npm run dev
```

默认启动后访问：

- `http://localhost:5173`

## 构建

```bash
npm run build
npm run preview
```

## 项目结构

```text
src/
  ├── components/
  │   ├── PriceCard.tsx
  │   ├── PriceChart.tsx
  │   ├── NewsFeed.tsx
  │   └── ConnectionStatus.tsx
  ├── hooks/
  │   └── useWebSocket.ts
  ├── types/
  │   └── index.ts
  ├── App.tsx
  └── main.tsx
```
