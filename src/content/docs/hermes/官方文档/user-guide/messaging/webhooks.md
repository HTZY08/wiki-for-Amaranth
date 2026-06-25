---
title: Webhooks
---

## 故障排除（Troubleshooting） {#troubleshooting}

### Webhook 未到达

- 确认端口已暴露且可从 Webhook 来源访问
- 检查防火墙规则 — 必须开放端口 `8644`（或你配置的端口）
- 验证 URL 路径是否匹配：`http://your-server:8644/webhooks/<route-name>`
- 使用 `/health` 端点确认服务器正在运行

### 签名验证失败

- 确保路由配置中的密钥（secret）与 Webhook 来源配置的密钥完全一致
- 对于 GitHub，密钥是基于 HMAC 的 — 检查 `X-Hub-Signature-256`
- 对于 GitLab，密钥是明文令牌匹配 — 检查 `X-Gitlab-Token`
- 检查网关日志中是否有 `Invalid signature` 警告

### 事件被忽略

- 检查事件类型是否包含在路由的 `events` 列表中
- GitHub 事件使用诸如 `pull_request`、`push`、`issues` 等值（即 `X-GitHub-Event` 头部值）
- GitLab 事件使用诸如 `merge_request`、`push` 等值（即 `X-GitLab-Event` 头部值）
- 如果 `events` 为空或未设置，则接受所有事件

### 代理（Agent）无响应

- 在前台运行网关以查看日志：`hermes gateway run`
- 检查提示模板（prompt template）是否正常渲染
- 验证交付目标（delivery target）已配置并连接

### 重复响应

- 幂等性缓存（idempotency cache）应能防止此情况 — 检查 Webhook 来源是否发送了交付 ID 头部（`X-GitHub-Delivery` 或 `X-Request-ID`）
- 交付 ID 会缓存 1 小时

### `gh` CLI 错误（GitHub 评论交付）

- 在网关主机上运行 `gh auth login`
- 确保经过身份验证的 GitHub 用户对仓库具有写入权限
- 检查 `gh` 是否已安装并在 PATH 中

---

--- body ---
## 环境变量（Environment Variables） {#environment-variables}

| 变量（Variable） | 描述（Description） | 默认值（Default） |
|----------|-------------|---------|
| `WEBHOOK_ENABLED` | 启用 Webhook 平台适配器（platform adapter） | `false` |
| `WEBHOOK_PORT` | 接收 Webhook 的 HTTP 服务器端口 | `8644` |
| `WEBHOOK_SECRET` | 全局 HMAC 密钥（当路由未指定自己的密钥时作为后备使用） | _(无)_ |