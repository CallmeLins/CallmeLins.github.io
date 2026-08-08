---
title: "Vaultwarden + AList WebDAV 加密备份完整指南"
date: 2026-08-08
categories: 运维
tags: [Vaultwarden, Docker, AList, WebDAV, 备份, NAS, Rclone]
---

> **适用环境**：飞牛 NAS / Debian 系系统 · Docker 部署 Vaultwarden · AList WebDAV 异地备份
> **核心功能**：无缝迁移旧 Vaultwarden 密码库数据 + 每日定时自动加密备份至 115 网盘 + 备份成败邮件通知
> **关键原理**：采用容器 Host 网络模式解决 Docker 容器无法访问宿主机 AList 的问题，不挂载网盘、纯容器直传备份，稳定无故障

## 前言

Bitwarden 自托管方案 **Vaultwarden** 以轻量、低资源占用著称，是很多人在 NAS 上托管密码库的首选。但「数据在自己手里」的另一面是——**备份全靠自己**。一旦容器损坏、磁盘故障或 NAS 失窃，密码库就可能永久丢失。

本文记录一套在飞牛 NAS / Debian 系系统上的完整方案：

- 复用旧 Vaultwarden 容器的数据目录，**零迁移**衔接历史密码库；
- 用 `ttionya/vaultwarden-backup` 容器每日定时把数据**加密压缩**后直传到 AList 挂载的 115 网盘；
- 备份成功 / 失败均通过 QQ 邮箱 SMTP **双向通知**，异常第一时间感知。

整套方案最大的坑是「Docker 容器默认桥接网络下访问不到宿主机 AList 的 `127.0.0.1:5255`」，本文用 `network_mode: host` 一招解决，无需修改 Rclone 远端 IP、无需把网盘挂进容器，长期运行稳定无故障。

<!-- more -->

## 一、前期准备

### 1.1 环境依赖

- Docker & Docker Compose 已正常安装运行
- AList 已部署，开启 WebDAV 服务（默认端口 `5255`），可宿主机本地访问
- 旧版 Vaultwarden 容器及数据目录存在（`/vol1/1000/Docker/vaultwarden`）
- 可用邮箱（本文以 QQ 邮箱为例，支持 SMTP 授权码登录）

### 1.2 核心路径说明

- **Vaultwarden 旧数据目录**：`/vol1/1000/Docker/vaultwarden`（直接复用，无需迁移复制）
- **Rclone 配置文件路径**：`/home/Hao/.config/rclone/rclone.conf`
- **备份存储远端**：AList 115 网盘目录 `/115网盘/001_资料`
- **Vaultwarden 访问端口**：`51998`（沿用旧端口，客户端无需重新配置）

## 二、Rclone 配置 AList WebDAV 远端

### 2.1 安装 Rclone

系统已预装可跳过，未安装执行官方一键安装脚本：

```bash
curl https://rclone.org/install.sh | sudo bash
```

### 2.2 新建 AList WebDAV 远端

进入 Rclone 配置界面：

```bash
rclone config
```

按照以下步骤逐项配置：

1. 创建新远端：输入 `n`
2. 远端名称：输入 `openlist`（后续备份服务固定调用此名称）
3. 存储类型：输入 `webdav`
4. WebDAV 地址：`http://127.0.0.1:5255/dav`
5. 服务商类型：输入 `other`
6. 用户名：填写你的 AList 登录账号
7. 密码：输入 AList 登录密码（加密保存）
8. Bearer 令牌：直接回车留空
9. 高级配置：输入 `n` 跳过
10. 保存配置：输入 `y` 确认，最后 `q` 退出配置界面

### 2.3 验证 Rclone 远端连通性

必须带冒号，否则会识别为本地目录：

```bash
rclone lsd openlist:
```

正常输出 AList 根目录文件即为配置成功。

## 三、停止旧 Vaultwarden 容器（关键步骤）

SQLite 数据库不支持多进程同时读写，必须彻底停止旧容器，防止数据库损坏：

```bash
# 停止旧容器
sudo docker stop vaultwarden

# 删除旧容器（仅删容器，保留本地数据目录）
sudo docker rm vaultwarden

# 校验数据库无进程占用（无输出即为正常）
sudo fuser -v /vol1/1000/Docker/vaultwarden/db.sqlite3* 2>&1
```

## 四、生成 Vaultwarden 后台管理密钥

终端执行命令生成随机安全 `ADMIN_TOKEN`：

```bash
openssl rand -base64 48
```

复制输出的完整字符串，后续填入配置文件，用于后台 `/admin` 登录。

## 五、完整 Docker Compose 配置文件

### 5.1 创建部署目录

```bash
sudo mkdir -p /vol1/1000/Docker/vaultwarden-compose
cd /vol1/1000/Docker/vaultwarden-compose
```

### 5.2 编写 docker-compose.yml

新建文件并填入以下完整配置，替换文中 **自定义占位符**：

```yaml
version: '3'

services:
  # 主服务：Vaultwarden 密码库
  vaultwarden:
    image: vaultwarden/server:latest
    container_name: vaultwarden
    restart: unless-stopped
    ports:
      - "51998:80" # 沿用旧端口，客户端无需修改配置
    volumes:
      # 直接复用旧数据目录，无缝迁移所有密码数据
      - /vol1/1000/Docker/vaultwarden:/data
    environment:
      TZ: "Asia/Shanghai"
      WEBSOCKET_ENABLED: "true" # 开启设备实时同步

      # 安全策略配置
      SIGNUPS_ALLOWED: "false"   # 禁止陌生人注册
      INVITATIONS_ALLOWED: "false" # 禁止邀请注册
      SHOW_PASSWORD_HINT: "false" # 关闭密码提示

      # 后台管理密钥（替换为openssl生成的密钥）
      ADMIN_TOKEN: "你的随机ADMIN_TOKEN"

      # 图标缓存优化
      ICON_SERVICE: "internal"
      ICON_CACHE_TTL: "7776000"
      ICON_CACHE_NEGTTL: "259200"
      ICON_DOWNLOAD_TIMEOUT: "30"
      ROCKET_WORKERS: "20"

  # 附属服务：定时异地备份
  backup:
    image: ttionya/vaultwarden-backup:latest
    container_name: vaultwarden_backup
    restart: unless-stopped
    network_mode: host # 核心配置：使用宿主机网络，可正常访问127.0.0.1:5255
    volumes:
      # 挂载Vaultwarden原始数据目录
      - /vol1/1000/Docker/vaultwarden:/bitwarden/data
      # 挂载本地Rclone配置，读取AList远端配置
      - /home/Hao/.config/rclone/rclone.conf:/config/rclone/rclone.conf
    environment:
      TZ: "Asia/Shanghai" # 校正时区，定时任务按北京时间执行
      DATA_DIR: "/bitwarden/data"

      # 备份策略：每日4:45自动备份，保留30天备份文件
      CRON: "45 4 * * *"
      BACKUP_KEEP_DAYS: "30"

      # 备份压缩加密配置
      ZIP_ENABLE: "TRUE"
      ZIP_PASSWORD: "自定义备份压缩包密码"

      # 异地备份目标（AList 115网盘目录）
      RCLONE_REMOTE_NAME: "openlist"
      RCLONE_REMOTE_DIR: "/115网盘/001_资料"

      # 邮件通知配置（QQ邮箱SMTP）
      MAIL_SMTP_ENABLE: "TRUE"
      MAIL_ON_SUCCESS: "TRUE"
      MAIL_ON_FAILURE: "TRUE"
      SMTP_HOST: "smtp.qq.com"
      SMTP_PORT: "587"
      SMTP_USERNAME: "你的QQ邮箱@qq.com"
      SMTP_PASSWORD: "你的QQ邮箱SMTP授权码"
      MAIL_FROM: "你的QQ邮箱@qq.com"
      MAIL_TO: "接收通知的邮箱@163.com"
```

### 5.3 占位符替换说明

- **ADMIN_TOKEN**：第四步 `openssl` 生成的随机密钥
- **ZIP_PASSWORD**：自定义备份压缩包解密密码（务必妥善保存）
- **邮箱配置**：替换为自己的 QQ 邮箱及 SMTP 授权码（非登录密码）

## 六、启动服务并验证部署

### 6.1 启动整套服务

```bash
sudo docker compose up -d
```

### 6.2 查看容器运行状态

```bash
sudo docker ps
```

正常输出：`vaultwarden`、`vaultwarden_backup` 两个容器状态为 `Up`。

### 6.3 验证密码库迁移成功

浏览器访问：`http://NAS_IP:51998`，使用旧账号密码登录，确认所有密码数据、图标、缓存全部保留。

### 6.4 手动触发备份（核心验证步骤）

```bash
sudo docker exec vaultwarden_backup sh -c "/app/backup.sh"
```

执行完成后，进入 AList 115 网盘 `001_资料` 目录，查看是否生成加密压缩备份包，同时查看接收邮箱是否收到备份通知邮件。

## 七、关键优化与避坑说明

### 7.1 解决容器无法访问宿主机 AList

新增 `network_mode: host` 配置，让备份容器复用宿主机网络，可直接访问 `127.0.0.1:5255`，无需修改 Rclone 远端 IP。

### 7.2 时区校正

添加 `TZ: Asia/Shanghai`，解决容器默认 UTC 时区导致定时任务时间偏移问题，保证每日 `4:45` 北京时间准时备份。

### 7.3 数据安全保障

- 直接复用旧数据目录，零数据迁移损耗，无缝衔接
- 备份包全局加密，无明文数据泄露风险
- 自动清理 30 天前旧备份，避免网盘空间溢出
- 备份成败双向邮件通知，及时发现异常

### 7.4 常见问题排查

1. **备份上传失败**：检查 Rclone 配置文件挂载路径、`openlist` 远端连通性
2. **数据库异常**：确保旧容器彻底删除，无进程占用数据库文件
3. **定时任务不执行**：优先检查容器时区配置是否正确

## 八、参考文章

- [Linux.do · Vaultwarden 备份社区方案](https://linux.do/t/topic/1297490)
- [飞牛 NAS rclone 挂载 AList 网盘](https://mtom.top/archives/%E9%A3%9E%E7%89%9BNAS-rclone%E6%8C%82%E8%BD%BDalist%E7%BD%91%E7%9B%98/?highlight=rclone)
