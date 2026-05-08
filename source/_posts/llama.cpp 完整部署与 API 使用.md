---
title: "llama.cpp 完整部署与 CLI/API 使用"
date: 2026-05-08 14:00:00
updated: 2026-05-08 14:00:00
categories: 开发工具
tags:
  - Ubuntu
  - llama
---

# llama.cpp 完整部署与 CLI/API 使用手册
本文基于 **llama.cpp b9066** + **Gemma-4-31B-it-uncensored-GGUF**，适配双路 Xeon 8368 + 256GB 内存服务器，从安装到接入 Claude Code 一站式整理。

---

## 一、环境说明
- 硬件：双路 Xeon 8368（76核152线程）、256GB 内存
- 系统：Ubuntu Linux
- 模型：Gemma-4-31B-it-uncensored-Q4_K_M.gguf
- 工具：llama.cpp（预编译二进制，无需编译）

---

## 二、llama.cpp 快速安装（预编译版）
### 1. 下载与解压
```bash
mkdir -p ~/Workspace/llama && cd ~/Workspace/llama
wget https://github.com/ggml-org/llama.cpp/releases/download/b9066/llama-b9066-bin-ubuntu-x64.tar.gz
tar -zxvf llama-b9066-bin-ubuntu-x64.tar.gz
cd llama-b9066
```

### 2. 目录结构（关键文件）
```
llama-b9066/
├── llama-server    # Web UI + OpenAI 兼容 API 服务
├── llama-cli       # 命令行聊天工具
└── models/         # 模型存放目录（自建）
```

---

## 三、模型下载（Gemma-4-31B GGUF）
### 1. 创建模型目录
```bash
mkdir -p models/gemma-4-31b
cd models/gemma-4-31b
```

### 2. 下载 4-bit 量化版（推荐）
```bash
wget https://huggingface.co/TrevorJS/gemma-4-31B-it-uncensored-GGUF/blob/main/gemma-4-31B-it-uncensored-Q4_K_M.gguf
```
- 大小：18.7GB
- 内存占用：≈20GB（256GB 内存无压力）

---

## 四、启动服务（双路 CPU 最优参数）
### 1. 启动 Web UI + API 服务（推荐）
```bash
cd ~/Workspace/llama/llama-b9066

./llama-server \
-m models/gemma-4-31b/gemma-4-31B-it-uncensored-Q4_K_M.gguf \
--numa distribute \
--threads 76 \
--host 0.0.0.0 \
--port 8080
```

### 2. 参数说明
- `--numa distribute`：双路 CPU 负载均衡（必开）
- `--threads 76`：使用全部物理核心（双路 38+38）
- `--host 0.0.0.0`：局域网可访问
- `--port 8080`：服务端口

### 3. 启动成功标识
```
llama server listening at http://0.0.0.0:8080
```

---

## 五、命令行直接使用（llama-cli）
### 1. 交互聊天模式
```bash
./llama-cli \
-m models/gemma-4-31b/gemma-4-31B-it-uncensored-Q4_K_M.gguf \
--numa distribute \
--threads 76 \
-i
```

### 2. 单轮问答
```bash
./llama-cli \
-m models/gemma-4-31b/gemma-4-31B-it-uncensored-Q4_K_M.gguf \
--numa distribute \
--threads 76 \
-p "What is the capital of France?"
```

---

## 六、接入 Claude Code / Cline / IDE 插件
llama-server 自带 **OpenAI 兼容 API**，所有 Claude 生态工具直接接入。

### 1. 通用配置（所有工具通用）
- API 地址：`http://服务器IP:8080/v1`
- API Key：`dummy`（任意字符串）
- 模型名：`gemma-4-31B-it-uncensored-Q4_K_M`
- 协议：`OpenAI Compatible`

### 2. VSCode Claude Code（Cline）配置
1. 插件设置 → API Provider 选择 `OpenAI Compatible`
2. 填写：
   - Endpoint：`http://你的服务器IP:8080/v1`
   - API Key：`dummy`
   - Model：`gemma-4-31B-it-uncensored-Q4_K_M`

### 3. Aider CLI 一键接入
```bash
aider --openai-api-key dummy --openai-api-base http://服务器IP:8080/v1 --model gemma-4-31B-it-uncensored-Q4_K_M
```

---

## 七、服务后台运行（关闭终端不退出）
```bash
nohup ./llama-server -m models/gemma-4-31b/gemma-4-31B-it-uncensored-Q4_K_M.gguf --numa distribute --threads 76 --host 0.0.0.0 --port 8080 > server.log 2>&1 &
```

### 停止服务
```bash
pkill -f llama-server
```

---

## 八、常见问题
### 1. `--numa` 参数报错
错误：`error while handling argument "--numa": invalid value`
解决：必须用 `--numa distribute`，不能填数字 1。

### 2. 速度优化
- 必开：`--numa distribute` + 物理核心数线程
- 关闭系统 NUMA 平衡（可选）：`echo 0 | sudo tee /proc/sys/kernel/numa_balancing`

---

## 九、性能参考
- 模型：Gemma-4-31B Q4_K_M
- 速度：12～18 token/s
- 内存占用：≈20GB
- 适用场景：私有部署、代码辅助、文档问答

---