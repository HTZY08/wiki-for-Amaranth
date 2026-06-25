```yaml
---
title: 看板工作线程
description: Hermes Agent 官方文档汉化版
---

--- body ---
# 看板工作线程（Worker Lane）

**工作线程（Worker Lane）** 是看板调度器可将任务路由到的一类进程。每个线程都有一个身份（assignee 字符串）、一个生成机制，以及一个关于生成后必须对任务执行何种操作的契约。

本页面就是该契约。它面向两类读者：

- **操作员（Operators）**：选择哪些线程接入看板（创建哪些配置文件、使用哪些 assignee）。
- **插件/集成作者（Plugin / integration authors）**：希望添加新的线程形态（例如包装 Codex / Claude Code / OpenCode 的 CLI 工作线程、容器化审查线程、通过 API 拉取任务的非 Hermes 服务）。

如果你正在编写工作线程本身的代码——即在*线程内部*运行的 agent——看板生命周期和参考细节会自动注入到 worker 的系统提示中（参见 [`agent/prompt_builder.py`](https://github.com/NousResearch/hermes-agent/blob/main/agent/prompt_builder.py) 中的 `KANBAN_GUIDANCE` 块）。

## 层级结构

```text
Hermes Kanban  =  规范的任务生命周期 + 审计追踪
Worker lane    =  为某张已分配卡片执行实现的执行器
Reviewer       =  把关“完成”状态的人类或人类代理
GitHub PR      =  可上流的产物（可选，用于代码型线程）
```

Hermes Kanban 拥有生命周期真相——`ready` → `running` → `blocked` / `done` / `archived`。工作线程执行工作，但从不拥有那个真相；它们所做的一切都通过 `kanban_*` 工具（对于非 Hermes 外部工作线程，则通过 API）流回看板内核。审阅者（Reviewer）把关从“代码变更已编写”到“任务完成”的状态转换。

## 线程提供什么

要成为一个看板工作线程，集成必须提供三样东西：

### 1. assignee 字符串

调度器将 `task.assignee` 与某个 Hermes 配置文件名称（默认线程形态）或一个已注册的不可生成标识符（插件线程形态——见下文[添加外部 CLI 工作线程](#adding-an-external-cli-worker-lane)）进行匹配。如果 assignee 无法解析，任务将保持在 `ready` 状态并记录一个 `skipped_nonspawnable` 事件，以便看板操作员修复；这些任务不会被静默丢弃，也不会被任意回退执行。

### 2. 生成机制

对于 Hermes 配置文件线程，调度器的 `_default_spawn` 会在任务的固定工作区内运行 `hermes -p <assignee> chat -q <prompt>`（如果 `hermes` 垫片不在 `$PATH` 中，则使用等效的模块形式），并设置以下环境变量：

| 变量 | 内容 |
|---|---|
| `HERMES_KANBAN_TASK` | 工作线程正在操作的任务 ID |
| `HERMES_KANBAN_DB` | 每个看板的 SQLite 文件的绝对路径 |
| `HERMES_KANBAN_BOARD` | 看板 slug |
| `HERMES_KANBAN_WORKSPACES_ROOT` | 看板工作区树的根目录 |
| `HERMES_KANBAN_WORKSPACE` | *当前*任务工作区的绝对路径 |
| `HERMES_KANBAN_RUN_ID` | 当前运行的 ID（用于生命周期门控） |
| `HERMES_KANBAN_CLAIM_LOCK` | 声明锁字符串（`<host>:<pid>:<uuid>`） |
| `HERMES_PROFILE` | 工作线程自身的配置文件名称（用于 `kanban_comment` 作者归属） |
| `HERMES_TENANT` | 租户命名空间（如果任务有） |

对于非 Hermes 线程（通过插件注册），插件提供自己的 `spawn_fn` 可调用对象，该对象接收 `task`、`workspace` 和 `board`，并返回一个可选的 PID 用于崩溃检测。

### 3. 生命周期终止器

每次声明必须以且仅以以下之一结束：

- `kanban_complete(summary=..., metadata=...)` —— 任务成功，状态翻转为 `done`。
- `kanban_block(reason=...)` —— 任务等待人工输入，状态翻转为 `blocked`。当执行 `kanban_unblock` 时，调度器会重新生成。
- 工作线程进程退出但未调用任何工具。内核回收它并发出 `crashed`（PID 死亡）或 `gave_up`（连续失败断路器触发）或 `timed_out`（超过 `max_runtime`）事件。这是失败路径；健康的工作线程不会在此结束。

看板内核强制每次运行恰好由其中之一终止。一个正常退出但既未调用 `kanban_complete` 也未调用 `kanban_block` 的工作线程将被视为崩溃。

## 输出与需要审查的约定

对于大多数修改代码的任务，工作线程完成时工作并不算真正*完成*——它需要人工审阅者。看板内核不强制执行此区分（“修改代码的任务”是模糊的，如果强制每个代码工作线程都使用阻止而非完成，则会破坏那些不需要审查的工作流）。这是一个叠加在之上的约定：

- **使用阻止而非完成**，并将 `reason` 前缀设为 `review-required: `，这样仪表板/`hermes kanban show` 会将该行显示为等待审查。
- **先通过 `kanban_comment` 放入结构化元数据**，因为 `kanban_block` 只携带人类可读的 `reason`。注释是持久的注解渠道——所有与审计相关的字段（`changed_files`、`tests_run`、`diff_path` 或 PR url、决策）都应放在那里。
- **审阅者要么批准并解除阻止**，这会使用注释线程重新生成工作线程以进行后续工作；要么通过另一条注释要求修改，下一次工作线程运行会将其视为 `kanban_show` 上下文的一部分。

注入的 `KANBAN_GUIDANCE` 涵盖了 `kanban_complete`（真正终结的任务——拼写错误修复、文档变更、研究写作）和 `review-required` 阻止模式。

## 日志与审计追踪

调度器将每个工作线程的 stdout/stderr 写入 `<board-root>/logs/<task_id>.log`。日志可通过看板元数据审计：

- `task_runs` 行包含 `log_path`、退出码（如果可用）、摘要和元数据。
- `task_events` 行包含每个状态转换（`promoted`、`claimed`、`heartbeat`、`completed`、`blocked`、`gave_up`、`crashed`、`timed_out`、`reclaimed`、`claim_extended`）。
- `kanban_show` 返回两者，因此审阅者（或后续工作线程）读取任务时无需仪表板访问权限即可获得完整历史。

仪表板以摘要、元数据块和退出状态徽章的形式展示运行历史。CLI 用户可以运行 `hermes kanban tail <task_id>` 实时跟踪，或运行 `hermes kanban runs <task_id>` 查看历史尝试列表。

## 现有线程形态

### Hermes 配置文件线程（默认）

这是目前每个看板工作线程所采用的形态：assignee 是配置文件名称，调度器生成 `hermes -p <profile>`，工作线程自动获得注入的 `KANBAN_GUIDANCE` 系统提示块，并使用 `kanban_*` 工具终止运行。无需在定义配置文件之外进行任何设置。

当你为工作线程池创建配置文件时，选择与希望编排器路由到的*角色*相匹配的名称。编排器（如果有）通过 `hermes profile list` 发现你的配置文件名称——系统没有假定固定的列表（契约的编排器部分包含在注入的 `KANBAN_GUIDANCE` 中）。

### 编排器配置文件线程

配置文件线程的一个特化：编排器是一个 Hermes 配置文件，其工具集包含 `kanban`，但排除了用于实现的 `terminal` / `file` / `code` / `web`。它的工作是通过 `kanban_create` + `kanban_link` 将高级目标分解为子任务，然后退后一步。编排器技能（Orchestrator skill）编码了反诱惑规则。

## 添加外部 CLI 工作线程

将一个非 Hermes CLI 工具（Codex CLI、Claude Code CLI、OpenCode CLI、本地编码模型运行器等）作为看板工作线程接入*目前还不是一条铺好的路*。调度器的生成函数是可插拔的（`spawn_fn` 是 `dispatch_once` 的一个参数），插件可以为非 Hermes 的 assignee 注册自己的 `spawn_fn`，但周围的集成工作——将 CLI 的退出码包装成 `kanban_complete` / `kanban_block` 调用，将 CLI 的工作区/沙盒约定映射到调度器的 `HERMES_KANBAN_WORKSPACE` 环境变量，处理认证和每个 CLI 的策略——仍然是每个集成设计的任务。

如果你在考虑添加一个 CLI 线程，请创建一个 issue，描述具体的 CLI 和你试图启用的工作流。上述契约是任何此类线程必须满足的约束；实现形状（每个 CLI 一个插件 vs 一个由配置参数化的通用 CLI 运行器插件）是开放的。

相关问题历史记录为 [#19931](https://github.com/NousResearch/hermes-agent/issues/19931) 以及已关闭但未合并的 Codex 特定 PR [#19924](https://github.com/NousResearch/hermes-agent/pull/19924)——它们描述了原始架构提案，但最终未落地运行器。

## 调度器处理的故障模式

这样线程作者就不必重新实现它们了：

- **过期声明 TTL** —— 一个声明后从未心跳/完成/阻止的工作线程会在 `DEFAULT_CLAIM_TTL_SECONDS`（默认 15 分钟）后重新声明——但仅当工作线程进程实际死亡时。一个存活的工作线程（慢模型在一个无工具 LLM 调用中花费超过 20 分钟）会获得声明*延长*而不是被杀死；只有死掉的 PID 会被重新声明。
- **工作线程崩溃** —— 当工作线程的本地主机 PID 消失时，会被 `detect_crashed_workers` 检测到并回收；任务递增 `consecutive_failures`，当断路器触发时可能自动阻止。
- **运行级重试** —— 当任务被重试（解除阻止后、崩溃后、重新声明后），工作线程可以在终止工具上使用 `expected_run_id` 参数，以便在其自身运行已被取代时快速失败。
- **每个任务的最大运行时长** —— `task.max_runtime_seconds` 硬限制每次运行的挂钟时间，无论 PID 是否存活。捕获那些本来会被存活 PID 延长机制一直运行下去的真正死锁工作线程。
- **滞留任务检测** —— 一个就绪任务在其 assignee 在 `kanban.stranded_threshold_seconds`（默认 30 分钟）内未产生声明时，会在 `hermes kanban diagnostics` 中显示为 `stranded_in_ready` 警告。严重性在阈值的 2 倍时升级为错误，6 倍时升级为严重。通过一个信号捕获拼写错误的 assignee、已删除的配置文件和关闭的外部工作线程池——与身份无关，无需维护每个看板的白名单。

## 相关

- [看板概述](./kanban) —— 面向用户的介绍。
- [看板教程](./kanban-tutorial) —— 配合仪表板打开的实操演练。
- [`KANBAN_GUIDANCE`](https://github.com/NousResearch/hermes-agent/blob/main/agent/prompt_builder.py) —— 注入到每个看板工作线程系统提示中的工作线程+编排器生命周期。
```