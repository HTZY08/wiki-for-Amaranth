---
sidebar_position: 15
title: "订阅代理（Subscription Proxy）"
description: "将你的 Nous Portal 订阅（或其他 OAuth 提供商）作为外部应用的 OpenAI 兼容端点使用"
---

# 订阅代理（Subscription Proxy）

订阅代理是一个本地 HTTP 服务器，允许外部应用——OpenViking、Karakeep、Open WebUI 或任何支持 OpenAI 兼容聊天补全（OpenAI-compatible chat completions）的应用——将你通过 Hermes 管理的提供商订阅（provider subscription）作为其 LLM 端点。代理会自动附加正确的凭证（自动刷新），因此应用永远不需要静态 API 密钥。

这与 [API 服务器（API server）](./api-server.md) 不同：

| | API 服务器（API server） | 订阅代理（Subscription proxy） |
|---|---|---|
| 提供的内容 | 你的代理（完整工具集、记忆、技能） | 原始模型推理 |
| 使用场景 | “将 Hermes 作为聊天后端使用” | “从其他应用使用我的 Portal 订阅” |
| 认证 | 你的 `API_SERVER_KEY` | 任何承载令牌（代理会附加真实令牌） |
| 工具调用 | 是——代理运行工具 | 否——仅透传 |

当你想要 **代理（agent）** 作为后端时，使用 API 服务器；当你只想通过订阅使用 **模型（model）** 时，使用代理。

## 快速开始

### 1. 登录你的提供商（一次性操作）

```bash
hermes portal
```

此命令会在浏览器中打开 Nous Portal OAuth 流程。Hermes 将刷新令牌存储在 `~/.hermes/auth.json` 中——所有 Hermes 提供商登录信息都存储在同一位置。

### 2. 启动代理

```bash
hermes proxy start
```

```
Starting Hermes proxy for Nous Portal
  Listening on:  http://127.0.0.1:8645/v1
  Forwarding to: (resolved per-request from your subscription)
  Use any bearer token in the client — the proxy attaches your real credential.
```

保持此命令在前台运行。如果希望在登出后仍保持运行，可以使用 `tmux`、`nohup` 或 systemd 单元。

### 3. 将你的应用指向代理

任何 OpenAI 兼容的应用配置都需要以下三要素：

```
Base URL:   http://127.0.0.1:8645/v1
API key:    任意值（例如 "sk-unused"）
Model:      Hermes-4-70B    # 或 Hermes-4.3-36B、Hermes-4-405B
```

代理会忽略来自你应用的 `Authorization` 头部，并将你真实的 Portal 凭证附加到上游请求中。当承载令牌接近过期时，会自动进行刷新。

## 可用的提供商

```bash
hermes proxy providers
```

目前内置的提供商：`nous`（Nous Portal）和 `xai`（xAI / Grok）。通过实现 `hermes_cli/proxy/adapters/` 中的 `UpstreamAdapter` 接口，可以添加更多 OAuth 提供商。

## 检查状态

```bash
hermes proxy status
```

```
Hermes proxy upstream adapters

  [nous    ] Nous Portal — ready (bearer expires 2026-05-15T06:43:21Z)
```

如果看到 `not logged in`，请运行 `hermes portal`。如果看到 `credentials need attention`，说明你的刷新令牌已被撤销（较为罕见——如果从 Portal 网页界面退出登录会发生这种情况）——只需重新运行 `hermes portal`。

## 允许的路径

代理仅转发上游实际服务的路径。对于 Nous Portal：

| 路径 | 用途 |
|------|------|
| `/v1/chat/completions` | 聊天补全（流式 + 非流式） |
| `/v1/completions` | 传统文本补全 |
| `/v1/embeddings` | 嵌入 |
| `/v1/models` | 模型列表 |

其他路径（`/v1/images/generations`、`/v1/audio/speech` 等）会返回 404，并附带明确指向允许路径的错误信息。这可以防止杂散客户端向上游发送奇怪的请求。

## 配置 OpenViking 使用 Portal

[OpenViking](https://github.com/volcengine/OpenViking) 是一个上下文数据库（context database），需要 LLM 提供商来支持其 VLM（视觉/语言模型，用于提取记忆）和嵌入模型。通过代理，你可以将其 `vlm.api_base` 指向本地代理：

编辑 `~/.openviking/ov.conf`：

```json
{
  "vlm": {
    "provider": "openai",
    "model": "Hermes-4-70B",
    "api_base": "http://127.0.0.1:8645/v1",
    "api_key": "unused-proxy-attaches-real-creds"
  }
}
```

然后在一个终端中启动代理，同时在另一个终端中运行 `openviking-server`：

```bash
# 终端 1
hermes proxy start

# 终端 2
openviking-server
```

现在 OpenViking 的 VLM 调用将通过你的 Portal 订阅进行。嵌入模型部分仍需要自己的提供商——Portal 确实服务 `/v1/embeddings` 端点，但模型选择取决于你的套餐支持情况；请查看 `portal.nousresearch.com/models`。

## 配置 Karakeep（或任何书签/摘要应用）

[Karakeep](https://karakeep.app/) 使用 OpenAI 兼容的 API 进行书签摘要。在其配置中：

```bash
# Karakeep .env
OPENAI_API_BASE_URL=http://127.0.0.1:8645/v1
OPENAI_API_KEY=any-non-empty-string
INFERENCE_TEXT_MODEL=Hermes-4-70B
```

同样的模式也适用于 Open WebUI、LobeChat、NextChat 或任何其他 OpenAI 兼容客户端。

## 在局域网中暴露

默认情况下，代理绑定到 `127.0.0.1`（仅限本地主机）。要让网络中的其他机器使用它：

```bash
hermes proxy start --host 0.0.0.0 --port 8645
```

⚠ **请注意：** 网络中的任何人都可以使用你的 Portal 订阅。代理本身没有认证机制——它接受任何承载令牌。如果在受信任网络之外暴露，请使用防火墙、VPN 或带有适当认证的反向代理。

## 速率限制

你的 Portal 套餐的 RPM/TPM 限制适用于整个代理。代理不会进行扇出或池化——它是一个承载令牌，代表你全部订阅配额。在 [portal.nousresearch.com](https://portal.nousresearch.com) 监控使用情况。

## 架构

代理设计得尽量简洁。每个请求的处理流程如下：

1. 从你的应用接收 `POST /v1/chat/completions`
2. 查找适配器的当前凭证（如果即将过期则刷新）
3. 原样转发请求体，并附加 `Authorization: Bearer <minted-key>`
4. 将响应原样流式返回（保留 SSE）

无转换。不记录请求体。无代理循环。代理只是一个附加凭证的透传层。

## 未来：更多 OAuth 提供商

适配器系统是可插拔的。添加新的提供商（例如 HuggingFace、GitHub Copilot 的聊天端点、通过 OAuth 的 Anthropic）需要在 `hermes_cli/proxy/adapters/<provider>.py` 中实现 `UpstreamAdapter`，并在 `adapters/__init__.py` 中注册。在协议层面不兼容 OpenAI 的提供商（例如 Anthropic Messages API）需要转换层，这超出了当前范围。