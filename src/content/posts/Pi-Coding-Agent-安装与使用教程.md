---
title: Pi Coding Agent — 安装与使用教程
date: 2026-05-09
categories: 开发工具
tags: [AI, pi, CLI, Agent]
---

> 原文：[【最强AI Agent】π 使用教程 - LINUX DO](https://linux.do/t/topic/1680124)
> 作者：Ziphyrien

## 前言

**[Pi Coding Agent](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent)** 是一个有主见且极简的 Coding Agent，这段时间爆火的 OpenClaw 就是基于此工具包构建的。上手了一段时间后，可以说这就是目前最好用的 AI Agent CLI。

作者关于设计理念的阐述非常值得一读，详见博文：[Introducing Pi](https://mariozechner.at/posts/2025-11-30-pi-coding-agent/)。

### 设计理念

Pi 奉行近乎激进的可扩展性，因此无需、也不愿替你规定工作流。许多在别的工具中"内建"的能力，在这里都可通过 Extensions、Skills，或安装第三方 Pi Packages 来实现。这样既能让核心保持精简，又能让你按自己的工作方式塑造 Pi。

- **不做 MCP** — 你可以构建带有 README 的 CLI 工具（见 Skills），也可以编写 Extension 为 Pi 增加 MCP 支持
- **不设 Sub-agents** — 可借助 tmux 启动多个 Pi 实例，或用 Extensions 自行搭建
- **不弹 Permission Popups** — 在容器中运行，或通过 Extensions 构建确认流程
- **不设 Plan Mode** — 计划可直接写入文件，或借助 Extensions 实现
- **不内置 To-dos** — 使用 `TODO.md`，或用 Extensions 自定义
- **不提供后台 Bash** — 使用 tmux，全程可观测，交互更直接

<!-- more -->

## 快速上手

使用过程中有困难可以 [Ask DeepWiki](https://deepwiki.com/badlogic/pi-mono)。

### 安装

```bash
npm install -g @mariozechner/pi-coding-agent
```

接着可通过 `pi` 命令来启动，或[为你的终端配置快捷键](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/terminal-setup.md)。

#### Windows

注意：使用 Windows 的还需要一个 bash shell。检查顺序：

1. `~/.pi/agent/settings.json` 中的自定义路径
2. Git Bash（`C:\Program Files\Git\bin\bash.exe`）
3. PATH 中的 `bash.exe`（如 Cygwin、MSYS2、WSL）

对于大多数用户，[Git for Windows](https://git-scm.com/download/win) 足够了。

自定义 Shell 路径（`settings.json`）：

```json
{ "shellPath": "C:\\cygwin64\\bin\\bash.exe" }
```

#### Termux（Android）

详见[原文](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/termux.md)。

### 模型配置

配置好后可以通过 `/model`（或 Ctrl+L）选择模型。

#### 订阅登录

对于具有以下订阅之一的用户：

- Claude Pro/Max
- ChatGPT Plus/Pro (Codex)
- GitHub Copilot
- Google Gemini CLI
- Google Antigravity

可通过 `/login` 进行登录，使用 `/logout` 登出。认证 Token 会被储存在 `~/.pi/agent/auth.json`。

#### API 密钥

详见[原文](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/providers.md)。

可通过环境变量设置：

```bash
export ANTHROPIC_API_KEY=sk-ant-...
pi
```

或写入 `~/.pi/agent/auth.json`：

```json
{
  "anthropic": { "type": "api_key", "key": "sk-ant-..." },
  "openai": { "type": "api_key", "key": "sk-..." },
  "google": { "type": "api_key", "key": "..." },
  "opencode": { "type": "api_key", "key": "..." }
}
```

支持的供应商：

| 供应商 | 环境变量 | auth.json 键 |
|--------|---------|-------------|
| Anthropic | `ANTHROPIC_API_KEY` | `anthropic` |
| Azure OpenAI Responses | `AZURE_OPENAI_API_KEY` | `azure-openai-responses` |
| OpenAI | `OPENAI_API_KEY` | `openai` |
| Google Gemini | `GEMINI_API_KEY` | `google` |
| Mistral | `MISTRAL_API_KEY` | `mistral` |
| Groq | `GROQ_API_KEY` | `groq` |
| Cerebras | `CEREBRAS_API_KEY` | `cerebras` |
| xAI | `XAI_API_KEY` | `xai` |
| OpenRouter | `OPENROUTER_API_KEY` | `openrouter` |
| Vercel AI Gateway | `AI_GATEWAY_API_KEY` | `vercel-ai-gateway` |
| ZAI | `ZAI_API_KEY` | `zai` |
| OpenCode Zen | `OPENCODE_API_KEY` | `opencode` |
| Hugging Face | `HF_TOKEN` | `huggingface` |
| Kimi For Coding | `KIMI_API_KEY` | `kimi-coding` |
| MiniMax | `MINIMAX_API_KEY` | `minimax` |
| MiniMax（中国） | `MINIMAX_CN_API_KEY` | `minimax-cn` |

默认情况下 `auth.json` 是携带 `0600` 权限创建的（仅用户可读/写），Auth 文件凭证优先于环境变量。

#### 第三方提供商

详见[原文](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/models.md)。

创建 `~/.pi/agent/models.json`，完整示例：

```json
{
  "providers": {
    "CloseAI": {
      "baseUrl": "https://api.closeai.com/v1",
      "api": "openai-responses",
      "apiKey": "sk-...",
      "models": [
        {
          "id": "gpt-5.4",
          "name": "GPT-5.4",
          "reasoning": true,
          "input": ["text", "image"],
          "contextWindow": 1000000,
          "maxTokens": 128000,
          "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 }
        }
      ]
    }
  }
}
```

API 类型：

| API | 描述 |
|-----|------|
| `openai-completions` | OpenAI Chat Completions（最兼容） |
| `openai-responses` | OpenAI Responses API |
| `anthropic-messages` | Anthropic Messages API |
| `google-generative-ai` | Google Generative AI |

- 在 `providers` 层级设置的 `api`，作为该 provider 下所有 models 的默认值
- 在 `models` 层级中，单个模型可以通过自己的 `api` 字段覆盖这个默认值
- 如遇报错 `Error: 403 Your request was blocked.` 说明请求被 CF 阻断，自定义请求头加上 UA 即可：

```json
"headers": {
  "User-Agent": "MyCustomClient/1.0"
},
```

御三家模型配置示例（需套到上面的完整配置中）：

```json
{
  "models": [
    {
      "id": "gpt-5.4",
      "name": "GPT 5.4",
      "reasoning": true,
      "input": ["text", "image"],
      "contextWindow": 1000000,
      "maxTokens": 128000
    },
    {
      "id": "claude-opus-4-6",
      "name": "Claude Opus 4.6",
      "reasoning": true,
      "input": ["text", "image"],
      "contextWindow": 200000,
      "maxTokens": 128000
    },
    {
      "id": "gemini-3.1-pro-preview",
      "name": "Gemini 3.1 Pro Preview",
      "reasoning": true,
      "input": ["text", "image"],
      "contextWindow": 1048576,
      "maxTokens": 65536
    }
  ]
}
```

每次在 Pi 中键入 `/model` 时，文件都会重新加载，因此在会话期间编辑 `models.json` 无需重启。

## 指南

详见 [README](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent#readme)。

### 编辑器

指的是输入框。

| 功能 | 用法 |
|------|------|
| 文件引用 | 输入 `@` 可模糊搜索项目文件 |
| 路径补全 | 按 `Tab` 自动补全路径 |
| 多行输入 | `Shift+Enter`（Windows Terminal 下也可用 `Ctrl+Enter`） |
| 图片 | `Ctrl+V` 粘贴（Windows 下可用 `Alt+V`），或直接拖到终端 |
| Bash 命令 | `!command` 执行并把输出发给模型，`!!command` 执行但不发送输出 |

删除单词、撤销等使用标准编辑快捷键。详见[此处](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/keybindings.md)。

### 命令

在编辑器里输入 `/` 可触发命令。[扩展](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent#extensions)可注册自定义命令，[技能](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent#skills)可用 `/skill:name` 调用，[提示词模板](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent#prompt-templates)可通过 `/templatename` 展开。

| 命令 | 说明 |
|------|------|
| `/login`, `/logout` | OAuth 登录/退出 |
| `/model` | 切换模型 |
| `/scoped-models` | 启用/禁用 `Ctrl+P` 轮换可选模型 |
| `/settings` | 设置思考等级、主题、消息投递、传输方式 |
| `/resume` | 从历史会话中恢复 |
| `/new` | 新建会话 |
| `/name <name>` | 设置会话显示名称 |
| `/session` | 显示会话信息（路径、Token、费用） |
| `/tree` | 跳转到会话任意节点并从那里继续 |
| `/fork` | 从当前分支创建新会话 |
| `/compact [prompt]` | 手动压缩上下文，可自定义压缩提示 |
| `/copy` | 复制助手上一条回复到剪贴板 |
| `/export [file]` | 导出会话为 HTML 文件 |
| `/share` | 上传为私有 GitHub Gist，并生成可分享 HTML 链接 |
| `/reload` | 重载扩展、技能、提示词、上下文文件（主题会自动热更新） |
| `/hotkeys` | 显示全部快捷键 |
| `/changelog` | 显示版本更新记录 |
| `/quit`, `/exit` | 退出 pi |

### 消息队列

智能体工作时，你也可以继续发消息：

- **Enter**：排入一条*引导消息*，会在当前工具执行完后立即送达（并中断后续未执行工具）
- **Alt+Enter**：排入一条*跟进消息*，只会在代理完成全部工作后送达
- **Escape**：中止当前过程，并把已排队消息恢复到编辑器
- **Alt+Up**：把队列中的消息取回到编辑器

可在 [settings](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/settings.md) 配置投递方式：`steeringMode` 和 `followUpMode` 可设为 `"one-at-a-time"`（默认，收到回复后再发下一条）或 `"all"`（一次性发送队列全部消息）。`transport` 用于选择支持多传输的提供方通道偏好（`"sse"`、`"websocket"` 或 `"auto"`）。

### 会话

会话以 JSONL 树结构保存。每条记录都有 `id` 和 `parentId`，所以可以在同一个文件里直接分支，不必新建文件。文件格式见[此处](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/session.md)。

### 管理

会话会自动保存到 `~/.pi/agent/sessions/`，并按工作目录（cwd）分组。

- `pi -c`：继续最近一次会话
- `pi -r`：浏览并选择历史会话
- `pi --no-session`：临时模式（不保存会话）
- `pi --session <path>`：使用指定会话文件或会话 ID

### 分支

- **`/tree`**：在当前会话文件内浏览会话树。你可以选中任意历史节点，从那继续，并在不同分支间切换。输入关键词可搜索，`←/→` 翻页。过滤模式（Ctrl+O）：default → no-tools → user-only → labeled-only → all。按 `l` 可给条目标记书签。

- **`/fork`**：从当前分支创建一个新的会话文件。系统会打开选择器，复制到所选节点为止的历史，并把该节点消息放入编辑器，方便你继续修改。

### 设置

使用 `/settings` 修改常用选项，或直接编辑 JSON 文件：

| 位置 | 范围 |
|------|------|
| `~/.pi/agent/settings.json` | 全局 |
| `.pi/settings.json` | 项目 |

详见[此处](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/settings.md)。

### 项目上下文

Pi 在启动时会从以下位置加载 `AGENTS.md`（或 `CLAUDE.md`）：

- `~/.pi/agent/AGENTS.md`（全局）
- 父目录（从当前工作目录向上查找）
- 当前目录

用于项目说明、约束和常用命令封装。所有匹配的 md 文件将被拼接在一起。

#### 系统提示

- `.pi/SYSTEM.md`（项目）— 替换系统提示词
- `~/.pi/agent/SYSTEM.md`（全局）— 替换系统提示词
- `.pi/APPEND_SYSTEM.md` / `~/.pi/agent/APPEND_SYSTEM.md` — 追加在系统提示词末尾

## 自定义

这部分的内容都可以封装为 [PI Package](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent#pi-packages)。

这里整理了公开的 Pi 包：[Packages - pi.dev](https://pi.dev/packages)

### 提示词模板

将提示词封装为 Markdown 文件，输入 `/文件名` 展开。

```markdown
<!-- ~/.pi/agent/prompts/review.md -->
Review this code for bugs, security issues, and performance problems. Focus on: {{focus}}
```

放置在 `~/.pi/agent/prompts/`（全局）、`.pi/prompts/`（项目）或封装为 [PI Package](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent#pi-packages)。

### 技能（Skills）

按需加载的技能包，遵循 [Agent Skills 标准](https://agentskills.io/)。可通过输入 `/skill:name` 调用，也可让 Agent 自动加载。

```markdown
<!-- ~/.pi/agent/skills/my-skill/SKILL.md -->
# My Skill

Use this skill when the user asks about X.

## Steps
1. Do this
2. Then that
```

安装路径：

全局：
- `~/.pi/agent/skills/`
- `~/.agents/skills/`

项目：
- `.pi/skills/`
- `.agents/skills/`（从当前工作目录向上逐级查找父目录）

Pi 作者维护的[技能包](https://github.com/badlogic/pi-skills)，包含浏览器控制、Brave 搜索等技能，Pi 和其它支持 Skill 的项目都能直接使用。

### 扩展（Extensions）

放入 `~/.pi/agent/extensions/`（全局）、`.pi/extensions/`（项目）或封装为 PI Package。

参见[文档](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/extensions.md)和[例子](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/examples/extensions)。

### 主题（Themes）

内置暗色与明亮，修改主题配置后可热重载。

放入 `~/.pi/agent/themes/`（全局）、`.pi/themes/`（项目）或封装为 PI Package。

详见[此处](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/themes.md)。

> **通过扩展与主题系统可以极大增强使用体验！** 直接对模型说出需求即可，因为 Pi 的系统提示词中包含了 Pi 的文档路径。

## Pi Telegram Bot

这是原作者用 Pi 编写出来的项目，可以在 Telegram 上与 Pi Agent 沟通，并且是直接使用已有包进行 Markdown 到 HTML 的转换和标签清洗，而非手写转换。

项目地址：[Ziphyrien/Pi-Telegram](https://github.com/Ziphyrien/Pi-Telegram)

使用过程中有困难可以 [Ask DeepWiki](https://deepwiki.com/Ziphyrien/Pi-Telegram)。
