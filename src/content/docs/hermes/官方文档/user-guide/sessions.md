---
sidebar_position: 7
title: "会话"
description: "会话持久化、续传、搜索、管理及按平台追踪会话"
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# 会话（Session）

Hermes 代理（Agent）自动将每次对话保存为一个会话（session）。会话支持对话续传、跨会话搜索以及完整的对话历史管理。

## 会话的工作方式

每次对话——无论是来自 CLI、Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Teams 还是其他消息平台——都会作为会话存储，包含完整的消息历史。会话在以下位置进行追踪：

1. **SQLite 数据库** (`~/.hermes/state.db`) —— 存储结构化会话元数据，支持 FTS5 全文搜索，以及完整的消息历史

SQLite 数据库存储：
- 会话 ID、来源平台、用户 ID
- **会话标题**（唯一、人类可读的名称）
- 模型名称和配置
- 系统提示的快照
- 完整的消息历史（角色、内容、工具调用、工具结果）
- 令牌（token）数量（输入/输出）
- 时间戳（开始时间、结束时间）
- 父会话 ID（用于压缩触发的会话拆分）

### 哪些内容计入上下文（Context）

Hermes 会存储会话历史以便能够续传对话，但不会反复发送它处理过的每一个字节。每次轮次（turn），模型看到的是选定的系统提示、当前的对话窗口（conversation window）以及 Hermes 为该轮次显式注入的任何内容。

媒体附件作为轮次范围内的输入处理：

- 图片可以直接附加到下一次模型调用中，或者当当前模型不支持原生视觉时，先分析成文本描述。
- 当配置了语音转文字（speech-to-text）时，音频会被转录为文本。
- 文本文档可以包含提取出的文本；其他类型的文档通常以保存的本地路径和简短备注表示。
- 附件路径以及提取/派生出的文本可以出现在对话记录中，但原始图片、音频或二进制文件的字节不会重复复制到未来的提示中。

例如，如果用户发送一张图片并要求 Hermes 基于它制作一个迷因（meme），Hermes 可能使用视觉能力检查该图片一次，并运行一个图像处理脚本。未来的轮次不会自动携带原始的 JPEG 作为上下文。它们只携带写入对话的内容，例如用户的请求、简短的图片描述、本地缓存路径或最终的助手回复。

上下文增长的最常见原因并非媒体文件本身，而是冗长的文本：粘贴的对话记录、完整的日志、大型工具输出、长差异（diff）、重复的状态报告以及详细的调试输出。建议优先使用摘要、文件路径、重点摘录以及基于工具（tool）的查询，而不是将大型工件（artifact）复制到聊天中。

:::tip
当会话变得过长时，请使用 `/compress`；如果需要全新的对话线程，使用 `/new`；仅当你想从存储中删除旧的已结束会话时，才使用 `hermes sessions prune`。压缩会减少活动的上下文，但它不是隐私删除。向 `/new` 传递一个名称（例如 `/new payments-refactor`）可以预先设置新会话的初始标题——这便于之后使用 `/resume <name>` 或在 `/sessions` 选择器中找到它。
:::

### 会话来源

每个会话都标记有其来源平台：

| 来源 | 描述 |
|------|-------------|
| `cli` | 交互式 CLI（`hermes` 或 `hermes chat`） |
| `telegram` | Telegram 通讯工具 |
| `discord` | Discord 服务器/私信（DM） |
| `slack` | Slack 工作区 |
| `whatsapp` | WhatsApp 通讯工具 |
| `signal` | Signal 通讯工具 |
| `matrix` | Matrix 房间和私信 |
| `mattermost` | Mattermost 频道 |
| `email` | 电子邮件（IMAP/SMTP） |
| `sms` | 通过 Twilio 的短信 |
| `dingtalk` | 钉钉通讯工具 |
| `feishu` | 飞书/Lark 通讯工具 |
| `wecom` | 企业微信 |
| `weixin` | 微信（个人微信） |
| `bluebubbles` | 通过 BlueBubbles macOS 服务器的 Apple iMessage |
| `qqbot` | QQ 机器人（腾讯 QQ）通过官方 API v2 |
| `homeassistant` | Home Assistant 对话 |
| `webhook` | 入站 Webhook |
| `api-server` | API 服务器请求 |
| `acp` | ACP 编辑器集成 |
| `cron` | 计划任务（cron job） |
| `batch` | 批量处理运行 |

## CLI 会话续传

使用 `--continue` 或 `--resume` 从 CLI 续传之前的对话：

### 续传上次会话

```bash
# 续传最近的 CLI 会话
hermes --continue
hermes -c

# 或者使用 chat 子命令
hermes chat --continue
hermes chat -c
```

这会在 SQLite 数据库中查找最近的 `cli` 会话，并加载其完整的对话历史。

### 按名称续传

如果你已经给会话设置了标题（参见下面的[会话命名](#会话命名)），你可以通过名称续传它：

```bash
# 续传一个命名的会话
hermes -c "my project"

# 如果有衍生变体（my project, my project #2, my project #3），
# 这会自动续传最新的一个
hermes -c "my project"   # → 续传 "my project #3"
```

### 续传特定会话

```bash
# 按 ID 续传特定会话
hermes --resume 20250305_091523_a1b2c3d4
hermes -r 20250305_091523_a1b2c3d4

# 按标题续传
hermes --resume "refactoring auth"

# 或者使用 chat 子命令
hermes chat --resume 20250305_091523_a1b2c3d4
```

会话 ID 会在你退出 CLI 会话时显示，并且可以通过 `hermes sessions list` 查找。

### 续传时的对话回顾（Recap）

当你续传一个会话时，Hermes 会在输入提示之前以样式化的面板显示之前对话的紧凑回顾：

<img className="docs-terminal-figure" src={useBaseUrl('/img/docs/session-recap.svg')} alt="续传 Hermes 会话时显示的“先前对话”回顾面板的风格化预览。" />
<p className="docs-figure-caption">续传模式会在回到实时提示之前显示一个紧凑的回顾面板，包含最近的用户轮次和助手轮次。</p>

回顾会显示：
- **用户消息**（金色 `●`）和**助手回复**（绿色 `◆`）
- **截断**长消息（用户消息 300 字符，助手消息 200 字符或 3 行）
- **折叠工具调用**为带有工具名称的计数（例如，`[3 tool calls: terminal, web_search]`）
- **隐藏**系统消息、工具结果和内部推理
- **限制**为最近的 10 轮对话，并带有 "... N earlier messages ..." 指示
- 使用**暗淡样式**以区别于活跃会话

要禁用回顾并保持单行提示行为，请在 `~/.hermes/config.yaml` 中设置：

```yaml
display:
  resume_display: minimal   # 默认为 full
```

:::tip
会话 ID 的格式为 `YYYYMMDD_HHMMSS_<hex>` —— CLI/TUI 会话使用 6 字符十六进制后缀（例如 `20250305_091523_a1b2c3`），网关会话使用 8 字符后缀（例如 `20250305_091523_a1b2c3d4`）。你可以通过 ID（完整或唯一前缀）或标题来续传 —— 两者均可用于 `-c` 和 `-r`。
:::

## 跨平台移交（Cross-Platform Handoff）

在 CLI 会话中使用 `/handoff <platform>` 将当前对话转移到消息平台的母频道（home channel）。代理会从 CLI 中断的地方精确接续——相同的会话 ID、完整的角色感知对话记录、工具调用等所有内容。

```bash
# 在 CLI 会话内部
/handoff telegram
```

过程如下：

1. CLI 验证 `<platform>` 已启用并设置了母频道（在目标聊天中运行 `/sethome` 配置一次）。
2. CLI 将会话标记为待定，并**阻塞轮询网关**。如果代理正在响应中，它会拒绝——请等待当前回复完成后再执行。
3. 网关监听器（watcher）认领该移交，并要求目标适配器（adapter）创建一个新线程：
   - **Telegram** —— 打开一个新的论坛话题（如果聊天中启用了 Bot API 9.4+ 的 Topics 模式，则为 DM 话题；否则为论坛超级群组话题）。
   - **Discord** —— 在母文字频道下创建一个 1440 分钟自动归档的线程。
   - **Slack** —— 发布一条种子消息，并将其 `ts` 作为线程锚点。
   - **WhatsApp / Signal / Matrix / SMS** —— 没有原生线程，直接降级到母频道。
4. 网关将目标键重新绑定到你现有的 CLI 会话 ID，然后伪造一个合成用户轮次，要求代理确认并总结。回复会发布到新线程中。
5. 当网关确认成功时，CLI 打印一条 `/resume` 提示并干净退出：

   ```
   ↻ Handoff complete. The session is now active on telegram.
     Resume it on this CLI later with: /resume my-session-title
   ```

6. 从此，对话就在该平台上持续。在新线程中回复——该频道中任何获授权的用户都共享同一个会话，并且该线程中的任何后续真实用户消息都会无缝加入，因为线程会话不会根据 `user_id` 键进行区分。

**返回 CLI：** 当你想回到桌面环境时，只需运行 `/resume <title>`（或在 shell 中运行 `hermes -r "<title>"`），即可从平台中断的地方继续。

**失败情况：**
- 没有配置母频道 → CLI 拒绝并提示 `/sethome`。
- 平台未启用/网关未运行 → CLI 在 60 秒后超时，显示明确消息，你的 CLI 会话保持不变。
- 线程创建失败（权限问题、话题模式关闭）→ 直接降级到母频道，移交仍然完成；没有线程隔离，但移交本身有效。
- `adapter.send` 失败（速率限制、临时 API 错误）→ 移交标记为失败并附上原因；行被清除，因此你可以重试。

**值得注意的限制：** 对于不支持线程的多用户群组母频道平台，合成轮次会键为一个 DM 风格的会话。这对于自 DM 母频道（典型设置）有效，但对于真正的共享群组聊天并不理想。线程功能覆盖 Telegram / Discord / Slack —— 这是常见用例 —— 所以大多数设置不会遇到这个问题。

## 会话命名（Session Naming）

为会话赋予人类可读的标题，以便轻松查找和续传。

### 自动生成标题

Hermes 会在第一次对话后自动为每个会话生成一个简短描述性标题（3–7 个词）。这会在后台线程中通过一个快速的辅助模型运行，因此不会增加延迟。你可以在使用 `hermes sessions list` 或 `hermes sessions browse` 浏览会话时看到自动生成的标题。

自动标题生成只触发一次，如果你已经手动设置了标题，则会跳过。

### 手动设置标题

在任何聊天会话（CLI 或网关）内部使用 `/title` 斜杠命令：

```
/title my research project
```

标题会立即生效。如果该会话尚未在数据库中创建（例如，你在发送第一条消息之前运行了 `/title`），它会被排队，并在会话开始时应用。

你也可以从命令行重命名现有会话：

```bash
hermes sessions rename 20250305_091523_a1b2c3d4 "refactoring auth module"
```

### 标题规则

- **唯一** —— 两个会话不能共享相同标题
- **最多 100 个字符** —— 保持列表输出整洁
- **经过清理** —— 控制字符、零宽字符和 RTL 覆盖符会自动删除
- **普通 Unicode 正常** —— 表情符号、中日韩文字、带变音符号的字符均可

### 压缩时的自动衍生

当会话的上下文被压缩时（手动通过 `/compress` 或自动），Hermes 会创建一个新的延续会话。如果原会话有标题，新会话会自动获得一个带数字编号的标题：

```
"my project" → "my project #2" → "my project #3"
```

当你按名称续传时（`hermes -c "my project"`），它会自动选择衍生链中最新的会话。

### 消息平台中的 /title

`/title` 命令在所有网关平台（Telegram、Discord、Slack、WhatsApp）中均可使用：

- `/title My Research` —— 设置会话标题
- `/title` —— 显示当前标题

## 会话管理命令

Hermes 通过 `hermes sessions` 提供一套完整的会话管理命令：

### 列出会话

```bash
# 列出最近的会话（默认：最近 20 个）
hermes sessions list

# 按平台过滤
hermes sessions list --source telegram

# 显示更多会话
hermes sessions list --limit 50
```

当会话有标题时，输出显示标题、预览和相对时间：

```
Title                  Preview                                  Last Active   ID
────────────────────────────────────────────────────────────────────────────────────────────────
refactoring auth       Help me refactor the auth module please   2h ago        20250305_091523_a
my project #3          Can you check the test failures?          yesterday     20250304_143022_e
—                      What's the weather in Las Vegas?          3d ago        20250303_101500_f
```

当没有会话有标题时，使用更简单的格式：

```
Preview                                            Last Active   Src    ID
──────────────────────────────────────────────────────────────────────────────────────
Help me refactor the auth module please             2h ago        cli    20250305_091523_a
What's the weather in Las Vegas?                    3d ago        tele   20250303_101500_f
```

### 导出会话

```bash
# 将所有会话导出到一个 JSONL 文件
hermes sessions export backup.jsonl

# 从特定平台导出会话
hermes sessions export telegram-history.jsonl --source telegram

# 导出一个会话
hermes sessions export session.jsonl --session-id 20250305_091523_a1b2c3d4
```

导出的文件每行包含一个 JSON 对象，包含完整的会话元数据和所有消息。

### 删除会话

```bash
# 删除特定会话（需要确认）
hermes sessions delete 20250305_091523_a1b2c3d4

# 不确认直接删除
hermes sessions delete 20250305_091523_a1b2c3d4 --yes
```

### 重命名会话

```bash
# 设置或更改会话标题
hermes sessions rename 20250305_091523_a1b2c3d4 "debugging auth flow"

# 多词标题在 CLI 中不需要引号
hermes sessions rename 20250305_091523_a1b2c3d4 debugging auth flow
```

如果该标题已被其他会话使用，会显示错误。

### 清理旧会话

```bash
# 删除 90 天前已结束的会话（默认）
hermes sessions prune

# 自定义年龄阈值
hermes sessions prune --older-than 30

# 仅清理来自特定平台的会话
hermes sessions prune --source telegram --older-than 60

# 跳过确认
hermes sessions prune --older-than 30 --yes
```

:::info
清理仅删除**已结束**的会话（已明确结束或自动重置的会话）。活跃会话永远不会被清理。
:::

### 会话统计

```bash
hermes sessions stats
```

输出：

```
Total sessions: 142
Total messages: 3847
  cli: 89 sessions
  telegram: 38 sessions
  discord: 15 sessions
Database size: 12.4 MB
```

如需更深入的分析——令牌用量、成本估算、工具分解和活动模式——请使用 [`hermes insights`](/reference/cli-commands#hermes-insights)。

## 会话搜索工具

代理内置了一个 `session_search` 工具，通过 SQLite 的 FTS5 搜索引擎在所有过往对话中执行全文搜索——并允许代理滚动查看它找到的任何会话。无需 LLM 调用、无需摘要、无需截断。每种调用形式都从数据库返回实际消息。

### 三种调用形式

该工具根据你设置的参数推断你的需求。没有 `mode` 参数。

**1. 发现（Discovery）——传递 `query`：**

```python
session_search(query="auth refactor", limit=3)
```

运行 FTS5，对命中结果按会话衍生链去重，返回前 N 个会话。每个结果包含：

- `session_id`、`title`、`when`、`source`
- `snippet` —— FTS5 高亮的匹配摘要
- `bookend_start` —— 会话开始的前 3 条用户+助手消息（目标/启动）
- `messages` —— FTS5 匹配结果前后各 5 条消息，锚定消息被标记（上下文中的命中）
- `bookend_end` —— 会话末尾的后 3 条用户+助手消息（解决方案/决策）
- `match_message_id`、`messages_before`、`messages_after`

书签（bookends）加窗口共同重构了目标→匹配→解决方案的脉络，而无需支付整个对话记录的消耗。在真实的会话数据库上，典型耗时：15–50 毫秒。

**2. 滚动（Scroll）——传递 `session_id` + `around_message_id`：**

```python
session_search(session_id="20260510_174648_805cc2", around_message_id=590803, window=10)
```

返回以锚点为中心、前后各 `window` 条消息的窗口。不涉及 FTS5，也没有书签——只是消息切片。在发现调用之后使用，当你需要比默认前后 5 条窗口更多上下文时。

- 要**向前**滚动：将 `messages[-1].id` 作为 `around_message_id` 传回
- 要**向后**滚动：将 `messages[0].id` 作为 `around_message_id` 传回
- 边界消息会出现在两个窗口中，作为方向标记
- 当 `messages_before` 或 `messages_after` 小于 `window` 时，说明你位于会话的开始或末尾

每次滚动调用的典型耗时：1–2 毫秒。

**3. 浏览（Browse）——无参数：**

```python
session_search()
```

按时间顺序返回最近的会话（标题、预览、时间戳）。当用户询问“我之前在做什么”但没有指定主题时很有用。

### FTS5 查询语法

关键词模式支持标准的 FTS5 查询语法：

- 简单关键词：`docker deployment`（FTS5 默认为 AND）
- 短语：`"exact phrase"`
- 布尔运算：`docker OR kubernetes`、`python NOT java`
- 前缀：`deploy*`

### 可选参数

- `sort` —— `newest` 或 `oldest`，基于 FTS5 排序之上。省略则仅按相关性排序（默认；适用于探索性回忆）。使用 `newest` 回答“我们上次做的 X 在哪里”类型的问题，使用 `oldest` 回答“X 是如何开始的”类型的问题。
- `role_filter` —— 逗号分隔的角色列表，用于包含。发现调用默认为 `user,assistant`（工具输出通常是噪音）。传递 `user,assistant,tool` 以包含工具输出（调试工具行为），或传递 `tool` 仅搜索工具输出。

### 何时使用它

代理会被提示自动使用会话搜索：

> *“当用户引用过往对话中的内容，或者你怀疑存在相关的先前上下文时，在要求他们重复之前，使用 session_search 来回忆相关内容。”*

典型的触发词：”we did this before“、”remember when“、”last time“、”as I mentioned“，或者任何在当前窗口中未出现的项目/人物/概念。

## 按平台追踪会话

### 网关会话

在消息平台上，会话通过一个从消息来源构建的确定性会话键来标识：

| 聊天类型 | 默认键格式 | 行为 |
|-----------|--------------------|----------|
| Telegram 私信 | `agent:main:telegram:dm:<chat_id>` | 每个私信对话一个会话 |
| Discord 私信 | `agent:main:discord:dm:<chat_id>` | 每个私信对话一个会话 |
| WhatsApp 私信 | `agent:main:whatsapp:dm:<canonical_identifier>` | 每个私信用户一个会话（当存在映射时，LID/电话号码别名合并为一个身份） |
| 群组聊天 | `agent:main:<platform>:group:<chat_id>:<user_id>` | 群组内按用户区分（当平台公开用户 ID 时） |
| 群组线程/话题 | `agent:main:<platform>:group:<chat_id>:<thread_id>` | 共享会话给所有线程参与者（默认）。设置 `thread_sessions_per_user: true` 时为按用户区分。 |
| 频道 | `agent:main:<platform>:channel:<chat_id>:<user_id>` | 频道内按用户区分（当平台公开用户 ID 时） |

当 Hermes 无法获取共享聊天的参与者标识符时，它会退回到该房间的一个共享会话。

### 群组会话共享 vs 隔离

默认情况下，Hermes 在 `config.yaml` 中使用 `group_sessions_per_user: true`。这意味着：

- Alice 和 Bob 可以在同一个 Discord 频道中与 Hermes 对话，而不会共享对话记录
- 一个用户长时间、工具密集的任务不会污染另一个用户的上下文窗口
- 中断处理也保持按用户进行，因为运行中的代理键与隔离的会话键匹配

如果你想要一个共享的“房间大脑”，请设置：

```yaml
group_sessions_per_user: false
```

这会将群组/频道恢复为每个房间一个共享会话，这保留了共享的对话上下文，但也会共享令牌成本、中断状态和上下文增长。

### 会话重置策略

网关会话会根据可配置的策略自动重置：

- **idle** —— 在 N 分钟不活动后重置
- **daily** —— 每天在特定小时重置
- **both** —— 以先到的为准（空闲或每日）
- **none** —— 从不自动重置

在会话自动重置之前，代理会获得一个轮次来保存对话中的任何重要记忆或技能（memory/skill）。

具有**活跃后台进程**的会话永远不会自动重置，无论策略如何。

## 存储位置

| 内容 | 路径 | 描述 |
|------|------|-------------|
| SQLite 数据库 | `~/.hermes/state.db` | 所有会话的元数据 + 消息，附带 FTS5 |
| 网关消息 | `~/.hermes/state.db` | SQLite —— 所有会话消息的规范存储 |
| 网关路由索引 | `~/.hermes/sessions/sessions.json` | 将会话键映射到活跃会话 ID（来源元数据、过期标志） |

SQLite 数据库使用 WAL 模式以支持并发读取和单个写入者，这非常适合网关的多平台架构。

:::warning `sessions.json` 不是会话列表
`~/.hermes/sessions/sessions.json` 是**网关路由索引**——它将消息会话键（`agent:main:<platform>:...`）映射到活跃会话 ID。它只包含网关/消息条目，因此如果你运行消息平台，你只会看到这些（例如 `agent:main:whatsapp:dm:...`）。

这是**预期的**，**并不**意味着你的 CLI 会话丢失了。`hermes sessions list`、`/sessions` 和仪表盘都读取 `state.db`，它保存**所有**会话（CLI、TUI 和网关）。`~/.hermes/sessions/saved/*.json` 中的 `/save` 快照是便利的导出文件，而不是索引。

如果 CLI 会话确实没有出现在 `hermes sessions list` 中，原因是 `state.db` 没有收到它们——运行 `hermes sessions repair` 并检查 CLI 启动时是否有 `⚠ Session store unavailable` 警告，这表示那次运行的 SQLite 持久化失败。
:::

:::note 旧版 JSONL 对话记录
在 `state.db` 成为规范存储之前创建的会话可能在 `~/.hermes/sessions/` 中留有 `*.jsonl` 文件。Hermes 不再写入或读取它们。在确认对应会话存在于 `state.db` 后，可以安全删除它们。
:::

### 数据库模式

`state.db` 中的关键表：

- **sessions** —— 会话元数据（id、source、user_id、model、title、timestamps、token_counts）。标题具有唯一索引（允许 NULL 标题，只有非 NULL 的必须唯一）。
- **messages** —— 完整的消息历史（role、content、tool_calls、tool_name、token_count）
- **messages_fts** —— FTS5 虚拟表，用于消息内容的全文搜索

## 会话过期与清理

### 自动清理

- 网关会话根据配置的重置策略自动重置
- 重置前，代理会保存即将过期会话中的记忆和技能
- 可选自动清理：当 `sessions.auto_prune` 为 `true` 时，在 CLI/网关启动时，结束超过 `sessions.retention_days`（默认 90）天的旧会话会被清理
- 在确实删除行之后，会对 `state.db` 执行 `VACUUM` 以回收磁盘空间（SQLite 在普通 DELETE 操作下不会缩小文件）
- 清理最多每 `sessions.min_interval_hours`（默认 24）小时运行一次；最后运行的时间戳记录在 `state.db` 本身内部，因此同一 `HERMES_HOME` 下的所有 Hermes 进程共享

默认是**关闭**的——会话历史对于 `session_search` 回忆很有价值，静默删除可能让用户意外。在 `~/.hermes/config.yaml` 中启用：

```yaml
sessions:
  auto_prune: true          # 选择加入——默认为 false
  retention_days: 90        # 已结束会话保留这么多天
  vacuum_after_prune: true  # 清理后回收磁盘空间
  min_interval_hours: 24    # 在此间隔内不重复运行清理
```

活跃会话永远不会自动清理，无论其存在多久。

### 手动清理

```bash
# 清理超过 90 天的会话
hermes sessions prune

# 删除特定会话
hermes sessions delete <session_id>

# 清理前先导出（备份）
hermes sessions export backup.jsonl
hermes sessions prune --older-than 30 --yes
```

:::tip
数据库增长缓慢（典型情况：成百上千个会话大约 10-15 MB），并且会话历史为跨过往对话的 `session_search` 回忆提供支持，因此自动清理默认禁用。如果你正在运行高负载的网关/定时任务工作负载，且 `state.db` 显著影响性能（观察到的问题模式：384 MB 的 state.db 包含约 1000 个会话，导致 FTS5 插入和 `/resume` 列表变慢），可以启用它。使用 `hermes sessions prune` 进行一次性清理，而无需打开自动清理。
:::