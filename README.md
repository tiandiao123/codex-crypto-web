# Crypto Web - 实时加密货币数据网站

> 🤖 这是一个由多 Agent 协作开发的项目

## 项目简介

实时展示加密货币价格和新闻动态的 Web 应用。

| 功能 | 描述 | 更新频率 |
|-----|------|---------|
| 实时价格 | BTC、ETH 等主流币价格 | 5 秒 |
| 趋势图表 | 24小时价格走势 | 实时 |
| 新闻聚合 | 加密行业最新动态 | 15 分钟 |

## 技术栈

- **前端**: React + TypeScript + Tailwind + Recharts
- **后端**: Python + FastAPI + WebSocket
- **数据**: Python 爬虫 + Redis 缓存

## 开发模式

本项目采用 **OpenClaw + 多 Codex Agent** 协作开发：

```
OpenClaw (协调者)
    ├── 前端 Agent (Codex) → frontend/
    ├── 后端 Agent (Codex) → backend/
    └── 数据 Agent (Codex) → data/
```

详细架构说明见 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

## 目录结构

```
cryptoweb/
├── docs/           # 文档
├── frontend/       # React 前端
├── backend/        # FastAPI 后端
└── data/           # 爬虫和数据处理
```

## 快速开始

> 待 Agent 开发完成后补充

---

*多 Agent 协作开发中...*
