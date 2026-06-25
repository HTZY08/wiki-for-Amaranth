---
title: Xurl
---

## 备注（Notes）

- **速率限制（Rate limits）：** X 对每个端点实行速率限制。收到 429 状态码表示需要等待并重试。写入端点（发帖、回复、点赞、转发）的限制比读取端点更严格。
- **作用域（Scopes）：** OAuth 2.0 令牌使用宽泛的作用域。对特定操作返回 403 通常意味着令牌缺少某个作用域——让用户重新运行 `xurl auth oauth2`。
- **令牌刷新（Token refresh）：** OAuth 2.0 令牌会自动刷新。无需额外操作。
- **多个应用（Multiple apps）：** 每个应用拥有独立的凭据/令牌。通过 `xurl auth default` 或 `--app` 进行切换。
- **每个应用多个账号（Multiple accounts per app）：** 使用 `-u / --username` 选择，或通过 `xurl auth default APP USER` 设置默认账号。
- **令牌存储（Token storage）：** `~/.xurl` 是 YAML 格式。在 Docker 中，使用 Hermes 子进程的 HOME（官方镜像中的 `/opt/data/home`），这样令牌会存放在 `/opt/data/home/.xurl` 目录下。切勿将此文件读取或发送至 LLM 上下文。
- **费用（Cost）：** X API 访问通常需付费才能有意义地使用。多数失败是由于计划/权限问题，而非代码问题。

---

--- body ---
--- body ---
## 归属（Attribution）

- 上游 CLI：https://github.com/xdevplatform/xurl （X 开发者平台团队，Chris Park 等）
- 上游智能体技能：https://github.com/openclaw/openclaw/blob/main/skills/xurl/SKILL.md
- Hermes 改编：按照 Hermes 技能规范重新格式化；安全护栏（safety guardrails）逐字保留。