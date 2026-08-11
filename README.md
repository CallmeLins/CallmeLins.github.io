# CallmeLins' Blog

CallmeLins 的个人博客，基于 [Astro](https://astro.build/) 和
[astro-whono](https://github.com/cxro/astro-whono) 构建。

## 技术栈

- Astro 7
- Svelte 5（仅用于本地管理界面的交互组件）
- Astro Content Collections
- GitHub Actions 与 GitHub Pages
- 自托管中文字体、浅色/深色模式和阅读模式

## 环境要求

- Node.js 22.12 或更高版本
- 项目推荐版本见 [`.nvmrc`](./.nvmrc)

## 本地开发

```bash
npm install
npm run dev
```

默认访问地址为 <http://localhost:4321/>。

开发环境还提供本地管理界面：<http://localhost:4321/admin/>。管理界面可以调整站点设置、编辑内容和管理图片；生产构建仍然输出静态站点。

## 构建与预览

```bash
npm run build
npm run preview
```

生产环境应设置 `SITE_URL`，用于生成 canonical、Open Graph、RSS 和 sitemap 等绝对地址：

```bash
SITE_URL=https://blog.bayinlabs.com npm run build
```

PowerShell 可以使用：

```powershell
$env:SITE_URL = 'https://blog.bayinlabs.com'
npm run build
```

## 内容结构

| 内容 | 源文件 | 页面 |
| --- | --- | --- |
| 随笔 | `src/content/essay/` | `/essay/`、`/archive/` |
| 絮语 | `src/content/bits/` | `/bits/` |
| 小记 | `src/content/memo/index.md` | `/memo/` |
| 关于 | `src/content/about/index.md` | `/about/` |

站点个性化配置位于 `src/data/settings/`：

- `site.json`：站点标题、描述、页脚和社交链接
- `shell.json`：品牌、侧栏文案和导航
- `home.json`：首页介绍和头图
- `page.json`：各栏目标题与说明
- `ui.json`：排版、阅读模式和界面选项

静态图片和其他公开资源放在 `public/` 中。

## 部署

推送到 `master` 分支会触发 [GitHub Actions](./.github/workflows/deploy.yml)，构建并发布到 GitHub Pages。

## 致谢

博客界面与内容管理能力来自 [cxro/astro-whono](https://github.com/cxro/astro-whono)，原项目采用 MIT License。
