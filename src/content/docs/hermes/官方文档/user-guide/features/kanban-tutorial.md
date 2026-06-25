---
title: 看板教程
description: Hermes Agent 官方文档汉化版
---

# 看板（Kanban）教程

本教程将通过四个用例详细讲解 Hermes 看板（Kanban）系统的设计功能，你可以在浏览器中打开仪表盘（Dashboard）进行跟随操作。如果你还没有阅读[看板（Kanban）概览](./kanban)，建议先阅读该文档——本教程假设你已经了解任务（Task）、运行（Run）、分配人（Assignee）和调度器（Dispatcher）的含义。

## 设置

```bash
hermes kanban init           # 可选；首次执行 `hermes kanban <任何命令>` 会自动初始化
hermes dashboard             # 在浏览器中打开 http://127.0.0.1:9119
# 点击左侧导航栏中的 Kanban
```

仪表盘（Dashboard）是 **你** 观察系统最舒适的入口。调度器（Dispatcher）生成的工作者（Worker）代理永远不会看到仪表盘或 CLI——它们通过专用的 `kanban_*` [工具集](./kanban#how-workers-interact-with-the-board)（`kanban_show`, `kanban_list`, `kanban_complete`, `kanban_block`, `kanban_heartbeat`, `kanban_comment`, `kanban_create`, `kanban_link`, `kanban_unblock`）来驱动看板。仪表盘、CLI 和工作者的工具都路由到同一个基于看板的 SQLite 数据库（默认看板使用 `~/.hermes/kanban.db`，你之后创建的任何看板使用 `~/.hermes/kanban/boards/<slug>/kanban.db`），因此无论变更来自哪个侧面，每个看板的数据都是一致的。

本教程全程使用 `default` 看板。如果你需要多个独立的队列（每个项目/仓库/领域一个），请参阅概览中的[看板（多项目）](./kanban#boards-multi-project)——每个看板适用相同的 CLI / 仪表盘 / 工作者流程，并且工作者在物理上无法看到其他看板上的任务。

在本教程中，**标记为 `bash` 的代码块表示 *你* 需要运行的命令。** 标记为 `# worker tool calls` 的代码块显示生成的工作者模型发出的工具调用——这里展示出来是为了让你看到端到端的循环，而不是因为你需要亲自运行它们。

## 看板概览

![看板总览](/img/kanban-tutorial/01-board-overview.png)

从左到右共有六列：

- **待分类（Triage）**——原始想法。默认情况下，调度器（Dispatcher）会自动对此列中的任务运行**分解器（Decomposer）**：内置的分解器使用 `auxiliary.kanban_decomposer`，读取你的配置文件中的人物简介（Profile）名册和描述，然后生成一个子任务图谱，路由给最匹配的专家。原始任务作为父任务保持存活，以便其分配人（`kanban.orchestrator_profile`，或未设置时的默认活跃 profile）在所有子任务完成后唤醒并判断是否完成。点击看板页面顶部的 **编排（Orchestration）：自动/手动** 按钮可以切换模式。在手动模式下，点击卡片上的 **⚗ 分解**，或运行 `hermes kanban decompose <id>` / `/kanban decompose <id>`。对于不需要展开的单个任务，**✨ 详细说明** 会执行一次性说明重写（目标、方法、验收标准）并提升到 `todo`。在 `config.yaml` 的 `auxiliary.kanban_decomposer` 和 `auxiliary.triage_specifier` 下配置模型。参见主看板指南中的[自动 vs 手动编排](./kanban#auto-vs-manual-orchestration)。
- **待办（Todo）**——已创建但正在等待依赖项，或尚未分配。
- **就绪（Ready）**——已分配，正在等待调度器（Dispatcher）认领。
- **进行中（In progress）**——工作者（Worker）正在积极运行该任务。如果启用了“按角色分泳道”（默认启用），此列会按分配人分组，让你一目了然地看到每个工作者在做什么。
- **阻塞（Blocked）**——工作者询问了人类输入，或断路器（Circuit breaker）触发了。
- **完成（Done）**——已完成。

顶部栏包含搜索、租户和分配人的筛选器，以及一个`按角色分泳道`切换按钮和一个`催促调度器`按钮（点击后立即执行一次调度，而不是等待守护进程的下一个间隔）。点击任意卡片会在右侧打开其抽屉视图。

### 平面视图

如果角色泳道太杂乱，可以关闭“按角色分泳道”开关，这样“进行中”列会折叠成一个按认领时间排序的平面列表：

![关闭按角色分泳道的看板](/img/kanban-tutorial/02-board-flat.png)

## 故事 1——独立开发者发布一个功能

你正在开发一个功能。经典流程：设计数据库模式，实现API，编写测试。三个任务，具有父子依赖关系。

```bash
SCHEMA=$(hermes kanban create "设计认证模式" \
    --assignee backend-dev --tenant auth-project --priority 2 \
    --body "为认证模块设计用户/会话/令牌模式。" \
    --json | jq -r .id)

API=$(hermes kanban create "实现认证API端点" \
    --assignee backend-dev --tenant auth-project --priority 2 \
    --parent $SCHEMA \
    --body "POST /register, POST /login, POST /refresh, POST /logout。" \
    --json | jq -r .id)

hermes kanban create "编写认证集成测试" \
    --assignee qa-dev --tenant auth-project --priority 2 \
    --parent $API \
    --body "覆盖快乐路径、错误密码、过期令牌、并发刷新。"
```

由于 `API` 以 `SCHEMA` 为父任务，而 `tests` 以 `API` 为父任务，因此只有 `SCHEMA` 一开始处于 `ready` 状态。另外两个任务在它们的父任务完成之前会一直停留在 `todo` 状态。这就是依赖提升引擎（Dependency promotion engine）的作用——在有 API 可以测试之前，不会有其他工作者去编写测试。

在下一次调度器（Dispatcher）滴答（默认60秒，或者如果你点击了**催促调度器**则立即执行）时，`backend-dev` 角色会生成一个工作者，其环境变量中设置了 `HERMES_KANBAN_TASK=$SCHEMA`。以下是工作者工具调用循环从代理内部看起来的样子：

```python
# 工作者工具调用——不是你运行的命令
kanban_show()
# → 返回标题、正文、工作者上下文、父任务、先前尝试、评论

# (工作者读取工作者上下文，使用终端/文件工具设计模式，
#  编写迁移脚本，运行自己的检查，提交——实际工作在此处完成)

kanban_heartbeat(note="模式已起草，正在编写迁移脚本")

kanban_complete(
    summary="users(id, email, pw_hash), sessions(id, user_id, jti, expires_at); "
            "刷新令牌存储为类型为'refresh'的会话",
    metadata={
        "changed_files": ["migrations/001_users.sql", "migrations/002_sessions.sql"],
        "decisions": ["使用bcrypt进行哈希", "使用JWT作为会话令牌",
                      "刷新令牌7天，访问令牌15分钟"],
    },
)
```

`kanban_show` 默认 `task_id` 为 `$HERMES_KANBAN_TASK`，因此工作者不需要知道自己的ID。`kanban_complete` 将摘要和元数据写入当前的 `task_runs` 行，关闭该运行，并将任务转换为 `done`——所有这些都通过 `kanban_db` 以原子跳跃完成。

当 `SCHEMA` 进入 `done` 状态时，依赖引擎会自动将 `API` 提升为 `ready` 状态。API工作者在接手时会调用 `kanban_show()` 并看到父任务交接的 `SCHEMA` 的摘要和元数据——因此它知道模式决策，无需重新阅读长篇设计文档。

点击看板上已完成的任务，抽屉会显示所有信息：

![独立开发者——已完成模式任务抽屉](/img/kanban-tutorial/03-drawer-schema-task.png)

底部的“运行历史”部分是关键新增项。一次尝试：结果 `completed`，工作者 `@backend-dev`，持续时间，时间戳，以及完整的交接摘要。元数据块（`changed_files`，`decisions`）也存储在运行中，并展示给任何读取此父任务的下游工作者。

你可以随时在终端中检查相同的数据——这些命令是 **你** 窥探看板，而不是工作者：

```bash
hermes kanban show $SCHEMA
hermes kanban runs $SCHEMA
# #  结果        角色           耗时  开始时间
# 1  completed   backend-dev     0s  2026-04-27 19:34
#     → users(id, email, pw_hash), sessions(id, user_id, jti, expires_at); refresh tokens ...
```

## 故事 2——并行任务群

你有三个工作者（一个翻译人员，一个转录员，一个文案撰写人）和一堆独立的任务。你希望所有三个工作者同时拉取任务并显示可见的进度。这是最简单的看板用例，也是原始设计优化的重点。

创建工作：

```bash
for lang in Spanish French German; do
    hermes kanban create "将主页翻译为$lang" \
        --assignee translator --tenant content-ops
done
for i in 1 2 3 4 5; do
    hermes kanban create "转录Q3客户通话#$i" \
        --assignee transcriber --tenant content-ops
done
for sku in 1001 1002 1003 1004; do
    hermes kanban create "生成产品描述：SKU-$sku" \
        --assignee copywriter --tenant content-ops
done
```

启动网关（Gateway）并离开——它托管内置调度器（Dispatcher），该调度器会拾取同一个 kanban.db 上所有三个专家角色的任务：

```bash
hermes gateway start
```

现在将看板过滤为 `content-ops`（或直接搜索“Transcribe”），你会得到如下视图：

![并行任务视图，过滤为转录任务](/img/kanban-tutorial/07-fleet-transcribes.png)

两个转录任务已完成，一个正在运行，两个就绪等待下一个调度器滴答。进行中列按角色分组（默认启用“按角色分泳道”），因此你可以看到每个工作者的活动任务，而无需扫描混合列表。一旦当前任务完成，调度器会将下一个就绪任务提升为运行状态。三个守护进程并行处理三个分配人池，整个内容队列会无需进一步人工输入而完成。

**故事1中关于结构化交接的所有内容在此同样适用。** 翻译工作者在完成一次调用时会发出 `kanban_complete(summary="翻译了4页，风格匹配现有营销语气", metadata={"duration_seconds": 720, "tokens_used": 2100})` ——这对于分析以及任何依赖此任务的下游任务都很有用。

## 故事 3——带重试的角色管道

这是看板相对于普通待办列表的优势所在。项目经理（PM）编写规范。工程师实现它。评审员拒绝第一次尝试。工程师根据修改意见再次尝试。评审员批准。

看板视图，过滤为 `auth-project`：

![多角色功能的管道视图](/img/kanban-tutorial/08-pipeline-auth.png)

三个阶段的链条一目了然：`规范：密码重置流程`（已完成，pm），`实现密码重置流程`（已完成，backend-dev），`审查密码重置PR`（就绪，reviewer）。每个任务在底部有绿色标记的父任务，以及作为依赖的子任务。

有趣的是实现任务，因为它曾经被阻塞并进行了重试。以下是完整的三个代理编排，显示每个工作者模型发出的工具调用：

```python
# --- PM工作者在$SPEC上生成并编写验收标准 ---
# 工作者工具调用
kanban_show()
kanban_complete(
    summary="规范已批准；POST /forgot-password发送电子邮件，"
            "GET /reset/:token渲染表单，POST /reset应用新密码",
    metadata={"acceptance": [
        "过期令牌返回410",
        "重复使用最近3个密码返回400并附带消息",
        "成功重置会使所有活动会话失效",
    ]},
)
# → $SPEC完成；$IMPL自动从todo提升到ready

# --- 工程师工作者在$IMPL上生成（第一次尝试） ---
# 工作者工具调用
kanban_show()   # 在工作器上下文中读取$SPEC的摘要和验收元数据
（工程师编写代码，运行测试，打开PR）
# 评审员反馈到达——工程师认为担忧有效并阻塞
kanban_block(
    reason="审查：缺少密码强度检查，重置链接不是一次性的（30分钟内可重放）",
)
# → $IMPL转换为blocked；运行1以结果'blocked'关闭
```

现在你（人类，或单独的评审员角色）阅读阻塞原因，确定修复方向明确，然后从仪表盘的“取消阻塞”按钮取消阻塞——或者从CLI/斜杠命令：

```bash
hermes kanban unblock $IMPL
# 或从聊天：/kanban unblock $IMPL
```

调度器将 `$IMPL` 提升回 `ready` 状态，并在下一个滴答时重新生成 `backend-dev` 工作者。第二次生成是同一任务上的**新运行**：

```python
# --- 工程师工作者在$IMPL上生成（第二次尝试） ---
# 工作者工具调用
kanban_show()
# → 工作器上下文现在包含运行1的阻塞原因，因此此工作者知道需要修复哪两件事，而不是重新阅读整个规范
（工程师添加zxcvbn检查，使重置令牌成为一次性使用，重新运行测试）
kanban_complete(
    summary="添加了zxcvbn强度检查，重置令牌现在是一次性的（存储并在成功时删除）",
    metadata={
        "changed_files": [
            "auth/reset.py",
            "auth/tests/test_reset.py",
            "migrations/003_single_use_reset_tokens.sql",
        ],
        "tests_run": 11,
        "review_iteration": 2,
    },
)
```

点击实现任务。抽屉显示**两次尝试**：

![实现任务，两次运行——阻塞然后完成](/img/kanban-tutorial/04b-drawer-retry-history-scrolled.png)

- **运行1**——`blocked`，由 `@backend-dev` 执行。审查反馈直接显示在结果下方：“缺少密码强度检查，重置链接不是一次性的（30分钟内可重放）”。
- **运行2**——`completed`，由 `@backend-dev` 执行。新的摘要，新的元数据。

每次运行都是 `task_runs` 表中的一行，拥有自己的结果、摘要和元数据。重试历史不是基于“最新状态”任务概念之外的附加概念——它是最主要的表示形式。当重试的工作者打开任务时，`build_worker_context` 会向其显示先前的尝试，因此第二次尝试的工作者会看到第一次尝试被阻塞的原因，并处理这些具体发现，而不是从头开始重做。

评审员接下来接手。当他们打开 `审查密码重置PR` 时，会看到：

![评审员的管道抽屉视图](/img/kanban-tutorial/09-drawer-pipeline-review.png)

父任务链接是已完成的实现。当评审员的工作者在 `Review password reset PR` 上生成并调用 `kanban_show()` 时，返回的 `worker_context` 包含父任务最近完成的运行的摘要和元数据——因此评审员会读到“添加了zxcvbn强度检查，重置令牌现在是一次性使用的”，并在查看差异之前手中就有了更改文件的列表。

## 故事 4——断路器和崩溃恢复

真正的工作者会失败。凭证缺失、内存不足（OOM）杀死、暂时的网络错误。调度器有两道防线：一个**断路器（Circuit breaker）**，在连续N次失败后自动阻塞，防止看板永远抖动；以及**崩溃检测**，回收其工作者PID在TTL到期之前消失的任务。

### 断路器——看似永久性的失败

一个部署任务，因为其角色的环境中没有设置 `AWS_ACCESS_KEY_ID` 而无法生成工作者：

```bash
hermes kanban create "部署到staging（缺少凭证）" \
    --assignee deploy-bot --tenant ops \
    --max-retries 3
```

调度器尝试生成工作者。生成失败（`RuntimeError: AWS_ACCESS_KEY_ID not set`）。调度器释放认领，递增失败计数器，并在下一个滴答时再次尝试。由于此示例设置了 `--max-retries 3`，断路器在连续三次失败后触发：任务进入 `blocked` 状态，结果 `gave_up`。如果你省略该标志，Hermes 使用 `kanban.failure_limit`（默认：2）。在没有人类取消阻塞之前，不会再有重试。

点击阻塞的任务：

![断路器——2次生成失败+1次放弃](/img/kanban-tutorial/11-drawer-gave-up.png)

三次运行，`error` 字段上都有相同的错误。前两次是 `spawn_failed`（可重试），第三次是 `gave_up`（终止）。上面的事件日志显示完整的序列：`created → claimed → spawn_failed → claimed → spawn_failed → claimed → gave_up`。

在终端上：

```bash
hermes kanban runs t_ef5d
# #  结果         角色          耗时  开始时间
# 1   spawn_failed deploy-bot     0s  2026-04-27 19:34
#       ! deploy-bot环境未设置AWS_ACCESS_KEY_ID
# 2   spawn_failed deploy-bot     0s  2026-04-27 19:34
#       ! deploy-bot环境未设置AWS_ACCESS_KEY_ID
# 3   gave_up      deploy-bot     0s  2026-04-27 19:34
#       ! deploy-bot环境未设置AWS_ACCESS_KEY_ID
```

如果接入了 Telegram / Discord / Slack，网关会在 `gave_up` 事件上触发通知，因此你会收到停机警报，无需检查看板。

### 崩溃恢复——工作者在飞行中死亡

有时生成成功了，但工作者进程后来死亡——段错误、OOM、`systemctl stop`。调度器轮询 `kill(pid, 0)` 并检测到死pid；认领被释放，任务回到 `ready` 状态，下一个滴答将其交给一个新的工作者。

种子数据中的示例是一个因内存不足而运行的迁移：

```bash
# 工作者认领任务，开始扫描240万行，在约230万行时OOM杀死它
# 调度器检测到死pid，释放认领，递增尝试计数器
# 使用分块策略的重试成功
```

抽屉显示完整的两次尝试历史：

![崩溃和恢复——1次崩溃+1次完成](/img/kanban-tutorial/06-drawer-crash-recovery.png)

运行1——`crashed`，错误为`在第230万行OOM杀死（进程99999消失）`。运行2——`completed`，其元数据中包含`"strategy": "chunked with LIMIT + WHERE id > last_id"`。重试的工作者在其上下文中看到了运行1的崩溃，并选择了更安全的策略；元数据使得未来观察者（或事后分析撰写者）能清楚地看到发生了什么变化。

## 结构化交接——为什么 `summary` 和 `metadata` 很重要

在上述每个故事中，工作者最后都调用了 `kanban_complete(summary=..., metadata=...)`。这不是装饰——它是工作流阶段之间的主要交接渠道。

当任务B上的工作者被生成并调用 `kanban_show()` 时，其获得的 `worker_context` 包括：

- B的**先前尝试**（之前的运行：结果、摘要、错误、元数据），这样重试的工作者不会重复失败的路径。
- **父任务结果**——对于每个父任务，最近完成的运行的摘要和元数据——这样下游工作者可以看到上游工作是如何完成的以及原因。

这取代了扁平看板系统中常见的“翻阅评论和工作输出”的做法。项目经理在规范的元数据中编写验收标准，工程师的工作者通过父任务交接结构性地看到它们。工程师记录他们运行了哪些测试以及通过了多少，评审员的工作者在打开差异之前手中就有了该列表。

存在批量关闭保护是因为这些数据是按运行存储的。`hermes kanban complete a b c --summary X`（你，从CLI）会被拒绝——将相同的摘要复制粘贴到三个任务上几乎总是错误的。不带交接标志的批量关闭仍然适用于常见的“我完成了一堆管理任务”的情况。工具表面根本不暴露批量变体；`kanban_complete` 始终是每次单个任务，原因相同。

## 检查当前正在运行的任务

为完整起见——以下是仍在进行中的任务的抽屉（来自故事1的API实现，由`backend-dev`认领但尚未完成）：

![已认领、进行中的任务](/img/kanban-tutorial/10-drawer-in-flight.png)

状态为 `Running`。活动运行显示在运行历史部分，结果 `active`，没有 `ended_at`。如果此工作者死亡或超时，调度器会以适当的结果关闭此运行，并在下一次认领时打开一个新运行——尝试行永远不会消失。

## 后续步骤

- [看板（Kanban）概览](./kanban)——完整的数据模型、事件词汇和CLI参考。
- `hermes kanban --help`——每个子命令，每个标志。
- `hermes kanban watch --kinds completed,gave_up,timed_out`——实时流式传输整个看板上的终端事件。
- `hermes kanban notify-subscribe <task> --platform telegram --chat-id <id>`——当特定任务完成时接收网关通知。