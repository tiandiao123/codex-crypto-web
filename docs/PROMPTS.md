# Agent Prompts - Crypto Web 项目

> 这是给三个 Codex Agent 的具体任务指令

---

## Agent #1: 前端 (Frontend)

### Prompt

```
你是前端开发专家。请在 ~/AgentWork/cryptoweb/frontend/ 目录下创建一个 React 实时加密货币价格面板。

## 技术栈要求
- React 18 + TypeScript (严格模式)
- Tailwind CSS (样式)
- Recharts (价格趋势图表)
- Socket.io-client (WebSocket 客户端)
- Vite (构建工具)

## 功能需求

### 1. 价格面板组件
- 显示 BTC、ETH、SOL 三种币的实时价格
- 每个币种卡片显示：
  - 币种名称和图标
  - 当前价格 (USD)
  - 24小时涨跌幅 (绿色涨/红色跌)
  - 最后更新时间

### 2. 趋势图表
- 显示选中币种的 24 小时价格走势
- 支持点击切换币种
- 使用 Recharts 的 AreaChart

### 3. 新闻流组件
- 右侧边栏显示最新加密新闻
- 每条新闻显示：标题、来源、发布时间
- 点击标题可跳转原文

### 4. 连接状态
- 显示 WebSocket 连接状态 (已连接/断开)
- 断开后自动重连

## 接口契约 (必须严格遵循)

### WebSocket 连接
const socket = io('ws://localhost:8000');

### 监听事件
socket.on('price_update', (data: PriceUpdate) => {
  // data = { symbol: "BTC", price: 67500.50, change24h: 2.5, timestamp: 1234567890 }
});

socket.on('news_update', (data: NewsUpdate) => {
  // data = { id: "1", title: "...", source: "Cointelegraph", url: "...", publishedAt: "..." }
});

## 目录结构要求
src/
  ├── components/
  │   ├── PriceCard.tsx      # 价格卡片组件
  │   ├── PriceChart.tsx     # 趋势图表组件
  │   ├── NewsFeed.tsx       # 新闻流组件
  │   └── ConnectionStatus.tsx # 连接状态
  ├── hooks/
  │   └── useWebSocket.ts    # WebSocket Hook
  ├── types/
  │   └── index.ts           # TypeScript 类型定义
  ├── App.tsx
  └── main.tsx

## 输出要求
1. 完整的可运行代码
2. package.json 包含所有依赖
3. README.md 说明如何运行 (npm install && npm run dev)
4. 代码必须有注释，解释关键逻辑

## 完成通知
完成后，创建一个文件 DONE.txt，内容写：
"Frontend Agent completed. Features: [列出完成的功能]"

现在请开始开发。
```

---

## Agent #2: 后端 (Backend)

### Prompt

```
你是后端开发专家。请在 ~/AgentWork/cryptoweb/backend/ 目录下创建一个 FastAPI WebSocket 服务。

## 技术栈要求
- Python 3.11+
- FastAPI (Web 框架)
- WebSocket (socket.io 或原生)
- Redis (数据缓存)
- Uvicorn (ASGI 服务器)

## 功能需求

### 1. WebSocket 服务
- 端点: /ws/prices
- 向前端推送实时价格数据
- 支持多个客户端同时连接

### 2. 数据聚合 API
GET /api/prices
返回: [{"symbol": "BTC", "price": 67500.50, "change24h": 2.5, "timestamp": 1234567890}, ...]

GET /api/prices/{symbol}
返回: 指定币种的当前价格详情

GET /api/prices/{symbol}/history?range=24h
返回: 24小时价格历史数据 (用于图表)

GET /api/news
返回: 最新新闻列表 [{"id": "1", "title": "...", "source": "...", "url": "...", "publishedAt": "..."}]

GET /api/health
返回: {"status": "ok", "timestamp": 1234567890}

### 3. 数据消费
- 从 Redis 读取价格数据 (数据 Agent 写入)
- 从 Redis 读取新闻数据
- 价格变化时通过 WebSocket 推送给所有连接的客户端

### 4. CORS 配置
- 允许前端 http://localhost:5173 访问

## 接口契约 (必须严格遵循)

### WebSocket 消息格式
{
  "type": "price_update",
  "data": {
    "symbol": "BTC",           // 大写币种代码
    "price": 67500.50,         // 当前价格
    "change24h": 2.5,          // 24小时涨跌百分比
    "timestamp": 1234567890    // Unix 时间戳(秒)
  }
}

{
  "type": "news_update",
  "data": {
    "id": "unique-id",
    "title": "新闻标题",
    "source": "Cointelegraph",  // 来源名称
    "url": "https://...",       // 原文链接
    "publishedAt": "2024-01-15T10:30:00Z"  // ISO 8601 格式
  }
}

### Redis 数据结构
# 价格数据 (Hash)
HGETALL crypto:prices
# 返回: {"BTC": "{\"price\":67500.50,...}", "ETH": "...", ...}

# 新闻数据 (List)
LRANGE crypto:news 0 19
# 返回: 最近20条新闻的 JSON 字符串列表

## 目录结构要求
backend/
  ├── app/
  │   ├── __init__.py
  │   ├── main.py           # FastAPI 应用入口
  │   ├── websocket.py      # WebSocket 处理
  │   ├── api.py            # REST API 路由
  │   ├── redis_client.py   # Redis 连接
  │   └── models.py         # Pydantic 模型
  ├── requirements.txt
  └── README.md

## 输出要求
1. 完整的可运行代码
2. requirements.txt 包含所有依赖
3. README.md 说明如何运行 (pip install + uvicorn)
4. 包含错误处理和日志
5. 代码必须有注释

## 完成通知
完成后，创建一个文件 DONE.txt，内容写：
"Backend Agent completed. Features: [列出完成的功能]"

现在请开始开发。
```

---

## Agent #3: 数据 (Data)

### Prompt

```
你是数据工程师。请在 ~/AgentWork/cryptoweb/data/ 目录下创建加密货币数据爬虫和处理脚本。

## 技术栈要求
- Python 3.11+
- websockets (异步 WebSocket 客户端)
- aiohttp (HTTP 请求)
- feedparser (RSS 解析)
- APScheduler (定时任务)
- redis (数据存储)

## 功能需求

### 1. 实时价格获取 (核心功能)
- 连接 Binance WebSocket 流
- 订阅 BTCUSDT、ETHUSDT、SOLUSDT 的实时交易数据
- 每 5 秒计算并存储一次最新价格
- 写入 Redis Hash: crypto:prices

### 2. 价格历史记录
- 每分钟保存一次价格快照
- 保留最近 24 小时数据
- 用于前端图表展示

### 3. 新闻聚合 (定时任务)
- 每 15 分钟抓取一次 RSS 源
- 数据源:
  - https://cointelegraph.com/rss
  - https://coindesk.com/arc/outboundfeeds/rss/
- 解析标题、链接、发布时间
- 写入 Redis List: crypto:news (保留最近 50 条)
- 去重：同一链接不重复存储

### 4. 数据清洗
- 价格数据格式化到 2 位小数
- 新闻标题去除多余空格
- 处理时区统一为 UTC

## 接口契约 (必须严格遵循)

### Redis 写入格式

# 价格数据 (Hash: crypto:prices)
HSET crypto:prices BTC '{"symbol":"BTC","price":67500.50,"change24h":2.5,"timestamp":1234567890}'
HSET crypto:prices ETH '{"symbol":"ETH","price":3500.00,"change24h":-1.2,"timestamp":1234567890}'

注意：
- symbol: 大写，不含 USDT (BTC 而不是 BTCUSDT)
- price: float
- change24h: float, 百分比 (如 2.5 表示涨 2.5%)
- timestamp: Unix 时间戳 (秒)
- 整个对象作为 JSON 字符串存储

# 新闻数据 (List: crypto:news)
LPUSH crypto:news '{"id":"...","title":"...","source":"...","url":"...","publishedAt":"..."}'
LTRIM crypto:news 0 49  # 只保留最近50条

注意：
- id: 使用 URL 的 MD5 或 UUID
- publishedAt: ISO 8601 格式

## 目录结构要求
data/
  ├── crawlers/
  │   ├── __init__.py
  │   ├── binance_ws.py     # Binance WebSocket 价格获取
  │   ├── price_history.py  # 价格历史记录
  │   └── news_rss.py       # RSS 新闻抓取
  ├── scheduler.py          # 定时任务调度
  ├── redis_client.py       # Redis 连接工具
  ├── main.py               # 入口文件
  ├── requirements.txt
  └── README.md

## 数据源详情

### Binance WebSocket
连接: wss://stream.binance.com:9443/ws/btcusdt@trade/ethusdt@trade/solusdt@trade
消息格式: {"s":"BTCUSDT","p":"67500.50",...}

### 24小时涨跌幅计算
使用 Binance REST API:
GET https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT
返回: {"priceChangePercent": "2.5", ...}

### RSS 源
- Cointelegraph: https://cointelegraph.com/rss
- CoinDesk: https://coindesk.com/arc/outboundfeeds/rss/

## 输出要求
1. 完整的可运行代码
2. requirements.txt 包含所有依赖
3. README.md 说明如何运行 (pip install + python main.py)
4. 包含错误处理、重连机制、日志记录
5. 代码必须有注释

## 完成通知
完成后，创建一个文件 DONE.txt，内容写：
"Data Agent completed. Features: [列出完成的功能]"

现在请开始开发。
```

---

## 附：OpenClaw 启动命令

```bash
# 前端 Agent
exec pty:true background:true workdir:~/AgentWork/cryptoweb/frontend \
  command:"codex --full-auto exec '[上面前端 Prompt]'"

# 后端 Agent  
exec pty:true background:true workdir:~/AgentWork/cryptoweb/backend \
  command:"codex --full-auto exec '[上面后端 Prompt]'"

# 数据 Agent
exec pty:true background:true workdir:~/AgentWork/cryptoweb/data \
  command:"codex --full-auto exec '[上面数据 Prompt]'"
```

---

*Prompt 版本: v1.0*
