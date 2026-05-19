---
title: Ubuntu 部署 Claude Code 与自定义中转全面指南
date: 2026-05-12 13:15:00
categories: 运维
tags: [Ubuntu, Claude Code, AI, Node.js, Linux]
---

## 前言

Claude Code 是 Anthropic 推出的终端 AI 编程助手，能够通过自然语言指令自主完成代码生成、调试、重构和自动化开发任务。不同于传统的代码补全 AI，它可以主动读取代码库、编辑文件、运行命令、执行测试，并与 Git、IDE 及其他开发工具集成。

本文将详细介绍在 Ubuntu 系统上部署 Claude Code 的完整流程，以及如何通过配置使用国内大模型 API 中转（以阿里云百炼为例），解决国内用户无法直接访问 Claude 模型的问题。

<!-- more -->

## 环境要求

- Ubuntu 20.04 / 22.04 / 24.04 LTS
- Node.js 18+
- Git
- 终端

## 一、基础环境准备

### 1.1 更新系统

```bash
sudo apt update && sudo apt upgrade -y
```

### 1.2 安装 Node.js

首先检查当前 Node.js 版本：

```bash
node --version
```

如果版本低于 18 或未安装，推荐使用 nvm 安装 Node.js 20 LTS：

```bash
# 安装 nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc

# 配置国内镜像源（可选，加速下载）
export NVM_NODEJS_ORG_MIRROR=https://npmmirror.com/mirrors/node
export NVM_NPM_MIRROR=https://npmmirror.com/mirrors/npm

# 安装 Node.js 20
nvm install 20
nvm use 20
nvm alias default 20

# 验证
node --version
npm --version
```

或者直接使用 NodeSource 官方源安装：

```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install nodejs -y
```

### 1.3 安装 Git

```bash
git --version          # 检查是否已安装
sudo apt install -y git   # 如未安装则安装
```

## 二、安装 Claude Code CLI

### 2.1 全局安装

```bash
sudo npm install -g @anthropic-ai/claude-code
```

如果遇到网络问题，切换国内 npm 镜像源：

```bash
sudo npm config set registry https://registry.npmmirror.com
```

切换后重新执行安装命令：

```bash
sudo npm install -g @anthropic-ai/claude-code
```

### 2.2 验证安装

```bash
claude --version
```

### 2.3 跳过首次引导（必做）

创建 `~/.claude.json` 文件跳过首次登录引导：

```bash
echo '{
  "hasCompletedOnboarding": true,
  "clientDataCache": {}
}' > ~/.claude.json
```

> 注意：该文件路径是 `~/.claude.json`，不是 `settings.json`。若文件已存在，直接覆盖避免 JSON 格式错误。

验证：

```bash
cat ~/.claude.json
```

## 三、配置 API 中转（阿里云百炼）

因为网络限制，国内很难直接使用 Claude 模型。但 Claude Code 是一个执行框架，不一定需要对接 Claude 模型——可以通过配置对接国内大模型平台（如阿里云百炼）的 Anthropic 兼容接口。

### 3.1 获取 API Key

1. 访问 [阿里云百炼模型广场](https://bailian.console.aliyun.com/)
2. 选择支持 Anthropic API 兼容接口的模型（如 qwen3.5-coder-plus）
3. 点击「开通并获取 API Key」
4. 开通后记录你的 API Key

### 3.2 创建配置文件

创建 `~/.claude/settings.json`：

```bash
sudo mkdir -p ~/.claude
sudo nano ~/.claude/settings.json
```

填写以下配置（替换 `sk-你的真实APIKey` 为你申请的 Key）：

```json
{
  "env": {
    "ANTHROPIC_API_KEY": "sk-你的真实APIKey",
    "ANTHROPIC_BASE_URL": "https://dashscope.aliyuncs.com/apps/anthropic",
    "ANTHROPIC_MODEL": "qwen3.5-coder-plus"
  }
}
```

`Ctrl+O` 保存，`Ctrl+X` 退出。

### 3.3 配置说明

| 配置项 | 说明 |
|--------|------|
| `ANTHROPIC_API_KEY` | 阿里云百炼申请的 API Key |
| `ANTHROPIC_BASE_URL` | 阿里云 Anthropic 兼容接口地址 |
| `ANTHROPIC_MODEL` | 使用的模型名称（如 qwen3.5-coder-plus） |

## 四、启动与使用

### 4.1 创建工作目录

```bash
mkdir -p ~/workspace/my_project
cd ~/workspace/my_project
```

### 4.2 启动 Claude Code

```bash
claude
```

首次启动会进入交互式对话界面，直接在终端输入需求即可。

### 4.3 常用命令

| 命令 | 说明 |
|------|------|
| `claude` | 启动 Claude Code |
| `claude --help` | 查看帮助 |
| `claude update` | 更新到最新版本 |
| `exit` | 退出 Claude Code |

### 4.4 更新 Claude Code

```bash
sudo claude update
```

## 五、CC-Switch：多模型切换工具

CC-Switch 是一款开源工具，可以统一管理 Claude Code、DeepSeek、Kimi、智谱、MiniMax 等模型，无需手动改环境变量和配置文件，实现一键切换 AI 服务商。

### 5.1 安装 CC-Switch

```bash
# 下载最新版 deb 包
wget https://github.com/farion1231/cc-switch/releases/download/v3.14.1/CC-Switch-v3.14.1-Linux-x86_64.deb

# 安装
sudo dpkg -i CC-Switch-v3.14.1-Linux-x86_64.deb

# 修复依赖
sudo apt-get install -f -y
```

### 5.2 启动 CC-Switch

```bash
cc-switch
```

图形界面将自动弹出，可在界面中配置各个模型的 API Key，之后即可在 Claude Code 中快速切换不同的模型提供商。

## 六、VS Code 插件配置（可选）

### 6.1 安装插件

在 VS Code 扩展商店搜索「Claude Code」并安装。

### 6.2 关闭登录提示

按下 `Ctrl+,` 打开设置，搜索 `claude code`，勾选「Disable Login Prompt」禁用每次登录提示，重启 VS Code。

### 6.3 全局配置

在 VS Code 中点击 Claude Code 图标的齿轮按钮 → `setting.json`，将之前的环境变量配置转化为 JSON 格式：

```json
[
  {
    "name": "ANTHROPIC_API_KEY",
    "value": "sk-你的真实APIKey"
  },
  {
    "name": "ANTHROPIC_BASE_URL",
    "value": "https://dashscope.aliyuncs.com/apps/anthropic"
  },
  {
    "name": "ANTHROPIC_MODEL",
    "value": "qwen3.5-coder-plus"
  }
]
```

配置完成后重启 VS Code，即可在编辑器中使用 Claude Code。

### 6.4 三种模式说明

| 模式 | 说明 |
|------|------|
| **Ask**（先说后动） | 操作前会咨询，由你决定是否执行 |
| **Edit**（直接执行） | 根据指令直接执行，适合明确、风险可控的操作 |
| **Plan**（先规划后执行） | 拆解详细步骤和计划，逐步确认后再修改 |

## 七、一键安装脚本

以下是完整的 Ubuntu 22.04 Claude Code 一键安装脚本，整合了上述所有步骤：

```bash
#!/bin/bash
# Ubuntu 22.04 Claude Code 一键安装脚本

echo "=== 开始安装 Claude Code ==="

# 1. 更新系统
echo "更新系统..."
sudo apt update && sudo apt upgrade -y

# 2. 安装 nvm
echo "安装 nvm..."
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc

# 3. 配置国内镜像
echo "配置国内镜像源..."
export NVM_NODEJS_ORG_MIRROR=https://npmmirror.com/mirrors/node
export NVM_NPM_MIRROR=https://npmmirror.com/mirrors/npm

# 4. 安装 Node.js
echo "安装 Node.js 20..."
nvm install 20
nvm use 20
nvm alias default 20

# 5. 配置 npm 镜像
echo "配置 npm 镜像..."
npm config set registry https://registry.npmmirror.com

# 6. 安装 Claude Code
echo "安装 Claude Code..."
npm install -g @anthropic-ai/claude-code --force

# 7. 跳过首次引导
echo "跳过首次引导..."
echo '{
  "hasCompletedOnboarding": true,
  "clientDataCache": {}
}' > ~/.claude.json

# 8. 验证安装
echo "验证安装..."
if command -v claude &> /dev/null; then
    claude --version
    echo "✅ Claude Code 安装成功！"
else
    echo "❌ 安装失败，请检查错误信息"
fi

echo "=== 安装完成 ==="
echo "请手动配置 ~/.claude/settings.json 中的 API Key"
```

## 八、常见问题排查

### 问题1：安装时提示权限错误（EACCES）

使用 `sudo` 执行 npm 全局安装，或配置 npm 全局路径：

```bash
npm config set prefix ~/.npm-global
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### 问题2：npm 安装速度缓慢

配置国内镜像源：

```bash
npm config set registry https://registry.npmmirror.com
```

### 问题3：启动时提示需要登录

确保已创建 `~/.claude.json` 并包含 `"hasCompletedOnboarding": true`，同时检查 `~/.claude/settings.json` 中的 API Key 配置是否正确。

### 问题4：API 调用返回 403

请求被 Cloudflare 阻断，可尝试在配置中添加自定义 User-Agent：

```json
{
  "env": {
    "ANTHROPIC_API_KEY": "sk-...",
    "ANTHROPIC_BASE_URL": "https://dashscope.aliyuncs.com/apps/anthropic",
    "ANTHROPIC_MODEL": "qwen3.5-coder-plus",
    "ANTHROPIC_HEADERS": "{\"User-Agent\": \"MyCustomClient/1.0\"}"
  }
}
```

### 问题5：VS Code 插件 Unsupported JVM version

确保 VS Code 版本在 1.98.0 以上，Java 运行环境在 JDK 17 以上。

## 九、总结

通过以上步骤，你可以在 Ubuntu 系统上完整部署 Claude Code，并通过阿里云百炼等国内平台提供的 Anthropic 兼容接口使用编程助手功能。结合 CC-Switch 工具还可以在多个模型之间自由切换，CC-Switch 的图形界面让配置更加直观。

主要优势：
- ✅ 零网络障碍：通过国内中转使用 Claude Code 框架
- ✅ 多模型支持：通义千问、DeepSeek、智谱等均可接入
- ✅ VS Code 深度集成：支持 Ask / Edit / Plan 三种模式
- ✅ 开源免费：Claude Code 框架本身开源，仅需模型 API 费用
