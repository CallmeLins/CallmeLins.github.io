---
title: "Tauri 跨平台应用开发完整指南：从创建到构建（Windows/macOS/iOS/Android）"
date: 2026-04-06 20:10:00
updated: 2026-04-06 20:10:00
categories: Tauri
tags:
  - Tauri
  - Rust
  - 跨平台
---

本文整理 **Tauri 项目全生命周期命令**，包含项目创建、初始化、桌面端（Windows/macOS）开发构建、移动端（Android/iOS）开发构建、常用运维命令，覆盖完整开发流程，可直接复制使用。

## 一、前置准备

在执行命令前，需先配置好 Tauri 基础环境：

1. 安装 Node.js（v16+）
2. 安装 Rust 环境
3. 桌面端：Windows/macOS 系统依赖
4. 移动端：Android Studio（Android）、Xcode（iOS/macOS）

## 二、Tauri 项目创建与初始化

### 1. 快速创建 Tauri 项目（推荐）

拉取最新官方模板，交互式创建项目（选择前端框架、包管理器等）：

```bash
npm create tauri-app@latest
```

### 2. 手动初始化 Tauri 配置

已存在前端项目时，手动集成 Tauri 并初始化配置：

```bash
npm run tauri init
```

## 三、桌面端开发与构建（Windows + macOS）

### 1. 开发模式（热重载预览）

启动本地开发服务，实时预览桌面端效果：

```bash
# 通用开发命令（自动适配当前系统）
npm run tauri dev
```

### 2. 生产构建（打包安装包）

构建对应系统的正式安装包，生成可分发文件：

```bash
# 构建当前系统安装包（Windows: .exe/.msi | macOS: .dmg/.app）
npm run tauri build
```

### 3. 跨平台构建补充（针对性命令）

```bash
# Windows 专属构建（仅 Windows 系统执行）
npm run tauri build -- --target x86_64-pc-windows-msvc

# macOS 专属构建（仅 macOS 系统执行）
npm run tauri build -- --target aarch64-apple-darwin  # M系列芯片
npm run tauri build -- --target x86_64-apple-darwin   # Intel芯片
```

## 四、移动端开发与构建（Android + iOS）

### 1. Android 平台（全流程命令）

```bash
# 1. 初始化 Android 开发环境（首次必执行）
npm run tauri android init

# 2. Android 开发模式（连接真机/模拟器）
npm run tauri android dev

# 3. 构建 Android 安装包（指定 aarch64 架构，主流手机适配）
npm run tauri android build -- --target aarch64
```

### 2. iOS / macOS 平台（仅 macOS 系统执行）

Tauri iOS 构建仅支持 macOS + Xcode，Windows 无法操作：

```bash
# 1. 初始化 iOS 环境
npm run tauri ios init

# 2. iOS 开发模式（连接 iPhone/iPad 或模拟器）
npm run tauri ios dev

# 3. 构建 iOS 安装包
npm run tauri ios build

# 补充：macOS 额外构建命令（同桌面端，Xcode 优化构建）
npm run tauri build -- --target universal-apple-darwin  # 通用包（兼容 Intel + M 系列）
```

## 五、Tauri 常用运维命令

### 1. 进程强制终止（解决卡死/编译卡住）

```bash
# Windows 系统：强制终止 cargo 编译进程
taskkill /f /im cargo.exe

# macOS/Linux 系统：强制终止 cargo 进程
pkill -f cargo
```

### 2. 依赖与配置相关

```bash
# 重新生成 Tauri 依赖（解决依赖报错）
npm run tauri deps install

# 清理构建缓存（解决打包异常）
npm run tauri clean

# 检查环境是否配置正确
npm run tauri info
```

### 3. 快捷调试命令

```bash
# 打开开发者工具（开发模式下快速调试）
npm run tauri dev -- --open-devtools
```

## 六、完整执行流程（推荐顺序）

### 桌面端全流程

```bash
# 1. 创建项目
npm create tauri-app@latest
# 2. 进入项目目录
cd 你的项目名
# 3. 开发预览
npm run tauri dev
# 4. 生产构建
npm run tauri build
```

### 移动端全流程（Android）

```bash
# 1. 初始化 Android 环境
npm run tauri android init
# 2. 开发预览
npm run tauri android dev
# 3. 生产构建
npm run tauri android build -- --target aarch64
```

### 移动端全流程（iOS - 仅 macOS）

```bash
# 1. 初始化 iOS 环境
npm run tauri ios init
# 2. 开发预览
npm run tauri ios dev
# 3. 生产构建
npm run tauri ios build
```

## 七、补充说明

1. **系统限制**：iOS/macOS 构建必须使用 macOS 系统 + Xcode，Windows 仅支持 Windows/Android 构建。
2. **命令前提**：所有 `npm run` 命令需在 **项目根目录**（含 `package.json`）执行。
3. **架构说明**：`aarch64` 为移动端主流架构，`x86_64` 为桌面端主流架构。
4. **报错处理**：编译卡住优先使用进程终止命令，依赖报错执行清理 + 重新安装。

## 总结

1. 本文覆盖 Tauri **创建 -> 初始化 -> 开发 -> 构建** 全流程，支持 Windows/macOS/Android/iOS 四平台。
2. 补充了环境检查、缓存清理、进程终止等高频运维命令，解决开发常见问题。
3. 命令按场景分类，可直接复制使用，适配新手快速上手。
