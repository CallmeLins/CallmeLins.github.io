# qdrust Wiki 站点

qdrust 的项目介绍站，采用 **Wiki 风格**（侧边目录 + 正文 + 本页锚点目录），纯静态 HTML + Tailwind CSS 构建。

与 `pages/bayin`（偏产品介绍）不同，这个站点侧重**把项目讲清楚**：是什么、为什么这么设计、怎么用，内容主要来源于 `qdrust` 仓库的 README、`docs/` 目录与源码。

## 📁 文件结构

```
public/pages/qdrust/
├── index.html          # 总览：定位、核心特性、与 QD 的关系、快速上手
├── deploy.html         # 部署与运维：Docker / Compose、反代到二级目录、环境变量、数据库、通知、备份回滚
├── usage.html          # 使用指南：初始化管理员、第三方登录（OIDC / Header）、导入 HAR、任务、调度与时区、日志、CLI
├── architecture.html   # 架构设计：运行时模型、执行链路、调度与租约、数据模型、安全、API
├── templates.html      # 模板与表达式：HAR 契约、Schema v1、变量断言、函数过滤器、util 工具
├── browser.html        # 浏览器插件：api://browser/* 的 action、会话用法、生命周期与限制
├── notify.html         # 推送与通知：11 种渠道、通知动作、标题正文模板变量
├── api.html            # API 接口：80 个 REST 端点的路径与权限、认证、错误码、数据模型、调用示例
├── faq.html            # 常见问题
└── README.md           # 本文档
```

页面的**正文片段**不在这里，而放在 `scripts/qdrust-wiki/_parts/`，由脚本拼装成上面的成品页（见「页面的更新方式」）。

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

### 页面的更新方式

成品页由**外壳 + 正文片段**拼装而成，**不要直接改** `architecture / templates / browser / notify / deploy / usage / faq` 这 7 个 HTML——改了会被下次生成覆盖：

| 改什么 | 改哪里 |
|---|---|
| 导航、配色、脚本（影响全站） | `index.html`——它就是全站外壳 |
| 某页的正文内容 | `scripts/qdrust-wiki/_parts/<页名>.part.html` |
| 新增一页 | 加一个 part，再到 `scripts/qdrust-wiki/build_pages.py` 的 `PAGES` 登记 |

改完重跑脚本：

```bash
python scripts/qdrust-wiki/build_pages.py
```

脚本以 `index.html` 为外壳，把每个 part 塞进 `<main>`，并按页修正 `<title>`、`meta description`、`canonical` 与侧边栏高亮。`api.html` 不在其中——它由另一个脚本生成（见下）。

> `index.html` 本身是手写的（它既是总览页，也是外壳），不参与生成。

### 内容来源

qdrust 的 README 已精简为**指路页**，详细内容拆进了仓库的 `docs/` 目录。因此各页的对应关系是：

| 页面 | 主要来源 |
|---|---|
| 总览 | `README.md` 的介绍 / 核心特性 / 与 QD 的差异 / 组成 |
| 部署与运维 | `docs/deployment.md` + `.env.example` + `compose.yaml` + `docs/operations.md` |
| 使用指南 | `docs/usage.md` + `docs/authentication.md`（初始化、第三方登录、导入 HAR、任务、调度、日志、CLI） |
| 推送与通知 | `docs/notifications.md` + `crates/qdrust-server/src/push_channels.rs` 的 `ALL_CHANNEL_KINDS` |
| 架构设计 | `docs/adr/` + `docs/threat-model.md` + `crates/*` 源码 + `migrations/` |
| 模板与表达式 | `docs/expressions.md` + `docs/template-schema-v1.md` + `crates/qdrust-core/src/expression.rs`、`plugin.rs` |
| 浏览器插件 | `docs/browser-plugin.md` + `crates/qdrust-plugin-browser/src/` |
| API 接口 | `docs/openapi-v1.json` + `crates/qdrust-server/src/api.rs` 路由注册 + `docs/api-error-codes.md` |
| 常见问题 | `docs/faq.md`（wiki 另有分组与补充） |

> 表达式的函数 / 过滤器清单、`api://util/*` 工具清单、浏览器 action 清单、通知渠道 <code>kind</code> 清单均从源码核对得出，与文档的概述性表述有出入时以源码为准。
>
> 两个已知的文档与源码不一致（wiki 以源码为准）：`docs/expressions.md` 写「26 个过滤器 + 38 个函数」，实际是 **37 个全局函数 / 51 个过滤器**（26 个通过 `qd_fn!` 同时注册为函数与过滤器）；`docs/notifications.md` 的渠道数与 `ALL_CHANNEL_KINDS` 一致，为 11 种。

### API 页面的更新方式

`api.html` 由脚本生成，**不要手改 HTML**——下次 qdrust 升级时会重新生成，手改内容会被覆盖：

```bash
# 默认读取 C:/UserData/WorkSpace/Learn/qdrust
python scripts/gen-qdrust-api.py

# 或指定仓库路径
python scripts/gen-qdrust-api.py --qdrust D:/code/qdrust
```

脚本合并两份数据源，因为单看任一份都不完整：

1. `crates/qdrust-server/src/api.rs` 的路由注册 —— 给出「路径 + 方法 + handler」，并通过扫描 handler 函数体判断鉴权级别（调 `require_admin` 为管理员、调 `require_session` 为需登录、都没有则公开）。**OpenAPI 文档没有 security 描述，权限只能从源码拿。**
   路由注册在源码里分两段，脚本都扫：inner（`Router::new()` 到 `let state = AppState {`，含 API 与 SPA）与 root（`let mut root = Router::new()` 到 `root.with_state`，只含 `/health`、`/ready` 探针——它们刻意留在根路径，不受 `QDRUST_BASE_PATH` 影响）。
2. `docs/openapi-v1.json` —— 给出参数、请求体、响应与 `components.schemas`。

脚本会自动补两份数据的缺口：OpenAPI 不收录文档自身端点 `/api/v1/openapi.json`，源码里已注册却未进文档的端点也会一并补入，并在页面末尾的「与 OpenAPI 文档的差异」列出——**条数与清单都是动态生成的**，不用手改（当前 5 处：`DELETE /admin/users/{id}`、3 个 OIDC 登录端点、`POST /notification-actions/batch`）。

新增端点时只需在脚本的 `DESC` 字典补一条中文说明，`GROUPS` 列表调整分组规则，其余全部随源码自动更新。

> ⚠️ 脚本靠**字符串锚点**定位路由段，qdrust 若重构这段代码（比如改名 `inner` / `root`、调整 `AppState` 构造位置）会导致解析失败或静默漏端点。报错时先核对上述锚点是否还在；跑完也请留意输出的端点总数（当前 **80**：公开 13 / 需登录 56 / 管理员 11），与上次对比是否异常下降。

## 🔗 相关链接

- 源码仓库：https://github.com/CallmeLins/qdrust
- 参考项目（QD）：https://github.com/qd-today/qd
- 博客主站：https://callmelins.github.io

## 📄 许可证

与 qdrust 项目一致，采用 [MIT 许可证](https://github.com/CallmeLins/qdrust/blob/main/LICENSE) 开源。
