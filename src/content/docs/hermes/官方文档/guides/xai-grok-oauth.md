---
title: Xai Grok Oauth
---

sidebar_position: 16
title: "xAI Grok OAuth（SuperGrok / X Premium+）"
description: "使用您的 SuperGrok 或 X Premium+ 订阅登录，即可在 Hermes Agent 中使用 Grok 模型——无需 API 密钥"
---

--- body ---
# xAI Grok OAuth（SuperGrok / X Premium+）

Hermes Agent 支持通过基于浏览器的 OAuth 登录流程对 [accounts.x.ai](https://accounts.x.ai) 验证 xAI Grok，可使用 **SuperGrok 订阅**（[grok.com](https://x.ai/grok)）或 **X Premium+ 订阅**（关联的 X 账号）。无需 `XAI_API_KEY`——只需登录一次，Hermes 便会自动在后台刷新您的会话。

当您使用拥有 Premium+ 的 X 账号登录时，xAI 会自动将订阅状态关联到您的 xAI 会话，因此 OAuth 流程与直接 SuperGrok 订阅者相同。

传输层复用了 `codex_responses` 适配器（xAI 暴露了一个 Responses 风格的端点），因此推理、工具调用、流式传输和提示缓存无需修改适配器即可正常工作。

同一个 OAuth bearer 令牌也被 Hermes 中所有直达 xAI 的表面复用——TTS、图像生成、视频生成和转录——因此一次登录即可覆盖所有四个功能。

## 概览

| 项目 | 值 |
|------|------|
| 提供商 ID | `xai-oauth` |
| 显示名称 | xAI Grok OAuth（SuperGrok / X Premium+） |
| 认证类型 | 浏览器 OAuth 2.0 PKCE（环回回调） |
| 传输层 | xAI Responses API（`codex_responses`） |
| 默认模型 | `grok-build-0.1` |
| 端点 | `https://api.x.ai/v1` |
| 认证服务器 | `https://accounts.x.ai` |
| 需要环境变量 | 否（此提供商**不**使用 `XAI_API_KEY`） |
| 订阅 | [SuperGrok](https://x.ai/grok) 或 [X Premium+](https://x.com/i/premium_sign_up)——请参阅下方说明 |

## 前提条件

- Python 3.9+
- 已安装 Hermes Agent
- 您的 xAI 账号拥有有效的 **SuperGrok** 订阅，**或**您登录使用的 X 账号拥有 **X Premium+** 订阅（xAI 会自动关联订阅）
- 本地机器上有可用的浏览器（或使用 `--no-browser` 进行远程会话）

:::warning xAI 可能会按层级限制 OAuth API 访问
xAI 的后端对 OAuth API 表面执行自己的白名单，并且已发现即使应用内订阅处于活动状态，也会拒绝标准 SuperGrok 订阅者并返回 `HTTP 403`（参见问题 [#26847](https://github.com/NousResearch/hermes-agent/issues/26847)）。如果 OAuth 登录在浏览器中成功但推理返回 403，请设置 `XAI_API_KEY` 并切换到 API 密钥路径（`provider: xai`）——该表面目前不受相同限制。
:::

## 快速开始

```bash
# 启动提供商和模型选择器
hermes model
# → 从提供商列表中选择 "xAI Grok OAuth（SuperGrok / X Premium+）"
# → Hermes 将打开您的浏览器跳转到 accounts.x.ai
# → 在浏览器中批准访问
# → 选择一个模型（grok-build-0.1 在顶部）
# → 开始聊天

hermes
```

首次登录后，凭据将存储在 `~/.hermes/auth.json` 中，并在过期前自动刷新。

## 手动登录

您无需通过模型选择器即可触发登录：

```bash
hermes auth add xai-oauth
```

### 远程 / 无头会话

在服务器、容器或 SSH 会话（没有浏览器可用）中，Hermes 会检测远程环境，并打印授权 URL 而非打开浏览器。

**重要提示：**环回监听器仍在远程机器的 `127.0.0.1:56121` 上运行。xAI 的重定向需要到达*该*监听器，因此在您的笔记本电脑上打开 URL 会失败（`无法建立连接。我们无法到达您的应用程序。`），除非您进行端口转发：

```bash
# 在本地机器的另一个终端中：
ssh -N -L 56121:127.0.0.1:56121 user@remote-host

# 然后在远程机器的 SSH 会话中：
hermes auth add xai-oauth --no-browser
# 在本地浏览器中打开打印的授权 URL。
```

通过跳板机 / 堡垒机：添加 `-J jump-user@jump-host`。

完整的分步指南（包括 ProxyJump 链、mosh/tmux 和 ControlMaster 陷阱）请参见 [通过 SSH / 远程主机的 OAuth](./oauth-over-ssh.md)。

### 仅浏览器远程环境（Cloud Shell、Codespaces、EC2 Instance Connect）

如果您没有常规的 SSH 客户端（例如您在 GCP Cloud Shell、GitHub Codespaces、AWS EC2 Instance Connect、Gitpod 或其他基于浏览器的控制台中运行 Hermes），则上述 `ssh -L` 方法不可用。请改用 `--manual-paste`——Hermes 会跳过环回监听器，让您直接从浏览器粘贴失败的回调 URL：

```bash
hermes auth add xai-oauth --manual-paste
# 或者通过模型选择器：
hermes model --manual-paste
```

完整操作指南请参见 [通过 SSH / 远程主机的 OAuth](./oauth-over-ssh.md#仅浏览器远程-cloud-shell--codespaces--ec2-instance-connect)。问题修复请参见 [#26923](https://github.com/NousResearch/hermes-agent/issues/26923)。

如果授权页直接将授权代码呈现在页面上（xAI 在基于浏览器的控制台上的当前行为）而不是重定向到您的 `127.0.0.1:56121/callback`，请在 `Callback URL:` 提示符处粘贴**仅代码值**——Hermes 可以接受完整 URL、带有 `?code=...&state=...` 的裸查询片段或裸代码。

## 登录工作原理

1. Hermes 打开您的浏览器跳转到 `accounts.x.ai`。
2. 您登录（或确认现有会话）并批准访问。
3. xAI 重定向回 Hermes，令牌保存到 `~/.hermes/auth.json`。
4. 此后，Hermes 会在后台刷新访问令牌——您将保持登录状态，直到运行 `hermes auth logout xai-oauth` 或从 xAI 账号设置中撤销访问权限。

## 检查登录状态

```bash
hermes doctor
```

`◆ Auth Providers` 部分将显示每个提供商的当前状态，包括 `xai-oauth`。

## 切换模型

```bash
hermes model
# → 选择 "xAI Grok OAuth（SuperGrok / X Premium+）"
# → 从模型列表中选择（grok-build-0.1 固定在最顶部）
```

或者直接设置模型：

```bash
hermes config set model.default grok-build-0.1
hermes config set model.provider xai-oauth
```

## 配置参考

登录后，`~/.hermes/config.yaml` 将包含：

```yaml
model:
  default: grok-build-0.1
  provider: xai-oauth
  base_url: https://api.x.ai/v1
```

### 提供商别名

以下所有别名均解析为 `xai-oauth`：

```bash
hermes --provider xai-oauth        # 规范名称
hermes --provider grok-oauth       # 别名
hermes --provider x-ai-oauth       # 别名
hermes --provider xai-grok-oauth   # 别名
```

## 直达 xAI 工具（TTS / 图像 / 视频 / 转录 / X 搜索）

一旦您通过 OAuth 登录，每个直达 xAI 的工具都会自动复用同一个 bearer 令牌——无需**单独设置**，除非您更愿意使用 API 密钥。

为每个工具选择后端：

```bash
hermes tools
# → 文本转语音       → "xAI TTS"
# → 图像生成     → "xAI Grok Imagine（图像）"
# → 视频生成     → "xAI Grok Imagine"
# → X（Twitter）搜索   → "xAI Grok OAuth（SuperGrok / X Premium+）"
```

如果 OAuth 令牌已存储，选择器会确认并跳过凭据提示。如果既未设置 OAuth 也未设置 `XAI_API_KEY`，选择器会提供一个 3 选项菜单：OAuth 登录、粘贴 API 密钥或跳过。

:::note 视频生成默认关闭
`video_gen` 工具集默认禁用。在代理可以调用 `video_generate` 之前，请在 `hermes tools` → `🎬 视频生成`（按空格键）中启用它。否则代理可能会回退到捆绑的 ComfyUI 技能，该技能也被标记为用于视频生成。
:::

:::note 当存在 xAI 凭据时，X 搜索会自动启用
只要配置了 xAI 凭据（SuperGrok / X Premium+ OAuth 令牌或 `XAI_API_KEY`），`x_search` 工具集就会自动启用。如果您不希望这样，请通过 `hermes tools` → `🐦 X（Twitter）搜索`（按空格键）显式禁用它。该工具通过 xAI 内置的 `x_search` Responses API 路由——它可与**您的** SuperGrok / X Premium+ OAuth 登录或付费的 `XAI_API_KEY` 配合使用，当两者都配置时优先使用 OAuth（使用您的订阅配额而不是 API 消耗）。当未配置任何 xAI 凭据时，无论工具集是否启用，该工具的架构都会对模型隐藏。
:::

### 模型

| 工具 | 模型 | 备注 |
|------|------|------|
| 聊天 | `grok-build-0.1` | 默认；通过 OAuth 登录时自动选择 |
| 聊天 | `grok-4.3` | 之前的默认 |
| 聊天 | `grok-4.20-0309-reasoning` | 推理变体 |
| 聊天 | `grok-4.20-0309-non-reasoning` | 非推理变体 |
| 聊天 | `grok-4.20-multi-agent-0309` | 多代理变体 |
| 图像 | `grok-imagine-image` | 默认；约 5–10 秒 |
| 图像 | `grok-imagine-image-quality` | 更高保真度；约 10–20 秒 |
| 视频 | `grok-imagine-video` | 文本转视频 |
| 视频 | `grok-imagine-video-1.5-preview` | 图像转视频；过时别名 `grok-imagine-video-1.5-2026-05-30` |
| TTS | （默认语音） | xAI `/v1/tts` 端点 |

聊天目录从磁盘上的 `models.dev` 缓存动态生成；新的 xAI 版本在该缓存刷新后会自动出现。`grok-build-0.1` 始终固定在列表顶部。

## 环境变量

| 变量 | 效果 |
|------|------|
| `XAI_BASE_URL` | 覆盖默认的 `https://api.x.ai/v1` 端点（很少需要）。 |

要选择 xAI 作为活动提供商，请在 `config.yaml` 中设置 `model.provider: xai-oauth`（使用 `hermes setup` 进行引导流程），或为单次调用传递 `--provider xai-oauth`。

## 故障排除

### 令牌过期——未自动重新登录

Hermes 会在每个会话之前刷新令牌，并在收到 401 时再次刷新。如果刷新失败并返回 `invalid_grant`（刷新令牌被撤销，或账号被轮换），Hermes 会显示类型化的重新认证消息而不是崩溃。

当刷新失败是终局性的（HTTP 4xx、`invalid_grant`、被撤销的授权等）时，Hermes 会将刷新令牌标记为失效并在本地隔离——后续调用会跳过注定失败的刷新尝试，而不是一遍又一遍地重复同样的 401。代理会显示一条“需要重新认证”消息，并在您再次登录之前保持不干预状态。

**解决方法：**再次运行 `hermes auth add xai-oauth` 以启动新的登录。隔离会在下一次成功交换时清除。

### 授权超时

环回监听器有一个有限的过期窗口（默认 180 秒）。如果您未及时批准登录，Hermes 会引发超时错误。

**解决方法：**重新运行 `hermes auth add xai-oauth`（或 `hermes model`）。流程从头开始。

### 状态不匹配（可能的 CSRF）

Hermes 检测到授权服务器返回的 `state` 值与其发送的不匹配。

**解决方法：**重新运行登录。如果问题持续，请检查是否有代理或重定向修改了 OAuth 响应。

### 从远程服务器登录

在 SSH 或容器会话中，Hermes 会打印授权 URL 而不是打开浏览器。环回回调监听器仍绑定远程主机上的 `127.0.0.1:56121`——您笔记本电脑的浏览器无法在没有 SSH 本地转发的情况下访问它：

```bash
# 本地机器，另一个终端：
ssh -N -L 56121:127.0.0.1:56121 user@remote-host

# 远程机器：
hermes auth add xai-oauth --no-browser
```

完整操作指南（跳板机、mosh/tmux、端口冲突）：[通过 SSH / 远程主机的 OAuth](./oauth-over-ssh.md)。

### 成功登录后出现 HTTP 403（层级 / 权限）

OAuth 已在浏览器中完成，令牌已保存，但推理或令牌刷新返回 `HTTP 403`，消息类似 *"调用者无权执行指定操作"*。

这**不是**令牌过期问题——重新运行 `hermes model` 不会改变。xAI 的后端已被发现将 OAuth API 访问限制在特定的 SuperGrok 层级，尽管应用内订阅处于活动状态（问题 [#26847](https://github.com/NousResearch/hermes-agent/issues/26847)）。

**解决方法：**设置 `XAI_API_KEY` 并切换到 API 密钥路径：

```bash
export XAI_API_KEY=xai-...
hermes config set model.provider xai
```

或者如果必须使用 OAuth 路由，请在 [x.ai/grok](https://x.ai/grok) 升级您的订阅。

### 运行时出现 "No xAI credentials found" 错误

认证存储中没有 `xai-oauth` 条目，也没有设置 `XAI_API_KEY`。您尚未登录，或者凭据文件已被删除。

**解决方法：**运行 `hermes model` 并选择 xAI Grok OAuth 提供商，或者运行 `hermes auth add xai-oauth`。

## 注销

要删除所有存储的 xAI Grok OAuth 凭据：

```bash
hermes auth logout xai-oauth
```

这会清除 `auth.json` 中的单例 OAuth 条目以及 `xai-oauth` 的任何凭据池行。如果您只想删除单个池条目，请使用 `hermes auth remove xai-oauth <索引|ID|标签>`（运行 `hermes auth list xai-oauth` 查看它们）。

## 另请参阅

- [通过 SSH / 远程主机的 OAuth](./oauth-over-ssh.md) —— 如果 Hermes 与您的浏览器不在同一台机器上，请务必阅读
- [AI 提供商参考](../integrations/providers.md)
- [环境变量](../reference/environment-variables.md)
- [配置](../user-guide/configuration.md)
- [语音与 TTS](../user-guide/features/tts.md)