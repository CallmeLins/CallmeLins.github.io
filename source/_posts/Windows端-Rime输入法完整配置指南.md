---
title: "Windows 端 Rime 输入法（小狼毫）完整配置指南（基于白霜拼音+自然码双拼）"
date: 2026-05-06 21:00:00
updated: 2026-05-06 21:00:00
categories: 开发工具
tags:
  - Windows
  - Rime
---

近期被 Windows 自带输入法和 Visual Studio 2022 的兼容性问题困扰，每次写中文 commit message 时输入法都会崩溃、系统卡死。于是转向了开源、高度可定制且注重隐私的 Rime 输入法。花了不少时间折腾配置，这里记录一份完整流程，方便后续回溯，也希望能帮到有同样需求的朋友。

## 一、前期准备：安装 Rime 小狼毫输入法

### 1.1 下载与安装

1. 访问 Rime 输入法官方下载地址：https://rime.im/download/ ，下载 Windows 端版本（小狼毫输入法）。
2. 运行安装程序，建议指定自定义用户文件夹（后续便于管理个人配置文件），其余默认下一步即可。
3. 安装完成后，切换至小狼毫输入法，进入之前指定的用户文件夹，删除文件夹内所有默认配置文件（清空初始配置，为后续安装白霜拼音做准备）。

### 1.2 安装白霜拼音（基础词库）

1. 访问白霜拼音 GitHub Release 页面：https://github.com/iDvel/rime-frost/releases ，下载最新 release 版本中的 `full.zip`。
2. 将压缩包解压，把解压后的所有文件复制到之前指定的 Rime 用户文件夹（覆盖同名文件即可）。
3. 右键点击任务栏中的小狼毫图标，选择「重新部署」，等待部署完成（约 10-20 秒）。
4. 再次右键点击输入法图标，选择「输入法设定」，在弹窗中仅保留「白霜拼音」，删除其他多余方案，保存后再次点击「重新部署」。

## 二、词库定制：导入联系人 + 自定义短语

默认词库不一定满足个人习惯（如常用联系人姓名、自定义短语），因此需要手动整理并导入两类词库：「联系人词库」和「自定义短语词库」。

### 2.1 词库素材整理

#### 2.1.1 手机通讯录词库素材

1. 从手机导出通讯录，保存为 `.vcf` 文件。
2. 使用 Excel 打开 `.vcf` 文件，以 `:` 为分隔符分列，筛选出 `FN` 列（联系人姓名）。
3. 复制姓名列，粘贴到新的文本文件中，保存为 `.txt`（UTF-8 编码）。

#### 2.1.2 自定义短语素材

如果之前用过 Windows 自带输入法并维护了自定义短语，可直接导出：

1. 打开 Windows 自带输入法设置，找到「自定义短语」。
2. 使用导出功能，导出为 `UserDefinedPhrase.dat`。

### 2.2 词库转换（深蓝词库转换工具）

深蓝词库转换工具可以把各种词库格式转为 Rime 可用格式。

#### 2.2.1 转换联系人词库

1. 打开深蓝词库转换工具。
2. 选择「文件」->「打开」，导入联系人 `.txt`。
3. 转换方案选择：「无拼音纯汉字」->「Rime 中州韵」。
4. 点击「转换」，生成 Rime 词库文件。

#### 2.2.2 转换自定义短语词库（自然码双拼）

1. 打开深蓝词库转换工具，导入 `UserDefinedPhrase.dat`。
2. 拼音编码方案选择「自然码」。
3. 转换方案选择：「Win10 微软五笔（用户自定义短语）」->「Gboard - 自然码」。
4. 转换完成后，在工具目录找到 `Gboard词库.zip`，解压得到 `dictionary.txt`。
5. 用文本编辑器打开 `dictionary.txt`，可复制到 Excel 调整列顺序或替换权重（如把 `zh-CN` 替换为 `100`，权重越高优先级越高）。

## 三、Rime 词库编写与挂载

### 3.1 编写联系人词库

1. 将 2.2.1 的结果文件重命名为 `contacts.dict.yaml`。
2. 打开文件，在开头添加词库头：

```yaml
---
name: contacts
version: "2025-08-29"
sort: by_weight
columns:
  - text
  - code
  - weight
---
```

3. 保存为 UTF-8，并移动到用户文件夹的 `cn_dicts` 目录（没有则手动创建）。

### 3.2 挂载自定义词库（修改主词库）

1. 在 Rime 用户文件夹找到 `rime_frost.dict.yaml`。
2. 复制一份并重命名为 `extended.dict.yaml`（避免直接改原文件）。
3. 打开 `extended.dict.yaml`，修改 `name` 并配置 `import_tables`：

```yaml
---
name: extended
version: "2025-08-29"
import_tables:
  - cn_dicts/contacts
  - cn_dicts/8105
  - cn_dicts/base
  - cn_dicts/ext
  - cn_dicts/others
---
```

4. 新建补丁文件 `rime_frost_double_pinyin.custom.yaml`，指定新词库：

```yaml
patch:
  translator/dictionary: extended
```

### 3.3 配置自定义短语

1. 在 Rime 用户文件夹新建 `custom_phrase_double.txt`。
2. 将 2.2.2 中处理后的 `dictionary.txt` 内容复制进去。
3. 按 `词汇<Tab>编码<Tab>权重` 格式整理（编码需为自然码双拼）。
4. 保存为 UTF-8。

## 四、个人化配置（优化使用体验）

核心文件是 `weasel.custom.yaml`（皮肤与界面）和 `default.custom.yaml`（行为与快捷键）。

### 4.1 weasel.custom.yaml（皮肤与界面配置）

```yaml
patch:
  style/font_face: "Microsoft YaHei UI,JetBrains Maple Mono"
  style/label_font_face: "Microsoft YaHei UI,JetBrains Maple Mono"
  style/comment_font_face: "Microsoft YaHei UI,JetBrains Maple Mono"

  style/display_tray_icon: false

  style/+:
    label_format: "%s"
    inline_preedit: true
    font_point: 12
    label_font_point: 10
    comment_font_point: 12
    horizontal: true
    color_scheme: win11light
    color_scheme_dark: win11dark
    layout:
      min_width: 10
      margin_x: 16
      margin_y: 8
      border: 2
      candidate_spacing: 22
      hilite_spacing: 6
      hilite_padding: 2
      hilite_padding_x: 8
      corner_radius: 5
      round_corner: 4
      shadow_radius: 4

  preset_color_schemes/+:
    win11light:
      name: "Win11 浅色 / Win11light"
      text_color: 0x191919
      label_color: 0x191919
      hilited_label_color: 0x191919
      back_color: 0xf9f9f9
      border_color: 0x009e5a00
      hilited_mark_color: 0xc06700
      hilited_candidate_back_color: 0xf0f0f0
      shadow_color: 0x20000000
    win11dark:
      name: "Win11 暗色 / Win11Dark"
      text_color: 0xf9f9f9
      label_color: 0xf9f9f9
      back_color: 0x2C2C2C
      hilited_label_color: 0xf9f9f9
      border_color: 0x002C2C2C
      hilited_mark_color: 0xFFC24C
      hilited_candidate_back_color: 0x383838
      shadow_color: 0x20000000
```

### 4.2 default.custom.yaml（输入法行为与快捷键）

```yaml
patch:
  ascii_composer:
    good_old_caps_lock: true
    switch_key:
      Caps_Lock: clear
      Shift_L: commit_code
      Shift_R: commit_code

  menu/page_size: 7

  key_binder/bindings/+:
    - { accept: comma, send: Page_Up, when: paging }
    - { accept: period, send: Page_Down, when: has_menu }
    - { accept: "Shift+space", toggle: full_shape, when: always }

  schema_list:
    - { schema: rime_frost_double_pinyin }

  switcher/hotkeys: []
  switcher/hotkeys/+:
    - Control+Shift+F4
```

## 五、生效与调试

1. 所有配置文件修改后，右键小狼毫图标，选择「重新部署」。
2. 测试联系人词库、自定义短语、快捷键和皮肤是否生效。
3. 若不生效，检查：
   - 配置文件是否 UTF-8 编码
   - 词库文件名和路径是否正确
   - 是否执行了重新部署
4. 后续每次改 `.custom.yaml` 或词库文件，都需要重新部署。
