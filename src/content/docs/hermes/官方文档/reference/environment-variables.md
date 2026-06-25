--- frontmatter ---
---
sidebar_position: 2
title: "环境变量"
description: "Hermes Agent 使用的所有环境变量的完整参考"
---

--- body ---

# 环境变量参考

Hermes 从进程环境变量中读取配置，对于用户管理的密钥，则从 `~/.hermes/.env` 读取。将 API 密钥、机器人令牌、OAuth 密钥和其他凭据保存在 `.env` 中；对于非密钥的行为设置，优先使用 `config.yaml`（如果存在对应的配置键）。下面列出的一些变量是仅限进程的覆盖项或内部桥接变量，即使本文档列出了它们，也不应将其写入 `.env`。

## LLM 提供者（Provider）

| 变量 | 描述 |
|----------|-------------|
| `OPENROUTER_API_KEY` | OpenRouter API 密钥（推荐，灵活性高） |
| `OPENROUTER_BASE_URL` | 覆盖与 OpenRouter 兼容的基础 URL |
| `HERMES_OPENROUTER_CACHE` | 启用 OpenRouter 响应缓存（`1`/`true`/`yes`/`on`）。覆盖 `config.yaml` 中的 `openrouter.response_cache`。参见[响应缓存](https://openrouter.ai/docs/guides/features/response-caching)。 |
| `HERMES_OPENROUTER_CACHE_TTL` | 缓存生存时间（秒，1-86400）。覆盖 `config.yaml` 中的 `openrouter.response_cache_ttl`。 |
| `NOUS_BASE_URL` | 覆盖 Nous Portal 基础 URL（很少使用；仅用于开发/测试） |
| `NOUS_INFERENCE_BASE_URL` | 直接覆盖 Nous 推理端点 |
| `OPENAI_API_KEY` | 自定义 OpenAI 兼容端点的 API 密钥（与 `OPENAI_BASE_URL` 配合使用） |
| `OPENAI_BASE_URL` | 自定义端点（VLLM、SGLang 等）的基础 URL |
| `LM_API_KEY` | LM Studio（`lmstudio` 提供者）的 API 密钥。对于本地服务器通常是一个占位符 |
| `LM_BASE_URL` | LM Studio 基础 URL（默认：`http://localhost:1234/v1`） |
| `COPILOT_GITHUB_TOKEN` | Copilot API 的 GitHub 令牌——最高优先级（OAuth `gho_*` 或细粒度 PAT `github_pat_*`；经典 PAT `ghp_*` **不支持**） |
| `GH_TOKEN` | GitHub 令牌——Copilot 的第二优先级（也用于 `gh` CLI） |
| `GITHUB_TOKEN` | GitHub 令牌——Copilot 的第三优先级 |
| `HERMES_COPILOT_ACP_COMMAND` | 覆盖 Copilot ACP CLI 二进制路径（默认：`copilot`） |
| `COPILOT_CLI_PATH` | `HERMES_COPILOT_ACP_COMMAND` 的别名 |
| `HERMES_COPILOT_ACP_ARGS` | 覆盖 Copilot ACP 参数（默认：`--acp --stdio`） |
| `COPILOT_ACP_BASE_URL` | 覆盖 Copilot ACP 基础 URL |
| `COPILOT_API_BASE_URL` | 覆盖 Copilot API 基础 URL（`copilot` 提供者） |
| `GLM_API_KEY` | z.ai / 智谱 AI GLM API 密钥（[z.ai](https://z.ai)） |
| `ZAI_API_KEY` | `GLM_API_KEY` 的别名 |
| `Z_AI_API_KEY` | `GLM_API_KEY` 的别名 |
| `GLM_BASE_URL` | 覆盖 z.ai 基础 URL（默认：`https://api.z.ai/api/paas/v4`） |
| `KIMI_API_KEY` | Kimi / Moonshot AI API 密钥（[moonshot.ai](https://platform.moonshot.ai)） |
| `KIMI_CODING_API_KEY` | `kimi-coding` 提供者的别名密钥（与 `KIMI_API_KEY` 同时接受） |
| `KIMI_BASE_URL` | 覆盖 Kimi 基础 URL（默认：`https://api.moonshot.ai/v1`） |
| `KIMI_CN_API_KEY` | Kimi / Moonshot 中国 API 密钥（[moonshot.cn](https://platform.moonshot.cn)） |
| `ARCEEAI_API_KEY` | Arcee AI API 密钥（[chat.arcee.ai](https://chat.arcee.ai/)） |
| `ARCEE_BASE_URL` | 覆盖 Arcee 基础 URL（默认：`https://api.arcee.ai/api/v1`） |
| `GMI_API_KEY` | GMI Cloud API 密钥（[gmicloud.ai](https://www.gmicloud.ai/)） |
| `GMI_BASE_URL` | 覆盖 GMI Cloud 基础 URL（默认：`https://api.gmi-serving.com/v1`） |
| `MINIMAX_API_KEY` | MiniMax API 密钥——全球端点（[minimax.io](https://www.minimax.io)）。**`minimax-oauth` 不用此密钥**（OAuth 路径改为使用浏览器登录）。 |
| `MINIMAX_BASE_URL` | 覆盖 MiniMax 基础 URL（默认：`https://api.minimax.io/anthropic`——Hermes 使用 MiniMax 的 Anthropic 消息兼容端点）。**`minimax-oauth` 不用此 URL**。 |
| `MINIMAX_CN_API_KEY` | MiniMax API 密钥——中国端点（[minimaxi.com](https://www.minimaxi.com)）。**`minimax-oauth` 不用此密钥**（OAuth 路径改为使用浏览器登录）。 |
| `MINIMAX_CN_BASE_URL` | 覆盖 MiniMax 中国基础 URL（默认：`https://api.minimaxi.com/anthropic`）。**`minimax-oauth` 不用此 URL**。 |
| `KILOCODE_API_KEY` | Kilo Code API 密钥（[kilo.ai](https://kilo.ai)） |
| `KILOCODE_BASE_URL` | 覆盖 Kilo Code 基础 URL（默认：`https://api.kilo.ai/api/gateway`） |
| `XIAOMI_API_KEY` | 小米 MiMo API 密钥（[platform.xiaomimimo.com](https://platform.xiaomimimo.com)） |
| `XIAOMI_BASE_URL` | 覆盖小米 MiMo 基础 URL（默认：`https://api.xiaomimimo.com/v1`） |
| `TOKENHUB_API_KEY` | 腾讯 TokenHub API 密钥（[tokenhub.tencentmaas.com](https://tokenhub.tencentmaas.com)） |
| `TOKENHUB_BASE_URL` | 覆盖腾讯 TokenHub 基础 URL（默认：`https://tokenhub.tencentmaas.com/v1`） |
| `AZURE_FOUNDRY_API_KEY` | Microsoft Foundry / Azure OpenAI API 密钥（[ai.azure.com](https://ai.azure.com/)）。当 `model.auth_mode: entra_id` 时不需要 |
| `AZURE_FOUNDRY_BASE_URL` | Microsoft Foundry 端点 URL（例如 OpenAI 风格：`https://<resource>.openai.azure.com/openai/v1`，或 Anthropic 风格：`https://<resource>.services.ai.azure.com/anthropic`） |
| `AZURE_ANTHROPIC_KEY` | 用于 `provider: anthropic` + `base_url` 指向 Microsoft Foundry Claude 部署的 Azure Anthropic API 密钥（当同时配置了 Anthropic 和 Azure Anthropic 时，替代 `ANTHROPIC_API_KEY`） |
| `AZURE_TENANT_ID` | Entra ID 租户 ID（服务主体流程；当 `model.auth_mode: entra_id` 时由 `azure-identity` 使用） |
| `AZURE_CLIENT_ID` | Entra ID 客户端 ID（服务主体、工作负载标识或用户分配的托管标识） |
| `AZURE_CLIENT_SECRET` | `EnvironmentCredential` 使用的服务主体密码 |
| `AZURE_CLIENT_CERTIFICATE_PATH` | 服务主体证书（替代 `AZURE_CLIENT_SECRET`） |
| `AZURE_FEDERATED_TOKEN_FILE` | AKS 工作负载标识 / OIDC 流程的联合令牌文件路径 |
| `AZURE_AUTHORITY_HOST` | 主权云授权覆盖（例如 Azure 政府使用 `https://login.microsoftonline.us`）。参见 [Azure Foundry 指南](/guides/azure-foundry#sovereign-clouds-government-china) |
| `IDENTITY_ENDPOINT` / `MSI_ENDPOINT` | 用于应用服务、函数和容器应用的托管标识端点；虚拟机通常使用 IMDS，不设置这两个变量 |
| `HF_TOKEN` | Hugging Face 推理提供者（Inference Providers）的令牌（[huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)） |
| `HF_BASE_URL` | 覆盖 Hugging Face 基础 URL（默认：`https://router.huggingface.co/v1`） |
| `GOOGLE_API_KEY` | Google AI Studio API 密钥（[aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)） |
| `GEMINI_API_KEY` | `GOOGLE_API_KEY` 的别名 |
| `GEMINI_BASE_URL` | 覆盖 Google AI Studio 基础 URL |
| `ANTHROPIC_API_KEY` | Anthropic Console API 密钥（[console.anthropic.com](https://console.anthropic.com/)） |
| `ANTHROPIC_BASE_URL` | 覆盖 Anthropic API 基础 URL |
| `ANTHROPIC_TOKEN` | 手动或旧版 Anthropic OAuth/设置令牌覆盖 |
| `DASHSCOPE_API_KEY` | 通义千问（阿里 DashScope）API 密钥，用于 Qwen 模型（[modelstudio.console.alibabacloud.com](https://modelstudio.console.alibabacloud.com/)） |
| `DASHSCOPE_BASE_URL` | 自定义 DashScope 基础 URL（默认：`https://dashscope-intl.aliyuncs.com/compatible-mode/v1`；中国内地区域使用 `https://dashscope.aliyuncs.com/compatible-mode/v1`） |
| `ALIBABA_CODING_PLAN_API_KEY` | 通义千问编码计划（Qwen Coding Plan）API 密钥（`alibaba-coding-plan` 提供者） |
| `ALIBABA_CODING_PLAN_BASE_URL` | 覆盖通义千问编码计划基础 URL |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥，用于直接访问 DeepSeek（[platform.deepseek.com](https://platform.deepseek.com/api_keys)） |
| `DEEPSEEK_BASE_URL` | 自定义 DeepSeek API 基础 URL |
| `NOVITA_API_KEY` | NovitaAI API 密钥——AI 原生云，提供模型 API、Agent 沙箱和 GPU 云（[novita.ai/settings/key-management](https://novita.ai/settings/key-management)） |
| `NOVITA_BASE_URL` | 覆盖 NovitaAI 基础 URL（默认：`https://api.novita.ai/openai/v1`） |
| `NVIDIA_API_KEY` | NVIDIA NIM API 密钥——Nemotron 和开放模型（[build.nvidia.com](https://build.nvidia.com)） |
| `NVIDIA_BASE_URL` | 覆盖 NVIDIA 基础 URL（默认：`https://integrate.api.nvidia.com/v1`；本地 NIM 端点设为 `http://localhost:8000/v1`） |
| `STEPFUN_API_KEY` | StepFun API 密钥——Step 系列模型（[platform.stepfun.com](https://platform.stepfun.com)） |
| `STEPFUN_BASE_URL` | 覆盖 StepFun 基础 URL（默认：`https://api.stepfun.com/v1`） |
| `OLLAMA_API_KEY` | Ollama Cloud API 密钥——无需本地 GPU 的托管 Ollama 目录（[ollama.com/settings/keys](https://ollama.com/settings/keys)） |
| `OLLAMA_BASE_URL` | 覆盖 Ollama Cloud 基础 URL（默认：`https://ollama.com/v1`） |
| `XAI_API_KEY` | xAI（Grok）API 密钥，用于聊天 + TTS + 网络搜索（[console.x.ai](https://console.x.ai/)） |
| `XAI_BASE_URL` | 覆盖 xAI 基础 URL（默认：`https://api.x.ai/v1`） |
| `MISTRAL_API_KEY` | Mistral API 密钥，用于 Voxtral TTS 和 Voxtral STT（[console.mistral.ai](https://console.mistral.ai)） |
| `AWS_REGION` | Bedrock 推理的 AWS 区域（例如 `us-east-1`、`eu-central-1`）。由 boto3 读取。 |
| `AWS_PROFILE` | Bedrock 认证的 AWS 命名配置文件（读取 `~/.aws/credentials`）。不设置则使用默认 boto3 凭证链。 |
| `BEDROCK_BASE_URL` | 覆盖 Bedrock 运行时基础 URL（默认：`https://bedrock-runtime.us-east-1.amazonaws.com`；通常保持不设置，改用 `AWS_REGION`） |
| `HERMES_QWEN_BASE_URL` | 通义千问 Portal 基础 URL 覆盖（默认：`https://portal.qwen.ai/v1`） |
| `OPENCODE_ZEN_API_KEY` | OpenCode Zen API 密钥——按需付费访问精选模型（[opencode.ai](https://opencode.ai/auth)） |
| `OPENCODE_ZEN_BASE_URL` | 覆盖 OpenCode Zen 基础 URL |
| `OPENCODE_GO_API_KEY` | OpenCode Go API 密钥——10美元/月订阅开放模型（[opencode.ai](https://opencode.ai/auth)） |
| `OPENCODE_GO_BASE_URL` | 覆盖 OpenCode Go 基础 URL |
| `CLAUDE_CODE_OAUTH_TOKEN` | 手动导出的显式 Claude Code 令牌覆盖 |
| `HERMES_MODEL` | 在进程级别覆盖模型名称（由 cron 调度器使用；正常使用请优先使用 `config.yaml`） |
| `VOICE_TOOLS_OPENAI_KEY` | 用于 OpenAI 语音转文本和文本转语音提供者的首选 OpenAI 密钥 |
| `HERMES_LOCAL_STT_COMMAND` | 可选的本地语音转文本命令模板。支持 `{input_path}`、`{output_dir}`、`{language}` 和 `{model}` 占位符 |
| `HERMES_LOCAL_STT_LANGUAGE` | 传递给 `HERMES_LOCAL_STT_COMMAND` 的默认语言，或自动检测的本地 `whisper` CLI 回退（默认：`en`） |
| `HERMES_HOME` | 覆盖 Hermes 配置目录（默认：`~/.hermes`）。同时影响网关 PID 文件和 systemd 服务名称，因此多个安装可以同时运行 |
| `HERMES_GIT_BASH_PATH` | **仅 Windows。** 覆盖终端工具的 `bash.exe` 发现路径。指向任何 bash——完整 Git for Windows 安装、通过符号链接的 WSL bash、MSYS2、Cygwin。安装程序自动将其设置为它提供的 PortableGit 路径。参见 [Windows（原生）指南](../user-guide/windows-native.md#how-hermes-runs-shell-commands-on-windows) |
| `HERMES_DISABLE_WINDOWS_UTF8` | **仅 Windows。** 设为 `1` 可禁用 UTF-8 stdio 垫片（`configure_windows_stdio()`），回退到控制台的区域代码页。用于二分编码错误；正常操作中很少是正确的设置 |
| `HERMES_KANBAN_HOME` | 覆盖共享的 Hermes 根目录，该目录锚定看板（数据库 + 工作区 + 工作进程日志）。回退到 `get_default_hermes_root()`（任何活动配置文件的父目录）。用于测试和不常见的部署 |
| `HERMES_KANBAN_BOARD` | 为该进程固定活动的看板。优先级高于 `~/.hermes/kanban/current`；调度器将其注入工作进程子进程环境变量，使工作进程实际上看不到其他板上的任务。默认为 `default`。slug 验证：小写字母数字 + 连字符 + 下划线，1-64 个字符 |
| `HERMES_KANBAN_DB` | 直接固定看板数据库文件路径（最高优先级；优先级高于 `HERMES_KANBAN_BOARD` 和 `HERMES_KANBAN_HOME`）。调度器将其注入工作进程子进程环境变量，使配置文件工作进程收敛到调度器的板上 |
| `HERMES_KANBAN_WORKSPACES_ROOT` | 直接固定看板工作区根目录（工作区的最高优先级；优先级高于 `HERMES_KANBAN_HOME`）。调度器将其注入工作进程子进程环境变量 |
| `HERMES_KANBAN_DISPATCH_IN_GATEWAY` | 运行时覆盖 `kanban.dispatch_in_gateway`。设为 `0`、`false`、`no` 或 `off` 可阻止网关启动嵌入式看板调度器；任何其他非空值则启用。当有单独的调度器进程拥有该板时很有用。 |

## 提供者认证（OAuth）

对于原生 Anthropic 认证，Hermes 优先使用 Claude Code 自身的凭据文件（如果存在），因为这些凭据可以自动刷新。**针对 Anthropic 的 OAuth 需要 Claude Max 计划并购买额外使用额度**——Hermes 以 Claude Code 身份路由，仅从 Max 计划的额外/超量额度中扣除，而非基础 Max 津贴，并且在 Claude Pro 上不起作用。如果没有 Max + 额外额度，请改用 API 密钥。环境变量如 `ANTHROPIC_TOKEN` 仍然可用作手动覆盖，但它们不再是 Claude Max 登录的首选路径。

| 变量 | 描述 |
|----------|-------------|
| `HERMES_PORTAL_BASE_URL` | 覆盖 Nous Portal URL（用于开发/测试） |
| `NOUS_INFERENCE_BASE_URL` | 覆盖 Nous 推理 API URL |
| `HERMES_NOUS_MIN_KEY_TTL_SECONDS` | 代理密钥在重新生成前的最小 TTL（默认：1800 = 30 分钟） |
| `HERMES_NOUS_TIMEOUT_SECONDS` | Nous 凭据/令牌流程的 HTTP 超时 |
| `HERMES_DUMP_REQUESTS` | 将 API 请求负载转储到日志文件（`true`/`false`） |
| `HERMES_PREFILL_MESSAGES_FILE` | 临时预填充消息的 JSON 文件路径，在 API 调用时注入 |
| `HERMES_TIMEZONE` | IANA 时区覆盖（例如 `America/New_York`） |

## 工具 API

| 变量 | 描述 |
|----------|-------------|
| `PARALLEL_API_KEY` | AI 原生网络搜索（[parallel.ai](https://parallel.ai/)） |
| `FIRECRAWL_API_KEY` | 网络抓取和云浏览器（[firecrawl.dev](https://firecrawl.dev/)） |
| `FIRECRAWL_API_URL` | 自定义 Firecrawl API 端点，用于自托管实例（可选） |
| `TAVILY_API_KEY` | Tavily API 密钥，用于 AI 原生网络搜索、提取和爬取（[app.tavily.com](https://app.tavily.com/home)） |
| `SEARXNG_URL` | SearXNG 实例 URL，用于免费自托管网络搜索——无需 API 密钥（[searxng.github.io](https://searxng.github.io/searxng/)） |
| `TAVILY_BASE_URL` | 覆盖 Tavily API 端点。用于企业代理和自托管的 Tavily 兼容搜索后端。与 `GROQ_BASE_URL` 模式相同。 |
| `EXA_API_KEY` | Exa API 密钥，用于 AI 原生网络搜索和内容（[exa.ai](https://exa.ai/)） |
| `BROWSERBASE_API_KEY` | 浏览器自动化（[browserbase.com](https://browserbase.com/)） |
| `BROWSERBASE_PROJECT_ID` | Browserbase 项目 ID |
| `BROWSER_USE_API_KEY` | Browser Use 云浏览器 API 密钥（[browser-use.com](https://browser-use.com/)） |
| `FIRECRAWL_BROWSER_TTL` | Firecrawl 浏览器会话 TTL（秒，默认：300） |
| `BROWSER_CDP_URL` | 本地浏览器的 Chrome DevTools Protocol URL（通过 `/browser connect` 设置，例如 `ws://localhost:9222`） |
| `CAMOFOX_URL` | Camofox 本地反检测浏览器 URL（默认：`http://localhost:9377`） |
| `CAMOFOX_USER_ID` | 可选的外部管理的 Camofox 用户 ID，用于共享可见会话 |
| `CAMOFOX_SESSION_KEY` | 可选的 Camofox 会话密钥，在创建 `CAMOFOX_USER_ID` 的标签页时使用 |
| `CAMOFOX_ADOPT_EXISTING_TAB` | 设为 `true` 可在创建新标签页之前重用现有的 Camofox 标签页 |
| `BROWSER_INACTIVITY_TIMEOUT` | 浏览器会话不活动超时（秒） |
| `AGENT_BROWSER_ARGS` | 额外的 Chromium 启动标志（逗号或换行分隔）。Hermes 在 root 用户运行或受 AppArmor 限制的非特权用户命名空间（Ubuntu 23.10+、DGX Spark、许多容器镜像）下运行时自动注入 `--no-sandbox,--disable-dev-shm-usage`；请仅在需要覆盖或添加其他标志时手动设置。 |
| `FAL_KEY` | 图像生成（[fal.ai](https://fal.ai/)） |
| `GROQ_API_KEY` | Groq Whisper STT API 密钥（[groq.com](https://groq.com/)） |
| `ELEVENLABS_API_KEY` | ElevenLabs 高级 TTS 语音（[elevenlabs.io](https://elevenlabs.io/)） |
| `STT_GROQ_MODEL` | 覆盖 Groq STT 模型（默认：`whisper-large-v3-turbo`） |
| `GROQ_BASE_URL` | 覆盖 Groq OpenAI 兼容的 STT 端点 |
| `STT_OPENAI_MODEL` | 覆盖 OpenAI STT 模型（默认：`whisper-1`） |
| `STT_OPENAI_BASE_URL` | 覆盖 OpenAI 兼容的 STT 端点 |
| `GITHUB_TOKEN` | 用于 Skills Hub 的 GitHub 令牌（更高的 API 速率限制、技能发布） |
| `HONCHO_API_KEY` | 跨会话用户建模（[honcho.dev](https://honcho.dev/)） |
| `HONCHO_BASE_URL` | 自托管 Honcho 实例的基础 URL（默认：Honcho 云）。本地实例无需 API 密钥 |
| `HINDSIGHT_TIMEOUT` | Hindsight 内存提供者 API 调用的超时时间（秒，默认：`60`）。如果 Hindsight 实例在 `/sync` 或 `on_session_switch` 期间响应缓慢，并且在 `errors.log` 中看到超时，请增大此值。 |
| `SUPERMEMORY_API_KEY` | 具有配置文件回忆和会话摄入的语义长期记忆（[supermemory.ai](https://supermemory.ai)） |
| `DAYTONA_API_KEY` | Daytona 云沙箱（[daytona.io](https://daytona.io)） |

### Langfuse 可观测性

用于内置 [`observability/langfuse`](/user-guide/features/built-in-plugins#observabilitylangfuse) 插件 的环境变量。在 `~/.hermes/.env` 中设置。插件还必须启用（`hermes plugins enable observability/langfuse`，或在 `hermes plugins` 中勾选），这些变量才会生效。

| 变量 | 描述 |
|----------|-------------|
| `HERMES_LANGFUSE_PUBLIC_KEY` | Langfuse 项目公钥（`pk-lf-...`）。必填。 |
| `HERMES_LANGFUSE_SECRET_KEY` | Langfuse 项目密钥（`sk-lf-...`）。必填。 |
| `HERMES_LANGFUSE_BASE_URL` | Langfuse 服务器 URL（默认：`https://cloud.langfuse.com`）。自托管时设置。 |
| `HERMES_LANGFUSE_ENV` | 追踪的环境标签（`production`、`staging` 等） |
| `HERMES_LANGFUSE_RELEASE` | 追踪的发布/版本标签 |
| `HERMES_LANGFUSE_SAMPLE_RATE` | SDK 采样率 0.0–1.0（默认：`1.0`） |
| `HERMES_LANGFUSE_MAX_CHARS` | 序列化负载的每字段截断长度（默认：`12000`） |
| `HERMES_LANGFUSE_DEBUG` | `true` 启用详细插件日志记录到 `agent.log` |
| `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` / `LANGFUSE_BASE_URL` | 标准 Langfuse SDK 名称。当 `HERMES_LANGFUSE_*` 等效项未设置时作为回退接受。 |

### Nous 工具网关

这些变量配置付费 Nous 订阅者或自托管网关部署的[工具网关](/user-guide/features/tool-gateway)。大多数用户无需设置——网关通过 `hermes model` 或 `hermes tools` 自动配置。

| 变量 | 描述 |
|----------|-------------|
| `TOOL_GATEWAY_DOMAIN` | 工具网关路由的基础域名（默认：`nousresearch.com`） |
| `TOOL_GATEWAY_SCHEME` | 网关 URL 的 HTTP 或 HTTPS 方案（默认：`https`） |
| `TOOL_GATEWAY_USER_TOKEN` | 工具网关的认证令牌（通常从 Nous 认证自动填充） |
| `FIRECRAWL_GATEWAY_URL` | 专门覆盖 Firecrawl 网关端点的 URL |

## 终端后端

| 变量 | 描述 |
|----------|-------------|
| `TERMINAL_ENV` | 后端：`local`、`docker`、`ssh`、`singularity`、`modal`、`daytona` |
| `HERMES_DOCKER_BINARY` | 覆盖 Hermes 调用的容器二进制文件（例如 `podman`、`/usr/local/bin/docker`）。未设置时，Hermes 自动发现 `PATH` 上的 `docker` 或 `podman`。当两者都安装并且你想使用非默认项，或二进制文件不在 `PATH` 中时需要。 |
| `TERMINAL_DOCKER_IMAGE` | Docker 镜像（默认：`nikolaik/python-nodejs:python3.11-nodejs20`） |
| `TERMINAL_DOCKER_FORWARD_ENV` | JSON 数组，显式转发到 Docker 终端会话的环境变量名称。注意：技能声明的 `required_environment_variables` 会自动转发——你只需要为任何技能未声明的变量设置此项。 |
| `TERMINAL_DOCKER_VOLUMES` | 额外的 Docker 卷挂载（逗号分隔的 `host:container` 对） |
| `TERMINAL_DOCKER_MOUNT_CWD_TO_WORKSPACE` | 高级选择加入：将启动 cwd 挂载到 Docker `/workspace`（`true`/`false`，默认：`false`） |
| `TERMINAL_SINGULARITY_IMAGE` | Singularity 镜像或 `.sif` 路径 |
| `TERMINAL_MODAL_IMAGE` | Modal 容器镜像 |
| `TERMINAL_DAYTONA_IMAGE` | Daytona 沙箱镜像 |
| `TERMINAL_TIMEOUT` | 命令超时（秒） |
| `TERMINAL_LIFETIME_SECONDS` | 终端会话的最大生存时间（秒） |
| `TERMINAL_CWD` | 已弃用。用于网关/cron 终端会话的直接覆盖。优先使用 `config.yaml` 中的 `terminal.cwd`；CLI 仍使用启动目录。 |
| `SUDO_PASSWORD` | 无需交互式提示即可使用 sudo |

对于云沙箱后端，持久性是基于文件系统的。`TERMINAL_LIFETIME_SECONDS` 控制 Hermes 何时清理空闲的终端会话，后续恢复可能会重新创建沙箱，而不是保持相同的实时进程运行。

## SSH 后端

| 变量 | 描述 |
|----------|-------------|
| `TERMINAL_SSH_HOST` | 远程服务器主机名 |
| `TERMINAL_SSH_USER` | SSH 用户名 |
| `TERMINAL_SSH_PORT` | SSH 端口（默认：22） |
| `TERMINAL_SSH_KEY` | 私钥路径 |
| `TERMINAL_SSH_PERSISTENT` | 覆盖 SSH 的持久 shell（默认：遵循 `TERMINAL_PERSISTENT_SHELL`） |

## 容器资源（Docker、Singularity、Modal、Daytona）

| 变量 | 描述 |
|----------|-------------|
| `TERMINAL_CONTAINER_CPU` | CPU 核心数（默认：1） |
| `TERMINAL_CONTAINER_MEMORY` | 内存（MB，默认：5120） |
| `TERMINAL_CONTAINER_DISK` | 磁盘（MB，默认：51200） |
| `TERMINAL_CONTAINER_PERSISTENT` | 跨会话持久化容器文件系统（默认：`true`） |
| `TERMINAL_SANDBOX_DIR` | 工作区和覆盖层的主机目录（默认：`~/.hermes/sandboxes/`） |

## 持久 Shell

| 变量 | 描述 |
|----------|-------------|
| `TERMINAL_PERSISTENT_SHELL` | 启用非本地后端的持久 shell（默认：`true`）。也可通过 `config.yaml` 中的 `terminal.persistent_shell` 设置 |
| `TERMINAL_LOCAL_PERSISTENT` | 启用本地后端的持久 shell（默认：`false`） |
| `TERMINAL_SSH_PERSISTENT` | 覆盖 SSH 后端的持久 shell（默认：遵循 `TERMINAL_PERSISTENT_SHELL`） |

## 消息

| 变量 | 描述 |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Telegram 机器人令牌（来自 @BotFather） |
| `TELEGRAM_ALLOWED_USERS` | 逗号分隔的用户 ID，允许使用该机器人（适用于私聊、群组和论坛） |
| `TELEGRAM_GROUP_ALLOWED_USERS` | 逗号分隔的发送者用户 ID，仅在群组/论坛中授权（不授予私聊访问权限）。以 `-` 开头的聊天 ID 形状的值仍被视作聊天 ID，以保持与 #17686 之前配置的向后兼容性，但会给出弃用警告。 |
| `TELEGRAM_GROUP_ALLOWED_CHATS` | 逗号分隔的群组/论坛聊天 ID；任何成员均被授权 |
| `TELEGRAM_HOME_CHANNEL` | 用于 cron 交付的默认 Telegram 聊天/频道 |
| `TELEGRAM_HOME_CHANNEL_NAME` | Telegram 首页频道的显示名称 |
| `TELEGRAM_CRON_THREAD_ID` | 接收 cron 交付的论坛主题 ID；仅覆盖 cron 的 `TELEGRAM_HOME_CHANNEL_THREAD_ID`。在主题模式下使用，这样对 cron 消息的回复会打开一个新会话，而不是进入系统大厅 (#24409)。 |
| `TELEGRAM_WEBHOOK_URL` | 用于 webhook 模式的公共 HTTPS URL（启用 webhook 而非轮询） |
| `TELEGRAM_WEBHOOK_PORT` | webhook 服务器的本地监听端口（默认：`8443`） |
| `TELEGRAM_WEBHOOK_SECRET` | Telegram 在每次更新中回显以进行验证的密钥令牌。**只要设置了 `TELEGRAM_WEBHOOK_URL` 就必须设置**——网关启动时会拒绝启动，如果没有该令牌会报错（GHSA-3vpc-7q5r-276h）。使用 `openssl rand -hex 32` 生成。 |
| `TELEGRAM_REACTIONS` | 在处理过程中启用消息的表情反应（默认：`false`） |
| `TELEGRAM_REQUIRE_MENTION` | 在 Telegram 群组中需要显式触发才响应。等同于 `config.yaml` 中的 `telegram.require_mention`。 |
| `TELEGRAM_MENTION_PATTERNS` | JSON 数组、换行分隔列表或逗号分隔的正则表达式唤醒词模式列表，在启用 Telegram 群组提及门控时接受。等同于 `telegram.mention_patterns`。 |
| `TELEGRAM_EXCLUSIVE_BOT_MENTIONS` | 启用后，Telegram 群组中的显式 `@...bot` 提及仅在回复或唤醒词回退运行之前路由到被提及的机器人用户名。默认：`true`。等同于 `telegram.exclusive_bot_mentions`。 |
| `TELEGRAM_REPLY_TO_MODE` | 回复引用行为：`off`、`first`（默认）或 `all`。与 Discord 模式匹配。 |
| `TELEGRAM_IGNORED_THREADS` | 逗号分隔的 Telegram 论坛主题/线程 ID，机器人永远不会在这些线程中回复 |
| `TELEGRAM_PROXY` | Telegram 连接的代理 URL——覆盖 `HTTPS_PROXY`。支持 `http://`、`https://`、`socks5://` |
| `DISCORD_BOT_TOKEN` | Discord 机器人令牌 |
| `DISCORD_ALLOWED_USERS` | 逗号分隔的 Discord 用户 ID，允许使用该机器人 |
| `DISCORD_ALLOWED_ROLES` | 逗号分隔的 Discord 角色 ID，允许使用该机器人（与 `DISCORD_ALLOWED_USERS` 是 OR 关系）。自动启用 Members intent。当管理团队更替时很有用——角色授权会自动传播。 |
| `DISCORD_ALLOWED_CHANNELS` | 逗号分隔的 Discord 频道 ID。设置后，机器人仅在这些频道中回复（加上允许的私聊）。覆盖 `config.yaml` 中的 `discord.allowed_channels`。 |
| `DISCORD_PROXY` | Discord 连接的代理 URL——覆盖 `HTTPS_PROXY`。支持 `http://`、`https://`、`socks5://` |
| `DISCORD_HOME_CHANNEL` | 用于 cron 交付的默认 Discord 频道 |
| `DISCORD_HOME_CHANNEL_NAME` | Discord 首页频道的显示名称 |
| `DISCORD_COMMAND_SYNC_POLICY` | Discord 斜杠命令启动同步策略：`safe`（差异比较和协调）、`bulk`（旧版 `tree.sync()`）或 `off` |
| `DISCORD_REQUIRE_MENTION` | 在服务器频道中需要 @提及才回复 |
| `DISCORD_FREE_RESPONSE_CHANNELS` | 逗号分隔的频道 ID，这些频道中不需要提及 |
| `DISCORD_AUTO_THREAD` | 支持时自动将长回复转换为线程 |
| `DISCORD_ALLOW_ANY_ATTACHMENT` | 为 `true` 时，接受任何文件类型的附件（不仅是内置的 PDF/文本/zip/Office 允许列表）。未知类型会被缓存，并以本地路径形式提供给代理，使其可以通过 `terminal` / `read_file` / `ffprobe` 检查。默认 `false`。 |
| `DISCORD_MAX_ATTACHMENT_BYTES` | 网关将缓存的每个附件的最大字节数。默认 `33554432`（32 MiB）。设为 `0` 表示无限制（附件在写入时保存在内存中）。 |
| `DISCORD_REACTIONS` | 在处理过程中启用消息的表情反应（默认：`true`） |
| `DISCORD_IGNORED_CHANNELS` | 逗号分隔的频道 ID，机器人永远不会在这些频道中回复 |
| `DISCORD_NO_THREAD_CHANNELS` | 逗号分隔的频道 ID，机器人在这些频道中回复时不自动创建线程 |
| `DISCORD_REPLY_TO_MODE` | 回复引用行为：`off`、`first`（默认）或 `all` |
| `DISCORD_ALLOW_MENTION_EVERYONE` | 允许机器人 @所有人/@在这里（默认：`false`）。参见[提及控制](../user-guide/messaging/discord.md#mention-control)。 |
| `DISCORD_ALLOW_MENTION_ROLES` | 允许机器人 @角色 提及（默认：`false`）。 |
| `DISCORD_ALLOW_MENTION_USERS` | 允许机器人 @用户 提及（默认：`true`）。 |
| `DISCORD_ALLOW_MENTION_REPLIED_USER` | 回复消息时 @提及原作者（默认：`true`）。 |
| `SLACK_BOT_TOKEN` | Slack 机器人令牌（`xoxb-...`） |
| `SLACK_APP_TOKEN` | Slack 应用级令牌（`xapp-...`，Socket Mode 必需） |
| `SLACK_ALLOWED_USERS` | 逗号分隔的 Slack 用户 ID |
| `SLACK_HOME_CHANNEL` | 用于 cron 交付的默认 Slack 频道 |
| `SLACK_HOME_CHANNEL_NAME` | Slack 首页频道的显示名称 |
| `GOOGLE_CHAT_PROJECT_ID` | 托管 Pub/Sub 主题的 GCP 项目（回退到 `GOOGLE_CLOUD_PROJECT`） |
| `GOOGLE_CHAT_SUBSCRIPTION_NAME` | 完整的 Pub/Sub 订阅路径，`projects/{proj}/subscriptions/{sub}`（旧别名：`GOOGLE_CHAT_SUBSCRIPTION`） |
| `GOOGLE_CHAT_SERVICE_ACCOUNT_JSON` | 服务账户 JSON 文件路径，或内联 JSON（回退到 `GOOGLE_APPLICATION_CREDENTIALS`） |
| `GOOGLE_CHAT_ALLOWED_USERS` | 逗号分隔的允许与机器人聊天的用户电子邮件 |
| `GOOGLE_CHAT_ALLOW_ALL_USERS` | 允许任何 Google Chat 用户触发机器人（仅限开发） |
| `GOOGLE_CHAT_HOME_CHANNEL` | 用于 cron 交付的默认空间（例如 `spaces/AAAA...`） |
| `GOOGLE_CHAT_HOME_CHANNEL_NAME` | Google Chat 首页空间的显示名称 |
| `GOOGLE_CHAT_MAX_MESSAGES` | Pub/Sub FlowControl 最大在途消息数（默认：`1`） |
| `GOOGLE_CHAT_MAX_BYTES` | Pub/Sub FlowControl 最大在途字节数（默认：`16777216`，16 MiB） |
| `GOOGLE_CHAT_BOOTSTRAP_SPACES` | 逗号分隔的额外空间 ID，在启动时探测，用于解析机器人自身的 `users/{id}` |
| `GOOGLE_CHAT_DEBUG_RAW` | 设为任意值可在 DEBUG 级别记录已编辑的 Pub/Sub 信封（仅调试） |
| `WHATSAPP_ENABLED` | 启用 WhatsApp 桥接器（`true`/`false`） |
| `WHATSAPP_MODE` | `bot`（独立号码）或 `self-chat`（给自己发消息） |
| `WHATSAPP_ALLOWED_USERS` | 逗号分隔的电话号码（带国家代码，无 `+`），或 `*` 允许所有发送者 |
| `WHATSAPP_ALLOW_ALL_USERS` | 允许所有 WhatsApp 发送者，无需允许列表（`true`/`false`） |
| `WHATSAPP_DEBUG` | 在桥接器中记录原始消息事件以进行故障排除（`true`/`false`） |
| `WHATSAPP_CLOUD_PHONE_NUMBER_ID` | WhatsApp Business Cloud API 的 Meta 电话号码 ID（15–17 位数字；**不是**电话号码本身） |
| `WHATSAPP_CLOUD_ACCESS_TOKEN` | Meta 访问令牌（以 `EAA` 开头）；临时令牌 24 小时后过期，系统用户令牌是永久的 |
| `WHATSAPP_CLOUD_APP_SECRET` | 32 字符十六进制应用密钥，用于验证入站 webhook 签名 |
| `WHATSAPP_CLOUD_VERIFY_TOKEN` | Meta webhook 验证握手的共享密钥（由设置向导自动生成） |
| `WHATSAPP_CLOUD_ALLOWED_USERS` | 逗号分隔的 `wa_id`（带国家代码的电话号码，无 `+`），允许给机器人发送消息 |
| `WHATSAPP_CLOUD_ALLOW_ALL_USERS` | 允许所有 WhatsApp Cloud 发送者，无需允许列表（`true`/`false`） |
| `WHATSAPP_CLOUD_APP_ID` | 可选的 Meta App ID（用于未来的分析集成） |
| `WHATSAPP_CLOUD_WABA_ID` | 可选的 WhatsApp Business Account ID（用于未来的分析集成） |
| `WHATSAPP_CLOUD_WEBHOOK_HOST` | 入站 webhook 服务器绑定的接口（默认 `0.0.0.0`） |
| `WHATSAPP_CLOUD_WEBHOOK_PORT` | 入站 webhook 服务器绑定的端口（默认 `8090`） |
| `WHATSAPP_CLOUD_WEBHOOK_PATH` | Meta 发布入站消息的 URL 路径（默认 `/whatsapp/webhook`） |
| `WHATSAPP_CLOUD_API_VERSION` | 要调用的 Meta Graph API 版本（默认 `v20.0`） |
| `WHATSAPP_CLOUD_HOME_CHANNEL` | 用作机器人首页频道的 `wa_id`（用于 cron 任务等） |
| `WHATSAPP_CLOUD_DM_POLICY` | Cloud 适配器的私聊门控（`open`/`allowlist`/`disabled`）；未设置时回退到 `WHATSAPP_DM_POLICY` |
| `WHATSAPP_CLOUD_ALLOW_FROM` | 当 `dm_policy: allowlist` 时允许的发送者（逗号分隔的 `wa_id`；Baileys 风格的 JID 会被规范化） |
| `WHATSAPP_CLOUD_GROUP_POLICY` | Cloud 适配器的群组门控（`open`/`allowlist`/`disabled`）；未设置时回退到 `WHATSAPP_GROUP_POLICY` |
| `WHATSAPP_CLOUD_GROUP_ALLOW_FROM` | 当 `group_policy: allowlist` 时允许的群组聊天 ID（逗号分隔） |
| `SIGNAL_HTTP_URL` | signal-cli 守护进程 HTTP 端点（例如 `http://127.0.0.1:8080`） |
| `SIGNAL_ACCOUNT` | 机器人电话号码（E.164 格式） |
| `SIGNAL_ALLOWED_USERS` | 逗号分隔的 E.164 电话号码或 UUID |
| `SIGNAL_GROUP_ALLOWED_USERS` | 逗号分隔的群组 ID，或 `*` 表示所有群组 |
| `SIGNAL_HOME_CHANNEL_NAME` | Signal 首页频道的显示名称 |
| `SIGNAL_IGNORE_STORIES` | 忽略 Signal 故事/状态更新 |
| `SIGNAL_ALLOW_ALL_USERS` | 允许所有 Signal 用户，无需允许列表 |
| `TWILIO_ACCOUNT_SID` | Twilio 账户 SID（与电话技能共享） |
| `TWILIO_AUTH_TOKEN` | Twilio 认证令牌（与电话技能共享；也用于 webhook 签名验证） |
| `TWILIO_PHONE_NUMBER` | Twilio 电话号码（E.164 格式）（与电话技能共享） |
| `SMS_WEBHOOK_URL` | Twilio 签名验证的公共 URL——必须与 Twilio 控制台中的 webhook URL 匹配（必填） |
| `SMS_WEBHOOK_PORT` | 入站短信的 webhook 监听端口（默认：`8080`） |
| `SMS_WEBHOOK_HOST` | Webhook 绑定地址（默认：`0.0.0.0`） |
| `SMS_INSECURE_NO_SIGNATURE` | 设为 `true` 可禁用 Twilio 签名验证（仅限本地开发——不可用于生产） |
| `SMS_ALLOWED_USERS` | 逗号分隔的 E.164 电话号码，允许聊天 |
| `SMS_ALLOW_ALL_USERS` | 允许所有短信发送者，无需允许列表 |
| `SMS_HOME_CHANNEL` | 用于 cron 作业/通知传递的电话号码 |
| `SMS_HOME_CHANNEL_NAME` | 短信首页频道的显示名称 |
| `EMAIL_ADDRESS` | 电子邮件网关适配器的电子邮件地址 |
| `EMAIL_PASSWORD` | 电子邮件账户的密码或应用密码 |
| `EMAIL_IMAP_HOST` | 电子邮件适配器的 IMAP 主机名 |
| `EMAIL_IMAP_PORT` | IMAP 端口 |
| `EMAIL_SMTP_HOST` | 电子邮件适配器的 SMTP 主机名 |
| `EMAIL_SMTP_PORT` | SMTP 端口 |
| `EMAIL_ALLOWED_USERS` | 逗号分隔的电子邮件地址，允许给机器人发消息 |
| `EMAIL_HOME_ADDRESS` | 主动邮件传递的默认收件人 |
| `EMAIL_HOME_ADDRESS_NAME` | 电子邮件首页目标的显示名称 |
| `EMAIL_POLL_INTERVAL` | 电子邮件轮询间隔（秒） |
| `EMAIL_ALLOW_ALL_USERS` | 允许所有入站电子邮件发送者 |
| `DINGTALK_CLIENT_ID` | 来自开发者门户的钉钉机器人 AppKey（[open.dingtalk.com](https://open.dingtalk.com)） |
| `DINGTALK_CLIENT_SECRET` | 来自开发者门户的钉钉机器人 AppSecret |
| `DINGTALK_ALLOWED_USERS` | 逗号分隔的钉钉用户 ID，允许给机器人发消息 |
| `FEISHU_APP_ID` | 来自 [open.feishu.cn](https://open.feishu.cn/) 的飞书/Lark 机器人 App ID |
| `FEISHU_APP_SECRET` | 飞书/Lark 机器人 App Secret |
| `FEISHU_DOMAIN` | `feishu`（中国）或 `lark`（国际）。默认：`feishu` |
| `FEISHU_CONNECTION_MODE` | `websocket`（推荐）或 `webhook`。默认：`websocket` |
| `FEISHU_ENCRYPT_KEY` | 可选的 webhook 模式加密密钥 |
| `FEISHU_VERIFICATION_TOKEN` | 可选的 webhook 模式验证令牌 |
| `FEISHU_ALLOWED_USERS` | 逗号分隔的飞书用户 ID，允许给机器人发消息 |
| `FEISHU_ALLOW_BOTS` | `none`（默认）/ `mentions` / `all`——接受来自其他机器人的入站消息。参见[机器人间消息](../user-guide/messaging/feishu.md#bot-to-bot-messaging) |
| `FEISHU_REQUIRE_MENTION` | `true`（默认）/ `false`——群组消息是否必须 @提及机器人。可通过 `group_rules.<chat_id>.require_mention` 按聊天覆盖。 |
| `FEISHU_HOME_CHANNEL` | 用于 cron 传递和通知的飞书聊天 ID |
| `WECOM_BOT_ID` | 来自管理控制台的企业微信 AI 机器人 ID |
| `WECOM_SECRET` | 企业微信 AI 机器人密钥 |
| `WECOM_WEBSOCKET_URL` | 自定义 WebSocket URL（默认：`wss://openws.work.weixin.qq.com`） |
| `WECOM_ALLOWED_USERS` | 逗号分隔的企业微信用户 ID，允许给机器人发消息 |
| `WECOM_HOME_CHANNEL` | 用于 cron 传递和通知的企业微信聊天 ID |
| `WECOM_CALLBACK_CORP_ID` | 企业微信企业 Corp ID，用于回调自建应用 |
| `WECOM_CALLBACK_CORP_SECRET` | 自建应用的 Corp 密钥 |
| `WECOM_CALLBACK_AGENT_ID` | 自建应用的 Agent ID |
| `WECOM_CALLBACK_TOKEN` | 回调验证令牌 |
| `WECOM_CALLBACK_ENCODING_AES_KEY` | 回调加密的 AES 密钥 |
| `WECOM_CALLBACK_HOST` | 回调服务器绑定地址（默认：`0.0.0.0`） |
| `WECOM_CALLBACK_PORT` | 回调服务器端口（默认：`8645`） |
| `WECOM_CALLBACK_ALLOWED_USERS` | 逗号分隔的用户 ID，用于允许列表 |
| `WECOM_CALLBACK_ALLOW_ALL_USERS` | 设为 `true` 以允许所有用户，无需允许列表 |
| `WEIXIN_ACCOUNT_ID` | 通过 iLink Bot API 的二维码登录获取的微信账户 ID |
| `WEIXIN_TOKEN` | 通过 iLink Bot API 的二维码登录获取的微信认证令牌 |
| `WEIXIN_BASE_URL` | 覆盖微信 iLink Bot API 基础 URL（默认：`https://ilinkai.weixin.qq.com`） |
| `WEIXIN_CDN_BASE_URL` | 覆盖微信媒体 CDN 基础 URL（默认：`https://novac2c.cdn.weixin.qq.com/c2c`） |
| `WEIXIN_DM_POLICY` | 私聊策略：`open`、`allowlist`、`pairing`、`disabled`（默认：`open`） |
| `WEIXIN_GROUP_POLICY` | 群聊策略：`open`、`allowlist`、`disabled`（默认：`disabled`） |
| `WEIXIN_ALLOWED_USERS` | 逗号分隔的微信用户 ID，允许给机器人发私聊 |
| `WEIXIN_GROUP_ALLOWED_USERS` | 逗号分隔的微信群聊 ID（不是成员用户 ID），允许与机器人交互。变量名是旧版——它期望的是群组 ID。仅在 iLink 实际传递群组事件时生效；二维码登录的 iLink 机器人身份（`...@im.bot`）通常不会收到普通微信群消息。 |
| `WEIXIN_HOME_CHANNEL` | 用于 cron 传递和通知的微信聊天 ID |
| `WEIXIN_HOME_CHANNEL_NAME` | 微信首页频道的显示名称 |
| `WEIXIN_ALLOW_ALL_USERS` | 允许所有微信用户，无需允许列表（`true`/`false`） |
| `BLUEBUBBLES_SERVER_URL` | BlueBubbles 服务器 URL（例如 `http://192.168.1.10:1234`） |
| `BLUEBUBBLES_PASSWORD` | BlueBubbles 服务器密码 |
| `BLUEBUBBLES_WEBHOOK_HOST` | Webhook 监听器绑定地址（默认：`127.0.0.1`） |
| `BLUEBUBBLES_WEBHOOK_PORT` | Webhook 监听器端口（默认：`8645`） |
| `BLUEBUBBLES_HOME_CHANNEL` | 用于 cron/通知传递的电话/电子邮件 |
| `BLUEBUBBLES_ALLOWED_USERS` | 逗号分隔的授权用户 |
| `BLUEBUBBLES_ALLOW_ALL_USERS` | 允许所有用户（`true`/`false`） |
| `QQ_APP_ID` | 来自 [q.qq.com](https://q.qq.com) 的 QQ 机器人 App ID |
| `QQ_CLIENT_SECRET` | 来自 [q.qq.com](https://q.qq.com) 的 QQ 机器人 App Secret |
| `QQ_STT_API_KEY` | 外部 STT 回退提供者的 API 密钥（可选，当 QQ 内置 ASR 不返回文本时使用） |
| `QQ_STT_BASE_URL` | 外部 STT 提供者的基础 URL（可选） |
| `QQ_STT_MODEL` | 外部 STT 提供者的模型名称（可选） |
| `QQ_ALLOWED_USERS` | 逗号分隔的 QQ 用户 openID，允许给机器人发消息 |
| `QQ_GROUP_ALLOWED_USERS` | 逗号分隔的 QQ 群组 ID，用于群 @-消息访问 |
| `QQ_ALLOW_ALL_USERS` | 允许所有用户（`true`/`false`，覆盖 `QQ_ALLOWED_USERS`） |
| `QQBOT_HOME_CHANNEL` | 用于 cron 传递和通知的 QQ 用户/群组 openID |
| `QQBOT_HOME_CHANNEL_NAME` | QQ 首页频道的显示名称 |
| `QQ_PORTAL_HOST` | 覆盖 QQ 门户主机（设为 `sandbox.q.qq.com` 以通过沙箱网关路由；默认：`q.qq.com`）。 |
| `MATTERMOST_URL` | Mattermost 服务器 URL（例如 `https://mm.example.com`） |
| `MATTERMOST_TOKEN` | Mattermost 的机器人令牌或个人访问令牌 |
| `MATTERMOST_ALLOWED_USERS` | 逗号分隔的 Mattermost 用户 ID，允许给机器人发消息 |
| `MATTERMOST_HOME_CHANNEL` | 用于主动消息传递（cron、通知）的频道 ID |
| `MATTERMOST_REQUIRE_MENTION` | 在频道中需要 `@提及`（默认：`true`）。设为 `false` 以响应所有消息。 |
| `MATTERMOST_FREE_RESPONSE_CHANNELS` | 逗号分隔的频道 ID，机器人无需 `@提及` 即可回复 |
| `MATTERMOST_REPLY_MODE` | 回复样式：`thread`（线程回复）或 `off`（平面消息，默认） |
| `MATRIX_HOMESERVER` | Matrix 家庭服务器 URL（例如 `https://matrix.org`） |
| `MATRIX_ACCESS_TOKEN` | 用于机器人认证的 Matrix 访问令牌 |
| `MATRIX_USER_ID` | Matrix 用户 ID（例如 `@hermes:matrix.org`）——密码登录必需，访问令牌可选 |
| `MATRIX_PASSWORD` | Matrix 密码（替代访问令牌） |
| `MATRIX_ALLOWED_USERS` | 逗号分隔的 Matrix 用户 ID，允许给机器人发消息（例如 `@alice:matrix.org`） |
| `MATRIX_ALLOWED_ROOMS` | 逗号分隔的 Matrix 房间 ID，允许触发机器人回复 |
| `MATRIX_HOME_ROOM` | 用于主动消息传递的房间 ID（例如 `!abc123:matrix.org`） |
| `MATRIX_ENCRYPTION` | 启用端到端加密（`true`/`false`，默认：`false`） |
| `MATRIX_E2EE_MODE` | Matrix E2EE 行为：`off`、`optional` 或 `required`。设置时覆盖 `MATRIX_ENCRYPTION`。 |
| `MATRIX_DEVICE_ID` | 稳定的 Matrix 设备 ID，用于跨重启保持 E2EE 持久性（例如 `HERMES_BOT`）。没有此设置，E2EE 密钥会在每次启动时轮换，历史房间解密会失败。 |
| `MATRIX_REACTIONS` | 在入站消息上启用处理生命周期表情反应（默认：`true`）。设为 `false` 可禁用。 |
| `MATRIX_REQUIRE_MENTION` | 在房间中需要 `@提及`（默认：`true`）。设为 `false` 以响应所有消息。 |
| `MATRIX_FREE_RESPONSE_ROOMS` | 逗号分隔的房间 ID，机器人无需 `@提及` 即可回复 |
| `MATRIX_IGNORE_USER_PATTERNS` | 逗号分隔的正则表达式，用于忽略 Matrix 桥接器/应用服务幽灵用户 ID |
| `MATRIX_PROCESS_NOTICES` | 处理入站 Matrix `m.notice` 事件（默认：`false`） |
| `MATRIX_SESSION_SCOPE` | 项目房间的 Matrix 会话作用域：`auto`、`room` 或 `thread`（默认：`auto`） |
| `MATRIX_TOOLS_ALLOW_CROSS_ROOM` | 允许 Matrix 工具定位当前房间以外的显式房间（默认：`false`） |
| `MATRIX_TOOLS_ALLOW_CROSS_ROOM_DESTRUCTIVE` | 允许跨房间的 Matrix 编辑/邀请类工具；需要 `MATRIX_TOOLS_ALLOW_CROSS_ROOM=true`（默认：`false`） |
| `MATRIX_TOOLS_ALLOW_REDACTION` | 允许执行 Matrix 消息编辑工具（默认：`false`） |
| `MATRIX_TOOLS_ALLOW_INVITES` | 允许执行 Matrix 邀请工具（默认：`false`） |
| `MATRIX_TOOLS_ALLOW_ROOM_CREATE` | 允许执行 Matrix 房间创建工具（默认：`false`） |
| `MATRIX_ALLOW_ROOM_MENTIONS` | 允许出站 `@room` 提及以通知所有房间成员（默认：`false`） |
| `MATRIX_AUTO_THREAD` | 为房间消息自动创建线程（默认：`true`） |
| `MATRIX_DM_MENTION_THREADS` | 在私聊中机器人被 `@提及` 时创建线程（默认：`false`） |
| `MATRIX_APPROVAL_REQUIRE_SENDER` | 要求批准/模型选择器反应来自已知的原始请求者（默认：`true`） |
| `MATRIX_APPROVAL_TIMEOUT_SECONDS` | Matrix 反应批准/模型选择器提示的超时时间（默认：`300`） |
| `MATRIX_ALLOW_PUBLIC_ROOMS` | 允许 Matrix 房间创建工具创建公共房间（默认：`false`） |
| `MATRIX_MAX_MEDIA_BYTES` | Matrix 媒体上传/下载的最大字节数（默认：`104857600`） |
| `MATRIX_RECOVERY_KEY` | 设备密钥轮换后用于交叉签名验证的恢复密钥。推荐用于启用了交叉签名的 E2EE 设置。 |
| `MATRIX_RECOVERY_KEY_OUTPUT_FILE` | 可选的一次性路径，用于生成的 Matrix 恢复密钥。使用权限 `0600` 创建，且从不覆盖。 |
| `HASS_TOKEN` | Home Assistant 长期访问令牌（启用 HA 平台 + 工具） |
| `HASS_URL` | Home Assistant URL（默认：`http://homeassistant.local:8123`） |
| `WEBHOOK_ENABLED` | 启用 webhook 平台适配器（`true`/`false`） |
| `WEBHOOK_PORT` | 接收 webhook 的 HTTP 服务器端口（默认：`8644`） |
| `WEBHOOK_SECRET` | 全局 HMAC 密钥，用于 webhook 签名验证（当路由未指定自己的密钥时作为回退使用） |
| `API_SERVER_ENABLED` | 启用 OpenAI 兼容的 API 服务器（`true`/`false`）。与其他平台一起运行。 |
| `API_SERVER_KEY` | API 服务器认证的 Bearer 令牌。API 服务器启用时必需。 |
| `API_SERVER_CORS_ORIGINS` | 逗号分隔的浏览器来源，允许直接调用 API 服务器（例如 `http://localhost:3000,http://127.0.0.1:3000`）。默认：禁用。 |
| `API_SERVER_PORT` | API 服务器的端口（默认：`8642`） |
| `API_SERVER_HOST` | API 服务器的主机/绑定地址（默认：`127.0.0.1`）。回环地址上仍需要 `API_SERVER_KEY`；对于浏览器访问，请使用窄范围的 `API_SERVER_CORS_ORIGINS` 允许列表。 |
| `API_SERVER_MODEL_NAME` | 在 `/v1/models` 上通告的模型名称。默认为配置文件名称（对于默认配置文件为 `hermes-agent`）。对于多用户设置，像 Open WebUI 这样的前端需要每个连接有一个不同的模型名称，此设置很有用。 |
| `GATEWAY_PROXY_URL` | 远程 Hermes API 服务器的 URL，用于转发消息（[代理模式](/user-guide/messaging/matrix#proxy-mode-e2ee-on-macos)）。设置后，网关仅处理平台 I/O——所有代理工作都委托给远程服务器。也可通过 `config.yaml` 中的 `gateway.proxy_url` 配置。 |
| `GATEWAY_PROXY_KEY` | 在代理模式下与远程 API 服务器进行认证的 Bearer 令牌。必须与远程主机上的 `API_SERVER_KEY` 匹配。 |
| `MESSAGING_CWD` | 已弃用。网关工作目录的兼容性回退。优先使用 `config.yaml` 中的 `terminal.cwd`。 |
| `GATEWAY_ALLOWED_USERS` | 逗号分隔的用户 ID，允许跨所有平台使用 |
| `GATEWAY_ALLOW_ALL_USERS` | 允许所有用户，无需允许列表（`true`/`false`，默认：`false`） |

### Web 仪表盘和 Hermes Desktop

用于 [Web 仪表盘](/user-guide/features/web-dashboard) 以及将 [Hermes Desktop 连接到远程后端](/user-guide/features/web-dashboard#connecting-hermes-desktop-to-a-remote-backend) 的认证。按照仅限密钥的约定，凭据应放在 `~/.hermes/.env` 中；OAuth `client_id` 最好在 `config.yaml` 的 `dashboard.oauth` 下设置（环境变量优先）。

内置三个仪表盘认证提供者。对于远程 Hermes Desktop 连接或面向互联网的仪表盘，推荐的提供者是 **OAuth (Nous Portal)**——设置 `HERMES_DASHBOARD_OAUTH_CLIENT_ID`（使用 `hermes dashboard register` 配置）。内置的**用户名/密码**提供者（`HERMES_DASHBOARD_BASIC_AUTH_*`）是最快捷的选项，适用于受信任 LAN 或 VPN 后的后端，但不适合直接暴露在公共互联网上。要针对您自己的身份提供者进行认证，请使用**自托管 OIDC** 提供者（`HERMES_DASHBOARD_OIDC_*`）。无论哪种方式，非回环绑定（`hermes dashboard --host 0.0.0.0`）都会启用认证门控。完整详情请参阅 [Web 仪表盘 → 认证](/user-guide/features/web-dashboard#authentication-gated-mode)。

| 变量 | 描述 |
|----------|-------------|
| `HERMES_DASHBOARD_BASIC_AUTH_USERNAME` | 内置用户名/密码仪表盘认证提供者（`plugins/dashboard_auth/basic`）的用户名。与密码同时设置时激活该提供者。覆盖 `dashboard.basic_auth.username`。 |
| `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD` | 基础提供者的明文密码（加载时在内存中哈希化）。优先于配置中的 `password_hash`，因此你可以通过环境变量轮换密码。覆盖 `dashboard.basic_auth.password`。 |
| `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD_HASH` | 基础提供者的 scrypt 密码哈希（推荐——静态时不保留明文）。使用 `python -c "from plugins.dashboard_auth.basic import hash_password; print(hash_password('PW'))"` 计算。覆盖 `dashboard.basic_auth.password_hash`。 |
| `HERMES_DASHBOARD_BASIC_AUTH_SECRET` | HMAC 密钥（32+ 字节，base64/hex/raw），用于签署基础提供者的无状态会话令牌。显式设置后，会话可在重启后继续存在或跨多个工作进程共享；空白 = 每个进程随机生成（每次重启都会登出）。覆盖 `dashboard.basic_auth.secret`。 |
| `HERMES_DASHBOARD_BASIC_AUTH_TTL_SECONDS` | 基础提供者的访问令牌生存时间（默认 12 小时）。覆盖 `dashboard.basic_auth.session_ttl_seconds`。 |
| `HERMES_DASHBOARD_OAUTH_CLIENT_ID` | OAuth 客户端 ID（`agent:{instance_id}`），用于门控/公共仪表盘，激活 Nous（`plugins/dashboard_auth/nous`）提供者。覆盖 `dashboard.oauth.client_id`。使用 `hermes dashboard register` 配置。 |
| `HERMES_DASHBOARD_PUBLIC_URL` | 仪表盘可访问的完整公共 URL，用于反向代理后的 OAuth 回调构建。覆盖 `dashboard.public_url`。 |
| `HERMES_DASHBOARD_OIDC_ISSUER` | 内置自托管 OIDC 提供者（`plugins/dashboard_auth/self_hosted`）的 OIDC 发行者 URL。激活该提供者必需。覆盖 `dashboard.oauth.self_hosted.issuer`。 |
| `HERMES_DASHBOARD_OIDC_CLIENT_ID` | 自托管 OIDC 提供者的公共 OIDC 客户端 ID（授权码 + PKCE）。激活该提供者必需。覆盖 `dashboard.oauth.self_hosted.client_id`。 |
| `HERMES_DASHBOARD_OIDC_SCOPES` | 自托管 OIDC 提供者请求的 OIDC 作用域（默认 `openid profile email`）。覆盖 `dashboard.oauth.self_hosted.scopes`。 |
| `HERMES_DESKTOP_REMOTE_URL` | （桌面端）远程后端的 Base URL，例如 `http://host:9119`。设置后，覆盖应用内的网关 URL；你仍然需要从网关设置面板登录（OAuth 重定向或用户名/密码，取决于后端通告的类型）。 |
| `HERMES_DESKTOP_HERMES` | 桌面后端命令覆盖。由打包器/Nix 或在故障排除时使用，用于在后端探测后将 Electron 指向特定的 `hermes` 可执行文件。 |
| `HERMES_DESKTOP_HERMES_ROOT` | 桌面源代码检出覆盖，由 `hermes desktop --hermes-root` 使用；在打包的首次启动安装或 `PATH` 上已有的 `hermes` 之前检查。 |
| `HERMES_DESKTOP_IGNORE_EXISTING` | 设为 `1` 使桌面在后端解析期间忽略 `PATH` 上已有的 `hermes`。等同于 `hermes desktop --ignore-existing`。 |
| `HERMES_DESKTOP_CWD` | 桌面聊天会话的初始项目目录。由 `hermes desktop --cwd` 设置。 |

### Microsoft Graph (Teams 会议)

用于即将推出的 Teams 会议摘要管道的 Microsoft Graph REST 客户端的应用级凭据。请参阅[注册 Microsoft Graph 应用程序](/guides/microsoft-graph-app-registration) 了解 Azure 门户的逐步操作以及所需的确切 API 权限。

| 变量 | 描述 |
|----------|-------------|
| `MSGRAPH_TENANT_ID` | Graph 应用注册的 Azure AD 租户 ID（目录 GUID）。 |
| `MSGRAPH_CLIENT_ID` | Azure 应用注册的应用程序（客户端）ID。 |
| `MSGRAPH_CLIENT_SECRET` | 应用注册的客户端密钥值。存储在 `~/.hermes/.env` 中并设置 `chmod 600`；定期通过 Azure 门户轮换。 |
| `MSGRAPH_SCOPE` | 客户端凭据令牌请求的 OAuth2 作用域（默认：`https://graph.microsoft.com/.default`）。 |
| `MSGRAPH_AUTHORITY_URL` | Microsoft 标识平台授权机构（默认：`https://login.microsoftonline.com`）。仅在国家/主权云中覆盖（例如 GCC High 使用 `https://login.microsoftonline.us`）。 |

### Microsoft Graph Webhook 监听器

Graph 事件（Teams 会议、日历、聊天等）的入站变更通知监听器。请参阅 [Microsoft Graph Webhook 监听器](/user-guide/messaging/msgraph-webhook) 了解设置和安全强化。

| 变量 | 描述 |
|----------|-------------|
| `MSGRAPH_WEBHOOK_ENABLED` | 启用 `msgraph_webhook` 网关平台（`true`/`1`/`yes`）。 |
| `MSGRAPH_WEBHOOK_PORT` | 监听器绑定的端口（默认：`8646`）。 |
| `MSGRAPH_WEBHOOK_CLIENT_STATE` | Graph 在每个通知中回显的共享密钥；与 `hmac.compare_digest` 比较