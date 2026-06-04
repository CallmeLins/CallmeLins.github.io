---
title: "Mac VSCode 优化配置"
date: 2026-06-04
updated: 2026-06-04
categories: 开发工具
tags:
  - VSCode
  - Mac
  - 快捷键
  - 配置
---

# Mac VSCode 优化配置

## 一、配置说明

本文档为 Mac 专属 VSCode 终极适配方案，解决两大核心需求：

- **全盘快捷键适配 Windows**：所有默认 Cmd 快捷键 100% 替换为 Ctrl，适配 Windows 操作习惯
- **彻底关闭全部 AI 功能**：禁用 VSCode 内置 AI、Copilot、智能补全、AI 搜索、Agent 智能体等所有 AI 入口，纯净编辑器模式

所有配置开箱即用，直接复制覆盖即可，无冲突、无残留。

## 二、第一步：完整 settings.json（关闭AI + 基础美化）

### 1. 打开配置文件

- 快捷键：`Ctrl + ,` 打开设置
- 点击右上角 `{}` 图标 打开 JSON 配置文件
- 清空原有内容，粘贴下方完整配置

### 2. 完整配置代码

```json
{
    // 基础界面美化配置
    "workbench.secondarySideBar.defaultVisibility": "hidden",
    "workbench.colorTheme": "One Dark Pro",
    "workbench.startupEditor": "none",

    // ========== 核心：彻底关闭所有 VSCode 内置AI ==========
    "chat.disableAIFeatures": true,
    "chat.agent.enabled": false,
    "chat.useHooks": false,

    // ========== 彻底禁用 GitHub Copilot 全部功能 ==========
    "github.copilot.enabled": false,
    "github.copilot.inlineSuggest.enable": false,
    "github.copilot.chat.enabled": false,

    // ========== 关闭所有AI补全、内联弹窗建议 ==========
    "editor.inlineSuggest.enabled": false,
    "editor.suggest.showInlineDetails": false,
    "editor.quickSuggestions": false,

    // ========== 关闭AI搜索、命令栏AI提问 ==========
    "workbench.settings.showAISearchToggle": false,
    "workbench.commandPalette.experimental.askChatLocation": "never",
    "search.searchView.semanticSearchBehavior": "never"
}
```

## 三、第二步：完整 keybindings.json（全量 Cmd 改 Ctrl）

### 1. 打开快捷键配置文件

- 快捷键：`Ctrl + K` 松开后按 `Ctrl + S` 打开快捷键面板
- 点击右上角 `{}` 图标 打开快捷键 JSON 文件
- 清空原有内容，粘贴下方全量快捷键配置

### 2. 全量快捷键配置（100% Cmd 转 Ctrl）

```json
[
  // 文件操作
  { "key": "ctrl+n", "command": "workbench.action.files.newUntitledFile" },
  { "key": "ctrl+o", "command": "workbench.action.files.openFile" },
  { "key": "ctrl+s", "command": "workbench.action.files.save" },
  { "key": "ctrl+shift+s", "command": "workbench.action.files.saveAs" },
  { "key": "ctrl+w", "command": "workbench.action.closeActiveEditor" },
  { "key": "ctrl+shift+t", "command": "workbench.action.reopenClosedEditor" },
  { "key": "ctrl+f4", "command": "workbench.action.closeActiveEditor" },
  { "key": "ctrl+shift+w", "command": "workbench.action.closeWindow" },

  // 基础编辑操作
  { "key": "ctrl+x", "command": "editor.action.clipboardCutAction" },
  { "key": "ctrl+c", "command": "editor.action.clipboardCopyAction" },
  { "key": "ctrl+v", "command": "editor.action.clipboardPasteAction" },
  { "key": "ctrl+z", "command": "undo" },
  { "key": "ctrl+shift+z", "command": "redo" },
  { "key": "ctrl+y", "command": "redo" },
  { "key": "ctrl+a", "command": "editor.action.selectAll" },
  { "key": "ctrl+f", "command": "actions.find" },
  { "key": "ctrl+h", "command": "editor.action.startFindReplaceAction" },
  { "key": "ctrl+g", "command": "workbench.action.gotoLine" },

  // 多行光标选择
  { "key": "ctrl+d", "command": "editor.action.addSelectionToNextFindMatch" },
  { "key": "ctrl+alt+up", "command": "editor.action.insertCursorAbove" },
  { "key": "ctrl+alt+down", "command": "editor.action.insertCursorBelow" },

  // 代码行操作
  { "key": "ctrl+enter", "command": "editor.action.insertLineAfter" },
  { "key": "ctrl+shift+enter", "command": "editor.action.insertLineBefore" },
  { "key": "ctrl+shift+k", "command": "editor.action.deleteLines" },
  { "key": "ctrl+]", "command": "editor.action.indentLines" },
  { "key": "ctrl+[", "command": "editor.action.outdentLines" },

  // 代码注释
  { "key": "ctrl+/", "command": "editor.action.commentLine" },
  { "key": "ctrl+shift+/", "command": "editor.action.blockComment" },

  // 代码格式化
  { "key": "ctrl+shift+i", "command": "editor.action.formatDocument" },

  // 窗口与面板控制
  { "key": "ctrl+shift+p", "command": "workbench.action.showCommands" },
  { "key": "ctrl+b", "command": "workbench.action.toggleSidebarVisibility" },
  { "key": "ctrl+`", "command": "workbench.action.terminal.toggleTerminal" },
  { "key": "ctrl+\\", "command": "workbench.action.splitEditor" },
  { "key": "ctrl+tab", "command": "workbench.action.openNextRecentlyUsedEditorInGroup" },
  { "key": "ctrl+shift+tab", "command": "workbench.action.openPreviousRecentlyUsedEditorInGroup" },

  // 全局搜索替换
  { "key": "ctrl+shift+f", "command": "workbench.action.findInFiles" },
  { "key": "ctrl+shift+h", "command": "workbench.action.replaceInFiles" },

  // 代码调试
  { "key": "f5", "command": "workbench.action.debug.start" },
  { "key": "ctrl+f5", "command": "workbench.action.debug.run" },
  { "key": "shift+f5", "command": "workbench.action.debug.stop" },
  { "key": "f10", "command": "debug.stepOver" },
  { "key": "f11", "command": "debug.stepInto" },
  { "key": "shift+f11", "command": "debug.stepOut" },

  // 代码重构与修复
  { "key": "ctrl+.", "command": "editor.action.quickFix" },
  { "key": "ctrl+shift+r", "command": "editor.action.rename" },
  { "key": "ctrl+shift+f12", "command": "editor.action.revealDefinition" },

  // 代码跳转定位
  { "key": "ctrl+p", "command": "workbench.action.quickOpen" },
  { "key": "ctrl+shift+o", "command": "workbench.action.gotoSymbol" },
  { "key": "ctrl+shift+m", "command": "workbench.actions.view.problems" },
  { "key": "ctrl+shift+[", "command": "editor.fold" },
  { "key": "ctrl+shift+]", "command": "editor.unfold" },

  // 代码选择
  { "key": "ctrl+shift+l", "command": "editor.action.selectHighlights" },
  { "key": "ctrl+i", "command": "editor.action.selectLine" },
  { "key": "ctrl+l", "command": "expandLineSelection" },

  // 终端操作
  { "key": "ctrl+shift+c", "command": "workbench.action.terminal.openNativeConsole" },
  { "key": "ctrl+shift+`", "command": "workbench.action.terminal.new" },

  // 标签页快速切换
  { "key": "ctrl+1", "command": "workbench.action.openEditorAtIndex1" },
  { "key": "ctrl+2", "command": "workbench.action.openEditorAtIndex2" },
  { "key": "ctrl+3", "command": "workbench.action.openEditorAtIndex3" },
  { "key": "ctrl+4", "command": "workbench.action.openEditorAtIndex4" },
  { "key": "ctrl+5", "command": "workbench.action.openEditorAtIndex5" },
  { "key": "ctrl+6", "command": "workbench.action.openEditorAtIndex6" },
  { "key": "ctrl+7", "command": "workbench.action.openEditorAtIndex7" },
  { "key": "ctrl+8", "command": "workbench.action.openEditorAtIndex8" },
  { "key": "ctrl+9", "command": "workbench.action.openLastEditorInGroup" }
]
```

## 四、第三步：彻底卸载AI扩展（杜绝残留）

1. 打开扩展面板：`Ctrl + Shift + X`
2. 卸载/禁用所有 AI 相关扩展，常见列表：
   - GitHub Copilot
   - Copilot Chat
   - Tabnine
   - CodeGeeX
   - 所有标注 AI、LLM、智能补全的扩展

## 五、生效方式

全部配置粘贴完成后，执行以下操作生效：

1. 保存所有配置文件（`Ctrl + S`）
2. 打开命令面板：`Ctrl + Shift + P`
3. 输入并执行：`Developer: Reload Window` 重载窗口

## 六、最终效果

- ✅ 所有 VSCode 快捷键完全适配 Windows Ctrl 习惯，无 Cmd 依赖
- ✅ 无 AI 弹窗、无智能补全、无 AI 聊天、无语义搜索
- ✅ 无 Copilot 后台运行，编辑器纯净无广告、无推送
- ✅ 保留主题、界面优化配置，简洁高效
