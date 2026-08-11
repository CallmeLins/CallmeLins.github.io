---
title: "通过 Cloudflare mTLS 用户端凭证实现全站私有访问"
date: 2026-08-11
tags: ["运维", "Cloudflare", "mTLS"]
---


> **适用环境**：域名托管于 Cloudflare（DNS 开启小黄云代理）· 免费套餐可用 · 需 Chrome / Safari 等支持 PFX 导入的浏览器
> **核心功能**：mTLS 双向 TLS 客户端证书验证，实现「无证书完全无法访问」的全站私有访问
> **关键原理**：在 TLS 握手层拦截未授权流量，配合 WAF 自定义规则完成证书校验与防护豁免双层校验

## 前言

很多自建后台、私有面板、NodeWarden、私有博客仅允许本人访问，单纯依靠账号密码极易遭受暴力破解、扫描攻击。常规人机验证、IP 黑白名单存在局限性：更换网络、动态 IP 会直接失效。

Cloudflare 免费提供 **mTLS 双向 TLS 客户端证书验证**，实现「无证书完全无法访问网站」，从 TLS 握手层拦截所有未授权流量，搭配 WAF 自定义规则完成双层安全校验，适合需要完全私有化、零外部访客的站点。

本文基于实测完整流程，区分传统「仅保护后台」方案与本文「全站强制 mTLS 私有访问」方案，完整覆盖证书生成、PFX 打包、浏览器导入、WAF 规则配置、常见踩坑排查。

## 一、mTLS 原理简介

常规 TLS 仅客户端验证服务器证书；**mTLS 双向 TLS** 增加客户端证书校验流程：

1. 客户端发起 HTTPS 连接
2. Cloudflare 返回站点服务端证书，客户端校验
3. Cloudflare 主动向浏览器索要**客户端证书**
4. 浏览器出示已安装的合法证书
5. Cloudflare 校验证书有效性、是否吊销
6. 校验通过才放行 HTTP 流量；校验失败直接断开 TCP 连接 / 返回 403

优势：

- 攻击者无 PFX 证书，连网站握手阶段都无法通过，不存在爆破入口
- 免费套餐可用，无需 Zero Trust 付费功能
- 可搭配 WAF 跳过机器人检测、托管防护，避免本人访问被误拦截

## 二、前置要求

1. 域名托管在 Cloudflare，DNS 记录开启**小黄云代理**（灰色云 DNS 直连不支持 mTLS）
2. Chrome、Safari 等主流浏览器（仅支持导入 PFX 格式证书）
3. Windows / Linux 任选其一打包公私钥生成 PFX

## 三、步骤 1：添加受保护主机（关键踩坑点）

进入面板：`SSL/TLS → 客户端证书`

1. 点击**编辑（Hosts 主机名）**
2. 添加需要强制私有访问的域名
   - 裸域名：填写完整 `example.com`
   - 子域名：填写 `www.example.com`、`admin.example.com`
3. 重要限制：**Hosts 不支持通配符 `*.example.com`**，所有需要保护的域名必须逐条手动添加
4. 保存主机列表

> 踩坑提醒：域名未添加至 Hosts 列表时，CF 不会向浏览器索要客户端证书，`cf.tls_client_auth.cert_verified` 永远为 false，直接被拦截，表现为「浏览器已装证书，但访问直接提示连接意外终止」。

## 四、步骤 2：生成客户端证书公私钥

1. 客户端证书页面点击**建立凭证**
2. 加密算法默认 RSA（兼容性最佳），有效期按需设置（推荐 1 年，到期重新生成）
3. 确认创建，页面会输出两段文本：
   - 凭证（公钥 `.crt`）
   - 私密金钥（私钥 `.key`）

> 页面关闭后密钥无法找回，复制完整内容保存，不要遗漏头尾 `-----BEGIN` / `-----END-----` 标记。

## 五、步骤 3：公私钥合并为 PFX 证书（浏览器导入专用）

### 5.1 Windows 用户（PowerShell）

1. 桌面空白处右键 → 在此处打开 PowerShell 窗口
2. 创建公钥文件

```powershell
notepad cert.crt
```

粘贴公钥完整内容，保存关闭

3. 创建私钥文件

```powershell
notepad cert.key
```

粘贴私钥完整内容，保存关闭

4. 合并生成加密 PFX（访问浏览器需要输入该密码）

```powershell
certutil -mergepfx cert.crt cert.pfx
```

连续两次输入自定义证书密码，桌面生成 `cert.pfx` 文件。

### 5.2 Linux / macOS 用户（OpenSSL）

```bash
# 分别保存 crt、key 文件后执行
openssl pkcs12 -export -out cert.pfx -inkey cert.key -in cert.crt
```

设置证书加密密码，输出 `cert.pfx`。

## 六、步骤 4：浏览器导入 PFX 客户端证书

### 6.1 Chrome Windows

1. 地址栏打开：`chrome://certificate-manager/`
2. 侧边栏选择**您的凭证** → 管理从 Windows 汇入的凭证
3. 点击「汇入」，选择桌面 `cert.pfx`，输入打包时设置的证书密码
4. 一路下一步完成导入，无需修改存储位置

### 6.2 iOS Safari（移动端访问）

1. 将 pfx 文件通过系统自带「邮件」App 发送至 iPhone
2. 手机打开邮件点击附件，弹出「已下载描述档」
3. 设置 → 已下载描述档 → 安装，依次输入锁屏密码、证书加密密码
4. 仅 Safari 支持客户端证书，Chrome iOS 暂不兼容 mTLS 弹窗。

## 七、步骤 5：WAF 自定义规则配置（全站强制私有访问）

进入面板：`安全性 → WAF → 自订规则 → 建立规则`

> 作用域提醒：若同一 Cloudflare Zone 下还有其他公开子域名（如官网、博客），务必在表达式开头用 `http.host in {"..."}` 限定目标主机，否则 Block / Skip 规则会误伤同 Zone 的其他站点。下文示例均以 `example.com`、`admin.example.com` 两个私有主机为例，请按需替换为自己的域名。

### 7.1 规则顺序核心逻辑

拦截 Block 规则放**第一位**（尽早丢弃非法流量），Skip 跳过规则放第二位；Block 命中直接终止请求，Skip 仅跳过 WAF 防护组件，不会中断连接。

### 7.2 规则 1：强制执行 mTLS 身份验证【阻止】（优先级 1）

- 规则名称：强制执行 mTLS 身份验证 [阻止]
- 表达式（切换至「编辑表达式」手写，可视化界面无 `cert_revoked` 字段）

```text
(http.host in {"example.com" "admin.example.com"}) and ((not cf.tls_client_auth.cert_verified) or (cf.tls_client_auth.cert_revoked))
```

- 动作：阻止（Block）
- 逻辑说明：
  1. 未提交有效客户端证书 → 拦截全站所有访问
  2. 证书已被后台吊销 → 无论任何页面全部拦截

> 修复原版教程漏洞：CF 默认吊销证书后 `cert_verified` 仍为 true，必须增加 `cf.tls_client_auth.cert_revoked` 判断防止作废证书访问。

### 7.3 规则 2：合法证书跳过全部 WAF 防护【跳过】（优先级 2）

- 规则名称：强制执行 mTLS 身份验证 [跳过]
- 表达式

```text
(http.host in {"example.com" "admin.example.com"}) and (cf.tls_client_auth.cert_verified and not cf.tls_client_auth.cert_revoked)
```

- 动作：跳过（Skip）
- 跳过组件：全部勾选（超级自动程序攻击模式、托管 WAF 规则等）
- 逻辑说明：持有有效未吊销证书，自动跳过机器人校验、防火墙拦截，本人访问不会触发人机验证、5 秒攻击检测页面。

### 7.4 完整规则排序

1. 【阻止】无证书 / 吊销证书全站拦截
2. 【跳过】合法证书豁免所有 WAF 检测

## 八、访问测试与现象说明

1. 清空浏览器缓存、重启浏览器，访问私有域名
2. 正常生效表现：浏览器弹出「选择客户端证书」弹窗，选中导入的证书即可正常打开网站
3. 异常现象 1：直接提示「连接意外终止 / NodeWarden 意外终止连接」
   - 原因：访问域名未添加到 SSL/TLS 客户端证书 Hosts 列表，CF 不索要证书，握手直接断开
4. 异常现象 2：弹出证书选择，但选中后返回 403
   - 排查：PFX 公私钥复制不全、证书已在后台吊销、域名填写错误
5. 验证规则生效：WAF 安全事件查看计数，Skip 规则计数大于 0 代表证书校验成功

## 结语

借助 Cloudflare 免费 mTLS 客户端证书，可搭建硬件级私有访问门槛，双重 TLS 校验配合 WAF 规则彻底隔绝外部扫描与爆破。相比密码、IP 白名单，证书认证不存在泄露、动态 IP 失效问题，适合各类自建私有服务长期加固。如需兼顾公开访客，可调整规则仅对后台路径开启 mTLS 校验，平衡安全性与访问便捷性。

## 参考文章

- [Cloudflare mTLS 用户端凭证保护博客登录页面](https://www.liups.net/2025/06/cloudflare-mtls-%e7%94%a8%e6%88%b7%e7%ab%af%e5%87%ad%e8%af%81%e4%bf%9d%e6%8a%a4%e5%8d%9a%e5%ae%a2%e7%99%bb%e5%85%a5%e9%a1%b5%e9%9d%a2/#mtls-rules)
