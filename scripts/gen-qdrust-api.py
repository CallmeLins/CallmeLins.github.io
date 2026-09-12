#!/usr/bin/env python3
"""从 qdrust 源码重新生成博客里的 API 参考页（public/pages/qdrust/api.html）。

数据源有两处，脚本负责合并它们——因为单看任一份都不完整：

1. ``crates/qdrust-server/src/api.rs`` 的 ``Router::new()`` 路由注册
   给出「路径 + 方法 + handler」，并通过扫描 handler 函数体判断鉴权级别。
   OpenAPI 文档里没有 security 描述，权限只能从这里拿。
2. ``docs/openapi-v1.json``
   给出参数、请求体、响应与 ``components.schemas``。

用法::

    python .workbuddy/scripts/gen-qdrust-api.py
    python .workbuddy/scripts/gen-qdrust-api.py --qdrust D:/code/qdrust

刷新页面时通常只需要改两处：下面 ``DESC`` 表（新增端点的中文说明）
和 ``GROUPS`` 表（分组规则）。其余内容全部随源码自动更新。
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
from collections import Counter

# 本文件位于 <博客仓库>/scripts/，故 parents[1] 即仓库根
BLOG = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_QDRUST = pathlib.Path(r"C:\UserData\WorkSpace\Learn\qdrust")

PAGE_DIR = BLOG / "public" / "pages" / "qdrust"
SHELL = PAGE_DIR / "index.html"
TARGET = PAGE_DIR / "api.html"

METHOD_ORDER = ["GET", "POST", "PUT", "PATCH", "DELETE"]

# --------------------------------------------------------------------------
# 端点中文说明。键为 (方法, 路径)。新增端点时在这里补一条。
# --------------------------------------------------------------------------
DESC = {
    ("GET", "/health"): "存活探针，固定返回服务标识，不检查依赖",
    ("GET", "/ready"): "就绪探针，额外检查数据库连通性",
    ("GET", "/api/v1/openapi.json"): "内嵌的 OpenAPI 3.1 文档，可直接喂给 Swagger UI",

    ("POST", "/api/v1/auth/bootstrap"): "创建首个管理员账号；已有用户时返回 409，整个生命周期只能成功一次",
    ("POST", "/api/v1/auth/register"): "注册普通用户；首个用户请改用 bootstrap",
    ("POST", "/api/v1/auth/login"): "登录并下发会话 Cookie；失败会计入限流窗口",
    ("GET", "/api/v1/auth/session"): "获取当前登录用户、角色与邮箱验证状态",
    ("POST", "/api/v1/auth/logout"): "注销当前会话并清除 Cookie",
    ("POST", "/api/v1/auth/password"): "修改当前用户密码（需校验旧密码）",
    ("POST", "/api/v1/auth/forgot-password"): "申请密码重置，向邮箱发送令牌",
    ("POST", "/api/v1/auth/reset-password"): "凭重置令牌设置新密码",
    ("POST", "/api/v1/auth/verify-email"): "校验邮箱验证码",
    ("POST", "/api/v1/auth/resend-verification"): "重发邮箱验证邮件",
    ("POST", "/api/v1/auth/csrf/rotate"): "轮换 CSRF 令牌，返回新的 <code>qd_csrf</code>",
    ("GET", "/api/v1/auth/config"): "读取服务端认证策略：<code>auth_mode</code>、<code>local_login_enabled</code>、<code>oidc_enabled</code>、<code>oidc_provider_name</code>、<code>header_auth_enabled</code>。WebUI 据此决定渲染哪些登录入口",
    ("GET", "/api/v1/auth/oidc/start"): "发起 OIDC 授权码 + PKCE 流程：发现 IdP 后生成 state 与 PKCE verifier，落一条一次性记录并重定向到 IdP",
    ("GET", "/api/v1/auth/oidc/callback"): "OIDC 回调端点：校验 state 与 PKCE 后建档或登录并下发会话。<strong>需在 IdP 侧登记为回调地址</strong>",

    ("GET", "/api/v1/templates"): "分页列出模板，支持关键词搜索、分组过滤与游标翻页",
    ("POST", "/api/v1/templates"): "新建模板（Template Schema v1）",
    ("GET", "/api/v1/templates/{id}"): "获取单个模板完整定义",
    ("PUT", "/api/v1/templates/{id}"): "更新模板名称、描述、定义或分组",
    ("DELETE", "/api/v1/templates/{id}"): "删除模板",
    ("POST", "/api/v1/templates/import-qd-har"): "导入旧 QD 的 HAR 生成模板并落库",
    ("POST", "/api/v1/templates/validate-qd-har"): "只校验 HAR 能否导入，不写库；WebUI 用它做实时预检",
    ("PUT", "/api/v1/templates/{id}/qd-har"): "覆盖模板的 QD HAR 内容",
    ("POST", "/api/v1/templates/{id}/publish"): "提交发布申请，进入管理员审批队列",
    ("DELETE", "/api/v1/templates/{id}/publish"): "撤回申请或从公共模板市场下架",

    ("GET", "/api/v1/tasks"): "列出当前用户可见的任务",
    ("POST", "/api/v1/tasks"): "新建任务，绑定模板或直接配置 HTTP 请求",
    ("POST", "/api/v1/tasks/batch"): "批量执行启停、删除等操作，返回逐条结果",
    ("GET", "/api/v1/task-groups"): "列出任务分组，用于 WebUI 侧边筛选",
    ("GET", "/api/v1/tasks/{id}"): "获取任务详情，含上次运行状态与错误",
    ("PUT", "/api/v1/tasks/{id}"): "更新任务配置",
    ("DELETE", "/api/v1/tasks/{id}"): "删除任务",
    ("POST", "/api/v1/tasks/{id}/run"): "立即触发一次运行；已返回 202 表示入队，不等待执行完成",
    ("GET", "/api/v1/tasks/{id}/runs"): "列出该任务的运行历史",
    ("DELETE", "/api/v1/tasks/{id}/runs"): "清空该任务的运行历史",

    ("GET", "/api/v1/runs/{id}/steps"): "列出一次运行的每个步骤：请求、响应与提取到的变量",
    ("GET", "/api/v1/runs/{id}/steps/live"): "WebSocket 实时推送步骤与状态变更",
    ("POST", "/api/v1/runs/{id}/cancel"): "请求取消运行；由执行器在下一个可中断点停下",
    ("DELETE", "/api/v1/runs/{id}"): "删除单条运行记录",
    ("DELETE", "/api/v1/runs"): "清空当前用户的全部运行记录",

    ("GET", "/api/v1/subscriptions"): "列出已订阅的模板仓库",
    ("POST", "/api/v1/subscriptions"): "新增模板订阅",
    ("GET", "/api/v1/subscriptions/{id}"): "获取单个订阅",
    ("PUT", "/api/v1/subscriptions/{id}"): "更新订阅地址或启停状态",
    ("DELETE", "/api/v1/subscriptions/{id}"): "删除订阅",
    ("POST", "/api/v1/subscriptions/{id}/sync"): "立即同步一次，异步执行",
    ("GET", "/api/v1/subscriptions/{id}/syncs"): "列出同步历史与结果",
    ("GET", "/api/v1/subscriptions/{id}/sync/live"): "WebSocket 推送同步进度",

    ("GET", "/api/v1/notification-channels"): "列出通知渠道",
    ("POST", "/api/v1/notification-channels"): "新建通知渠道",
    ("GET", "/api/v1/notification-channels/{id}"): "获取渠道配置",
    ("PUT", "/api/v1/notification-channels/{id}"): "更新渠道配置",
    ("DELETE", "/api/v1/notification-channels/{id}"): "删除渠道，同时解除任务绑定",
    ("GET", "/api/v1/tasks/{id}/notification-actions"): "列出任务已绑定的通知渠道与触发时机",
    ("POST", "/api/v1/tasks/{id}/notification-actions"): "把渠道绑定到任务，指定在成功 / 失败 / 总是时推送",
    ("POST", "/api/v1/notification-actions/batch"): "批量把同一渠道绑定到多个任务",
    ("DELETE", "/api/v1/notification-actions/{id}"): "解除绑定",

    ("GET", "/api/v1/public-templates"): "列出公共模板市场已通过审批的模板",
    ("POST", "/api/v1/public-templates/{id}/copy"): "把公共模板复制到自己的模板库",
    ("GET", "/api/v1/push-requests"): "列出我提交的发布申请及审批结果",
    ("POST", "/api/v1/push-requests"): "提交发布申请，附说明给管理员",

    ("GET", "/api/v1/plugins"): "列出已注册的外部插件",
    ("POST", "/api/v1/plugins"): "注册插件二进制与能力声明",
    ("GET", "/api/v1/plugins/{id}"): "获取插件配置",
    ("PUT", "/api/v1/plugins/{id}"): "更新插件配置或启停",
    ("DELETE", "/api/v1/plugins/{id}"): "删除插件",
    ("POST", "/api/v1/plugins/{id}/invoke"): "同步调用插件，返回其输出",

    ("GET", "/api/v1/admin/users"): "列出全部用户",
    ("PATCH", "/api/v1/admin/users/{id}"): "修改角色或启禁用状态",
    ("DELETE", "/api/v1/admin/users/{id}"): "删除用户及其数据",
    ("GET", "/api/v1/admin/push-requests"): "列出待审批的公共模板发布申请",
    ("POST", "/api/v1/admin/push-requests/{id}/decision"): "通过或驳回发布申请",
    ("GET", "/api/v1/admin/settings"): "列出站点级运行时设置",
    ("GET", "/api/v1/admin/settings/{key}"): "读取单个设置项",
    ("PUT", "/api/v1/admin/settings/{key}"): "写入设置项，热生效无需重启",
    ("GET", "/api/v1/admin/backup"): "导出数据库备份",
    ("POST", "/api/v1/admin/restore"): "从备份恢复，覆盖现有数据",
    ("DELETE", "/api/v1/admin/logs"): "按保留天数清理运行日志与审计日志",
}

# --------------------------------------------------------------------------
# 分组：显示顺序即列表顺序。prefixes 为路径前缀。
# --------------------------------------------------------------------------
GROUPS = [
    ("system", "系统与监控", []),
    ("auth", "认证与会话", ["/api/v1/auth/"]),
    ("templates", "模板", ["/api/v1/templates", "/api/v1/templates/{id}"]),
    ("tasks", "任务", ["/api/v1/tasks", "/api/v1/task-groups"]),
    ("runs", "运行记录", ["/api/v1/runs"]),
    ("subscriptions", "模板订阅", ["/api/v1/subscriptions"]),
    ("notifications", "通知渠道与绑定", ["/api/v1/notification-", "/api/v1/tasks/{id}/notification-actions"]),
    ("public", "公共模板与发布申请", ["/api/v1/public-templates", "/api/v1/push-requests"]),
    ("plugins", "外部插件", ["/api/v1/plugins"]),
    ("admin", "管理员", ["/api/v1/admin/"]),
]

# 精确匹配优先于前缀匹配：否则 /tasks/{id}/notification-actions 会被 tasks 组抢走
EXACT = {
    "/api/v1/tasks/{id}/notification-actions": "notifications",
    "/api/v1/openapi.json": "system",
    "/health": "system",
    "/ready": "system",
}

PERM_LABEL = {"public": ("公开", "perm-public"), "user": ("登录", "perm-user"), "admin": ("管理员", "perm-admin")}
METHOD_CLASS = {"GET": "m-get", "POST": "m-post", "PUT": "m-put", "DELETE": "m-del", "PATCH": "m-patch"}
WS_PATHS = {"/api/v1/runs/{id}/steps/live", "/api/v1/subscriptions/{id}/sync/live"}

MODEL_ORDER = ["Task", "Run", "Template", "User", "NotificationChannel", "NotificationAction",
               "PushRequest", "TemplateSubscription", "SubscriptionSync", "Plugin", "RunEvent", "ApiError"]

MODEL_NOTES = {
    "Task": "任务。读回的对象是 <code>CreateTask</code> 加上服务端生成的字段，因此 <code>id</code>、<code>created_at</code> 等只在响应中出现。",
    "Run": "一次任务运行。<code>lease_owner</code> / <code>lease_expires_at</code> 是崩溃恢复用的租约，非调度参数。",
    "Template": "模板。<code>definition</code>（原生 schema）与 <code>qd_har</code>（旧 QD HAR）二选一，由 <code>source_format</code> 标明。",
    "User": "用户。<code>role</code> 只有 <code>admin</code> 与 <code>user</code> 两档。",
    "NotificationChannel": "通知渠道。<code>kind</code> 决定 <code>config</code> 的结构，共 11 种渠道（webhook / custom_http / email + 8 种推送）。",
    "RunEvent": "WebSocket 推送的事件。<code>type</code> 为 <code>status</code>（状态变更）、<code>step</code>（步骤完成）或 <code>snapshot</code>（连接建立时的全量快照，用于补齐连上之前已产出的步骤）。",
    "TemplatePage": "模板列表的分页结果。<code>next_cursor</code> 为 null 时表示已到末页。",
    "ApiError": "所有 4xx / 5xx 响应的统一信封。<code>code</code> 是稳定的错误键，前端据此做本地化；<code>message</code> 为英文兜底。",
}


# ==========================================================================
# 1. 从源码解析路由与鉴权
# ==========================================================================
def _router_segments(api_rs: str) -> list[str]:
    """切出路由注册区间。

    路由注册在源码里分成两段，都要扫：
      - inner：API + SPA，从首个 ``Router::new()`` 到 ``let state = AppState {``
      - root ：``/health``、``/ready`` 探针，从 ``let mut root = Router::new()``
        到 ``root.with_state``。这两个探针被刻意留在根路径，不受
        ``QDRUST_BASE_PATH`` 影响，因此不在 inner 里。
    """
    specs = [
        ("Router::new()", ["let state = AppState {", ".with_state(AppState"]),
        ("let mut root = Router::new()", ["root.with_state", ".with_state(AppState"]),
    ]
    segments = []
    for start_anchor, end_anchors in specs:
        start = api_rs.find(start_anchor)
        if start < 0:
            print(f"  ! 跳过路由段：未找到起始锚点 {start_anchor!r}")
            continue
        end = -1
        for anchor in end_anchors:
            pos = api_rs.find(anchor, start + len(start_anchor))
            if pos > 0:
                end = pos
                break
        if end < 0:
            print(f"  ! 跳过路由段：未找到结束锚点 {end_anchors}")
            continue
        segments.append(api_rs[start:end])
    return segments


def _parse_route_calls(router_src: str) -> list[tuple[str, str, str]]:
    """扫出 ``(路径, 方法, handler)``。

    用括号平衡取出 ``.route()`` 的第二个参数，而不是靠行尾 lookahead——
    路由注册是多行链式调用，结尾形态不一（``;``、``.`` 续行、``if`` 块），
    lookahead 容易漏掉最后一条。
    """
    entries = []
    for m in re.finditer(r'\.route\(\s*"([^"]+)"\s*,', router_src):
        path = m.group(1)
        # 起点已位于 .route( 的参数列表内，故初始深度为 1——
        # 否则 get(x).put(y).delete(z) 这类链式注册会在第一个 ) 处提前收尾。
        depth = 1
        end = m.end()
        for j in range(m.end(), len(router_src)):
            ch = router_src[j]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    end = j
                    break
        spec = router_src[m.end() - 1:end + 1]
        for mm in re.finditer(r"(?:axum::routing::)?(get|post|put|patch|delete)\((\w+)\)", spec):
            entries.append((path, mm.group(1).upper(), mm.group(2)))
    return entries


def parse_routes(api_rs: str) -> dict[tuple[str, str], tuple[str, str]]:
    """返回 {(方法, 路径): (权限, handler)}。"""

    entries = []
    for segment in _router_segments(api_rs):
        entries.extend(_parse_route_calls(segment))

    def fn_body(name: str) -> str:
        m = re.search(r"\n(?:async )?fn " + re.escape(name) + r"\s*\(", api_rs)
        if not m:
            return ""
        i = api_rs.index("{", m.end())
        depth = 0
        for j in range(i, len(api_rs)):
            if api_rs[j] == "{":
                depth += 1
            elif api_rs[j] == "}":
                depth -= 1
                if depth == 0:
                    return api_rs[i:j + 1]
        return ""

    out = {}
    for path, method, handler in entries:
        body = fn_body(handler)
        if "require_admin" in body:
            perm = "admin"
        elif "require_session" in body or "AuthenticatedSession" in body:
            perm = "user"
        else:
            perm = "public"
        out[(method, path)] = (perm, handler)
    return out


# ==========================================================================
# 2. 读取 OpenAPI 明细
# ==========================================================================
def ref_name(obj) -> str | None:
    r = obj.get("$ref") if isinstance(obj, dict) else None
    return r.split("/")[-1] if r else None


def load_openapi(doc: dict, perms: dict) -> tuple[list[dict], dict]:
    METHODS = ["get", "post", "put", "patch", "delete"]

    def resolve(obj):
        n = ref_name(obj)
        if not n:
            return obj
        for sec in ("schemas", "requestBodies", "parameters", "responses"):
            if n in doc.get("components", {}).get(sec, {}):
                return doc["components"][sec][n]
        return obj

    ops = []
    for p, node in doc["paths"].items():
        shared = node.get("parameters", [])
        for m in METHODS:
            if m not in node:
                continue
            op = node[m]
            params = []
            for pr in shared + op.get("parameters", []):
                pr = resolve(pr)
                params.append({
                    "name": pr.get("name"), "in": pr.get("in"),
                    "required": bool(pr.get("required")),
                    "type": (pr.get("schema") or {}).get("type", "string"),
                })
            rbody = None
            if "requestBody" in op:
                rb = resolve(op["requestBody"])
                ct = list(rb.get("content", {}).keys())
                if ct:
                    rbody = ref_name(rb["content"][ct[0]].get("schema", {}))
            resps = []
            for code, r in sorted(op.get("responses", {}).items()):
                r = resolve(r)
                sch = None
                for _ct, c in (r.get("content") or {}).items():
                    sch = ref_name(c.get("schema", {})) or c.get("schema", {}).get("type")
                resps.append({"code": code, "desc": r.get("description", ""), "schema": sch})
            perm, handler = perms.get((m.upper(), p), ("user", "?"))
            ops.append({
                "method": m.upper(), "path": p, "opId": op.get("operationId", ""),
                "summary": op.get("summary", ""), "perm": perm, "handler": handler,
                "params": params, "body": rbody, "responses": resps,
            })

    # OpenAPI 不收录文档自身端点
    if not any(o["path"] == "/api/v1/openapi.json" for o in ops):
        ops.append({
            "method": "GET", "path": "/api/v1/openapi.json", "opId": "openapi",
            "summary": "", "perm": "public", "handler": "openapi",
            "params": [], "body": None,
            "responses": [{"code": "200", "desc": "OpenAPI document", "schema": None}],
        })

    # 文档漏收但源码已注册的端点，按源码补入（例如 DELETE /admin/users/{id}、
    # OIDC 登录相关端点）。补入清单会渲染到页面末尾的「与 OpenAPI 文档的差异」。
    known = {(o["method"], o["path"]) for o in ops}
    patched = []
    for (method, path), (perm, handler) in perms.items():
        if (method, path) in known:
            continue
        params = [
            {"name": seg[1:-1], "in": "path", "required": True, "type": "string"}
            for seg in path.split("/") if seg.startswith("{") and seg.endswith("}")
        ]
        ops.append({
            "method": method, "path": path, "opId": handler, "summary": "",
            "perm": perm, "handler": handler, "params": params, "body": None,
            "responses": [{"code": "204", "desc": "Success", "schema": None}],
        })
        patched.append((method, path, handler))
    return ops, doc.get("components", {}).get("schemas", {}), patched


# ==========================================================================
# 3. 渲染
# ==========================================================================
def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def type_str(sch) -> str:
    if not isinstance(sch, dict):
        return esc(str(sch))
    if "$ref" in sch:
        return sch["$ref"].split("/")[-1]
    for k in ("allOf", "oneOf", "anyOf"):
        if k in sch:
            sep = " &amp; " if k == "allOf" else " | "
            return sep.join(type_str(x) for x in sch[k])
    ty = sch.get("type")
    if ty == "array":
        return f"array&lt;{type_str(sch.get('items', {}))}>"
    if ty == "integer":
        return "int64" if sch.get("format") == "int64" else "int"
    if "enum" in sch:
        vals = ", ".join(str(x) for x in sch["enum"][:4])
        return f"enum: {vals}"
    return esc(str(ty or "any"))


def flatten(schemas: dict, name: str, depth: int = 0) -> tuple[dict, set]:
    v = schemas.get(name)
    if not v or depth > 3:
        return {}, set()
    props, req = {}, set()
    if "allOf" in v:
        for sub in v["allOf"]:
            if isinstance(sub, dict) and "$ref" in sub:
                p2, r2 = flatten(schemas, sub["$ref"].split("/")[-1], depth + 1)
                props.update(p2)
                req |= r2
            elif isinstance(sub, dict):
                props.update(sub.get("properties", {}))
                req |= set(sub.get("required", []))
    props.update(v.get("properties", {}))
    req |= set(v.get("required", []))
    return props, req


def group_of(path: str) -> str:
    if path in EXACT:
        return EXACT[path]
    for key, _title, prefixes in GROUPS:
        if any(path.startswith(pre) for pre in prefixes):
            return key
    return "system"


def build_part(ops: list[dict], schemas: dict, version: str,
               patched: list[tuple[str, str, str]]) -> str:
    buckets: dict[str, list] = {key: [] for key, _, _ in GROUPS}
    for op in ops:
        buckets.setdefault(group_of(op["path"]), []).append(op)
    for key in buckets:
        buckets[key].sort(key=lambda o: (o["path"], METHOD_ORDER.index(o["method"])))

    tables = []
    for key, title, _ in GROUPS:
        rows = buckets.get(key, [])
        if not rows:
            continue
        out = [
            f'                <h3 id="ep-{key}">{title} <span class="count">{len(rows)}</span></h3>',
            "                    <table>",
            "                        <thead><tr><th>方法</th><th>路径</th><th>权限</th><th>说明</th></tr></thead>",
            "                        <tbody>",
        ]
        for op in rows:
            m, p = op["method"], op["path"]
            mdisp = '<code class="m-get">WS</code>' if p in WS_PATHS else f'<code class="{METHOD_CLASS.get(m, "")}">{m}</code>'
            label, pcls = PERM_LABEL[op["perm"]]
            desc = DESC.get((m, p), esc(op["summary"]))
            out.append(
                f'                            <tr><td>{mdisp}</td>'
                f'<td><code>{esc(p)}</code></td>'
                f'<td><span class="perm {pcls}">{label}</span></td>'
                f'<td>{desc}</td></tr>'
            )
        out += ["                        </tbody>", "                    </table>", ""]
        tables.append("\n".join(out))

    models = []
    for name in MODEL_ORDER:
        props, req = flatten(schemas, name)
        if not props:
            continue
        models.append(f'                <h3 id="model-{name.lower()}"><code>{name}</code></h3>')
        if name in MODEL_NOTES:
            models.append(f"                <p>{MODEL_NOTES[name]}</p>")
        models += [
            "                    <table>",
            '                        <thead><tr><th>字段</th><th>类型</th><th>必填</th></tr></thead>',
            "                        <tbody>",
        ]
        for k, p in props.items():
            mark = "是" if k in req else '<span class="dim">否</span>'
            models.append(f'                            <tr><td><code>{k}</code></td>'
                          f'<td>{type_str(p)}</td><td>{mark}</td></tr>')
        models += ["                        </tbody>", "                    </table>", ""]

    perm_count = Counter(op["perm"] for op in ops)
    group_count = {key: len(buckets.get(key, [])) for key, _, _ in GROUPS}
    stats_rows = "\n".join(
        f'                            <tr><td><a href="#ep-{key}">{title}</a></td><td>{group_count[key]}</td>'
        f'<td>{sum(1 for o in buckets[key] if o["perm"] == "public")}</td>'
        f'<td>{sum(1 for o in buckets[key] if o["perm"] == "user")}</td>'
        f'<td>{sum(1 for o in buckets[key] if o["perm"] == "admin")}</td></tr>'
        for key, title, _ in GROUPS if group_count.get(key)
    )

    n = len(ops)
    if patched:
        items = "\n".join(
            f'                    <li><code>{esc(m)} {esc(p)}</code> —— 源码已注册'
            f'（handler <code>{esc(h)}</code>），但 OpenAPI 文档未收录。本页已补上。</li>'
            for m, p, h in sorted(patched)
        )
        notes_body = (
            "                <p>\n"
            "                    本页以 <code>crates/qdrust-server/src/api.rs</code> 的路由注册为准。"
            f"比对内嵌文档后发现 <strong>{len(patched)} 处</strong>遗漏：\n"
            "                </p>\n"
            "                <ul>\n" + items + "\n"
            "                </ul>\n"
            "                <p>若你用文档生成客户端 SDK，这些端点需要手动补。</p>"
        )
    else:
        notes_body = (
            "                <p>\n"
            "                    本页以 <code>crates/qdrust-server/src/api.rs</code> 的路由注册为准，"
            "与内嵌 OpenAPI 文档比对后<strong>没有发现遗漏</strong>。\n"
            "                </p>"
        )

    return f"""                <h1 class="text-3xl md:text-4xl font-bold text-gray-900 mb-3">API 接口</h1>
                <p class="text-lg text-gray-600 mb-6">
                    qdrust 服务端的完整 REST 契约：<strong>{n} 个端点</strong>，覆盖认证、模板、任务调度、运行记录、订阅同步、通知、插件与站点管理。
                </p>
                <div class="mb-10">
                    <span class="badge badge-dark">v{version}</span>
                    <span class="badge">REST · JSON</span>
                    <span class="badge">OpenAPI 3.1</span>
                    <span class="badge">Cookie + CSRF</span>
                </div>

                <div class="callout">
                    <div class="callout-title">机器可读版本</div>
                    <p>
                        服务内嵌了同一份契约的 OpenAPI 3.1 文档，运行时可直接取用：<code>GET /api/v1/openapi.json</code>。
                        把它丢进 Swagger UI 或导入 Postman 即可获得可交互的接口调试台。本页内容由该文档与 <code>crates/qdrust-server/src/api.rs</code> 共同核对生成。
                    </p>
                </div>

                <h2 id="overview">概览</h2>
                <p>
                    所有业务接口挂在 <code>/api/v1</code> 下，请求与响应一律 <code>application/json</code>。
                    非 <code>/api</code> 前缀的路径由前端静态资源兜底，因此拼错接口会先命中 SPA 的 <code>index.html</code>——只有带 <code>/api</code> 前缀却不存在时，才返回统一的 404 信封。
                </p>
                    <table>
                        <thead><tr><th>资源</th><th>端点数</th><th>公开</th><th>需登录</th><th>需管理员</th></tr></thead>
                        <tbody>
{stats_rows}
                            <tr><td><strong>合计</strong></td><td><strong>{n}</strong></td><td><strong>{perm_count["public"]}</strong></td><td><strong>{perm_count["user"]}</strong></td><td><strong>{perm_count["admin"]}</strong></td></tr>
                        </tbody>
                    </table>

                <h2 id="auth">认证与会话</h2>
                <p>
                    认证走 <strong>Cookie</strong>，不使用 Bearer Token。登录成功后服务端下发两个 Cookie：
                </p>
                    <table>
                        <thead><tr><th>Cookie</th><th>属性</th><th>作用</th></tr></thead>
                        <tbody>
                            <tr><td><code>qd_session</code></td><td><code>HttpOnly</code> · <code>SameSite=Strict</code></td><td>会话令牌，前端脚本读不到，服务端只存其 SHA-256</td></tr>
                            <tr><td><code>qd_csrf</code></td><td><code>SameSite=Strict</code></td><td>CSRF 令牌，前端可读，需回写到请求头</td></tr>
                        </tbody>
                    </table>
                <p>
                    <strong>写操作需带 CSRF 头</strong>：<code>POST</code> / <code>PUT</code> / <code>PATCH</code> / <code>DELETE</code> 必须携带
                    <code>x-csrf-token</code>，其值与 <code>qd_csrf</code> Cookie 完全一致。服务端会做两件事——比对 Cookie 与头是否相同，再校验其哈希是否与会话中记录的相符，任一不符即 <code>403 csrf_validation_failed</code>。比对用常量时间，不泄漏时序信息。
                </p>
                <pre><code># 浏览器里取出 CSRF Cookie 并回写
curl -X POST http://localhost:5000/api/v1/tasks \\
  -b "qd_session=$SESSION; qd_csrf=$CSRF" \\
  -H "x-csrf-token: $CSRF" \\
  -H "Content-Type: application/json" \\
  -d '{{"name":"签到","cron":"0 9 * * *","url":"https://example.com"}}'</code></pre>

                <h3 id="auth-levels">三种权限级别</h3>
                    <table>
                        <thead><tr><th>级别</th><th>数量</th><th>判定方式</th></tr></thead>
                        <tbody>
                            <tr><td><span class="perm perm-public">公开</span></td><td>{perm_count["public"]}</td><td>不校验会话。含探针、登录注册、密码重置与 HAR 预检</td></tr>
                            <tr><td><span class="perm perm-user">登录</span></td><td>{perm_count["user"]}</td><td>校验 <code>qd_session</code>；数据按 <code>owner_id</code> 隔离，看不到他人资源</td></tr>
                            <tr><td><span class="perm perm-admin">管理员</span></td><td>{perm_count["admin"]}</td><td>在会话有效的基础上再要求 <code>role == "admin"</code>，否则 <code>403 admin_required</code></td></tr>
                        </tbody>
                    </table>

                <h2 id="conventions">通用约定</h2>

                <h3 id="error-envelope">错误信封</h3>
                <p>
                    所有非 2xx 响应结构一致。<strong><code>code</code> 是稳定的错误键</strong>，前端据此做本地化，<code>message</code> 只是英文兜底文案；
                    <code>field_errors</code> 给出逐字段的校验失败原因；<code>request_id</code> 用于对照服务端日志。内部异常细节只写日志，不出现在响应里。
                </p>
                <pre><code>{{
  "code": "validation_error",
  "message": "cron expression is invalid",
  "field_errors": {{ "cron": ["must be a valid cron expression"] }},
  "request_id": "7f3c1e9a2b8d4f6e"
}}</code></pre>
                    <table>
                        <thead><tr><th>Code</th><th>状态</th><th>含义</th></tr></thead>
                        <tbody>
                            <tr><td><code>api_endpoint_not_found</code></td><td>404</td><td><code>/api</code> 下无此路由</td></tr>
                            <tr><td><code>task_not_found</code></td><td>404</td><td>任务不存在</td></tr>
                            <tr><td><code>run_not_found</code></td><td>404</td><td>运行不存在，或不属于当前用户</td></tr>
                            <tr><td><code>template_not_found</code></td><td>404</td><td>模板不存在</td></tr>
                            <tr><td><code>validation_error</code></td><td>422</td><td>请求体或领域校验失败，看 <code>field_errors</code></td></tr>
                            <tr><td><code>authentication_required</code></td><td>401</td><td>会话缺失、过期、被吊销或账号已禁用</td></tr>
                            <tr><td><code>invalid_credentials</code></td><td>401</td><td>用户名或密码不对</td></tr>
                            <tr><td><code>csrf_validation_failed</code></td><td>403</td><td>CSRF 三元组（Cookie / 头 / 会话哈希）校验失败</td></tr>
                            <tr><td><code>admin_required</code></td><td>403</td><td>需要管理员角色</td></tr>
                            <tr><td><code>bootstrap_already_completed</code></td><td>409</td><td>首个管理员已存在，不可重复初始化</td></tr>
                            <tr><td><code>login_rate_limited</code></td><td>429</td><td>该用户名登录失败过多，暂时限流</td></tr>
                            <tr><td><code>internal_error</code></td><td>500</td><td>未预期的内部错误</td></tr>
                        </tbody>
                    </table>

                <h3 id="pagination">分页与限流</h3>
                <p>
                    列表接口用<strong>游标分页</strong>而非 offset：<code>limit</code> 默认 50、上限 200，响应回 <code>next_cursor</code>，为 <code>null</code> 即末页。
                    这样在频繁写入的场景下翻页不会漏项或重复。
                </p>
                <p>
                    登录接口单独限流：同一用户名在窗口内失败超过阈值即返回 <code>429 login_rate_limited</code>，成功一次即清零。
                    阈值与窗口由启动参数配置，目的是挡住针对固定用户名的暴力枚举。
                </p>

                <h2 id="endpoints">接口一览</h2>
                <p>
                    下表按资源分组列出全部 {n} 个端点。标 <code>WS</code> 的是 WebSocket 升级端点，其余为标准 HTTP。
                    路径参数写作 <code>{{id}}</code>。
                </p>

{chr(10).join(tables)}
                <h2 id="websocket">WebSocket 实时接口</h2>
                <p>
                    两个实时端点都用<strong>普通 HTTP 握手升级</strong>，因此仍走同一套 Cookie 鉴权——浏览器可直接连，非浏览器客户端带上 <code>qd_session</code> 即可。
                    服务端以文本帧推送 JSON，客户端无需发送任何消息。
                </p>
                    <table>
                        <thead><tr><th>端点</th><th>推送内容</th></tr></thead>
                        <tbody>
                            <tr><td><code>/api/v1/runs/{{id}}/steps/live</code></td><td>该次运行的步骤明细与状态变更</td></tr>
                            <tr><td><code>/api/v1/subscriptions/{{id}}/sync/live</code></td><td>模板订阅的同步进度</td></tr>
                        </tbody>
                    </table>
                <p>
                    帧体即 <code>RunEvent</code>：<code>type</code> 为 <code>status</code>（运行状态变更）、<code>step</code>（单个步骤完成）或 <code>snapshot</code>（连接建立时的全量快照，用于补齐连上之前已产出的步骤）。
                    <strong>先收 <code>snapshot</code> 再收增量</strong>，客户端就能在任意时刻接入而不丢数据。
                </p>
                <pre><code>{{"type":"snapshot","run_id":42,"status":"running"}}
{{"type":"step","run_id":42,"step":{{"index":0,"url":"https://example.com","status":200}}}}
{{"type":"status","run_id":42,"status":"success"}}</code></pre>

                <h2 id="models">数据模型</h2>
                <p>
                    以下为接口间流转的主要对象，字段取自 OpenAPI 的 <code>components.schemas</code>。
                </p>

{chr(10).join(models)}
                <h2 id="examples">一次完整调用</h2>
                <p>
                    从初始化管理员到拿到运行结果，串起最小可用链路：
                </p>
                <pre><code># 1) 初始化首个管理员（只能成功一次）
curl -c jar.txt -X POST http://localhost:5000/api/v1/auth/bootstrap \\
  -H "Content-Type: application/json" \\
  -d '{{"username":"admin","password":"a-long-enough-password"}}'

# 2) 取出 CSRF Cookie
CSRF=$(grep qd_csrf jar.txt | awk '{{print $7}}')

# 3) 导入一份旧 QD 的 HAR 模板
curl -b jar.txt -X POST http://localhost:5000/api/v1/templates/import-qd-har \\
  -H "x-csrf-token: $CSRF" -H "Content-Type: application/json" \\
  -d '{{"name":"每日签到","har":{{/* 抓包得到的 HAR */}}}}'

# 4) 建任务，绑定模板并配 cron
curl -b jar.txt -X POST http://localhost:5000/api/v1/tasks \\
  -H "x-csrf-token: $CSRF" -H "Content-Type: application/json" \\
  -d '{{"name":"签到","cron":"0 9 * * *","template_id":1,"timezone":"Asia/Shanghai"}}'

# 5) 立刻跑一次（202 表示已入队，不等待执行）
curl -b jar.txt -X POST http://localhost:5000/api/v1/tasks/1/run \\
  -H "x-csrf-token: $CSRF"

# 6) 查运行结果
curl -b jar.txt http://localhost:5000/api/v1/tasks/1/runs

# 7) 看某个 run 的每一步
curl -b jar.txt http://localhost:5000/api/v1/runs/7/steps</code></pre>
                <div class="callout">
                    <div class="callout-title">注意 202 与 200 的区别</div>
                    <p>
                        触发运行返回 <strong>202 Accepted</strong> 只表示已入队。要确认执行结果，得再去查
                        <code>/api/v1/tasks/{{id}}/runs</code> 或订阅 <code>/steps/live</code>——这是异步执行框架的典型约定，别把 202 当成执行成功。
                    </p>
                </div>

                <h2 id="notes">与 OpenAPI 文档的差异</h2>
{notes_body}
                <div class="wiki-meta">
                    <span>基于 qdrust v{version} 服务端路由与 OpenAPI 3.1 文档整理</span>
                    <span>共 {n} 个端点</span>
                </div>
"""


# ==========================================================================
# 4. 套壳生成最终页面
# ==========================================================================
MAIN_CLOSE = "</main>"
TITLE = "API 接口 | qdrust Wiki"
# {n} 在生成时替换为实际端点数，避免端点增减后描述失真
DESCRIPTION = ("qdrust 完整 REST API 参考：{n} 个端点的路径、权限与用途，Cookie 与 CSRF 认证、"
               "错误信封与错误码、WebSocket 实时接口、核心数据模型与调用示例。")


def build_page(shell: str, part: str, endpoint_count: int) -> str:
    desc = DESCRIPTION.format(n=endpoint_count)
    out = re.sub(r"<title>.*?</title>", f"<title>{TITLE}</title>", shell, count=1)
    out = re.sub(r'(<meta name="description" content=")[^"]*(")',
                 lambda m: m.group(1) + desc + m.group(2), out, count=1)
    out = re.sub(r'(<link rel="canonical" href=")[^"]*(")',
                 lambda m: m.group(1) + "https://callmelins.github.io/pages/qdrust/api.html" + m.group(2),
                 out, count=1)

    def fix_nav(m: re.Match) -> str:
        href = m.group(1)
        cls = "wiki-nav-link is-active" if href == "api.html" else "wiki-nav-link"
        return f'<a href="{href}" class="{cls}">'

    out = re.sub(r'<a href="([a-z-]+\.html)" class="wiki-nav-link[^"]*">', fix_nav, out)
    # 用正则而非固定字符串：外壳的 <main> 可能被编辑器注入额外属性
    m = re.search(r"<main[^>]*>", out)
    if not m:
        raise ValueError("index.html 外壳里找不到 <main> 标记")
    start = m.end()
    end = out.index(MAIN_CLOSE, start)
    return out[:start] + "\n" + part.rstrip("\n") + "\n            " + out[end:]


def main() -> int:
    ap = argparse.ArgumentParser(description="重新生成 qdrust API 参考页")
    ap.add_argument("--qdrust", default=str(DEFAULT_QDRUST), help="qdrust 仓库路径")
    args = ap.parse_args()

    qdrust = pathlib.Path(args.qdrust)
    api_rs = qdrust / "crates" / "qdrust-server" / "src" / "api.rs"
    openapi = qdrust / "docs" / "openapi-v1.json"
    for f in (api_rs, openapi):
        if not f.exists():
            print(f"ERROR: 找不到 {f}", file=__import__("sys").stderr)
            return 1

    source = api_rs.read_text(encoding="utf-8")
    perms = parse_routes(source)
    doc = json.loads(openapi.read_text(encoding="utf-8"))
    ops, schemas, patched = load_openapi(doc, perms)
    version = doc.get("info", {}).get("version", "0.0.0")

    missing = [f"{m} {p}" for (m, p) in perms if not any(o["method"] == m and o["path"] == p for o in ops)]
    if missing:
        print("WARN: 源码有、文档无（已按源码补入）:", missing)

    part = build_part(ops, schemas, version, patched)
    html = build_page(SHELL.read_text(encoding="utf-8"), part, len(ops))
    TARGET.write_text(html, encoding="utf-8")

    counts = Counter(op["perm"] for op in ops)
    print(f"已写出 {TARGET} ({len(html)} chars)")
    print(f"端点 {len(ops)} 个：公开 {counts['public']} / 需登录 {counts['user']} / 管理员 {counts['admin']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
