---
title: Whatsapp
---

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| **二维码无法扫描** | 确保终端宽度足够（60 列以上）。尝试使用不同的终端。确认扫描的是正确的 WhatsApp 账户（机器人号码，而非个人号码）。 |
| **二维码过期** | 二维码每约 20 秒刷新一次。如果超时，请重新启动 `hermes whatsapp`。 |
| **会话未持久化** | 检查 `~/.hermes/platforms/whatsapp/session` 是否存在且可写。如果使用容器化部署，请将其挂载为持久卷。 |
| **意外登出** | 长时间不活动后，WhatsApp 会取消设备链接。请保持手机开机并连接网络，如有必要，使用 `hermes whatsapp` 重新配对。 |
| **桥接崩溃或重连循环** | 重启网关，更新 Hermes，如果会话因 WhatsApp 协议变更而失效，则重新配对。 |
| **WhatsApp 更新后机器人停止工作** | 更新 Hermes 以获取最新桥接版本，然后重新配对。 |
| **macOS：终端中可以运行 `node`，但提示“Node.js not installed”** | launchd 服务不会继承你的 shell PATH。运行 `hermes gateway install` 将当前 PATH 重新快照到 plist 中，然后运行 `hermes gateway start`。详情请参阅[网关服务文档](./index.md#macos-launchd)。 |
| **无法接收消息** | 确认 `WHATSAPP_ALLOWED_USERS` 包含发送者的号码（包含国家代码，不含 `+` 或空格），或将其设置为 `*` 以允许所有人。在 `.env` 中设置 `WHATSAPP_DEBUG=true` 并重启网关，可在 `bridge.log` 中查看原始消息事件。 |
| **机器人向陌生人回复配对码** | 如果希望未授权的私信被静默忽略，可在 `~/.hermes/config.yaml` 中设置 `whatsapp.unauthorized_dm_behavior: ignore`。 |

---

--- body ---
## 安全

:::warning
**在正式上线之前配置访问控制**。使用具体电话号码（包含国家代码，不含 `+`）设置 `WHATSAPP_ALLOWED_USERS`，使用 `*` 允许所有人，或设置 `WHATSAPP_ALLOW_ALL_USERS=true`。如果未设置任何这些选项，网关将**拒绝所有传入消息**作为安全措施。
:::

默认情况下，未授权的私信仍会收到配对码回复。如果你希望一个私密的 WhatsApp 号码对陌生人完全保持沉默，请设置：

```yaml
whatsapp:
  unauthorized_dm_behavior: ignore
```

- `~/.hermes/platforms/whatsapp/session` 目录包含完整的会话凭证 —— 请像保护密码一样保护它
- 设置文件权限：`chmod 700 ~/.hermes/platforms/whatsapp/session`
- 为机器人使用**专用电话号码**，以隔离对个人账户的风险
- 如果怀疑泄露，请通过 WhatsApp → 设置 → 已链接设备 取消设备链接
- 日志中的电话号码会部分脱敏，但请检查你的日志保留策略