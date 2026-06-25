---
title: Email
---

## 安全性（Security）

:::warning
**使用专用电子邮件账户**。不要使用您的个人电子邮件 — 代理（Agent）会将密码存储在 `.env` 文件中，并通过 IMAP 拥有完整的收件箱访问权限。
:::

- 使用**应用密码（App Passwords）**而不是主密码（Gmail 启用双重验证时必需）
- 设置 `EMAIL_ALLOWED_USERS` 来限制哪些用户可以与此代理交互
- 密码存储在 `~/.hermes/.env` 中 — 请保护此文件（`chmod 600`）
- IMAP 默认使用 SSL（端口 993），SMTP 默认使用 STARTTLS（端口 587）— 连接已加密

---

--- body ---
--- body ---
## 环境变量参考（Environment Variables Reference）

| 变量名 | 是否必需 | 默认值 | 描述 |
|----------|----------|---------|-------------|
| `EMAIL_ADDRESS` | 是 | — | 代理的电子邮件地址 |
| `EMAIL_PASSWORD` | 是 | — | 电子邮件密码或应用密码 |
| `EMAIL_IMAP_HOST` | 是 | — | IMAP 服务器主机（例如 `imap.gmail.com`） |
| `EMAIL_SMTP_HOST` | 是 | — | SMTP 服务器主机（例如 `smtp.gmail.com`） |
| `EMAIL_IMAP_PORT` | 否 | `993` | IMAP 服务器端口 |
| `EMAIL_SMTP_PORT` | 否 | `587` | SMTP 服务器端口 |
| `EMAIL_POLL_INTERVAL` | 否 | `15` | 检查收件箱的间隔秒数 |
| `EMAIL_ALLOWED_USERS` | 否 | — | 允许的发件人地址（以逗号分隔） |
| `EMAIL_HOME_ADDRESS` | 否 | — | 定时任务（Cron Job）的默认投递目标 |
| `EMAIL_ALLOW_ALL_USERS` | 否 | `false` | 允许所有发件人（不推荐） |