--- frontmatter ---

# Nous 工具网关

**一份订阅。集成所有内置工具。**

工具网关包含在每个付费 [Nous 门户](https://portal.nousresearch.com) 订阅中。它通过 Nous 已经运行的基础设施路由 Hermes 的工具调用——网络搜索、图像生成、文本转语音和云端浏览器自动化——因此您无需为了使用代理而分别注册 Firecrawl、FAL、OpenAI、Browser Use 或其他任何服务。

<div style={{display: 'flex', gap: '1rem', flexWrap: 'wrap', margin: '1.5rem 0'}}>
  <a href="https://portal.nousresearch.com/manage-subscription" style={{background: 'var(--ifm-color-primary)', color: 'white', padding: '0.75rem 1.5rem', borderRadius: '6px', textDecoration: 'none', fontWeight: 'bold'}}>开始或管理订阅 →</a>
</div>

## 包含内容

| | 工具 | 您将获得 |
|---|---|---|
| 🔍 | **网络搜索与提取** | 通过 Firecrawl 实现代理级网络搜索和整页提取。无需担心频率限制——网关会自动处理扩展。 |
| 🎨 | **图像生成** | 一个端点下支持九种模型：**FLUX 2 Klein 9B**、**FLUX 2 Pro**、**Z-Image Turbo**、**Nano Banana Pro** (Gemini 3 Pro Image)、**GPT Image 1.5**、**GPT Image 2**、**Ideogram V3**、**Recraft V4 Pro**、**Qwen Image**。通过标志按次选择模型，或让 Hermes 默认使用 FLUX 2 Klein。 |
| 🔊 | **文本转语音** | OpenAI TTS 语音已接入 `text_to_speech` 工具。将语音笔记发送到 Telegram、为流水线生成音频、或为任何内容配音。 |
| 🌐 | **云端浏览器自动化** | 通过 Browser Use 实现无头 Chromium 会话。`browser_navigate`、`browser_click`、`browser_type`、`browser_vision`——所有代理驱动原语，无需 Browserbase 账户。 |

上述四项均为按使用量付费，从您的 Nous 订阅中扣除。您可以使用任意组合——例如，通过网关进行网络和图像操作，同时保留您自己的 ElevenLabs 密钥用于 TTS，或者将所有操作都通过 Nous 路由。

## 为什么存在

构建一个真正能*做事*的代理意味着要整合 5 个以上的 API 订阅——每个都有独立的注册、频率限制、计费和特性。网关将这些合并为一个账户：

- **一份账单。** 向 Nous 付费；其余我们处理。
- **一次注册。** 无需管理 Firecrawl、FAL、Browser Use 或 OpenAI 音频账户。
- **一个密钥。** 您的 Nous 门户 OAuth 涵盖所有工具。
- **相同质量。** 与直接密钥路由使用相同的后端——只是由我们前置。

您可以随时使用自己的密钥——按工具单独使用。网关不是锁定，而是一种捷径。

## 快速开始

有三种接入方式——选择适合您当前情况的一种：

```bash
hermes setup --portal     # 全新安装：一步完成 Nous OAuth + 将 Nous 设为提供商 + 开启工具网关
```

```bash
hermes model              # 将您的推理提供商切换为 Nous 门户 — Hermes 随后会询问是否开启所有工具网关
```

```bash
hermes tools              # 按工具启用网关 — 为任何您想要的工具选择 "Nous Subscription"
```

`hermes setup --portal` 和 `hermes model` 是全量路径：登录一次，可选将所有工具切换到网关。`hermes tools` 是按需路径——一次只开启您想要的工具。

**您无需先登录。** 使用 `hermes tools` 时，Nous 托管的后端（网络搜索、图像、视频、TTS、浏览器）始终列出，即使您从未登录过 Nous 门户。选择一个后，如果您尚未认证，Hermes 会立即运行门户登录——无需事先运行 `hermes model`。如果您的 Nous OAuth 已经激活，选择后端会立即启用，无需额外提示。此路径仅登录并开启您选择的那个工具——它**不会**切换您的推理提供商，也**不会**提示您为所有其他工具启用网关。

随时查看当前激活状态：

```bash
hermes portal info        # 门户认证 + 工具网关路由摘要
hermes portal tools       # 网关目录，显示每个工具的当前路由
hermes status             # 完整系统状态（工具网关是其中一个部分）
```

`hermes portal info` 会显示类似以下部分：

```
◆ Nous 工具网关
  Nous 门户     ✓ 托管工具可用
  网络工具       ✓ 通过 Nous 订阅激活
  图像生成       ✓ 通过 Nous 订阅激活
  TTS           ✓ 通过 Nous 订阅激活
  浏览器         ○ 通过 Browser Use 密钥激活
```

标记为“通过 Nous 订阅激活”的工具正在通过网关路由。其他工具则使用您自己的密钥。

## 资格

工具网关是一项**付费订阅**功能。免费层级的 Nous 账户可以使用门户进行推理，但不包含托管工具——[升级您的计划](https://portal.nousresearch.com/manage-subscription) 以解锁网关。

某些账户还有权享受**免费工具池**——一个小的托管工具配额，无需付费订阅即可覆盖网关工具调用。当免费池可用时，网关会显示它，并在首次使用时显示设置提示，以便您选择加入并立即开始使用托管工具。

## 混合搭配

网关是按工具启用的。只为您想要的工具开启它：

- **所有工具通过 Nous** — 最简单；一个订阅，搞定。
- **网关用于网络 + 图像，自带 TTS** — 保留您的 ElevenLabs 语音，其余由 Nous 处理。
- **网关仅用于您没有密钥的部分** — “我已经付费使用 Browserbase，但我不想注册 Firecrawl 账户”这种情况完全可行。

随时通过以下命令切换任何工具：

```bash
hermes tools          # 每个工具类别的交互式选择器
```

选择工具，选择 **Nous Subscription** 作为提供商（或您更喜欢的任何直接提供商）。无需编辑配置。如果您尚未登录 Nous 门户，选择 **Nous Subscription** 会立即启动门户内联登录——您无需先通过 `hermes model` 进行认证。

## 使用单独的图像模型

图像生成默认使用 FLUX 2 Klein 9B 以提升速度。您可以通过将模型 ID 传递给 `image_generate` 工具来覆盖每次调用的模型：

| 模型 | ID | 最佳用途 |
|---|---|---|
| FLUX 2 Klein 9B | `fal-ai/flux-2/klein/9b` | 快速，良好的默认选项 |
| FLUX 2 Pro | `fal-ai/flux-2-pro` | 高保真度的 FLUX |
| Z-Image Turbo | `fal-ai/z-image/turbo` | 风格化，快速 |
| Nano Banana Pro | `fal-ai/nano-banana-pro` | Google Gemini 3 Pro Image |
| GPT Image 1.5 | `fal-ai/gpt-image-1.5` | OpenAI 图像生成，支持文本+图像 |
| GPT Image 2 | `fal-ai/gpt-image-2` | OpenAI 最新版本 |
| Ideogram V3 | `fal-ai/ideogram/v3` | 强提示遵循 + 字体设计 |
| Recraft V4 Pro | `fal-ai/recraft/v4/pro/text-to-image` | 矢量风格，图形设计 |
| Qwen Image | `fal-ai/qwen-image` | 阿里巴巴多模态模型 |

集合会不断更新——运行 `hermes tools` → 图像生成可查看当前实时列表。

---

--- body ---
## 配置参考

大多数用户无需接触此部分——`hermes model` 和 `hermes tools` 已交互式覆盖所有工作流程。此部分适用于直接编写 config.yaml 或脚本化设置。

### 按工具设置 `use_gateway` 标志

每个工具的配置块接受一个 `use_gateway` 布尔值：

```yaml
web:
  backend: firecrawl
  use_gateway: true

image_gen:
  use_gateway: true

tts:
  provider: openai
  use_gateway: true

browser:
  cloud_provider: browser-use
  use_gateway: true
```

优先级：`use_gateway: true` 会通过 Nous 路由，无论 `.env` 中是否有直接密钥。`use_gateway: false`（或缺失）则优先使用直接密钥（如果存在），仅在无密钥时回退到网关。

### 禁用网关

```yaml
web:
  use_gateway: false   # Hermes 现在使用 .env 中的 FIRECRAWL_API_KEY
```

`hermes tools` 在您选择非网关提供商时会自动清除该标志，因此通常这对您自动生效。

### 自托管网关（高级）

运行您自己的兼容 Nous 的网关？在 `~/.hermes/.env` 中覆盖端点：

```bash
TOOL_GATEWAY_DOMAIN=your-domain.example.com
TOOL_GATEWAY_SCHEME=https
TOOL_GATEWAY_USER_TOKEN=your-token        # 通常从门户登录自动填充
FIRECRAWL_GATEWAY_URL=https://...         # 单独覆盖一个端点
```

这些设置项用于自定义基础设施环境（企业部署、开发环境）。普通订阅者无需设置。

## 常见问题

### 它与 Telegram / Discord / 其他消息网关兼容吗？

是的。工具网关在工具执行层运行，而非 CLI。任何能够调用工具的接口——CLI、Telegram、Discord、Slack、IRC、Teams、API 服务器等——都能透明地受益。

### 如果我的订阅过期会怎样？

通过网关路由的工具将停止工作，直到您续费或通过 `hermes tools` 替换为直接 API 密钥。Hermes 会显示一个明确的错误，指向门户。

### 我可以查看每个工具的使用量或成本吗？

可以——[Nous 门户仪表盘](https://portal.nousresearch.com) 按工具细分使用情况，让您了解驱动账单的因素。

### Modal（无服务器终端）包含在内吗？

Modal 作为**可选附加组件**通过 Nous 订阅提供，不属于默认工具网关包的一部分。当您需要用于 shell 执行的远程沙箱时，可通过 `hermes setup terminal` 或直接在 `config.yaml` 中配置。

### 启用网关后，我需要删除现有的 API 密钥吗？

不需要——将它们保留在 `.env` 中。当 `use_gateway: true` 时，Hermes 会跳过直接密钥并使用网关。将标志改回 `false`，您的密钥将再次成为来源。网关不是锁定。