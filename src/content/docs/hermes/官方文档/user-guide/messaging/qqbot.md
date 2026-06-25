---
title: Qqbot
---

title: QQ 机器人
description: Hermes Agent 官方文档汉化版
---

--- body ---

# QQ 机器人 (QQ Bot)

通过 **官方 QQ 机器人 API (v2)** 将 Hermes 连接到 QQ —— 支持私聊（C2C）、群聊 @提及、频道以及带语音转写的私信。

## 概述

QQ 机器人适配器使用 [官方 QQ 机器人 API](https://bot.q.qq.com/wiki/develop/api-v2/) 实现以下功能：

- 通过持久的 **WebSocket** 连接 QQ 网关接收消息
- 通过 **REST API** 发送文本和 Markdown 回复
- 下载并处理图片、语音消息和文件附件
- 使用腾讯内置的 ASR 或可配置的 STT 提供者对语音消息进行转写

## 前提条件

1. **QQ 机器人应用** —— 在 [q.qq.com](https://q.qq.com) 注册：
   - 创建一个新应用，记下你的 **应用ID (App ID)** 和 **应用密钥 (App Secret)**
   - 启用所需的意图（intents）：C2C 消息、群聊 @消息、频道消息
   - 在沙箱模式下配置机器人用于测试，或发布用于生产环境

2. **依赖项** —— 适配器需要 `aiohttp` 和 `httpx`：
   ```bash
   pip install aiohttp httpx
   ```

## 配置

### 交互式设置

```bash
hermes gateway setup
```

从平台列表中选择 **QQ 机器人 (QQ Bot)**，然后按照提示操作。

### 手动配置

在 `~/.hermes/.env` 文件中设置所需的环境变量：

```bash
QQ_APP_ID=你的应用ID
QQ_CLIENT_SECRET=你的应用密钥
```

## 环境变量

| 变量 | 描述 | 默认值 |
|---|---|---|
| `QQ_APP_ID` | QQ 机器人应用ID (必填) | — |
| `QQ_CLIENT_SECRET` | QQ 机器人应用密钥 (必填) | — |
| `QQBOT_HOME_CHANNEL` | 用于定时任务/通知投递的 OpenID | — |
| `QQBOT_HOME_CHANNEL_NAME` | 主频道显示名称 | `Home` |
| `QQ_ALLOWED_USERS` | 允许私信访问的用户 OpenID，以逗号分隔 | open (所有用户) |
| `QQ_GROUP_ALLOWED_USERS` | 允许群组访问的群 OpenID，以逗号分隔 | — |
| `QQ_ALLOW_ALL_USERS` | 设置为 `true` 以允许所有私信 | `false` |
| `QQ_PORTAL_HOST` | 覆盖 QQ 门户主机 (设置为 `sandbox.q.qq.com` 用于沙箱路由) | `q.qq.com` |
| `QQ_STT_API_KEY` | 语音转文字提供者的 API 密钥 | — |
| `QQ_STT_BASE_URL` | (不直接读取——请在 `config.yaml` 中设置 `platforms.qqbot.extra.stt.baseUrl`) | 不适用 |
| `QQ_STT_MODEL` | STT 模型名称 | `glm-asr` |

## 高级配置

如需精细控制，将平台设置添加到 `~/.hermes/config.yaml`：

```yaml
platforms:
  qqbot:
    enabled: true
    extra:
      app_id: "你的应用ID"
      client_secret: "你的密钥"
      markdown_support: true       # 启用 QQ markdown (msg_type 2)。仅限配置项；无对应环境变量。
      dm_policy: "open"          # open | allowlist | disabled
      allow_from:
        - "用户_openid_1"
      group_policy: "open"       # open | allowlist | disabled
      group_allow_from:
        - "群组_openid_1"
      stt:
        provider: "zai"          # zai (GLM-ASR), openai (Whisper) 等
        baseUrl: "https://open.bigmodel.cn/api/coding/paas/v4"
        apiKey: "你的STT密钥"
        model: "glm-asr"
```

## 语音消息 (STT)

语音转写分两个阶段进行：

1. **QQ 内置 ASR** (免费，始终优先尝试) —— QQ 在语音消息附件中提供 `asr_refer_text`，该字段使用腾讯自有的语音识别
2. **配置的 STT 提供者** (回退) —— 如果 QQ 的 ASR 未返回文本，适配器会调用与 OpenAI 兼容的 STT API：

   - **智谱/GLM (zai)**：默认提供者，使用 `glm-asr` 模型
   - **OpenAI Whisper**：设置 `QQ_STT_BASE_URL` 和 `QQ_STT_MODEL`
   - 任何与 OpenAI 兼容的 STT 端点

## 故障排除

### 机器人立即断开连接 (快速断连)

通常意味着：
- **应用ID / 密钥无效** —— 在 q.qq.com 上仔细检查你的凭证
- **缺少权限** —— 确保机器人已启用所需的意图
- **仅沙箱机器人** —— 如果机器人处于沙箱模式，它只能接收来自 QQ 沙箱测试频道的消息

### 语音消息未被转写

1. 检查附件数据中是否存在 QQ 内置的 `asr_refer_text`
2. 如果使用自定义 STT 提供者，请验证 `QQ_STT_API_KEY` 是否正确设置
3. 查看网关日志中的 STT 错误信息

### 消息未投递

- 验证在 q.qq.com 上是否已启用机器人的 **意图 (intents)**
- 如果私信访问受限，检查 `QQ_ALLOWED_USERS`
- 对于群消息，确保机器人被 **@提及** (群组策略可能需要白名单)
- 检查 `QQBOT_HOME_CHANNEL` 是否用于定时任务/通知投递

### 连接错误

- 确保已安装 `aiohttp` 和 `httpx`：`pip install aiohttp httpx`
- 检查与 `api.sgroup.qq.com` 和 WebSocket 网关的网络连通性
- 查看网关日志以获取详细的错误信息和重连行为