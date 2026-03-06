# CryptoWeb Backend (FastAPI + Socket.IO + Redis)

一个基于 **Python 3.11+** 的后端服务，提供：
- REST API 查询价格、历史、新闻、健康状态
- Socket.IO 实时推送价格和新闻更新
- Redis 作为数据源

## 技术栈
- FastAPI
- python-socketio
- Redis
- Uvicorn

## 目录结构
```text
app/
  ├── __init__.py
  ├── main.py
  ├── socket_server.py
  ├── api.py
  ├── redis_client.py
  └── models.py
requirements.txt
README.md
DONE.txt
```

## 安装与运行
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

默认 Redis 地址：`redis://localhost:6379/0`，可通过环境变量覆盖：
```bash
export REDIS_URL=redis://localhost:6379/0
```

## CORS
已允许前端地址：`http://localhost:5173`

## Socket.IO
- 端点：`/socket.io/`
- 事件：`price_update`
```json
{
  "type": "price_update",
  "data": {
    "symbol": "BTC",
    "price": 67500.5,
    "change24h": 2.5,
    "timestamp": 1234567890
  }
}
```
- 事件：`news_update`
```json
{
  "type": "news_update",
  "data": {
    "id": "news-1",
    "title": "...",
    "source": "...",
    "url": "...",
    "publishedAt": "2026-03-06T08:00:00Z"
  }
}
```

## REST API
- `GET /api/prices` 返回所有币种当前价格
- `GET /api/prices/{symbol}` 返回指定币种价格
- `GET /api/prices/{symbol}/history?range=24h` 返回指定范围历史
- `GET /api/news` 返回最新新闻（最多20条）
- `GET /api/health` 健康检查

## Redis 数据结构
- `HGETALL crypto:prices`
  - 格式：`{ 'BTC': '{"price":67500.50,...}', ... }`
- `LRANGE crypto:news 0 19`
  - 格式：最近20条新闻 JSON 字符串
- 历史数据（本服务读取约定）：
  - `LRANGE crypto:history:{SYMBOL}:{RANGE} 0 -1`

## 日志与错误处理
- Redis 连接、API 异常、Socket 推送异常均有日志
- Redis 不可用时，API 返回 `503`（健康检查返回 `degraded`）
