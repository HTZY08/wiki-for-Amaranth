---

## 与 Baileys 桥接的对比

| | Baileys (`hermes whatsapp`) | Cloud API (`hermes whatsapp-cloud`) |
|---|---|---|
| 账户类型 | 个人 | 商业 |
| 设置 | 扫描 QR 码 | Meta 应用 + WABA + 令牌 |
| 依赖项 | Node.js + npm | 纯 Python (httpx + aiohttp) |
| 进程 | 管理的 Node 子进程 | aiohttp webhook 服务器 |
| 是否需要公网 URL？ | 否 | 是 |
| 账户封禁风险 | 有（非官方 API） | 无（官方支持） |
| 入站消息 | 轮询 Node 桥接 | Meta 的 Webhook POST |
| 出站消息 | 本地桥接 → Baileys | HTTPS 到 graph.facebook.com |
| 群组 | 完全支持 | 仅私聊（v1） |
| 24 小时窗口 | 无限制 | 硬性规则——之后需要模板 |
| 语音消息（出站） | 原生 | 原生（带 ffmpeg，否则降级为 MP3） |
| 已读回执 | 否 | 是（蓝色双勾） |
| 输入状态指示器 | 否 | 是（响应后自动消失） |
| 交互按钮 | 仅文本回退 | 原生（澄清、批准、斜杠确认） |
| 生产环境使用 | 有风险（Meta 可封禁） | 专为此设计 |

运行 Hermes 的个人项目用户大多使用 Baileys。运行面向客户的机器人的用户大多使用 Cloud API。

---

## 另请参阅

- [Meta 官方 WhatsApp Business Cloud API 文档](https://developers.facebook.com/documentation/business-messaging/whatsapp/) — 底层平台、定价、应用审核和 Meta 侧速率限制的权威参考。
- [WhatsApp (Baileys 桥接) 设置](whatsapp.md) — 个人项目的替代集成方案。
- [消息平台概述](index.md) — 所有消息集成一览。