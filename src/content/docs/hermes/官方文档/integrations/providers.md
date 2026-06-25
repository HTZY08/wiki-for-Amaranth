--- frontmatter ---
---

### 选择合适的设置

| 使用场景 | 推荐方案 |
|----------|----------|
| **只想开箱即用** | OpenRouter（默认）或 Nous Portal |
| **本地模型，简单配置** | Ollama |
| **生产环境 GPU 服务** | vLLM 或 SGLang |
| **Mac / 无 GPU** | Ollama 或 llama.cpp |
| **多提供商路由** | LiteLLM Proxy 或 OpenRouter |
| **成本优化** | ClawRouter 或 OpenRouter（使用 `sort: "price"`） |
| **最大隐私** | Ollama、vLLM 或 llama.cpp（完全本地） |
| **企业 / Azure** | 使用自定义端点的 Azure OpenAI |
| **中文 AI 模型** | z.ai (GLM)、Kimi/Moonshot（`kimi-coding` 或 `kimi-coding-cn`）、MiniMax、小米 MiMo 或腾讯 TokenHub（一级提供商） |

:::tip
你可以随时使用 `hermes model` 切换提供商——无需重启。无论使用哪个提供商，你的对话历史、记忆和技能都会保留。
:::

## 可选的 API 密钥

| 功能 | 提供商 | 环境变量 |
|------|--------|----------|
| 网页抓取 | [Firecrawl](https://firecrawl.dev/) | `FIRECRAWL_API_KEY`、`FIRECRAWL_API_URL` |
| 浏览器自动化 | [Browserbase](https://browserbase.com/) | `BROWSERBASE_API_KEY`、`BROWSERBASE_PROJECT_ID` |
| 图像生成 | [FAL](https://fal.ai/) | `FAL_KEY` |
| 高级 TTS 语音 | [ElevenLabs](https://elevenlabs.io/) | `ELEVENLABS_API_KEY` |
| OpenAI TTS + 语音转录 | [OpenAI](https://platform.openai.com/api-keys) | `VOICE_TOOLS_OPENAI_KEY` |
| Mistral TTS + 语音转录 | [Mistral](https://console.mistral.ai/) | `MISTRAL_API_KEY` |
| 跨会话用户建模 | [Honcho](https://honcho.dev/) | `HONCHO_API_KEY` |
| 语义长期记忆 | [Supermemory](https://supermemory.ai) | `SUPERMEMORY_API_KEY` |

### 自托管 Firecrawl

默认情况下，Hermes 使用 [Firecrawl 云 API](https://firecrawl.dev/) 进行网络搜索和抓取。如果你更想在本地运行 Firecrawl，可以将 Hermes 指向自托管实例。请参阅 Firecrawl 的 [SELF_HOST.md](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) 获取完整的设置说明。

**优点：** 无需 API 密钥、无速率限制、无按页计费、完全数据主权。

**缺点：** 云版本使用 Firecrawl 专有的“Fire-engine”进行高级反机器人绕过（Cloudflare、验证码、IP 轮换）。自托管版本使用基本的 fetch + Playwright，因此某些受保护的网站可能失败。搜索使用 DuckDuckGo 而非 Google。

**设置步骤：**

1. 克隆并启动 Firecrawl Docker 堆栈（5 个容器：API、Playwright、Redis、RabbitMQ、PostgreSQL——需约 4-8 GB 内存）：
   ```bash
   git clone https://github.com/firecrawl/firecrawl
   cd firecrawl
   # 在 .env 中设置：USE_DB_AUTHENTICATION=false, HOST=0.0.0.0, PORT=3002
   docker compose up -d
   ```

2. 将 Hermes 指向你的实例（无需 API 密钥）：
   ```bash
   hermes config set FIRECRAWL_API_URL http://localhost:3002
   ```

如果你的自托管实例启用了身份验证，你也可以同时设置 `FIRECRAWL_API_KEY` 和 `FIRECRAWL_API_URL`。

## OpenRouter 提供商路由

使用 OpenRouter 时，你可以控制请求如何在各个提供商之间路由。在 `~/.hermes/config.yaml` 中添加一个 `provider_routing` 部分：

```yaml
provider_routing:
  sort: "throughput"          # "price"（默认）、"throughput" 或 "latency"
  # only: ["anthropic"]      # 仅使用这些提供商
  # ignore: ["deepinfra"]    # 跳过这些提供商
  # order: ["anthropic", "google"]  # 按此顺序尝试提供商
  # require_parameters: true  # 仅使用支持所有请求参数的提供商
  # data_collection: "deny"   # 排除可能存储/训练数据的提供商
```

**快捷方式：** 在任何模型名称后添加 `:nitro` 表示按吞吐量排序（例如 `anthropic/claude-sonnet-4:nitro`），或添加 `:floor` 表示按价格排序。

## OpenRouter Pareto Code 路由器

OpenRouter 在 `openrouter/pareto-code` 提供一个实验性的编码模型路由器，它会自动将请求路由到符合编码质量门槛的最便宜模型（由 [Artificial Analysis](https://artificialanalysis.ai/) 排名）。选择此模型并在 `~/.hermes/config.yaml` 中调整 `min_coding_score` 参数：

```yaml
model:
  provider: openrouter
  model: openrouter/pareto-code

openrouter:
  min_coding_score: 0.65   # 0.0–1.0；值越高 = 编码能力越强（也更贵）。默认值 0.65。
```

注意事项：

- `min_coding_score` **仅**在 `model.model` 为 `openrouter/pareto-code` 时发送。使用任何其他模型时该值无效。
- 如果将该值设为空字符串（或删除该行），则让 OpenRouter 选择当前可用的最强编码模型——这是文档中省略插件块时的行为。
- 对于给定的分数，选择在一天内是确定的，但实际选中的模型可能随着帕累托前沿的变化（新模型、基准更新）而发生变动。
- 有关完整的路由器行为，请参阅 OpenRouter 的 [Pareto 路由器文档](https://openrouter.ai/docs/guides/routing/routers/pareto-router)。
- 如果要对某个**辅助任务**（压缩、视觉等）而不是主代理使用 Pareto Code 路由器，请在该任务下设置 `extra_body.plugins`——参见[辅助模型 → OpenRouter 路由及用于辅助任务的 Pareto Code](/user-guide/configuration#openrouter-routing--pareto-code-for-auxiliary-tasks)。

## 回退提供商（Fallback Providers）

配置一个后备提供商链，当主模型失败（速率限制、服务器错误、身份验证失败）时，Hermes 会按顺序尝试这些提供商。规范的格式是顶层 `fallback_providers:` 列表：

```yaml
fallback_providers:
  - provider: openrouter
    model: anthropic/claude-sonnet-4
  - provider: anthropic
    model: claude-sonnet-4
    # base_url: http://localhost:8000/v1    # 可选，用于自定义端点
    # api_mode: chat_completions           # 可选覆盖
```

为保持向后兼容，仍然接受旧的单对 `fallback_model:` 字典形式：

```yaml
fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
```

激活时，回退会在会话中切换模型和提供商，不会丢失你的对话。链按条目逐一尝试；激活是一次性的，每个会话只有一次。

支持的提供商：`openrouter`、`nous`、`novita`、`openai-codex`、`copilot`、`copilot-acp`、`anthropic`、`gemini`、`qwen-oauth`、`huggingface`、`zai`、`kimi-coding`、`kimi-coding-cn`、`minimax`、`minimax-cn`、`minimax-oauth`、`deepseek`、`nvidia`、`xai`、`xai-oauth`、`ollama-cloud`、`bedrock`、`azure-foundry`、`opencode-zen`、`opencode-go`、`kilocode`、`xiaomi`、`arcee`、`gmi`、`stepfun`、`lmstudio`、`alibaba`、`alibaba-coding-plan`、`tencent-tokenhub`、`custom`。

:::tip
回退的配置完全通过 `config.yaml` 完成——也可以交互式地通过 `hermes fallback` 进行。有关触发条件、链如何推进以及与辅助任务和委托的交互的详细信息，请参阅[回退提供商](/user-guide/features/fallback-providers)。
:::

---

--- body ---
## 另请参阅

- [配置](/user-guide/configuration) — 常规配置（目录结构、配置优先级、终端后端、内存、压缩等）
- [环境变量](/reference/environment-variables) — 所有环境变量的完整参考