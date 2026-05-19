---
title: "Mac tmux + SSH 完整使用指南（含免密登录配置）"
date: 2026-04-06 20:20:00
updated: 2026-04-06 20:20:00
categories: 运维
tags:
  - tmux
  - SSH
  - Mac
---

本文整合 Mac 端 tmux 常用操作、SSH 连接配置、密钥免密登录全流程，适配 Ghostty/iTerm2 终端，解决 SSH 连接卡顿、断连、密码输入繁琐等问题，适合日常开发、远程运维使用。

## 一、基础环境安装（Mac 本地）

### 1.1 安装 tmux

使用 Homebrew 安装：

```bash
brew install tmux
```

### 1.2 安装终端（推荐 Ghostty）

替代 Termius，选择 Apple Silicon 原生、GPU 加速的 Ghostty：

```bash
brew install --cask ghostty
```

备选 iTerm2：

```bash
brew install --cask iterm2
```

### 1.3 远程服务器安装 tmux（可选）

若需在远程服务器使用 tmux，登录服务器后执行（以 Ubuntu/Debian 为例）：

```bash
sudo apt update && sudo apt install tmux -y
```

## 二、tmux 核心常用功能（Mac 本地 + 远程通用）

### 2.1 tmux 基础操作（会话管理）

tmux 核心是“会话”，断开连接后会话仍在后台运行，可随时重连：

- `tmux new -s 会话名`：新建命名会话，例如 `tmux new -s my_session`
- `tmux ls`：查看所有后台会话
- `tmux attach -t 会话名`：重连指定会话，简写 `tmux a -t 会话名`
- `tmux detach`：分离当前会话，快捷键 `Ctrl+b` 然后按 `d`
- `tmux kill-session -t 会话名`：关闭指定会话
- `tmux kill-server`：关闭所有 tmux 会话
- `tmux rename-session -t 旧会话名 新会话名`：重命名会话

### 2.2 tmux 快捷键（前缀：Ctrl+b）

所有快捷键需先按 `Ctrl+b`，再按对应按键：

会话管理快捷键：

- `Ctrl+b d`：分离当前会话
- `Ctrl+b s`：列出所有会话，按方向键选择切换
- `Ctrl+b $`：重命名当前会话

窗口/窗格管理快捷键：

- `Ctrl+b c`：新建窗口
- `Ctrl+b n`：切换到下一个窗口
- `Ctrl+b p`：切换到上一个窗口
- `Ctrl+b %`：垂直分屏
- `Ctrl+b "`：水平分屏
- `Ctrl+b 方向键`：在不同窗格间切换
- `Ctrl+b x`：关闭当前窗格

其他常用快捷键：

- `Ctrl+b [`：进入复制模式
- `Ctrl+b ?`：查看所有 tmux 快捷键

## 三、SSH 连接配置（重点：免密登录 + 防断连）

### 3.1 SSH 配置文件编写（`~/.ssh/config`）

通过配置文件，可实现“一键登录”，无需每次输入 IP、端口、用户名，同时配置防断连、连接复用。下面使用占位示例：

步骤 1：编辑配置文件

```bash
vim ~/.ssh/config
```

步骤 2：粘贴配置

```sshconfig
# 远程服务器配置（命名：my-server，便于记忆）
Host my-server
  HostName <your-server-ip>
  User root
  Port <your-ssh-port>
  IdentityFile ~/.ssh/id_ed25519
  ServerAliveInterval 60
  ServerAliveCountMax 3
  ControlMaster auto
  ControlPath ~/.ssh/cm-%r@%h:%p
  ControlPersist 10m
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
  ProxyCommand none
```

步骤 3：保存退出

在 Vim 中按 `Esc`，输入 `:wq` 后回车。

### 3.2 密钥免密登录配置（无需输入密码）

步骤 1：生成本地密钥

```bash
ssh-keygen -t ed25519
```

生成后，本地会出现两个文件：

- `~/.ssh/id_ed25519`：私钥，不可泄露
- `~/.ssh/id_ed25519.pub`：公钥，可上传到服务器

步骤 2：上传公钥到远程服务器

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub -p <your-ssh-port> root@<your-server-ip>
```

执行后输入服务器密码，上传成功后即可使用密钥登录。

步骤 3：验证免密登录

```bash
ssh my-server
```

### 3.3 手动上传公钥（备用方案）

若 `ssh-copy-id` 执行失败，可手动上传：

1. 复制本地公钥内容：

```bash
cat ~/.ssh/id_ed25519.pub
```

2. 密码登录服务器：

```bash
ssh -p <your-ssh-port> root@<your-server-ip>
```

3. 在服务器上执行：

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo "复制的公钥内容" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
exit
```

4. 重试免密登录：

```bash
ssh my-server
```

## 四、tmux + SSH 组合使用（高效远程工作流）

结合 tmux 和 SSH，可实现“断开连接后保留任务”。

### 4.1 方案 1：远程启动 tmux 会话（推荐）

1. 登录服务器：

```bash
ssh my-server
```

2. 启动 tmux 会话：

```bash
tmux new -s server_session
```

3. 执行任务：

```bash
python test.py
```

4. 分离会话：按 `Ctrl+b`，再按 `d`

5. 下次重连：

```bash
tmux attach -t server_session
```

### 4.2 方案 2：本地 tmux + SSH（多窗口分屏）

1. 本地启动 tmux 会话：

```bash
tmux new -s local_session
```

2. 分屏：

- 垂直分屏：`Ctrl+b %`
- 水平分屏：`Ctrl+b "`

3. 在任意窗格登录服务器：

```bash
ssh my-server
```

4. 本地分离会话：`Ctrl+b` 然后按 `d`

5. 下次重连本地会话：

```bash
tmux attach -t local_session
```

## 五、常见问题排查（避坑指南）

### 5.1 SSH 连接报错：`Connection closed by 127.0.0.1 port 10808`

原因：SSH 被强制走本地代理，而代理未启动或端口错误。

解决方案：

- 配置文件中添加 `ProxyCommand none`
- 或临时清空代理环境变量：

```bash
unset http_proxy https_proxy all_proxy
```

### 5.2 `ssh-copy-id` 报错：`Connection refused port 22`

原因：未指定实际 SSH 端口。

解决方案：

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub -p <your-ssh-port> root@<your-server-ip>
```

### 5.3 免密登录失败，仍提示输密码

原因：服务器端 `.ssh` 目录或 `authorized_keys` 文件权限错误。

解决方案：

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### 5.4 tmux 中文乱码

在本地 `~/.tmux.conf` 文件中添加：

```tmux
set -g utf8 on
set -g status-utf8 on
```

保存后重启 tmux：

```bash
tmux kill-server && tmux new -s my_session
```

## 六、总结

- `tmux`：后台会话、多窗格分屏，解决远程任务断连问题。
- SSH 配置：一键登录、防断连、连接复用，提升登录效率。
- 免密登录：替代密码输入，更安全也更便捷。

按本文步骤配置后，可实现 `ssh my-server` 一键免密登录服务器，并用 tmux 保留后台任务。
