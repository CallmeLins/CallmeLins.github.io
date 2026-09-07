"""Generate qdrust wiki pages from index.html shell + per-page article parts.

用法：
    python scripts/qdrust-wiki/build_pages.py

说明：
  - 外壳取自 public/pages/qdrust/index.html，因此改导航 / 配色只需改 index.html，
    再重跑本脚本即可同步到下面列出的所有页面。
  - api.html 不在此列：它由 scripts/gen-qdrust-api.py 单独生成（数据来源不同），
    但同样以 index.html 为外壳，所以样式改动也会同步过去。
"""

import pathlib
import re
import sys

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1] / "public" / "pages" / "qdrust"
SHELL = ROOT / "index.html"

# _parts 是构建中间产物，不放在 public/ 下，避免被原样复制到 dist 发布出去
PARTS = SCRIPT_DIR / "_parts"

PAGES = [
    {
        "file": "usage.html",
        "part": "usage.part.html",
        "nav": "usage.html",
        "title": "使用指南 | qdrust Wiki",
        "description": "qdrust 使用指南：初始化管理员、导入 QD HAR 模板、创建与运行任务、可视化 HAR 编辑器、调度与随机延迟、cron 时区与夏令时、运行日志与 CLI。",
        "path": "usage.html",
    },
    {
        "file": "architecture.html",
        "part": "architecture.part.html",
        "nav": "architecture.html",
        "title": "架构设计 | qdrust Wiki",
        "description": "qdrust 架构设计：单进程 Tokio 运行时、执行链路、调度与租约队列、数据模型、安全模型、API 一览与横向扩展边界。",
        "path": "architecture.html",
    },
    {
        "file": "templates.html",
        "part": "templates.part.html",
        "nav": "templates.html",
        "title": "模板与表达式 | qdrust Wiki",
        "description": "qdrust 模板体系：旧 QD HAR 兼容契约、Template Schema v1、变量与断言、Jinja2 函数与过滤器、api://util/* 内置工具。",
        "path": "templates.html",
    },
    {
        "file": "browser.html",
        "part": "browser.part.html",
        "nav": "browser.html",
        "title": "浏览器插件 | qdrust Wiki",
        "description": "qdrust 无头浏览器插件 api://browser/*：启用方式、action 一览、混合签到模板写法、会话生命周期与行为限制。",
        "path": "browser.html",
    },
    {
        "file": "deploy.html",
        "part": "deploy.part.html",
        "nav": "deploy.html",
        "title": "部署与运维 | qdrust Wiki",
        "description": "qdrust 部署与运维：Docker 快速启动、生产 Compose 配置、环境变量全表、数据库选型、10 种通知渠道、备份与升级回滚。",
        "path": "deploy.html",
    },
    # 注意：api.html 不在此生成——它由 scripts/gen-qdrust-api.py 负责
    # （数据来自 docs/openapi-v1.json + api.rs 路由表，来源不同）。
    # 若在此列入，会用陈旧的 api.part.html 覆盖掉那份正确产物。
    {
        "file": "faq.html",
        "part": "faq.part.html",
        "nav": "faq.html",
        "title": "常见问题 | qdrust Wiki",
        "description": "qdrust 常见问题：HTTPS 会话、SMTP 配置、迁移与回滚范围、调度精度、CLI 网络策略、模板沙箱与浏览器插件。",
        "path": "faq.html",
    },
]

MAIN_CLOSE = "</main>"


def build(shell: str, page: dict, part: str) -> str:
    # 1. <title>
    out = re.sub(r"<title>.*?</title>", f"<title>{page['title']}</title>", shell, count=1)

    # 2. meta description
    out = re.sub(
        r'(<meta name="description" content=")[^"]*(")',
        lambda m: m.group(1) + page["description"] + m.group(2),
        out,
        count=1,
    )

    # 3. canonical
    out = re.sub(
        r'(<link rel="canonical" href=")[^"]*(")',
        lambda m: m.group(1) + "https://callmelins.github.io/pages/qdrust/" + page["path"] + m.group(2),
        out,
        count=1,
    )

    # 4. sidebar active state
    def fix_nav(match: re.Match) -> str:
        href = match.group(1)
        cls = "wiki-nav-link is-active" if href == page["nav"] else "wiki-nav-link"
        return f'<a href="{href}" class="{cls}">'

    out = re.sub(r'<a href="([a-z-]+\.html)" class="wiki-nav-link[^"]*">', fix_nav, out)

    # 5. article body
    # 用正则而非固定字符串：外壳的 <main> 可能被编辑器注入额外属性
    m = re.search(r"<main[^>]*>", out)
    if not m:
        raise ValueError("index.html 外壳里找不到 <main> 标记")
    start = m.end()
    end = out.index(MAIN_CLOSE, start)
    out = out[:start] + "\n" + part.rstrip("\n") + "\n            " + out[end:]

    return out


def main() -> int:
    shell = SHELL.read_text(encoding="utf-8")
    if not re.search(r"<main[^>]*>", shell) or MAIN_CLOSE not in shell:
        print("ERROR: main markers not found in index.html", file=sys.stderr)
        return 1

    for page in PAGES:
        part_path = PARTS / page["part"]
        if not part_path.exists():
            print(f"ERROR: missing part {part_path}", file=sys.stderr)
            return 1
        html = build(shell, page, part_path.read_text(encoding="utf-8"))
        target = ROOT / page["file"]
        target.write_text(html, encoding="utf-8")
        print(f"wrote {target.name} ({len(html)} chars)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
