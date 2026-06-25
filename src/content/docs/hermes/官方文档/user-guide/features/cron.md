--- frontmatter ---
---
sidebar_position: 5
title: "定时任务（Cron）"
description: "使用自然语言调度自动化任务，通过一个 cron 工具管理它们，并附加一个或多个技能（Skill）"
---

--- body ---
# 定时任务（Cron）

使用自然语言或 cron 表达式调度任务自动运行。Hermes 通过一个统一的 `cronjob` 工具（tool）暴露 cron 管理功能，采用动作（action）式操作，而不是独立的 schedule/list/remove 工具。

## cron 现在能做什么

Cron 作业可以：

- 调度一次性或重复任务
- 暂停、恢复、编辑、触发和删除作业
- 为零个、一个或多个技能（skill）附加到作业
- 将结果返回给原始聊天、本地文件或已配置的平台目标
- 在全新的代理（agent）会话中运行，使用常规的静态工具列表
- 在 **无代理模式（no-agent mode）** 下运行——一个按计划运行的脚本，其标准输出直接传递，零 LLM 参与（见下文 [无代理模式（仅脚本作业）](#no-agent-mode-script-only-jobs) 部分）

所有这些都可以通过 `cronjob` 工具直接供 Hermes 使用，因此您可以通过自然语言提问来创建、暂停、编辑和删除作业——无需 CLI。

:::tip
在创建时，一个未固定 provider/model 的作业将遵循 `hermes model` 选择的全局默认值——并且 Hermes **快照（snapshot）** 该 provider 和 model 到作业上。如果后来全局默认值更改，作业将**故障关闭（fails closed）**：它跳过运行，不进行推理调用，并发送警报，要求您显式固定 provider/model（`cronjob action=update job_id=… provider=… model=…`）才能继续。这可以防止无人值守的作业静默继承切换到付费 provider/model 并花费您未预期的费用（#44585）。要让作业故意跟踪您的全局默认值，请在更改后将其固定为新值。对于无人值守运行，`hermes setup --portal` 是摩擦最小的选项，因为 OAuth 刷新是自动的。参见 [Nous Portal](/integrations/nous-portal)。
:::

:::warning
Cron 运行的会话无法递归创建更多 cron 作业。Hermes 在 cron 执行内部禁用 cron 管理工具，以防止失控的调度循环。
:::

## 创建定时任务

### 在聊天中使用 `/cron`

```bash
/cron add 30m "Remind me to check the build"
/cron add "every 2h" "Check server status"
/cron add "every 1h" "Summarize new feed items" --skill blogwatcher
/cron add "every 1h" "Use both skills and combine the result" --skill blogwatcher --skill maps
```

### 从独立 CLI

```bash
hermes cron create "every 2h" "Check server status"
hermes cron create "every 1h" "Summarize new feed items" --skill blogwatcher
hermes cron create "every 1h" "Use both skills and combine the result" \
  --skill blogwatcher \
  --skill maps \
  --name "Skill combo"
```

### 通过自然对话

正常向 Hermes 提问：

```text
Every morning at 9am, check Hacker News for AI news and send me a summary on Telegram.
```

Hermes 会在内部使用统一的 `cronjob` 工具。

## 技能支持的 cron 作业

一个 cron 作业可以在运行提示词（prompt）之前加载一个或多个技能。

### 单个技能

```python
cronjob(
    action="create",
    skill="blogwatcher",
    prompt="Check the configured feeds and summarize anything new.",
    schedule="0 9 * * *",
    name="Morning feeds",
)
```

### 多个技能

技能按顺序加载。提示词成为叠加在这些技能之上的任务指令。

```python
cronjob(
    action="create",
    skills=["blogwatcher", "maps"],
    prompt="Look for new local events and interesting nearby places, then combine them into one short brief.",
    schedule="every 6h",
    name="Local brief",
)
```

当您希望一个定时代理继承可重复使用的工作流程而无需将完整技能文本塞入 cron 提示词本身时，这很有用。

## 在项目目录内运行作业

Cron 作业默认在脱离任何仓库的情况下运行——不加载 `AGENTS.md`、`CLAUDE.md` 或 `.cursorrules`，终端/文件/代码执行工具从网关启动时的工作目录运行。传递 `--workdir`（CLI）或 `workdir=`（工具调用）来更改此行为：

```bash
# 独立 CLI（schedule 和 prompt 是位置参数）
hermes cron create "every 1d at 09:00" \
  "Audit open PRs, summarize CI health, and post to #eng" \
  --workdir /home/me/projects/acme
```

```python
# 从聊天中，通过 cronjob 工具
cronjob(
    action="create",
    schedule="every 1d at 09:00",
    workdir="/home/me/projects/acme",
    prompt="Audit open PRs, summarize CI health, and post to #eng",
)
```

当设置了 `workdir`：

- 来自该目录的 `AGENTS.md`、`CLAUDE.md` 和 `.cursorrules` 被注入系统提示词（发现顺序与交互式 CLI 相同）
- `terminal`、`read_file`、`write_file`、`patch`、`search_files` 和 `execute_code` 都使用该目录作为工作目录
- 路径必须是存在的绝对目录——相对路径和不存在的目录在创建/更新时会被拒绝
- 在编辑时传递 `--workdir ""`（或通过工具传递 `workdir=""`）以清除它并恢复旧行为

:::note 序列化
带有 `workdir` 的作业在调度器 tick 上顺序运行，而不是在并行池中。这是有意为之：cron 工作器通过进程全局终端状态应用作业的 workdir，因此两个 workdir 作业同时运行会互相破坏彼此的 cwd。没有 workdir 的作业仍然像以前一样并行运行。
:::

## 编辑作业

您不需要为了更改作业而删除并重新创建它们。

:::tip 作业引用
下面的 `<job_id>` 占位符（以及[生命周期操作](#lifecycle-actions)中的）也接受作业的名称（不区分大小写）——当您记得 `morning-digest` 但不记得十六进制 ID 时很方便。确切的作业 ID 优先于名称匹配；如果引用不是 ID 且名称匹配多个作业，命令会拒绝并打印候选 ID 以便您消除歧义。
:::

### 聊天

```bash
/cron edit <job_id> --schedule "every 4h"
/cron edit <job_id> --prompt "Use the revised task"
/cron edit <job_id> --skill blogwatcher --skill maps
/cron edit <job_id> --remove-skill blogwatcher
/cron edit <job_id> --clear-skills
```

### 独立 CLI

```bash
hermes cron edit <job_id> --schedule "every 4h"
hermes cron edit <job_id> --prompt "Use the revised task"
hermes cron edit <job_id> --skill blogwatcher --skill maps
hermes cron edit <job_id> --add-skill maps
hermes cron edit <job_id> --remove-skill blogwatcher
hermes cron edit <job_id> --clear-skills
```

注意：

- 重复的 `--skill` 会替换作业附带的技能列表
- `--add-skill` 附加到现有列表而不替换
- `--remove-skill` 移除特定的附带技能
- `--clear-skills` 移除所有附带技能

## 生命周期操作

Cron 作业现在拥有比仅创建/删除更完整的生命周期。

### 聊天

```bash
/cron list
/cron pause <job_id>
/cron resume <job_id>
/cron run <job_id>
/cron remove <job_id>
```

### 独立 CLI

```bash
hermes cron list
hermes cron pause <job_id_or_name>
hermes cron resume <job_id_or_name>
hermes cron run <job_id_or_name>
hermes cron remove <job_id_or_name>
hermes cron edit <job_id_or_name> [...flags]
hermes cron status
hermes cron tick
```

它们的作用：

- `pause` —— 保留作业但停止调度它
- `resume` —— 重新启用作业并计算下一次运行时间
- `run` —— 在下一个调度器 tick 上触发作业
- `remove` —— 完全删除它
- `edit` —— 修改 schedule、prompt、delivery 等

**基于名称的查找。** 所有四个可变动词（`pause`、`resume`、`run`、`remove`、`edit`）以及代理的 `cronjob` 工具现在都接受作业**名称**（不区分大小写）代替十六进制 ID。代理和 CLI 都优先选择确切的 ID 匹配（如果存在）；模糊的名称匹配（多个作业共享相同名称）会被拒绝，并给出完整候选 ID 列表，以便您明确选择一个。名称不是唯一的，因此这个保护很重要——它可以防止当两个作业同名时静默修改错误的作业。

## 工作原理

**Cron 执行由网关守护进程处理。** 网关每 60 秒 tick 一次调度器，在隔离的代理会话中运行任何到期的作业。

```bash
hermes gateway install     # 安装为用户服务
sudo hermes gateway install --system   # Linux：服务器启动时的系统服务
hermes gateway             # 或者在前台运行

hermes cron list
hermes cron status
```

### 网关调度器行为

在每个 tick，Hermes：

1. 从 `~/.hermes/cron/jobs.json` 加载作业
2. 检查 `next_run_at` 与当前时间
3. 为每个到期作业启动一个新的 `AIAgent` 会话
4. 可选地将一个或多个附带技能注入到该新会话中
5. 运行提示词直到完成
6. 传递最终响应
7. 更新运行元数据和下一次调度时间

`~/.hermes/cron/.tick.lock` 的文件锁防止重叠的调度器 tick 双倍运行相同的作业批次。

## 交付选项

调度作业时，您可以指定输出的去向：

| 选项 | 描述 | 示例 |
|--------|-------------|---------|
| `"origin"` | 回到创建作业的位置 | 消息平台上的默认值 |
| `"local"` | 仅保存到本地文件（`~/.hermes/cron/output/`） | CLI 上的默认值 |
| `"telegram"` | Telegram 首页频道 | 使用 `TELEGRAM_HOME_CHANNEL` |
| `"telegram:123456"` | 通过 ID 指定 Telegram 聊天 | 直接交付 |
| `"telegram:-100123:17585"` | 指定的 Telegram 主题 | `chat_id:thread_id` 格式 |
| `"discord"` | Discord 首页频道 | 使用 `DISCORD_HOME_CHANNEL` |
| `"discord:#engineering"` | 指定的 Discord 频道 | 按频道名称 |
| `"slack"` | Slack 首页频道 | |
| `"whatsapp"` | WhatsApp 首页 | |
| `"signal"` | Signal | |
| `"matrix"` | Matrix 首页房间 | |
| `"mattermost"` | Mattermost 首页频道 | |
| `"email"` | 电子邮件 | |
| `"sms"` | 通过 Twilio 的短信 | |
| `"homeassistant"` | Home Assistant | |
| `"dingtalk"` | 钉钉 | |
| `"feishu"` | 飞书/Lark | |
| `"wecom"` | 企业微信 | |
| `"weixin"` | 微信（WeChat） | |
| `"bluebubbles"` | BlueBubbles（iMessage） | |
| `"qqbot"` | QQ 机器人（腾讯 QQ） | |
| `"all"` | 风扇分发到所有已连接的首页频道 | 在触发时解析 |
| `"telegram,discord"` | 风扇分发到特定的一组频道 | 逗号分隔的列表 |
| `"origin,all"` | 交付到原始位置**再加上**每个其他已连接的频道 | 组合任意标记 |

代理的最终响应会自动交付。您不需要在 cron 提示词中调用 `send_message`。

### 路由意图（`all`）

`all` 让您将一个 cron 作业分发到您配置的所有消息频道，而无需逐一枚举名称。它在**触发时解析**，因此一个在您设置 Telegram 之前创建的作业将在您设置 `TELEGRAM_HOME_CHANNEL` 后的下一个 tick 上接入 Telegram。

语义：`all` 展开为每个配置了首页频道的平台。零个也是可以的；作业只是不产生任何交付目标，并在上游记录为交付失败。

`all` 可以与显式目标组合。`origin,all` 交付到原始聊天*再加上*每个其他已连接的首页频道，通过 `(platform, chat_id, thread_id)` 去重。

### Telegram cron 主题（`TELEGRAM_CRON_THREAD_ID`）

当启用 Telegram 主题模式时，根 DM 被保留为系统大厅——发送到那里的回复会被大厅提醒拒绝，并且 `reply_to_message_id` 被丢弃，因此您无法回复落在主聊天中的 cron 消息。

将 cron 指向一个专用的论坛主题：

1. 在 Telegram 中，打开机器人 DM 并创建一个主题，例如命名为 `Cron`。长按主题标题 → **复制链接**；末尾的整数是主题的 `message_thread_id`。
2. 在您的 `.env` 中设置 `TELEGRAM_CRON_THREAD_ID=<那个 id>`。

这仅适用于 cron 交付。`TELEGRAM_HOME_CHANNEL_THREAD_ID`（在其他地方使用，例如重启通知）保持不变。显式的 `deliver="telegram:chat_id:thread_id"` 目标会优先于环境变量。对 cron 消息的回复现在会进入现有的主题会话中，因此您可以直接对其采取行动。

### 响应包装

默认情况下，交付的 cron 输出会带有页眉和页脚，以便收件人知道它来自定时任务：

```
Cronjob Response: Morning feeds
-------------

<agent output here>

Note: The agent cannot see this message, and therefore cannot respond to it.
```

要交付原始代理输出而不带包装，将 `cron.wrap_response` 设置为 `false`：

```yaml
# ~/.hermes/config.yaml
cron:
  wrap_response: false
```

### 可继续的作业（回复 cron 交付）

默认情况下，cron 交付是一次性的（fire-and-forget）：消息被发送，但它不在聊天的对话历史中，因此如果您回复它，代理没有它说过什么的记录。将作业设置为**可继续的（continuable）**，交付的简报就会变成一个您可以回复的对话——代理在上下文中拥有简报，而不是问“任务 #2 是什么？”

选择加入，**默认关闭**。在配置中全局启用，或通过 `cronjob` 工具的 `attach_to_session` 按作业启用（该设置会覆盖该作业的全局设置）：

```yaml
# ~/.hermes/config.yaml
cron:
  mirror_delivery: false   # 设置为 true 使 cron 交付可继续
```

行为是**主题优先的（thread-preferred）**，限定在作业的原始聊天范围内：

- **支持主题的平台**（Telegram 主题、Discord/Slack 线程）：每次交付都会打开其专用的线程，并且简报被植入该线程的会话中，因此线程内的回复会继续具有完整上下文。重复作业（例如每日简报）每次运行都会打开一个新线程，保持每次交付的后续讨论隔离。
- **仅 DM 平台**（WhatsApp, Signal, SMS）：不存在线程，因此简报改为镜像到原始 DM 会话中——DM 本身是继续的界面。

只有原始聊天会被触及：扇出/广播目标（`all`、显式的其他聊天交付）永远不会被设置为可继续。镜像被编写为带标签的用户轮次（`[Cron delivery: <任务名>]`），这保持了所有模型提供商的对话历史交替安全。

### 静默抑制

如果代理的最终响应包含 `[SILENT]`，则交付完全被抑制。输出仍然本地保存以便审计（在 `~/.hermes/cron/output/` 中），但不会向交付目标发送消息。

这对于仅应在出现问题时报告的监控作业很有用：

```text
Check if nginx is running. If everything is healthy, respond with only [SILENT].
Otherwise, report the issue.
```

失败的作业始终会交付，无论 `[SILENT]` 标记如何——只有成功的运行可以被静默。对于安静的监控作业，提示代理在无报告内容时仅回复 `[SILENT]`。

## 脚本超时

预运行脚本（通过 `script` 参数附加）的默认超时为 120 秒。如果您的脚本需要更长时间——例如，包含随机延迟以避免类似机器人的定时模式——您可以增加此值：

```yaml
# ~/.hermes/config.yaml
cron:
  script_timeout_seconds: 300   # 5 分钟
```

或设置 `HERMES_CRON_SCRIPT_TIMEOUT` 环境变量。解析顺序为：环境变量 → config.yaml → 120s 默认值。

## 无代理模式（仅脚本作业）

对于不需要 LLM 推理的重复作业——经典的看门狗、磁盘/内存警报、心跳、CI ping——在创建时传递 `no_agent=True`。调度器按计划运行您的脚本并直接传递其标准输出，完全跳过代理：

```bash
hermes cron create "every 5m" \
  --no-agent \
  --script memory-watchdog.sh \
  --deliver telegram \
  --name "memory-watchdog"
```

语义：

- 脚本标准输出（修剪后）→ 直接作为消息传递。
- **空标准输出 → 静默 tick**，不交付。这是看门狗模式：“只有当有问题时才说点什么”。
- 非零退出或超时 → 发送错误警报，因此损坏的看门狗不能静默失败。
- 最后一行 `{"wakeAgent": false}` → 静默 tick（与 LLM 作业使用的相同门控）。
- 无 tokens、无 model、无 provider 回退——作业从不触及推理层。

`.sh` / `.bash` 文件在 `/bin/bash` 下运行；其他任何文件使用当前 Python 解释器（`sys.executable`）。脚本必须位于 `~/.hermes/scripts/` 中（与预运行脚本门控相同的沙盒规则）。

### 代理为您设置这些

`cronjob` 工具的 schema 直接将 `no_agent` 暴露给 Hermes，因此您可以在聊天中描述一个看门狗，让代理连接起来：

```text
Ping me on Telegram if RAM is over 85%, every 5 minutes.
```

Hermes 会通过 `write_file` 将检查脚本写入 `~/.hermes/scripts/`，然后调用：

```python
cronjob(action="create", schedule="every 5m",
        script="memory-watchdog.sh", no_agent=True,
        deliver="telegram", name="memory-watchdog")
```

当消息内容完全由脚本确定时（看门狗、阈值警报、心跳），它会自动选择 `no_agent=True`。同一工具还允许代理暂停、恢复、编辑和删除作业——因此整个生命周期由聊天驱动，无需任何人触碰 CLI。

参见 [仅脚本 Cron 作业指南](/guides/cron-script-only) 获取示例。

## 使用 `context_from` 链接作业

Cron 作业在隔离的会话中运行，没有之前运行的记忆。但有时一个作业的输出正是下一个作业所需要的。`context_from` 参数自动连接该连接——作业 B 的提示词在运行时会被附加作业 A 的最新输出作为上下文。

```python
# 作业 1：收集原始数据
cronjob(
    action="create",
    prompt="Fetch the top 10 AI/ML stories from Hacker News. Save them to ~/.hermes/data/briefs/raw.md in markdown format with title, URL, and score.",
    schedule="0 7 * * *",
    name="AI News Collector",
)

# 作业 2：分类——接收作业 1 的输出作为上下文
# 从 cronjob(action="list") 获取作业 1 的 ID
cronjob(
    action="create",
    prompt="Read ~/.hermes/data/briefs/raw.md. Score each story 1–10 for engagement potential and novelty. Output the top 5 to ~/.hermes/data/briefs/ranked.md.",
    schedule="30 7 * * *",
    context_from="<job1_id>",
    name="AI News Triage",
)

# 作业 3：发送——接收作业 2 的输出作为上下文
cronjob(
    action="create",
    prompt="Read ~/.hermes/data/briefs/ranked.md. Write 3 tweet drafts (hook + body + hashtags). Deliver to telegram:7976161601.",
    schedule="0 8 * * *",
    context_from="<job2_id>",
    name="AI News Brief",
)
```

**工作原理：**

- 当作业 2 触发时，Hermes 从 `~/.hermes/cron/output/{job1_id}/*.md` 读取作业 1 的最新输出
- 该输出自动附加到作业 2 的提示词前
- 作业 2 不需要硬编码“读取此文件”——它以上下文形式接收内容
- 链可以是任意长度：作业 1 → 作业 2 → 作业 3 → ...

**`context_from` 接受的内容：**

| 格式 | 示例 |
|--------|---------|
| 单个作业 ID（字符串） | `context_from="a1b2c3d4"` |
| 多个作业 ID（列表） | `context_from=["job_a", "job_b"]` |

输出按列出的顺序拼接。

**何时使用：**

- 多阶段流水线（收集 → 过滤 → 格式化 → 交付）
- 依赖任务，其中步骤 N 的工作依赖于步骤 N−1 的输出
- 扇出/扇入模式，其中一个作业聚合来自多个其他作业的结果

## 提供商恢复

Cron 作业继承您配置的回退提供商和凭据池轮换。如果主要 API 密钥被限流或提供商返回错误，cron 代理可以：

- **回退到备用提供商**，如果您在 `config.yaml` 中配置了 `fallback_providers`（或旧版 `fallback_model`）
- **轮换到下一个凭据**，来自同一提供商的[凭据池](/user-guide/configuration#credential-pool-strategies)

这意味着在高峰时间或高频运行的 cron 作业更具弹性——单个被限流的密钥不会导致整个运行失败。

## 调度格式

代理的最终响应会自动交付——您**不需要**在 cron 提示词中包含 `send_message` 到同一目标。如果 cron 运行调用 `send_message` 到调度器将交付的确切目标，Hermes 会跳过该重复发送，并告诉模型将面向用户的内容放在最终响应中。仅对其他或附加目标使用 `send_message`。

### 相对延迟（一次性）

```text
30m     → 30 分钟后运行一次
2h      → 2 小时后运行一次
1d      → 1 天后运行一次
```

### 间隔（重复）

```text
every 30m    → 每 30 分钟
every 2h     → 每 2 小时
every 1d     → 每天
```

### Cron 表达式

```text
0 9 * * *       → 每天上午 9:00
0 9 * * 1-5     → 工作日每天上午 9:00
0 */6 * * *     → 每 6 小时
30 8 1 * *      → 每月第一天上午 8:30
0 0 * * 0       → 每星期日午夜
```

### ISO 时间戳

```text
2026-03-15T09:00:00    → 一次性，2026 年 3 月 15 日上午 9:00
```

## 重复行为

| 调度类型 | 默认重复次数 | 行为 |
|--------------|----------------|----------|
| 一次性（`30m`，时间戳） | 1 | 运行一次 |
| 间隔（`every 2h`） | 永远 | 运行直到被移除 |
| Cron 表达式 | 永远 | 运行直到被移除 |

您可以覆盖它：

```python
cronjob(
    action="create",
    prompt="...",
    schedule="every 2h",
    repeat=5,
)
```

## 以编程方式管理作业

面向代理的 API 是一个工具：

```python
cronjob(action="create", ...)
cronjob(action="list")
cronjob(action="update", job_id="...")
cronjob(action="pause", job_id="...")
cronjob(action="resume", job_id="...")
cronjob(action="run", job_id="...")
cronjob(action="remove", job_id="...")
```

对于 `update`，传递 `skills=[]` 以移除所有附加的技能。

## cron 作业可用的工具集

Cron 在每个作业的新代理会话中运行，没有附加任何聊天平台。默认情况下，cron 代理获得**您在 `hermes tools` 中为 `cron` 平台配置的工具集（toolset）**——而不是 CLI 默认值，也不是所有工具。

```bash
hermes tools
# → 在 curses UI 中选择 "cron" 平台
# → 像对 Telegram/Discord 等一样切换工具集开关
```

通过 `cronjob.create`（或通过 `cronjob.update` 修改现有作业）上的 `enabled_toolsets` 字段可以实现更精细的按作业控制：

```text
cronjob(action="create", name="weekly-news-summary",
        schedule="every sunday 9am",
        enabled_toolsets=["web", "file"],      # 仅 web + file，无 terminal/browser 等
        prompt="Summarize this week's AI news: ...")
```

当作业上设置了 `enabled_toolsets` 时，它优先；否则 `hermes tools` 的 cron 平台配置优先；否则 Hermes 回退到内置默认值。这对于成本控制很重要：将 `moa`、`browser`、`delegation` 带入每个微小的“获取新闻”作业会膨胀每个 LLM 调用上的工具 schema 提示词。

### 完全跳过代理：`wakeAgent`

如果您的 cron 作业附加了预检查脚本（通过 `script=`），脚本可以在运行时决定 Hermes 是否应该调用代理。输出标准输出的最后一行，格式为：

```text
{"wakeAgent": false}
```

...cron 会在本次 tick 中完全跳过代理运行。对于频繁轮询（每 1-5 分钟）很有用，这些轮询仅在状态实际更改时才需要唤醒 LLM——否则您会为没有内容的代理轮次反复付费。

```python
# 预检查脚本
import json, sys
latest = fetch_latest_issue_count()
prev = read_state("issue_count")
if latest == prev:
    print(json.dumps({"wakeAgent": False}))   # 跳过此 tick
    sys.exit(0)
write_state("issue_count", latest)
print(json.dumps({"wakeAgent": True, "context": {"new_issues": latest - prev}}))
```

当省略 `wakeAgent` 时，默认值为 `true`（照常唤醒代理）。

#### 配方：廉价的预运行门控

`wakeAgent` 门控为您提供了一种 $0 的方式来决定定时作业是否应花费任何 LLM tokens。三种模式涵盖了大多数用例。

**文件更改门控**——仅在监视的文件自上次成功 tick 后有新内容时才运行。调度器记录每个作业的 `last_run_at`；将其与文件的 mtime 比较。

```bash
#!/bin/bash
# ~/.hermes/scripts/feed-changed.sh
FEED="$HOME/data/feed.json"
STATE="$HOME/.hermes/scripts/.feed-changed.last"
test -f "$FEED" || { echo '{"wakeAgent": false}'; exit 0; }
mtime=$(stat -c %Y "$FEED")
last=$(cat "$STATE" 2>/dev/null || echo 0)
if [ "$mtime" -le "$last" ]; then
  echo '{"wakeAgent": false}'
else
  echo "$mtime" > "$STATE"
  echo '{"wakeAgent": true}'
fi
```

```text
cronjob(action="create", name="process-feed",
        schedule="every 30m",
        script="feed-changed.sh",
        prompt="A new ~/data/feed.json has landed. Summarize what changed.")
```

**外部标志门控**——仅当其他进程已发出就绪信号时才运行（例如部署钩子放下一个文件，CI 作业在您的状态存储中设置一个值）。

```bash
#!/bin/bash
# ~/.hermes/scripts/flag-ready.sh
if test -f /tmp/new-data-ready; then
  rm -f /tmp/new-data-ready
  echo '{"wakeAgent": true}'
else
  echo '{"wakeAgent": false}'
fi
```

```text
cronjob(action="create", name="nightly-analysis",
        schedule="0 9 * * *",
        script="flag-ready.sh",
        prompt="Run the nightly analysis over today's batch.")
```

**SQL 计数门控**——仅在您的数据库中有新的行要处理时才运行。脚本还可以通过 `context` 将计数传递给代理，以便代理知道它正在查看多少数据而无需重新查询。

```python
#!/usr/bin/env python
# ~/.hermes/scripts/new-rows.py
import json, sqlite3
conn = sqlite3.connect("/home/me/data/app.db")
n = conn.execute(
    "SELECT COUNT(*) FROM messages WHERE ts > strftime('%s','now','-2 hours')"
).fetchone()[0]
if n < 1:
    print(json.dumps({"wakeAgent": False}))
else:
    print(json.dumps({"wakeAgent": True, "context": {"new_rows": n}}))
```

```text
cronjob(action="create", name="summarize-new-msgs",
        schedule="every 2h",
        script="new-rows.py",
        prompt="Summarize the new messages from the last 2 hours.")
```

相同的模式适用于任何可以从脚本查询的数据源——Postgres、HTTP API、您自己的状态存储——而无需将 SQL 求值器烘焙到 cron 子系统中。

:::tip
Hermes 自己的 `~/.hermes/state.db` 是内部 schema，在不同版本之间会发生变化。不要从预运行门控查询它——请指向您自己的数据库或 feed。
:::

致谢：此配方集由 @iankar8 在 [#2654](https://github.com/NousResearch/hermes-agent/pull/2654) 中的探索提示，该探索提议添加 sql/file/command 触发器作为并行机制。`script` + `wakeAgent` 门控已经以 $0 覆盖了这三种情况，因此相关工作落地为文档而不是代码。

### 链接作业：`context_from`

一个 cron 作业可以通过在 `context_from` 中列出它们的名称（或 ID）来消费一个或多个其他作业的最新成功输出：

```text
cronjob(action="create", name="daily-digest",
        schedule="every day 7am",
        context_from=["ai-news-fetch", "github-prs-fetch"],
        prompt="Write the daily digest using the outputs above.")
```

被引用作业的最新完成输出会被注入到该运行的提示词之上作为上下文。每个上游条目必须是一个有效的作业 ID 或名称（见 `cronjob action="list"`）。注意：链式读取*最新完成的*输出——它不会等待在同一 tick 中运行的上游作业。

## 作业存储

作业存储在 `~/.hermes/cron/jobs.json` 中。作业运行的输出保存到 `~/.hermes/cron/output/{job_id}/{timestamp}.md`。

作业可能将 `model` 和 `provider` 存储为 `null`。当这些字段被省略时，Hermes 在执行时从全局配置中解析它们。只有当设置了按作业覆盖时，它们才会出现在作业记录中。

存储使用原子文件写入，因此中断的写入不会留下部分写入的作业文件。

## 自包含提示词仍然重要

:::warning 重要
Cron 作业在完全全新的代理会话中运行。提示词必须包含代理所需的一切，这些内容不是由附加技能提供的。
:::

**不好：** `"Check on that server issue"`

**好：** `"SSH into server 192.168.1.100 as user 'deploy', check if nginx is running with 'systemctl status nginx', and verify https://example.com returns HTTP 200."`

## 安全

在创建和更新时，定时任务提示词会被扫描是否存在提示注入和凭据泄露模式。包含不可见 Unicode 技巧、SSH 后门尝试或明显秘密泄露负载的提示词会被阻止。