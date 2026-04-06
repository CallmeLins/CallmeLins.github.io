# CallmeLins.github.io

Personal blog source built with Hexo and the Cactus theme.

## Stack

- Hexo 8
- Cactus theme
- GitHub Actions for Pages deployment

## Local development

Install dependencies:

```bash
npm ci
```

Start the local server:

```bash
npm run server
```

Build the site:

```bash
npm run clean
npm run build
```

## Deployment

Pushing to `master` triggers the GitHub Actions workflow in [`.github/workflows/pages.yml`](./.github/workflows/pages.yml), which builds the Hexo site and deploys it to GitHub Pages.

## Content

- Posts: [`source/_posts`](./source/_posts)
- Pages: [`source/about`](./source/about), [`source/categories`](./source/categories), [`source/tags`](./source/tags)
- Site config: [`_config.yml`](./_config.yml)
