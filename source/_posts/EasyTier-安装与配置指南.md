---
title: "EasyTier 安装与配置指南"
date: 2026-04-06 20:30:00
updated: 2026-04-06 20:30:00
categories: 运维
tags:
  - EasyTier
  - 内网穿透
  - 组网
---

## 一、工具简介

EasyTier 是一款轻量级内网穿透/组网工具，可快速实现多设备私有组网，操作简单、部署高效，以下是完整的安装、启动及基础配置流程。

## 二、核心命令（直接复制执行）

### 2.1 安装命令

```bash
wget -O /tmp/easytier.sh "https://raw.githubusercontent.com/EasyTier/EasyTier/main/script/install.sh" && sudo bash /tmp/easytier.sh install --gh-proxy https://ghfast.top/
```

### 2.2 启动命令（私有组网模式）

```bash
sudo easytier-core --private-mode true --network-name HAO-EASYTIER-NET --network-secret <your-network-secret>
```

## 三、命令逐行解析

### 3.1 安装命令解析

- `wget -O /tmp/easytier.sh "https://raw.githubusercontent.com/EasyTier/EasyTier/main/script/install.sh"`：从 GitHub 官方地址下载 EasyTier 安装脚本，并保存到 `/tmp` 临时目录。
- `&&`：仅当前面的下载命令执行成功后，才继续执行安装命令。
- `sudo bash /tmp/easytier.sh install`：以管理员权限执行安装脚本。
- `--gh-proxy https://ghfast.top/`：指定 GitHub 代理地址，解决国内下载缓慢或失败的问题。

### 3.2 启动命令解析

该命令用于启动 EasyTier 核心服务，采用私有组网模式，仅授权设备可加入：

- `--private-mode true`：启用私有组网模式，关闭公开节点访问，提升安全性。
- `--network-name HAO-EASYTIER-NET`：自定义组网名称，用于区分不同网络。
- `--network-secret <your-network-secret>`：组网核心密钥，其他设备要加入该网络，必须保持一致。

## 四、执行前准备

### 4.1 环境要求

- 系统：支持主流 Linux 发行版，如 Ubuntu、Debian、CentOS、Fedora。
- 依赖：系统需安装 `wget` 工具。
- 权限：执行命令的用户需拥有 `sudo` 管理员权限。

若未安装 `wget`，可按系统执行：

- Debian/Ubuntu：

```bash
sudo apt install wget -y
```

- CentOS/RHEL：

```bash
sudo yum install wget -y
```

## 五、常见问题与解决方法

### 5.1 下载脚本失败

现象：`wget` 提示无法连接、超时等错误。

解决：更换代理地址，修改安装命令中的 `--gh-proxy` 参数，备选：

- `https://ghproxy.com/`
- `https://mirror.ghproxy.com/`

### 5.2 启动后终端被占用

现象：执行启动命令后，终端无法输入其他命令，关闭终端后服务会停止。

解决：采用后台运行方式：

```bash
sudo nohup easytier-core --private-mode true --network-name HAO-EASYTIER-NET --network-secret <your-network-secret> > /var/log/easytier.log 2>&1 &
```

参数说明：

- `nohup`：让进程脱离终端独立运行。
- `> /var/log/easytier.log 2>&1`：将日志输出到文件，方便排查问题。
- `&`：将进程放入后台执行。

## 六、服务验证

启动服务后，可通过以下命令验证是否正常运行。

### 6.1 查看进程

```bash
ps aux | grep easytier-core
```

若输出中包含 `easytier-core` 相关进程，说明服务已启动。

### 6.2 查看日志（后台运行模式）

```bash
cat /var/log/easytier.log
```

若日志中无明显报错，且出现 `start success` 等提示，说明服务运行正常。

## 七、注意事项

1. 组网密钥 `--network-secret` 需妥善保管，切勿泄露。
2. 若需修改组网名称或密钥，更新命令参数后重启服务即可生效。
3. 系统重启后，后台运行的 EasyTier 服务会停止，若需开机自启，可进一步配置 `systemd` 服务。
4. 若安装或启动过程中出现其他报错，可查看 `/var/log/easytier.log` 排查。
