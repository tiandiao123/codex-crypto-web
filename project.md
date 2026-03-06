# Crypto Web 项目说明（project.md）

## 1. 项目简介

Crypto Web 是一个实时加密货币数据看板，包含三部分服务：

- 前端：React + TypeScript + Vite（实时展示 BTC / ETH / SOL）
- 后端：FastAPI + Socket.IO（提供 REST API 和 WebSocket 推送）
- 数据服务：Python 爬虫（Binance 实时价格 + RSS 新闻）
- 缓存：Redis（共享价格、新闻、历史数据）

核心能力：

- 实时价格推送（`price_update`）
- 新闻推送（`news_update`）
- REST 查询（`/api/prices`、`/api/news`、`/api/health`）
- 市场指标聚合（`/api/market-metrics`）

---

## 2. 项目结构

- `frontend/`：前端页面
- `backend/`：API + Socket 服务
- `data/`：数据采集与调度
- `docker-compose.yml`：本地/服务器一键启动编排
- `docs/`：架构与部署文档

---

## 3. 运行环境要求

- Docker
- Docker Compose（`docker-compose` 或 `docker compose` 任一可用）

> 推荐 Linux / macOS。Windows 建议在 WSL2 中运行。

---

## 4. 一键启动（推荐）

在项目根目录执行：

```bash
# 旧版本命令
sudo docker-compose up -d --build

# 或新版本命令
sudo docker compose up -d --build
```

查看服务状态：

```bash
sudo docker-compose ps
```

查看日志：

```bash
sudo docker logs -f crypto-backend
sudo docker logs -f crypto-data
sudo docker logs -f crypto-frontend-dev
```

---

## 5. 访问地址

### 本机访问（在服务器本机）

- 前端：`http://localhost:5173`
- 后端健康检查：`http://localhost:8000/api/health`

### 远程访问（本地浏览器访问云服务器）

- 前端：`http://<服务器公网IP>:5173`
- 后端健康检查：`http://<服务器公网IP>:8000/api/health`

例如：

- `http://118.26.39.18:5173`
- `http://118.26.39.18:8000/api/health`

---

## 6. 启动成功判定

满足以下条件即为启动成功：

1. `docker-compose ps` 显示服务为 `Up`：
   - `crypto-redis`
   - `crypto-data`
   - `crypto-backend`
   - `crypto-frontend-dev`
2. 后端健康检查返回：

```json
{"status":"ok","redis":"up"}
```

3. `GET /api/prices` 返回 BTC/ETH/SOL 数据
4. 前端页面右上角显示 `WebSocket: 已连接`

---

## 7. 常见问题排查

### Q1：页面一直显示“WebSocket: 连接中”

优先检查：

- 后端是否正常：`curl http://127.0.0.1:8000/api/health`
- Socket 握手是否正常：
  - `curl "http://127.0.0.1:8000/socket.io/?EIO=4&transport=polling"`
- 云安全组是否放行 `5173` 和 `8000`

### Q2：本机（Mac）打不开公网地址

通常是云防火墙/安全组未放行。需要在云控制台开放入站端口：

- TCP 5173
- TCP 8000

### Q3：`docker-compose up` 报 `'ContainerConfig'`

这是旧版 docker-compose 的已知兼容问题。可先删除异常容器后再拉起：

```bash
sudo docker ps -a
sudo docker rm -f <异常容器ID>
sudo docker-compose up -d backend frontend-dev
```

### Q4：无实时数据

检查 `crypto-data` 日志是否出现：

- `Binance WebSocket 已连接`
- `新闻聚合完成`

### Q5：市场指标部分显示 `--`

可能是上游公共接口限流或短时不可用，系统会自动降级到备用源。

- 期权源：Deribit 公共 API
- 宏观主源：Yahoo Finance
- 宏观备用源：Stooq（DXY/ES/NQ）、FRED（US10Y）
- 其他：CoinGecko（BTC Dominance）、Alternative.me（Fear & Greed）

可先检查：

```bash
curl http://127.0.0.1:8000/api/market-metrics
```

若接口返回但部分字段为 `null`，通常是源站限流，等待下一轮轮询或稍后重试即可。

---

## 8. 市场指标模块说明（新增）

首页新增“市场指标（期权 + 宏观）”区域，默认每 30 秒刷新。

### 8.1 指标清单

1. 期权数据
   - BTC Call Open Interest
   - BTC Put Open Interest
   - BTC Put/Call Ratio
   - ETH Total Open Interest

2. 宏观数据
   - DXY（美元指数）
   - US10Y（10年期美债收益率）
   - ES / NQ（标普 / 纳指期货）
   - BTC Dominance
   - Fear & Greed

### 8.2 接口说明

- 路径：`GET /api/market-metrics`
- 示例返回：

```json
{
  "options": {
    "btc_call_open_interest": 277626.4,
    "btc_put_open_interest": 200388.9,
    "btc_put_call_ratio": 0.7218,
    "eth_total_open_interest": 2280329.0
  },
  "macro": {
    "dxy": { "value": 98.962, "change_pct": -0.0384 },
    "us10y": { "value": 4.09, "change_pct": null },
    "sp500_futures": { "value": 6847.75, "change_pct": 0.3223 },
    "nasdaq_futures": { "value": 25127.5, "change_pct": 0.4457 },
    "btc_dominance": 57.02,
    "fear_greed_index": 18.0
  },
  "updated_at": 1772783200
}
```

---

## 9. 停止服务

---

```bash
sudo docker-compose down
```

---

## 10. 安全建议（生产）

- 不要将 Redis（6379）暴露公网
- 使用 Nginx/HTTPS 反向代理前后端
- 将 CORS 配置收紧到实际域名
- 为容器与镜像增加版本化发布流程
