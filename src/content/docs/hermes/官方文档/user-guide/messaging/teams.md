---
title: Teams
---

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| `health` 端点正常工作但机器人无响应 | 检查你的隧道是否仍在运行，且机器人的消息端点与隧道 URL 匹配 |
| 日志中出现 `KeyError: 'teams'` | 重启容器——此问题已在当前版本中修复 |
| 机器人响应认证错误 | 确认 `TEAMS_CLIENT_ID`、`TEAMS_CLIENT_SECRET` 和 `TEAMS_TENANT_ID` 已正确设置 |
| `未配置推理提供者（No inference provider configured）` | 检查 `~/.hermes/.env` 中是否设置了 `ANTHROPIC_API_KEY`（或其他提供者密钥） |
| 机器人收到消息但忽略它们 | 你的 AAD 对象 ID 可能不在 `TEAMS_ALLOWED_USERS` 中。运行 `teams status --verbose` 来查找 |
| 隧道 URL 在重启后发生变化 | devtunnel URL 在使用命名隧道（`devtunnel create hermes-bot`）时是持久的。ngrok 和 cloudflared 除非使用付费计划，否则每次运行都会生成新的 URL——当 URL 发生变化时，使用 `teams app update` 更新机器人端点 |
| Teams 显示“此机器人无响应” | Webhook 返回了错误。检查 `docker logs hermes` 中的回溯信息 |
| 日志中出现 `[teams] 连接失败（Failed to connect）` | SDK 认证失败。仔细检查你的凭据，并确保租户 ID 与你在 `teams login` 中使用的账户匹配 |

---

--- body ---
## 安全

:::warning
**始终设置 `TEAMS_ALLOWED_USERS`**  为授权用户的 AAD 对象 ID。如果不设置，任何能找到或安装你的机器人的人都可以与之交互。

将 `TEAMS_CLIENT_SECRET` 视为密码——通过 Azure 门户或 Teams CLI 定期轮换它。
:::

- 将凭据存储在 `~/.hermes/.env` 文件中，并设置权限为 `600`（`chmod 600 ~/.hermes/.env`）
- 机器人只接受来自 `TEAMS_ALLOWED_USERS` 中用户的消息；未经授权的消息会被静默丢弃
- 你的公共端点（`/api/messages`）由 Teams Bot Framework 进行认证——没有有效 JWT 的请求将被拒绝

## 相关文档

- [Teams 会议](/user-guide/messaging/teams-meetings)
- [运维 Teams 会议管线](/guides/operate-teams-meeting-pipeline)