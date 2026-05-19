# CallmeLins.github.io

Personal blog built with [Astro](https://astro.build) and [Tailwind CSS](https://tailwindcss.com), inspired by [sunls24/sunls24](https://github.com/sunls24/sunls24).

## Stack

- **Astro 5** + **React 19** + **Tailwind CSS 3**
- **Framer Motion** — BlurFade entrance animations
- **lucide-react** — icon library
- **GitHub Actions** — Pages deployment
- Dark / light mode with system preference detection

## Local development

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
```

## Preview production build

```bash
npm run preview
```

## Deployment

Pushing to `master` triggers the GitHub Actions workflow in [`.github/workflows/deploy.yml`](./.github/workflows/deploy.yml), which builds the Astro site and deploys to GitHub Pages.

## Content

- Posts: [`src/content/posts`](./src/content/posts)
- Site config: [`src/lib/config.ts`](./src/lib/config.ts)
- Meta info: [`src/lib/meta.ts`](./src/lib/meta.ts)
