---
title: Index
---

title: "集成"
sidebar_label: "概述"
sidebar_position: 0
---

--- body ---
# 集成

Hermes Agent 连接外部系统以实现 AI 推理、工具服务器、IDE 工作流、程序化访问等功能。这些集成扩展了 Hermes 的能力和运行范围。

:::tip 从这里开始
如果你只有时间设置一个集成，建议设置 [Nous Portal](/integrations/nous-portal) — 一次 OAuth 登录即可覆盖 300 多个模型以及四个 Tool Gateway 工具（网页搜索、图像生成、TTS 和浏览器自动化）。
:::

## AI 提供商与路由

Hermes 开箱即支持多个 AI 推理提供商。使用 `hermes model` 进行交互式配置，或在 `config.yaml` 中设置。

- **[AI 提供商（AI Providers）](/user-guide/features/provider-routing)** — OpenRouter、Anthropic、OpenAI、Google 以及任何兼容 OpenAI 的端点。Hermes 可自动检测每个提供商的能力，如视觉、流式传输和工具使用。
- **[提供商路由（Provider Routing）](/user-guide/features/provider-routing)** — 精细控制哪些底层提供商处理你的 OpenRouter 请求。通过排序、白名单、黑名单和显式优先级排序，优化成本、速度或质量。
- **[回退提供商（Fallback Providers）](/user-guide/features/fallback-providers)** — 当主模型遇到错误时，自动故障转移到备用 LLM 提供商。包括主模型回退以及独立的辅助任务回退（用于视觉、压缩和网页提取）。

## 工具服务器（MCP）

- **[MCP 服务器（MCP Servers）](/user-guide/features/mcp)** — 通过模型上下文协议（Model Context Protocol）将 Hermes 连接到外部工具服务器。可从 GitHub、数据库、文件系统、浏览器堆栈、内部 API 等访问工具，而无需编写原生 Hermes 工具。支持 stdio 和 SSE 传输方式、每个服务器工具过滤以及支持能力的资源/提示注册。

## 网页搜索后端

`web_search` 和 `web_extract` 工具支持八个后端提供商，通过 `config.yaml` 或 `hermes tools` 配置：

| 后端 | 环境变量 | 搜索 | 提取 | 爬取 |
|---------|---------|--------|---------|-------|
| **Firecrawl**（默认） | `FIRECRAWL_API_KEY` | ✔ | ✔ | ✔ |
| **SearXNG** | `SEARXNG_URL` | ✔ | — | — |
| **Brave**（免费层） | `BRAVE_SEARCH_API_KEY` | ✔ | — | — |
| **DuckDuckGo**（ddgs） | _（无）_ | ✔ | — | — |
| **Tavily** | `TAVILY_API_KEY` | ✔ | ✔ | ✔ |
| **Exa** | `EXA_API_KEY` | ✔ | ✔ | — |
| **Parallel** | `PARALLEL_API_KEY` | ✔ | ✔ | — |
| **xAI** | `XAI_API_KEY` | ✔ | — | — |

快速设置示例：

```yaml
web:
  backend: firecrawl    # firecrawl | searxng | brave-free | ddgs | tavily | exa | parallel | xai
```

如果未设置 `web.backend`，后端将根据可用的 API 密钥自动检测。自托管 Firecrawl 也受支持，通过 `FIRECRAWL_API_URL` 进行设置。

## 浏览器自动化

Hermes 包含完整的浏览器自动化功能，具有多个后端选项，可用于导航网站、填写表单和提取信息：

- **Browserbase** — 托管云浏览器，具有反机器人工具、CAPTCHA 解决和住宅代理
- **Browser Use** — 替代云浏览器提供商
- **本地 Chromium 系列 CDP** — 使用 `/browser connect` 连接到正在运行的 Chrome、Brave、Chromium 或 Edge 浏览器
- **本地 Chromium** — 通过 `agent-browser` CLI 运行的无头本地浏览器

有关设置和使用，请参阅[浏览器自动化](/user-guide/features/browser)。

## 语音与 TTS 提供商

所有消息平台上的文本转语音和语音转文本：

| 提供商 | 质量 | 成本 | API 密钥 |
|----------|---------|------|---------|
| **Edge TTS**（默认） | 良好 | 免费 | 无需 |
| **ElevenLabs** | 优秀 | 付费 | `ELEVENLABS_API_KEY` |
| **OpenAI TTS** | 良好 | 付费 | `VOICE_TOOLS_OPENAI_KEY` |
| **MiniMax** | 良好 | 付费 | `MINIMAX_API_KEY` |
| **xAI TTS** | 良好 | 付费 | `XAI_API_KEY` |
| **NeuTTS** | 良好 | 免费 | 无需 |

语音转文本支持六个提供商：本地 faster-whisper（免费，在设备上运行）、本地命令包装器、Groq、OpenAI Whisper API、Mistral 和 xAI。语音消息转录在 Telegram、Discord、WhatsApp 和其他消息平台上均可使用。有关详细信息，请参阅[语音与 TTS](/user-guide/features/tts) 和[语音模式](/user-guide/features/voice-mode)。

## IDE 与编辑器集成

- **[IDE 集成（ACP）](/user-guide/features/acp)** — 在 ACP 兼容的编辑器（如 VS Code、Zed 和 JetBrains）中使用 Hermes Agent。Hermes 作为 ACP 服务器运行，在编辑器中呈现聊天消息、工具活动、文件差异和终端命令。

## 程序化访问

- **[API 服务器（API Server）](/user-guide/features/api-server)** — 将 Hermes 暴露为兼容 OpenAI 的 HTTP 端点。任何支持 OpenAI 格式的前端——Open WebUI、LobeChat、LibreChat、NextChat、ChatBox——都可以连接并使用 Hermes 作为后端，并享受其完整的工具集。

## 记忆与个性化

- **[内置记忆（Built-in Memory）](/user-guide/features/memory)** — 通过 `MEMORY.md` 和 `USER.md` 文件实现持久化的精选记忆。代理维护个人笔记和用户配置文件的有界存储，这些信息在会话之间保持。
- **[记忆提供商（Memory Providers）](/user-guide/features/memory-providers)** — 接入外部记忆后端以实现更深层次的个性化。支持八个提供商：Honcho（辩证推理）、OpenViking（分层检索）、Mem0（云端提取）、Hindsight（知识图谱）、Holographic（本地 SQLite）、RetainDB（混合搜索）、ByteRover（基于 CLI）和 Supermemory。

## 消息平台

Hermes 作为网关机器人运行在 27 个以上的消息平台上，所有平台都通过相同的 `gateway` 子系统进行配置：

- **[Telegram](/user-guide/messaging/telegram)**、**[Discord](/user-guide/messaging/discord)**、**[Slack](/user-guide/messaging/slack)**、**[WhatsApp](/user-guide/messaging/whatsapp)**、**[Signal](/user-guide/messaging/signal)**、**[Matrix](/user-guide/messaging/matrix)**、**[Mattermost](/user-guide/messaging/mattermost)**、**[Email](/user-guide/messaging/email)**、**[短信（SMS）](/user-guide/messaging/sms)**、**[钉钉（DingTalk）](/user-guide/messaging/dingtalk)**、**[飞书（Feishu/Lark）](/user-guide/messaging/feishu)**、**[企业微信（WeCom）](/user-guide/messaging/wecom)**、**[企业微信回调（WeCom Callback）](/user-guide/messaging/wecom-callback)**、**[微信（Weixin）](/user-guide/messaging/weixin)**、**[BlueBubbles](/user-guide/messaging/bluebubbles)**、**[QQ 机器人（QQ Bot）](/user-guide/messaging/qqbot)**、**[元宝（Yuanbao）](/user-guide/messaging/yuanbao)**、**[Home Assistant](/user-guide/messaging/homeassistant)**、**[Microsoft Teams](/user-guide/messaging/teams)**、**[Microsoft Teams 会议（Microsoft Teams Meetings）](/user-guide/messaging/teams-meetings)**、**[Microsoft Graph Webhook](/user-guide/messaging/msgraph-webhook)**、**[Google Chat](/user-guide/messaging/google_chat)**、**[LINE](/user-guide/messaging/line)**、**[ntfy](/user-guide/messaging/ntfy)**、**[SimpleX](/user-guide/messaging/simplex)**、**[Open WebUI](/user-guide/messaging/open-webui)**、**[Webhooks](/user-guide/messaging/webhooks)**

请参阅[消息网关概述](/user-guide/messaging)以获取平台比较表和设置指南。

## 家庭自动化

- **[Home Assistant](/user-guide/messaging/homeassistant)** — 通过四个专用工具（`ha_list_entities`、`ha_get_state`、`ha_list_services`、`ha_call_service`）控制智能家居设备。当配置了 `HASS_TOKEN` 时，Home Assistant 工具集将自动激活。

## 插件

- **[插件系统（Plugin System）](/user-guide/features/plugins)** — 通过自定义工具、生命周期钩子和 CLI 命令扩展 Hermes，无需修改核心代码。插件可从 `~/.hermes/plugins/`、项目本地 `.hermes/plugins/` 以及 pip 安装的入口点发现。
- **[构建插件（Build a Plugin）](/guides/build-a-hermes-plugin)** — 创建具有工具、钩子和 CLI 命令的 Hermes 插件的逐步指南。

## 训练与评估

- **[批量处理（Batch Processing）](/user-guide/features/batch-processing)** — 并行在数百个提示上运行代理，生成结构化的 ShareGPT 格式轨迹数据，用于训练数据生成或评估。