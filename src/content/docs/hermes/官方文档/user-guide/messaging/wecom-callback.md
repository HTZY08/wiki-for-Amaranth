---
sidebar_position: 15
title: Wecom Callback
---

# 企业微信回调（自建应用）

通过回调/Webhook 模式，将 Hermes 连接到企业微信，作为自建企业应用。

:::info 企业微信机器人 vs 企业微信回调
Hermes 支持两种企业微信集成模式：
- **[企业微信机器人](wecom.md)** — 机器人模式，通过 WebSocket 连接。设置更简单，可在群聊中使用。
- **企业微信回调**（本页）— 自建应用，接收加密的 XML 回调。作为一级应用显示在用户的企业微信侧边栏中。支持多企业路由。
:::

另请参见：[企业微信机器人](./wecom.md) 了解机器人集成方式。

> 运行 `hermes gateway setup` 并选择 **企业微信回调** 以获取引导式教程。

## 工作原理

1. 在企业微信管理后台注册一个自建应用
2. 企业微信将加密的 XML 推送到你的 HTTP 回调端点
3. Hermes 解密消息，放入代理（Agent）队列
4. 立即确认（静默——不向用户显示任何内容）
5. 代理处理请求（通常需要 3–30 分钟）
6. 通过企业微信的 `message/send` API 主动发送回复

## 前提条件

- 一个拥有管理员权限的企业微信企业账号
- `aiohttp` 和 `httpx` Python 包（默认安装中包含）
- 一个可公开访问的回调 URL 服务器（或类似 ngrok 的隧道）

## 设置步骤

### 1. 在企业微信中创建自建应用

1. 前往 [企业微信管理后台](https://work.weixin.qq.com/) → **应用管理** → **创建应用**
2. 记下你的 **企业ID**（显示在管理后台顶部）
3. 在应用设置中，创建一个 **企业 Secret**
4. 在应用概览页面记下 **Agent ID**
5. 在 **接收消息** 中，配置回调 URL：
   - URL：`http://你的公网IP:8645/wecom/callback`
   - Token：生成一个随机 Token（企业微信会提供一个）
   - EncodingAESKey：生成一个密钥（企业微信会提供一个）

### 2. 配置环境变量

添加到你的 `.env` 文件中：

```bash
WECOM_CALLBACK_CORP_ID=你的企业ID
WECOM_CALLBACK_CORP_SECRET=你的企业Secret
WECOM_CALLBACK_AGENT_ID=1000002
WECOM_CALLBACK_TOKEN=你的回调Token
WECOM_CALLBACK_ENCODING_AES_KEY=你的43字符AES密钥

# 可选
WECOM_CALLBACK_HOST=0.0.0.0
WECOM_CALLBACK_PORT=8645
WECOM_CALLBACK_ALLOWED_USERS=user1,user2
```

### 3. 启动网关

```bash
hermes gateway
```

（只有在 `hermes gateway install` 注册了 systemd/launchd 服务后，才使用 `hermes gateway start`。）

回调适配器会在配置的端口上启动一个 HTTP 服务器。企业微信将通过 GET 请求验证回调 URL，然后开始通过 POST 发送消息。

## 配置参考

在 `config.yaml` 的 `platforms.wecom_callback.extra` 下设置这些参数，或使用环境变量：

| 设置项 | 默认值 | 描述 |
|---------|---------|-------------|
| `corp_id` | — | 企业微信企业 ID（必填） |
| `corp_secret` | — | 自建应用的 corp secret（必填） |
| `agent_id` | — | 自建应用的 Agent ID（必填） |
| `token` | — | 回调验证 Token（必填） |
| `encoding_aes_key` | — | 回调加密用的 43 字符 AES 密钥（必填） |
| `host` | `0.0.0.0` | HTTP 回调服务器的绑定地址 |
| `port` | `8645` | HTTP 回调服务器的端口 |
| `path` | `/wecom/callback` | 回调端点的 URL 路径 |

## 多应用路由

对于运行多个自建应用的企业（例如，跨不同部门或子公司），在 `config.yaml` 中配置 `apps` 列表：

```yaml
platforms:
  wecom_callback:
    enabled: true
    extra:
      host: "0.0.0.0"
      port: 8645
      apps:
        - name: "部门A"
          corp_id: "ww_corp_a"
          corp_secret: "secret-a"
          agent_id: "1000002"
          token: "token-a"
          encoding_aes_key: "key-a-43-chars..."
        - name: "部门B"
          corp_id: "ww_corp_b"
          corp_secret: "secret-b"
          agent_id: "1000003"
          token: "token-b"
          encoding_aes_key: "key-b-43-chars..."
```

用户通过 `corp_id:user_id` 进行范围限定，以防止跨企业冲突。当用户发送消息时，适配器会记录他们所属的应用（企业），并通过正确的应用 access token 路由回复。

## 访问控制

限制哪些用户可以与应用交互：

```bash
# 允许特定用户
WECOM_CALLBACK_ALLOWED_USERS=zhangsan,lisi,wangwu

# 或者允许所有用户
WECOM_CALLBACK_ALLOW_ALL_USERS=true
```

## 端点

适配器暴露以下端点：

| 方法 | 路径 | 用途 |
|--------|------|---------|
| GET | `/wecom/callback` | URL 验证握手（企业微信在设置时发送） |
| POST | `/wecom/callback` | 加密消息回调（企业微信在此处发送用户消息） |
| GET | `/health` | 健康检查——返回 `{"status": "ok"}` |

## 加密

所有回调负载都使用 EncodingAESKey 进行 AES-CBC 加密。适配器负责处理：

- **入站**：解密 XML 负载，验证 SHA1 签名
- **出站**：通过主动 API 发送回复（非加密的回调响应）

加密实现与腾讯官方的 WXBizMsgCrypt SDK 兼容。

## 限制

- **无流式传输** — 回复在代理完成后作为完整消息到达
- **无输入状态指示** — 回调模式不支持输入状态
- **仅支持文本** — 目前仅支持文本消息输入；图像/文件/语音输入尚未实现。代理通过企业微信平台提示了解出站媒体能力（图片、文档、视频、语音）。
- **响应延迟** — 代理会话需要 3–30 分钟；用户在处理完成后看到回复

## 故障排除

**签名验证失败。**
企业微信使用你在管理后台注册的 **Token** 对每个请求进行签名。Hermes 中配置的 Token 与管理后台期望的 Token 不匹配是最常见的原因。请从管理后台重新复制 **Token** 和 **EncodingAESKey** ——它们很容易被截断。`~/.hermes/.env` 中 `=` 号周围的空白字符也会破坏签名检查。修复后，重新启动 `hermes gateway run`。

**回调 URL 无法访问 / 验证步骤失败。**
企业微信会访问你注册的公网 URL。请确认：
1. 你的反向代理/隧道已将 `/wecom/callback` 转发到网关的端口。
2. 管理后台中的 URL 是 HTTPS（企业微信拒绝纯 HTTP）。
3. 从你的网络外部，`curl -i https://<你的域名>/wecom/callback` 返回的不是超时（没有查询参数时返回 4xx 也没关系——这只表示监听器可达）。

**端口无法访问 / 监听器未绑定。**
检查 `hermes gateway run` 日志中绑定的主机/端口。如果适配器绑定到了 `127.0.0.1`，你必须使用反向代理或隧道将其暴露——企业微信的服务器无法访问回环地址。在 `config.yaml` 中设置 `extra.host: 0.0.0.0`（如果直接暴露，还需设置 `allowed_source_cidrs`），或者保持回环地址并使用 Cloudflare Tunnel / nginx 等隧道。