---
title: "Ubuntu 22.04/24.04 配置 SSH 和远程桌面完整指南"
date: 2026-05-25 10:00:00
updated: 2026-05-25 10:00:00
categories: 运维
tags:
  - Ubuntu
  - SSH
  - xrdp
  - 远程桌面
  - XFCE
---

# Ubuntu 22.04/24.04 配置 SSH 和远程桌面完整指南

本教程适用于 Ubuntu 22.04 及 24.04 新装系统，提供一键脚本和详细说明，帮助你快速开启 SSH 远程管理以及 xrdp 远程桌面（支持 Windows 自带「远程桌面连接」）。

---

## 一、配置 SSH（安全外壳协议）

### 1. 一键安装并开启 SSH 服务

```bash
sudo apt update
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
```

### 2. 验证 SSH 是否运行成功

```bash
sudo systemctl status ssh
```

当看到 `active (running)` 字样，说明 SSH 服务已正常启动。

### 3. 防火墙放行 SSH（Ubuntu 默认使用 ufw）

```bash
sudo ufw allow ssh
sudo ufw reload
```

### 4. 查看本机 IP 地址

```bash
hostname -I
# 或
ip a
```

记录下你的内网 IP（例如 `192.168.1.100`），用于远程连接。

### 5. 远程连接命令（Windows / macOS / Linux 通用）

```bash
ssh 你的用户名@服务器IP
# 示例：ssh zhang@192.168.1.100
```

Windows 用户也可使用 PowerShell 或 CMD 直接执行上述命令。

### 6. 安全加固（强烈建议）

编辑 SSH 配置文件：

```bash
sudo nano /etc/ssh/sshd_config
```

修改以下参数：

```plaintext
PermitRootLogin no          # 禁止 root 直接登录
PasswordAuthentication no   # 禁止密码登录（需先配置好密钥）
PubkeyAuthentication yes    # 启用密钥登录
```

保存后重启 SSH 服务：

```bash
sudo systemctl restart ssh
```

> **提示**：若需要一键生成并配置免密密钥登录，可以另外参考相关教程。

---

## 二、配置 xrdp 远程桌面（支持 Windows RDP 客户端）

### 方案一：使用 GNOME 桌面（可能存在黑屏问题，需额外处理）

#### 1. 安装 xrdp 和 GNOME 桌面

```bash
sudo apt update
sudo apt install -y xrdp ubuntu-desktop
```

#### 2. 添加用户权限

```bash
sudo usermod -aG ssl-cert $USER
```

#### 3. 配置 GNOME 兼容 xrdp

```bash
echo "gnome-session" > ~/.xsession
sudo systemctl restart xrdp
```

#### 4. 防火墙放行 3389 端口（RDP 默认端口）

```bash
sudo ufw allow 3389/tcp
sudo ufw reload
```

#### 5. 连接测试

- 查看 IP：`hostname -I`
- Windows 按 `Win+R`，输入 `mstsc` 打开远程桌面连接，输入 Ubuntu 的 IP 地址，然后使用你的系统用户名和密码登录。

#### 6. 解决 GNOME + xrdp 黑屏 / 灰色背景问题

Ubuntu 22.04+ 自带的远程桌面服务（GNOME Remote Desktop）会与 xrdp 抢占 3389 端口，导致 xrdp 连接后黑屏。需要**彻底关闭自带服务**：

```bash
# 1. 禁用自带 RDP/VNC 配置
gsettings set org.gnome.desktop.remote-desktop.rdp enable false
gsettings set org.gnome.desktop.remote-desktop.vnc enable false

# 2. 停止当前服务
systemctl --user stop gnome-remote-desktop

# 3. 禁止开机自启
systemctl --user disable gnome-remote-desktop

# 4. 确认 3389 端口已被 xrdp 占用（没有其他进程）
ss -tulnp | grep 3389

# 5. 检查进程是否残留
ps -ef | grep gnome-remote
```

执行完毕后重启 xrdp：

```bash
sudo systemctl restart xrdp
```

此时再尝试 RDP 连接，应该能正常进入 GNOME 桌面。

---

### 方案二：直接换装 XFCE 桌面（彻底避免兼容性问题，推荐）

如果 GNOME 下仍然出现问题，或者你希望一个轻量、稳定的远程桌面体验，可以安装 XFCE 桌面环境。

```bash
# 1. 安装 xfce4 和 xrdp 支持包
sudo apt install -y xfce4 xfce4-goodies xorgxrdp

# 2. 写入 xfce 会话启动文件
echo "startxfce4" > ~/.xsession
chmod +x ~/.xsession

# 3. 重启 xrdp 服务
sudo systemctl restart xrdp
```

之后使用 Windows 远程桌面连接，登录时**会话类型选择 Xorg**，输入用户名密码即可进入正常的 XFCE 桌面。

> **注意**：如果之前安装过 GNOME 并尝试过方案一，建议先卸载 `ubuntu-desktop`（可选，非必需），但安装 xfce4 后两个桌面环境可以共存，登录时选择即可。

---

## 三、总结

| 服务 | 端口 | 关键命令 | 常见问题 |
|------|------|----------|----------|
| SSH | 22 | `sudo systemctl enable --now ssh` | 防火墙未放行 / 密码错误 |
| xrdp (GNOME) | 3389 | 关闭自带远程桌面服务 | 黑屏 / 灰色背景 |
| xrdp (XFCE) | 3389 | `echo "startxfce4" > ~/.xsession` | 几乎无兼容问题 |

按照以上步骤操作，你可以在 Ubuntu 22.04/24.04 上快速获得可用的 SSH 远程管理和稳定可靠的远程桌面服务。如果遇到任何问题，欢迎查阅系统日志（`journalctl -u xrdp` 或 `/var/log/xrdp.log`）进行排查。
