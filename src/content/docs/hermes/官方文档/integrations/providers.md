---
title: AI 提供商
---

本页介绍如何为 Hermes Agent 配置推理提供商——从 OpenRouter 和 Anthropic 等云 API，到 Ollama 和 vLLM 等自托管端点，以及高级路由和备用配置。你需要至少配置一个提供商才能使用 Hermes。

## 推理提供商

你至少需要一种方式连接到 LLM。使用 `hermes model` 交互式切换提供商和模型，或直接配置：

| 提供商 | 配置方式 |
| --- | --- |
| Nous Portal | `hermes model`（OAuth，基于订阅） |
| OpenAI Codex | `hermes model`（ChatGPT OAuth，使用 Codex 模型） |
| GitHub Copilot | `hermes model`（OAuth 设备码流程，`COPILOT_GITHUB_TOKEN`，`GH_TOKEN`，或 `gh auth token`） |
| GitHub Copilot ACP | `hermes model`（启动本地 `copilot --acp --stdio`） |
| Anthropic | `hermes model`（Claude Max + 通过 OAuth 的额外用量积分；也支持 Anthropic API 密钥或手动 setup-token——见下方说明） |
| OpenRouter | `~/.hermes/.env` 中的 `OPENROUTER_API_KEY` |
| Fireworks AI | `~/.hermes/.env` 中的 `FIREWORKS_API_KEY`（provider: `fireworks`；别名: `fireworks-ai`, `fw`） |
| NovitaAI | `~/.hermes/.env` 中的 `NOVITA_API_KEY`（provider: `novita`，200+ 模型，Model API，Agent Sandbox，GPU Cloud） |
| z.ai / GLM | `~/.hermes/.env` 中的 `GLM_API_KEY`（provider: `zai`） |
| Kimi / Moonshot | `~/.hermes/.env` 中的 `KIMI_API_KEY`（provider: `kimi-coding`） |
| Kimi / Moonshot（中国） | `~/.hermes/.env` 中的 `KIMI_CN_API_KEY`（provider: `kimi-coding-cn`；别名: `kimi-cn`, `moonshot-cn`） |
| Arcee AI | `~/.hermes/.env` 中的 `ARCEEAI_API_KEY`（provider: `arcee`；别名: `arcee-ai`, `arceeai`） |
| GMI Cloud | `~/.hermes/.env` 中的 `GMI_API_KEY`（provider: `gmi`；别名: `gmi-cloud`, `gmicloud`） |
| MiniMax | `~/.hermes/.env` 中的 `MINIMAX_API_KEY`（provider: `minimax`） |
| MiniMax 中国 | `~/.hermes/.env` 中的 `MINIMAX_CN_API_KEY`（provider: `minimax-cn`） |
| xAI (Grok) — Responses API | `~/.hermes/.env` 中的 `XAI_API_KEY`（provider: `xai`） |
| xAI Grok OAuth (SuperGrok) | `hermes model` → "xAI Grok OAuth (SuperGrok / Premium+)" — 浏览器登录，无需 API 密钥。参见指南 |
| Qwen Cloud（阿里云 DashScope） | `~/.hermes/.env` 中的 `DASHSCOPE_API_KEY`（provider: `alibaba`） |
| 阿里云（Coding Plan） | `DASHSCOPE_API_KEY`（provider: `alibaba-coding-plan`，别名: `alibaba_coding`）— 独立计费 SKU，不同端点 |
| Kilo Code | `~/.hermes/.env` 中的 `KILOCODE_API_KEY`（provider: `kilocode`） |
| 小米 MiMo | `~/.hermes/.env` 中的 `XIAOMI_API_KEY`（provider: `xiaomi`，别名: `mimo`, `xiaomi-mimo`） |
| 腾讯 TokenHub | `~/.hermes/.env` 中的 `TOKENHUB_API_KEY`（provider: `tencent-tokenhub`，别名: `tencent`, `tokenhub`, `tencentmaas`） |
| OpenCode Zen | `~/.hermes/.env` 中的 `OPENCODE_ZEN_API_KEY`（provider: `opencode-zen`） |
| OpenCode Go | `~/.hermes/.env` 中的 `OPENCODE_GO_API_KEY`（provider: `opencode-go`） |
| DeepSeek | `~/.hermes/.env` 中的 `DEEPSEEK_API_KEY`（provider: `deepseek`） |
| Hugging Face | `~/.hermes/.env` 中的 `HF_TOKEN`（provider: `huggingface`，别名: `hf`） |
| Google / Gemini | `~/.hermes/.env` 中的 `GOOGLE_API_KEY`（或 `GEMINI_API_KEY`）（provider: `gemini`） |
| Google Vertex AI | `hermes model` → "Google Vertex AI"（provider: `vertex`；通过服务账号 JSON 或 ADC 的 OAuth2，GCP 计费） |
| OpenAI API（直接） | `~/.hermes/.env` 中的 `OPENAI_API_KEY`（provider: `openai-api`，可选 `OPENAI_BASE_URL`） |
| Azure AI Foundry | `hermes model` → "Azure AI Foundry"（provider: `azure-foundry`；使用 Azure OpenAI / Foundry 端点和密钥） |
| AWS Bedrock | `hermes model` → "AWS Bedrock"（provider: `bedrock`；通过 boto3 的标准 AWS 凭证链） |
| NVIDIA Build | `~/.hermes/.env` 中的 `NVIDIA_API_KEY`（provider: `nvidia`；build.nvidia.com 上的 NIM 托管模型） |
| Ollama Cloud | `hermes model` → "Ollama Cloud"（provider: `ollama-cloud`；云端托管 Ollama API） |
| Qwen OAuth | `hermes model` → "Qwen OAuth"（provider: `qwen-oauth`；浏览器 PKCE 登录） |
| MiniMax OAuth | `hermes model` → "MiniMax (OAuth)"（provider: `minimax-oauth`；浏览器 PKCE 登录） |
| StepFun | `~/.hermes/.env` 中的 `STEPFUN_API_KEY`（provider: `stepfun`） |
| LM Studio | `hermes model` → "LM Studio"（provider: `lmstudio`，可选 `LM_API_KEY`） |
| 自定义端点 | `hermes model` → 选择 "Custom endpoint"（保存在 `config.yaml` 中） |

对于官方 API 密钥路径，请参见专门的 Google Gemini 指南。

模型键别名

在 `model:` 配置段中，你可以使用 `default:` 或 `model:` 作为模型 ID 的键名。`model: { default: my-model }` 和 `model: { model: my-model }` 两种写法效果相同。

### Nous Portal

Nous Portal 是 Nous Research 的统一订阅网关，也是运行 Hermes Agent 的推荐方式。一次 OAuth 登录即可覆盖 300 多个前沿 Agent 模型（Claude、GPT、Gemini、DeepSeek、Qwen、Kimi、GLM、MiniMax、Grok...），以及 Tool Gateway（网页搜索、图像生成、TTS、浏览器自动化）和 Nous Chat——均通过你的 Nous 订阅计费，无需单独的提供商账户。

```bash
hermes setup --portal     # 全新安装 — 一步完成 OAuth + 提供商 + 网关配置
hermes model              # 已有安装 — 从列表中选择 "Nous Portal"
hermes portal info        # 随时查看登录和路由状态
```

还没有订阅？请访问 portal.nousresearch.com/manage-subscription 获取。

完整详情：请参见专门的 Nous Portal 集成页面（订阅内容、模型目录、故障排除）和分步指南《使用 Nous Portal 运行 Hermes Agent》。

客户端标识。Hermes Agent 的每个 Portal 请求都会携带 `client=hermes-client-v<版本>` 标签（例如 `client=hermes-client-v0.13.0`），自动匹配你安装的版本。该标签会发送到所有 Portal 路径——主聊天循环、辅助调用、压缩摘要器、网页提取——让 Portal 端遥测能够区分 Hermes 流量和其他客户端。无需配置；运行 `hermes update` 时标签会自动更新。

JWT 认证（自动）。Hermes 优先使用作用域为 `inference:invoke` 的 JWT 进行 Portal 请求，同时保留传统不透明会话密钥路径作为回退。无需配置——凭证由 OAuth 流管理并透明轮换。被撤销的刷新令牌会被隔离，避免重放循环。

Codex 说明

OpenAI Codex 提供商通过设备码进行认证（打开 URL，输入验证码）。Hermes 将生成的凭据存储在自己的认证存储 `~/.hermes/auth.json` 中，也可以在存在时导入现有 Codex CLI 凭据（`~/.codex/auth.json`）。无需安装 Codex CLI。

如果令牌刷新遇到致命错误（HTTP 4xx、`invalid_grant`、已撤销授权等），Hermes 会将刷新令牌标记为失效并停止重试，避免出现大量相同的认证失败。下次请求会显示类型化的重新认证消息。运行 `hermes auth add openai-codex`（或 `hermes model` → OpenAI Codex）开始新的设备码登录；隔离状态在下一次成功交换后清除。

警告

即使使用 Nous Portal、Codex 或自定义端点，某些工具（视觉、网页摘要、MoA）也会使用独立的"辅助"模型。默认情况下（`auxiliary.*.provider: "auto"`），Hermes 将这些任务路由到你的主聊天模型——即你在 `hermes model` 中选择的同一模型。你可以单独覆盖每个任务，将其路由到更便宜/更快的模型（例如 OpenRouter 上的 Gemini Flash）——参见辅助模型。

Nous Tool Gateway

付费的 Nous Portal 订阅用户还可以使用 Tool Gateway——网页搜索、图像生成、TTS 和浏览器自动化，全部通过你的订阅路由。无需额外的 API 密钥。全新安装时，`hermes setup --portal` 会一步完成登录、设置 Nous 为提供商并启用网关。已有用户可以从 `hermes model` 启用，或通过 `hermes tools` 按工具启用。随时使用 `hermes portal info` 查看路由状态。

### 两个模型管理命令

Hermes 有两个服务于不同目的的模型命令：

| 命令 | 在哪里运行 | 功能 |
| --- | --- | --- |
| `hermes model` | 你的终端（在会话之外） | 完整设置向导——添加提供商、运行 OAuth、输入 API 密钥、配置端点 |
| `/model` | 在 Hermes 聊天会话内部 | 在已配置的提供商和模型之间快速切换 |

如果你要切换到尚未设置的提供商（例如你只配置了 OpenRouter，想使用 Anthropic），你需要 `hermes model`，而不是 `/model`。先退出当前会话（`Ctrl+C` 或 `/quit`），运行 `hermes model` 完成提供商设置，然后启动新会话。

### Anthropic（原生）

直接通过 Anthropic API 使用 Claude 模型——无需 OpenRouter 代理。支持三种认证方式：

需要 Claude Max "额外用量"积分

当你通过 `hermes model` → Anthropic OAuth（或通过 `hermes auth add anthropic --type oauth`）进行认证时，Hermes 会作为 Claude Code 路由到你的 Anthropic 账户。这仅在你拥有 Claude Max 计划并购买了额外用量积分时才有效。基础 Max 计划配额（Claude Code 默认包含的用量）不会被 Hermes 消耗——只有你额外添加的超额积分会被消耗。Claude Pro 订阅用户无法使用此路径。

如果你没有 Max + 额外积分，请改用 `ANTHROPIC_API_KEY`——请求将按该密钥组织的按 token 计费方式计费（标准 API 定价，与任何 Claude 订阅无关）。

```bash
# 使用 API 密钥（按 token 付费）
export ANTHROPIC_API_KEY=***
hermes chat --provider anthropic --model claude-sonnet-4-6

# 推荐：通过 `hermes model` 认证
# Hermes 会在可用时直接使用 Claude Code 的凭据存储
hermes model

# 使用 setup-token 手动覆盖（备用/旧版方式）
export ANTHROPIC_TOKEN=***  # setup-token 或手动 OAuth 令牌
hermes chat --provider anthropic

# 自动检测 Claude Code 凭据（如果你已在使用 Claude Code）
hermes chat --provider anthropic  # 自动读取 Claude Code 凭据文件
```

当通过 `hermes model` 选择 Anthropic OAuth 时，Hermes 优先使用 Claude Code 自己的凭据存储，而不是将令牌复制到 `~/.hermes/.env`。这样可以使可刷新的 Claude 凭据保持可刷新状态。

或永久设置：

```yaml
model:
  provider: "anthropic"
  default: "claude-sonnet-4-6"
```

别名

`--provider claude` 和 `--provider claude-code` 也可以作为 `--provider anthropic` 的简写。

### GitHub Copilot

Hermes 支持 GitHub Copilot 作为一等提供商，有两种模式：

`copilot` — 直接 Copilot API（推荐）。使用你的 GitHub Copilot 订阅通过 Copilot API 访问 GPT-5.x、Claude、Gemini 和其他模型。

```bash
hermes chat --provider copilot --model gpt-5.4
```

认证选项（按此顺序检查）：

1. `COPILOT_GITHUB_TOKEN` 环境变量
2. `GH_TOKEN` 环境变量
3. `GITHUB_TOKEN` 环境变量
4. `gh auth token` CLI 回退

如果未找到令牌，`hermes model` 会提供 OAuth 设备码登录——与 Copilot CLI 和 opencode 使用的流程相同。

令牌类型

Copilot API 不支持经典的个人访问令牌（`ghp_*`）。支持的令牌类型：

| 类型 | 前缀 | 获取方式 |
| --- | --- | --- |
| OAuth 令牌 | `gho_` | `hermes model` → GitHub Copilot → 使用 GitHub 登录 |
| 细粒度 PAT | `github_pat_` | GitHub 设置 → Developer settings → Fine-grained tokens（需要 Copilot Requests 权限） |
| GitHub App 令牌 | `ghu_` | 通过 GitHub App 安装 |

如果你的 `gh auth token` 返回 `ghp_*` 令牌，请改用 `hermes model` 通过 OAuth 认证。

Hermes 中的 Copilot 认证行为

Hermes 将支持的 GitHub 令牌（`gho_*`、`github_pat_*` 或 `ghu_*`）直接发送到 `api.githubcopilot.com`，并包含 Copilot 专用头部（`Editor-Version`、`Copilot-Integration-Id`、`Openai-Intent`、`x-initiator`）。

在 HTTP 401 时，Hermes 现在会在回退前执行一次凭据恢复：

1. 通过正常优先级链重新解析令牌（`COPILOT_GITHUB_TOKEN` → `GH_TOKEN` → `GITHUB_TOKEN` → `gh auth token`）
2. 用刷新的头部重建共享 OpenAI 客户端
3. 重试请求一次

某些较旧的社区代理使用 `api.github.com/copilot_internal/v2/token` 交换流程。该端点对某些账户类型可能不可用（返回 404）。因此 Hermes 将直接令牌认证作为主要路径，并依赖运行时凭据刷新 + 重试来保证稳健性。

API 路由：GPT-5+ 模型（除了 `gpt-5-mini`）自动使用 Responses API。所有其他模型（GPT-4o、Claude、Gemini 等）使用 Chat Completions。模型从实时 Copilot 目录自动检测。

`copilot-acp` — Copilot ACP Agent 后端。将本地 Copilot CLI 作为子进程启动：

```bash
hermes chat --provider copilot-acp --model copilot-acp
# 需要 PATH 中存在 GitHub Copilot CLI 和已有的 `copilot login` 会话
```

永久配置：

```yaml
model:
  provider: "copilot"
  default: "gpt-5.4"
```

| 环境变量 | 说明 |
| --- | --- |
| `COPILOT_GITHUB_TOKEN` | 用于 Copilot API 的 GitHub 令牌（最高优先级） |
| `HERMES_COPILOT_ACP_COMMAND` | 覆盖 Copilot CLI 二进制路径（默认：`copilot`） |
| `HERMES_COPILOT_ACP_ARGS` | 覆盖 ACP 参数（默认：`--acp --stdio`） |

### 一等 API 密钥提供商

这些提供商具有内置支持，带有专用提供商 ID。设置 API 密钥并使用 `--provider` 选择：

```bash
# Fireworks AI
hermes chat --provider fireworks --model accounts/fireworks/models/kimi-k2p6
# 需要：~/.hermes/.env 中的 FIREWORKS_API_KEY

# NovitaAI Model API
hermes chat --provider novita --model moonshotai/kimi-k2.5
# 需要：~/.hermes/.env 中的 NOVITA_API_KEY

# z.ai / ZhipuAI GLM
hermes chat --provider zai --model glm-5
# 需要：~/.hermes/.env 中的 GLM_API_KEY

# Kimi / Moonshot AI（国际：api.moonshot.ai）
hermes chat --provider kimi-coding --model kimi-for-coding
# 需要：~/.hermes/.env 中的 KIMI_API_KEY

# Kimi / Moonshot AI（中国：api.moonshot.cn）
hermes chat --provider kimi-coding-cn --model kimi-k2.5
# 需要：~/.hermes/.env 中的 KIMI_CN_API_KEY

# MiniMax（全球端点）
hermes chat --provider minimax --model MiniMax-M2.7
# 需要：~/.hermes/.env 中的 MINIMAX_API_KEY

# MiniMax（中国端点）
hermes chat --provider minimax-cn --model MiniMax-M2.7
# 需要：~/.hermes/.env 中的 MINIMAX_CN_API_KEY

# Qwen Cloud / DashScope（Qwen 模型）
hermes chat --provider alibaba --model qwen3.5-plus
# 需要：~/.hermes/.env 中的 DASHSCOPE_API_KEY

# 小米 MiMo
hermes chat --provider xiaomi --model mimo-v2-pro
# 需要：~/.hermes/.env 中的 XIAOMI_API_KEY

# 腾讯 TokenHub（Hy3 Preview）
hermes chat --provider tencent-tokenhub --model hy3-preview
# 需要：~/.hermes/.env 中的 TOKENHUB_API_KEY

# Arcee AI（Trinity 模型）
hermes chat --provider arcee --model trinity-large-thinking
# 需要：~/.hermes/.env 中的 ARCEEAI_API_KEY

# GMI Cloud
# 使用 GMI 的 /v1/models 端点返回的确切模型 ID。
hermes chat --provider gmi --model zai-org/GLM-5.1-FP8
# 需要：~/.hermes/.env 中的 GMI_API_KEY
```

Fireworks 使用其原生斜杠格式的目录 ID，例如 `accounts/fireworks/models/kimi-k2p6`。运行 `hermes model`，选择 Fireworks AI，从实时目录中选择或输入其他 Fireworks 模型 ID。默认端点为 `https://api.fireworks.ai/inference/v1`；通过 `config.yaml` 中的 `model.base_url` 配置不同端点，而非 `.env`。

或在 `config.yaml` 中永久设置提供商：

```yaml
model:
  provider: "gmi"
  default: "zai-org/GLM-5.1-FP8"
```

基础 URL 可以通过 `NOVITA_BASE_URL`、`GLM_BASE_URL`、`KIMI_BASE_URL`、`MINIMAX_BASE_URL`、`MINIMAX_CN_BASE_URL`、`DASHSCOPE_BASE_URL`、`XIAOMI_BASE_URL`、`GMI_BASE_URL` 或 `TOKENHUB_BASE_URL` 环境变量覆盖。

Z.AI 端点自动检测

使用 Z.AI / GLM 提供商时，Hermes 会自动探测多个端点（全球、中国、编码变体），找到接受你 API 密钥的那个。你无需手动设置 `GLM_BASE_URL`——工作端点会被自动检测并缓存。

### xAI (Grok) — Responses API + 提示缓存

xAI 通过 Responses API（`codex_responses` 传输）进行连接，自动支持 Grok 4 模型的推理——无需 `reasoning_effort` 参数，服务器默认进行推理。在 `~/.hermes/.env` 中设置 `XAI_API_KEY`，然后在 `hermes model` 中选择 xAI，或通过快捷方式 `/model grok-4-fast-reasoning` 使用。

SuperGrok 和 X Premium+ 订阅用户可以使用浏览器 OAuth 登录，无需 API 密钥——在 `hermes model` 中选择 xAI Grok OAuth (SuperGrok / Premium+)，或运行 `hermes auth add xai-oauth`。相同的 OAuth Bearer 令牌会自动被直接通往 xAI 的工具（TTS、图像生成、视频生成、转录）重用。完整流程请参见 xAI Grok OAuth 指南——如果 Hermes 在远程主机上运行，还需参见通过 SSH / 远程主机的 OAuth 了解所需的 `ssh -L` 隧道。

使用 xAI 作为提供商时（任何包含 `x.ai` 的基础 URL），Hermes 会自动启用提示缓存，在每个 API 请求中发送 `x-grok-conv-id` 头部。这会将请求路由到同一会话中的同一台服务器，使 xAI 的基础设施能够重用缓存的系统提示和对话历史。

无需配置——当检测到 xAI 端点且有可用会话 ID 时，缓存会自动激活。这可以减少多轮对话的延迟和成本。

xAI 还提供了专用的 TTS 端点（`/v1/tts`）。在 `hermes tools` → Voice & TTS 中选择 xAI TTS，或参见 Voice & TTS 页面了解配置。

已退役的 xAI 模型迁移（2026 年 5 月 15 日）：xAI 将于 2026 年 5 月 15 日退役 `grok-4*`、`grok-3`、`grok-code-fast-1` 和 `grok-imagine-image-pro`。`hermes doctor` 和 `hermes chat` 启动时都会检测任何仍指向已退役引用的配置，并打印推荐的替代方案。使用 `hermes migrate xai` 进行一次性配置重写——默认仅预览，添加 `--apply` 写入更改（会自动创建带时间戳的 `config.yaml.bak-pre-migrate-xai-*` 备份）。

```bash
hermes migrate xai          # 预览替换
hermes migrate xai --apply  # 原地重写 ~/.hermes/config.yaml
```

xAI 网页搜索后端。当 Web Search 工具集启用时，`web.backend: xai` 通过 xAI 托管的搜索端点路由搜索请求，使用相同的 `XAI_API_KEY` / OAuth 凭据。如果 xAI 已配置为提供商，则无需额外设置。

### NovitaAI

NovitaAI 是面向构建者和 Agent 的 AI 原生云。其三条产品线是：Model API（200+ 模型）、Agent Sandbox（构建和运行 AI Agent）、GPU Cloud（可扩展计算），均可从同一平台获取。

```bash
# 使用任何可用模型
hermes chat --provider novita --model moonshotai/kimi-k2.5
# 需要：~/.hermes/.env 中的 NOVITA_API_KEY

# 短别名
hermes chat --provider novita-ai --model deepseek/deepseek-v3-0324
```

或在 `config.yaml` 中永久设置：

```yaml
model:
  provider: "novita"
  default: "moonshotai/kimi-k2.5"
  base_url: "https://api.novita.ai/openai/v1"
```

在 novita.ai/settings/key-management 获取你的 API 密钥。基础 URL 可以通过 `NOVITA_BASE_URL` 覆盖。

### Ollama Cloud — 托管 Ollama 模型，OAuth + API 密钥

Ollama Cloud 托管与本地 Ollama 相同的开放权重目录，但无需 GPU。在 `hermes model` 中将其选择为 Ollama Cloud，粘贴来自 ollama.com/settings/keys 的 API 密钥，Hermes 会自动发现可用模型。

```bash
hermes model
# → 选择 "Ollama Cloud"
# → 粘贴你的 OLLAMA_API_KEY
# → 从发现的模型中选择（gpt-oss:120b, glm-4.6:cloud, qwen3-coder:480b-cloud 等）
```

或直接使用 `config.yaml`：

```yaml
model:
  provider: "ollama-cloud"
  default: "gpt-oss:120b"
```

模型目录从 `ollama.com/v1/models` 动态获取并缓存一小时。`model:tag` 表示法（例如 `qwen3-coder:480b-cloud`）通过规范化保留——不要使用破折号。

Ollama Cloud 与本地 Ollama

两者都使用相同的 OpenAI 兼容 API。Cloud 是一等提供商（`--provider ollama-cloud`，`OLLAMA_API_KEY`）；本地 Ollama 通过自定义端点流程访问（基础 URL `http://localhost:11434/v1`，无需密钥）。对于无法本地运行的大模型使用云端；需要隐私或离线工作时使用本地。

### AWS Bedrock

通过 AWS Bedrock 使用 Anthropic Claude、Amazon Nova、DeepSeek v3.2、Meta Llama 4 等模型。使用 AWS SDK（`boto3`）凭据链——无需 API 密钥，只需标准 AWS 认证。

```bash
# 最简单——使用 ~/.aws/credentials 中的命名配置文件
hermes chat --provider bedrock --model us.anthropic.claude-sonnet-4-6

# 或使用显式环境变量
AWS_PROFILE=myprofile AWS_REGION=us-east-1 hermes chat --provider bedrock --model us.anthropic.claude-sonnet-4-6
```

或在 `config.yaml` 中永久设置：

```yaml
model:
  provider: "bedrock"
  default: "us.anthropic.claude-sonnet-4-6"
bedrock:
  region: "us-east-1"          # 或设置 AWS_REGION
  # profile: "myprofile"       # 或设置 AWS_PROFILE
  # discovery: true            # 从 IAM 自动发现区域
  # guardrail:                 # 可选的 Bedrock 护栏
  #   guardrail_identifier: "your-guardrail-id"
  #   guardrail_version: "DRAFT"
```

认证使用标准 boto3 链：显式 `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`、来自 `~/.aws/credentials` 的 `AWS_PROFILE`、EC2/ECS/Lambda 上的 IAM 角色、IMDS 或 SSO。如果你已通过 AWS CLI 认证，则无需环境变量。

Bedrock 底层使用 Converse API——请求被转换为 Bedrock 的模型无关格式，因此同一配置适用于 Claude、Nova、DeepSeek 和 Llama 模型。仅在调用非默认区域端点时设置 `BEDROCK_BASE_URL`。

参见 AWS Bedrock 指南，了解 IAM 设置、区域选择和跨区域推理的详细步骤。

### Google Vertex AI

通过 Vertex 的 OpenAI 兼容端点在 Google Cloud Vertex AI 上使用 Gemini 模型。认证方式为 OAuth2——从服务账号 JSON 或应用默认凭据（ADC）生成的短期访问令牌（约 1 小时）。没有静态 API 密钥；Hermes 为你生成并自动刷新令牌，包括在会话中途出现 `401` 时重新生成。

```bash
# 服务账号 JSON（推荐用于服务器/网关）
echo "VERTEX_CREDENTIALS_PATH=/path/to/service-account.json" >> ~/.hermes/.env

# 或使用应用默认凭据
gcloud auth application-default login

hermes model   # → "Google Vertex AI" → 项目 → 区域 → 模型
```

或在 `config.yaml` 中（project/region 为非机密信息，写在这里；凭据路径保留在 `.env` 中）：

```yaml
model:
  provider: "vertex"
  default: "google/gemini-3-flash-preview"   # Vertex 需要 google/ 前缀
vertex:
  project_id: "my-gcp-project"   # 留空 → 使用凭据中嵌入的项目
  region: "global"               # Gemini 3.x 预览版需要
```

`VERTEX_PROJECT_ID` / `VERTEX_REGION` 环境变量会覆盖 `config.yaml` 中的值。使用 `pip install 'hermes-agent[vertex]'` 安装（或让 Hermes 在首次使用时延迟安装 `google-auth`）。完整步骤参见 Google Vertex AI 指南；静态 API 密钥的 AI Studio 路径参见 Google Gemini 指南。

### Qwen Portal (OAuth)

阿里云的 Qwen Portal，支持基于浏览器的 OAuth 登录。在 `hermes model` 中选择 Qwen OAuth (Portal)，通过浏览器登录，Hermes 会持久化刷新令牌。

```bash
hermes model
# → 选择 "Qwen OAuth (Portal)"
# → 浏览器打开；使用你的阿里云账号登录
# → 确认 — 凭据保存到 ~/.hermes/auth.json
hermes chat   # 使用 portal.qwen.ai/v1 端点
```

或配置 `config.yaml`：

```yaml
model:
  provider: "qwen-oauth"
  default: "qwen3-coder-plus"
```

仅当 Portal 端点迁移时设置 `HERMES_QWEN_BASE_URL`（默认：`https://portal.qwen.ai/v1`）。

Qwen OAuth 与 Qwen Cloud（阿里云 DashScope）

`qwen-oauth` 使用面向消费者的 Qwen Portal，通过 OAuth 登录——适合个人用户。`alibaba` 提供商使用 Qwen Cloud（阿里云 DashScope）和 `DASHSCOPE_API_KEY`——适合编程/生产工作负载。两者都路由到 Qwen 系列模型，但位于不同的端点。

### 阿里云（Coding Plan）

如果你订阅了阿里云的 Coding Plan（与标准 DashScope API 访问分离的定价 SKU），Hermes 会将其作为独立的一等提供商暴露：`alibaba-coding-plan`。端点：`https://coding-intl.dashscope.aliyuncs.com/v1`。与常规的 `alibaba` 提供商一样兼容 OpenAI，但使用不同的基础 URL 和计费面。

```yaml
model:
  provider: alibaba_coding     # alibaba-coding-plan 的别名
  model: qwen3-coder-plus
```

或从 CLI：

```bash
hermes chat --provider alibaba_coding --model qwen3-coder-plus
```

`alibaba_coding` 使用与你的 `alibaba` 条目相同的 `DASHSCOPE_API_KEY`——无需单独密钥，只是路由目标不同。在此提供商注册之前，在 `config.yaml` 中设置 `provider: alibaba_coding` 的用户会静默回退到 OpenRouter 路由。

### MiniMax (OAuth)

通过浏览器 OAuth 登录使用 MiniMax-M2.7——无需 API 密钥。在 `hermes model` 中选择 MiniMax (OAuth)，通过浏览器登录，Hermes 会持久化访问令牌和刷新令牌。底层使用 Anthropic Messages 兼容端点（`/anthropic`）。

```bash
hermes model
# → 选择 "MiniMax (OAuth)"
# → 浏览器打开；使用你的 MiniMax 账号登录（全球或中国区域）
# → 确认 — 凭据保存到 ~/.hermes/auth.json
hermes chat   # 使用 api.minimax.io/anthropic 端点
```

或配置 `config.yaml`：

```yaml
model:
  provider: "minimax-oauth"
  default: "MiniMax-M2.7"
```

支持的模型：`MiniMax-M2.7`（主要）和 `MiniMax-M2.7-highspeed`（作为默认辅助模型）。OAuth 路径忽略 `MINIMAX_API_KEY` / `MINIMAX_BASE_URL`。

MiniMax OAuth 与 API 密钥

`minimax-oauth` 使用 MiniMax 面向消费者的 Portal，通过 OAuth 登录——无需设置计费。`minimax` 和 `minimax-cn` 提供商使用 `MINIMAX_API_KEY` / `MINIMAX_CN_API_KEY`——用于编程访问。完整步骤参见 MiniMax OAuth 指南。

### NVIDIA NIM

通过 build.nvidia.com（免费 API 密钥）或本地 NIM 端点使用 Nemotron 和其他开源模型。

```bash
# 云端 (build.nvidia.com)
hermes chat --provider nvidia --model nvidia/nemotron-3-super-120b-a12b
# 需要：~/.hermes/.env 中的 NVIDIA_API_KEY

# 本地 NIM 端点 — 覆盖基础 URL
NVIDIA_BASE_URL=http://localhost:8000/v1 hermes chat --provider nvidia --model nvidia/nemotron-3-super-120b-a12b
```

或在 `config.yaml` 中永久设置：

```yaml
model:
  provider: "nvidia"
  default: "nvidia/nemotron-3-super-120b-a12b"
```

本地 NIM

对于本地部署（DGX Spark、本地 GPU），设置 `NVIDIA_BASE_URL=http://localhost:8000/v1`。NIM 暴露与 build.nvidia.com 相同的 OpenAI 兼容聊天补全 API，因此在云端和本地之间切换只需一行环境变量更改。

Hermes 会自动在每个发往 `build.nvidia.com` 的请求上附加 NIM 计费来源头部——无需配置。这会将消耗量路由到 NVIDIA 计费仪表板中的正确来源。

### GMI Cloud

通过 GMI Cloud 使用开放和推理模型——OpenAI 兼容 API，API 密钥认证。

```bash
# GMI Cloud
hermes chat --provider gmi --model deepseek-ai/DeepSeek-V3.2
# 需要：~/.hermes/.env 中的 GMI_API_KEY
```

或在 `config.yaml` 中永久设置：

```yaml
model:
  provider: "gmi"
  default: "deepseek-ai/DeepSeek-V3.2"
```

基础 URL 可以通过 `GMI_BASE_URL` 覆盖（默认：`https://api.gmi-serving.com/v1`）。

### StepFun

通过 StepFun 使用 Step 系列模型——OpenAI 兼容 API，API 密钥认证。

```bash
# StepFun
hermes chat --provider stepfun --model step-3.5-flash
# 需要：~/.hermes/.env 中的 STEPFUN_API_KEY
```

或在 `config.yaml` 中永久设置：

```yaml
model:
  provider: "stepfun"
  default: "step-3.5-flash"
```

基础 URL 可以通过 `STEPFUN_BASE_URL` 覆盖（默认：`https://api.stepfun.com/v1`）。

### Hugging Face Inference Providers

Hugging Face Inference Providers 通过统一的 OpenAI 兼容端点（`router.huggingface.co/v1`）路由到 20 多个开放模型。请求会自动路由到最快的可用后端（Groq、Together、SambaNova 等），并自动故障转移。

```bash
# 使用任何可用模型
hermes chat --provider huggingface --model Qwen/Qwen3.5-397B-A17B
# 需要：~/.hermes/.env 中的 HF_TOKEN

# 短别名
hermes chat --provider hf --model deepseek-ai/DeepSeek-V3.2
```

或在 `config.yaml` 中永久设置：

```yaml
model:
  provider: "huggingface"
  default: "Qwen/Qwen3.5-397B-A17B"
```

在 huggingface.co/settings/tokens 获取你的令牌——确保启用"Make calls to Inference Providers"权限。包含免费套餐（每月 $0.10 积分，提供商费率不加价）。

你可以为模型名称附加路由后缀：`:fastest`（默认）、`:cheapest` 或 `:provider_name` 强制使用特定后端。

基础 URL 可以通过 `HF_BASE_URL` 覆盖。

## 自定义和自托管 LLM 提供商

Hermes Agent 可以与任何 OpenAI 兼容的 API 端点配合使用。如果服务器实现了 `/v1/chat/completions`，你就可以将 Hermes 指向它。这意味着你可以使用本地模型、GPU 推理服务器、多提供商路由器或任何第三方 API。

### 通用设置

配置自定义端点的三种方式：

交互式设置（推荐）：

```bash
hermes model
# 选择 "Custom endpoint (self-hosted / VLLM / etc.)"
# 输入：API 基础 URL、API 密钥、模型名称
```

手动配置（`config.yaml`）：

```yaml
# 在 ~/.hermes/config.yaml 中
model:
  default: your-model-name
  provider: custom
  base_url: http://localhost:8000/v1
  api_key: your-key-or-leave-empty-for-local
```

传统环境变量

`.env` 中的 `LLM_MODEL` 已移除——`config.yaml` 是模型和端点配置的唯一真实来源。`OPENAI_BASE_URL` 仍然被支持，但仅适用于 `openai-api` 提供商（它覆盖直接 API 密钥访问的 OpenAI 端点）。对于其他提供商和自定义端点，请使用 `hermes model` 或直接在 `config.yaml` 中设置 `model.base_url`。如果你的 `.env` 中有过时的条目，它们会在下次 `hermes setup` 或配置迁移时自动清除。

两种方法都会持久化到 `config.yaml`，这是模型、提供商和基础 URL 的唯一真实来源。

### 使用 /model 切换模型

hermes model 与 /model

`hermes model`（在你的终端中运行，在任何聊天会话之外）是完整的提供商设置向导。用于添加新提供商、运行 OAuth 流程、输入 API 密钥和配置自定义端点。

`/model`（在活跃的 Hermes 聊天会话中输入）只能在你已设置的提供商和模型之间切换。它不能添加新提供商、运行 OAuth 或提示输入 API 密钥。如果你只配置了一个提供商（例如 OpenRouter），`/model` 将只显示该提供商的模型。

要添加新提供商：退出会话（`Ctrl+C` 或 `/quit`），运行 `hermes model`，设置新提供商，然后启动新会话。

一旦你至少配置了一个自定义端点，你可以在会话中切换模型：

```text
/model custom:qwen-2.5          # 切换到自定义端点上的模型
/model custom                   # 从端点自动检测模型
/model openrouter:claude-sonnet-4 # 切换回云提供商
```

如果你配置了命名自定义提供商（见下文），使用三元语法：

```text
/model custom:local:qwen-2.5    # 使用 "local" 自定义提供商，模型 qwen-2.5
/model custom:work:llama3       # 使用 "work" 自定义提供商，模型 llama3
```

切换提供商时，Hermes 会将基础 URL 和提供商持久化到配置中，以便更改在重启后仍然有效。当从自定义端点切换到内置提供商时，过时的基础 URL 会自动清除。

提示

`/model custom`（裸调用，不带模型名称）会查询你端点的 `/models` API，如果只加载了一个模型则自动选择。对于运行单个模型的本地服务器非常有用。

以下所有内容遵循相同的模式——只需更改 URL、密钥和模型名称。

---

### Ollama — 本地模型，零配置

Ollama 可以用一条命令在本地运行开放权重模型。最适合：快速本地实验、隐私敏感工作、离线使用。通过 OpenAI 兼容 API 支持工具调用。

```bash
# 安装并运行模型
ollama pull qwen2.5-coder:32b
ollama serve   # 在端口 11434 启动
```

然后配置 Hermes：

```bash
hermes model
# 选择 "Custom endpoint (self-hosted / VLLM / etc.)"
# 输入 URL：http://localhost:11434/v1
# 跳过 API 密钥（Ollama 不需要）
# 输入模型名称（例如 qwen2.5-coder:32b）
```

或直接配置 `config.yaml`：

```yaml
model:
  default: qwen2.5-coder:32b
  provider: custom
  base_url: http://localhost:11434/v1
  context_length: 64000   # 参见下方警告
```

Ollama 默认为非常低的上下文长度

Ollama 默认不使用模型的完整上下文窗口。根据你的 VRAM，默认值为：

| 可用 VRAM | 默认上下文 |
| --- | --- |
| 小于 24 GB | 4,096 tokens |
| 24–48 GB | 32,768 tokens |
| 48+ GB | 256,000 tokens |

Hermes Agent 需要至少 64,000 tokens 的上下文才能支持带工具的 Agent 使用。较小的窗口会在启动时被拒绝，因为系统提示、工具架构和工作会话状态需要足够的空间来保证可靠的多步骤工作流。

如何增加（选择一种）：

```bash
# 选项 1：通过环境变量全局设置（推荐）
OLLAMA_CONTEXT_LENGTH=64000 ollama serve

# 选项 2：对于 systemd 管理的 Ollama
sudo systemctl edit ollama.service
# 添加：Environment="OLLAMA_CONTEXT_LENGTH=64000"
# 然后：sudo systemctl daemon-reload && sudo systemctl restart ollama

# 选项 3：烘焙到自定义模型中（持久化，按模型）
echo -e "FROM qwen2.5-coder:32b\nPARAMETER num_ctx 64000" > Modelfile
ollama create qwen2.5-coder-64k -f Modelfile
```

你不能通过 OpenAI 兼容 API（`/v1/chat/completions`）设置上下文长度。它必须在服务器端或通过 Modelfile 配置。这是将 Ollama 与 Hermes 等工具集成时最容易混淆的问题来源。

验证你的上下文是否正确设置：

```bash
ollama ps
# 查看 CONTEXT 列——它应显示你配置的值
```

提示

使用 `ollama list` 列出可用模型。使用 `ollama pull <模型名>` 从 Ollama 库拉取任何模型。Ollama 会自动处理 GPU 卸载——大多数设置无需配置。

---

### vLLM — 高性能 GPU 推理

vLLM 是生产级 LLM 服务的标准。最适合：GPU 硬件上的最大吞吐量、服务大型模型、连续批处理。

```bash
pip install vllm
vllm serve meta-llama/Llama-3.1-70B-Instruct \
  --port 8000 \
  --max-model-len 65536 \
  --tensor-parallel-size 2 \
  --enable-auto-tool-choice \
  --tool-call-parser hermes
```

然后配置 Hermes：

```bash
hermes model
# 选择 "Custom endpoint (self-hosted / VLLM / etc.)"
# 输入 URL：http://localhost:8000/v1
# 跳过 API 密钥（或如果你用 --api-key 配置了 vLLM 则输入一个）
# 输入模型名称：meta-llama/Llama-3.1-70B-Instruct
```

上下文长度：vLLM 默认读取模型的 `max_position_embeddings`。如果超过 GPU 内存，它会报错并让你设置更低的 `--max-model-len`。你也可以使用 `--max-model-len auto` 自动找到适合的最大值。设置 `--gpu-memory-utilization 0.95`（默认 0.9）可以在 VRAM 中挤出更多上下文。

工具调用需要显式标志：

| 标志 | 用途 |
| --- | --- |
| `--enable-auto-tool-choice` | 需要 `tool_choice: "auto"`（Hermes 默认值） |
| `--tool-call-parser <解析器>` | 模型工具调用格式的解析器 |

支持的解析器：`hermes`（Qwen 2.5、Hermes 2/3）、`llama3_json`（Llama 3.x）、`mistral`、`deepseek_v3`、`deepseek_v31`、`xlam`、`pythonic`。没有这些标志，工具调用将无法工作——模型会将工具调用以文本形式输出。

Qwen 推理解析器：当 OpenAI 兼容服务器返回结构化推理元数据（如 `reasoning`、`reasoning_content` 和流式推理 delta）时，Hermes 会保留它们。这些元数据被视为推理/思考轨迹数据，而不是助手可见答案的替代品。对于由 vLLM 服务的 Qwen 推理模型，请确保最终用户可见的响应仍出现在 `content` 中。如果 `--reasoning-parser qwen3` 在你的部署中导致 `content` 为空，请禁用该解析器或通过 `extra_body` 传递服务器支持的请求选项，例如 `chat_template_kwargs.enable_thinking: false`。

提示

vLLM 支持人类可读的大小：`--max-model-len 64k`（小写 k = 1000，大写 K = 1024）。

---

### SGLang — 使用 RadixAttention 的快速服务

SGLang 是 vLLM 的替代方案，使用 RadixAttention 实现 KV 缓存重用。最适合：多轮对话（前缀缓存）、约束解码、结构化输出。

```bash
pip install "sglang[all]"
python -m sglang.launch_server \
  --model meta-llama/Llama-3.1-70B-Instruct \
  --port 30000 \
  --context-length 65536 \
  --tp 2 \
  --tool-call-parser qwen
```

然后配置 Hermes：

```bash
hermes model
# 选择 "Custom endpoint (self-hosted / VLLM / etc.)"
# 输入 URL：http://localhost:30000/v1
# 输入模型名称：meta-llama/Llama-3.1-70B-Instruct
```

上下文长度：SGLang 默认从模型配置中读取。使用 `--context-length` 覆盖。如果需要超过模型声明的最大值，设置 `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1`。

工具调用：使用 `--tool-call-parser` 加上适合你模型系列的解析器：`qwen`（Qwen 2.5）、`llama3`、`llama4`、`deepseekv3`、`mistral`、`glm`。没有这个标志，工具调用会以纯文本形式返回。

SGLang 默认为 128 个最大输出令牌

如果响应看起来被截断，请为请求添加 `max_tokens` 或在服务器上设置 `--default-max-tokens`。SGLang 在请求中未指定时，默认每个响应只有 128 个令牌。

---

### llama.cpp / llama-server — CPU 和 Metal 推理

llama.cpp 在 CPU、Apple Silicon (Metal) 和消费级 GPU 上运行量化模型。最适合：在没有数据中心 GPU 的情况下运行模型、Mac 用户、边缘部署。

```bash
# 构建并启动 llama-server
cmake -B build && cmake --build build --config Release
./build/bin/llama-server \
  --jinja -fa \
  -c 64000 \
  -ngl 99 \
  -m models/qwen2.5-coder-32b-instruct-Q4_K_M.gguf \
  --port 8080 --host 0.0.0.0
```

上下文长度（`-c`）：最近的构建默认使用 `0`，即从 GGUF 元数据中读取模型的训练上下文。对于训练上下文为 128k+ 的模型，这可能会因尝试分配完整的 KV 缓存而导致内存溢出。显式设置 `-c` 至少为 64,000 个令牌以供 Hermes 使用。如果使用并行槽（`-np`），总上下文会在槽之间分配——使用 `-c 64000 -np 4` 时，每个槽只有 16k，低于 Hermes 每个活跃会话的最低要求。

然后将 Hermes 指向它：

```bash
hermes model
# 选择 "Custom endpoint (self-hosted / VLLM / etc.)"
# 输入 URL：http://localhost:8080/v1
# 跳过 API 密钥（本地服务器不需要）
# 输入模型名称 — 或留空以便在只加载了一个模型时自动检测
```

这会将端点保存到 `config.yaml`，使其在会话之间持久化。

`--jinja` 是工具调用所必需的

没有 `--jinja`，llama-server 会完全忽略 `tools` 参数。模型会尝试通过在其响应文本中编写 JSON 来调用工具，但 Hermes 不会将其识别为工具调用——你会看到像 `{"name": "web_search", ...}` 这样的原始 JSON 作为消息打印出来，而不是实际搜索。

原生工具调用支持（最佳性能）：Llama 3.x、Qwen 2.5（包括 Coder）、Hermes 2/3、Mistral、DeepSeek、Functionary。所有其他模型使用通用处理器，可以工作但效率可能较低。参见 llama.cpp 函数调用文档获取完整列表。

你可以通过检查 `http://localhost:8080/props` 来验证工具支持是否激活——`chat_template` 字段应存在。

提示

从 Hugging Face 下载 GGUF 模型。Q4_K_M 量化在质量和内存使用之间提供了最佳平衡。

---

### LM Studio — 带本地模型的桌面应用

LM Studio 是一款用于运行本地模型的桌面应用，带有 GUI。最适合：喜欢可视化界面的用户、快速模型测试、macOS/Windows/Linux 上的开发者。

从 LM Studio 应用启动服务器（开发者选项卡 → Start Server），或使用 CLI：

```bash
lms server start                        # 在端口 1234 启动
lms load qwen2.5-coder --context-length 64000
```

然后配置 Hermes：

```bash
hermes model
# 选择 "LM Studio"
# 按 Enter 使用 http://localhost:1234/v1
# 从发现的模型中选择一个
# 如果 LM Studio 服务器启用了认证，则按提示输入 LM_API_KEY
```

默认情况下，Hermes 会在首次请求前显式要求 LM Studio 以 64K 上下文长度加载所选模型。

在 LM Studio 中更改上下文长度：

1. 点击模型选择器旁边的齿轮图标
2. 将"Context Length"设置为至少 64000 以获得流畅体验
3. 重新加载模型以使更改生效
4. 如果你的机器无法容纳 64000，考虑使用支持更大上下文长度的较小模型

或者，使用 CLI：`lms load model-name --context-length 64000`

你可以使用 CLI 估算模型是否适合：`lms load model-name --context-length 64000 --estimate-only`

要设置持久的按模型默认值：My Models 选项卡 → 模型上的齿轮图标 → 设置上下文大小。

如果你使用 LM Studio 的即时加载 / Auto-Evict 功能，并希望 LM Studio 从正常聊天请求中管理模型加载和驱逐，请跳过 Hermes 的显式预加载步骤：

```bash
hermes config set model.lmstudio_load_mode jit
```

恢复为默认的显式预加载行为：

```bash
hermes config set model.lmstudio_load_mode explicit
```

工具调用：自 LM Studio 0.3.6 起支持。具有原生工具调用训练的模型（Qwen 2.5、Llama 3.x、Mistral、Hermes）会被自动检测并显示工具徽章。其他模型使用通用回退，可能不太可靠。

---

### WSL2 网络（Windows 用户）

由于 Hermes Agent 需要 Unix 环境，Windows 用户需在 WSL2 内部运行。如果你的模型服务器（Ollama、LM Studio 等）在 Windows 主机上运行，你需要桥接网络——WSL2 使用具有自己子网的虚拟网络适配器，因此 WSL2 内部的 `localhost` 指向的是 Linux 虚拟机，而不是 Windows 主机。

两者都在 WSL2 中？没问题。

如果你的模型服务器也在 WSL2 内部运行（vLLM、SGLang 和 llama-server 常见这种情况），`localhost` 可以正常工作——它们共享相同的网络命名空间。跳过此部分。

#### 选项 1：镜像网络模式（推荐）

在 Windows 11 22H2+ 上可用，镜像模式使 `localhost` 在 Windows 和 WSL2 之间双向工作——最简单的修复方法。

创建或编辑 `%USERPROFILE%\.wslconfig`（例如 `C:\Users\你的用户名\.wslconfig`）：

```ini
[wsl2]
networkingMode=mirrored
```

从 PowerShell 重启 WSL：

```powershell
wsl --shutdown
```

重新打开 WSL2 终端。`localhost` 现在可以访问 Windows 服务：

```bash
curl http://localhost:11434/v1/models   # Windows 上的 Ollama — 可以工作
```

Hyper-V 防火墙

在某些 Windows 11 版本上，Hyper-V 防火墙会默认阻止镜像连接。如果启用镜像模式后 `localhost` 仍无法工作，请在管理员 PowerShell 中运行：

```powershell
Set-NetFirewallHyperVVMSetting -Name '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' -DefaultInboundAction Allow
```

#### 选项 2：使用 Windows 主机 IP（Windows 10 / 较旧版本）

如果无法使用镜像模式，请从 WSL2 内部找到 Windows 主机 IP 并代替 `localhost` 使用：

```bash
# 获取 Windows 主机 IP（WSL2 虚拟网络的默认网关）
ip route show | grep -i default | awk '{ print $3 }'
# 示例输出：172.29.192.1
```

在 Hermes 配置中使用该 IP：

```yaml
model:
  default: qwen2.5-coder:32b
  provider: custom
  base_url: http://172.29.192.1:11434/v1   # Windows 主机 IP，不是 localhost
```

动态辅助

主机 IP 在 WSL2 重启时可能发生变化。你可以在 shell 中动态获取它：

```bash
export WSL_HOST=$(ip route show | grep -i default | awk '{ print $3 }')
echo "Windows host at: $WSL_HOST"
curl http://$WSL_HOST:11434/v1/models   # 测试 Ollama
```

或使用你机器的 mDNS 名称（需要在 WSL2 中安装 `libnss-mdns`）：

```bash
sudo apt install libnss-mdns
curl http://$(hostname).local:11434/v1/models
```

#### 服务器绑定地址（NAT 模式必需）

如果你使用选项 2（使用主机 IP 的 NAT 模式），Windows 上的模型服务器必须接受来自 `127.0.0.1` 之外的连接。默认情况下，大多数服务器只监听 localhost——NAT 模式下的 WSL2 连接来自不同的虚拟子网，会被拒绝。在镜像模式下，`localhost` 直接映射，因此默认的 `127.0.0.1` 绑定可以正常工作。

| 服务器 | 默认绑定 | 如何修复 |
| --- | --- | --- |
| Ollama | `127.0.0.1` | 在启动 Ollama 前设置 `OLLAMA_HOST=0.0.0.0` 环境变量（Windows 系统设置 → 环境变量，或编辑 Ollama 服务） |
| LM Studio | `127.0.0.1` | 在 Developer 选项卡 → Server 设置中启用 "Serve on Network" |
| llama-server | `127.0.0.1` | 在启动命令中添加 `--host 0.0.0.0` |
| vLLM | `0.0.0.0` | 默认已绑定到所有接口 |
| SGLang | `127.0.0.1` | 在启动命令中添加 `--host 0.0.0.0` |

Windows 上的 Ollama（详细）：Ollama 作为 Windows 服务运行。要设置 `OLLAMA_HOST`：

1. 打开系统属性 → 环境变量
2. 添加新的系统变量：`OLLAMA_HOST` = `0.0.0.0`
3. 重启 Ollama 服务（或重启）

#### Windows 防火墙

Windows 防火墙将 WSL2 视为一个独立的网络（在 NAT 和镜像模式下都是如此）。如果在以上步骤后连接仍然失败，请为你的模型服务器端口添加防火墙规则：

```powershell
# 在管理员 PowerShell 中运行 — 将 PORT 替换为你的服务器端口
New-NetFirewallRule -DisplayName "Allow WSL2 to Model Server" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 11434
```

常见端口：Ollama `11434`，vLLM `8000`，SGLang `30000`，llama-server `8080`，LM Studio `1234`。

#### 快速验证

从 WSL2 内部测试能否连接到你的模型服务器：

```bash
# 将 URL 替换为你的服务器地址和端口
curl http://localhost:11434/v1/models          # 镜像模式
curl http://172.29.192.1:11434/v1/models       # NAT 模式（使用你的实际主机 IP）
```

如果你收到列出模型的 JSON 响应，就说明一切正常。在 Hermes 配置中使用相同的 URL 作为 `base_url`。

---

### 本地模型故障排除

这些问题在使用 Hermes 时会影响所有本地推理服务器。

#### 从 WSL2 到 Windows 托管的模型服务器出现"Connection refused"

如果你在 WSL2 内部运行 Hermes，而模型服务器在 Windows 主机上，在 WSL2 的默认 NAT 网络模式下，`http://localhost:<端口>` 无法工作。请参见上方的 WSL2 网络部分获取修复方法。

#### 工具调用以文本形式出现而非实际执行

模型输出类似 `{"name": "web_search", "arguments": {...}}` 作为消息，而不是实际调用工具。

原因：你的服务器未启用工具调用，或模型不支持通过服务器的工具调用实现。

| 服务器 | 修复方法 |
| --- | --- |
| llama.cpp | 在启动命令中添加 `--jinja` |
| vLLM | 添加 `--enable-auto-tool-choice --tool-call-parser hermes` |
| SGLang | 添加 `--tool-call-parser qwen`（或适当的解析器） |
| Ollama | 工具调用默认启用——确保你的模型支持（使用 `ollama show model-name` 检查） |
| LM Studio | 更新到 0.3.6+ 并使用具有原生工具支持的模型 |

#### 模型似乎忘记上下文或给出不连贯的响应

原因：上下文窗口太小。当对话超过上下文限制时，大多数服务器会静默丢弃较早的消息。Hermes 的系统提示 + 工具架构本身可能占用 4k–8k 令牌。

诊断：

```bash
# 检查 Hermes 认为的上下文大小
# 查看启动行："Context limit: X tokens"
# 检查你服务器的实际上下文
# Ollama：ollama ps（CONTEXT 列）
# llama.cpp：curl http://localhost:8080/props | jq '.default_generation_settings.n_ctx'
# vLLM：检查启动参数中的 --max-model-len
```

修复：将上下文设置为至少 64,000 个令牌以供 Agent 使用。请参见上方每个服务器的章节获取具体标志。

#### 启动时显示"Context limit: 2048 tokens"

Hermes 会从你的服务器的 `/v1/models` 端点自动检测上下文长度。如果服务器报告的值较低（或根本不报告），Hermes 会使用模型声明的限制，这可能是错误的。

修复：在 `config.yaml` 中显式设置：

```yaml
model:
  default: your-model
  provider: custom
  base_url: http://localhost:11434/v1
  context_length: 64000
```

#### 响应在句子中间被截断

可能的原因：

1. 服务器上输出上限（`max_tokens`）过低——SGLang 默认为每个响应 128 个令牌。在服务器上设置 `--default-max-tokens`，或使用 `model.max_tokens` 配置 Hermes。注意：`max_tokens` 仅控制响应长度——与对话历史长度无关（那是 `context_length` 的作用）。
2. 上下文耗尽——模型填满了它的上下文窗口。增加 `model.context_length` 或在 Hermes 中启用上下文压缩。

---

### LiteLLM Proxy — 多提供商网关

LiteLLM 是一个 OpenAI 兼容的代理，将 100 多个 LLM 提供商统一在单个 API 之后。最适合：在提供商之间切换而无需更改配置、负载均衡、回退链、预算控制。

```bash
# 安装并启动
pip install "litellm[proxy]"
litellm --model anthropic/claude-sonnet-4 --port 4000
# 或使用配置文件配置多个模型：
litellm --config litellm_config.yaml --port 4000
```

然后使用 `hermes model` → Custom endpoint → `http://localhost:4000/v1` 配置 Hermes。

带回退的 `litellm_config.yaml` 示例：

```yaml
model_list:
  - model_name: "best"
    litellm_params:
      model: anthropic/claude-sonnet-4
      api_key: sk-ant-...
  - model_name: "best"
    litellm_params:
      model: openai/gpt-4o
      api_key: sk-...
router_settings:
  routing_strategy: "latency-based-routing"
```

---

### ClawRouter — 成本优化路由

ClawRouter by BlockRunAI 是一个本地路由代理，根据查询复杂度自动选择模型。它在 14 个维度上对请求进行分类，并路由到能够处理该任务的最便宜模型。通过 USDC 加密货币支付（无需 API 密钥）。

```bash
# 安装并启动
npx @blockrun/clawrouter    # 在端口 8402 启动
```

然后使用 `hermes model` → Custom endpoint → `http://localhost:8402/v1` → 模型名 `blockrun/auto` 配置 Hermes。

路由配置文件：

| 配置文件 | 策略 | 节省 |
| --- | --- | --- |
| `blockrun/auto` | 平衡质量/成本 | 74-100% |
| `blockrun/eco` | 尽可能最便宜 | 95-100% |
| `blockrun/premium` | 最佳质量模型 | 0% |
| `blockrun/free` | 仅免费模型 | 100% |
| `blockrun/agentic` | 针对工具使用优化 | 因情况而异 |

注意

ClawRouter 需要一个在 Base 或 Solana 上以 USDC 充值的钱包用于支付。所有请求都通过 BlockRun 的后端 API 路由。运行 `npx @blockrun/clawrouter doctor` 检查钱包状态。

---

### 其他兼容提供商

任何具有 OpenAI 兼容 API 的服务都可以使用。一些流行的选择：

| 提供商 | 基础 URL | 说明 |
| --- | --- | --- |
| Together AI | `https://api.together.xyz/v1` | 云端托管开放模型 |
| Groq | `https://api.groq.com/openai/v1` | 超快推理 |
| DeepSeek | `https://api.deepseek.com/v1` | DeepSeek 模型 |
| Fireworks AI | `https://api.fireworks.ai/inference/v1` | 快速开放模型托管 |
| GMI Cloud | `https://api.gmi-serving.com/v1` | 托管式 OpenAI 兼容推理 |
| Cerebras | `https://api.cerebras.ai/v1` | 晶圆级芯片推理 |
| Mistral AI | `https://api.mistral.ai/v1` | Mistral 模型 |
| OpenAI | `https://api.openai.com/v1` | 直接 OpenAI 访问 |
| Azure OpenAI | `https://YOUR.openai.azure.com/` | 企业级 OpenAI |
| LocalAI | `http://localhost:8080/v1` | 自托管，多模型 |
| Jan | `http://localhost:1337/v1` | 本地模型桌面应用 |

使用 `hermes model` → Custom endpoint，或在 `config.yaml` 中配置其中任何一个：

```yaml
model:
  default: meta-llama/Llama-3.1-70B-Instruct-Turbo
  provider: custom
  base_url: https://api.together.xyz/v1
  api_key: your-together-key
```

---

### 上下文长度检测

两个容易混淆的设置

`context_length` 是总上下文窗口——输入和输出令牌的合计预算（例如 Claude Opus 4.6 为 200,000）。Hermes 使用此值来决定何时压缩历史记录以及验证 API 请求。

`model.max_tokens` 是输出上限——模型在单个响应中可生成的最大令牌数。它与你的对话历史可以有多长无关。业界标准名称 `max_tokens` 是常见的混淆来源；Anthropic 的原生 API 后来将其更名为 `max_output_tokens` 以提高清晰度。

当自动检测得到的窗口大小错误时，设置 `context_length`。仅当需要限制单个响应的长度时，设置 `model.max_tokens`。

Hermes 使用多源解析链来检测你的模型和提供商的正确上下文窗口：

1. 配置覆盖——`config.yaml` 中的 `model.context_length`（最高优先级）
2. 自定义提供商按模型——`custom_providers[].models[].context_length`
3. 持久缓存——先前发现的值（重启后仍有效）
4. 端点 `/models`——查询你服务器的 API（本地/自定义端点）
5. Anthropic `/v1/models`——查询 Anthropic 的 API 获取 `max_input_tokens`（仅限 API 密钥用户）
6. OpenRouter API——来自 OpenRouter 的实时模型元数据
7. Nous Portal——将 Nous 模型 ID 后缀与 OpenRouter 元数据匹配
8. models.dev——社区维护的注册表，包含 100 多个提供商 3800+ 模型的提供商特定上下文长度
9. 回退默认值——广泛的模型系列模式（128K 默认）

对于大多数设置，这可以开箱即用。该系统具有提供商感知能力——同一模型根据服务方不同可能有不同的上下文限制（例如，`claude-opus-4.6` 在 Anthropic 直接使用时为 1M，但在 GitHub Copilot 上为 128K）。

要显式设置上下文长度，请将 `context_length` 添加到模型配置中：

```yaml
model:
  default: "qwen3.5:9b"
  base_url: "http://localhost:8080/v1"
  context_length: 131072  # tokens
```

对于自定义端点，你也可以按模型设置上下文长度：

```yaml
custom_providers:
  - name: "My Local LLM"
    base_url: "http://localhost:11434/v1"
    models:
      qwen3.5:27b:
        context_length: 64000
      deepseek-r1:70b:
        context_length: 65536
```

`hermes model` 在配置自定义端点时会提示输入上下文长度。留空则使用自动检测。

何时手动设置

- 你使用自定义 `num_ctx` 且低于模型最大值的 Ollama
- 你想要将上下文限制在模型最大值以下（例如，128k 模型上使用 8k 以节省 VRAM）
- 你在不暴露 `/v1/models` 的代理后面运行

---

### 命名自定义提供商

如果你使用多个自定义端点（例如，本地开发服务器和远程 GPU 服务器），你可以在 `config.yaml` 中将它们定义为命名自定义提供商：

```yaml
custom_providers:
  - name: local
    base_url: http://localhost:8080/v1
    # api_key 省略 — Hermes 对于不需要密钥的本地服务器使用 "no-key-required"
  - name: work
    base_url: https://gpu-server.internal.corp/v1
    key_env: CORP_API_KEY
    api_mode: chat_completions   # 由 `hermes model` → Custom Endpoint 向导显式设置；自动检测仍作为回退发生
  - name: anthropic-proxy
    base_url: https://proxy.example.com/anthropic
    key_env: ANTHROPIC_PROXY_KEY
    api_mode: anthropic_messages  # 用于 Anthropic 兼容代理
```

某些 OpenAI 兼容端点需要提供商特定的请求体字段。将 `extra_body` 映射添加到匹配的自定义提供商，Hermes 会将其合并到该端点的每个聊天补全请求中：

```yaml
custom_providers:
  - name: gemma-local
    base_url: http://localhost:8080/v1
    model: google/gemma-4-31b-it
    extra_body:
      enable_thinking: true
      reasoning_effort: high
```

使用你的服务器文档中记录的格式。例如，vLLM Gemma 部署和一些 NVIDIA NIM 端点期望 `enable_thinking` 放在 `chat_template_kwargs` 下，而不是作为顶层的 `extra_body` 字段：

```yaml
extra_body:
  chat_template_kwargs:
    enable_thinking: true
```

对于由 vLLM 服务的 Qwen 推理模型，当推理解析器将所有生成的文本分离到推理字段并导致助手 `content` 为空时，可以使用相同的格式来禁用思考：

```yaml
extra_body:
  chat_template_kwargs:
    enable_thinking: false
```

`hermes model` → Custom Endpoint 向导现在会显式提示输入 `api_mode`，并将你的答案持久化到 `config.yaml`。基于 URL 的自动检测（例如 `/anthropic` 路径 → `anthropic_messages`）仍在字段留空时作为回退发生。

自定义提供商模型的原生视觉支持。如果你的自定义端点服务一个具有视觉能力的模型且该模型不在 models.dev 中，设置 `model.supports_vision: true`，这样 Hermes 会将附带的图像原生路由（作为 `image_url` 部分），而不是通过 `vision_analyze` 进行预处理。单一开关——无需同时设置 `agent.image_input_mode: native`。

```yaml
model:
  provider: custom
  base_url: http://localhost:8080/v1
  default: qwen3.6-35b-a3b
  supports_vision: true   # 原生发送图像；否则 vision_analyze 会预先描述
```

相同的键也适用于按命名提供商的模型（`custom_providers[*].models[*].supports_vision`），接受标准 YAML 布尔值（`true/false/yes/no/on/off/1/0`）。

在会话中使用三元语法切换：

```text
/model custom:local:qwen-2.5       # 使用 "local" 端点，模型 qwen-2.5
/model custom:work:llama3-70b      # 使用 "work" 端点，模型 llama3-70b
/model custom:anthropic-proxy:claude-sonnet-4  # 使用代理
```

你也可以从交互式 `hermes model` 菜单中选择命名自定义提供商。

---

### 菜谱：Together AI、Groq、Perplexity

在"其他兼容提供商"中列出的云提供商都使用 OpenAI 的 REST 方言，因此它们在 `custom_providers:` 下的配置方式相同。以下是三个可直接使用的方案。每个方案放入 `~/.hermes/config.yaml`，匹配的 API 密钥放入 `~/.hermes/.env`。

#### Together AI

托管开放权重模型（Llama、MiniMax、Gemma、DeepSeek、Qwen），价格显著低于第一方 API。多模型舰队的不错默认选择。

```yaml
# ~/.hermes/config.yaml
custom_providers:
  - name: together
    base_url: https://api.together.xyz/v1
    key_env: TOGETHER_API_KEY
    # api_mode: chat_completions  # 默认值——无需设置
model:
  default: MiniMaxAI/MiniMax-M2.7   # 或任何来自 together.ai/models 的模型
  provider: custom:together
```

```bash
# ~/.hermes/.env
TOGETHER_API_KEY=your-together-key
```

在会话中切换模型：

```text
/model custom:together:meta-llama/Llama-3.3-70B-Instruct-Turbo
/model custom:together:google/gemma-4-31b-it
/model custom:together:deepseek-ai/DeepSeek-V3
```

Together 的 `/v1/models` 端点可以工作，因此 `hermes model` 可以自动发现可用模型。

#### Groq

超快推理（Llama-3.3-70B 上约每秒 500 令牌）。目录较小，但对于延迟敏感的交互使用来说很强。

```yaml
# ~/.hermes/config.yaml
custom_providers:
  - name: groq
    base_url: https://api.groq.com/openai/v1
    key_env: GROQ_API_KEY
model:
  default: llama-3.3-70b-versatile
  provider: custom:groq
```

```bash
# ~/.hermes/.env
GROQ_API_KEY=your-groq-key
```

#### Perplexity

当你需要一个能够自动进行实时网页搜索和引用的模型时非常有用。对可用的模型有严格限制——请查看 perplexity.ai/settings/api 获取当前列表。

```yaml
# ~/.hermes/config.yaml
custom_providers:
  - name: perplexity
    base_url: https://api.perplexity.ai
    key_env: PERPLEXITY_API_KEY
model:
  default: sonar
  provider: custom:perplexity
```

```bash
# ~/.hermes/.env
PERPLEXITY_API_KEY=your-perplexity-key
```

#### 在单个配置中使用多个提供商

这三个方案可以组合——全部一起使用，每轮通过 `/model custom:<名称>:<模型>` 切换：

```yaml
custom_providers:
  - name: together
    base_url: https://api.together.xyz/v1
    key_env: TOGETHER_API_KEY
  - name: groq
    base_url: https://api.groq.com/openai/v1
    key_env: GROQ_API_KEY
  - name: perplexity
    base_url: https://api.perplexity.ai
    key_env: PERPLEXITY_API_KEY
model:
  default: MiniMaxAI/MiniMax-M2.7
  provider: custom:together      # 启动时使用 Together；之后可自由切换
```

故障排除

- `hermes doctor` 在 CLI 验证器修复（#15083）后，不应再对这些名称打印任何 "Unknown provider" 警告。
- 如果某个提供商的 `/v1/models` 端点不可达（Perplexity 是常见情况），`hermes model` 会以警告方式持久化模型，而非硬性拒绝——参见 #15136。
- 要完全跳过 `custom_providers:` 并使用裸 `provider: custom` 配合 `CUSTOM_BASE_URL` 环境变量，参见 #15103。

---

### 选择合适的设置

| 使用场景 | 推荐方案 |
| --- | --- |
| 只想开箱即用 | OpenRouter（默认）或 Nous Portal |
| 本地模型，简单配置 | Ollama |
| 生产环境 GPU 服务 | vLLM 或 SGLang |
| Mac / 无 GPU | Ollama 或 llama.cpp |
| 多提供商路由 | LiteLLM Proxy 或 OpenRouter |
| 成本优化 | ClawRouter 或 OpenRouter（使用 `sort: "price"`） |
| 最大隐私 | Ollama、vLLM 或 llama.cpp（完全本地） |
| 企业 / Azure | 使用自定义端点的 Azure OpenAI |
| 中文 AI 模型 | z.ai (GLM)、Kimi/Moonshot（`kimi-coding` 或 `kimi-coding-cn`）、MiniMax、小米 MiMo 或腾讯 TokenHub（一等提供商） |

提示

你可以随时使用 `hermes model` 切换提供商——无需重启。无论使用哪个提供商，你的对话历史、记忆和技能都会保留。

## 可选的 API 密钥

| 功能 | 提供商 | 环境变量 |
| --- | --- | --- |
| 网页抓取 | Firecrawl | `FIRECRAWL_API_KEY`，`FIRECRAWL_API_URL` |
| 浏览器自动化 | Browserbase | `BROWSERBASE_API_KEY`，`BROWSERBASE_PROJECT_ID` |
| 图像生成 | FAL | `FAL_KEY` |
| 高级 TTS 语音 | ElevenLabs | `ELEVENLABS_API_KEY` |
| OpenAI TTS + 语音转录 | OpenAI | `VOICE_TOOLS_OPENAI_KEY` |
| Mistral TTS + 语音转录 | Mistral | `MISTRAL_API_KEY` |
| 跨会话用户建模 | Honcho | `HONCHO_API_KEY` |
| 语义长期记忆 | Supermemory | `SUPERMEMORY_API_KEY` |

### 自托管 Firecrawl

默认情况下，Hermes 使用 Firecrawl 云 API 进行网页搜索和抓取。如果你更希望在本地运行 Firecrawl，你可以将 Hermes 指向自托管实例。参见 Firecrawl 的 SELF_HOST.md 获取完整的设置说明。

你能获得的好处：无需 API 密钥、无速率限制、无按页成本、完全数据主权。

你需要牺牲的：云版本使用 Firecrawl 专有的"Fire-engine"进行高级反爬绕过（Cloudflare、CAPTCHA、IP 轮换）。自托管版本使用基本 fetch + Playwright，因此某些受保护的网站可能失败。搜索使用 DuckDuckGo 替代 Google。

设置：

克隆并启动 Firecrawl Docker 栈（5 个容器：API、Playwright、Redis、RabbitMQ、PostgreSQL——需要约 4-8 GB RAM）：

```bash
git clone https://github.com/firecrawl/firecrawl
cd firecrawl
# 在 .env 中设置：USE_DB_AUTHENTICATION=false, HOST=0.0.0.0, PORT=3002
docker compose up -d
```

将 Hermes 指向你的实例（无需 API 密钥）：

```bash
hermes config set FIRECRAWL_API_URL http://localhost:3002
```

如果你的自托管实例启用了认证，你也可以同时设置 `FIRECRAWL_API_KEY` 和 `FIRECRAWL_API_URL`。

## OpenRouter 提供商路由

使用 OpenRouter 时，你可以控制请求如何在提供商之间路由。在 `~/.hermes/config.yaml` 中添加 `provider_routing` 部分：

```yaml
provider_routing:
  sort: "throughput"          # "price"（默认），"throughput"，或 "latency"
  # only: ["anthropic"]      # 仅使用这些提供商
  # ignore: ["deepinfra"]    # 跳过这些提供商
  # order: ["anthropic", "google"]  # 按此顺序尝试提供商
  # require_parameters: true  # 仅使用支持所有请求参数的提供商
  # data_collection: "deny"   # 排除可能存储/训练数据的提供商
```

快捷方式：在任何模型名称后附加 `:nitro` 按吞吐量排序（例如 `anthropic/claude-sonnet-4:nitro`），或使用 `:floor` 按价格排序。

## OpenRouter Pareto Code Router

OpenRouter 在 `openrouter/pareto-code` 上提供了一个实验性的编码模型路由器，它会自动将请求路由到满足编码质量门槛的最便宜模型（由 Artificial Analysis 排名）。选择此模型并在 `~/.hermes/config.yaml` 中调整 `min_coding_score` 旋钮：

```yaml
model:
  provider: openrouter
  model: openrouter/pareto-code
openrouter:
  min_coding_score: 0.65   # 0.0–1.0；越高 = 越强（越贵）的编码模型。默认 0.65。
```

注意：

- `min_coding_score` 仅在 `model.model` 为 `openrouter/pareto-code` 时发送。在其他任何模型上该值都是空操作。
- 设为空字符串（或删除该行）让 OpenRouter 选择最强的可用编码模型——这是省略 plugins 块时的文档化行为。
- 选择在给定分数上是确定性的，但实际选择的模型可能随着帕累托前沿移动而变化（新模型、基准测试更新）。
- 参见 OpenRouter 的 Pareto Router 文档获取完整的路由器行为。
- 要为特定辅助任务（压缩、视觉等）而不是主 Agent 使用 Pareto Code 路由器，在该任务下设置 `extra_body.plugins`——参见辅助模型 → OpenRouter 路由与用于辅助任务的 Pareto Code。

## 备用提供商

配置一个备用提供商链，当主模型失败时（速率限制、服务器错误、认证失败），Hermes 会按顺序尝试。规范格式是顶级的 `fallback_providers:` 列表：

```yaml
fallback_providers:
  - provider: openrouter
    model: anthropic/claude-sonnet-4
  - provider: anthropic
    model: claude-sonnet-4
    # base_url: http://localhost:8000/v1
    # 可选，用于自定义端点
    # api_mode: chat_completions           # 可选覆盖
```

为了向后兼容，仍然接受旧式的单对 `fallback_model:` 字典：

```yaml
fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
```

当激活时，备用会在不丢失对话的情况下在会话中切换模型和提供商。链按条目逐一尝试；激活在每个会话中只触发一次。

支持的提供商：`openrouter`、`nous`、`novita`、`openai-codex`、`copilot`、`copilot-acp`、`anthropic`、`gemini`、`qwen-oauth`、`huggingface`、`zai`、`kimi-coding`、`kimi-coding-cn`、`minimax`、`minimax-cn`、`minimax-oauth`、`deepseek`、`nvidia`、`xai`、`xai-oauth`、`ollama-cloud`、`bedrock`、`azure-foundry`、`opencode-zen`、`opencode-go`、`kilocode`、`xiaomi`、`arcee`、`gmi`、`stepfun`、`lmstudio`、`alibaba`、`alibaba-coding-plan`、`tencent-tokenhub`、`custom`。

提示

备用完全通过 `config.yaml` 配置——或通过 `hermes fallback` 交互式配置。关于何时触发、链如何推进，以及它与辅助任务和委托的交互，完整详情请参见备用提供商。

---

## 参见

- 配置 — 通用配置（目录结构、配置优先级、终端后端、记忆、压缩等）
- 环境变量 — 所有环境变量的完整参考
