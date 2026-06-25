--- frontmatter ---
---

## 安全性

:::warning
**始终配置访问控制。** 机器人默认拥有终端访问权限。如果没有设置 `SIGNAL_ALLOWED_USERS` 或进行 DM 配对（DM pairing），网关将拒绝所有传入消息作为安全措施。
:::

- 电话号码在所有日志输出中会被隐去
- 使用 DM 配对（DM pairing）或显式的允许列表（allowlist）来安全地接纳新用户
- 除非你特别需要群组支持，否则请保持群组功能禁用，或者只将你信任的群组加入允许列表
- Signal 的端到端加密保护消息在传输过程中的内容
- `~/.local/share/signal-cli/` 中的 signal-cli 会话数据包含账户凭据——请像保护密码一样保护它

---

--- body ---
--- body ---
## 环境变量参考

| 变量 | 必需 | 默认值 | 描述 |
|----------|----------|---------|-------------|
| `SIGNAL_HTTP_URL` | 是 | — | signal-cli HTTP 端点 |
| `SIGNAL_ACCOUNT` | 是 | — | 机器人电话号码（E.164 格式） |
| `SIGNAL_ALLOWED_USERS` | 否 | — | 逗号分隔的电话号码/UUID |
| `SIGNAL_GROUP_ALLOWED_USERS` | 否 | — | 要监控的群组 ID，或使用 `*` 表示所有群组（省略此项则禁用群组） |
| `SIGNAL_ALLOW_ALL_USERS` | 否 | `false` | 允许任何用户交互（跳过允许列表） |
| `SIGNAL_HOME_CHANNEL` | 否 | — | 定时任务的默认投递目标 |