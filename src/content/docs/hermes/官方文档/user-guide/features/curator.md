--- frontmatter ---
---
sidebar_position: 3
title: "策展器"
description: "对代理创建的技能进行后台维护——使用跟踪、过时处理、归档以及LLM驱动的审查"
---

--- body ---
# 策展器（Curator）

策展器是对**代理创建的技能**进行后台维护的过程。它追踪每个技能被查看、使用和修补的频率，将长期未使用的技能通过 `active → stale → archived` 状态流转，并定期启动一个简短的辅助模型审查环节，提出整合建议或修补漂移。

它的存在是为了防止通过[自我改进循环](/user-guide/features/skills#agent-managed-skills-skill_manage-tool)创建的技能无限堆积。每次代理解决一个新问题并保存一个技能时，该技能就会存入 `~/.hermes/skills/`。如果没有维护，最终你会得到几十个狭窄的近似副本，污染目录并浪费 token。

默认情况下（`prune_builtins: true`），策展器可以在 `archive_after_days` 天未被使用后将**未使用的捆绑内置技能**（附带的）归档，同时也会管理它主要管理的代理创建技能。从中心（[agentskills.io](https://agentskills.io)）安装的技能始终不受影响。设置 `curator.prune_builtins: false` 可以恢复仅针对代理创建技能的旧行为，即从不触碰捆绑技能。策展器**也从不自动删除**——最坏的结果是归档到 `~/.hermes/skills/.archive/`，这是可恢复的。

追踪 [issue #7816](https://github.com/NousResearch/hermes-agent/issues/7816)。

## 如何运行

策展器由非活动检查触发，而不是 cron 守护进程。在 CLI 会话启动时，以及在 gateway 的 cron-ticker 线程内的定期 tick 中，Hermes 会检查：

1. 自上次策展器运行以来是否已过去足够的时间（`interval_hours`，默认 **7 天**），以及
2. 代理是否已经空闲了足够长的时间（`min_idle_hours`，默认 **2 小时**）。

如果两者都成立，它会生成一个 `AIAgent` 的后台分支——与记忆/技能自我改进提示使用的模式相同。该分支在自己的提示缓存中运行，并且从不触及当前对话。

:::info 首次运行行为
在全新安装（或之前无策展器的安装在进行 `hermes update` 后第一次 tick）时，策展器**不会立即运行**。第一次观察将 `last_run_at` 播种为“现在”，并将第一次真正运行推迟一个完整的 `interval_hours`。这给了你一个完整的时间间隔来检查你的技能库，固定任何重要内容，或者在策展器触及之前完全退出。

如果你想在策展器实际运行之前查看它*会*做什么，请运行 `hermes curator run --dry-run`——它会生成相同的审查报告，但不会改变库。
:::

一次运行包含两个阶段：

1. **自动转换**（确定性，无需 LLM）。未使用天数超过 `stale_after_days`（30）的技能变为 `stale`；未使用天数超过 `archive_after_days`（90）的技能被移动到 `~/.hermes/skills/.archive/`。这是始终开启的修剪行为——只要策展器启用，它就会运行，无需辅助模型成本。
2. **LLM 整合（consolidation）**（单次辅助模型传递，`max_iterations=8`）——**默认关闭**。当 `curator.consolidate: true` 时，分支代理会调查代理创建的技能，可以使用 `skill_view` 读取其中任何一个，并针对每个技能决定是保留、修补（通过 `skill_manage`）、将重叠的技能整合为类级别的伞形技能（umbrella），还是通过终端工具归档。整合将技能视为一个完整的包：如果某个技能包含 `references/`、`templates/`、`scripts/`、`assets/` 或指向这些路径的相对链接，策展器必须要么将其独立保留，要么重新安置所需的支持文件并重写路径，要么原封不动地将整个包归档——而不是仅将 `SKILL.md` 扁平化到另一个技能的 `references/` 文件中。

:::info 整合是选择加入的
默认情况下，策展器仅**修剪**——确定性非活动传递将技能标记为过时并归档长期未使用的技能。带有观点的 LLM **整合**传递（构建伞形技能、合并重叠技能）默认关闭，因为每次运行都会消耗辅助模型 token，并对你的库进行广泛的结构性更改。使用 `curator.consolidate: true` 打开它，或者按需使用 `hermes curator run --consolidate` 运行一次。
:::

固定的技能（Pinned skills）对策展器的自动转换和代理自己的 `skill_manage` 工具都不可触及。请参见下面的[固定技能](#固定技能pinning-a-skill)。

## 配置

所有设置位于 `config.yaml` 的 `curator:` 下（不是 `.env`——这不是秘密）。默认值：

```yaml
curator:
  enabled: true
  interval_hours: 168          # 7 days
  min_idle_hours: 2
  stale_after_days: 30
  archive_after_days: 90
  consolidate: false           # LLM umbrella-building pass — opt-in (prune-only by default)
  prune_builtins: true         # archive unused bundled built-in skills too (hub skills always exempt)
```

要完全禁用，设置 `curator.enabled: false`。要保留始终开启的修剪但选择 LLM 整合，设置 `curator.consolidate: true`。

### 在更便宜的辅助模型上运行审查

策展器的 LLM 审查传递是一个常规辅助任务槽——`auxiliary.curator`——与 Vision、Compression、Session Search 等并列。“Auto”表示“使用我主要聊天模型”；覆盖该槽可以为审查传递固定特定的提供商+模型。

**最简单的方式——`hermes model`：**

```bash
hermes model                   # → "Auxiliary models — side-task routing"
                               # → pick "Curator" → pick provider → pick model
```

同样的选择器也可以在 Web 仪表板的 **Models** 选项卡中使用。

**直接 config.yaml（等效）：**

```yaml
auxiliary:
  curator:
    provider: openrouter
    model: google/gemini-3-flash-preview
    timeout: 600               # generous — reviews can take several minutes
```

将 `provider: auto`（默认）会使审查传递通过你的主要聊天模型路由，与所有其他辅助任务的行为一致。

:::note 旧配置
早期版本使用了一个一次性的 `curator.auxiliary.{provider,model}` 块。该路径仍然有效，但会输出弃用日志行——请迁移到上面的 `auxiliary.curator`，这样策展器就能与所有其他辅助任务共享相同的管道（`hermes model`、仪表板 Models 选项卡、`base_url`、`api_key`、`timeout`、`extra_body`）。
:::

## CLI 命令

```bash
hermes curator status         # last run, counts, pinned list, LRU top 5
hermes curator run            # trigger a run now (blocks until done). Prune-only unless curator.consolidate: true
hermes curator run --consolidate # force the LLM consolidation pass on for this run, overriding the config default
hermes curator run --background  # fire-and-forget: start the run in a background thread
hermes curator run --dry-run  # preview only — report without any mutations
hermes curator backup         # take a manual snapshot of ~/.hermes/skills/
hermes curator rollback       # restore from the newest snapshot
hermes curator rollback --list     # list available snapshots
hermes curator rollback --id <ts>  # restore a specific snapshot
hermes curator rollback -y         # skip the confirmation prompt
hermes curator pause          # stop runs until resumed
hermes curator resume
hermes curator pin <skill>    # never auto-transition this skill
hermes curator unpin <skill>
hermes curator restore <skill>  # move an archived skill back to active
hermes curator list-archived    # list skills currently in ~/.hermes/skills/.archive/
hermes curator archive <skill>  # manually archive a single skill now
hermes curator prune [--days N] # bulk-archive agent-created skills idle >= N days (default 90)
```

## 备份与回滚

在每次真实的策展器运行之前，Hermes 会取一份 `~/.hermes/skills/` 的 tar.gz 快照，保存在 `~/.hermes/skills/.curator_backups/<utc-iso>/skills.tar.gz`。如果某次运行归档或整合了你不想被触碰的内容，你可以用一个命令撤销整个运行：

```bash
hermes curator rollback        # restore newest snapshot (with confirmation)
hermes curator rollback -y     # skip the prompt
hermes curator rollback --list # see all snapshots with reason + size
```

回滚本身是可逆的：在替换技能树之前，Hermes 会再取一份快照，标记为 `pre-rollback to <target-id>`，因此误回滚可以通过使用 `--id` 回滚到该快照来撤销。

你也可以随时使用 `hermes curator backup --reason "before-refactor"` 手动创建快照。`--reason` 字符串会存入快照的 `manifest.json` 中，并在 `--list` 中显示。

快照数量限制在 `curator.backup.keep`（默认 5）以控制磁盘使用：

```yaml
curator:
  backup:
    enabled: true
    keep: 5
```

设置 `curator.backup.enabled: false` 可禁用自动快照。手动 `hermes curator backup` 命令在备份禁用时仍然有效，但前提是你先将 `enabled: true` 设置一次——该标志对称地控制两条路径，因此不存在在变异运行中意外跳过预运行快照的可能。

`hermes curator status` 还会列出五个最近最少使用的技能——快速了解接下来哪些技能可能变得过时。

相同的子命令也可作为 `/curator` 斜杠命令在运行中的会话（CLI 或 gateway 平台）中使用。

## “代理创建”的含义

策展器仅管理那些在 `~/.hermes/skills/.usage.json` 中显式标记为 **代理创建的** 技能。一个技能在以下**所有**条件成立时符合条件：

1. 其名称**不在** `~/.hermes/skills/.bundled_manifest` 中（附带的捆绑技能）。
2. 其名称**不在** `~/.hermes/skills/.hub/lock.json` 中（从中心安装的技能）。
3. 其 `.usage.json` 条目具有 `"created_by": "agent"` 或 `"agent_created": true`。

目前，只有**后台自我改进审查分支**会设置此标记——当它在定期审查传递（大约每 10 次代理轮次）期间创建新的伞形技能时。后台分支以写源 `"background_review"`（通过 `tools/skill_provenance.py`）运行，这是触发 `skill_manage` 中 `mark_agent_created()` 调用的唯一路径。

前台代理在对话期间通过 `skill_manage(action="create")` 创建的技能**不会**被标记为代理创建——它们被认为是用户导向的，策展器故意不碰它们。

:::warning 你手写的技能不会被策展
如果你手动创建了一个 `SKILL.md` 或将 Hermes 指向外部技能目录，该技能将在 `.usage.json` 中获得 `created_by: null`（或缺少该字段）。策展器不会触碰它。前台代理应你请求创建的技能也是如此。

**要查看策展器实际管理的技能**，请运行 `hermes curator status`。如果代理创建数量为 0，则当前没有技能处于策展器的管辖范围内——LLM 审查传递将被跳过，报告将显示 `Model: (not resolved) via (not resolved)` 且 `Duration: 0s`。
:::

被**标记为代理创建**的技能遵循完整的生命周期：

- `active` → (30 天未使用) `stale` → (90 天未使用) `archived`
- 固定的技能绕过所有自动转换
- 归档的技能可通过 `hermes curator restore <name>` 恢复

如果你想保护某个特定技能免于被触碰——例如你依赖的手写技能——请使用 `hermes curator pin <name>`。请参见下一节。

## 固定技能（Pinning a skill）

固定保护技能不被删除——无论是策展器的自动归档传递还是代理的 `skill_manage(action="delete")` 工具调用。一旦技能被固定：

- **策展器**在自动转换（`active → stale → archived`）时跳过它，并且其 LLM 审查传递被指示不要碰它。
- **代理的 `skill_manage` 工具**拒绝对其执行 `delete`，并提示用户 `hermes curator unpin <name>`。修补和编辑仍然可以进行，因此代理可以在遇到陷阱时改进固定技能的内容，而不必进行固定/取消固定/重新固定的操作。

使用以下命令固定和取消固定：

```bash
hermes curator pin <skill>
hermes curator unpin <skill>
```

该标志作为 `"pinned": true` 存储在技能在 `~/.hermes/skills/.usage.json` 的条目中，因此跨会话持久化。

只有**代理创建的**技能可以被固定——`hermes curator pin` 会拒绝操作捆绑和中心安装的技能，并给出解释信息。中心安装的技能始终不受策展器变更的影响。捆绑的内置技能仅在 `curator.prune_builtins: true`（默认）时被触碰，而且即使如此也仅在 `archive_after_days` 天未使用后被归档——永远不会被修补、整合或删除。设置 `curator.prune_builtins: false` 可完全豁免捆绑技能。

一小部分**受保护的内置技能**被硬编码为不可归档且不可整合，无论 `curator.prune_builtins`、固定状态或 LLM 判断如何。这些技能承载着重要的用户体验——例如，`plan` 驱动 `/plan` 斜杠命令流程——因此静默归档一个会导致该斜杠命令变成“未知命令”错误，且不给你任何信号。受保护的内置技能被完全过滤掉，不出现在策展器的候选列表中，因此整合传递永远不会看到它们。

如果你想要比“不可删除”更强的保证——例如在代理仍可读取技能的同时完全冻结其内容——请直接用你的编辑器编辑 `~/.hermes/skills/<name>/SKILL.md`。固定保护的是工具驱动的删除，而不是你自己的文件系统访问。

## 使用遥测（Usage telemetry）

策展器维护一个边车文件 `~/.hermes/skills/.usage.json`，每个技能对应一个条目：

```json
{
  "my-skill": {
    "use_count": 12,
    "view_count": 34,
    "last_used_at": "2026-04-24T18:12:03Z",
    "last_viewed_at": "2026-04-23T09:44:17Z",
    "patch_count": 3,
    "last_patched_at": "2026-04-20T22:01:55Z",
    "created_at": "2026-03-01T14:20:00Z",
    "state": "active",
    "pinned": false,
    "archived_at": null
  }
}
```

计数器在以下情况递增：

- `view_count`：代理对该技能调用 `skill_view`。
- `use_count`：该技能被加载到对话提示中。
- `patch_count`：对该技能执行 `skill_manage patch/edit/write_file/remove_file`。

捆绑和中心安装的技能被明确排除在遥测写入之外。

## 每次运行的报告

每次策展器运行会在 `~/.hermes/logs/curator/` 下写入一个带时间戳的目录：

```
~/.hermes/logs/curator/
└── 20260429-111512/
    ├── run.json      # machine-readable: full fidelity, stats, LLM output
    └── REPORT.md     # human-readable summary
```

`REPORT.md` 是快速查看某次运行做了什么的好方法——哪些技能发生了转换、LLM 审查者说了什么、修补了哪些技能。适合审计，而无需 grep `agent.log`。

:::note 没有候选？报告显示 `(not resolved)`
当策展器**没有要审查的代理创建技能**时，LLM 审查传递被完全跳过。报告头部将显示 `Model: (not resolved) via (not resolved)` 且 `Duration: 0s`——这**不**表示配置错误或模型解析失败。这仅仅意味着没有候选，因此从未调用模型。自动转换阶段仍然运行并正常报告其计数。
:::

### 摘要中的重命名映射

如果某次运行将多个技能整合到一个伞形技能下（或合并了近似重复），运行结束时打印的用户可见摘要会包含一个显式的重命名映射，显示策展器应用的每一对 `旧名称 → 新名称`。这是对每个技能转换行的补充，因此当一波重命名到来时，你可以一目了然地发现它们，而无需比对 JSON 报告。该提示也会在 `hermes curator pin` 下显示，因此如果你想要锁定新标签，可以立即固定伞形技能名称。

## 恢复归档的技能

如果策展器归档了你仍然想要的内容：

```bash
hermes curator restore <skill-name>
```

这会将技能从 `~/.hermes/skills/.archive/` 移回活动树，并将其状态重置为 `active`。如果同名捆绑或中心安装的技能后来已被安装（会遮蔽上游），恢复操作会拒绝。

## 按环境禁用

策展器默认开启。要关闭它：

- **仅针对一个配置文件：** 编辑 `~/.hermes/config.yaml`（或活动配置文件的配置），设置 `curator.enabled: false`。
- **仅针对一次运行：** `hermes curator pause`——暂停状态跨会话持久化；使用 `resume` 重新启用。

如果 `min_idle_hours` 尚未过去，策展器也会拒绝运行，因此在活跃的开发机器上它自然只在安静时段运行。

## 另请参见

- [技能系统](/user-guide/features/skills) —— 技能通常如何工作以及创建技能的自我改进循环
- [记忆](/user-guide/features/memory) —— 维护长期记忆的并行后台审查
- [捆绑技能目录](/reference/skills-catalog)
- [问题 #7816](https://github.com/NousResearch/hermes-agent/issues/7816) —— 原始提案和设计讨论