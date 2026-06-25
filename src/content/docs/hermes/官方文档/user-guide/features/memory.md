---
sidebar_position: 3
title: "持久记忆（Persistent Memory）"
description: "Hermes Agent 如何在会话之间记忆——MEMORY.md、USER.md 和会话搜索"
---

# 持久记忆（Persistent Memory）

Hermes Agent 拥有有限、精心管理的记忆，这些记忆会跨会话持久存在。这使得它能够记住你的偏好、项目、环境以及所学到的东西。

## 工作原理

两份文件构成了代理的记忆：

| 文件 | 用途 | 字符限制 |
|------|---------|------------|
| **MEMORY.md** | 代理的个人笔记——环境事实、约定、学到的东西 | 2,200 字符（约 800 tokens） |
| **USER.md** | 用户档案——你的偏好、沟通风格、期望 | 1,375 字符（约 500 tokens） |

两份文件都存储在 `~/.hermes/memories/` 中，并在会话开始时作为冻结快照注入到系统提示（system prompt）中。代理通过 `memory` 工具管理自己的记忆——它可以添加、替换或删除条目。

:::info
字符限制让记忆保持聚焦。记忆**不会**自动压缩：当写入会超出限制时，`memory` 工具会返回一个错误，而不是静默丢弃条目。然后代理会自行腾出空间——在同一回合中合并或删除条目，然后重试（请参阅[记忆已满时会发生什么](#what-happens-when-memory-is-full)）。请注意，`replace` 也受限于该限制：将一个条目替换为更长的条目仍可能溢出，因此新内容必须缩短（或删除另一个条目）以容纳。
:::

## 记忆在系统提示中的呈现方式

在每个会话开始时，记忆条目从磁盘加载并作为冻结块渲染到系统提示中：

```
══════════════════════════════════════════════
记忆（你的个人笔记）[67% — 1,474/2,200 字符]
══════════════════════════════════════════════
用户的项目是一个位于 ~/code/myapi 的 Rust Web 服务，使用 Axum + SQLx
§
这台机器运行 Ubuntu 22.04，已安装 Docker 和 Podman
§
用户偏好简洁的回答，不喜欢冗长的解释
```

格式包括：
- 一个头部，显示是哪个存储（MEMORY 或 USER PROFILE）
- 使用百分比和字符数，以便代理知道容量
- 用 `§`（节符号）分隔的各个条目
- 条目可以有多行

**冻结快照模式：** 系统提示注入在会话开始时捕获一次，并且在会话期间永远不会改变。这是有意为之——它保留了 LLM 的前缀缓存（prefix cache）以提升性能。当代理在会话期间添加/删除记忆条目时，更改会立即持久化到磁盘，但直到下一个会话开始才会出现在系统提示中。工具响应始终显示实时状态。

## 记忆工具操作

代理使用 `memory` 工具执行以下操作：

- **add** — 添加一条新的记忆条目
- **replace** — 用更新的内容替换现有条目（使用 `old_text` 进行子串匹配）
- **remove** — 删除不再相关的条目（使用 `old_text` 进行子串匹配）

没有 `read` 操作——记忆内容会在会话开始时自动注入到系统提示中。代理将其记忆视为对话上下文的一部分。

### 子串匹配

`replace` 和 `remove` 操作使用短唯一子串匹配——你不需要完整的条目文本。`old_text` 参数只需是一个唯一子串，能识别出恰好一个条目：

```python
# 如果记忆包含 "User prefers dark mode in all editors"
memory(action="replace", target="memory",
       old_text="dark mode",
       content="User prefers light mode in VS Code, dark mode in terminal")
```

如果该子串匹配了多个条目，则会返回一个错误，要求提供更具体的匹配。

## 两个目标的解释

### `memory` — 代理的个人笔记

用于代理需要记住的关于环境、工作流程和经验教训的信息：

- 环境事实（操作系统、工具、项目结构）
- 项目约定和配置
- 发现的工具特性和变通方法
- 已完成任务的日记条目
- 有效的技能和技术

### `user` — 用户档案

用于关于用户身份、偏好和沟通风格的信息：

- 姓名、角色、时区
- 沟通偏好（简洁 vs 详细，格式偏好）
- 讨厌的事情和要避免的事情
- 工作习惯
- 技术技能水平

## 应保存什么 vs 跳过什么

### 保存这些（主动保存）

代理会自动保存——你不需要要求。当它学到以下内容时，它就会保存：

- **用户偏好：** "我更喜欢 TypeScript 而不是 JavaScript" → 保存到 `user`
- **环境事实：** "这个服务器运行 Debian 12 和 PostgreSQL 16" → 保存到 `memory`
- **纠正：** "不要对 Docker 命令使用 `sudo`，用户属于 docker 组" → 保存到 `memory`
- **约定：** "项目使用制表符，120 字符行宽，Google 风格的文档字符串" → 保存到 `memory`
- **已完成的工作：** "于 2026-01-15 将数据库从 MySQL 迁移到 PostgreSQL" → 保存到 `memory`
- **明确请求：** "记住我的 API 密钥按月轮换" → 保存到 `memory`

### 跳过这些

- **琐碎/显而易见的信息：** "用户询问了关于 Python 的问题" — 太模糊，没有用
- **容易重新发现的事实：** "Python 3.12 支持 f-string 嵌套" — 可以网络搜索
- **原始数据转储：** 大型代码块、日志文件、数据表 — 对于记忆来说太大
- **会话特定的临时信息：** 临时文件路径、一次性调试上下文
- **上下文文件中已有的信息：** SOUL.md 和 AGENTS.md 的内容

## 容量管理

记忆有严格的字符限制，以保持系统提示的范围可控：

| 存储 | 限制 | 典型条目数 |
|-------|-------|----------------|
| memory | 2,200 字符 | 8-15 条 |
| user | 1,375 字符 | 5-10 条 |

### 记忆已满时会发生什么

当你尝试添加一条会导致超过限制的条目时，该工具会返回一个错误：

```json
{
  "success": false,
  "error": "Memory at 2,100/2,200 chars. Adding this entry (250 chars) would exceed the limit. Consolidate now: use 'replace' to merge overlapping entries into shorter ones or 'remove' stale or less important entries (see current_entries below), then retry this add — all in this turn.",
  "current_entries": ["..."],
  "usage": "2,100/2,200"
}
```

然后代理应该：
1. 读取当前条目（显示在错误响应中）
2. 识别可以删除或合并的条目
3. 使用 `replace` 将相关条目合并为更短的版本
4. 然后 `add` 新条目

**最佳实践：** 当记忆超过 80% 容量（在系统提示头部可见）时，在添加新条目之前先合并条目。例如，将三个单独的"项目使用 X"条目合并为一个全面的项目描述条目。

### 良好记忆条目的实际示例

**紧凑、信息密集的条目效果最佳：**

```
# 好：将多个相关事实打包在一起
用户运行 macOS 14 Sonoma，使用 Homebrew，已安装 Docker Desktop 和 Podman。Shell：zsh 搭配 oh-my-zsh。编辑器：VS Code 带 Vim 键绑定。

# 好：具体、可操作的约定
项目 ~/code/api 使用 Go 1.22，sqlc 用于数据库查询，chi 路由器。运行测试使用 'make test'。CI 通过 GitHub Actions。

# 好：带有上下文的经验教训
暂存服务器（10.0.1.50）需要使用 SSH 端口 2222，而不是 22。密钥位于 ~/.ssh/staging_ed25519。

# 差：太模糊
用户有一个项目。

# 差：太冗长
2026年1月5日，用户让我查看他们的项目，项目位于 ~/code/api。我发现它使用了 Go 版本 1.22 和...
```

## 重复预防

记忆系统会自动拒绝完全重复的条目。如果你尝试添加已经存在的内容，它会返回成功并显示"未添加重复条目"的消息。

## 安全扫描

记忆条目在被接受之前会扫描注入和泄露模式，因为它们会被注入到系统提示中。匹配威胁模式（提示注入、凭据泄露、SSH 后门）或包含不可见 Unicode 字符的内容将被阻止。

## 会话搜索

除了 MEMORY.md 和 USER.md 之外，代理还可以使用 `session_search` 工具搜索其过去的对话：

- 所有 CLI 和消息会话都存储在 SQLite（`~/.hermes/state.db`）中，并启用 FTS5 全文搜索
- 搜索查询返回来自数据库的实际消息——没有 LLM 摘要，没有截断
- 代理可以找到几周前讨论过的事情，即使它们不在其活跃记忆中
- 代理还可以在其找到的任何会话内向前/向后滚动

```bash
hermes sessions list    # 浏览过去的会话
```

请参阅[会话搜索工具](/user-guide/sessions#session-search-tool)了解三种调用形式（发现 / 滚动 / 浏览）和响应格式。

### session_search 与 memory 对比

| 特性 | 持久记忆（Persistent Memory） | 会话搜索（Session Search） |
|---------|------------------|----------------|
| **容量** | 总共约 1,300 tokens | 无限制（所有会话） |
| **速度** | 即时（在系统提示中） | 约 20ms FTS5 查询，约 1ms 滚动 |
| **成本** | 每次提示的 token 成本 | 免费——无需 LLM 调用 |
| **用例** | 关键事实始终可用 | 查找特定的过去对话 |
| **管理** | 由代理手动管理 | 自动——所有会话都存储 |
| **Token 成本** | 每个会话固定（约 1,300 tokens） | 按需（需要时搜索） |

**记忆**用于那些应该始终在上下文中的关键事实。**会话搜索**用于"我们上周讨论过 X 吗？"的查询，代理需要从过去的对话中回忆具体细节。

## 配置

```yaml
# 在 ~/.hermes/config.yaml 中
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200   # 约 800 tokens
  user_char_limit: 1375     # 约 500 tokens
  write_approval: false     # false = 自由写入（默认）| true = 需要批准
```

## 控制记忆写入（`write_approval`）

默认情况下，代理自由保存记忆——包括在回合后运行的后台自我改进审查。如果你希望先批准保存，请设置 `memory.write_approval: true`。这是一个简单的开关，适用于**前台回合**和**后台审查**：

| `write_approval` | 行为 |
|------------------|-----------|
| `false`（默认） | 自由写入——门是关闭的（门前的行为）。 |
| `true` | 在保存任何内容之前需要批准。在交互式 CLI 中，前台写入会提示你内联（条目足够小，可以完整阅读）。在其他地方——消息平台、脚本和后台自我改进审查——写入会被**暂存**以供审查，使用 `/memory pending`。 |

> 要完全关闭记忆（不仅仅是门控），请设置 `memory_enabled: false`。

从 CLI 或任何消息平台审查暂存的写入：

```
/memory pending             # 列出暂存的记忆写入（自动写入会被标记为 [auto]）
/memory approve <id>        # 应用一个（或 'all'）
/memory reject <id>         # 丢弃一个（或 'all'）
/memory approval on         # 打开门（或 'off'）并持久化
```

这就是对"代理保存了关于我的错误假设"的答案：设置 `write_approval: true`，每次保存——尤其是那些未经提示的后台保存——都会等待你的同意/拒绝，然后才会进入你的档案。

## 后台审查通知（`display.memory_notifications`）

在一个回合之后，后台自我改进审查可能会静默地保存一条记忆或更新一项技能。这是 Hermes 的知情学习循环：重复的纠正和持久的工作流程经验会变成紧凑的记忆条目或程序性技能，而 `write_approval` 可以暂存这些写入，以便在它们影响未来会话之前进行审查。默认情况下，它会在聊天中显式显示一条简短的 `💾 Memory updated` 行，以便你知道发生了。控制其啰嗦程度：

```yaml
display:
  memory_notifications: on    # off | on（默认）| verbose
```

| 值 | 行为 |
|-------|-----------|
| `off` | 不在聊天中通知。审查仍然运行并仍然写入——只是你看不到它的行。 |
| `on`（默认） | 通用行，例如 `💾 Memory updated`，`💾 Skill 'foo' patched`。 |
| `verbose` | 包含一个紧凑的更改预览，例如 `💾 Memory ➕ User prefers terse replies` 或一个 `"old" → "new"` 技能差异片段。 |

> 这仅控制**网关**聊天通知。审查本身以及对你记忆/技能存储的写入不受此设置影响。可以通过 `display.platforms.<platform>.memory_notifications` 按平台设置。

## 在更便宜的模型上运行审查（`auxiliary.background_review`）

默认情况下，审查在你的**主要聊天模型**上运行，重放对话——这在提示缓存中已经是热的，所以缓存读取很便宜。在昂贵的主要模型上，你可以改为在更便宜的模型上运行审查：

```yaml
auxiliary:
  background_review:
    provider: openrouter
    model: google/gemini-3-flash-preview   # auto（默认）= 主要聊天模型
```

当你将其指向与主要模型**不同**的模型时，审查会在那里以更低成本运行（基准测试中约 3-5 倍）。由于不同的模型无法重用你的主要模型的提示缓存，因此分支会自动重放一个紧凑的对话**摘要**（最近的回合逐字记录 + 旧回合的摘要），而不是完整记录——最小化写入新缓存的内容。捕获保持：在测试中，记忆捕获相同，技能捕获与主要模型审查几乎相同。

将其保留为 `auto`（或设置为你的主要模型），则没有任何变化——审查会继续在主要模型上进行，并使用完整的缓存热重放。

## 控制技能写入（`skills.write_approval`）

技能使用相同的开关门，但审查用户体验不同，因为 `SKILL.md` 太大，无法在聊天气泡中阅读：

```yaml
skills:
  write_approval: false     # false = 自由写入（默认）| true = 需要批准
```

当 `write_approval: true` 时，技能写入（创建 / 编辑 / 补丁 / write_file / 删除）无论来源如何，始终**暂存**。你可以在内联中审查一行摘要，但完整差异保持在带外：

```
/skills pending             # 列出暂存的技能写入 + 每一行的摘要
/skills diff <id>           # 完整统一差异（最好在 CLI 或仪表板中查看）
/skills approve <id>        # 应用它（或 'all'）
/skills reject <id>         # 丢弃它（或 'all'）
/skills approval on         # 打开门（或 'off'）并持久化
```

在消息平台上，从其摘要 + 元数据批准一项技能，或者当你想阅读整个更改时，在 CLI / 仪表板 / 暂存文件 `~/.hermes/pending/skills/<id>.json` 中打开 `/skills diff`。完整详情见[门控代理技能写入](/user-guide/features/skills#gating-agent-skill-writes-skillswrite_approval)。

## 外部记忆提供者

对于超出 MEMORY.md 和 USER.md 的更深入、持久的记忆，Hermes 内置了 8 个外部记忆提供者插件——包括 Honcho、OpenViking、Mem0、Hindsight、Holographic、RetainDB、ByteRover 和 Supermemory。

外部提供者**在**内置记忆**旁边**运行（从未取代它），并增加诸如知识图谱、语义搜索、自动事实提取和跨会话用户建模等功能。

```bash
hermes memory setup      # 选择一个提供者并配置它
hermes memory status     # 检查哪个是活动的
```

请参阅[记忆提供者](./memory-providers.md)指南以了解每个提供者的完整详细信息、设置说明和比较。