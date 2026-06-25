---
title: Sms
---

## 安全性

### Webhook 签名验证

Hermes 通过验证 `X-Twilio-Signature` 请求头（HMAC-SHA1）来确保入站 Webhook 确实来自 Twilio。这样可以防止攻击者注入伪造消息。

**必须设置 `SMS_WEBHOOK_URL`。**请将其设置为你在 Twilio Console 中配置的公开 URL。缺少该变量时适配器将拒绝启动。

如果在本地开发时没有公开 URL，可以禁用验证：

```bash
# 仅限本地开发 — 不可用于生产环境
SMS_INSECURE_NO_SIGNATURE=true
```

### 用户白名单（User allowlists）

**默认情况下网关拒绝所有用户。**请配置白名单：

```bash
# 推荐做法：限制到特定电话号码
SMS_ALLOWED_USERS=+15559876543,+15551112222

# 或者允许所有（不推荐用于具有终端访问权限的机器人）
SMS_ALLOW_ALL_USERS=true
```

:::warning
SMS 没有内置加密功能。除非你了解其安全影响，否则不要使用 SMS 进行敏感操作。对于敏感场景，建议使用 Signal 或 Telegram。
:::

---

--- body ---
--- body ---
## 故障排除

### 消息未到达

1. 检查你的 Twilio Webhook URL 是否正确且可公开访问
2. 确认 `TWILIO_ACCOUNT_SID` 和 `TWILIO_AUTH_TOKEN` 正确
3. 在 Twilio Console → **Monitor → Logs → Messaging** 中查看投递错误
4. 确保你的电话号码在 `SMS_ALLOWED_USERS` 中（或设置了 `SMS_ALLOW_ALL_USERS=true`）

### 回复未发送

1. 检查 `TWILIO_PHONE_NUMBER` 是否设置正确（E.164 格式，带 `+`）
2. 确认你的 Twilio 账户拥有支持 SMS 的号码
3. 检查 Hermes 网关日志中是否有 Twilio API 错误

### Webhook 端口冲突

如果端口 8080 已被占用，请更改端口：

```bash
SMS_WEBHOOK_PORT=3001
```

同时在 Twilio Console 中更新 Webhook URL 以匹配新端口。