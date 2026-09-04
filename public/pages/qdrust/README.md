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
├── api.html            # API 接口：76 个 REST 端点的路径与权限、认证、错误码、数据模型、调用示例
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

各页面**互相独立**、互不依赖，可单独打开预览。页面之间只共享同一份头部样式与侧边栏 HTML——修改导航或配色时需要同步改动所有 7 个文件。

内容来源与对应关系：

| 页面 | 主要来源 |
|---|---|
| 总览 | `README.md` 的介绍 / 核心特性 / 与 QD 的差异 / 组成 |
| 架构设计 | `README.md` 架构决策说明 + `crates/*` 源码 + `migrations/` |
| 模板与表达式 | `README.md` + `docs/template-schema-v1.md` + `crates/qdrust-core/src/expression.rs`、`plugin.rs` |
| 浏览器插件 | `README.md` 浏览器插件章节 + `crates/qdrust-plugin-browser/src/` |
| 部署与运维 | `README.md` 部署 / 更新章节 + `.env.example` + `compose.yaml` |
| API 接口 | `docs/openapi-v1.json` + `crates/qdrust-server/src/api.rs` 路由注册 + `docs/api-error-codes.md` |
| 常见问题 | `README.md` 的 FAQ 章节 |

> 表达式的函数 / 过滤器清单、`api://util/*` 工具清单、浏览器 action 清单均从源码核对得出，与 README 的概述性表述可能有出入时以源码为准。

### API 页面的更新方式

`api.html` 由脚本生成，**不要手改 HTML**——下次 qdrust 升级时会重新生成，手改内容会被覆盖：

```bash
# 默认读取 C:/UserData/WorkSpace/Learn/qdrust
python scripts/gen-qdrust-api.py

# 或指定仓库路径
python scripts/gen-qdrust-api.py --qdrust D:/code/qdrust
```

脚本合并两份数据源，因为单看任一份都不完整：

1. `crates/qdrust-server/src/api.rs` 的 `Router::new()` 路由注册 —— 给出「路径 + 方法 + handler」，并通过扫描 handler 函数体判断鉴权级别（调 `require_admin` 为管理员、调 `require_session` 为需登录、都没有则公开）。**OpenAPI 文档没有 security 描述，权限只能从源码拿。**
2. `docs/openapi-v1.json` —— 给出参数、请求体、响应与 `components.schemas`。

脚本会自动补两份数据的缺口并打印提示：OpenAPI 不收录文档自身端点 `/api/v1/openapi.json`，也漏收了 `DELETE /api/v1/admin/users/{id}`。

新增端点时只需在脚本的 `DESC` 字典补一条中文说明，`GROUPS` 列表调整分组规则，其余全部随源码自动更新。

## 🔗 相关链接

- 源码仓库：https://github.com/CallmeLins/qdrust
- 参考项目（QD）：https://github.com/qd-today/qd
- 博客主站：https://callmelins.github.io

## 📄 许可证

与 qdrust 项目一致，采用 [MIT 许可证](https://github.com/CallmeLins/qdrust/blob/main/LICENSE) 开源。
