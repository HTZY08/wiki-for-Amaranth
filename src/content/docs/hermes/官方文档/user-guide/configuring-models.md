--- frontmatter ---
sidebar_position: 3
---

--- body ---
# 配置模型（Configuring Models）

Hermes 使用两种模型槽位：

- **主模型（Main model）**——代理思考时使用的模型。每一条用户消息、每一个工具调用循环、每一次流式响应都经过此模型。
- **辅助模型（Auxiliary models）**——代理委托执行的较小旁路任务。包括上下文压缩（Context compression）、视觉（图像分析）、网页摘要、审批评分（Approval scoring）、MCP 工具路由、会话标题生成以及技能搜索（Skill search）。每个任务都有独立的槽位，可以单独覆盖。

本页介绍如何从仪表盘配置这两类模型。如果您更喜欢配置文件或 CLI，请跳至底部的[替代方法](#alternative-methods)。

:::tip 最快路径：Nous Portal
[Nous Portal](/user-guide/features/tool-gateway) 提供超过 300 个模型，只需一个订阅。在新安装后，运行 `hermes setup --portal` 即可一次性登录并将 Nous 设置为您的提供商。使用 `hermes portal info` 检查已连接的配置。

- Portal 订阅者还可享受 **基于令牌计费的提供商 10% 折扣**。
:::

:::note `model:` 架构——空字符串 vs. 映射
在新安装的默认配置中，`model: ""`（一个空字符串哨兵，表示“尚未配置”）。当您首次运行 `hermes setup` 或 `hermes model` 时，该键会被原地升级为包含 `provider`、`default`、`base_url` 和 `api_mode` 子键的映射——本页及 [`profiles.md`](./profiles.md) / [`configuration.md`](./configuration.md) 中均展示此结构。如果您在 `config.yaml` 中看到空字符串，请运行 `hermes model`（或单击仪表盘中的 **Change**），Hermes 将为您写入字典形式。
:::

## 模型页面（The Models page）

打开仪表盘，点击侧边栏中的 **Models**。您将看到两个部分：

1. **模型设置（Model Settings）**——顶部面板，在此处为槽位分配模型。
2. **使用分析（Usage analytics）**——排名卡片，显示所选时间段内运行过会话的每个模型，包含令牌数、成本和能力徽章。

![模型页概览](/img/docs/dashboard-models/overview.png)

顶部卡片是 **模型设置** 面板。主行始终显示代理将为新会话启动的模型。点击 **Change** 打开选择器。

## 设置主模型

点击主模型行上的 **Change**：

![模型选择器对话框](/img/docs/dashboard-models/picker-dialog.png)

选择器有两列：

- **左侧**——已认证的提供商。只有您已设置的提供商（API 密钥已设置、已 OAuth 或定义为自定义端点）才会显示在此处。如果缺少某个提供商，请前往 **Keys** 添加其凭据。
- **右侧**——所选提供商的精选模型列表。这些是 Hermes 推荐用于该提供商的代理模型，而非原始的 `/models` 转储（在 OpenRouter 上，该接口包含 400 多个模型，包括 TTS、图像生成器和重排序器）。

在筛选框中输入内容，可按提供商名称、slug 或模型 ID 进行筛选。

选择一个模型，点击 **Switch**，Hermes 会将其写入 `~/.hermes/config.yaml` 的 `model` 部分。**这仅适用于新会话**——您已打开的聊天标签页将继续使用其启动时的模型。要热切换当前聊天，请在其中使用 `/model` 斜杠命令。

### 会话中切换与上下文警告

当您在**活跃会话内部**切换模型时（Herm TUI 模型选择器、`hermes` CLI 或 Telegram/Discord 上的 `/model`），Hermes 会估算您的**下一条消息**是否会针对新模型的窗口运行**预检上下文压缩（preflight context compression）**。如果会话已经接近或超过该模型的压缩阈值（参见[上下文压缩](./configuration.md#context-compression)），切换回复将包含一条警告——与昂贵模型通知相同的 `warning_message` 路径。切换会立即生效；压缩会在**切换后的第一条用户消息**时运行，在模型回答之前。

## 设置辅助模型

点击 **Show auxiliary** 展开 11 个任务槽位：

![辅助面板展开](/img/docs/dashboard-models/auxiliary-expanded.png)

每个辅助任务默认为 `auto`——即 Hermes 也会尝试使用主模型完成该任务。如果该路径不可用或遇到容量类型故障，`auto` 将遵循特定任务的 `auxiliary.<task>.fallback_chain`，然后遵循主 `fallback_providers` / `fallback_model` 链，最后使用 Hermes 内置的辅助发现链。当您希望为旁路任务使用更便宜或更快的模型时，可以覆盖特定任务。

### 常见覆盖模式

| 任务 | 何时覆盖 |
|---|---|
| **标题生成（Title Gen）** | 几乎总是。一个 $0.10/M 的 flash 模型就能像 Opus 一样写出会话标题。默认配置在 OpenRouter 上将其设置为 `google/gemini-3-flash-preview`。|
| **视觉（Vision）** | 当您的主模型缺乏视觉支持时。将其指向 `google/gemini-2.5-flash` 或 `gpt-4o-mini`。|
| **压缩（Compression）** | 当您将推理令牌浪费在 Opus/M2.7 上仅用于总结上下文时。一个快速的聊天模型可以以 1/50 的成本完成该工作。|
| **审批（Approval）** | 用于 `approval_mode: smart`——一个快速/便宜的模型（haiku、flash、gpt-5-mini）决定是否自动批准低风险命令。在此处使用昂贵模型是浪费。|
| **网页提取（Web Extract）** | 当您大量使用 `web_extract` 时。逻辑与压缩相同——摘要不需要推理。|
| **技能中心（Skills Hub）** | `hermes skills search` 使用此模型。通常保留 `auto` 即可。|
| **MCP** | MCP 工具路由。通常保留 `auto` 即可。|
| **分类说明器（Triage Specifier）** | 路由看板分类说明器（`hermes kanban specify`），将粗略的一行描述扩展为具体说明。一个便宜且能力足够的模型效果很好。|
| **看板分解器（Kanban Decomposer）** | 路由看板任务分解——将分类任务拆分为子任务图，供专业角色使用。|
| **角色描述器（Profile Describer）** | 路由角色描述生成（`hermes profile describe --auto` / 仪表盘自动生成按钮）。短小、便宜。|
| **策展器（Curator）** | 路由策展技能使用审核。在推理模型上可能运行数分钟，因此使用更便宜的辅助模型通常值得。|

### 逐个任务覆盖

点击任意辅助行上的 **Change**。会打开相同的选择器，行为相同——选择提供商 + 模型，点击 Switch。该行会更新显示 `provider · model`，而不是 `auto (use main model)`。

### 全部重置为 auto

如果您过度调整并希望重新开始，请点击辅助部分顶部的 **Reset all to auto**。每个槽位都会恢复为使用主模型。

## “Use as”快捷方式

页面上的每个模型卡片都有一个 **Use as** 下拉菜单。这是快速路径——在分析中看到某个模型，点击 **Use as**，一步将其分配给主槽位或任何特定辅助任务：

![Use as 下拉菜单](/img/docs/dashboard-models/use-as-dropdown.png)

下拉菜单包含：

- **Main model**——与点击主行上的 Change 相同。
- **All auxiliary tasks**——将此模型同时分配给所有 11 个辅助槽位。当您希望所有旁路任务都使用一个便宜的 flash 模型时非常有用。
- **Individual task options**——视觉、网页提取、压缩等。每个任务当前分配的模型会标记为 `current`。

当模型当前被分配使用时，卡片会标记 `main` 或 `aux · <task>`——因此您可以一目了然地看到哪些历史模型在何处连接。

## 写入 `config.yaml` 的内容

当您通过仪表盘保存时，Hermes 会写入 `~/.hermes/config.yaml`：

**主模型：**
```yaml
model:
  provider: openrouter
  default: anthropic/claude-opus-4.7
  base_url: ''        # 切换提供商时清除
  api_mode: chat_completions
```

**辅助覆盖（示例——视觉使用 gemini-flash）：**
```yaml
auxiliary:
  vision:
    provider: openrouter
    model: google/gemini-2.5-flash
    base_url: ''
    api_key: ''
    timeout: 120
    extra_body: {}
    download_timeout: 30
```

**辅助使用 auto（默认）：**
```yaml
auxiliary:
  compression:
    provider: auto
    model: ''
    base_url: ''
    # ... 其他字段不变
```

`provider: auto` 和 `model: ''` 告诉 Hermes 为该任务使用主模型，同时如果主路径无法服务辅助调用，仍会遵循故障转移策略。

可选的特定任务故障转移链位于同一辅助任务下：

```yaml
auxiliary:
  title_generation:
    provider: auto
    model: ''
    fallback_chain:
      - provider: openrouter
        model: inclusionai/ring-2.6-1t:free
```

当没有 `fallback_chain` 时，`auto` 会在内置辅助发现链之前使用顶层 `fallback_providers` 链。

## 何时生效？

- **CLI**（`hermes chat`）：下一次调用 `hermes chat` 时。
- **网关**（Telegram、Discord、Slack 等）：下一次**新**会话时。现有会话保留其模型。如果希望强制所有会话获取更改，请重启网关（`hermes gateway restart`）。
- **仪表盘聊天标签页**（`/chat`）：下一次新的 PTY 时。当前打开的聊天保留其模型——请在其中使用 `/model` 进行热切换。

更改绝不会使运行中会话的提示缓存失效。这是有意为之：在会话内部切换主模型需要重置缓存（系统提示包含特定于模型的内容），我们将其保留给聊天内的显式 `/model` 斜杠命令。

## 故障排除

### 选择器中显示“No authenticated providers”

Hermes 仅在有有效凭据时才列出提供商。检查侧边栏中的 **Keys**——您应该看到以下之一：API 密钥、成功的 OAuth 或自定义端点 URL。如果您想要的提供商不在列表中，请运行 `hermes setup` 进行配置，或前往 **Keys** 添加环境变量。

### 正在运行的聊天中主模型未更改

符合预期。仪表盘写入 `config.yaml`，新会话会读取它。当前打开的聊天是一个活跃的代理进程——它保留其启动时使用的模型。在聊天内使用 `/model <name>` 热切换该特定会话。

### 辅助覆盖“未生效”

检查以下三项：

1. **您是否启动了新会话？** 现有聊天不会重新读取配置。
2. **`provider` 是否设置为非 `auto` 的值？** 如果字段显示 `auto`，则该任务仍在使用您的主模型。点击 **Change** 并选择一个真实提供商。
3. **提供商是否已认证？** 如果您将 `minimax` 分配给了某个任务但没有 MiniMax API 密钥，该任务会回退到 OpenRouter 默认值，并在 `agent.log` 中记录警告。

### 我选择了一个模型，但 Hermes 切换了提供商

在 OpenRouter（或任何聚合器）上，裸模型名称首先在聚合器内部解析。因此，OpenRouter 上的 `claude-sonnet-4` 会变成 `anthropic/claude-sonnet-4.6`，并保留在您的 OpenRouter 认证上。但如果您在原生 Anthropic 认证上输入 `claude-sonnet-4`，它会保持为 `claude-sonnet-4-6`。如果您看到意外的提供商切换，请检查您当前的提供商是否符合预期——选择器始终在对话框顶部显示当前主模型。

## 替代方法

### CLI 斜杠命令

在任何 `hermes chat` 会话内部：

```
/model gpt-5.4 --provider openrouter             # 仅会话
/model gpt-5.4 --provider openrouter --global    # 同时持久化到 config.yaml
```

`--global` 会执行与仪表盘 **Change** 按钮相同的操作，同时原地切换运行中的会话。

### 自定义别名

为您经常使用的模型定义自己的短名称，然后在 CLI 或任何消息平台上使用 `/model <alias>`。有两种等效格式——选择最适合您工作流的一种。

**规范格式（顶层 `model_aliases:`）**——完全控制 provider + base_url：

```yaml
# ~/.hermes/config.yaml
model_aliases:
  fav:
    model: claude-sonnet-4.6
    provider: anthropic
  grok:
    model: grok-4
    provider: x-ai
```

**短字符串格式（`model.aliases.<name>: provider/model`）**——从 shell 中更方便，因为 `hermes config set` 只写入标量值，但无法携带自定义 `base_url`：

```bash
hermes config set model.aliases.fav anthropic/claude-opus-4.6
hermes config set model.aliases.grok x-ai/grok-4
```

两种路径都使用相同的加载器（`hermes_cli/model_switch.py`）。在 `model_aliases:` 中声明的条目优先于同名的 `model.aliases:` 条目。

然后在聊天中使用 `/model fav` 或 `/model grok`。用户别名会覆盖内置短名称（`sonnet`、`kimi`、`opus` 等）。完整参考请参见[自定义模型别名](/reference/slash-commands#custom-model-aliases)。

### `hermes model` 子命令

```bash
hermes model            # 交互式提供商 + 模型选择器（切换默认值的规范方法）
```

`hermes model` 会引导您选择提供商、进行认证（OAuth 流程会打开浏览器；API 密钥提供商会提示输入密钥），然后从该提供商的精选目录中选择特定模型。选择结果会写入 `~/.hermes/config.yaml` 中的 `model.provider` 和 `model.model`。

要列出提供商/模型而不启动选择器，请使用仪表盘或下面的 REST 端点。要检查 CLI 当前实际使用的配置：`hermes config show | grep '^model\.'` 和 `hermes status`。

### 直接编辑配置文件

编辑 `~/.hermes/config.yaml`，然后重启读取它的组件。完整架构请参见[配置参考](./configuration.md)。

### REST API

仪表盘使用三个端点。适合脚本化操作：

```bash
# 列出已认证的提供商 + 精选模型列表
curl -H "X-Hermes-Session-Token: $TOKEN" http://localhost:PORT/api/model/options

# 读取当前主模型 + 辅助模型分配
curl -H "X-Hermes-Session-Token: $TOKEN" http://localhost:PORT/api/model/auxiliary

# 设置主模型
curl -X POST -H "Content-Type: application/json" -H "X-Hermes-Session-Token: $TOKEN" \
  -d '{"scope":"main","provider":"openrouter","model":"anthropic/claude-opus-4.7"}' \
  http://localhost:PORT/api/model/set

# 覆盖单个辅助任务
curl -X POST -H "Content-Type: application/json" -H "X-Hermes-Session-Token: $TOKEN" \
  -d '{"scope":"auxiliary","task":"vision","provider":"openrouter","model":"google/gemini-2.5-flash"}' \
  http://localhost:PORT/api/model/set

# 将一个模型分配给所有辅助任务
curl -X POST -H "Content-Type: application/json" -H "X-Hermes-Session-Token: $TOKEN" \
  -d '{"scope":"auxiliary","task":"","provider":"openrouter","model":"google/gemini-2.5-flash"}' \
  http://localhost:PORT/api/model/set

# 将所有辅助任务重置为 auto
curl -X POST -H "Content-Type: application/json" -H "X-Hermes-Session-Token: $TOKEN" \
  -d '{"scope":"auxiliary","task":"__reset__","provider":"","model":""}' \
  http://localhost:PORT/api/model/set
```

会话令牌在启动时注入到仪表盘 HTML 中，并在每次服务器重启时轮换。如果您正在针对正在运行的仪表盘编写脚本，请从浏览器开发者工具（`window.__HERMES_SESSION_TOKEN__`）中获取它。