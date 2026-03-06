# Crypto Web - 部署指南

## 🚀 快速开始（Docker 一键启动）

### 方式一：开发模式（适合调试）

```bash
cd ~/AgentWork/cryptoweb

# 启动所有服务
docker-compose up --build

# 后台运行
docker-compose up -d --build
```

访问地址：
- 前端：http://你的服务器IP:5173
- 后端 API：http://你的服务器IP:8000
- 健康检查：http://你的服务器IP:8000/api/health

### 方式二：生产模式（推荐）

```bash
# 修改 docker-compose.yml，注释掉 frontend-dev，取消注释 frontend 和 nginx
# 或者使用下面的命令

docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 🌐 公网访问配置

### 方案 A：直接使用 IP + 端口（最简单）

如果你的服务器有公网 IP，直接开放端口即可：

```bash
# 检查防火墙﻿
sudo ufw status

# 允许端口
sudo ufw allow 5173/tcp  # 前端开发端口
sudo ufw allow 8000/tcp  # 后端 API 端口
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
```

然后访问：http://你的服务器IP:5173

### 方案 B：使用 Nginx 反向代理（推荐）

配置 Nginx 来代理到 Docker 容器：

```nginx
# /etc/nginx/sites-available/crypto-web
server {
    listen 80;
    server_name your-domain.com;  # 或者你的服务器IP

    # 前端静态文件
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # API 代理
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket 代理
    location /socket.io/ {
        proxy_pass http://localhost:8000/socket.io/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/crypto-web /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 方案 C：使用域名 + HTTPS（最佳实践）

需要：
1. 一个域名（如 crypto.example.com）
2. 域名 A 记录指向服务器 IP
3. 申请 SSL 证书（Let's Encrypt）

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 申请证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

---

## 📋 常用命令

```bash
# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend-dev
docker-compose logs -f data-crawler

# 重启服务
docker-compose restart

# 停止所有服务
docker-compose down

# 完全重建（包括镜像）
docker-compose down --rmi all
docker-compose up -d --build

# 进入容器调试
docker exec -it crypto-backend /bin/bash
docker exec -it crypto-redis redis-cli
```

---

## 🔧 手动部署（不用 Docker）

如果服务器没有 Docker，可以手动部署：

### 1. 安装 Redis
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl enable redis
sudo systemctl start redis
```

### 2. 部署后端
```bash
cd ~/AgentWork/cryptoweb/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 使用 systemd 或 screen/tmux 后台运行
screen -S backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
# Ctrl+A+D  detach
```

### 3. 部署数据爬虫
```bash
cd ~/AgentWork/cryptoweb/data
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

screen -S crawler
python main.py
# Ctrl+A+D  detach
```

### 4. 部署前端
```bash
cd ~/AgentWork/cryptoweb/frontend
npm install
npm run build

# 用 serve 或 nginx 托管
npm install -g serve
serve -s dist -l 5173
```

---

## 🔒 安全建议

1. **防火墙**：只开放必要端口（80, 443, 8000）
2. **CORS**：修改 backend/app/main.py 中的 CORS 配置，只允许你的域名
3. **Rate Limiting**：后端添加请求频率限制
4. **环境变量**：生产环境敏感信息用环境变量，不要硬编码

---

## 🐛 故障排查

### 前端无法连接后端
检查 CORS 配置，确保 `CORS_ORIGINS` 包含前端地址

### WebSocket 连接失败
检查防火墙是否放行 WebSocket 端口，Nginx 配置是否有 `Upgrade` header

### Redis 连接失败
检查 Redis 是否运行：`docker-compose ps` 或 `redis-cli ping`

### 数据不更新
检查数据爬虫日志：`docker-compose logs -f data-crawler`

---

## 📊 性能优化

- 使用 CDN 加速静态资源
- 启用 Redis 持久化
- 后端添加缓存层
- 使用 PM2 管理 Node 进程（生产环境）

---

*部署遇到问题随时问我！*
