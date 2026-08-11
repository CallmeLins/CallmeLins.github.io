---
title: "CPA + New-API + Nginx 反代：自建 AI API 中转平台的完整部署指南"
date: 2026-07-30
updatedAt: 2026-07-30
tags: ["运维", "CPA", "New-API", "Nginx", "Docker", "中转", "Cloudflare", "AI"]
---


## 一、前言

随着国内外大模型 API 的爆发式增长，很多用户会同时使用 OpenAI、Claude、Gemini、通义千问等多个厂商的模型。每个厂商有不同的计费体系、API 地址和认证方式，管理起来非常混乱。

本文将介绍一套完整的自建 AI API 中转平台方案，通过 **CPA（CLI Proxy API）+ New-API + Nginx + Cloudflare**，实现：

- **统一 API 入口**：所有模型通过一个 OpenAI 兼容地址调用
- **管理后台**：用户管理、渠道管理、额度控制、日志审计
- **代理中间层**：支持各种上游 AI API 的协议转换和负载均衡
- **HTTPS 安全访问**：通过 Cloudflare 源证书 + Nginx 反代提供加密访问
- **多子域名隔离**：管理面板和 API 服务通过不同域名访问

> **适用场景**：个人/团队自用 AI API 聚合中转、企业内部 AI 网关、开发者测试环境。

---

## 二、架构总览

先看整体架构图，方便理解各组件之间的关系：

```
用户 → Cloudflare CDN
  → api.example.com  → Nginx → New-API (内网 3000)
  → cpa.example.com  → Nginx → CPA 管理面板 (内网 8317)
                                    → CPA API (内网 8317/v1)
```

### 服务清单

| 容器 | 镜像 | 对内端口 | 对外端口 | 用途 |
|------|------|---------|---------|------|
| nginx | nginx:alpine | 80/443 | 80/443 | HTTPS 反代 |
| new-api | calciumion/new-api:latest | 3000 | - | API 管理面板 |
| postgres | postgres:15 | 5432 | - | 数据库 |
| redis | redis:latest | 6379 | - | 缓存 |
| cpa | eceasy/cli-proxy-api:latest | 8317 | 8317(可选) | 代理中间层 |

### 请求链路（以客户端调用模型为例）

```
客户端 → https://api.example.com/v1/chat/completions
  → Cloudflare CDN（DDoS 防护 + 全球加速）
    → Nginx:443（SSL 卸载，反向代理）
      → New-API:3000（鉴权、限流、日志）
        → 调取 CPA 渠道 → http://cpa:8317/v1（协议转换）
          → CPA 处理 → 上游 AI API（如 OpenAI / Claude / Gemini）
            → 返回响应 → 原路返回
```

---

## 三、为什么选择这套方案？

在确定方案前，我对比了几种常见的中转方案：

| 方案 | 优点 | 缺点 |
|------|------|------|
| **单一 New-API** | 部署简单，自带管理面板 | 上游协议适配有限 |
| **单一 CPA** | 强大的协议转换能力 | 缺乏用户管理与鉴权 |
| **New-API + CPA** | 兼有管理和协议转换，灵活扩展 | 部署复杂度略高 |
| **商业中转服务** | 即开即用 | 费用高，数据经过第三方 |

本方案选择 **New-API + CPA** 组合的原因：

- New-API 负责**上层管理**：用户认证、额度控制、渠道管理、调用统计、日志审计
- CPA 负责**底层代理**：协议转换、流式支持、多模型适配、密钥分发
- 两者通过 Docker 内网通信，性能损耗极低

---

## 四、前置准备

### 4.1 环境要求

- 一台云服务器（推荐 2C4G 及以上）
- Ubuntu 22.04 / 24.04 LTS 或 Debian 12
- Docker 和 Docker Compose（建议 Docker 24+）
- 一个域名（已接入 Cloudflare）
- 基本的 Linux 操作能力

### 4.2 安装 Docker

```bash
# 一键安装 Docker
curl -fsSL https://get.docker.com | bash -s docker

# 安装 Docker Compose 插件
sudo apt-get install -y docker-compose-plugin

# 验证
docker --version && docker compose version
```

### 4.3 域名与 DNS

确保你的域名已接入 Cloudflare，后续需要添加 DNS A 记录。

---

## 五、Cloudflare 源服务器 SSL 证书

要让 Cloudflare 以"完全（严格）"模式与你的服务器通信，需要创建源服务器证书。

### 5.1 创建证书

1. 登录 Cloudflare 后台 → **SSL/TLS** → **源服务器（Origin Server）**
2. 点击 **创建证书**
3. **私钥类型**：默认 RSA (2048)
4. **主机名**：建议使用通配符，方便后续添加更多子域名
   - `*.example.com`
   - `example.com`
5. **有效期**：选择最长（15 年），一劳永逸
6. 点击 **创建**

### 5.2 保存证书

创建后会显示两个关键内容：

| 文件 | 对应字段 | 说明 |
|------|---------|------|
| `example.com.pem` | **源证书（Origin Certificate）** | 公钥证书 |
| `example.com.key` | **私钥（Private Key）** | ⚠️ **只显示一次，立即下载保存** |

### 5.3 设置 SSL/TLS 加密模式

创建完源证书后，在 Cloudflare **SSL/TLS** 页面将加密模式设为：

```
加密模式: 完全（严格）
```

这样 Cloudflare 会使用你上传的源证书与服务器进行 TLS 加密通信。

---

## 六、目录结构

完整的项目目录结构如下：

```
/path/to/proxy/
├── docker-compose.yml          # 统一 Docker 编排
├── cpa/                        # CPA 配置目录
│   ├── config.yaml             # CPA 配置文件（密码、API Keys）
│   ├── auths/                  # 认证文件目录
│   └── logs/                   # CPA 日志
├── newapi/                     # New-API 数据目录
│   ├── data/                   # PostgreSQL 持久化数据
│   └── logs/                   # New-API 日志
└── nginx/                      # Nginx 配置目录
    ├── nginx.conf              # Nginx 主配置
    ├── conf.d/
    │   └── api.conf            # 站点反代配置（双域名）
    ├── ssl/
    │   ├── example.com.pem     # Cloudflare 源证书
    │   └── example.com.key     # 私钥（权限 600）
    └── logs/                   # Nginx 访问/错误日志
```

创建所有目录：

```bash
mkdir -p /path/to/proxy/{cpa/{auths,logs},newapi/{data,logs},nginx/{conf.d,ssl,logs}}
```

---

## 七、核心配置文件

### 7.1 CPA 配置 (cpa/config.yaml)

CPA 是一个轻量级的 AI API 代理中间层，支持多种上游 AI 协议的转换。它的核心配置如下：

```yaml
# CPA 核心配置
port: 8317
auths-dir: /root/.cli-proxy-api

# 远程管理面板设置
remote-management:
  allow-remote: true
  secret-key: "your-admin-password"  # ⚠️ 管理面板登录密码，请修改

# API 网关密钥（New-API 渠道中使用的密钥）
api-keys:
  - "your-gateway-api-key"           # ⚠️ New-API 调用 CPA 时使用，请修改

# 日志配置
log-dir: /CLIProxyAPI/logs
log-level: info
```

> **安全提醒**：`secret-key` 和 `api-keys` 中的值务必修改为强密码，不要使用默认值。

### 7.2 docker-compose.yml（完整版）

以下是一份可直接使用的 Docker 编排文件，统一管理所有五个容器：

```yaml
services:
  new-api:
    image: calciumion/new-api:latest
    container_name: new-api
    restart: always
    command: --log-dir /app/logs
    expose:
      - '3000'
    volumes:
      - ./newapi/data:/data
      - ./newapi/logs:/app/logs
    environment:
      - SQL_DSN=postgresql://root:your-db-password@postgres:5432/new-api
      - REDIS_CONN_STRING=redis://redis
      - TZ=Asia/Shanghai
      - ERROR_LOG_ENABLED=true
      - BATCH_UPDATE_ENABLED=true
    depends_on:
      - redis
      - postgres
      - cpa
    healthcheck:
      test: ["CMD-SHELL", "wget -q -O - http://localhost:3000/api/status | grep -o '\"success\":\\s*true' || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - newapi-network

  redis:
    image: redis:latest
    container_name: redis
    restart: always
    networks:
      - newapi-network

  postgres:
    image: postgres:15
    container_name: postgres
    restart: always
    environment:
      POSTGRES_USER: root
      POSTGRES_PASSWORD: your-db-password  # ⚠️ 与 SQL_DSN 中的密码一致
      POSTGRES_DB: new-api
    volumes:
      - pg_data:/var/lib/postgresql/data
    networks:
      - newapi-network

  cpa:
    image: eceasy/cli-proxy-api:latest
    container_name: cpa
    ports:
      - '8317:8317'    # 可选：从外部直接访问管理面板
    volumes:
      - ./cpa/config.yaml:/CLIProxyAPI/config.yaml
      - ./cpa/auths:/root/.cli-proxy-api
      - ./cpa/logs:/CLIProxyAPI/logs
    restart: always
    networks:
      - newapi-network

  nginx:
    image: nginx:alpine
    container_name: nginx
    restart: always
    ports:
      - '80:80'
      - '443:443'
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./nginx/logs:/var/log/nginx
    depends_on:
      - new-api
    networks:
      - newapi-network

volumes:
  pg_data:

networks:
  newapi-network:
    driver: bridge
```

### 7.3 Nginx 主配置 (nginx/nginx.conf)

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100m;

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript
               application/xml+rss application/rss+xml
               font/truetype font/opentype
               application/vnd.ms-fontobject image/svg+xml;

    include /etc/nginx/conf.d/*.conf;
}
```

### 7.4 站点反代配置 (nginx/conf.d/api.conf)

> ⚠️ **重要**：CPA 和 New-API 使用不同的子域名访问，不能共用同一域名下的子路径。原因是 CPA 前端 JS 使用绝对路径请求 API，子路径方式会导致 API 请求路由错误。

```nginx
# ==========================================
# New-API - api.example.com
# ==========================================
server {
    listen 80;
    server_name api.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    http2 on;
    server_name api.example.com;

    ssl_certificate /etc/nginx/ssl/example.com.pem;
    ssl_certificate_key /etc/nginx/ssl/example.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 100m;

    location / {
        proxy_pass http://new-api:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 支持（New-API 的日志流等需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
}

# ==========================================
# CPA 管理面板 - cpa.example.com
# ==========================================
server {
    listen 80;
    server_name cpa.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    http2 on;
    server_name cpa.example.com;

    ssl_certificate /etc/nginx/ssl/example.com.pem;
    ssl_certificate_key /etc/nginx/ssl/example.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://cpa:8317;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
}
```

---

## 八、启动服务

所有配置文件准备就绪后，启动服务：

```bash
cd /path/to/proxy

# 上传证书文件后设置私钥权限
chmod 600 nginx/ssl/example.com.key

# 启动所有容器
docker compose up -d
```

### 验证容器状态

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

期望输出（5 个容器全部运行，状态为 Up）：

```
NAMES      STATUS                        PORTS
nginx      Up                            0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
new-api    Up (healthy)                  3000/tcp
postgres   Up                            5432/tcp
redis      Up                            6379/tcp
cpa        Up                            0.0.0.0:8317->8317/tcp
```

### 验证 Nginx 配置

```bash
docker exec nginx nginx -t && docker exec nginx nginx -s reload
```

### 验证域名访问

```bash
# 测试 New-API
curl -I https://api.example.com

# 测试 CPA 管理面板
curl -I https://cpa.example.com/management.html
```

---

## 九、New-API 初始化配置

### 9.1 注册管理员账号

打开浏览器访问 **https://api.example.com**，系统会跳转到初始化注册页面：

- **用户名**：建议使用 `root` 或 `admin`
- **密码**：设置强密码（建议 16 位以上，包含大小写字母、数字和特殊字符）

### 9.2 修改管理员密码（可选）

如果你需要通过 API 修改密码，可以使用以下命令：

```bash
# 登录获取 Token
TOKEN=$(curl -s -X POST http://localhost:3000/api/user/login \
  -H "Content-Type: application/json" \
  -d '{"username": "root", "password":"你的初始密码"}' | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',''))")

# 修改密码
curl -s -X PUT http://localhost:3000/api/user/self \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"password":"你的新密码"}'
```

### 9.3 了解 New-API 管理面板

登录后，你会看到以下核心功能模块：

- **仪表盘**：整体运行状态、请求量统计
- **渠道**：管理上游 API 渠道（CPA、OpenAI、Claude 等）
- **令牌**：管理 API Key，分配额度
- **日志**：查看各渠道的调用日志
- **用户**：管理多用户访问

---

## 十、CPA 与 New-API 联动配置

这是最关键的步骤——让 New-API 通过 CPA 渠道调用上游 AI 模型。

### 10.1 在 CPA 管理面板中添加 API Key

1. 访问 CPA 管理面板 **https://cpa.example.com/management.html**
2. 使用 `config.yaml` 中 `secret-key` 设置的密码登录
3. 进入 **API 密钥列表** → **添加 API Key**
4. 生成并复制该 Key（后续在 New-API 渠道中使用）

### 10.2 在 New-API 中添加 CPA 渠道

1. 登录 **https://api.example.com**
2. 进入 **渠道** → **添加渠道**
3. 填写以下信息：

| 字段 | 值 | 说明 |
|------|-----|------|
| 类型 | `OpenAI` | CPA 提供 OpenAI 兼容 API |
| 名称 | `CPA-渠道` | 可自定义 |
| Base URL | `http://cpa:8317/v1` | Docker 内网地址，直接用容器名通信 |
| 密钥 | 上一步生成的 API Key | CPA 网关密钥 |

### 10.3 添加模型

在渠道的**模型**字段中，填写 CPA 支持的所有模型名称，用逗号分隔：

```
gpt-4o,gpt-4o-mini,claude-sonnet-4,claude-3-5-sonnet,
gemini-2.5-pro,gemini-2.5-flash,gemini-2.0-flash,
deepseek-chat,deepseek-reasoner
```

> 具体支持的模型取决于你的 CPA 版本和上游 API 配置。

### 10.4 测试链路

在 New-API 渠道列表页，点击该渠道的 **测试** 按钮，返回成功即表示联动正常。

---

## 十一、Cloudflare DNS 配置

### 11.1 添加 A 记录

在 Cloudflare DNS 设置中添加以下记录：

| 类型 | 名称 | 值 | 代理状态 |
|------|------|-----|---------|
| A | `api` | 你的服务器 IP | 开启（橙色云）|
| A | `cpa` | 你的服务器 IP | 开启（橙色云）|

> **橙色云**表示启用 Cloudflare CDN 代理，可以隐藏源服务器 IP，提供 DDoS 防护和全球加速。
> 如果只是测试，也可以先关闭代理（灰色云），用 Cloudflare 仅做 DNS 解析。

### 11.2 后续添加更多子域名

按照相同模式添加即可，Nginx 侧对应增加 server block，目录结构不变。

---

## 十二、防火墙与安全配置

### 12.1 云服务商安全组

在云服务商控制台的安全组/防火墙中添加入站规则：

| 端口 | 协议 | 用途 | 建议 |
|------|------|------|------|
| 80 | TCP | HTTP 访问 | 必须（自动跳转到 HTTPS）|
| 443 | TCP | HTTPS 加密访问 | 必须 |
| 8317 | TCP | CPA 直连（可选）| 建议不开，通过子域名访问 |
| 22 | TCP | SSH 登录 | 必须，建议修改端口或限制 IP |

### 12.2 安全建议

1. **仅开放必要端口**：日常只开 22、80、443
2. **修改默认密码**：CPA 的 `secret-key`、数据库密码、管理员密码全部修改为强密码
3. **限制 SSH 来源 IP**：仅允许已知 IP 登录
4. **开启 Cloudflare CDN 代理**：隐藏源站 IP，防止被直接攻击

---

## 十三、日常运维

### 13.1 常用命令速查

```bash
# 启动
cd /path/to/proxy && docker compose up -d

# 停止
cd /path/to/proxy && docker compose down

# 查看日志
docker logs new-api --tail 50
docker logs cpa --tail 50
docker logs nginx --tail 20

# 重启某个服务
docker compose restart new-api

# 更新镜像
docker compose pull && docker compose up -d

# 重载 Nginx 配置（修改 api.conf 后）
docker exec nginx nginx -t && docker exec nginx nginx -s reload

# 进入容器内部调试
docker exec -it cpa sh
```

### 13.2 监控与排障

**检查容器健康状态：**

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

**查看 New-API 健康检查日志：**

```bash
docker inspect new-api | jq '.[].State.Health'
```

**检查 Nginx 错误日志：**

```bash
docker exec nginx cat /var/log/nginx/error.log | tail -20
```

**网络连通性测试（从 nginx 容器测试 new-api）：**

```bash
docker exec nginx wget -q -O - http://new-api:3000/api/status
```

### 13.3 备份数据

```bash
# 备份 PostgreSQL 数据
docker exec postgres pg_dump -U root new-api > backup/new-api-$(date +%Y%m%d).sql

# 备份整个配置目录
tar czf proxy-backup-$(date +%Y%m%d).tar.gz /path/to/proxy/{cpa,nginx,docker-compose.yml}
```

---

## 十四、常见问题排查

### Q1: CPA 管理面板添加 API Key 后前端不显示？

**原因**：通过子路径（如 `/cpa/`）反代时，CPA 前端 JS 使用绝对路径请求 API，导致请求被路由到 New-API。

**解决**：必须使用独立子域名（如 `cpa.example.com`）单独反代 CPA，不能和 New-API 共用同一域名。

### Q2: 证书不支持子域名？

**原因**：创建 Cloudflare 源证书时未包含通配符子域名。

**解决**：重新创建证书，在主机名中添加 `*.example.com`。

### Q3: New-API 渠道测试失败？

**可能原因**（按优先级排查）：

1. **CPA 容器未运行**：
   ```bash
   docker ps | grep cpa
   ```
2. **Base URL 填错**：Docker 内部通信必须用容器名 `http://cpa:8317/v1`，不要用 localhost 或外网地址
3. **网关 API Key 未配置**：先去 CPA 管理面板添加 API Key，确认 Key 值无误
4. **网络不通**：检查是否在同一 Docker 网络 `newapi-network`
   ```bash
   docker exec new-api wget -q -O - http://cpa:8317/v1/models
   ```

### Q4: 更新镜像后服务启动失败？

CPA 和 New-API 更新频繁，有时会引入不兼容变化：

```bash
# 查看容器日志定位问题
docker compose logs new-api --tail 50

# 回滚到之前版本
docker compose stop new-api
docker compose rm new-api
# 修改 docker-compose.yml 中的版本标签
docker compose up -d new-api
```

### Q5: Nginx 无法启动？

```bash
# 检查配置语法
docker exec nginx nginx -t

# 查看完整错误日志
docker logs nginx

# 常见原因：证书路径不对、端口被占用、配置文件语法错误
```

---

## 十五、进阶扩展

### 15.1 添加更多子域名服务

这套架构可以轻松扩展更多的子域名服务，例如：

- `log.example.com` → Grafana 日志面板
- `monitor.example.com` → 服务监控面板
- `doc.example.com` → API 文档站点

只需在 Nginx 的 `api.conf` 中新增 server block，并在 Cloudflare DNS 中添加对应的 A 记录即可。

### 15.2 集成 Prometheus + Grafana 监控

在 `docker-compose.yml` 中新增：

```yaml
prometheus:
  image: prom/prometheus
  ...

grafana:
  image: grafana/grafana
  ...
```

New-API 和 CPA 都支持 metrics 端点，可以接入 Prometheus 进行调用量、延迟、错误率的监控。

### 15.3 多节点部署

如果需要高可用，可以将 New-API 和 CPA 分开部署到不同服务器：

- 服务器 A：Nginx + New-API + PostgreSQL + Redis
- 服务器 B：CPA + 其他代理服务
- 通过 VPN 或专线连接内网

---

## 十六、总结

本文详细介绍了如何使用 **CPA + New-API + Nginx + Cloudflare** 构建一个完整的 AI API 中转平台。通过这套方案，你可以：

1. **统一管理**所有 AI 模型 API，一个地址搞定所有调用
2. **精细化控制**用户权限和额度，适合团队共享
3. **安全可靠**，通过 Cloudflare CDN 和源证书提供 HTTPS 加密访问
4. **易于扩展**，按需添加更多服务和子域名

整套方案全部开源且免费（除云服务器成本外），是我目前最推荐的自建中转方案。

---

> **文件索引**
>
> | 文件 | 作用 |
> |------|------|
> | `docker-compose.yml` | 定义和编排所有容器 |
> | `cpa/config.yaml` | CPA 核心配置（端口、密码、API Keys）|
> | `nginx/nginx.conf` | Nginx 主配置（日志、压缩、事件模型）|
> | `nginx/conf.d/api.conf` | 站点反代规则（双域名、HTTPS、路径转发）|
> | `nginx/ssl/*.pem` | Cloudflare 源服务器 SSL 证书 |
> | `nginx/ssl/*.key` | SSL 私钥（权限 600）|

> **版本参考**
>
> - CPA: v7.2.109
> - New-API: v1.0.0-rc.22
> - Nginx: alpine 最新版
> - Docker: 24+
> - 文档生成时间：2026-07-30
