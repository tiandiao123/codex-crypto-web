# Crypto Web 项目 - 多 Agent 协作开发文档

> 📍 工作目录：`/home/ubuntu/AgentWork/cryptoweb`
> 
> 🎯 目标：构建实时加密货币数据网站

---

## 一、整体架构

### 1.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户 (你)                                 │
│              提需求 ←────────────────→ 看结果                    │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OpenClaw (协调者/我)                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 职责：                                                   │   │
│  │ • 理解需求并拆解任务                                      │   │
│  │ • 编写接口契约文档                                        │   │
│  │ • 启动和管理 Coding Agents                               │   │
│  │ • 阶段性检查进度                                          │   │
│  │ • 发现问题时协调修复                                      │   │
│  │ • 向你汇报关键节点                                        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
    ┌─────────────────┐ ┌──────────────┐ ┌──────────────┐
    │  前端 Agent      │ │  后端 Agent   │ │  数据 Agent   │
    │  (Codex #1)      │ │  (Codex #2)   │ │  (Codex #3)   │
    │                 │ │              │ │              │
    │ • React + TS    │ │ • FastAPI    │ │ • 爬虫脚本    │
    │ • 实时价格面板   │ │ • WebSocket  │ │ • 新闻聚合    │
    │ • 新闻展示      │ │ • API 路由   │ │ • 数据清洗    │
    └─────────────────┘ └──────────────┘ └──────────────┘
```

### 1.2 数据流向

```
┌──────────┐     WebSocket      ┌──────────┐
│  Binance │ ─────────────────> │  后端    │
│  API     │                    │  Agent   │
└──────────┘                    └────┬─────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
              ┌──────────┐     ┌──────────┐     ┌──────────┐
              │  前端    │     │  缓存    │     │  新闻    │
              │  (实时   │ <── │  (Redis) │     │  RSS     │
              │  更新)   │     │          │     │          │
              └──────────┘     └──────────┘     └────┬─────┘
                                                     │
                                              ┌──────┴──────┐
                                              │   新闻源     │
                                              │ (Cointele..) │
                                              └─────────────┘
```

---

## 二、各 Agent 详细分工

### 2.1 前端 Agent (Codex #1)

**工作目录**: `~/AgentWork/cryptoweb/frontend/`

**技术栈**:
- React 18 + TypeScript
- Tailwind CSS (样式)
- Recharts (图表)
- Socket.io-client (WebSocket 客户端)

**核心功能**:
| 功能 | 描述 |
|-----|------|
| 价格面板 | 显示 BTC、ETH 等主流币实时价格 |
| 趋势图表 | 24小时价格走势图 |
| 新闻流 | 滚动显示最新加密新闻 |
| 响应式设计 | 适配桌面和移动端 |

**接口契约**:
```typescript
// WebSocket 消息格式 (后端 → 前端)
interface PriceUpdate {
  type: "price_update";
  data: {
    symbol: string;      // "BTCUSDT"
    price: number;       // 67500.50
    change24h: number;   // 2.5 (百分比)
    timestamp: number;   // Unix timestamp
  };
}

interface NewsUpdate {
  type: "news_update";
  data: {
    id: string;
    title: string;
    source: string;      // "Cointelegraph"
    url: string;
    publishedAt: string; // ISO 8601
  };
}
```

---

### 2.2 后端 Agent (Codex #2)

**工作目录**: `~/AgentWork/cryptoweb/backend/`

**技术栈**:
- Python 3.11+
- FastAPI (Web 框架)
- WebSocket (实时推送)
- Redis (数据缓存)

**核心功能**:
| 功能 | 描述 |
|-----|------|
| WebSocket 服务 | 向前端推送实时价格 |
| REST API | 提供历史数据查询 |
| 数据聚合 | 整合价格 + 新闻数据 |
| 缓存层 | Redis 缓存热点数据 |

**接口契约**:
```python
# WebSocket 端点
ws://localhost:8000/ws/prices

# REST API 端点
GET  /api/prices              # 获取所有币种当前价格
GET  /api/prices/{symbol}     # 获取指定币种价格
GET  /api/prices/{symbol}/history?range=24h  # 历史数据
GET  /api/news                # 获取最新新闻
GET  /api/health              # 健康检查
```

---

### 2.3 数据 Agent (Codex #3)

**工作目录**: `~/AgentWork/cryptoweb/data/`

**技术栈**:
- Python 3.11+
- aiohttp / websockets (异步请求)
- feedparser (RSS 解析)
- APScheduler (定时任务)

**核心功能**:
| 功能 | 描述 | 频率 |
|-----|------|------|
| 价格爬虫 | 连接 Binance WebSocket | 实时 (5秒推送) |
| 新闻聚合 | 抓取 RSS 源 | 每 15 分钟 |
| 数据清洗 | 格式化、去重 | 实时 |
| 数据存储 | 写入 Redis | 实时 |

**数据源**:
| 来源 | 用途 | 限制 |
|-----|------|------|
| Binance WebSocket | 实时价格 | 无限制，需后端转发 |
| CoinGecko API | 历史数据 | 免费版 10-30 calls/min |
| Cointelegraph RSS | 新闻 | 无限制 |
| CoinDesk RSS | 新闻备份 | 无限制 |

---

## 三、协作流程详解

### 3.1 启动流程

```
Step 1: OpenClaw 初始化项目骨架
   ├── 创建目录结构
   ├── 编写接口契约文档 (本文件)
   └── 准备环境配置

Step 2: 并行启动三个 Codex Agent
   ├── [后台进程] Codex #1 → frontend/ 目录
   ├── [后台进程] Codex #2 → backend/ 目录
   └── [后台进程] Codex #3 → data/ 目录

Step 3: 阶段性检查 (由 OpenClaw 执行)
   ├── T+10min: 检查是否启动成功，有无报错
   ├── T+30min: 检查接口契约遵循情况
   └── T+60min: 检查代码质量，准备联调

Step 4: 集成测试
   ├── 本地联调三个模块
   ├── 修复对接问题
   └── 准备部署
```

### 3.2 检查节点说明

| 检查点 | 时间 | 检查内容 |
|-------|------|---------|
| 检查 #1 | 启动后 10 分钟 | Agent 是否正常运行？有无安装报错？ |
| 检查 #2 | 启动后 30 分钟 | 接口是否遵循契约？数据结构正确吗？ |
| 检查 #3 | 启动后 60 分钟 | 代码质量如何？能否顺利对接？ |
| 最终验收 | 全部完成后 | 功能完整性、代码质量、部署就绪 |

---

## 四、OpenClaw 如何启动和管理 Agent

### 4.1 启动命令

我使用 `exec` 工具启动后台进程：

```bash
# 前端 Agent
exec pty:true background:true workdir:~/AgentWork/cryptoweb/frontend \
  command:"codex --full-auto exec '用 React + TypeScript 搭建实时价格面板...'"

# 后端 Agent  
exec pty:true background:true workdir:~/AgentWork/cryptoweb/backend \
  command:"codex --full-auto exec '用 FastAPI 搭建 WebSocket 服务...'"

# 数据 Agent
exec pty:true background:true workdir:~/AgentWork/cryptoweb/data \
  command:"codex --full-auto exec '写爬虫获取 CoinGecko/Binance 数据...'"
```

**参数说明**:
- `pty:true` - 分配伪终端，Codex 需要交互式环境
- `background:true` - 后台运行，用户关浏览器也不中断
- `workdir` - 限定工作目录，Agent 只能访问自己的"领地"
- `--full-auto` - 自动审批修改，无需人工确认

### 4.2 监控命令

```bash
# 查看所有运行中的 Agent
process action:list

# 查看某个 Agent 的输出日志
process action:log sessionId:<id>

# 查看 Agent 是否还在运行
process action:poll sessionId:<id>

# 如果需要，给 Agent 发送输入
process action:submit sessionId:<id> data:"yes"

# 紧急停止某个 Agent
process action:kill sessionId:<id>
```

### 4.3 持久化保证

即使发生以下情况，Agent 仍会继续运行：
- ✅ 你关闭浏览器
- ✅ 网络断开
- ✅ OpenClaw 会话超时

只有以下情况会中断：
- ❌ 服务器重启
- ❌ 手动 kill 进程
- ❌ Agent 自己 crash

---

## 五、项目目录结构

```
~/AgentWork/cryptoweb/
├── README.md                 # 项目总览
├── docs/
│   └── ARCHITECTURE.md       # 架构文档 (本文件)
│
├── frontend/                 # 前端 Agent 工作目录
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── backend/                  # 后端 Agent 工作目录
│   ├── app/
│   ├── requirements.txt
│   └── ...
│
└── data/                     # 数据 Agent 工作目录
    ├── crawlers/
    ├── requirements.txt
    └── ...
```

---

## 六、常见问题

### Q1: 三个 Agent 会互相干扰吗？
**不会**。每个 Agent 被限制在自己的 `workdir` 目录内，无法访问其他 Agent 的文件。

### Q2: 如果两个 Agent 需要修改同一个配置怎么办？
**由我来协调**。例如 `docker-compose.yml` 需要引用三个服务，我会：
1. 先让三个 Agent 各自完成
2. 由我整合最终的配置文件

### Q3: Agent 跑歪了怎么办？
**阶段性检查就是为了这个**。如果发现偏离需求：
- 小问题：我直接给 Agent 发指令修正
- 大问题：停止该 Agent，重新 spawn 一个

### Q4: 我想看实时进展怎么办？
随时问我：
- "前端 Agent 进度如何？"
- "有没有报错？"
- "让我看看 backend 的日志"

---

## 七、下一步行动

1. **确认方案** - 你确认这个架构和流程
2. **编写详细任务** - 我为每个 Agent 准备具体的 Prompt
3. **并行启动** - 同时启动三个 Agent
4. **阶段性检查** - 按计划检查进度

---

*文档版本: v1.0*  
*创建时间: 2026-03-06*  
*协调者: OpenClaw*
