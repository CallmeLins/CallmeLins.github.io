---
title: UV 完全使用教程（从入门到精通）
date: 2026-05-09
categories: 开发工具
tags: [Python, UV, 包管理, 虚拟环境]
---

> 原文：[UV 完全使用教程（从入门到精通，新手也能轻松上手） - CSDN](https://blog.csdn.net/weixin_42475060/article/details/160434523)

## 前言

Python 开发中总被环境冲突、包安装缓慢、多版本切换麻烦等问题困扰？**UV** 就是这些痛点的一站式解决方案。

UV 是一款轻量、高速的 Python 包与环境管理工具，兼容 pip、virtualenv、pyenv 等传统工具，无需额外依赖，能快速实现 Python 版本管理、虚拟环境创建、包管理及项目初始化，实测比 pip 快 **10 倍以上**。

<!-- more -->

## 一、UV 核心功能

在开始实操前，先明确 UV 的核心功能：

- ✅ **版本管理**：无需 pyenv，一键下载、安装、切换多个 Python 版本（支持 CPython、PyPy）
- ✅ **虚拟环境**：快速创建、激活、退出虚拟环境，隔离不同项目依赖
- ✅ **包管理**：替代 pip，安装、升级、卸载、导出，下载速度更快、依赖解析更精准
- ✅ **高效便捷**：全局缓存依赖包，减少磁盘占用；无需提前安装 Python
- ✅ **多平台兼容**：完美支持 macOS、Linux、Windows 三大系统

## 二、安装 UV

### macOS

推荐使用 Homebrew 安装（最稳定，无报错）：

```bash
brew install uv
```

### Linux

优先尝试官方脚本，报错则切换备用方式：

```bash
# 方案1：官方脚本
curl -LsSf https://astral.sh/uv/install.sh | sh

# 方案2：备用安装
wget -qO- https://astral.sh/uv/install.sh | sh
```

### Windows

Windows 11 及以上推荐使用 Winget：

```powershell
# 方案1：Winget 安装（推荐）
winget install uv

# 方案2：官方脚本
irm https://astral.sh/uv/install.ps1 | iex

# 方案3：备用脚本
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 安装验证

```bash
uv --version
```

输出示例：

```
uv 0.8.14 (Homebrew 2025-08-28)
```

> 若提示「uv 不是内部或外部命令」，检查环境变量。macOS/Linux 可执行 `source $HOME/.local/bin/env` 刷新环境变量。

## 三、核心功能实操

### 3.1 Python 版本管理

#### 查看可用版本

```bash
uv python list
```

#### 安装特定版本

```bash
# 安装最新稳定版 Python 3.12
uv python install 3.12

# 安装指定具体版本
uv python install 3.11.6

# 安装 PyPy 版本
uv python install pypy3.10
```

#### 设置全局默认版本

```bash
uv python default 3.12
```

验证：

```bash
python --version
```

#### 固定项目版本

在项目根目录执行，会生成 `.python-version` 文件：

```bash
uv python pin 3.11
```

### 3.2 虚拟环境管理

#### 创建虚拟环境

```bash
# 创建默认名称 (.venv) 的虚拟环境（推荐）
uv venv

# 指定 Python 版本
uv venv --python 3.11 .venv

# 自定义名称
uv venv --python 3.12 .venv312

# 指定本地 Python 路径（Windows 专用）
uv venv --python "C:\Python311\python.exe" .venv
```

#### 激活虚拟环境

激活后，终端提示符前会出现 `(.venv)` 标识：

```bash
# macOS/Linux
source .venv/bin/activate

# Windows (CMD/PowerShell)
.venv\Scripts\activate
```

#### 验证激活

```bash
python -VV
```

#### 退出虚拟环境

```bash
deactivate
```

### 3.3 包管理

#### 安装包

```bash
# 安装最新版本
uv pip install requests

# 安装指定版本
uv pip install requests==2.31.0

# 从 requirements.txt 批量安装
uv pip install -r requirements.txt

# 安装开发依赖
uv pip install --dev pytest
```

#### 升级与卸载

```bash
# 升级指定包
uv pip upgrade requests

# 升级所有包
uv pip upgrade --all

# 卸载包
uv pip uninstall requests
```

#### 导出依赖

```bash
# 导出全部依赖
uv pip freeze > requirements.txt

# 仅导出生产依赖
uv pip freeze --production > requirements.txt
```

#### 指定国内镜像源

```bash
uv pip install requests -i https://mirrors.aliyun.com/pypi/simple/
```

## 四、进阶技巧

### 4.1 清理缓存

```bash
uv cache clean
```

### 4.2 卸载 UV

```bash
# 1. 清理缓存和相关文件
uv cache clean
rm -r "$(uv python dir)"
rm -r "$(uv tool dir)"

# 2. 删除二进制文件（macOS/Linux）
rm ~/.local/bin/uv ~/.local/bin/uvx

# 2. 删除二进制文件（Windows）
rm $HOME\.local\bin\uv.exe
rm $HOME\.local\bin\uvx.exe
```

### 4.3 项目初始化

```bash
uv init my_project
cd my_project
```

自动生成 `pyproject.toml` 等规范文件。

## 五、常见问题

### 问题1：安装后提示「命令不存在」

检查环境变量。macOS/Linux 执行 `source $HOME/.local/bin/env` 刷新，Windows 重启终端或手动添加 UV 路径到环境变量。

### 问题2：官方脚本安装提示「invalid link」

切换到对应系统的备用安装方案（macOS 用 Homebrew，Windows 用 Winget）。

### 问题3：激活虚拟环境后安装的包退出后消失

这是正常现象——包仅安装在当前虚拟环境中。重新激活对应环境即可。

### 问题4：安装 Python 版本时下载缓慢

指定国内镜像源，或检查网络连接。

## 六、总结

UV 作为一站式 Python 环境与包管理工具，凭借高速、简洁、兼容的特点，完美解决了传统工具的痛点。建议新手从「虚拟环境创建 + 包安装/导出」开始练习，熟悉后再尝试版本管理和进阶技巧。

> 官方文档：[https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)
