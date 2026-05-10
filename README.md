# CallmeLins.github.io

Personal blog source built with [Hexo](https://hexo.io/) and the [Shiro](https://github.com/Acris/hexo-theme-shiro) theme.

## Stack

- Hexo 8
- [Shiro](https://github.com/Acris/hexo-theme-shiro) theme (v1.4.0)
- GitHub Actions for Pages deployment
- [Pagefind](https://pagefind.app/) — static site search (CJK-friendly)

## Local development

Install dependencies:

```bash
npm ci
```

Start the local server:

```bash
npm run server
```

Build the site (with search index):

```bash
npm run clean
npm run build
```

Preview the production build locally (required for Pagefind search):

```bash
npm run clean
npm run build
npx serve public
```

## Deployment

Pushing to `master` triggers the GitHub Actions workflow in [`.github/workflows/pages.yml`](./.github/workflows/pages.yml), which builds the Hexo site and deploys it to GitHub Pages.

## Content

- Posts: [`source/_posts`](./source/_posts)
- Pages: [`source/about`](./source/about)
- Site config: [`_config.yml`](./_config.yml)
- Theme config: [`_config.shiro.yml`](./_config.shiro.yml)
