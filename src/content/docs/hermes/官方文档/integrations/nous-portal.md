--- frontmatter ---
---
sidebar_position: 1
title: "Nous Portal"
description: "一个订阅，300+前沿模型，工具网关和Nous Chat——运行 Hermes Agent 的推荐方式"
---

--- body ---

# Nous Portal

[Nous Portal](https://portal.nousresearch.com) 是 Nous Research 的统一订阅网关，也是 **运行 Hermes Agent 的推荐方式**。一个 OAuth 登录即可取代跨多个模型实验室、搜索 API、图像生成器和浏览器提供商的独立账户、API 密钥和计费关系的繁琐操作，否则您需要手动逐一配置。

如果您只能设置一项，那就设置这个。最快的路径：

```bash
hermes setup --portal
```

这一条命令会运行 Portal OAuth，让您选择一个 Nous 模型，在 `config.yaml` 中将 Nous 设置为推理提供商，并开启工具网关。之后您就可以立即运行 `hermes chat`。

还没有订阅？前往 [portal.nousresearch.com/manage-subscription](https://portal.nousresearch.com/manage-subscription) — 注册，然后回来运行上面的命令。

## 订阅包含的内容

### 300+ 前沿模型，一张账单

Portal 代理了来自整个生态系统的精选可智能体模型目录——费用计入您的 Nous 订阅，而不是每个实验室的单独信用余额。

| 系列 | 模型 |
|--------|--------|
| **Anthropic Claude** | Opus 4.7, Opus 4.6, Sonnet 4.6, Haiku 4.5 |
| **OpenAI** | GPT-5.5, GPT-5.5 Pro, GPT-5.4 Mini, GPT-5.4 Nano, GPT-5.3 Codex |
| **Google Gemini** | Gemini 3 Pro Preview, Gemini 3 Flash Preview, Gemini 3.1 Pro Preview, Gemini 3.1 Flash Lite Preview |
| **DeepSeek** | DeepSeek V4 Pro |
| **Qwen** | Qwen3.7-Max, Qwen3.6-35B-A3B |
| **Kimi / Moonshot** | Kimi K2.6 |
| **GLM / Zhipu** | GLM-5.1 |
| **MiniMax** | MiniMax M2.7 |
| **xAI** | Grok 4.3 |
| **NVIDIA** | Nemotron-3 Super 120B-A12B |
| **Tencent** | Hunyuan 3 Preview |
| **Xiaomi** | MiMo V2.5 Pro |
| **StepFun** | Step 3.5 Flash |
| **Hermes** | Hermes-4-70B, Hermes-4-405B（聊天，参见[下面的备注](#关于-hermes-4-的说明)） |
| **+ 其他所有** | 280+ 其他模型——完整的智能体前沿 |

路由通过底层 OpenRouter 完成，因此模型可用性和故障转移行为与使用 OpenRouter 密钥时一致——只是费用计入您的 Nous 订阅。在会话中使用 `/model` 可以在 Claude Sonnet 4.6（用于代码）和 Gemini 3 Pro（用于长上下文）之间切换——无需新的凭据、无需充值、不会出现意外的零余额错误。

### Nous 工具网关

同一个订阅可以解锁[工具网关](/user-guide/features/tool-gateway)，该网关将 Hermes Agent 的工具调用路由到 Nous 管理的基础设施。五个后端，一次登录：

| 工具 | 合作伙伴 | 功能 |
|------|---------|--------------|
| **网页搜索与提取** | Firecrawl | 智能体级搜索和整页提取。无需 Firecrawl API 密钥，无需操心速率限制。 |
| **图像生成** | FAL | 一个端点下九个模型：FLUX 2 Klein 9B, FLUX 2 Pro, Z-Image Turbo, Nano Banana Pro (Gemini 3 Pro Image), GPT Image 1.5, GPT Image 2, Ideogram V3, Recraft V4 Pro, Qwen Image。 |
| **文本转语音** | OpenAI TTS | 高质量 TTS，无需单独的 OpenAI 密钥。跨消息平台启用[语音模式](/user-guide/features/voice-mode)。 |
| **云端浏览器自动化** | Browser Use | 无头 Chromium 会话，用于 `browser_navigate`、`browser_click`、`browser_type`、`browser_vision`。无需 Browserbase 账户。 |
| **云端终端沙箱** | Modal | 无服务器终端沙箱，用于代码执行（可选附加组件）。 |

没有网关，配置每个工具需要 Firecrawl 账户、FAL 账户、Browser Use 账户、OpenAI 密钥和 Modal 账户——五个独立注册、五个独立仪表盘、五个独立充值流程。有了网关，所有工具都通过一个订阅路由。

您也可以只启用特定的网关工具（例如仅网页搜索，不启用图像生成）——参见下面的[将网关与您自己的后端混合使用](#将网关与您自己的后端混合使用)。

### Nous Chat

您的 Portal 账户还涵盖 [chat.nousresearch.com](https://chat.nousresearch.com) —— Nous Research 的网络聊天界面，具有相同的模型目录。当您不在终端前时，或进行非智能体对话工作时非常有用。

### 您的 dotfiles 中无需凭据

由于所有工具都通过一个经过 OAuth 认证的 Portal 会话路由，您无需积累一个包含十几个长期有效 API 密钥的 `.env` 文件。`~/.hermes/auth.json` 中的刷新令牌是磁盘上唯一的凭据，Hermes 在每次请求时从中生成短期 JWT——参见下面的[令牌处理](#令牌处理)。

### 跨平台一致性

[Native Windows](/user-guide/windows-native) 使得按工具设置 API 密钥成为其痛点——在 Windows 上安装 Firecrawl 账户、FAL 账户、Browser Use 账户和 OpenAI 密钥是让一个有用的智能体运行起来最麻烦的部分。Portal 订阅简化了这一点：一次 OAuth 覆盖模型和所有网关工具，因此 Windows 用户无需手动配置四个后端即可获得与 macOS/Linux 相同的体验。

## 关于 Hermes 4 的说明

Nous Research 自家的 **Hermes 4** 系列（Hermes-4-70B, Hermes-4-405B）可通过 Portal 以大幅折扣价格使用。这些是 **前沿混合推理聊天模型**——在数学、科学、指令遵循、模式遵守、角色扮演和长篇写作方面表现出色。

然而，**不建议在 Hermes Agent 内部使用它们**。Hermes 4 是为聊天和推理调优的，而非智能体依赖的快速工具调用循环。将它们用于 [Nous Chat](https://chat.nousresearch.com)、研究工作流程，或通过[订阅代理](/user-guide/features/subscription-proxy)从其他工具使用——但对于智能体工作，请从目录中选择一个前沿智能体模型：

```bash
/model anthropic/claude-sonnet-4.6     # 最佳通用智能体模型
/model openai/gpt-5.5-pro              # 强推理 + 工具调用
/model google/gemini-3-pro-preview     # 大上下文窗口
/model deepseek/deepseek-v4-pro        # 高性价比编程
```

Portal 自己的[模型信息页面](https://portal.nousresearch.com/info)也包含相同的警告，所以这不是 Hermes 侧的观点——而是 Nous Research 的官方指导。

## 设置

### 全新安装——一条命令

```bash
hermes setup --portal
```

这将一次性完成完整设置：

1. 打开您的浏览器到 portal.nousresearch.com 进行 OAuth 登录
2. 将刷新令牌存储在 `~/.hermes/auth.json`
3. 让您从精选列表中选择一个 Nous 模型（或跳过以保留当前模型）
4. 在 `~/.hermes/config.yaml` 中将 Nous 设置为推理提供商（当您选择模型时）
5. 开启工具网关（网页、图像、TTS、浏览器路由）
6. 将您带回终端，准备运行 `hermes chat`

如果您还没有订阅，请先前往 [portal.nousresearch.com/manage-subscription](https://portal.nousresearch.com/manage-subscription) 注册。

### 现有安装——将 Portal 与其他提供商一起添加

如果您已经使用 OpenRouter、Anthropic 或其他任何提供商配置了 Hermes，并且想将 Portal 添加到其中：

```bash
hermes model
# 从提供商列表中选择 "Nous Portal"
# 浏览器打开，登录，完成
```

您现有的提供商将保持配置状态。您可以在会话中使用 `/model` 或在会话之间使用 `hermes model` 切换它们——Portal 成为您可用的提供商之一，而不是唯一的一个。

### 无头 / SSH / 远程设置

OAuth 需要浏览器，但回环回调在运行 Hermes 的机器上执行。对于远程主机，请参见[通过 SSH / 远程主机进行 OAuth](/guides/oauth-over-ssh)——与任何其他基于 OAuth 的提供商（`ssh -L` 端口转发，`--manual-paste` 用于仅浏览器环境如 Cloud Shell / Codespaces）相同的模式适用于 Portal。

### 配置文件设置

如果您使用 [Hermes 配置文件](/user-guide/profiles)，Portal 刷新令牌将通过共享令牌存储自动在所有配置文件之间共享。在任何配置文件上登录一次，其他配置文件将自动获取——无需为每个配置文件重复 OAuth 流程。

## 日常使用 Portal

### 检查已配置的内容

```bash
hermes portal            # 登录 Nous Portal + 设置（一次性引导）
hermes portal info       # 登录状态、订阅信息、模型 + 网关路由
hermes portal status     # `portal info` 的别名
hermes portal tools      # 详细的工具网关目录，包含每个工具的路由
hermes portal open       # 在浏览器中打开订阅管理页面
```

`hermes portal`（无子命令）是 `hermes auth add nous --type oauth` 的人类友好别名——它会登录、让您选择 Nous 模型、将 Nous 设置为推理提供商，并提供工具网关选择（与 `hermes setup --portal` 相同，且与首次快速设置相同的 Nous 流程）。

`hermes portal info` 提供高级概览：

```
  Nous Portal
  ───────────
  认证:    ✓ 已登录
  Portal:  https://portal.nousresearch.com
  模型:    ✓ 正在使用 Nous 作为推理提供商

  工具网关
  ────────────
  网页搜索与提取  通过 Nous Portal
  图像生成        通过 Nous Portal
  文本转语音      通过 Nous Portal
  浏览器自动化    通过 Nous Portal
  云端终端        未配置
```

### 切换模型

会话内：

```bash
/model anthropic/claude-sonnet-4.6
/model openai/gpt-5.5-pro
/model google/gemini-3-pro-preview
```

或者打开选择器：

```bash
/model
# 方向键，回车选择
```

会话外（完整设置向导，在添加新提供商时有用）：

```bash
hermes model
```

### 将网关与您自己的后端混合使用

如果您已经有，例如，一个 Browserbase 账户，并希望在通过 Nous 路由网页搜索和图像生成的同时继续使用它，这是支持的。使用 `hermes tools` 为每个工具选择后端：

```bash
hermes tools
# → 网页搜索        → "Nous Subscription"
# → 图像生成        → "Nous Subscription"
# → 浏览器          → "Browserbase"  (您现有的密钥)
# → TTS             → "Nous Subscription"
```

工具网关是每个工具可选加入的，而非全有或全无。无论您是否登录 Nous Portal，受管理的后端都会出现在 `hermes tools` 中——如果您在认证之前选择 "Nous Subscription"，Hermes 会内联运行 Portal 登录（它不会更改您的推理提供商或影响您的其他工具）。有关完整的每个工具配置矩阵，请参阅[工具网关文档](/user-guide/features/tool-gateway)。

### 订阅管理

随时管理您的套餐、查看使用情况或升级/取消：

- **网页：** [portal.nousresearch.com/manage-subscription](https://portal.nousresearch.com/manage-subscription)
- **CLI 快捷方式：** `hermes portal open`（在默认浏览器中打开同一页面）

## 配置参考

运行 `hermes setup --portal` 后，`~/.hermes/config.yaml` 将如下所示：

```yaml
model:
  provider: nous
  default: anthropic/claude-sonnet-4.6     # 或您选择的任何模型
  base_url: https://inference-api.nousresearch.com/v1
```

工具网关设置位于其各自工具部分下：

```yaml
web:
  backend: nous       # 网页搜索/提取通过工具网关路由

image_gen:
  provider: nous

tts:
  provider: nous

browser:
  backend: nous
```

OAuth 刷新令牌单独存储在 `~/.hermes/auth.json` 中（不在 `config.yaml` 中——凭据与配置有意分开）。

## 令牌处理

Hermes 在每次推理调用时从您存储的 Portal 刷新令牌生成一个短期的 JWT，而不是重复使用一个长期有效的 API 密钥。令牌生命周期完全自动——刷新、生成、在瞬态 401 时重试——您永远不会看到它。

如果 Portal 使刷新令牌失效（密码更改、手动撤销、会话过期），失效的刷新令牌会被**在本地隔离**，这样 Hermes 就不会重复重放它，您也不会看到一连串相同的 401。下一次调用会显示一条清晰的“需要重新认证”消息。运行 `hermes auth add nous` 以重新登录；隔离会在下一次成功登录时清除。

## 故障排除

### `hermes portal info` 显示“未登录”

您尚未完成 OAuth 流程，或者您的刷新令牌已被清除。运行：

```bash
hermes portal
```

或使用 `hermes model` 并重新选择 Nous Portal。

### 在会话中收到“需要重新认证”消息

您的 Portal 刷新令牌已失效（密码更改、手动撤销或会话过期）。运行 `hermes auth add nous`，您的下一个请求将使用新凭据。旧令牌上的任何隔离会在成功重新登录后自动清除。

### 想使用 Portal 未暴露的特定提供商模型

Portal 通过 OpenRouter 进行代理，因此 OpenRouter 支持的任何模型通常都是可用的。如果特定模型没有出现在 `/model` 中，请尝试直接使用 OpenRouter 风格的 slug：

```bash
/model anthropic/claude-opus-4.6
```

如果某个模型确实缺失，[提交一个 issue](https://github.com/NousResearch/hermes-agent/issues)——我们将 Portal 的目录暴露给 Hermes，缺口通常意味着我们可以更新的路由配置。

### 账单未出现在我的 Portal 账户中

首先检查 `hermes portal info`——如果显示您正在使用不同的提供商（`模型: 当前使用 openrouter` 而不是 `正在使用 Nous 作为推理提供商`），则您的本地配置已偏移。运行 `hermes model`，选择 Nous Portal，下一个请求将通过您的订阅路由。

## 参见

- **[工具网关](/user-guide/features/tool-gateway)** — 每个网关工具的完整详细信息、每个工具的配置和定价
- **[订阅代理](/user-guide/features/subscription-proxy)** — 从非 Hermes 工具（其他智能体、脚本、第三方客户端）使用您的 Portal 订阅
- **[语音模式](/user-guide/features/voice-mode)** — 使用 Portal 的 OpenAI TTS 进行语音对话
- **[AI 提供商](/integrations/providers)** — 如果您想比较替代方案，完整的提供商目录
- **[通过 SSH 进行 OAuth](/guides/oauth-over-ssh)** — 从远程主机或仅浏览器环境登录
- **[配置文件](/user-guide/profiles)** — 多个 Hermes 配置共享一个 Portal 登录