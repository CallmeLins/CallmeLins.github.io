---
title: 最小化安装 MSVC（可用于 GraalVM Native-Image）
date: 2026-05-12
categories: Windows
tags: [Windows, Java, MSVC, GraalVM, Native-Image]
---

## 前言

自从接触了 native-image，就想把所有 Java 项目全用 native-image 编译一遍，谁不喜欢 exe 呢。但 MSVC 的前置条件一直让人望而却步——Visual Studio 超级重量级的大小、强制占用的 C 盘空间……

之前的做法是：创建一个虚拟机，在里面安装 MSVC 编译好 exe 再复制出来用。但随着项目依赖的增加，编译时间越来越长，构建产物也越来越大，更麻烦的是，电脑性能没法被充分利用。

经过漫长的搜索，终于找到办法可以不安装 Visual Studio，只安装构建工具链。虽然还是要占用 4GB 左右，但相比完整安装已经小了很多。

<!-- more -->

## 最小化安装方案

只需要安装以下三个组件：

- MSVC 编译器工具集（`VC.Tools.x86.x64`）
- Windows 11 SDK（`Windows11SDK.22000`）
- MSBuild（构建工具，可能非必需但推荐保留）

## 安装步骤

### 1. 下载安装程序

从微软官方文档找到 Visual Studio Build Tools 下载器：

[https://learn.microsoft.com/en-us/visualstudio/install/use-command-line-parameters-to-install-visual-studio](https://learn.microsoft.com/en-us/visualstudio/install/use-command-line-parameters-to-install-visual-studio?view=vs-2022)

下载 `vs_buildtools.exe`。

### 2. 命令行安装

在 `vs_buildtools.exe` 所在目录打开 cmd，执行以下命令，表示只安装 MSVC 工具集和 Windows 11 SDK：

```bat
vs_buildtools.exe --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows11SDK.22000
```

等待安装程序自动下载并完成安装。

### 3. 验证安装

安装完成后，在开始菜单中找到 `x64 Native Tools Command Prompt for VS 2022`，这个就是 native-image 所需的 MSVC 编译环境。

打开该命令行终端，确认 cl.exe 可用：

```bat
cl --version
```

## 后记

### 添加其他组件

如果需要安装其他组件，可以参考微软官方文档中的组件列表：

[https://learn.microsoft.com/en-us/visualstudio/install/workload-component-id-vs-build-tools](https://learn.microsoft.com/en-us/visualstudio/install/workload-component-id-vs-build-tools?view=vs-2022)

所有组件名称均可通过 `--add` 参数自行添加。

### 空间占用

在实体机执行同样命令安装后，总空间占用约 **4.24GB**（MSBuild 可能无法去掉）。相比网上其他教程动辄 8GB 的安装大小，已经优化了很多。

不过安装完成后 C 盘仍然会减少约 2GB 的空间，这是微软安装程序的设计限制，部分依赖会强制写入系统盘。

## 与 GraalVM Native-Image 集成

安装完 MSVC 后，在 GraalVM 中使用 native-image 时，需要先激活 MSVC 环境：

```bat
# 打开 x64 Native Tools Command Prompt for VS 2022
# 然后在其中执行 native-image 编译
native-image -jar your-app.jar
```

如果是通过命令行手动激活（非开始菜单快捷方式），可以运行：

```bat
call "C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
```

这样就可以在任意终端中使用 native-image 编译 Windows 原生可执行文件了。
