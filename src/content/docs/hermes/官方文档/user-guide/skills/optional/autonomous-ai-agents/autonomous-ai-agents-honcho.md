---
title: Honcho
---

title: "Honcho"
sidebar_label: "Honcho"
description: "配置并使用 Honcho 记忆系统与 Hermes 集成 —— 跨会话用户建模、多配置文件对等体隔离、观察配置、辩证推理、会话摘要及上下文预算控制。用于设置 Honcho、排查记忆问题、使用 Honcho 对等体管理配置文件，或调整观察、回忆及辩证设置。"
---

--- body ---
{/* 此页面由技能 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，不要编辑此页面。 */}

# Honcho

配置并使用 Honcho 记忆系统与 Hermes 集成 —— 跨会话用户建模、多配置文件对等体隔离、观察配置、辩证推理、会话摘要及上下文预算控制。用于设置 Honcho、排查记忆问题、使用 Honcho 对等体管理配置文件，或调整观察、回忆及辩证设置。

## 技能元数据（Skill metadata）

| | |
|---|---|
| 来源 | 可选 —— 通过 `hermes skills install official/autonomous-ai-agents/honcho` 安装 |
| 路径 | `optional-skills/autonomous-ai-agents/honcho` |
| 版本 | `2.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Honcho`, `Memory`, `Profiles`, `Observation`, `Dialectic`, `User-Modeling`, `Session-Summary` |
| 相关技能 | [`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) |

## 参考：完整 SKILL.md

:::info
以下为当此技能被触发时 Hermes 加载的完整技能定义。这是技能激活时代理看到的指令。
:::

# Honcho 记忆系统用于 Hermes

Honcho 提供 AI 原生跨会话用户建模。它能在多次对话中学习用户身份，并为每个 Hermes 配置文件提供自己的对等体身份，同时共享统一的用户视图。

## 使用时机

- 设置 Honcho（云端或自托管）
- 排查记忆不工作 / 对等体不同步的问题
- 创建多配置文件设置，每个代理拥有独立的 Honcho 对等体
- 调整观察、回忆、辩证深度或写入频率设置
- 了解 5 个 Honcho 工具的功能及使用场景
- 配置上下文预算及会话摘要注入

## 设置

### 云端（app.honcho.dev）

```bash
hermes memory setup honcho
# 选择 "cloud"，粘贴从 https://app.honcho.dev 获取的 API 密钥
```

### 自托管

```bash
hermes memory setup honcho
# 选择 "local"，输入基础 URL（例如 http://localhost:8000）
```

参见：https://docs.honcho.dev/v3/guides/integrations/hermes#running-honcho-locally-with-hermes

### 验证

```bash
hermes honcho status    # 显示解析后的配置、连接测试、对等体信息
```

## 架构

### 基础上下文注入（Base Context Injection）

当 Honcho 将上下文注入系统提示（在 `hybrid` 或 `context` 回忆模式下），它会按以下顺序组装基础上下文块：

1. **会话摘要（Session summary）** —— 当前会话的简短摘要，放在最前面以便模型立即获得会话连续性
2. **用户表征（User representation）** —— Honcho 累积的用户模型（偏好、事实、模式）
3. **AI 对等体卡片（AI peer card）** —— 当前 Hermes 配置文件的 AI 对等体身份卡

会话摘要由 Honcho 在每个回合开始时自动生成（当存在之前的会话时）。它为模型提供温启动，无需回放完整历史。

### 冷/温提示选择

Honcho 自动选择两种提示策略：

| 条件 | 策略 | 行为 |
|-----------|----------|--------------|
| 无先前会话或表征为空 | **冷启动（Cold start）** | 轻量级介绍提示；跳过摘要注入；鼓励模型了解用户 |
| 存在表征和/或会话历史 | **温启动（Warm start）** | 完整基础上下文注入（摘要→表征→卡片）；更丰富的系统提示 |

无需手动配置 —— 基于会话状态自动完成。

### 对等体（Peers）

Honcho 将会话建模为**对等体**之间的交互。Hermes 为每个会话创建两个对等体：

- **用户对等体（User peer）**（`peerName`）：代表人类。Honcho 通过观察消息构建用户表征。
- **AI 对等体（AI peer）**（`aiPeer`）：代表此 Hermes 实例。每个配置文件拥有独立的 AI 对等体，使代理能形成独立视角。

### 观察（Observation）

每个对等体有两个观察开关，控制 Honcho 从何处学习：

| 开关 | 作用 |
|--------|-------------|
| `observeMe` | 观察该对等体自身的消息（构建自我表征） |
| `observeOthers` | 观察其他对等体的消息（构建跨对等体理解） |

默认：四个开关全部**开启**（完全双向观察）。

可在 `honcho.json` 中按对等体配置：

```json
{
  "observation": {
    "user": { "observeMe": true, "observeOthers": true },
    "ai":   { "observeMe": true, "observeOthers": true }
  }
}
```

或使用快捷预设：

| 预设 | 用户 | AI | 使用场景 |
|--------|------|----|----------|
| `"directional"`（默认） | me:开启, others:开启 | me:开启, others:开启 | 多代理，完整记忆 |
| `"unified"` | me:开启, others:关闭 | me:关闭, others:开启 | 单代理，仅用户建模 |

在 [Honcho 仪表板](https://app.honcho.dev) 中更改的设置会在会话初始化时同步回 —— 服务端配置优先于本地默认值。

### 会话（Sessions）

Honcho 会话用于限定消息和观察的存放范围。策略选项：

| 策略 | 行为 |
|----------|----------|
| `per-directory`（默认） | 每个工作目录一个会话 |
| `per-repo` | 每个 git 仓库根目录一个会话 |
| `per-session` | 每次 Hermes 运行时新建 Honcho 会话 |
| `global` | 跨所有目录的单个会话 |

手动覆盖：`hermes honcho map my-project-name`

### 回忆模式（Recall Modes）

代理访问 Honcho 记忆的方式：

| 模式 | 自动注入上下文？ | 工具可用？ | 使用场景 |
|------|---------------------|-----------------|----------|
| `hybrid`（默认） | 是 | 是 | 代理自行决定是否使用工具或自动上下文 |
| `context` | 是 | 否（隐藏） | 最小令牌成本，无工具调用 |
| `tools` | 否 | 是 | 代理显式控制所有记忆访问 |

## 三个正交旋钮

Honcho 的辩证行为由三个独立维度控制。每个维度可独立调节，互不影响：

### 节奏（Cadence）（何时）

控制**多频繁**执行辩证和上下文调用。

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `contextCadence` | `1` | 上下文 API 调用的最小间隔回合数 |
| `dialecticCadence` | `2` | 辩证 API 调用的最小间隔回合数。推荐 1–5 |
| `injectionFrequency` | `every-turn` | `every-turn` 或 `first-turn` 用于基础上下文注入 |

较高的节奏值意味着辩证 LLM 触发的频率更低。`dialecticCadence: 2` 表示引擎每隔一回合触发一次。设为 `1` 则每回合触发。

### 深度（Depth）（多少次）

控制每次查询 Honcho 执行的辩证推理轮数。

| 键 | 默认值 | 范围 | 描述 |
|-----|---------|-------|-------------|
| `dialecticDepth` | `1` | 1-3 | 每次查询的辩证推理轮数 |
| `dialecticDepthLevels` | -- | 数组 | 可选的逐轮深度级别覆盖（见下文） |

`dialecticDepth: 2` 表示 Honcho 运行两轮辩证综合。第一轮产生初步答案；第二轮进行优化。

`dialecticDepthLevels` 允许你为每一轮独立设置推理级别：

```json
{
  "dialecticDepth": 3,
  "dialecticDepthLevels": ["low", "medium", "high"]
}
```

如果省略 `dialecticDepthLevels`，各轮次使用基于 `dialecticReasoningLevel`（基础级别）推导的**比例级别**：

| 深度 | 通过级别 |
|-------|-------------|
| 1 | [基础] |
| 2 | [最低, 基础] |
| 3 | [最低, 基础, 低] |

这样可以在早期轮次保持低成本，同时在最终综合时使用完整深度。

**会话开始时的深度。** 会话开始前的预热会在后台运行完整的配置 `dialecticDepth`，在第一个回合之前进行。对于冷对等体，单次预热通常输出较薄——多轮深度会在用户发言之前执行审计/协调循环。第一个回合直接使用预热结果；如果预热未能及时完成，第一个回合会回退到带有有限超时的同步调用。

### 级别（Level）（多难）

控制每个辩证推理轮次的**强度**。

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `dialecticReasoningLevel` | `low` | `minimal`, `low`, `medium`, `high`, `max` |
| `dialecticDynamic` | `true` | 当为 `true` 时，模型可以向 `honcho_reasoning` 传递 `reasoning_level` 以覆盖每次调用的默认值。`false` = 始终使用 `dialecticReasoningLevel`，忽略模型覆盖 |

级别越高，综合结果越丰富，但在 Honcho 后端消耗的令牌成本也越高。

## 多配置文件设置（Multi-Profile Setup）

每个 Hermes 配置文件拥有独立的 Honcho AI 对等体，同时共享同一个工作空间（用户上下文）。这意味着：

- 所有配置文件看到相同的用户表征
- 每个配置文件构建自己的 AI 身份和观察
- 一个配置文件写入的结论可通过共享工作空间被其他配置文件看到

### 创建带 Honcho 对等体的配置文件

```bash
hermes profile create coder --clone
# 创建 hermes.coder 主机块，AI 对等体 "coder"，继承默认配置
```

`--clone` 对 Honcho 的作用：
1. 在 `honcho.json` 中创建 `hermes.coder` 主机块
2. 设置 `aiPeer: "coder"`（配置文件名称）
3. 从默认配置继承 `workspace`、`peerName`、`writeFrequency`、`recallMode` 等
4. 在 Honcho 中预先创建对等体，使其在第一条消息之前即存在

### 回填现有配置文件

```bash
hermes honcho sync    # 为所有尚未拥有主机块的配置文件创建主机块
```

### 每配置文件配置

在主机块中覆盖任何设置：

```json
{
  "hosts": {
    "hermes.coder": {
      "aiPeer": "coder",
      "recallMode": "tools",
      "dialecticDepth": 2,
      "observation": {
        "user": { "observeMe": true, "observeOthers": false },
        "ai": { "observeMe": true, "observeOthers": true }
      }
    }
  }
}
```

## 工具（Tools）

代理拥有 5 个双向 Honcho 工具（在 `context` 回忆模式下隐藏）：

| 工具 | 需要 LLM 调用？ | 成本 | 使用场景 |
|------|-----------|------|----------|
| `honcho_profile` | 否 | 最低 | 会话开始时快速获取事实快照，或快速查找姓名/角色/偏好 |
| `honcho_search` | 否 | 低 | 获取特定的历史事实供自己推理 —— 原始摘录，无综合 |
| `honcho_context` | 否 | 低 | 完整会话上下文快照：摘要、表征、卡片、最近消息 |
| `honcho_reasoning` | 是 | 中–高 | 由 Honcho 辩证引擎综合生成的自然语言问题答案 |
| `honcho_conclude` | 否 | 最低 | 写入或删除持久化结论；传递 `peer: "ai"` 用于 AI 自我认知 |

### `honcho_profile`
读取或更新对等体卡片 —— 精选的关键事实（姓名、角色、偏好、沟通风格）。传递 `card: [...]` 进行更新；省略则读取。无需 LLM 调用。

### `honcho_search`
对特定对等体的已存储上下文进行语义搜索。返回按相关性排序的原始摘录，无综合。默认 800 令牌，最大 2000。适用于你需要获取特定的历史事实自行推理而非等待综合答案的情况。

### `honcho_context`
来自 Honcho 的完整会话上下文快照 —— 会话摘要、对等体表征、对等体卡片和最近消息。无需 LLM 调用。当你希望一次性看到 Honcho 对当前会话和对等体所知的所有信息时使用。

### `honcho_reasoning`
由 Honcho 的辩证推理引擎（Honcho 后端的 LLM 调用）回答的自然语言问题。成本更高，质量更高。传递 `reasoning_level` 控制深度：`minimal`（快速/低成本）→ `low` → `medium` → `high` → `max`（透彻）。省略则使用配置的默认值（`low`）。用于对用户模式、目标或当前状态的综合理解。

### `honcho_conclude`
写入或删除关于某个对等体的持久化结论。传递 `conclusion: "..."` 创建结论。传递 `delete_id: "..."` 删除结论（用于 PII 移除 —— Honcho 会随时间自动修正不正确的结论，因此仅在涉及 PII 时需要手动删除）。**必须**且只能传递其中一个参数。

### 双向对等体定位

所有 5 个工具都接受可选的 `peer` 参数：
- `peer: "user"`（默认）—— 对用户对等体操作
- `peer: "ai"`—— 对此配置文件的 AI 对等体操作
- `peer: "<explicit-id>"`—— 工作空间中的任何对等体 ID

示例：
```
honcho_profile                        # 读取用户卡片
honcho_profile peer="ai"              # 读取 AI 对等体卡片
honcho_reasoning query="这个用户最关心什么？"
honcho_reasoning query="我的交互模式是什么？" peer="ai" reasoning_level="medium"
honcho_conclude conclusion="偏好简洁的回答"
honcho_conclude conclusion="我倾向于过度解释代码" peer="ai"
honcho_conclude delete_id="abc123"    # PII 移除
```

## 代理使用模式（Agent Usage Patterns）

当 Honcho 记忆激活时，供 Hermes 遵循的指南。

### 会话开始时

```
1. honcho_profile                  → 快速热身，无 LLM 成本
2. 如果上下文显得单薄 → honcho_context  (完整快照，仍无 LLM)
3. 如果需要深度综合 → honcho_reasoning  (LLM 调用，谨慎使用)
```

**不要**在每个回合都调用 `honcho_reasoning`。自动注入已处理持续的上下文刷新。仅在确实需要基础上下文未提供的综合洞察时使用推理工具。

### 当用户分享需要记住的内容

```
honcho_conclude conclusion="<具体、可操作的事实>"
```

好的结论："更喜欢代码示例而非文字解释"，"正在做 Rust 异步项目，持续到 2026 年 4 月"
不好的结论："用户说了些关于 Rust 的话"（过于模糊），"用户看起来懂技术"（已包含在表征中）

### 当用户询问过去的上下文 / 你需要回忆具体信息

```
honcho_search query="<话题>"       → 快速，无 LLM，适用于具体事实
honcho_context                       → 包含摘要和消息的完整快照
honcho_reasoning query="<问题>"  → 综合答案，在搜索不足以满足需求时使用
```

### 何时使用 `peer: "ai"`

使用 AI 对等体定位来构建和查询代理自身的自我认知：
- `honcho_conclude conclusion="我解释架构时倾向于冗长" peer="ai"` —— 自我纠正
- `honcho_reasoning query="我通常如何处理模糊请求？" peer="ai"` —— 自我审计
- `honcho_profile peer="ai"` —— 查看自己的身份卡

### 何时**不**应调用工具

在 `hybrid` 和 `context` 模式下，基础上下文（用户表征+卡片+会话摘要）会在每个回合前自动注入。不要重复获取已注入的内容。仅在以下情况调用工具：
- 你需要注入上下文中没有包含的信息
- 用户明确要求你回忆或检查记忆
- 你正在写入关于新内容的结论

### 节奏感知

工具侧的 `honcho_reasoning` 与自动注入的辩证共享相同成本。在显式工具调用后，自动注入的节奏会重置 —— 避免在同一回合重复计费。

## 配置参考（Config Reference）

配置文件：`$HERMES_HOME/honcho.json`（配置文件本地）或 `~/.honcho/config.json`（全局）。

### 关键设置

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `apiKey` | -- | API 密钥（[获取](https://app.honcho.dev)） |
| `baseUrl` | -- | 自托管 Honcho 的基础 URL |
| `peerName` | -- | 用户对等体身份 |
| `aiPeer` | 主机键 | AI 对等体身份 |
| `workspace` | 主机键 | 共享工作空间 ID |
| `recallMode` | `hybrid` | `hybrid`、`context` 或 `tools` |
| `observation` | 全部开启 | 每对等体的 `observeMe`/`observeOthers` 布尔值 |
| `writeFrequency` | `async` | `async`、`turn`、`session` 或整数 N |
| `sessionStrategy` | `per-directory` | `per-directory`、`per-repo`、`per-session`、`global` |
| `messageMaxChars` | `25000` | 每条消息的最大字符数（超出会拆分） |

### 辩证设置

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `dialecticReasoningLevel` | `low` | `minimal`、`low`、`medium`、`high`、`max` |
| `dialecticDynamic` | `true` | 根据查询复杂度自动提升推理级别。`false` = 固定级别 |
| `dialecticDepth` | `1` | 每次查询的辩证轮数（1-3） |
| `dialecticDepthLevels` | -- | 可选的逐轮级别数组，例如 `["low", "high"]` |
| `dialecticMaxInputChars` | `10000` | 辩证查询输入的最大字符数 |

### 上下文预算与注入（Context budget and injection）

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `contextTokens` | 无上限 | 组合基础上下文注入（摘要+表征+卡片）的最大令牌数。需手动设置上限 —— 省略则无上限，设为整数则限制注入大小。 |
| `injectionFrequency` | `every-turn` | `every-turn` 或 `first-turn` |
| `contextCadence` | `1` | 上下文 API 调用的最小间隔回合数 |
| `dialecticCadence` | `2` | 辩证 LLM 调用的最小间隔回合数（推荐 1–5） |

`contextTokens` 预算在注入时强制执行。如果会话摘要+表征+卡片超出预算，Honcho 会先裁剪摘要，再裁剪表征，保留卡片。这可以防止长会话中的上下文膨胀。

### 记忆上下文消毒

Honcho 在注入前对 `memory-context` 块进行消毒，防止提示注入和格式错误的内容：

- 从用户编写的结论中剥离 XML/HTML 标签
- 标准化空白字符和控制字符
- 截断超过 `messageMaxChars` 的单个结论
- 转义可能破坏系统提示结构的分隔符序列

此修复处理了边缘情况，即原始用户结论包含标记或特殊字符可能破坏注入的上下文块。

## 故障排除（Troubleshooting）

### "Honcho not configured"
运行 `hermes honcho setup`。确保 `~/.hermes/config.yaml` 中包含 `memory.provider: honcho`。

### 记忆在跨会话中不持久
检查 `hermes honcho status` —— 确认 `saveMessages: true` 且 `writeFrequency` 不是 `session`（后者仅在退出时写入）。

### 配置文件没有获得自己的对等体
创建时使用 `--clone`：`hermes profile create <name> --clone`。对于现有配置文件：`hermes honcho sync`。

### 仪表板中的观察更改未生效
观察配置在每次会话初始化时从服务器同步。在 Honcho UI 中更改设置后，启动新会话。

### 消息被截断
超过 `messageMaxChars`（默认 25k）的消息会自动用 `[continued]` 标记拆分。如果频繁遇到此问题，请检查工具结果或技能内容是否导致消息体积过大。

### 上下文注入过大
如果看到上下文预算超限的警告，请降低 `contextTokens` 或减少 `dialecticDepth`。预算紧张时会优先裁剪会话摘要。

### 缺少会话摘要
会话摘要需要在当前 Honcho 会话中至少有一个先前的回合。冷启动（新会话，无历史记录）时，会话摘要将被省略，Honcho 会使用冷启动提示策略。

## CLI 命令（CLI Commands）

| 命令 | 描述 |
|---------|-------------|
| `hermes honcho setup` | 交互式设置向导（云端/本地、身份、观察、回忆、会话） |
| `hermes honcho status` | 显示解析后的配置、连接测试、当前配置文件的对等体信息 |
| `hermes honcho enable` | 为当前配置文件启用 Honcho（如有需要则创建主机块） |
| `hermes honcho disable` | 为当前配置文件禁用 Honcho |
| `hermes honcho peer` | 显示或更新对等体名称（`--user <name>`、`--ai <name>`、`--reasoning <level>`） |
| `hermes honcho peers` | 显示所有配置文件的跨配置文件对等体身份 |
| `hermes honcho mode` | 显示或设置回忆模式（`hybrid`、`context`、`tools`） |
| `hermes honcho tokens` | 显示或设置令牌预算（`--context <N>`、`--dialectic <N>`） |
| `hermes honcho sessions` | 列出已知的目录到会话名称映射 |
| `hermes honcho map <name>` | 将当前工作目录映射到 Honcho 会话名称 |
| `hermes honcho identity` | 设定 AI 对等体身份或显示两个对等体表征 |
| `hermes honcho sync` | 为所有尚未拥有主机块的 Hermes 配置文件创建主机块 |
| `hermes honcho migrate` | 从 OpenClaw 原生记忆迁移到 Hermes + Honcho 的分步指南 |
| `hermes memory setup` | 通用记忆提供者选择器（选择 "honcho" 会运行相同向导） |
| `hermes memory status` | 显示当前活动的记忆提供者及配置 |
| `hermes memory off` | 禁用外部记忆提供者 |