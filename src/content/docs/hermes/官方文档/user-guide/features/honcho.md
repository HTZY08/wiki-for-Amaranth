--- frontmatter ---
---
sidebar_position: 99
title: "Honcho 记忆"
description: "通过 Honcho — 辩证法推理、多智能体用户建模和深度个性化实现的 AI 原生持久记忆"
---

--- body ---

# Honcho 记忆

[Honcho](https://github.com/plastic-labs/honcho) 是一个 AI 原生的记忆后端，它在 Hermes 内置的记忆系统之上增加了辩证法推理和深度用户建模。与简单的键值存储不同，Honcho 通过分析对话后的内容，维护一个正在运行的用户模型——包括用户的偏好、沟通风格、目标和模式。

:::info Honcho 是一个记忆提供者插件
Honcho 已集成到[记忆提供者](./memory-providers.md) 系统中。以下所有功能都可通过统一的记忆提供者接口使用。
:::

## Honcho 带来的增强

| 能力 | 内置记忆 | Honcho |
|-----------|----------------|--------|
| 跨会话持久性 | ✔ 基于文件的 MEMORY.md/USER.md | ✔ 服务端 API |
| 用户画像 | ✔ 手动智能体策划 | ✔ 自动辩证法推理 |
| 会话摘要 | — | ✔ 会话作用域上下文注入 |
| 多智能体隔离 | — | ✔ 每个对等体（peer）画像隔离 |
| 观察模式 | — | ✔ 统一或方向性观察 |
| 结论（衍生洞察） | — | ✔ 服务端关于模式的推理 |
| 历史搜索 | ✔ FTS5 会话搜索 | ✔ 基于结论的语义搜索 |

**辩证法推理**：每次对话回合后（由 `dialecticCadence` 控制），Honcho 分析对话内容并推导出关于用户偏好、习惯和目标的洞察。这些洞察随时间累积，使智能体能够获得超越用户明确陈述的深入理解。辩证法支持多遍数深度（1–3 遍），并自动选择冷/暖提示词策略——冷启动查询侧重于一般用户事实，而暖查询优先考虑会话作用域上下文。

**会话作用域上下文**：基本上下文现在除了用户表示和对等体卡之外，还包含会话摘要。这让智能体意识到当前会话中已经讨论过的内容，减少重复并实现连续性。

**多智能体画像**：当多个 Hermes 实例与同一个用户对话时（例如，一个编码助手和一个个人助手），Honcho 会维护独立的“对等体”画像。每个对等体只看到自己的观察和结论，防止上下文交叉污染。

## 设置

```bash
hermes memory setup    # 从提供者列表中选择 "honcho"
```

或者手动配置：

```yaml
# ~/.hermes/config.yaml
memory:
  provider: honcho
```

```bash
echo 'HONCHO_API_KEY=***' >> ~/.hermes/.env
```

在 [honcho.dev](https://honcho.dev) 获取 API 密钥。

## 架构

### 两层上下文注入

每一回合（在 `hybrid` 或 `context` 模式下），Honcho 会组装两层上下文注入到系统提示词中：

1. **基本上下文** — 会话摘要、用户表示、用户对等体卡、AI 自我表示和 AI 身份卡。在 `contextCadence` 时刷新。这是“这个用户是谁”的层次。
2. **辩证法补充** — LLM 合成的关于用户当前状态和需求的推理。在 `dialecticCadence` 时刷新。这是“此刻什么最重要”的层次。

两层上下文会被拼接并截断到 `contextTokens` 预算内（如果设置了的话）。

### 冷/暖提示词选择

辩证法自动在两个提示词策略之间选择：

- **冷启动**（尚无基本上下文）：一般查询——“这个人是谁？他们的偏好、目标和工作风格是什么？”
- **暖会话**（基本上下文已存在）：会话作用域查询——“考虑到目前会话中讨论的内容，关于这个用户的哪些上下文最相关？”

这是根据基本上下文是否已被填充自动发生的。

### 三个正交配置旋钮

成本和深度由三个独立的旋钮控制：

| 旋钮 | 控制 | 默认值 |
|------|----------|---------|
| `contextCadence` | `context()` API 调用之间的回合数（基本层刷新） | `1` |
| `dialecticCadence` | `peer.chat()` LLM 调用之间的回合数（辩证法层刷新） | `2`（推荐 1–5） |
| `dialecticDepth` | 每次辩证法调用中的 `.chat()` 遍数（1–3） | `1` |

这些旋钮是正交的——你可以频繁刷新上下文但少做辩证法，或者低频但深度多遍辩证法。示例：`contextCadence: 1, dialecticCadence: 5, dialecticDepth: 2` 每回合刷新基本上下文，每 5 回合运行一次辩证法，每次辩证法运行 2 遍。

### 辩证法深度（多遍）

当 `dialecticDepth` > 1 时，每次辩证法调用会运行多个 `.chat()` 遍：

- **第 0 遍**：冷或暖提示词（见上文）
- **第 1 遍**：自我审计——识别初始评估中的空白，并从最近会话中综合证据
- **第 2 遍**：调和——检查先前遍数之间的矛盾，并生成最终综合结果

每遍使用比例推理级别（早期遍数较轻，主要遍使用基础级别）。使用 `dialecticDepthLevels` 覆盖每遍的级别——例如，深度 3 运行时的 `["minimal", "medium", "high"]`。

如果前一遍返回了强信号（长而结构化的输出），则遍数会提前退出，因此深度 3 并不总是意味着 3 次 LLM 调用。

### 会话启动预热

在会话初始化时，Honcho 会在后台以完整配置的 `dialecticDepth` 执行一次辩证法调用，并将结果直接提供给第一回合的上下文组装。对于冷对等体，单遍预热通常返回浅薄输出——多遍深度会在用户开口之前运行审计/调和的循环。如果预热未能在第一回合前完成，第一回合会回退到带有限时超时的同步调用。

### 查询自适应推理级别

自动注入的辩证法会根据查询长度缩放 `dialecticReasoningLevel`：≥120 字符时 +1 级，≥400 时 +2，上限为 `reasoningLevelCap`（默认 `"high"`）。设置 `reasoningHeuristic: false` 可禁用此功能，使每次自动调用都固定为 `dialecticReasoningLevel`。可用级别：`minimal`, `low`, `medium`, `high`, `max`。

## 配置选项

Honcho 在 `~/.honcho/config.json`（全局）或 `$HERMES_HOME/honcho.json`（本地配置文件）中配置。设置向导会为你处理这些。

### 自托管 Honcho 带认证

当将 Hermes 指向自托管的 Honcho 服务器时，`hermes honcho setup`（以及 `hermes memory setup`）会在基础 URL 之后询问一个**本地 JWT / bearer 令牌**。粘贴一个用服务器的 `AUTH_JWT_SECRET`（Honcho 的 compose 环境变量）签名的 JWT 以启用认证访问；对于运行 `AUTH_USE_AUTH=false` 的服务器，留空即可。本地令牌存储在主机关联块下（`honcho.json` 中的 `hosts.<host>.apiKey`），与任何云端 `apiKey` 分开，因此你可以稍后将 `Cloud or local?` 提示切换回 `cloud`，而不会丢失任一凭据。

### 完整配置参考

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `contextTokens` | `null`（无上限） | 每回合自动注入上下文的令牌预算。设置为整数（例如 1200）以限制。按单词边界截断 |
| `contextCadence` | `1` | `context()` API 调用之间的最小回合数（基本层刷新） |
| `dialecticCadence` | `2` | `peer.chat()` LLM 调用之间的最小回合数（辩证法层）。推荐 1–5。在 `tools` 模式下不相关——模型显式调用 |
| `dialecticDepth` | `1` | 每次辩证法调用中的 `.chat()` 遍数。限制为 1–3 |
| `dialecticDepthLevels` | `null` | 每遍推理级别的可选数组，例如 `["minimal", "low", "medium"]`。覆盖比例默认值 |
| `dialecticReasoningLevel` | `'low'` | 基础推理级别：`minimal`, `low`, `medium`, `high`, `max` |
| `dialecticDynamic` | `true` | 为 `true` 时，模型可以通过工具参数每调用覆盖推理级别 |
| `dialecticMaxChars` | `600` | 注入到系统提示词中的辩证法结果的最大字符数 |
| `recallMode` | `'hybrid'` | `hybrid`（自动注入+工具）、`context`（仅注入）、`tools`（仅工具） |
| `writeFrequency` | `'async'` | 何时刷新消息：`async`（后台线程）、`turn`（同步）、`session`（结束时批处理）或整数 N |
| `saveMessages` | `true` | 是否将消息持久化到 Honcho API |
| `observationMode` | `'directional'` | `directional`（全部开启）或 `unified`（共享池）。可以通过 `observation` 对象覆盖以进行精细控制 |
| `messageMaxChars` | `25000` | 通过 `add_messages()` 发送的每条消息的最大字符数。超出时会分块 |
| `dialecticMaxInputChars` | `10000` | 辩证法查询输入到 `peer.chat()` 的最大字符数 |
| `sessionStrategy` | `'per-directory'` | `per-directory`、`per-repo`、`per-session` 或 `global` |
| `pinUserPeer` | `false` | 仅网关。为 `true` 时，每个平台用户都折叠到 `peerName` |
| `userPeerAliases` | `{}` | 仅网关。运行时 ID 到对等体的映射（`{"7654321": "alice"}`）。多对一 |
| `runtimePeerPrefix` | `""` | 仅网关。为未匹配别名的未知运行时 ID 加命名空间（`telegram_7654321`） |

**会话策略**控制 Honcho 会话如何映射到你的工作：
- `per-session` —— 每个 `hermes` 运行获得一个新会话。干净开始，通过工具记忆。推荐新用户使用。
- `per-directory` —— 每个工作目录一个 Honcho 会话。上下文跨运行累积。
- `per-repo` —— 每个 git 仓库一个会话。
- `global` —— 跨所有目录的单一会话。

**回忆模式**控制记忆如何流入对话：
- `hybrid` —— 上下文自动注入系统提示词，并且工具可用（模型决定何时查询）。
- `context` —— 仅自动注入，工具隐藏。
- `tools` —— 仅工具，无自动注入。智能体必须显式调用 `honcho_reasoning`、`honcho_search` 等。

**每个回忆模式的设置：**

| 设置 | `hybrid` | `context` | `tools` |
|---------|----------|-----------|---------|
| `writeFrequency` | 刷新消息 | 刷新消息 | 刷新消息 |
| `contextCadence` | 控制基本上下文刷新 | 控制基本上下文刷新 | 不相关——无注入 |
| `dialecticCadence` | 控制自动 LLM 调用 | 控制自动 LLM 调用 | 不相关——模型显式调用 |
| `dialecticDepth` | 每次调用多遍 | 每次调用多遍 | 不相关——模型显式调用 |
| `contextTokens` | 限制注入 | 限制注入 | 不相关——无注入 |
| `dialecticDynamic` | 控制模型覆盖 | 不可用（无工具） | 控制模型覆盖 |

在 `tools` 模式下，模型完全控制——它会在需要时以任意选择的 `reasoning_level` 调用 `honcho_reasoning`。间隔和预算设置仅适用于自动注入模式（`hybrid` 和 `context`）。

## 网关身份映射

这些设置仅在运行 [Hermes 网关](../../developer-guide/gateway-internals.md) 时才有意义——这是一个统一入口点，用户通过平台原生运行时 ID（Telegram UID、Discord snowflake、Slack 用户）到达。CLI、TUI 和桌面会话没有运行时 ID，总是解析为 `peerName`，因此非网关场景下这些键无效。

设置向导会检测是否连接了网关平台，如果没有则完全跳过此步骤。当它运行时，会问一个问题——*谁与此网关对话？*——并推导出对应的键：

| 回答 | 结果 |
|--------|--------|
| **只有我** | `pinUserPeer: true` —— 每个非智能体网关用户都折叠到你的对等体。Pin 会覆盖所有别名，因此仅在没有用户侧身份需要自己的对等体时选择此项。如果有多个智能体到达网关且每个都需要不同的对等体，则**不要** pin——将 `pinUserPeer` 设为 `false`，并通过 `userPeerAliases`（`[e]` 编辑器）映射它们 |
| **我 + 其他人**（共用） | `pinUserPeer: false` + `userPeerAliases` 将你的运行时 ID 映射到 `peerName` —— 你保留在共享历史中，其他人获得自己的对等体 |
| **只有其他人** | `pinUserPeer: false`，可选 `runtimePeerPrefix` —— 每个用户获得自己的对等体 |

在提示符下选择 `[e]` 可直接设置这三个键。

解析器按从上到下的顺序尝试键，第一个匹配者胜出：`pinUserPeer` → `userPeerAliases[id]` → `runtimePeerPrefix + id` → 原始运行时 ID → `peerName` → 会话键回退。

:::warning 取消固定会孤立共用记忆
将 `pinUserPeer` 从 `true` 切换到 `false` 不会迁移数据——在 `peerName` 下累积的记忆会留在那里，而平台用户会解析到新的空对等体。为保持你自己的连续性，选择 **共用** 路径，以便你的运行时 ID 别名回 `peerName`。当检测到转换时，向导会自动提供此建议。
:::

:::note 已弃用的键
`pinPeerName` 是 `pinUserPeer` 的遗留别名——出于向后兼容仍会读取（两者都设置时 `pinUserPeer` 优先），但永远不会写入。重新运行设置会将其迁移到规范键。
:::

## 观察（方向性与统一性）

Honcho 将会话建模为对等体之间交换消息。每个对等体有两个观察开关，一对一映射到 Honcho 的 `SessionPeerConfig`：

| 开关 | 效果 |
|--------|--------|
| `observeMe` | Honcho 从该对等体自己的消息构建其表示 |
| `observeOthers` | 该对等体观察另一个对等体的消息（促进交叉对等体推理） |

两个对等体 × 两个开关 = 四个标志。`observationMode` 是一个简写预设：

| 预设 | 用户标志 | AI 标志 | 语义 |
|--------|-----------|----------|-----------|
| `"directional"`（默认） | 我：开，他人：开 | 我：开，他人：开 | 完全相互观察。启用交叉对等体辩证法——“AI 基于用户说了什么以及 AI 的回复，对用户有哪些了解。” |
| `"unified"` | 我：开，他人：关 | 我：关，他人：开 | 共享池语义——AI 只观察用户的消息，用户对等体仅自我建模。单观察者池。 |

通过显式 `observation` 块覆盖预设，实现每个对等体的控制：

```json
"observation": {
  "user": { "observeMe": true,  "observeOthers": true },
  "ai":   { "observeMe": true,  "observeOthers": false }
}
```

常见模式：

| 意图 | 配置 |
|--------|--------|
| 完全观察（大多数用户） | `"observationMode": "directional"` |
| AI 不应从自己的回复中重新建模用户 | `"ai": {"observeMe": true, "observeOthers": false}` |
| 强角色个性，AI 对等体不应通过自我观察更新 | `"ai": {"observeMe": false, "observeOthers": true}` |

通过 [Honcho 仪表盘](https://app.honcho.dev) 设置的服务端开关会覆盖本地默认值——Hermes 在会话初始化时会同步它们。

## 工具

当 Honcho 作为活跃的记忆提供者时，五个工具变为可用：

| 工具 | 用途 |
|------|---------|
| `honcho_profile` | 读取或更新对等体卡——传递 `card`（事实列表）进行更新，省略则为读取 |
| `honcho_search` | 基于语义的上下文搜索——原始摘录，无 LLM 综合 |
| `honcho_context` | 完整会话上下文——摘要、表示、卡、最近消息 |
| `honcho_reasoning` | 来自 Honcho 的 LLM 的综合回答——传递 `reasoning_level`（minimal/low/medium/high/max）以控制深度 |
| `honcho_conclude` | 创建或删除结论——传递 `conclusion` 创建，传递 `delete_id` 删除（仅限 PII） |

## CLI 命令

`hermes honcho` 子命令**仅在 Honcho 是活跃记忆提供者时**才会注册（`config.yaml` 中 `memory.provider: honcho`）。在新安装时，直接使用 `hermes memory setup honcho` 配置 Honcho（或运行 `hermes memory setup` 并从列表中选择）；之后 `hermes honcho` 子命令会在下次调用时出现。

```bash
hermes memory setup honcho    # 直接配置 Honcho（在激活前可用）
hermes honcho status          # 连接状态、配置和关键设置
hermes honcho setup           # 重定向到 `hermes memory setup`（激活后的别名）
hermes honcho strategy        # 显示或设置会话策略（per-session/per-directory/per-repo/global）
hermes honcho peer            # 显示或更新对等体名称 + 辩证法推理级别
hermes honcho mode            # 显示或设置回忆模式（hybrid/context/tools）
hermes honcho tokens          # 显示或设置上下文和辩证法的令牌预算
hermes honcho identity        # 设置或显示 AI 对等体的 Honcho 身份
hermes honcho sync            # 同步 Honcho 配置到所有现有配置文件
hermes honcho peers           # 显示所有配置文件中的对等体身份
hermes honcho sessions        # 列出已知的 Honcho 会话映射
hermes honcho map             # 将当前目录映射到一个 Honcho 会话名称
hermes honcho enable          # 为当前活跃配置文件启用 Honcho
hermes honcho disable         # 为当前活跃配置文件禁用 Honcho
hermes honcho migrate         # 从 openclaw-honcho 迁移的分步指南
```

## 从 `hermes honcho` 迁移

如果你之前使用过独立的 `hermes honcho setup`：

1. 现有的配置（`honcho.json` 或 `~/.honcho/config.json`）将保留
2. 服务端数据（记忆、结论、用户画像）完整不变
3. 在 config.yaml 中设置 `memory.provider: honcho` 即可重新激活

无需重新登录或重新设置。运行 `hermes memory setup` 并选择 "honcho"——向导会检测到你的现有配置。

## 完整文档

参见[记忆提供者 — Honcho](./memory-providers.md#honcho) 以获得完整参考。