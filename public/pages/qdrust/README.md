# qdrust Wiki 站点

qdrust 的项目介绍站，采用 **Wiki 风格**（侧边目录 + 正文 + 本页锚点目录），纯静态 HTML + Tailwind CSS 构建。

与 `pages/bayin`（偏产品介绍）不同，这个站点侧重**把项目讲清楚**：是什么、为什么这么设计、怎么用，内容主要来源于 `qdrust` 仓库的 README 与源码。

## 📁 文件结构

```
public/pages/qdrust/
├── index.html          # 总览：定位、核心特性、与 QD 的关系、快速上手
├── architecture.html   # 架构设计：运行时模型、执行链路、调度与租约、数据模型、安全、API
├── templates.html      # 模板与表达式：HAR 契约、Schema v1、变量断言、函数过滤器、util 工具
├── browser.html        # 浏览器插件：api://browser/* 的 action、会话用法、生命周期与限制
├── deploy.html         # 部署与运维：Docker / Compose、环境变量、数据库、通知渠道、备份回滚
├── faq.html            # 常见问题
└── README.md           # 本文档
```

## 🚀 部署方式

作为静态站点部署在 Astro 博客的 `public/pages/qdrust/` 目录中，Astro 构建时会原样复制到输出目录。

```bash
# 本地预览
npm run dev        # http://localhost:4321/pages/qdrust/

# 生产构建
npm run build
```

部署后访问：https://callmelins.github.io/pages/qdrust/

## 🎨 设计特点

- **Wiki 三栏布局**：侧边主目录 + 正文 + 右侧本页锚点目录（滚动自动高亮）
- **零依赖**：除 Tailwind CDN 与 Google Fonts（Inter）外无外部依赖
- **响应式**：1100px 以下收起右侧目录，860px 以下侧边目录转为可折叠抽屉
- **轻量灰度配色**：与博客主站及 `pages/bayin` 保持同一套视觉语言
- **正文排版自持**：标题、表格、代码块、引用块样式内联在 `<style>` 中，不依赖 Tailwind Typography 插件

## 🛠 维护说明

各页面**互相独立**、互不依赖，可单独打开预览。页面之间只共享同一份头部样式与侧边栏 HTML——修改导航或配色时需要同步改动所有 6 个文件。

内容来源与对应关系：

| 页面 | 主要来源 |
|---|---|
| 总览 | `README.md` 的介绍 / 核心特性 / 与 QD 的差异 / 组成 |
| 架构设计 | `README.md` 架构决策说明 + `crates/*` 源码 + `migrations/` |
| 模板与表达式 | `README.md` + `docs/template-schema-v1.md` + `crates/qdrust-core/src/expression.rs`、`plugin.rs` |
| 浏览器插件 | `README.md` 浏览器插件章节 + `crates/qdrust-plugin-browser/src/` |
| 部署与运维 | `README.md` 部署 / 更新章节 + `.env.example` + `compose.yaml` |
| 常见问题 | `README.md` 的 FAQ 章节 |

> 表达式的函数 / 过滤器清单、`api://util/*` 工具清单、浏览器 action 清单均从源码核对得出，与 README 的概述性表述可能有出入时以源码为准。

## 🔗 相关链接

- 源码仓库：https://github.com/CallmeLins/qdrust
- 参考项目（QD）：https://github.com/qd-today/qd
- 博客主站：https://callmelins.github.io

## 📄 许可证

与 qdrust 项目一致，采用 [MIT 许可证](https://github.com/CallmeLins/qdrust/blob/main/LICENSE) 开源。
