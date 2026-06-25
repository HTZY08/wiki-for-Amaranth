--- frontmatter ---
---
sidebar_position: 23
title: "Microsoft Graph Webhook 监听器"
description: "在 Hermes 中接收 Microsoft Graph 变更通知（会议、日历、聊天等）"
---

--- body ---
# Microsoft Graph Webhook 监听器

`msgraph_webhook` 网关平台是一个入站事件监听器。它使 Hermes 能够接收来自 Microsoft Graph 的**变更通知**——例如"Teams 会议已结束"、"新消息已到达此聊天"、"此日历事件已更新"。这与 `teams` 平台（用户可与之交互的聊天机器人）不同——这是 M365 主动告知 Hermes 发生了某些事件，而非用户操作。

当前主要消费者是 Teams 会议摘要管道：Graph 在会议生成转录时发送通知，管道获取转录内容，Hermes 将摘要发布回 Teams。其他 Graph 资源（`/chats/.../messages`、`/users/.../events`）使用相同的监听器——管道消费者通过各自的 PR 接入。

## 前提条件

- Microsoft Graph 应用程序凭据——[注册一个 Microsoft Graph 应用程序](/guides/microsoft-graph-app-registration)
- 一个 Microsoft Graph 可访问的**公共 HTTPS URL**（Graph 不会调用私有端点）。开发隧道可用于测试；生产环境需要拥有有效证书的真实域名。
- 一个强共享密钥用作 `clientState` 值。使用 `openssl rand -hex 32` 生成，并将其放入 `~/.hermes/.env` 中的 `MSGRAPH_WEBHOOK_CLIENT_STATE`。

## 快速开始

最小 `~/.hermes/config.yaml` 配置：

```yaml
platforms:
  msgraph_webhook:
    enabled: true
    extra:
      host: 127.0.0.1
      port: 8646
      client_state: "replace-with-a-strong-secret"
      accepted_resources:
        - "communications/onlineMeetings"
```

或者通过 `~/.hermes/.env` 中的环境变量配置（启动时自动合并）：

```bash
MSGRAPH_WEBHOOK_ENABLED=true
MSGRAPH_WEBHOOK_PORT=8646
MSGRAPH_WEBHOOK_CLIENT_STATE=<generate-with-openssl-rand-hex-32>
MSGRAPH_WEBHOOK_ACCEPTED_RESOURCES=communications/onlineMeetings
```

注意：绑定主机从 `config.yaml` 的 `extra.host` 读取（参见上方示例）；没有 `MSGRAPH_WEBHOOK_HOST` 环境变量覆盖。

启动网关：`hermes gateway run`。监听器暴露以下端点：

- `POST /msgraph/webhook` —— 来自 Graph 的变更通知
- `GET /msgraph/webhook?validationToken=...` —— Graph 订阅验证握手
- `GET /health` —— 就绪探测，包含接受/重复计数的计数器

将监听器公开暴露（反向代理、开发隧道、ingress）。你的 Graph 订阅通知 URL 是你的公共 HTTPS 源地址后跟 `/msgraph/webhook`：

```
https://ops.example.com/msgraph/webhook
```

## 配置

所有设置位于 `platforms.msgraph_webhook.extra` 下：

| 设置项 | 默认值 | 描述 |
|---------|---------|-------------|
| `host` | `0.0.0.0` | HTTP 监听器的绑定地址。非回环地址绑定需要 `allowed_source_cidrs`；回环地址（`127.0.0.1` / `::1`）是最简单的开发隧道/反向代理设置方式。 |
| `port` | `8646` | 绑定端口。 |
| `webhook_path` | `/msgraph/webhook` | Graph 向其 POST 请求的 URL 路径。 |
| `health_path` | `/health` | 就绪端点。 |
| `client_state` | — | Graph 在每个通知中回传的共享密钥。与 `hmac.compare_digest` 进行比较——使用 `openssl rand -hex 32` 生成。 |
| `accepted_resources` | `[]`（接受所有） | Graph 资源路径/模式的允许列表。尾部 `*` 作为前缀匹配。允许前导 `/`。示例：`["communications/onlineMeetings", "chats/*/messages"]`。 |
| `max_seen_receipts` | `5000` | 通知 ID 的去重缓存大小。达到上限时淘汰最旧的条目。 |
| `allowed_source_cidrs` | `[]` | 非回环绑定必填。仅当监听器绑定到回环地址并通过本地隧道/反向代理前端时留空。 |

大多数设置也有对应的环境变量（`MSGRAPH_WEBHOOK_*`），在网关启动时合并到配置中（`host` 例外，它仅通过配置设置——参见上方注释）——请参阅[环境变量参考](/reference/environment-variables#microsoft-graph-teams-meetings)。

## 安全加固

### clientState 是主要的身份验证检查

每个 Graph 通知都包含你订阅时注册的 `clientState` 字符串。监听器会拒绝任何 `clientState` 不匹配的通知，并使用时序安全比较。这是 Microsoft 文档化的机制——请将此值视为强共享密钥。

如果 `client_state` 未设置，监听器将拒绝启动。

### 源 IP 允许列表（生产部署）

对于生产环境，将监听器限制为 Microsoft 发布的 Graph Webhook 源 IP 范围。Microsoft 在 [Office 365 IP 地址和 URL Web 服务](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges) 中记录了出口范围。配置如下：

```yaml
platforms:
  msgraph_webhook:
    enabled: true
    extra:
      host: 0.0.0.0
      client_state: "..."
      allowed_source_cidrs:
        - "52.96.0.0/14"
        - "52.104.0.0/14"
        # ...添加当前的 Microsoft 365 "Common" + "Teams" 类别出口范围
```

或作为环境变量：

```bash
MSGRAPH_WEBHOOK_ALLOWED_SOURCE_CIDRS="52.96.0.0/14,52.104.0.0/14"
```

如果绑定非回环主机（如 `0.0.0.0`、`::` 或 LAN IP）而未设置 `allowed_source_cidrs`，启动将被拒绝。如果你在同一台机器上使用开发隧道或反向代理，则将 Hermes 绑定到 `127.0.0.1` 或 `::1`，并保留允许列表为空。无效的 CIDR 字符串会记录警告并被忽略。**每季度审查 Microsoft IP 列表**——它会变化。

### HTTPS 终止

监听器使用纯 HTTP 通信。在你的反向代理（Caddy、Nginx、Cloudflare Tunnel、AWS ALB）处终止 TLS，并通过本地网络代理到监听器。Graph 拒绝向非 HTTPS 端点投递通知，因此不存在未加密流量从 Graph 到达你的路径。

### 响应清理

成功时监听器返回 `202 Accepted` 并带空体——内部计数器不会出现在网络响应中。操作员可以通过 `/health` 观察计数，该端点受与 Webhook 路径相同的源 IP 规则保护。

状态码表：

| 结果 | 状态码 |
|---------|--------|
| 通知已接受或去重 | 202 |
| 验证握手（带 `validationToken` 的 GET 请求） | 200（原样返回令牌） |
| 批次中所有项均未通过 clientState 检查 | 403 |
| JSON 格式错误 / 缺少 `value` 数组 / 未知资源 | 400 |
| 源 IP 不在允许列表中 | 403 |
| 不带 `validationToken` 的纯 GET 请求 | 400 |

## 故障排除

| 问题 | 检查点 |
|---------|---------------|
| Graph 订阅验证失败 | 公共 URL 可访问，`/msgraph/webhook` 路径匹配，带 `validationToken` 的 GET 请求在 10 秒内以 `text/plain` 格式原样返回令牌。 |
| 通知已 POST 但未摄入 | `client_state` 与你注册订阅时使用的值匹配。如果值发生变化，重新运行 `openssl rand -hex 32` 并创建新订阅。检查 `accepted_resources` 是否包含 Graph 发送的资源路径。 |
| 每个通知都返回 403 | `clientState` 不匹配（可能是伪造，或者订阅使用了不同的值注册）。使用 `hermes teams-pipeline subscribe --client-state "$MSGRAPH_WEBHOOK_CLIENT_STATE" ...` 重新创建订阅（随管道运行时 PR 提供）。 |
| 监听器拒绝在 `0.0.0.0` 上启动 | 将 `allowed_source_cidrs` 设置为 Microsoft 当前的 Webhook 出口范围，或者将 Hermes 绑定到隧道或反向代理后面的 `127.0.0.1` / `::1`。 |
| 监听器启动但 `curl http://localhost:8646/health` 挂起 | 端口绑定冲突。检查 `ss -tlnp | grep 8646`，如有必要更改 `port:`。 |
| 来自 Microsoft 的真实 Graph 请求返回 403 | 源 IP 允许列表太窄。扩大列表以包含当前 Microsoft 出口范围。如果你仍在验证隧道路径，则将 Hermes 绑定到回环地址，让隧道处理公共暴露。 |

## 相关文档

- [注册一个 Microsoft Graph 应用程序](/guides/microsoft-graph-app-registration) —— Azure 应用程序注册前置条件
- [环境变量 → Microsoft Graph](/reference/environment-variables#microsoft-graph-teams-meetings) —— 完整的环境变量列表
- [Microsoft Teams 机器人设置](/user-guide/messaging/teams) —— 用户可在 Teams 中与 Hermes 聊天的不同平台