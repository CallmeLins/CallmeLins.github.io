import type { icons } from "lucide-react"

interface Item {
  name: string
  desc: string
  link: string
  icon: keyof typeof icons
}

interface AboutConfig {
  mail: string
  me: string
  backend: string[]
  frontend: string[]
}

interface Config {
  github: string
  since: number
  projects: Item[]
  links: Item[]
  about: AboutConfig
}

export const config: Config = {
  github: "https://github.com/CallmeLins",
  since: 2021,
  projects: [
    {
      name: "BaYin",
      desc: "轻量音乐播放器，支持本地曲库播放，对接云端音乐资源",
      link: "https://github.com/CallmeLins/BaYin",
      icon: "Music",
    },
  ],
  links: [
    {
      name: "ARTICLE",
      link: "/articles",
      desc: "技术文章与折腾记录",
      icon: "Newspaper",
    },
    {
      name: "SEARCH",
      link: "/search",
      desc: "搜索文章内容",
      icon: "Search",
    },
    {
      name: "ARCHIVES",
      link: "/archives",
      desc: "按时间线浏览所有文章",
      icon: "Archive",
    },
    {
      name: "CATEGORIES",
      link: "/categories",
      desc: "按分类浏览文章",
      icon: "Folder",
    },
    {
      name: "TAGS",
      link: "/tags",
      desc: "按标签浏览文章",
      icon: "Tag",
    },
    {
      name: "ABOUT",
      link: "/about",
      desc: "关于这个兴趣使然的无名小站",
      icon: "User",
    },
  ],
  about: {
    mail: "",
    me: "兴趣使然的全栈工程师，崇尚简约，少即是多 💪",
    backend: ["Python", "Rust", "Docker", "Linux", "CUDA"],
    frontend: ["TypeScript", "React", "Next.js", "Flutter", "Astro"],
  },
}
