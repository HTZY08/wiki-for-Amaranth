---
title: Kanban
---

sidebar_position: 12
title: "看板（多智能体看板）"
description: "基于 SQLite 的持久化任务板，用于协调多个 Hermes 配置文件的协作"
---

--- body ---
# 看板 — 多智能体配置文件协作

> **想要一步一步指导？** 阅读[看板教程](./kanban-tutorial)——四个用户故事（独立开发者、农场机群、带重试的角色流水线、断路器），每个都配有仪表盘截图。本页面是参考文档；教程是叙事性说明。

Hermes 看板是一个持久化任务板，在你的所有 Hermes 配置文件之间共享，允许多个命名智能体协作完成工作，而无需脆弱的进程内子智能体集群。每个任务都是 `~/.hermes/kanban.db` 中的一行；每次交接都是一行任何人都可以读写的数据；每个工作者都是一个拥有自己身份的完整操作系统进程。

### 两个界面：模型通过工具进行交互，你通过 CLI 进行交互

看板有两个入口，都基于同一个 `~/.hermes/kanban.db`：

- **智能体通过专用的 `kanban_*` 工具集驱动看板**——`kanban_show`、`kanban_list`、`kanban_complete`、`kanban_block`、`kanban_heartbeat`、`kanban_comment`、`kanban_create`、`kanban_link`、`kanban_unblock`。调度器在生成工作者时，这些工具已经包含在它的模式中；编排器配置文件也可以显式启用 `kanban` 工具集。模型通过直接调用工具来读取和路由任务，*而不是*通过 `hermes kanban` 的外部命令。参见下面的[工作者如何与看板交互](#工作者如何与看板交互)。
- **你（以及脚本、cron）通过 CLI 的 `hermes kanban …`、斜杠命令 `/kanban …` 或仪表盘来驱动看板。** 这些是为人类和自动化准备的——背后没有工具调用模型的地方。

两个接口都通过相同的 `kanban_db` 层路由，因此读取看到一致的视图，写入不会漂移。本页面的其余部分展示了 CLI 示例，因为它们易于复制粘贴，但每个 CLI 动词都有一个模型使用的等价工具调用。

这是涵盖 `delegate_task` 无法完成的工作负载的形状：

- **研究分类**——并行研究员 + 分析师 + 作者，人机回环。
- **计划运维**——每周生成日志的每日简报。
- **数字孪生**——持久的命名助手（`inbox-triage`、`ops-review`），随时间积累记忆。
- **工程流水线**——分解 → 在并行工作树中实现 → 审查 → 迭代 → PR。
- **机群工作**——一个专家管理 N 个主体（50 个社交账号、12 个监控服务）。

对于完整的设计原理、与 Cline Kanban / Paperclip / NanoClaw / Google Gemini Enterprise 的对比分析，以及八种经典协作模式，请参阅仓库中的 `docs/hermes-kanban-v1-spec.pdf`。

## 看板 vs. `delegate_task`

它们看起来很相似，但并非同一原语。

| | `delegate_task` | 看板 |
|---|---|---|
| 形状 | RPC 调用（分叉 → 合并） | 持久化消息队列 + 状态机 |
| 父级 | 阻塞直到子级返回 | 创建后即忘 |
| 子级身份 | 匿名子智能体 | 具有持久记忆的命名配置文件 |
| 可恢复性 | 无——失败 = 失败 | 阻塞 → 解除阻塞 → 重新运行；崩溃 → 回收 |
| 人工介入 | 不支持 | 随时评论/解除阻塞 |
| 每任务智能体数 | 一次调用 = 一个子智能体 | 任务生命周期内的 N 个智能体（重试、审查、后续） |
| 审计追踪 | 上下文压缩后丢失 | SQLite 中持久存储的行 |
| 协调 | 层次化（调用者 → 被调用者） | 对等——任何配置文件可以读取/写入任何任务 |

**一句话区别：** `delegate_task` 是一个函数调用；看板是一个工作队列，每个交接都是一行，任何配置文件（或人类）都可以看到和编辑。

**何时使用 `delegate_task`：** 当父智能体在继续之前需要一个简短的推理答案，不涉及人类，结果返回父智能体的上下文。

**何时使用看板：** 当工作跨越智能体边界，需要存活于重启，可能需要人类输入，可能由不同的角色接手，或者需要在事后被发现。

它们可以共存：看板工作者在运行期间可以在内部调用 `delegate_task`。

## 核心概念

- **看板**——一个独立的任务队列，拥有自己的 SQLite 数据库、工作空间目录和调度器循环。一个安装可以拥有多个看板（例如，每个项目、仓库或域一个）；参见下面的[看板（多项目）](#看板多项目)。单项目用户保持在 `default` 看板上，除了本文档这一部分外，永远不会看到“看板”这个词。
- **任务**——包含标题、可选正文、一个负责人（配置文件名称）、状态（`triage | todo | ready | running | blocked | done | archived`）、可选租户命名空间、可选幂等键（用于重试自动化的去重）的行。
- **链接**——`task_links` 行记录父 → 子依赖关系。当所有父任务完成时，调度器将 `todo → ready` 提升。
- **评论**——智能体间协议。智能体和人类追加评论；当工作者（重新）生成时，它读取完整评论线程作为其上下文的一部分。
- **工作空间**——工作者操作的目录。三种类型：
  - `scratch`（默认）——在 `~/.hermes/kanban/workspaces/<id>/`（或非默认看板下的 `~/.hermes/kanban/boards/<slug>/workspaces/<id>/`）下创建的临时目录。**任务完成时删除**——scratch 设计为临时性的，因此在工作者（或 `hermes kanban complete <id>`）标记任务完成的那一刻，目录被清除。如果你想保留工作者的输出，请改用 `worktree:` 或 `dir:<path>`。第一次在安装中创建 scratch 工作空间时，调度器会记录一条警告，并在任务上发出 `tip_scratch_workspace` 事件（通过 `hermes kanban show <id>` 可见）。
  - `dir:<path>`——一个现有的共享目录（Obsidian vault、邮件操作目录、每个账户的文件夹）。**必须是绝对路径。** 像 `dir:../tenants/foo/` 这样的相对路径在调度时被拒绝，因为它们会相对于调度器的当前工作目录解析，这是歧义的，并且是混淆代理转义向量。路径在其他方面是受信任的——这是你的机器、你的文件系统，工作者使用你的 uid 运行。这是受信任本地用户的威胁模型；看板设计为单主机。**完成后保留。**
  - `worktree`——在 `.worktrees/<id>/` 下的一个 git 工作树，用于编码任务。使用 `worktree:<path>` 固定确切的目标路径。工作者端的 `git worktree add` 创建它，在提供 `--branch` 时使用。**完成后保留。**
- **调度器**——一个长期运行的循环，每 N 秒（默认 60）执行：回收过期的声明、回收崩溃的工作者（PID 已消失但 TTL 尚未过期）、提升就绪任务、原子性地声明、生成分配的工作者。**默认在网关内部运行**（`kanban.dispatch_in_gateway: true`）。一个调度器每秒扫描所有看板；工作者生成时设置了 `HERMES_KANBAN_BOARD`，因此它们不能看到其他看板。在同一个任务上连续生成失败 `kanban.failure_limit` 次后（默认：2），调度器自动将其阻塞并提供最后一个错误作为原因——防止在配置文件不存在、工作空间无法挂载等任务上反复抖动。
- **租户**——看板*内部*的可选字符串命名空间。一个专家机群可以通过工作空间路径和记忆键前缀的数据隔离服务于多个业务（`--tenant business-a`）。租户是一个软过滤器；看板是硬隔离边界。

## 看板（多项目）

看板允许你将不相关的工作流分离到隔离的队列中——每个项目、仓库或域一个。一个新的安装只有一个名为 `default` 的看板（数据库在 `~/.hermes/kanban.db` 以保持向后兼容）。只需要一个工作流的用户永远不需要了解看板；此功能是可选的。

每个看板之间的隔离是绝对的：

- 每个看板独立的 SQLite 数据库（`~/.hermes/kanban/boards/<slug>/kanban.db`）。
- 独立的 `workspaces/` 和 `logs/` 目录。
- 为任务生成的工作者只能看到**其看板**的任务——调度器在子环境变量中设置 `HERMES_KANBAN_BOARD`，并且工作者可以访问的每个 `kanban_*` 工具都会读取它。
- 不允许跨看板链接任务（保持模式简单；如果你真的需要跨项目引用，使用自由文本提及并在事后通过 id 手动查找）。

### 从 CLI 管理看板

```bash
# 查看磁盘上的内容。全新安装只显示 "default"。
hermes kanban boards list

# 创建一个新看板。
hermes kanban boards create atm10-server \
    --name "ATM10 Server" \
    --description "Minecraft modded server ops" \
    --icon 🎮 \
    --switch                   # 可选：使其成为活动看板

# 在不切换的情况下操作特定看板。
hermes kanban --board atm10-server list
hermes kanban --board atm10-server create "Restart ATM server" --assignee ops

# 更改后续调用的“当前”看板。
hermes kanban boards switch atm10-server
hermes kanban boards show             # 当前哪个看板是活动的？

# 重命名显示名称（slug 是不可变的——它是目录名）。
hermes kanban boards rename atm10-server "ATM10 (Prod)"

# 归档（默认）——将看板的目录移动到 boards/_archived/<slug>-<ts>/。
# 可以通过将目录移回来恢复。
hermes kanban boards rm atm10-server

# 硬删除——`rm -rf` 看板目录。不可恢复。
hermes kanban boards rm atm10-server --delete
```

看板解析顺序（最高优先级优先）：

1. 在 CLI 调用中显式指定 `--board <slug>`。
2. `HERMES_KANBAN_BOARD` 环境变量（由调度器在生成工作者时设置，因此工作者不能看到其他看板）。
3. `~/.hermes/kanban/current`——由 `hermes kanban boards switch` 持久化的 slug。
4. `default`。

Slug 经过验证：小写字母数字 + 连字符 + 下划线，1-64 个字符，必须以字母数字开头。大写输入自动转为小写。任何其他内容（斜杠、空格、点、`..`）在 CLI 层被拒绝，因此路径遍历技巧无法命名看板。

### 从仪表盘管理看板

`hermes dashboard` → 看板标签页在导航栏中，图标在“技能”之后。当存在多个看板（或者任何看板有任务）时，顶部会显示看板切换器。单看板用户只看到一个小的 `+ New board` 按钮；切换器在需要时才显示。

- **看板下拉菜单**——选择活动看板。你的选择保存在浏览器的 `localStorage` 中，因此跨重载保持，而不会在你离开的终端下改变 CLI 的 `current` 指针。
- **+ New board**——打开一个模态窗口，要求输入 slug、显示名称、描述和图标。可以选择自动切换到新看板。
- **Archive**——仅在非 `default` 看板上显示。确认后，将看板目录移动到 `boards/_archived/`。

所有仪表盘 API 端点接受 `?board=<slug>` 作为看板范围。事件 WebSocket 在连接时固定到一个看板；在 UI 中切换会打开一个针对新看板的新 WS。

## 文件附件

任务可以携带文件附件——PDF、图片、源文档——这样工作者就有所需的源材料，而无需你将路径粘贴到正文中并希望它能找到它们。

- **上传**——在仪表盘抽屉中打开一个任务，使用**附件**部分的 *Upload file* 按钮（一次多个文件都没问题）。每个上传上限为 25 MB。
- **存储**——文件存放在 `<hermes-home>/kanban/attachments/<task_id>/`（默认看板）或 `<hermes-home>/kanban/boards/<slug>/attachments/<task_id>/`（命名看板）。设置 `HERMES_KANBAN_ATTACHMENTS_ROOT` 来固定自定义位置。
- **工作者看到的内容**——当调度器将任务交给工作者时，工作者的上下文包含一个**附件**部分，列出每个文件的名称和**绝对路径**。工作者拥有完整的文件/终端工具访问权限，因此可以直接读取附件（`read_file`，或像 `pdftotext` 这样的 shell 工具）。
- **下载/移除**——抽屉列出每个附件，带有下载链接和移除（×）控件。移除附件会删除元数据行和磁盘上的文件。

:::note 远程终端后端
附件路径直接在**本地**终端后端解析，这是看板工作者的默认设置。如果你在远程后端（Docker、Modal）上运行工作者，将看板的 `attachments/` 目录挂载到沙箱中，以便工作者上下文中的绝对路径可达。
:::

## 快速入门

下面的命令是**你**（人类）设置看板并创建任务。一旦任务被分配，调度器会生成分配的工作者，之后**模型通过 `kanban_*` 工具调用驱动任务，而不是 CLI 命令**——参见[工作者如何与看板交互](#工作者如何与看板交互)。

```bash
# 1. 创建看板（你）
hermes kanban init

# 2. 启动网关（托管内嵌调度器）
hermes gateway start

# 3. 创建任务（你——或编排智能体通过 kanban_create）
hermes kanban create "research AI funding landscape" --assignee researcher

# 4. 实时观看活动（你）
hermes kanban watch

# 5. 查看看板（你）
hermes kanban list
hermes kanban stats
```

当调度器拾取 `t_abcd` 并生成 `researcher` 配置文件时，该工作者模型做的第一件事就是调用 `kanban_show()` 来读取其任务。它不会运行 `hermes kanban show t_abcd`。

### 网关内嵌调度器（默认）

调度器在网关进程内运行。无需安装，无需管理独立服务——如果网关正在运行，就绪任务会在下一个滴答中被拾取（默认 60 秒）。

```yaml
# config.yaml
kanban:
  dispatch_in_gateway: true        # 默认
  dispatch_interval_seconds: 60    # 默认
```

在运行时通过 `HERMES_KANBAN_DISPATCH_IN_GATEWAY=0` 覆盖配置标志以进行调试。标准网关监督适用：直接运行 `hermes gateway start`，或者将网关作为 systemd 用户单元连接（参见网关文档）。如果没有运行网关，`ready` 任务会保持在原地直到网关启动——`hermes kanban create` 在创建时对此发出警告。

作为一个独立进程运行 `hermes kanban daemon` 已被**弃用**；请使用网关。如果你真的无法运行网关（无头主机策略禁止长时间运行的服务等），`--force` 逃生舱将旧独立守护进程保留一个发布周期，但同时在同一个 `kanban.db` 上运行网关内嵌调度器**和**独立守护进程会导致声明竞争，不被支持。

### 幂等创建（用于自动化/webhooks）

```bash
# 第一次调用创建任务。任何后续调用使用相同键时返回现有任务 id 而不是重复。
hermes kanban create "nightly ops review" \
    --assignee ops \
    --idempotency-key "nightly-ops-$(date -u +%Y-%m-%d)" \
    --json
```

### 批量 CLI 动词

所有生命周期动词接受多个 id，以便一次命令清理一批：

```bash
hermes kanban complete t_abc t_def t_hij --result "batch wrap"
hermes kanban archive  t_abc t_def t_hij
hermes kanban unblock  t_abc t_def
hermes kanban block    t_abc "need input" --ids t_def t_hij
```

## 工作者如何与看板交互

**工作者不会 shell 调用 `hermes kanban`。** 当调度器生成工作者时，它在子进程环境中设置 `HERMES_KANBAN_TASK=t_abcd`，该环境变量在模型的模式中启用一个专用的**kanban 工具集**。相同的工具集也可用于在工具集配置中启用了 `kanban` 的编排器配置文件。这些工具直接通过 Python `kanban_db` 层读取和修改看板，与 CLI 相同。运行中的工作者像调用其他工具一样调用这些工具；它永远不会看到或需要 `hermes kanban` CLI。

| 工具 | 用途 | 必需参数 |
|---|---|---|
| `kanban_show` | 读取当前任务（标题、正文、先前的尝试、父级交接、评论、完整的预格式化 `worker_context`）。默认使用环境中的任务 id。 | — |
| `kanban_list` | 列出任务摘要，支持 `assignee`、`status`、`tenant`、归档可见性和限制筛选。用于编排器发现看板工作。 | — |
| `kanban_complete` | 以结构化的 `summary` + `metadata` 完成，形成正式交接。 | 至少提供 `summary` / `result` 之一 |
| `kanban_block` | 升级为需要人工输入，附带 `reason`。 | `reason` |
| `kanban_heartbeat` | 在长时间操作期间发送存活信号。纯副作用。 | — |
| `kanban_comment` | 向任务线程追加持久化注释。 | `task_id`、`body` |
| `kanban_create` | （编排器）扇出到子任务，指定 `assignee`、可选的 `parents`、`skills` 等。 | `title`、`assignee` |
| `kanban_link` | （编排器）事后添加 `parent_id → child_id` 依赖边。 | `parent_id`、`child_id` |
| `kanban_unblock` | （编排器）将阻塞任务移回 `ready`。 | `task_id` |

一个典型的工作者轮次如下：

```
# 模型的工具调用，按顺序：
kanban_show()                                     # 无参数——使用 HERMES_KANBAN_TASK
# (模型读取返回的 worker_context，通过终端/文件工具执行工作)
kanban_heartbeat(note="halfway through — 4 of 8 files transformed")
# (更多工作)
kanban_complete(
    summary="migrated limiter.py to token-bucket; added 14 tests, all pass",
    metadata={"changed_files": ["limiter.py", "tests/test_limiter.py"], "tests_run": 14},
)
```

**编排器**工作者则扇出：

```
kanban_show()
kanban_create(
    title="research ICP funding 2024-2026",
    assignee="researcher-a",
    body="focus on seed + series A, North America, AI-adjacent",
)
# → returns {"task_id": "t_r1", ...}
kanban_create(title="research ICP funding — EU angle", assignee="researcher-b", body="…")
# → returns {"task_id": "t_r2", ...}
kanban_create(
    title="synthesize findings into launch brief",
    assignee="writer",
    parents=["t_r1", "t_r2"],                     # 两者都完成后提升为 ready
    body="one-pager, 300 words, neutral tone",
)
kanban_complete(summary="decomposed into 2 research tasks + 1 writer; linked dependencies")
```

工具（编排器）——`kanban_list`、`kanban_create`、`kanban_link`、`kanban_unblock` 和 `kanban_comment`（用于外部任务）——通过同一工具集可用；约定（在自动注入的 kanban 指南中编码）是工作者配置文件不扇出或路由不相关的工作，而编排器配置文件不执行实现工作。调度器生成的工作者仍然针对破坏性生命周期操作限定在任务范围内，不能修改不相关的任务。

### 为什么使用工具而不是 shell 调用 `hermes kanban`

三个原因：

1. **后端可移植性。** 终端工具指向远程后端（Docker / Modal / Singularity / SSH）的工作者会在容器*内部*运行 `hermes kanban complete`，其中 `hermes` 未安装且 `~/.hermes/kanban.db` 未挂载。看板工具在智能体自己的 Python 进程中运行，无论终端后端如何，始终能到达 `~/.hermes/kanban.db`。
2. **无 shell 引用脆弱性。** 通过 shlex + argparse 传递 `--metadata '{"files": [...]}'` 是一个潜在的陷阱。结构化工具参数完全绕过了它。
3. **更好的错误信息。** 工具结果是模型可以推理的结构化 JSON，而不是它必须解析的 stderr 字符串。

**常规会话零模式占用。** 一个常规的 `hermes chat` 会话在其模式中没有任何 `kanban_*` 工具，除非活动配置文件显式启用了 `kanban` 工具集用于编排工作。调度器生成的任务工作者获得任务范围工具，因为设置了 `HERMES_KANBAN_TASK`；编排器配置文件通过配置获得更广泛的路由表面。对于从不接触看板的用户，没有工具膨胀。

自动注入的 kanban 指南教会模型何时以及以何种顺序调用哪个工具。

### 推荐的交接证据

`kanban_complete(summary=..., metadata={...})` 有意灵活：summary 是人类可读的结束语，而 `metadata` 是机器可读的交接，下游智能体、审查者或仪表盘可以重用而无需解析散文。

对于工程和审查任务，首选以下可选的 metadata 形状：

```json
{
  "changed_files": ["path/to/file.py"],
  "verification": ["pytest tests/hermes_cli/test_kanban_db.py -q"],
  "dependencies": ["parent task id or external issue, if any"],
  "blocked_reason": null,
  "retry_notes": "what failed before, if this was a retry",
  "residual_risk": ["what was not tested or still needs human review"]
}
```

这些键是一个约定，而不是模式要求。有用的属性是每个工作者留下足够的证据，让下一个读者快速回答四个问题：

1. 改变了什么？
2. 如何验证的？
3. 如果失败，什么可以解除阻塞或重试？
4. 哪些风险仍然故意留开？

不要在 `metadata` 中包含秘密、原始日志、令牌、OAuth 材料和不相关的转录内容。存储指针和摘要。如果任务没有文件或测试，在 `summary` 中明确说明，并利用 `metadata` 提供存在的证据，例如源 URL、问题 ID 或人工审查步骤。

### 工作者生命周期

每个处理看板任务的配置文件自动获得工作者生命周期——它在生成时被注入工作者的系统提示中（`KANBAN_GUIDANCE` 块），因此**无需安装或配置**。它教授工作者完整的生命周期，使用**工具调用**而非 CLI 命令：

1. 生成时，调用 `kanban_show()` 读取标题 + 正文 + 父级交接 + 先前尝试 + 完整评论线程。
2. `cd $HERMES_KANBAN_WORKSPACE`（通过终端工具）并在那里工作。
3. 在长时间操作期间，每隔几分钟调用 `kanban_heartbeat(note="...")`。**如果你的工作可能运行超过 1 小时，至少每小时调用一次 `kanban_heartbeat`**——调度器会回收那些运行超过 `kanban.dispatch_stale_timeout_seconds`（默认 4 小时）且在过去一小时内没有心跳的任务，假设工作者未清理就崩溃了。回收是良性的（任务回到 `ready` 状态重新调度，不增加失败计数器），但你会丢失当前运行的进度。
4. 完成后使用 `kanban_complete(summary="...", metadata={...})` 完成，或如果卡住则使用 `kanban_block(reason="...")`。

最后的 `kanban_complete` / `kanban_block` 调用是工作者协议的一部分。如果工作者进程在任务仍处于 `running` 状态时以状态码 0 退出，调度器将其视为协议违规，发出 `protocol_violation` 事件，并在下一个滴答中自动阻塞任务，而不是重新生成进入同一循环。这通常意味着模型写了一个纯文本答案并退出，而没有使用看板工具表面。

生命周期加上负载相关的参考细节（工作空间类型、交付物 `artifacts`、声明创建的卡片）在该系统提示块中发送，因此每个工作者无论运行在哪个配置文件下都拥有它们——无需每个配置文件的技能设置。

### 为特定任务固定额外技能

有时单个任务需要分配者配置文件默认不携带的专家上下文——一项需要 `translation` 技能的翻译工作、一个需要 `github-code-review` 的审查任务、一个需要 `security-pr-audit` 的安全审计。与其每次编辑分配者的配置文件，不如直接将技能附加到任务上。

**从编排智能体**（常见情况——一个智能体将工作路由给另一个），使用 `kanban_create` 工具的 `skills` 数组：

```
kanban_create(
    title="translate README to Japanese",
    assignee="linguist",
    skills=["translation"],
)

kanban_create(
    title="audit auth flow",
    assignee="reviewer",
    skills=["security-pr-audit", "github-code-review"],
)
```

**从人类（CLI / 斜杠命令）**，每个技能重复 `--skill`：

```bash
hermes kanban create "translate README to Japanese" \
    --assignee linguist \
    --skill translation

hermes kanban create "audit auth flow" \
    --assignee reviewer \
    --skill security-pr-audit \
    --skill github-code-review
```

**从仪表盘**，在行内创建表单的 **skills** 字段中用逗号分隔输入技能。

调度器为列表中的每个技能发出一个 `--skills <name>` 标志，因此工作者在自动注入的看板指南之上加载所有这些技能。技能名称必须与分配者配置文件上实际安装的技能匹配（运行 `hermes skills list` 查看可用项）；没有运行时安装。

### 目标模式卡片（`--goal`）

默认情况下每个工作者有**一次机会**处理其卡片——完成工作，调用 `kanban_complete`/`kanban_block`，退出。传递 `--goal`（CLI）或 `goal_mode=True`（`kanban_create` 工具 / 仪表盘）改为在那个工作者中运行**目标循环**，这是 `/goal` 斜杠命令背后的 Ralph 风格引擎：每轮后一个辅助判断器检查工作者的输出是否满足卡片的标题 + 正文（视为接受标准），如果工作未完成——且轮次预算还有剩余——工作者在同一会话中继续，直到判断器同意、工作者自行终止任务、或预算耗尽（此时卡片**阻塞**以待人工审查，而不是静默退出）。

```bash
hermes kanban create "Translate the docs site to French" \
    --body "Acceptance: every page translated, no English left, links intact." \
    --assignee linguist \
    --goal \
    --goal-max-turns 15      # 可选；默认为 20
```

用于开放式、多步骤或“继续直到 X 为真”的卡片。对于廉价的单次工作跳过它——每轮判断器的开销不值得，而且调度器现有的重试/断路器已经处理了临时工作者故障。判断器的好坏取决于你的目标文本，因此将正文写为**明确的接受标准**。

### 编排器的行为

一个**行为良好的编排器不会亲自完成工作。** 它将用户的目标分解成任务，将它们链接起来，将每个任务分配给你已设置的配置文件之一，然后退后。编排器指南——反诱惑规则、第零步配置文件发现提示（调度器静默失败于未知的分配者名称，因此编排器必须将每个卡片基于你的机器上实际存在的配置文件）、以及一个以 `kanban_create` / `kanban_link` / `kanban_comment` 为键的分解方案——自动注入工作者的系统提示中；无需安装。

一个典型的编排器轮次（两个并行研究员转交给写作者）：

```
# 用户目标：“草拟一份关于 ICP 融资格局的发布文章”
kanban_create(title="research ICP funding, NA angle",  assignee="researcher-a", body="…")  # → t_r1
kanban_create(title="research ICP funding, EU angle",  assignee="researcher-b", body="…")  # → t_r2
kanban_create(
    title="synthesize ICP funding research into launch post draft",
    assignee="writer",
    parents=["t_r1", "t_r2"],        # 两个研究员都完成时提升为“ready”
    body="one-pager, neutral tone, cite sources inline",
)                                     # → t_w1
# 可选：事后添加跨领域依赖而无需重新创建任务
kanban_link(parent_id="t_r1", child_id="t_followup")
kanban_complete(
    summary="decomposed into 2 parallel research tasks → 1 synthesis task; writer starts when both researchers finish",
)
```

编排器指南自动包含在工作者的系统提示中——无需为每个配置文件安装或同步。

为了获得最佳效果，将其与一个工具集仅限于看板操作（`kanban`、`gateway`、`memory`）的配置文件配对，这样编排器即使尝试也无法执行实现任务。

## 仪表盘（GUI）

`/kanban` CLI 和斜杠命令足以无头运行看板，但可视化看板通常是人工介入的正确界面：分类、跨配置文件监督、阅读评论线程、以及在列之间拖拽卡片。Hermes 将其作为**捆绑的仪表盘插件**在 `plugins/kanban/` 中提供——不是核心功能，不是独立服务——遵循[扩展仪表盘](./extending-the-dashboard)中阐述的模型。

通过以下方式打开：

```bash
hermes kanban init      # 一次性：如尚未创建则创建 kanban.db
hermes dashboard        # “Kanban”标签出现在导航中，位于“Skills”之后
```

### 插件提供的内容

- 一个**看板**标签页，每列显示一个状态：`triage`、`todo`、`ready`、`running`、`blocked`、`done`（以及当切换开启时的 `archived`）。
  - `triage` 是粗略想法的停放列。默认情况下（`kanban.auto_decompose: true`），调度器自动对部署到此处的任务运行**分解器**。内置分解器使用 `auxiliary.kanban_decomposer` 模型路径，读取你的配置文件名单（含描述），并将任务扇出成一个小的子任务图，路由到最合适的专家。原始任务作为所有子任务的父级存活，这样当所有任务完成时，其分配者（`kanban.orchestrator_profile`，或未设置时的活动默认配置文件）会醒来判断完成。翻转页面顶部的 **Orchestration: Auto/Manual** 药丸（翠绿色 = Auto，哑光灰色 = Manual），或直接编辑 `config.yaml`。两种模式都与 `hermes kanban specify` 共存——如果你不想要扇出，它仍然可以作为单个任务规范重写使用。
- 卡片显示任务 id、标题、优先级徽章、租户标签、分配配置文件、评论/链接计数、一个进度药丸（当任务有依赖项时显示 `N/M` 子任务完成），以及“在 N 前创建”。每张卡片有一个复选框用于多选。
- **每个配置文件的泳道在 Running 内**——工具栏复选框切换 Running 列的子分组，按分配者分组。
- **通过 WebSocket 实时更新**——插件以短轮询间隔追踪仅追加的 `task_events` 表；看板在任何配置文件（CLI、网关或另一个仪表盘标签）采取行动时立即反映变化。重新加载被去抖，因此事件突发只触发一次重新获取。
- **拖拽**卡片在各列之间移动以改变状态。放下发送 `PATCH /api/plugins/kanban/tasks/:id`，该调用通过 CLI 使用的相同 `kanban_db` 代码路由——三个表面永远不会漂移。移动到破坏性状态（`done`、`archived`、`blocked`）会提示确认。触摸设备使用基于指针的回退，因此看板在平板电脑上也可用。
- **行内创建**——点击任何列标题上的 `+` 以输入标题、分配者、优先级，以及（可选）从下拉菜单中选择一个父任务。按 Enter 创建任务，Shift+Enter 在标题字段中插入换行，或 Escape 取消。从 `triage` 列创建会自动将新任务停放在 triage 中。
- **多选与批量操作**——shift/ctrl 点击卡片或勾选其复选框以将其添加到选择中。顶部出现一个批量操作栏，带有批量状态转换、归档和重新分配（通过配置文件下拉菜单，或“(unassign)”）。破坏性批量操作先确认。每个 id 的部分失败会报告而不中止其余任务。
- **点击一张卡片**（不带 shift/ctrl）打开一个侧边抽屉（Escape 或点击外部关闭），其中包含：
  - **可编辑标题**——点击标题重命名。
  - **可编辑分配者/优先级**——点击元数据行进行重写。
  - **可编辑描述**——默认以 Markdown 渲染（标题、粗体、斜体、内联代码、围栏代码、`http(s)` / `mailto:` 链接、项目列表），带有一个“编辑”按钮切换到文本域。Markdown 渲染是一个微小的、XSS 安全的渲染器——每个替换在 HTML 转义输入上运行，只有 `http(s)` / `mailto:` 链接通过，并且始终设置 `target="_blank"` + `rel="noopener noreferrer"`。
  - **依赖编辑器**——父级和子级芯片列表，每个带有一个 `×` 解除链接，再加上其他任务的复选框添加新父级或子级。循环尝试在服务器端被拒绝并附带清晰消息。
  - **状态操作行**（→ triage / → ready / → running / block / unblock / complete / archive）对破坏性转换带有确认提示。对于 **Triage** 列中的卡片，行还暴露两个 LLM 驱动的操作：**⚗ Decompose** 将任务扇出一个子任务图，路由到按描述匹配的专家配置文件；以及 **✨ Specify** 进行单任务规范重写。当 LLM 决定任务不获益于扇出时，Decompose 回退到 specify 风格的提升，因此它是一个严格超集。两者都可以从 CLI（`hermes kanban decompose <id>` / `specify <id>` / `--all`）、从任何网关平台（`/kanban decompose <id>`）和以编程方式通过 `POST /api/plugins/kanban/tasks/:id/decompose` 和 `…/specify` 访问。在 `config.yaml` 中的 `auxiliary.kanban_decomposer` 和 `auxiliary.triage_specifier` 下配置模型。
  - 结果部分（也 Markdown 渲染）、评论线程（Enter 提交）、最近 20 个事件。
- **工具栏过滤器**——自由文本搜索、租户下拉菜单（默认为 `config.yaml` 中的 `dashboard.kanban.default_tenant`）、分配者下拉菜单、“显示归档”切换、“按配置文件泳道”切换，以及一个**推送调度器**按钮，这样你就不必等待下一个 60 秒滴答。

视觉上目标是与 Linear / Fusion 类似的布局：深色主题、带计数的列标题、彩色状态点、优先级和租户的药丸芯片。插件只读取主题 CSS 变量（`--color-*`、`--radius`、`--font-mono`、...），因此它会根据当前活动的仪表盘主题自动重新设置样式。

### 自动 vs 手动编排

看板有两种方式处理你放入 `triage` 列的任务：

**Auto（默认）**——`kanban.auto_decompose: true`。网关内嵌调度器在每个滴答上运行**分解器**，由 `kanban.auto_decompose_per_tick` 限制（默认每个滴答处理 3 个任务），这样批量加载 triage 任务不会爆发式消耗辅助 LLM。分解器使用内置分解提示加上 `auxiliary.kanban_decomposer` 模型路径，读取你已安装的配置文件及其描述，并要求 LLM 生成一个 JSON 任务图：要生成哪些任务、它们交给谁、哪个依赖哪个。原始 triage 任务成为图中每个叶节点的父级，因此它会一直存活直到整个图完成——然后提升回 `ready`，这样其分配者（`kanban.orchestrator_profile` 或未设置时的活动默认配置文件）可以判断完成，如果工作未完成则添加更多任务。这就是“丢下一行，走开”的流程。

**Manual（手动）**——`kanban.auto_decompose: false`。Triage 任务保持在 triage 中直到你采取行动。点击卡片上的 **⚗ Decompose** 按钮，运行 `hermes kanban decompose <id>`（或 `--all`），或从聊天中使用 `/kanban decompose <id>`。这匹配看板在分解器之前的行为，当你想要完全控制何时运行什么时很有用。

通过看板页面顶部的 **Orchestration: Auto/Manual** 药丸（翠绿色 = Auto，哑光灰色 = Manual）翻转两种模式，或直接编辑 `config.yaml`。两种模式与 `hermes kanban specify` 共存——如果你不想要扇出，它仍然可以作为单任务规范重写使用。

分解器的路由决策取决于配置文件描述，这是一个每个配置文件的标签原语，你可以通过 `hermes profile create --description "..."`、`hermes profile describe <name> --text "..."`、`hermes profile describe <name> --auto`（从配置文件的已安装技能 + 模型 LLM 生成）或仪表盘扩展后的 **Orchestration settings** 面板中的每个配置文件编辑器设置。没有描述的配置文件仍然出现在名单中——它们可以按名称路由，只是不够精确。分解器绝不会让子任务的 `assignee=None`：当 LLM 选择一个未知配置文件时，子任务被路由到 `kanban.default_assignee`（或如果未设置则回退到活动默认配置文件）。

`kanban.orchestrator_profile` 不会将该配置文件的提示、技能或自定义逻辑加载到分解调用中。它控制扇出后谁拥有根/编排任务。要更改分解器的模型/提供者，配置 `auxiliary.kanban_decomposer`。要使用配置文件的自定义任务拆分逻辑而不是内置分解器，切换到手动模式，让该配置文件显式创建或分解任务。

配置旋钮（都在 `~/.hermes/config.yaml` 的 `kanban:` 下）：

| 键 | 默认值 | 用途 |
|---|---|---|
| `auto_decompose` | `true` | 调度器在每个滴答上自动运行分解器。 |
| `auto_decompose_per_tick` | `3` | 每个调度器滴答允许的最大分解次数。多余的推迟到下一个滴答。 |
| `orchestrator_profile` | `""` | 分解后分配给根/编排任务的配置文件。空值 = 回退到活动默认配置文件。 |
| `default_assignee` | `""` | 当 LLM 选择未知配置文件时，子任务被分配到的位置。空值 = 回退到活动默认配置文件。 |
| `auto_subscribe_on_create` | `true` | 当工作者从具有持久传递渠道的会话内部调用 `kanban_create` 时（消息网关或 TUI），原始会话自动订阅新任务的完成/阻塞事件。调度器仍然驱动传递——这只改变调用者的聊天/键是否出现在通知订阅表中。设置为 `false` 以要求每个任务显式调用 `kanban_notify-subscribe`。 |

以及两个辅助 LLM 槽位：

| 键 | 用途 |
|---|---|
| `auxiliary.kanban_decomposer` | 生成任务图的模型（由 Decompose 调用）。设置 `provider`/`model` 以覆盖主聊天模型。 |
| `auxiliary.profile_describer` | 自动生成配置文件描述的模型（由 `hermes profile describe --auto` 调用）。 |

### 架构

GUI 严格是一个**通过数据库读取 + 通过 kanban_db 写入**的层，本身没有领域逻辑：

<!-- ascii-guard-ignore -->
```
┌────────────────────────┐      WebSocket (追踪 task_events)
│   React SPA (插件)   │ ◀──────────────────────────────────┐
│   HTML5 拖拽          │                                    │
└──────────┬─────────────┘                                    │
           │ REST 通过 fetchJSON                              │
           ▼                                                  │
┌────────────────────────┐     写入调用 kanban_db.*          │
│  FastAPI 路由器        │     直接——与 CLI /kanban 动词       │
│  plugins/kanban/       │     使用的代码路径相同             │
│  dashboard/plugin_api.py                                    │
└──────────┬─────────────┘                                    │
           │                                                  │
           ▼                                                  │
┌────────────────────────┐                                    │
│  ~/.hermes/kanban.db   │ ───── 追加 task_events ────────────┘
│  (WAL, 共享)           │
└────────────────────────┘
```
<!-- ascii-guard-ignore-end -->

### REST 接口

所有路由挂载在 `/api/plugins/kanban/` 下，受仪表盘的短暂会话令牌保护：

| 方法 | 路径 | 用途 |
|---|---|---|
| `GET` | `/board?tenant=<name>&include_archived=…` | 按状态列分组的完整看板，加上用于过滤器下拉菜单的租户和分配者 |
| `GET` | `/tasks/:id` | 任务 + 评论 + 事件 + 链接 |
| `POST` | `/tasks` | 创建（包装 `kanban_db.create_task`，接受 `triage: bool` 和 `parents: [id, …]`） |
| `PATCH` | `/tasks/:id` | 状态 / 分配者 / 优先级 / 标题 / 正文 / 结果 |
| `POST` | `/tasks/bulk` | 将相同的补丁（状态 / 归档 / 分配者 / 优先级）应用于 `ids` 中的每个 id。每个 id 的失败被报告而不中止兄弟任务 |
| `POST` | `/tasks/:id/comments` | 追加评论 |
| `POST` | `/tasks/:id/specify` | 运行 triage 指定器——辅助 LLM 充实任务正文并将其从 `triage` 提升到 `todo`。返回 `{ok, task_id, reason, new_title}`；`ok=false` 并带有可读原因（如“不在 triage”/无辅助客户端/LLM 错误）时返回 200，不是 4xx |
| `POST` | `/tasks/:id/decompose` | 运行看板分解器——辅助 LLM 生成任务图，然后帮助原子创建子任务 + 链接根任务 + 翻转 `triage → todo`。返回 `{ok, task_id, reason, fanout, child_ids, new_title}`。与 `/specify` 相同的 LLM 错误时返回 200 的约定。 |
| `GET` | `/profiles` | 列出已安装的配置文件及其描述（由仪表盘的配置文件描述编辑器和编排器选取器使用）。 |
| `PATCH` | `/profiles/:name` | 设置或清除配置文件的描述（用户创作——`description_auto: false`）。返回 `{ok, profile, description}`。 |
| `POST` | `/profiles/:name/describe-auto` | 通过 `auxiliary.profile_describer` 为配置文件生成描述。以 `description_auto: true` 持久保存，以便仪表盘可以显示一个“审查”徽章。 |
| `GET` | `/orchestration` | 读取看板编排设置（`orchestrator_profile`、`default_assignee`、`auto_decompose`）以及回退后的*已解析*有效值。 |
| `PUT` | `/orchestration` | 更新 `config.yaml` 中三个编排键的一个或多个。验证非空的配置文件名称确实存在。 |
| `POST` | `/links` | 添加依赖关系（`parent_id` → `child_id`） |
| `DELETE` | `/links?parent_id=…&child_id=…` | 移除依赖关系 |
| `POST` | `/dispatch?max=…&dry_run=…` | 推送调度器——跳过 60 秒等待 |
| `GET` | `/config` | 从 `config.yaml` 读取 `dashboard.kanban` 偏好——`default_tenant`、`lane_by_profile`、`include_archived_by_default`、`render_markdown` |
| `WS` | `/events?since=<event_id>` | `task_events` 行的实时流 |

每个处理程序都是一个轻量包装器——插件大约 700 行 Python（路由器 + WebSocket 追踪 + 批量处理器 + 配置读取器），不添加新的业务逻辑。一个微小的 `_conn()` 帮助器在每个读取和写入时自动初始化 `kanban.db`，因此全新安装无论用户是先打开仪表盘、直接访问 REST API 还是运行 `hermes kanban init` 都能工作。

### 仪表盘配置

`~/.hermes/config.yaml` 中 `dashboard.kanban` 下的任何键都会更改标签页的默认值——插件在加载时通过 `GET /config` 读取：

```yaml
dashboard:
  kanban:
    default_tenant: acme              # 预选租户过滤器
    lane_by_profile: true             # “lanes by profile”切换的默认值
    include_archived_by_default: false
    render_markdown: true             # 设置为 false 以使用纯 <pre> 渲染
```

每个键是可选的，并回退到显示的默认值。

### 安全模型

仪表盘的 HTTP 认证中间件[显式跳过 `/api/plugins/`](./extending-the-dashboard#backend-api-routes)——插件路由默认未认证，因为仪表盘默认绑定到 localhost。这意味着看板 REST 接口可以从主机上的任何进程访问。

WebSocket 多加一步：它需要仪表盘的短暂会话令牌作为 `?token=…` 查询参数（浏览器无法在升级请求上设置 `Authorization`），与浏览器内 PTY 桥使用的模式匹配。

如果你运行 `hermes dashboard --host 0.0.0.0`，每个插件路由——包括看板——都可以从网络访问。**不要在共享主机上这样做。** 看板包含任务正文、评论和工作空间路径；攻击者访问这些路由可以获得对你整个协作表面的读取权限，并且还可以创建/重新分配/归档任务。

`~/.hermes/kanban.db` 中的任务设计上是配置无关的（这是协调原语）。如果你使用 `hermes -p <profile> dashboard` 打开仪表盘，看板仍然显示主机上任何其他配置文件创建的任务。同一用户拥有所有配置文件，但如果多个角色共存，这一点值得注意。

### 实时更新

`task_events` 是一个仅追加的 SQLite 表，具有单调递增的 `id`。WebSocket 端点持有每个客户端最后看到的事件 id，并在新行到达时推送它们。当事件突发时，前端重新加载（非常便宜的）看板端点——比尝试从每个事件类型修补本地状态更简单、更正确。WAL 模式意味着读取循环永远不会阻塞调度器的 `BEGIN IMMEDIATE` 声明事务。

### 扩展它

插件使用标准的 Hermes 仪表盘插件合约——有关完整的清单参考、shell 槽位、页面范围槽位和插件 SDK，请参阅[扩展仪表盘](./extending-the-dashboard)。额外列、自定义卡片装饰、租户过滤器布局或完整的 `tab.override` 替换都可以实现，而无需派生此插件。

要禁用而不移除：在 `config.yaml` 中添加 `dashboard.plugins.kanban.enabled: false`（或删除 `plugins/kanban/dashboard/manifest.json`）。

### 范围边界

GUI 特意简单。插件能做的所有事情都可以从 CLI 访问；插件只是让人类更舒适。自动分配、预算、治理门和组织视图仍然是用户空间——一个路由器配置文件、另一个插件或对 `tools/approval.py` 的重用——正如设计规范的范围外部分所列的那样。

## CLI 命令参考

这是**你**（或脚本、cron、仪表盘）用来驱动看板的接口。在调度器内运行的工作者使用 `kanban_*` [工具接口](#工作者如何与看板交互)进行相同操作——此处的 CLI 和那里的工具都通过 `kanban_db` 路由，因此两个接口在构建上一致。

```
hermes kanban init                                     # 创建 kanban.db + 打印守护进程提示
hermes kanban create "<title>" [--body ...] [--assignee <profile>]
                                [--parent <id>]... [--tenant <name>]
                                [--workspace scratch|worktree|worktree:<path>|dir:<path>]
                                [--branch <name>]
                                [--priority N] [--triage] [--idempotency-key KEY]
                                [--max-runtime 30m|2h|1d|<seconds>]
                                [--max-retries N]
                                [--goal] [--goal-max-turns N]
                                [--skill <name>]...
                                [--json]
hermes kanban list [--mine] [--assignee P] [--status S] [--tenant T] [--archived]
        [--workflow-template-id <id>] [--current-step-key <key>]
        [--sort created|created-desc|priority|priority-desc|status|assignee|title|updated]
        [--json]
hermes kanban show <id> [--json]
hermes kanban assign <id> <profile>                    # 或 'none' 取消分配
hermes kanban reassign <id>... <profile>               # 批量重新分配任务到配置文件
hermes kanban edit <id> [--title ...] [--body ...]     # 原地编辑任务标题/正文/优先级
        [--priority N]
hermes kanban promote <id>...                          # 将 todo/blocked 任务移至 ready（恢复）
hermes kanban schedule <id> --at <ISO8601>             # 设置/清除任务的 scheduled_at 开始时间
hermes kanban diagnostics [--json]                     # 看板健康快照（别名：diag）
hermes kanban link <parent_id> <child_id>
hermes kanban unlink <parent_id> <child_id>
hermes kanban claim <id> [--ttl SECONDS]
hermes kanban comment <id> "<text>" [--author NAME]

# 批量动词——接受多个 id：
hermes kanban complete <id>... [--result "..."]
hermes kanban block <id> "<reason>" [--ids <id>...]
hermes kanban unblock <id>...
hermes kanban archive <id>...

hermes kanban tail <id>                                # 追踪单个任务的事件流
hermes kanban watch [--assignee P] [--tenant T]        # 实时流式传输所有事件到终端
        [--kinds completed,blocked,…] [--interval SECS]
hermes kanban heartbeat <id> [--note "..."]            # 工作者存活信号，用于长时间操作
hermes kanban runs <id> [--json]                       # 尝试历史（每次运行一行）
hermes kanban assignees [--json]                       # 磁盘上的配置文件 + 每个分配者的任务计数
hermes kanban dispatch [--dry-run] [--max N]           # 单次传递
        [--failure-limit N] [--json]
hermes kanban daemon --force                           # 已弃用 — 独立调度器（改用 `hermes gateway start`）
        [--failure-limit N] [--pidfile PATH] [-v]
hermes kanban stats [--json]                           # 每个状态 + 每个分配者的计数
hermes kanban log <id> [--tail BYTES]                  # 来自 ~/.hermes/kanban/logs/ 的工作者日志
hermes kanban notify-subscribe <id>                    # 网关桥接钩子（由网关中的 /kanban 使用）
        --platform <name> --chat-id <id> [--thread-id <id>] [--user-id <id>]
hermes kanban notify-list [<id>] [--json]
hermes kanban notify-unsubscribe <id>
        --platform <name> --chat-id <id> [--thread-id <id>]
hermes kanban context <id>                             # 工作者看到的内容
hermes kanban specify [<id> | --all] [--tenant T]      # 充实 triage 列的想法
        [--author NAME] [--json]                       #   成为完整规范并提升为 todo
hermes kanban gc [--event-retention-days N]            # 工作空间 + 旧事件 + 旧日志
        [--log-retention-days N]
```

所有命令也可作为交互式 CLI 和消息网关中的斜杠命令使用（见下面的 [`/kanban` 斜杠命令](#kanban-斜杠命令)）。

`--max-retries` 是每个任务调度器的断路器覆盖。`--max-retries 1` 在第一次非成功尝试时阻塞任务，而 `--max-retries 3` 允许两次重试，并在第三次失败时阻塞。省略它则使用 `config.yaml` 中的 `kanban.failure_limit`，然后是内置默认值。

### 并发、调度和子任务提升配置

| 配置键 | 默认值 | 用途 |
|--------|--------|------|
| `kanban.max_in_progress` | 未设置（无限制） | 限制同时运行的任务数量。当看板已有 N 个任务正在运行时，调度器跳过生成更多任务——对于慢速工作者（本地 LLM、资源受限的主机）很有用，这样它们能完成已有任务，而不是更多任务堆积并超时。无效或低于 1 的值会记录警告并表现为无限制。 |
| `kanban.max_in_progress_per_profile` | 未设置（无限制） | `max_in_progress` 的每个配置文件变体——限制任何单个分配者配置文件可以并发运行的任务数量。当一个配置文件慢或受到速率限制，但其他配置文件应继续流动时有用。与看板范围的 `max_in_progress` 一起应用；两者都必须允许生成才能进行。 |
| `kanban.auto_promote_children` | `true` | 在 `decompose_triage_task()` 生成没有父级阻塞依赖的子任务后，它们自动提升为 `ready` 以便调度器可以拾取。设置为 `false` 需要手动审查——子任务保持在 `todo` 直到你提升它们。 |
| `kanban.default_workdir` | 未设置 | 看板级别的默认工作目录，应用于新任务，当未指定 `--workspace` 或任务本身未覆盖时。每任务的 `workspace:` 仍然优先。 |

```yaml
kanban:
  max_in_progress: 2
  auto_promote_children: false
  default_workdir: ~/work/active-project
```

### 计划任务启动（`scheduled_at`）

在任务上设置 `scheduled_at` 以将调度延迟到特定时间。调度器跳过那些 `scheduled_at` 在未来时间的就绪任务，并在该时间戳后的第一个滴答拾取它们。

```bash
hermes kanban create "nightly backup audit" \
  --assignee ops --scheduled-at "2026-06-01T03:00:00Z"
```

### 重生保护

调度器拒绝在以下情况下重生成一个就绪任务：前一次运行遇到配额/认证/429 错误（`blocker_auth`），或者在保护窗口内成功完成运行（`recent_success`），或者最近的任务评论链接到一个 GitHub PR（`active_pr`）。这防止了在相同 bug 或任务上重复的工作者风暴，而人类正在赶上。参见[事件参考](#事件参考)中的 `respawn_guarded` 行。

### 拖拽删除和批量删除（仪表盘）

仪表盘在看板页面上暴露一个**垃圾桶拖放区**——将任何卡片拖入其中以删除任务（级联删除 `task_events`、子链接和订阅）。一个确认提示防止意外。批量删除也可以通过 `DELETE /api/plugins/kanban/tasks` 使用 JSON 主体 `{"ids": ["t_abc", "t_def", ...]}` 访问。

### 工作者可见性端点

仪表盘插件 API 现在为外部监控器暴露这些只读端点（加上一个运行控制动词）：

| 端点 | 返回 |
|------|------|
| `GET /api/plugins/kanban/workers/active` | 当前生成的工作者，包括 PID、配置文件、任务 id、开始时间、最后心跳 |
| `GET /api/plugins/kanban/runs/{id}` | 单次运行详情——任务 id、状态、开始/结束、退出代码、日志路径 |
| `POST /api/plugins/kanban/runs/{run_id}/terminate` | 终止一个可回收的运行——停止工作者并释放任务以便重新调度 |
| `GET /api/plugins/kanban/inspect` | 组合的调度器快照——积压任务、进行中计数与 `max_in_progress`、最近的事件 |

所有这些都受与其他看板插件 API 相同的仪表盘插件认证保护。

### 看板群体拓扑助手

`hermes kanban swarm` 一次性创建一个持久的**看板群体 v1** 图：一个已完成的根/黑板书卡、N 个并行工作者卡片、一个依赖于所有工作者的验证者卡片、以及一个依赖于验证者的合成者卡片。共享的群体上下文（“黑板书”）作为结构化 JSON 评论存储在根卡片上，以便任何工作者可以读取。

```bash
hermes kanban swarm "Design a multi-region failover plan" \
  --workers researcher,architect,sre \
  --verifier reviewer --synthesizer writer
```

生成的图正常调度——工作者并行运行，验证者在它们全部完成后唤醒，合成者在验证者标记工作干净后唤醒。

## `/kanban` 斜杠命令 {#kanban-斜杠命令}

每个 `hermes kanban <action>` 动词也可通过 `/kanban <action>` 访问——从交互式 `hermes chat` 会话内部**以及**从任何网关平台（Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Mattermost、电子邮件、SMS）。两个接口都调用完全相同的 `hermes_cli.kanban.run_slash()` 入口点，该入口点重用 `hermes kanban` argparse 树，因此参数表面、标志和输出格式在 CLI、`/kanban` 和 `hermes kanban` 之间一致。你无需离开聊天即可驱动看板。

```
/kanban list
/kanban show t_abcd
/kanban create "write launch post" --assignee writer --parent t_research
/kanban comment t_abcd "looks good, ship it"
/kanban unblock t_abcd
/kanban dispatch --max 3
/kanban specify t_abcd                  # 充实 triage 单行内容成为真实规范
/kanban specify --all --tenant engineering  # 扫描一个租户中的每个 triage 任务
```

引用多词参数的方式与在 shell 中相同——`run_slash` 使用 `shlex.split` 解析行的其余部分，因此 `"..."` 和 `'...'` 都有效。

### 运行中用法：`/kanban` 绕过运行中智能体保护

网关通常会在智能体仍在思考时排队斜杠命令和用户消息——这阻止你意外地在第一次飞行中开始第二次轮次。**`/kanban` 明确豁免于此保护。** 看板存在于 `~/.hermes/kanban.db` 中，而不是正在运行的智能体的状态中，因此读取（`list`、`show`、`context`、`tail`、`watch`、`stats`、`runs`）和写入（`comment`、`unblock`、`block`、`assign`、`archive`、`create`、`link`、…）即使在中途也立即通过。

这是分离的全部意义：

- 工作者等待同行阻塞→你从手机发送 `/kanban unblock t_abcd`，调度器在下一个滴答中拾取同行。被阻塞的工作者不会被中断——它只是不再被阻塞。
- 你注意到一个需要人类上下文的卡片→`/kanban comment t_xyz "use the 2026 schema, not 2025"` 落在任务线程上，该任务的*下一次*运行将会在 `kanban_show()` 中读取它。
- 你想知道你的机群在做什么而不停止编排器→`/kanban list --mine` 或 `/kanban stats` 检查看板而不触及你的主对话。

### 在 `/kanban create` 上自动订阅（仅限网关）

当你从网关使用 `/kanban create "…"` 创建任务时，原始聊天（平台 + 聊天 id + 线程 id）会自动订阅该任务的终端事件（`completed`、`blocked`、`gave_up`、`crashed`、`timed_out`）。每个终端事件你会收到一条消息——包括完成时工作者结果摘要的第一行——无需轮询或记住任务 id。

```
你> /kanban create "transcribe today's podcast" --assignee transcriber
机器人> Created t_9fc1a3  (ready, assignee=transcriber)
        (subscribed — you'll be notified when t_9fc1a3 completes or blocks)

… ~8 分钟后 …

机器人> ✓ t_9fc1a3 completed by transcriber
        transcribed 42 minutes, saved to podcast/2026-05-04.md
```

一旦任务达到 `done` 或 `archived` 状态，订阅会自动移除。如果你使用 `--json`（机器输出）脚本创建，则跳过自动订阅——假设脚本调用者想要通过 `/kanban notify-subscribe` 显式管理订阅。

### 消息中的输出截断

网关平台有实际的消息长度限制。如果 `/kanban list`、`/kanban show` 或 `/kanban tail` 产生超过约 3800 个字符的输出，响应会被截断，并附带 `… (truncated; use \`hermes kanban …\` in your terminal for full output)` 的页脚。CLI 表面没有这样的限制。

### 自动补全

在交互式 CLI 中，输入 `/kanban ` 并按下 Tab 会循环显示内置子命令列表（`list`、`ls`、`show`、`create`、`assign`、`link`、`unlink`、`claim`、`comment`、`complete`、`block`、`unblock`、`archive`、`tail`、`dispatch`、`context`、`init`、`gc`）。上面 CLI 参考中列出的其余动词（`watch`、`stats`、`runs`、`log`、`assignees`、`heartbeat`、`notify-subscribe`、`notify-list`、`notify-unsubscribe`、`daemon`）也有效——它们只是尚未出现在自动补全提示列表中。

## 协作模式

看板支持以下八种模式，无需任何新原语：

| 模式 | 形状 | 示例 |
|---|---|---|
| **P1 扇出** | N 个同辈，相同角色 | “并行研究 5 个角度” |
| **P2 流水线** | 角色链：侦察 → 编辑 → 写作者 | 每日简报汇编 |
| **P3 投票/法定人数** | N 个同辈 + 1 个聚合器 | 3 个研究员 → 1 个审查者选择 |
| **P4 长期运行日志** | 相同配置文件 + 共享目录 + cron | Obsidian vault |
| **P5 人机回环** | 工作者阻塞 → 用户评论 → 解除阻塞 | 模糊决策 |
| **P6 `@mention`** | 来自散文的内联路由 | `@reviewer look at this` |
| **P7 线程范围的工作空间** | 线程中的 `/kanban here` | 每个项目的网关线程 |
| **P8 农场机群** | 一个配置文件，N 个主体 | 50 个社交账号 |
| **P9 分类指定器** | 粗略想法 → `triage` → `hermes kanban specify` 扩展正文 → `todo` | “将这行内容变成一个规范任务” |

有关每个模式的详细示例，请参阅 `docs/hermes-kanban-v1-spec.pdf`。

## 多租户使用

当一个专家机群服务于多个业务时，用租户标记每个任务：

```bash
hermes kanban create "monthly report" \
    --assignee researcher \
    --tenant business-a \
    --workspace dir:~/tenants/business-a/data/
```

工作者接收 `$HERMES_TENANT` 并用前缀命名其记忆写入。看板、调度器和配置文件定义都是共享的；只有数据是范围的。

## 网关通知

当你从网关（Telegram、Discord、Slack 等）运行 `/kanban create …` 时，原始聊天会自动订阅新任务。网关的后台通知器每隔几秒轮询 `task_events`，并为每个终端事件（`completed`、`blocked`、`gave_up`、`crashed`、`timed_out`）向该聊天发送一条消息。已完成的任务还发送工作者 `--result` 的第一行，这样你无需 `/kanban show` 就能看到结果。

你可以从 CLI 显式管理订阅——当脚本/cron 作业想要通知一个它并非源自的聊天时很有用：

```bash
hermes kanban notify-subscribe t_abcd \
    --platform telegram --chat-id 12345678 --thread-id 7
hermes kanban notify-list
hermes kanban notify-unsubscribe t_abcd \
    --platform telegram --chat-id 12345678 --thread-id 7
```

一旦任务达到 `done` 或 `archived`，订阅会自动移除；无需清理。

## 运行——每次尝试一行

任务是一个逻辑工作单元；**运行**是执行它的一次尝试。当调度器声明一个就绪任务时，它会在 `task_runs` 中创建一行，并将 `tasks.current_run_id` 指向它。当该次尝试结束时——完成、阻塞、崩溃、超时、生成失败、回收——运行行会以一个 `outcome` 关闭，任务的指针被清除。一个被尝试了三次的任务有三行 `task_runs`。

为什么需要两个表而不是仅仅修改任务：你需要**完整的尝试历史**来进行真实世界的事后分析（“第二次审查者尝试到达了批准，第三次合并了”），并且你需要一个干净的地方来挂载每次尝试的元数据——更改了哪些文件、运行了哪些测试、审查者注意到了哪些发现。这些是运行事实，而不是任务事实。

运行也是**结构化交接**所在之处。当工作者完成任务（通过 `kanban_complete(...)`）时，它可以传递：

- `summary`（工具参数）/ `--summary`（CLI）——人类交接；保存在运行上；下游子任务在其 `build_worker_context` 中看到它。
- `metadata`（工具参数）/ `--metadata`（CLI）——自由格式 JSON 字典在运行上；子任务看到它与摘要一起序列化。
- `result`（工具参数）/ `--result`（CLI）——短日志行，放在任务行上（遗留字段，为向后兼容保留）。

下游子任务读取每个父任务的最近一次完成运行的摘要 + 元数据。重试的工作者读取其自身任务的先前尝试（结果、摘要、错误），这样它们不会重复已失败的路径。

```
# 工作者实际做的事情——智能体循环内的工具调用：
kanban_complete(
    summary="implemented token bucket, keys on user_id with IP fallback, all tests pass",
    metadata={"changed_files": ["limiter.py", "tests/test_limiter.py"], "tests_run": 14},
    result="rate limiter shipped",
)
```

当人类需要关闭工作者无法完成的任务时，同样的交接也可以从 CLI 访问——例如，一个被放弃的任务，或你从仪表盘手动标记完成的任务：

```bash
hermes kanban complete t_abcd \
    --result "rate limiter shipped" \
    --summary "implemented token bucket, keys on user_id with IP fallback, all tests pass" \
    --metadata '{"changed_files": ["limiter.py", "tests/test_limiter.py"], "tests_run": 14}'

# 查看重试任务的尝试历史：
hermes kanban runs t_abcd
#   #  OUTCOME       PROFILE           ELAPSED  STARTED
#   1  blocked       worker               12s  2026-04-27 14:02
#        → BLOCKED: need decision on rate-limit key
#   2  completed     worker                8m   2026-04-27 15:18
#        → implemented token bucket, keys on user_id with IP fallback
```

运行在仪表盘上暴露（抽屉中的运行历史部分，每次尝试一行带颜色），也在 REST API 上暴露（`GET /api/plugins/kanban/tasks/:id` 返回一个 `runs[]` 数组）。`PATCH /api/plugins/kanban/tasks/:id` 带有 `{status: "done", summary, metadata}` 将两者转发给内核，因此仪表盘的“标记完成”按钮与 CLI 等效。`task_events` 行携带它们所属的 `run_id`，以便 UI 可以按尝试分组事件，而 `completed` 事件在其有效载荷中嵌入第一行摘要（上限 400 字符），这样网关通知器可以渲染结构化交接而无需第二次 SQL 往返。

**批量关闭注意事项。** `hermes kanban complete a b c --summary X` 被拒绝——结构化交接是每次运行的，因此将相同的摘要复制粘贴到 N 个任务几乎总是错误的。批量关闭*不*带 `--summary` / `--metadata` 仍然适用于常见的“我完成了一堆管理任务”的情况。

**从状态更改回收的运行。** 如果你在仪表盘中将一个正在运行的任务拖离 `running`（回到 `ready`，或直接到 `todo`），或者归档一个仍在运行的任务，进行中的运行会以 `outcome='reclaimed'` 关闭，而不是成为孤儿。`task_runs` 行总是在 `tasks.current_run_id` 为 `NULL` 时处于终端状态，反之亦然——这个不变量在 CLI、仪表盘、调度器和通知器之间保持一致。

**从未声明完成任务的综合运行。** 完成或阻塞一个从未被声明的任务（例如，人类从仪表盘关闭一个 `ready` 任务并带有摘要，或 CLI 用户运行 `hermes kanban complete <ready-task> --summary X`）否则会丢失交接。相反，内核插入一个零持续时间的运行行（`started_at == ended_at`），携带摘要/元数据/原因，以便尝试历史保持完整。