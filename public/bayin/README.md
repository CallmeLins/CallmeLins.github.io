# 八音 BaYin 展示页

八音音乐播放器的官方展示网站，采用纯 HTML + Tailwind CSS 构建。

## 📁 文件结构

```
public/bayin/
├── index.html          # 首页（功能展示、下载）
├── about.html          # 关于页面（项目介绍、技术栈）
├── changelog.html      # 更新日志
├── faq.html           # 常见问题
├── contact.html       # 联系方式
└── README.md          # 本文档
```

## 🚀 部署方式

本项目作为静态站点部署在 Astro 博客的 `public/bayin/` 目录中。

### 本地开发

1. 直接用浏览器打开 HTML 文件预览
2. 或在 Astro 项目根目录运行：
   ```bash
   npm run dev
   ```
   访问：http://localhost:4321/bayin/

### 生产部署

Astro 构建时会自动将 `public/` 目录的内容复制到输出目录：

```bash
npm run build
```

部署后访问：https://callmelins.github.io/bayin/

## 🎨 设计特点

- ✅ 纯静态 HTML，零依赖（除 Tailwind CDN）
- ✅ 响应式设计，移动端友好
- ✅ 极简风格，灰色系配色
- ✅ 毛玻璃导航栏
- ✅ 横向无限滚动动画
- ✅ 图片使用 GitHub raw URL，无需本地存储

## 🔗 相关链接

- GitHub 仓库：https://github.com/CallmeLins/BaYin
- TG 群组：https://t.me/+sQPyUqlcYaY5OTI9
- 博客主站：https://callmelins.github.io

## 📝 更新内容

修改任何页面后，只需提交并推送，GitHub Actions 会自动部署。

## 🛠️ 技术栈

- HTML5
- Tailwind CSS (CDN)
- Google Fonts (Inter)
- 原生 JavaScript（平滑滚动）

## 📄 许可证

本展示页与八音项目共享 Apache License 2.0 许可。
