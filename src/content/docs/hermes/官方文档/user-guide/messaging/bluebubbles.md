--- frontmatter ---
---
title: BlueBubbles
description: Hermes Agent 官方文档汉化版
---

--- body ---
# BlueBubbles（iMessage）

通过 [BlueBubbles](https://bluebubbles.app/) 将 Hermes 连接到苹果 iMessage —— 一款免费、开源的 macOS 服务端，可将 iMessage 桥接到任何设备。

## 前提条件

- 一台**Mac**（持续开机）并运行 [BlueBubbles Server](https://bluebubbles.app/)
- 在该 Mac 的“信息”应用中登录了 Apple ID
- BlueBubbles Server v1.0.0 或以上版本（网络钩子（webhook）需要此版本）
- Hermes 与 BlueBubbles 服务端之间的网络连通性

## 设置

### 1. 安装 BlueBubbles Server

从 [bluebubbles.app](https://bluebubbles.app/) 下载并安装。完成设置向导 —— 用你的 Apple ID 登录并配置连接方式（本地网络、Ngrok、Cloudflare 或动态 DNS）。

### 2. 获取你的服务端 URL 和密码

在 BlueBubbles Server → **设置 → API** 中，记下：
- **服务端 URL**（例如 `http://192.168.1.10:1234`）
- **服务端密码**

### 3. 配置 Hermes

运行设置向导：

```bash
hermes gateway setup
```

选择 **BlueBubbles（iMessage）** 并输入你的服务端 URL 和密码。

或者直接在 `~/.hermes/.env` 中设置环境变量（environment variable）：

```bash
BLUEBUBBLES_SERVER_URL=http://192.168.1.10:1234
BLUEBUBBLES_PASSWORD=your-server-password
```

#### 可选：在群聊中要求提及

默认情况下，Hermes 会响应所有授权的 BlueBubbles/iMessage 私聊或群聊消息。若要使群聊为选择加入，请启用提及（mention）门控：

```yaml
platforms:
  bluebubbles:
    enabled: true
    extra:
      require_mention: true
```

当 `require_mention: true` 时，私聊消息仍正常工作，但群聊消息会被忽略，除非它们匹配某个提及模式（mention pattern）。如果你未配置自定义模式，Hermes 会使用保守的默认模式，适用于 `Hermes` 和 `@Hermes agent` 等变体。

如需自定义代理名称，请设置正则表达式（regex）模式：

```yaml
platforms:
  bluebubbles:
    extra:
      require_mention: true
      mention_patterns:
        - '(?<![\w@])@?amos\b[,:\-]?'
```

### 4. 授权用户

选择以下一种方式：

**私聊配对（推荐）：**
当有人给你的 iMessage 发送消息时，Hermes 会自动向他们发送一个配对码。用以下命令批准：
```bash
hermes pairing approve bluebubbles <CODE>
```
使用 `hermes pairing list` 查看待处理的配对码和已批准的用户。

**预授权特定用户**（在 `~/.hermes/.env` 中）：
```bash
BLUEBUBBLES_ALLOWED_USERS=user@icloud.com,+15551234567
```

**开放访问**（在 `~/.hermes/.env` 中）：
```bash
BLUEBUBBLES_ALLOW_ALL_USERS=true
```

### 5. 启动网关

```bash
hermes gateway run
```

Hermes 将连接到你的 BlueBubbles 服务端，注册一个网络钩子（webhook），并开始监听 iMessage 消息。

## 工作原理

```
iMessage → “信息”应用 → BlueBubbles Server → 网络钩子 → Hermes
Hermes → BlueBubbles REST API → “信息”应用 → iMessage
```

- **入站：** 当新消息到达时，BlueBubbles 将网络钩子事件发送给本地监听器。无需轮询 —— 即时投递。
- **出站：** Hermes 通过 BlueBubbles REST API 发送消息。
- **媒体：** 支持双向传输图片、语音消息、视频和文档。入站附件会被下载并缓存到本地，供代理（agent）处理。

## 环境变量（Environment Variables）

| 变量 | 是否必需 | 默认值 | 描述 |
|----------|----------|---------|-------------|
| `BLUEBUBBLES_SERVER_URL` | 是 | — | BlueBubbles 服务端 URL |
| `BLUEBUBBLES_PASSWORD` | 是 | — | 服务端密码 |
| `BLUEBUBBLES_WEBHOOK_HOST` | 否 | `127.0.0.1` | 网络钩子监听器绑定地址 |
| `BLUEBUBBLES_WEBHOOK_PORT` | 否 | `8645` | 网络钩子监听器端口 |
| `BLUEBUBBLES_WEBHOOK_PATH` | 否 | `/bluebubbles-webhook` | 网络钩子 URL 路径 |
| `BLUEBUBBLES_HOME_CHANNEL` | 否 | — | 用于定时任务投递的电话/邮箱 |
| `BLUEBUBBLES_ALLOWED_USERS` | 否 | — | 逗号分隔的授权用户列表 |
| `BLUEBUBBLES_ALLOW_ALL_USERS` | 否 | `false` | 允许所有用户 |
| `BLUEBUBBLES_REQUIRE_MENTION` | 否 | `false` | 要求在群聊中响应前匹配一个提及模式 |
| `BLUEBUBBLES_MENTION_PATTERNS` | 否 | Hermes 唤醒词 | JSON 数组、换行分隔或逗号分隔的正则表达式模式，用于群聊提及匹配 |

自动将消息标记为已读的功能由 `~/.hermes/config.yaml` 中 `platforms.bluebubbles.extra` 下的 `send_read_receipts` 键控制（默认：`true`）。没有对应的环境变量。

## 功能

### 文本消息
发送和接收 iMessage。Markdown 会被自动剥离，以干净的纯文本形式投递。

### 富媒体
- **图片：** 照片会原生显示在 iMessage 对话中
- **语音消息：** 音频文件作为 iMessage 语音消息发送
- **视频：** 视频附件
- **文档：** 文件作为 iMessage 附件发送

### Tapback 反应
喜爱、赞同、不赞同、大笑、强调和疑问反应。需要 BlueBubbles [私有 API 辅助工具](https://docs.bluebubbles.app/helper-bundle/installation)。

### 输入指示器
当代理正在处理时，在 iMessage 对话中显示“正在输入...”。需要私有 API。

### 已读回执
处理完成后自动将消息标记为已读。需要私有 API。

### 对话寻址
你可以通过邮箱或电话号码来寻址对话 —— Hermes 会自动将其解析为 BlueBubbles 对话 GUID。无需使用原始 GUID 格式。

## 私有 API

某些功能需要 BlueBubbles [私有 API 辅助工具](https://docs.bluebubbles.app/helper-bundle/installation)：
- Tapback 反应
- 输入指示器
- 已读回执
- 通过地址创建新对话

没有私有 API 的情况下，基本的文本消息和媒体仍可正常工作。

## 故障排除

### “无法连接到服务端”
- 确认服务端 URL 正确且 Mac 已开机
- 检查 BlueBubbles Server 是否正在运行
- 确保网络连通性（防火墙、端口转发）

### 消息未到达
- 检查网络钩子是否已在 BlueBubbles Server → 设置 → API → 网络钩子 中注册
- 确认 Mac 能够访问网络钩子 URL
- 查看 `hermes logs gateway` 以获取网络钩子错误（或使用 `hermes logs -f` 实时跟踪）

### “私有 API 辅助工具未连接”
- 安装私有 API 辅助工具：[docs.bluebubbles.app](https://docs.bluebubbles.app/helper-bundle/installation)
- 没有它则基本消息功能仍可工作 —— 只有反应、输入指示器和已读回执需要它