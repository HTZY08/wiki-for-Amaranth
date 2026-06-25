---
title: Slash Commands
---

sidebar_position: 2
title: "斜杠命令参考"
description: "交互式 CLI 和消息斜杠命令的完整参考"
---

--- body ---
# 斜杠命令参考

Hermes 有两个斜杠命令界面，均由 `hermes_cli/commands.py` 中的中央 `COMMAND_REGISTRY` 驱动：

- **交互式 CLI 斜杠命令** — 由 `cli.py` 分发，带有来自注册表的自动补全
- **消息斜杠命令** — 由 `gateway/run.py` 分发，帮助文本和平台菜单由注册表生成

已安装的技能（skill）也在两个界面上作为动态斜杠命令公开。这包括捆绑的技能，如 `/plan`，它会打开计划模式并将 markdown 计划保存在相对于活动工作区/后端工作目录的 `.hermes/plans/` 中。

## 权限与管理员/普通用户分离

每个支持按用户白名单的消息平台（Telegram、Discord、Slack、Matrix、Mattermost、Signal 等）也支持两层斜杠命令分离：**管理员**可以使用所有已注册的命令，**普通用户**只能使用你在 `user_allowed_commands` 中列出的命令（加上始终允许的基本命令 `/help` 和 `/whoami`）。在 `~/.hermes/gateway-config.yaml` 中的平台 `extra:` 块内配置 `allow_admin_from` 和 `user_allowed_commands`（以及按群组对应的 `group_allow_admin_from` / `group_user_allowed_commands`）。

有关示例，请参阅每个平台的文档 — 结构在所有平台中相同：

- [Telegram](../user-guide/messaging/telegram.md#slash-command-access-control)
- [Discord](../user-guide/messaging/discord.md)
- [Slack](../user-guide/messaging/slack.md)
- [Matrix](../user-guide/messaging/matrix.md)
- [Mattermost](../user-guide/messaging/mattermost.md)
- [Signal](../user-guide/messaging/signal.md)

如果某个作用域的 `allow_admin_from` 未设置，则该作用域保持不受限制的向后兼容模式 — 每个允许的用户都可以运行所有命令。

## 交互式 CLI 斜杠命令

在 CLI 中输入 `/` 可打开自动补全菜单。内置命令不区分大小写。

### 会话（Session）

| 命令 | 描述 |
|---------|-------------|
| `/new [name]`（别名：`/reset`） | 开始一个新的会话（新的会话 ID + 历史记录）。可选的 `[name]` 设置初始会话标题 — 例如 `/new my-experiment` 会打开一个已标记为 `my-experiment` 的新会话，以便稍后使用 `/resume` 或 `/sessions` 轻松找到。追加 `now`、`--yes` 或 `-y` 可跳过确认弹窗 — 例如 `/reset now`、`/new --yes my-experiment`。 |
| `/clear` | 清屏并开始新会话 |
| `/history` | 显示对话历史 |
| `/save` | 保存当前对话 |
| `/retry` | 重试最后一条消息（重新发送给智能体） |
| `/undo` | 删除最后一次用户/助手的交换内容 |
| `/title` | 为当前会话设置标题（用法：/title 我的会话名称） |
| `/compress [here [N] \| focus topic]` | 手动压缩对话上下文（清除记忆 + 总结）。`/compress here [N]` 会总结除最近 N 条交换（默认为 2）之外的所有内容，最近内容保持原样 — 你可以选择自己的压缩边界。通过焦点主题（focus topic）可以缩小完整总结保留的范围。 |
| `/rollback` | 列出或恢复文件系统检查点（用法：/rollback [number]） |
| `/snapshot [create\|restore <id>\|prune]`（别名：`/snap`） | 创建或恢复 Hermes 配置/状态的状态快照。`create [label]` 保存快照，`restore <id>` 还原到该快照，`prune [N]` 移除旧快照，无参数时列出所有。 |
| `/stop` | 终止所有正在运行的后台进程 |
| `/queue <prompt>`（别名：`/q`） | 为下一轮排队一个提示（不中断当前智能体响应）。 |
| `/steer <prompt>` | 插入一条中间运行的提示，该提示在 **下一次工具调用之后** 到达智能体 — 不中断，不产生新的用户轮次。文本会在当前工具完成后追加到最后一条工具结果的内容中，从而在不中断当前工具调用循环的情况下为智能体提供新上下文。可用于在任务进行中引导方向（例如，当智能体运行测试时提示“专注于认证模块”）。 |
| `/goal <text>` | 设置一个持久目标（persistent goal），Hermes 会在各轮次之间持续努力 — 这是我们对 Ralph 循环的实现。每轮之后，一个辅助评判模型（judge model）会判断目标是否完成；如果未完成，Hermes 会自动继续。子命令：`/goal status`、`/goal pause`、`/goal resume`、`/goal clear`。预算默认为 20 轮（`goals.max_turns`）；任何真实的用户消息都会抢占继续循环，状态在 `/resume` 后保留。参见 [持久化目标](/user-guide/features/goals) 了解完整指南。 |
| `/subgoal <text>` | 在循环期间向活动目标追加一个用户提供的标准。继续提示会按原样将所有子目标呈现给智能体，评判模型会将其纳入 DONE/CONTINUE 判断 — 因此只有当原始目标 **和** 所有子目标都满足时，目标才会标记为完成。子命令：`/subgoal`（列出）、`/subgoal remove <N>`、`/subgoal clear`。需要激活 `/goal`。 |
| `/resume [name]` | 恢复一个之前命名的会话 |
| `/sessions`（TUI 别名：`/switch`） | 经典 CLI：在交互式选择器中浏览和恢复之前的会话。TUI：打开当前打开 TUI 会话的实时会话切换器。在 TUI 中使用 `/sessions new` 可立即启动另一个实时会话。 |
| `/redraw` | 强制完全重绘 UI（可从 tmux 调整大小、鼠标选择伪影等导致的终端错位中恢复） |
| `/status` | 显示会话信息 — 模型、提供商、配置文件、会话 ID、工作目录、标题、创建/更新时间戳、令牌总数、智能体运行状态 — 后跟一个本地 **会话回顾（Session recap）** 区块（最近用户/助手轮次计数、工具结果数、使用最多的工具、最近接触的文件、最新用户提示和最新助手回复）。回顾从内存对话中本地计算；无需调用 LLM，不影响提示缓存。 |
| `/agents`（别名：`/tasks`） | 显示当前会话中的活动智能体和正在运行的任务。 |
| `/background <prompt>`（别名：`/bg`、`/btw`） | 在单独的后台会话中运行一个提示。智能体会独立处理你的提示 — 当前会话仍可自由进行其他工作。任务完成时结果以面板形式显示。参见 [CLI 后台会话](/user-guide/cli#background-sessions)。 |
| `/branch [name]`（别名：`/fork`） | 分支当前会话（探索不同的路径） |
| `/handoff <platform>` | **仅 CLI。** 将当前会话移交给消息平台（Telegram、Discord、Slack、WhatsApp、Signal、Matrix）。网关立即接收，在支持线程的平台（Telegram 主题、Discord 文本频道线程、Slack 消息锚定线程）上创建新线程，将目标重新绑定到你的 CLI session_id，以便完整的角色感知对话记录得以回放，并伪造一个合成用户轮次，让智能体确认它正在新位置工作。你的 CLI 在成功时干净退出，并显示 `/resume` 提示；随时使用 `/resume <title>` 在本地恢复。不允许在对话中途使用。需要网关正在运行且已为目标平台配置了主频道（从目标聊天中使用 `/sethome`）。参见 [跨平台移交](/user-guide/sessions#cross-platform-handoff)。 |

### 配置（Configuration）

| 命令 | 描述 |
|---------|-------------|
| `/config` | 显示当前配置 |
| `/model [model-name]` | 显示或更改当前模型。支持：`/model claude-sonnet-4`、`/model provider:model`（切换提供商）、`/model custom:model`（自定义端点）、`/model custom:name:model`（命名自定义提供商）、`/model custom`（从端点自动检测）以及用户定义的别名（`/model fav`、`/model grok` — 参见 [自定义模型别名](#custom-model-aliases)）。使用 `--global` 将更改持久化到 config.yaml。**注意：** `/model` 只能切换到已配置的提供商。要添加新提供商，请退出会话并从终端运行 `hermes model`。 |
| `/codex-runtime [auto\|codex_app_server\|on\|off]` | 切换可选的 [Codex 应用服务器运行时](../user-guide/features/codex-app-server-runtime) 用于 OpenAI/Codex 模型。`auto`（默认）使用 Hermes 标准聊天补全；`codex_app_server` 将轮次交给 `codex app-server` 子进程，以支持原生 shell、apply_patch、ChatGPT 订阅认证和已迁移的 Codex 插件。在下一个会话生效。 |
| `/personality` | 设置预定义的个性 |
| `/verbose` | 循环切换工具进度显示：关闭 → 新 → 全部 → 详细。可通过配置为[消息启用](#notes)。 |
| `/fast [normal\|fast\|status]` | 切换快速模式 — OpenAI 优先处理 / Anthropic 快速模式。选项：`normal`、`fast`、`status`。 |
| `/reasoning` | 管理推理努力和显示（用法：/reasoning [level\|show\|hide]） |
| `/skin` | 显示或更改显示皮肤/主题 |
| `/statusbar`（别名：`/sb`） | 切换上下文/模型状态栏的显示或隐藏 |
| `/voice [on\|off\|tts\|status]` | 切换 CLI 语音模式和语音播放。录音使用 `voice.record_key`（默认：`Ctrl+B`）。 |
| `/yolo` | 切换 YOLO 模式 — 跳过所有危险命令批准提示。 |
| `/footer [on\|off\|status]` | 在最终回复上切换网关运行时元数据页脚（显示模型、上下文百分比和当前工作目录）。 |
| `/busy [queue\|steer\|interrupt\|status]` | 仅 CLI：控制 Hermes 工作时按 Enter 键的行为 — 将新消息排队、在轮次中引导或立即中断。 |
| `/indicator [kaomoji\|emoji\|unicode\|ascii]` | 仅 CLI：选择 TUI 忙碌指示器的样式。 |

### 工具与技能（Tools & Skills）

| 命令 | 描述 |
|---------|-------------|
| `/tools [list\|disable\|enable] [name...]` | 管理工具：列出可用工具，或为当前会话禁用/启用特定工具。禁用工具会将其从智能体的工具集中移除，并触发会话重置。 |
| `/toolsets` | 列出可用的工具集 |
| `/browser [connect\|disconnect\|status]` | 管理本地 Chromium 系列 CDP 连接。`connect` 将浏览器工具附加到正在运行的 Chrome、Brave、Chromium 或 Edge 实例（默认：`http://127.0.0.1:9222`）。`disconnect` 断开连接。`status` 显示当前连接。如果未检测到调试器，则会自动启动支持的 Chromium 系列浏览器。 |
| `/skills` | 从在线注册表搜索、安装、检查或管理技能。同时也是技能写入批准网关的审查界面：`/skills pending`、`/skills diff <id>`、`/skills approve <id>`、`/skills reject <id>`、`/skills approval on\|off`。参见 [门控智能体技能写入](/user-guide/features/skills#gating-agent-skill-writes-skillswrite_approval)。 |
| `/memory [pending\|approve\|reject\|approval]` | 审查由写入批准网关（`memory.write_approval`）暂存的挂起记忆写入，并切换网关。参见 [控制记忆写入](/user-guide/features/memory#controlling-memory-writes-write_approval)。 |
| `/bundles` | 列出配置的技能包（skill bundle） — `/<name>` 斜杠别名，可一次预加载多个技能。在 `~/.hermes/config.yaml` 的 `bundles:` 下配置。参见 [技能包](/user-guide/features/skills#skill-bundles)。 |
| `/learn <what to learn from>` | 从你描述的任何内容中提炼可重用的技能 — 目录、URL、你刚刚让智能体执行的工作流程或粘贴的笔记。开放式的：智能体使用自己的工具收集来源，并根据内部编写标准创建 `SKILL.md`。适用于 CLI、消息网关、TUI 和仪表板技能页面。 |
| `/cron` | 管理定时任务（列出、添加/创建、编辑、暂停、恢复、运行、移除） |
| `/suggestions [accept\|dismiss N\|catalog\|clear]`（别名：`/suggest`） | 审查建议的自动化任务。使用 `/suggestions` 列出挂起的建议，`/suggestions accept <id>` 创建建议的自动化任务，`/suggestions dismiss <id>` 拒绝一个，`/suggestions catalog` 添加精选的入门自动化任务，`/suggestions clear` 清除已解决的建议记录。接受的任务会将当前界面保存为交付来源。 |
| `/blueprint [name] [slot=value ...]`（别名：`/bp`） | 从蓝图模板设置自动化任务。单独运行 `/blueprint` 列出目录；`/blueprint <name>` 在下一个智能体轮次启动引导式填空流程；`/blueprint <name> slot=value ...` 直接创建任务。 |
| `/curator` | 后台技能维护 — `status`、`run`、`pin`、`archive`。参见 [策展人](/user-guide/features/curator)。 |
| `/kanban <action>` | 无需离开聊天即可驱动多配置文件、多项目协作看板。完整的 `hermes kanban` 界面可用：`/kanban list`、`/kanban show t_abc`、`/kanban create "title" --assignee X`、`/kanban comment t_abc "text"`、`/kanban unblock t_abc`、`/kanban dispatch` 等。支持多看板：`/kanban boards list`、`/kanban boards create <slug>`、`/kanban boards switch <slug>`、`/kanban --board <slug> <action>`。参见 [看板斜杠命令](/user-guide/features/kanban#kanban-slash-command)。 |
| `/reload-mcp`（别名：`/reload_mcp`） | 从 config.yaml 重新加载 MCP 服务器 |
| `/reload-skills`（别名：`/reload_skills`） | 重新扫描 `~/.hermes/skills/` 以检测新安装或移除的技能 |
| `/reload` | 将 `.env` 变量重新加载到当前会话（无需重启即可获取新的 API 密钥） |
| `/plugins` | 列出已安装的插件及其状态 |

### 信息（Info）

| 命令 | 描述 |
|---------|-------------|
| `/help` | 显示此帮助信息 |
| `/version` | 显示 Hermes Agent 版本、构建和环境信息。 |
| `/usage` | 显示令牌使用量、成本明细、会话时长，并且 — 当活动提供商支持时 — 显示 **账户限制（Account limits）** 部分，包含从提供商 API 实时获取的剩余配额/积分/套餐使用情况。 |
| `/credits` | 显示你的 Nous 信用余额和充值跳转链接。 |
| `/billing` | CLI 终端计费流程（用于 Nous） — 查看余额、购买信用、管理自动充值/月度限制。 |
| `/insights` | 显示使用洞察和分析（过去 30 天） |
| `/platforms`（别名：`/gateway`） | 显示网关/消息平台状态（仅 CLI 摘要视图）。 |
| `/paste` | 附加剪贴板图像 |
| `/copy [number]` | 将最后一条助手响应复制到剪贴板（使用数字可复制倒数第 N 条）。仅 CLI。 |
| `/image <path>` | 附加本地图像文件作为下一个提示。 |
| `/debug` | 上传调试报告（系统信息 + 日志）并获取可共享链接。也可在消息中使用。 |
| `/profile` | 显示活动配置文件名称和主目录 |

### 退出（Exit）

| 命令 | 描述 |
|---------|-------------|
| `/quit` | 退出 CLI（也可使用 `/exit`）。 |

### 动态 CLI 斜杠命令

| 命令 | 描述 |
|---------|-------------|
| `/<skill-name>` | 将任何已安装的技能作为按需命令加载。示例：`/gif-search`、`/github-pr-workflow`、`/excalidraw`。 |
| `/skills ...` | 从注册表和官方可选技能目录中搜索、浏览、检查、安装、审计、发布和配置技能。 |

### 快速命令（Quick Commands）

用户定义的快速命令将短斜杠命令映射到 shell 命令或另一个斜杠命令。在 `~/.hermes/config.yaml` 中配置：

```yaml
quick_commands:
  status:
    type: exec
    command: systemctl status hermes-agent
  deploy:
    type: exec
    command: scripts/deploy.sh
  inbox:
    type: alias
    target: /gmail unread
```

然后在 CLI 或消息平台中输入 `/status`、`/deploy` 或 `/inbox`。快速命令在分发时解析，可能不会出现在所有内置的自动补全/帮助表中。

仅包含字符串的提示快捷方式不支持作为快速命令。将较长的可重用提示放入技能中，或使用 `type: alias` 指向现有斜杠命令。

### 自定义模型别名

为你经常使用的模型定义自己的短名称，然后在 CLI 或任何消息平台中用 `/model <alias>` 使用它们。别名在两者中工作方式相同，支持仅会话（默认）和 `--global` 开关。

支持两种配置格式：

**完整格式** — 固定精确模型、提供商，以及可选的 base URL。在 `~/.hermes/config.yaml` 中放入：

```yaml
model_aliases:
  fav:
    model: claude-sonnet-4.6
    provider: anthropic
  grok:
    model: grok-4
    provider: x-ai
  ollama-qwen:
    model: qwen3-coder:30b
    provider: custom
    base_url: http://localhost:11434/v1
```

**短格式** — 以 `provider/model` 形式放在一个字符串中。无需编辑 YAML 即可从 shell 设置：

```bash
hermes config set model.aliases.fav anthropic/claude-opus-4.6
hermes config set model.aliases.grok x-ai/grok-4
```

然后在聊天中使用：

```
/model fav            # 仅会话
/model grok --global  # 同时也将当前模型更改持久化到 config.yaml
```

用户别名优先于内置短名称，因此将别名命名为 `sonnet`、`kimi`、`opus` 等将覆盖内置名称。别名名称不区分大小写。

### 别名解析

命令支持前缀匹配：输入 `/h` 解析为 `/help`，`/mod` 解析为 `/model`。当前缀有歧义（匹配多个命令）时，按注册表顺序优先匹配第一个。完整命令名称和注册别名始终优先于前缀匹配。

## 消息斜杠命令

消息网关在 Telegram、Discord、Slack、WhatsApp、Signal、Email、Home Assistant 和 Teams 聊天中支持以下内置命令：

| 命令 | 描述 |
|---------|-------------|
| `/start` | 平台协议命令。许多聊天平台（Telegram、Discord 等）在用户首次打开机器人对话时自动发送 `/start`。Hermes 默默地确认该 ping — 不回复智能体，不消耗会话轮次 — 因此首次接触握手不会浪费一个轮次。你也可以显式发送它来确认网关可达。 |
| `/new` | 开始新的对话。 |
| `/reset` | 重置对话历史。 |
| `/status` | 显示会话信息，后跟一个本地 **会话回顾（Session recap）** 区块（最近轮次计数、使用最多的工具、接触的文件、最新提示 + 回复）。 |
| `/stop` | 终止所有正在运行的后台进程并中断正在运行的智能体。 |
| `/model [provider:model]` | 显示或更改模型。支持提供商切换（`/model zai:glm-5`）、自定义端点（`/model custom:model`）、命名自定义提供商（`/model custom:local:qwen`）、自动检测（`/model custom`）以及用户定义的别名（`/model fav`、`/model grok` — 参见 [自定义模型别名](#custom-model-aliases)）。使用 `--global` 将更改持久化到 config.yaml。**注意：** `/model` 只能切换到已配置的提供商。要添加新提供商或设置 API 密钥，请从终端运行 `hermes model`（在聊天会话之外）。 |
| `/codex-runtime [auto\|codex_app_server\|on\|off]` | 切换可选的 [Codex 应用服务器运行时](../user-guide/features/codex-app-server-runtime)。持久化到 config.yaml 中的 `model.openai_runtime` 并驱逐缓存的智能体，以便下一条消息使用新的运行时。在下一个会话生效。 |
| `/personality [name]` | 为会话设置个性叠加层。 |
| `/fast [normal\|fast\|status]` | 切换快速模式 — OpenAI 优先处理 / Anthropic 快速模式。 |
| `/retry` | 重试最后一条消息。 |
| `/undo` | 删除最后一次交换内容。 |
| `/sethome`（别名：`/set-home`） | 将当前聊天标记为平台主频道用于交付。 |
| `/compress [here [N] \| focus topic]` | 手动压缩对话上下文。`/compress here [N]` 保留最近 N 条交换（默认为 2）原样，并总结其余部分。焦点主题缩小完整总结保留的范围。 |
| `/topic [off\|help\|session-id]` | **仅 Telegram 私聊。** 管理用户管理的多会话主题模式。`/topic` 启用它或显示状态；`/topic off` 禁用它并清除绑定；`/topic help` 显示用法；在主题内使用 `/topic <session-id>` 恢复之前的会话。参见 [多会话私聊模式](/user-guide/messaging/telegram#multi-session-dm-mode-topic)。 |
| `/title [name]` | 设置或显示会话标题。 |
| `/resume [name]` | 恢复之前命名的会话。 |
| `/usage` | 显示令牌使用量、估算成本明细（输入/输出）、上下文窗口状态、会话时长，并且 — 当活动提供商支持时 — 显示 **账户限制（Account limits）** 部分，包含从提供商 API 实时获取的剩余配额/积分。 |
| `/credits` | 显示你的 Nous 信用余额和充值链接，该链接会在浏览器中打开门户计费页面。 |
| `/insights [days]` | 显示使用分析。 |
| `/reasoning [level\|show\|hide]` | 更改推理努力或切换推理显示。 |
| `/voice [on\|off\|tts\|join\|channel\|leave\|status]` | 控制聊天中的语音回复。`join`/`channel`/`leave` 管理 Discord 语音频道模式。 |
| `/rollback [number]` | 列出或恢复文件系统检查点。 |
| `/background <prompt>` | 在单独的后台会话中运行提示。任务完成时结果将交付回同一聊天。参见 [消息后台会话](/user-guide/messaging/#background-sessions)。 |
| `/queue <prompt>`（别名：`/q`） | 为下一轮排队一个提示，不中断当前轮次。 |
| `/steer <prompt>` | 在下一个工具调用之后插入一条消息而不中断 — 模型在下次迭代时接收它，而不是作为新轮次。 |
| `/goal <text>` | 设置一个持久目标，Hermes 会在各轮次之间持续努力。评判模型在每轮后检查；如果未完成，Hermes 自动继续直到完成、你暂停/清除它或达到轮次预算（默认为 20）。子命令：`/goal status`、`/goal pause`、`/goal resume`、`/goal clear`。在智能体运行中执行 status/pause/clear 是安全的；设置新目标需要先执行 `/stop`。参见 [持久化目标](/user-guide/features/goals)。 |
| `/footer [on\|off\|status]` | 在最终回复上切换运行时元数据页脚（显示模型、上下文百分比和当前工作目录）。 |
| `/curator [status\|run\|pin\|archive]` | 后台技能维护控制。 |
| `/suggestions [accept\|dismiss N\|catalog\|clear]` | 直接在聊天中审查建议的自动化任务。`/suggestions` 列出挂起的建议，`catalog` 添加精选的入门自动化任务，`clear` 清除已解决的建议记录。接受的建议保留此聊天/线程作为任务交付来源。 |
| `/blueprint [name] [slot=value ...]` | 浏览 cron 蓝图、开始引导式填空对话或直接创建蓝图任务。直接创建的任务会交付回当前聊天/线程。 |
| `/memory [pending\|approve\|reject\|approval]` | 审查由写入批准网关（`memory.write_approval`）暂存的挂起记忆写入 — 在聊天中批准或拒绝它们 — 并使用 `/memory approval on\|off` 切换网关。参见 [控制记忆写入](/user-guide/features/memory#controlling-memory-writes-write_approval)。 |
| `/skills [pending\|approve\|reject\|diff\|approval]` | 审查由写入批准网关（`skills.write_approval`）暂存的挂起 **技能** 写入。每个暂存写入显示一行摘要；`/skills diff <id>` 在聊天中会被截断 — 在 CLI 或 `~/.hermes/pending/skills/<id>.json` 中查看完整差异。仅在网关开启（或暂存写入仍存在）时出现；搜索/安装仍为 CLI 专用。 |
| `/kanban <action>` | 从聊天驱动多配置文件、多项目协作看板 — 参数界面与 CLI 相同。绕过正在运行的智能体守卫，因此 `/kanban unblock t_abc`、`/kanban comment t_abc "…"`、`/kanban list --mine`、`/kanban boards switch <slug>` 等可在智能体运行中执行。`/kanban create …` 会自动将发起聊天的线程订阅到新任务的终端事件。参见 [看板斜杠命令](/user-guide/features/kanban#kanban-slash-command)。 |
| `/platform <list\|pause\|resume> [name]` | 直接在聊天中操作正在运行的网关平台。`/platform list` 显示每个适配器及其状态（运行中、因断路器暂停、手动暂停）；`/platform pause <name>` 停止向该适配器分发新消息而不卸载它；`/platform resume <name>` 重新启用它并在上游恢复后清除跳闸的断路器。 |
| `/reload-mcp`（别名：`/reload_mcp`） | 从配置重新加载 MCP 服务器。 |
| `/yolo` | 切换 YOLO 模式 — 跳过所有危险命令批准提示。 |
| `/commands [page]` | 浏览所有命令和技能（分页）。 |
| `/approve [session\|always]` | 批准并执行挂起的危险命令。`session` 仅本会话批准；`always` 添加到永久白名单。 |
| `/deny` | 拒绝挂起的危险命令。 |
| `/update` | 更新 Hermes Agent 到最新版本。 |
| `/restart` | 在耗尽活动运行后优雅重启网关。当网关重新上线时，它会向请求者的聊天/线程发送确认消息。 |
| `/debug` | 上传调试报告（系统信息 + 日志）并获取可共享链接。 |
| `/help` | 显示消息帮助。 |
| `/<skill-name>` | 按名称调用任何已安装的技能。 |

## 注意

- `/skin`、`/snapshot`、`/reload`、`/tools`、`/toolsets`、`/browser`、`/config`、`/cron`、`/platforms`、`/paste`、`/image`、`/statusbar`、`/plugins`、`/busy`、`/indicator`、`/redraw`、`/clear`、`/history`、`/save`、`/copy`、`/handoff`、`/billing` 和 `/quit` 是 **仅 CLI** 命令。
- `/skills` 的搜索/浏览/安装是 **仅 CLI**；其写入批准审查子命令（`pending`、`approve`、`reject`、`diff`、`approval`）在 `skills.write_approval` 开启时也适用于消息平台。`/memory` 在 **两个** 界面都有效。
- `/verbose` 默认 **仅 CLI**，但可通过在 `config.yaml` 中设置 `display.tool_progress_command: true` 为消息平台启用。启用后，它会循环切换 `display.tool_progress` 模式并保存到配置。
- `/sethome`、`/update`、`/restart`、`/approve`、`/deny`、`/topic`、`/platform` 和 `/commands` 是 **仅消息** 命令。
- `/status`、`/version`、`/background`、`/queue`、`/steer`、`/voice`、`/reload-mcp`、`/reload-skills`、`/rollback`、`/debug`、`/fast`、`/footer`、`/curator`、`/kanban`、`/credits`、`/suggestions`、`/blueprint`、`/learn`、`/sessions` 和 `/yolo` 在 **CLI 和消息网关** 中都有效。
- `/voice join`、`/voice channel` 和 `/voice leave` 仅在 Discord 上有意义。
- 在 TUI 中，`/sessions` 显示当前 TUI 进程中的实时会话。使用 `/resume [name]` 或 `hermes --tui --resume <id-or-title>` 查看已保存或已关闭的对话记录。

## 破坏性命令的确认提示

CLI 在运行会丢弃未保存会话状态的斜杠命令前会提示。当前破坏性命令集为：

| 命令 | 它破坏的内容 |
|---------|-------------|
| `/clear` | 清屏并开始新会话 — 当前会话 ID 和内存历史记录被清除。 |
| `/new` / `/reset` | 开始新会话（新会话 ID + 空历史记录）。 |
| `/undo` | 从历史记录中删除最后一次用户/助手的交换内容。 |
| `/exit --delete` / `/quit --delete` | 退出 **并且** 永久删除当前会话的 SQLite 历史记录和磁盘上的对话记录。 |

对于这些命令，CLI 会打开一个三选项弹窗：**一次性批准（Approve Once）**（本次继续）、**始终批准（Always Approve）**（继续并将 `approvals.destructive_slash_confirm: false` 持久化，以便未来破坏性命令无需提示）、或 **取消（Cancel）**。

**内联跳过：** 追加 `now`、`--yes` 或 `-y` 以在单次调用中绕过弹窗 — 例如 `/reset now`、`/new --yes my-session`、`/clear -y`、`/undo -y`。当弹窗在终端中显示不正确（参见 [issue #30768](https://github.com/NousResearch/hermes-agent/issues/30768) 关于原生 Windows PowerShell）或针对 CLI 编写脚本时很有用。

在 `~/.hermes/config.yaml` 中设置 `approvals.destructive_slash_confirm: false` 以全局禁用提示；设置回 `true` 以重新启用。参见 [安全 — 破坏性斜杠命令确认](../user-guide/security.md#dangerous-command-approval) 了解背景信息。