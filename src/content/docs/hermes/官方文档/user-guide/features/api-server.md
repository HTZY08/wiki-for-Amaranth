---
title: Api Server
---

sidebar_position: 14
title: "API 服务器"
description: "将 hermes-agent 暴露为兼容 OpenAI 的 API，供任何前端使用"
---

--- body ---
# API 服务器

API 服务器将 hermes-agent 暴露为一个兼容 OpenAI 的 HTTP 端点。任何支持 OpenAI 格式的前端——Open WebUI、LobeChat、LibreChat、NextChat、ChatBox 等——都可以连接到 hermes-agent 并将其用作后端。

你的代理（Agent）使用其全套工具（终端、文件操作、网页搜索、记忆、技能）处理请求，并返回最终响应。在流式传输时，工具进度指示器会内联显示，以便前端展示代理正在执行的操作。

:::tip 一个后端同时覆盖模型和工具
Hermes 本身需要一个已配置的提供者（provider）和工具后端，API 服务器才能发挥作用。一个 [Nous Portal](/user-guide/features/tool-gateway) 订阅即可处理两者——300+ 模型以及通过工具网关（Tool Gateway）提供的网页/图像/TTS/浏览器功能。在启动 API 服务器之前运行 `hermes setup --portal` 一次，像 Open WebUI 或 LobeChat 这样的前端就能获得一个工具齐全的后端。
:::

## 快速开始

### 1. 启用 API 服务器

添加到 `~/.hermes/.env`：

```bash
API_SERVER_ENABLED=true
API_SERVER_KEY=change-me-local-dev
# 可选：仅当浏览器需要直接调用 Hermes 时才需要
# API_SERVER_CORS_ORIGINS=http://localhost:3000
```

### 2. 启动网关

```bash
hermes gateway
```

你会看到：

```
[API Server] API server listening on http://127.0.0.1:8642
```

### 3. 连接前端

将任何兼容 OpenAI 的客户端指向 `http://localhost:8642/v1`：

```bash
# 使用 curl 测试
curl http://localhost:8642/v1/chat/completions \
  -H "Authorization: Bearer change-me-local-dev" \
  -H "Content-Type: application/json" \
  -d '{"model": "hermes-agent", "messages": [{"role": "user", "content": "Hello!"}]}'
```

或者连接 Open WebUI、LobeChat 或任何其他前端——请参阅 [Open WebUI 集成指南](/user-guide/messaging/open-webui) 获取详细步骤。

## 端点

### POST /v1/chat/completions

标准 OpenAI 聊天补全（Chat Completions）格式。无状态——每次请求通过 `messages` 数组包含完整的对话。

**请求：**
```json
{
  "model": "hermes-agent",
  "messages": [
    {"role": "system", "content": "你是一个 Python 专家。"},
    {"role": "user", "content": "写一个斐波那契函数"}
  ],
  "stream": false
}
```

**响应：**
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1710000000,
  "model": "hermes-agent",
  "choices": [{
    "index": 0,
    "message": {"role": "assistant", "content": "这是一个斐波那契函数..."},
    "finish_reason": "stop"
  }],
  "usage": {"prompt_tokens": 50, "completion_tokens": 200, "total_tokens": 250}
}
```

**内联图像输入：** 用户消息可以发送 `content` 作为 `text` 和 `image_url` 部分的数组。支持远程 `http(s)` URL 和 `data:image/...` URL：

```json
{
  "model": "hermes-agent",
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "这张图片里有什么？"},
        {"type": "image_url", "image_url": {"url": "https://example.com/cat.png", "detail": "high"}}
      ]
    }
  ]
}
```

上传的文件（`file` / `input_file` / `file_id`）和非图像 `data:` URL 会返回 `400 unsupported_content_type`。

**流式传输**（`"stream": true`）：返回服务器推送事件（SSE），包含逐 token 的响应块。对于**聊天补全**，流使用标准的 `chat.completion.chunk` 事件以及 Hermes 自定义的 `hermes.tool.progress` 事件用于工具启动的用户体验。对于**响应**，流使用 OpenAI 响应事件类型，例如 `response.created`、`response.output_text.delta`、`response.output_item.added`、`response.output_item.done` 和 `response.completed`。

**流中的工具进度：**
- **聊天补全**：Hermes 发出 `event: hermes.tool.progress` 以提供工具启动可见性，同时不污染持久化的助手文本。
- **响应**：Hermes 在 SSE 流中发出规范原生的 `function_call` 和 `function_call_output` 输出项，因此客户端可以实时渲染结构化的工具 UI。

### POST /v1/responses

OpenAI 响应 API 格式。通过 `previous_response_id` 支持服务器端对话状态——服务器存储完整的对话历史（包括工具调用和结果），因此无需客户端管理即可保留多轮上下文。

**请求：**
```json
{
  "model": "hermes-agent",
  "input": "我的项目中有哪些文件？",
  "instructions": "你是一个有用的编码助手。",
  "store": true
}
```

**响应：**
```json
{
  "id": "resp_abc123",
  "object": "response",
  "status": "completed",
  "model": "hermes-agent",
  "output": [
    {"type": "function_call", "name": "terminal", "arguments": "{\"command\": \"ls\"}", "call_id": "call_1"},
    {"type": "function_call_output", "call_id": "call_1", "output": "README.md src/ tests/"},
    {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "你的项目有..."}]}
  ],
  "usage": {"input_tokens": 50, "output_tokens": 200, "total_tokens": 250}
}
```

**内联图像输入：** `input[].content` 可以包含 `input_text` 和 `input_image` 部分。支持远程 URL 和 `data:image/...` URL：

```json
{
  "model": "hermes-agent",
  "input": [
    {
      "role": "user",
      "content": [
        {"type": "input_text", "text": "描述一下这个屏幕截图。"},
        {"type": "input_image", "image_url": "data:image/png;base64,iVBORw0K..."}
      ]
    }
  ]
}
```

上传的文件（`input_file` / `file_id`）和非图像 `data:` URL 会返回 `400 unsupported_content_type`。

#### 使用 previous_response_id 进行多轮对话

链接响应以跨轮保持完整上下文（包括工具调用）：

```json
{
  "input": "现在显示 README",
  "previous_response_id": "resp_abc123"
}
```

服务器从存储的响应链重建完整对话——所有之前的工具调用和结果都会被保留。链式请求也共享同一个会话，因此多轮对话在仪表板和会话历史中显示为单个条目。

#### 命名对话

使用 `conversation` 参数代替跟踪响应 ID：

```json
{"input": "你好", "conversation": "my-project"}
{"input": "src/ 里有什么？", "conversation": "my-project"}
{"input": "运行测试", "conversation": "my-project"}
```

服务器自动链接到该对话中的最新响应。类似于网关会话的 `/title` 命令。

### GET /v1/responses/\{id\}

通过 ID 检索之前存储的响应。

### DELETE /v1/responses/\{id\}

删除存储的响应。

### GET /v1/models

将代理列为可用模型。广告的模型名称默认为[配置文件](/user-guide/profiles)名称（对于默认配置文件为 `hermes-agent`）。大多数前端需要此端点进行模型发现。

### GET /v1/capabilities

返回 API 服务器稳定表面的机器可读描述，用于外部 UI、编排器和插件桥接。

```json
{
  "object": "hermes.api_server.capabilities",
  "platform": "hermes-agent",
  "model": "hermes-agent",
  "auth": {"type": "bearer", "required": true},
  "features": {
    "chat_completions": true,
    "responses_api": true,
    "run_submission": true,
    "run_status": true,
    "run_events_sse": true,
    "run_stop": true
  }
}
```

在集成仪表板、浏览器 UI 或控制平面时使用此端点，以便它们可以检测运行的 Hermes 版本是否支持 run（运行）、流式传输、取消和会话连续性，而无需依赖私有的 Python 内部实现。

### GET /health

健康检查。返回 `{"status": "ok"}`。也可通过 **GET /v1/health** 访问，用于期望 `/v1/` 前缀的兼容 OpenAI 的客户端。

### GET /health/detailed

扩展健康检查，还报告活动会话、运行中的代理和资源使用情况。适用于监控/可观测性工具。

## Runs API（流式友好替代方案）

除了 `/v1/chat/completions` 和 `/v1/responses` 之外，服务器还公开了一个 **runs** API，用于长期会话，客户端希望订阅进度事件而不是自己管理流式传输。

### POST /v1/runs

创建一个新的代理运行。返回一个 `run_id`，可用于订阅进度事件。

```json
{
  "run_id": "run_abc123",
  "status": "started"
}
```

Runs 接受一个简单的 `input` 字符串和可选的 `session_id`、`instructions`、`conversation_history` 或 `previous_response_id`。当提供 `session_id` 时，Hermes 会在运行状态中显示它，以便外部 UI 可以将运行与其自己的对话 ID 关联起来。

### GET /v1/runs/\{run_id\}

轮询当前运行状态。这对于不需要保持 SSE 连接打开的仪表板，或者在导航后重新连接的 UI 很有用。

```json
{
  "object": "hermes.run",
  "run_id": "run_abc123",
  "status": "completed",
  "session_id": "space-session",
  "model": "hermes-agent",
  "output": "完成。",
  "usage": {"input_tokens": 50, "output_tokens": 200, "total_tokens": 250}
}
```

状态在终端状态（`completed`、`failed` 或 `cancelled`）后会短暂保留，以便轮询和 UI 协调。

### GET /v1/runs/\{run_id\}/events

以服务器推送事件（SSE）流的形式输出运行的工具调用进度、token 增量和生命周期事件。专为希望在不丢失状态的情况下附加/分离的仪表板和厚客户端设计。

### POST /v1/runs/\{run_id\}/stop

中断正在进行的代理轮次。端点立即返回 `{"status": "stopping"}`，同时 Hermes 要求活动代理在下一个安全中断点停止。

### POST /v1/runs/\{run_id\}/approval

解决运行中等待人工决策（例如，受审批策略限制的工具调用）的待处理审批。请求体包含审批决定；一旦记录决定，运行就会恢复。此端点在 `/v1/capabilities` 中以 `run_approval` 特性进行通告，以便外部 UI 在显示审批提示之前检测支持情况。

## Jobs API（后台定时工作）

服务器公开了一个轻量级的 jobs CRUD 表面，用于从远程客户端管理定时/后台代理运行。所有端点都受相同的 bearer 认证保护。

### GET /api/jobs

列出所有定时作业。

### POST /api/jobs

创建一个新的定时作业。请求体接受与 `hermes cron` 相同的结构——提示词、调度、技能、提供者覆盖、交付目标。

### GET /api/jobs/\{job_id\}

获取单个作业的定义和上次运行状态。

### PATCH /api/jobs/\{job_id\}

更新现有作业的字段（提示词、调度等）。部分更新会合并。

### DELETE /api/jobs/\{job_id\}

删除作业。同时取消任何正在进行的运行。

### POST /api/jobs/\{job_id\}/pause

暂停作业而不删除它。下次计划运行的时间戳会暂停，直到恢复。

### POST /api/jobs/\{job_id\}/resume

恢复之前暂停的作业。

### POST /api/jobs/\{job_id\}/run

立即触发作业运行，而不按计划执行。

## Sessions API（通过 REST 控制会话）

外部 UI 可以通过 REST 管理 Hermes 会话，而无需启动仪表板。所有端点都由 `API_SERVER_KEY` 保护，位于 `/api/sessions/*` 下。

| 方法 | 路径 | 描述 |
|--------|------|-------------|
| `GET` | `/api/sessions` | 列出会话（分页——`limit`、`offset`、`source`、`include_children`） |
| `POST` | `/api/sessions` | 创建一个空会话 |
| `GET` | `/api/sessions/{id}` | 读取会话元数据 |
| `PATCH` | `/api/sessions/{id}` | 更新标题或 `end_reason` |
| `DELETE` | `/api/sessions/{id}` | 删除会话 |
| `GET` | `/api/sessions/{id}/messages` | 会话的消息历史 |
| `POST` | `/api/sessions/{id}/fork` | 通过 `SessionDB` 血缘分支会话（匹配 CLI `/branch` 语义） |
| `POST` | `/api/sessions/{id}/chat` | 运行一个同步代理轮次 |
| `POST` | `/api/sessions/{id}/chat/stream` | 单个轮次的 SSE 封装——发出 `assistant.delta`、`tool.started`、`tool.completed`、`run.completed` 事件 |

`/v1/capabilities` 通过 `session_*` 特性标志和 `endpoints.session_*` 条目通告完整的表面，以便外部 UI 检测支持并安全地回退。在 `chat` 和 `chat/stream` 请求体中支持内联图像（多模态感知路径）。

```bash
# 分支会话并运行一个轮次
curl -X POST http://localhost:8642/api/sessions/$ID/fork \
  -H "Authorization: Bearer $API_SERVER_KEY" \
  -d '{"title": "探索替代路径"}'

# 通过 SSE 流式传输一个轮次
curl -N -X POST http://localhost:8642/api/sessions/$ID/chat/stream \
  -H "Authorization: Bearer $API_SERVER_KEY" \
  -d '{"input": "过去一小时哪些文件发生了变化？"}'
```

## 技能和工具集发现

`GET /v1/skills` 和 `GET /v1/toolsets` 允许外部客户端通过 REST 确定性地枚举代理的能力，而不是询问模型。两者都是只读的，并由 `API_SERVER_KEY` 保护。

```bash
curl http://localhost:8642/v1/skills \
  -H "Authorization: Bearer $API_SERVER_KEY"
# → [{"name": "github-pr-workflow", "description": "...", "category": "..."}, ...]

curl http://localhost:8642/v1/toolsets \
  -H "Authorization: Bearer $API_SERVER_KEY"
# → [{"name": "core", "label": "...", "description": "...", "enabled": true,
#     "configured": true, "tools": ["read_file", "write_file", ...]}, ...]
```

`/v1/skills` 返回技能中心内部使用的相同元数据。`/v1/toolsets` 返回为 `api_server` 平台解析的工具集，包含每个工具集展开的具体 `tools` 列表。两者都在 `/v1/capabilities` 中的 `endpoints.*` 下进行通告。

## 长期记忆作用域（`X-Hermes-Session-Key`）

像 Open WebUI 这样的多用户前端需要一个稳定的每通道标识符用于长期记忆（Honcho 等），该标识符**独立于**抄本作用域的 `X-Hermes-Session-Id`（后者在 `/new` 时轮换）。在 `/v1/chat/completions`、`/v1/responses` 或 `/v1/runs` 上传递 `X-Hermes-Session-Key`，Hermes 会将其传递到 `AIAgent(gateway_session_key=...)`，其中 Honcho 记忆提供者使用它来推导出稳定的作用域。

```http
POST /v1/chat/completions HTTP/1.1
Authorization: Bearer ***
X-Hermes-Session-Id: transcript-alpha
X-Hermes-Session-Key: agent:main:webui:dm:user-42
```

规则：最多 256 个字符，拒绝控制字符（`\r`、`\n`、`\x00`），并且该值会在响应中回显（JSON + SSE）。`/v1/capabilities` 通过 `"session_key_header": "X-Hermes-Session-Key"` 通告支持。如果没有此键，Honcho 的 `per-session` 策略会对每个 `session_id` 产生不同的作用域——这正是 Hermes 之前的行为。

## 系统提示处理

当前端发送 `system` 消息（聊天补全）或 `instructions` 字段（响应 API）时，hermes-agent 会将其**叠加**到其核心系统提示之上。你的代理保留所有工具、记忆和技能——前端的系统提示只是添加额外指令。

这意味着你可以在不丢失能力的情况下为每个前端定制行为：
- Open WebUI 系统提示：“你是一个 Python 专家。始终包含类型提示。”
- 代理仍然拥有终端、文件工具、网页搜索、记忆等。

## 认证

通过 `Authorization` 头进行 Bearer token 认证：

```
Authorization: Bearer ***
```

通过 `API_SERVER_KEY` 环境变量配置密钥。如果你需要浏览器直接调用 Hermes，还需将 `API_SERVER_CORS_ORIGINS` 设置为明确的白名单。

:::warning 安全
API 服务器提供对 hermes-agent 工具集的完全访问权限，**包括终端命令**。`API_SERVER_KEY` 在**每个部署中都是必需的**，包括默认的回环绑定 `127.0.0.1`。保持 `API_SERVER_CORS_ORIGINS` 狭窄，以在你明确允许浏览器调用者时控制浏览器访问。
:::

## 配置

### 环境变量

| 变量 | 默认值 | 描述 |
|----------|---------|-------------|
| `API_SERVER_ENABLED` | `false` | 启用 API 服务器 |
| `API_SERVER_PORT` | `8642` | HTTP 服务器端口 |
| `API_SERVER_HOST` | `127.0.0.1` | 绑定地址（默认仅 localhost） |
| `API_SERVER_KEY` | _(必需)_ | 用于认证的 Bearer token |
| `API_SERVER_CORS_ORIGINS` | _(无)_ | 允许的浏览器来源，以逗号分隔 |
| `API_SERVER_MODEL_NAME` | _(配置文件名)_ | `/v1/models` 上的模型名称。默认为配置文件名，对于默认配置文件为 `hermes-agent`。 |

### config.yaml

```yaml
# 尚未支持——请使用环境变量。
# config.yaml 支持将在未来版本中提供。
```

## 安全头

所有响应都包含安全头：
- `X-Content-Type-Options: nosniff` — 防止 MIME 类型嗅探
- `Referrer-Policy: no-referrer` — 防止 referrer 泄漏

## CORS

默认情况下，API 服务器**不**启用浏览器 CORS。

对于直接浏览器访问，设置明确的允许列表：

```bash
API_SERVER_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

当 CORS 启用时：
- **预检响应**包含 `Access-Control-Max-Age: 600`（10 分钟缓存）
- **SSE 流式响应**包含 CORS 头，以便浏览器 EventSource 客户端正常工作
- **`Idempotency-Key`** 是允许的请求头——客户端可以发送它以进行去重（响应按键缓存 5 分钟）

大多数有文档的前端（如 Open WebUI）进行服务器到服务器的连接，根本不需要 CORS。

## 兼容的前端

任何支持 OpenAI API 格式的前端都可以使用。已测试/有文档的集成：

| 前端 | Stars | 连接方式 |
|----------|-------|------------|
| [Open WebUI](/user-guide/messaging/open-webui) | 126k | 提供完整指南 |
| LobeChat | 73k | 自定义提供者端点 |
| LibreChat | 34k | 在 librechat.yaml 中自定义端点 |
| AnythingLLM | 56k | 通用 OpenAI 提供者 |
| NextChat | 87k | BASE_URL 环境变量 |
| ChatBox | 39k | API 主机设置 |
| Jan | 26k | 远程模型配置 |
| HF Chat-UI | 8k | OPENAI_BASE_URL |
| big-AGI | 7k | 自定义端点 |
| OpenAI Python SDK | — | `OpenAI(base_url="http://localhost:8642/v1")` |
| curl | — | 直接 HTTP 请求 |

## 使用配置文件的多用户设置

要为多个用户提供他们自己的隔离 Hermes 实例（独立的配置、记忆、技能），请使用[配置文件](/user-guide/profiles)：

```bash
# 为每个用户创建一个配置文件
hermes profile create alice
hermes profile create bob

# 在每个配置文件的不同端口上配置 API 服务器。API_SERVER_* 是环境变量
# （不是 config.yaml 键），因此将它们写入每个配置文件的 .env：
cat >> ~/.hermes/profiles/alice/.env <<EOF
API_SERVER_ENABLED=true
API_SERVER_PORT=8643
API_SERVER_KEY=alice-secret
EOF

cat >> ~/.hermes/profiles/bob/.env <<EOF
API_SERVER_ENABLED=true
API_SERVER_PORT=8644
API_SERVER_KEY=bob-secret
EOF

# 启动每个配置文件的网关
hermes -p alice gateway &
hermes -p bob gateway &
```

每个配置文件的 API 服务器会自动将配置文件名作为模型 ID 进行通告：

- `http://localhost:8643/v1/models` → 模型 `alice`
- `http://localhost:8644/v1/models` → 模型 `bob`

在 Open WebUI 中，将每个作为单独的连接添加。模型下拉菜单会显示 `alice` 和 `bob` 作为不同的模型，每个都后接一个完全隔离的 Hermes 实例。详见 [Open WebUI 指南](/user-guide/messaging/open-webui#multi-user-setup-with-profiles)。

## 限制

- **响应存储** — 存储的响应（用于 `previous_response_id`）会持久化在 SQLite 中，并在网关重启后仍然存在。最多 100 个存储的响应（LRU 淘汰）。
- **无文件上传** — 在 `/v1/chat/completions` 和 `/v1/responses` 上都支持内联图像，但上传的文件（`file`、`input_file`、`file_id`）和非图像文档输入不支持通过 API 进行。
- **模型字段是装饰性的** — 请求中的 `model` 字段会被接受，但实际使用的 LLM 模型是在服务器端的 config.yaml 中配置的。

## 代理模式

API 服务器也用作**网关代理模式**的后端。当另一个 Hermes 网关实例配置了指向此 API 服务器的 `GATEWAY_PROXY_URL` 时，它会将所有消息转发到这里，而不是运行自己的代理。这实现了分离部署——例如，一个处理 Matrix E2EE 的 Docker 容器将中继到主机端的代理。

请参阅 [Matrix 代理模式](/user-guide/messaging/matrix#proxy-mode-e2ee-on-macos) 获取完整设置指南。