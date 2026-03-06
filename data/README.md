# CryptoWeb 数据爬虫

基于 Python 3.11+ 的加密货币实时数据采集与处理服务，包含：
- Binance WebSocket 实时价格采集
- Binance REST 24h 涨跌幅补充
- 价格历史快照（每分钟）
- RSS 新闻聚合（每 15 分钟）
- Redis 存储与去重

## 目录结构

```text
crawlers/
  ├── __init__.py
  ├── binance_ws.py
  ├── price_history.py
  └── news_rss.py
scheduler.py
redis_client.py
main.py
requirements.txt
README.md
```

## 环境要求

- Python 3.11+
- Redis 服务可用（默认 `redis://localhost:6379/0`）

## 安装依赖

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 配置项（可选）

可通过环境变量覆盖默认配置：

- `REDIS_URL`：Redis 地址，默认 `redis://localhost:6379/0`
- `BINANCE_WS_URL`：WebSocket 地址，默认
  `wss://stream.binance.com:9443/ws/btcusdt@trade/ethusdt@trade/solusdt@trade`
- `BINANCE_REST_URL`：Binance REST 地址，默认 `https://api.binance.com`

## 运行

```bash
python main.py
```

## Redis 数据格式

### 1) 实时价格（Hash）

- Key: `crypto:prices`
- Field: `BTC` / `ETH` / `SOL`
- Value(JSON字符串):

```json
{"symbol":"BTC","price":67500.5,"change24h":2.5,"timestamp":1234567890}
```

### 2) 新闻（List）

- Key: `crypto:news`
- 写入：`LPUSH crypto:news <json>`
- 保留：`LTRIM crypto:news 0 49`

### 3) 历史价格（Sorted Set）

- Key: `crypto:history:BTC`（每个币种一份）
- Score: Unix 时间戳（秒）
- Member: 价格 JSON 字符串
- 保留最近 24 小时数据

## 可靠性设计

- WebSocket 断线自动重连
- 定时任务与网络请求均带异常捕获
- 统一使用 UTC 时间戳/时间
- 价格统一保留 2 位小数
- 日志输出关键任务状态

## 常见排查

1. Redis 连接失败：检查 `REDIS_URL` 与 Redis 服务状态。
2. 无实时价格：检查网络是否可访问 Binance。
3. 无新闻数据：检查 RSS 源地址是否可访问。
