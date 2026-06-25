---
sidebar_position: 1
title: "CLI 界面"
description: "掌握 Hermes Agent 终端界面 — 命令、快捷键、人格等"
---

# CLI 界面

Hermes Agent 的 CLI 是一个完整的终端用户界面（TUI），而非网页 UI。它支持多行编辑、斜杠命令自动补全、对话历史、中断与重定向、以及流式工具输出。专为习惯于终端操作的用户打造。

:::tip 首次设置
只需一条命令 — `hermes setup --portal` — 即可准备开始 `hermes chat`。请参阅 [Nous Portal](/integrations/nous-portal)。
:::

:::tip
Hermes 还附带了一个现代化的 TUI，支持模态覆盖、鼠标选择和免阻塞输入。使用 `hermes --tui` 启动 — 请参阅 [TUI](tui.md) 指南。
:::

## 运行 CLI

```bash
# 启动交互式会话（默认）
hermes

# 单次查询模式（非交互）
hermes chat -q "Hello"

# 使用特定模型
hermes chat --model "anthropic/claude-sonnet-4"

# 使用特定提供商
hermes chat --provider nous        # 使用 Nous Portal
hermes chat --provider openrouter  # 强制使用 OpenRouter

# 使用特定工具集
hermes chat --toolsets "web,terminal,skills"

# 启动时预加载一个或多个技能
hermes -s hermes-agent-dev,github-auth
hermes chat -s github-pr-workflow -q "open a draft PR"

# 恢复之前的会话
hermes --continue             # 恢复最近的 CLI 会话 (-c)
hermes --resume <session_id>  # 按 ID 恢复特定会话 (-r)

# 详细模式（调试输出）
hermes chat --verbose

# 隔离的 git 工作树（用于并行运行多个代理）
hermes -w                         # 在工作树中交互模式
hermes -w -z "Fix issue #123"     # 在工作树中单次查询
```

## 界面布局

<img className="docs-terminal-figure" src="/docs/img/docs/cli-layout.svg" alt="Hermes CLI 布局的样式化预览，显示横幅、对话区域和固定的输入提示。" />
<p className="docs-figure-caption">Hermes CLI 的横幅、对话流和固定的输入提示，以稳定的文档图形式呈现，而非易碎的文字图形。</p>

欢迎横幅一目了然地显示您的模型、终端后端、工作目录、可用工具和已安装的技能。

### 状态栏

输入区域上方有一个持久的状态栏，实时更新：

```
 ⚕ claude-sonnet-4-20250514 │ 12.4K/200K │ [██████░░░░] 6% │ $0.06 │ 15m
```

| 元素 | 描述 |
|---------|-------------|
| 模型名称 | 当前模型（超过 26 个字符时截断） |
| Token 数量 | 已使用的上下文 token / 最大上下文窗口 |
| 上下文条 | 可视化填充指示器，带有颜色编码阈值 |
| 成本 | 预估会话成本（对于未知/零价格模型显示 `n/a`） |
| 🗜️ N | **上下文压缩次数** — 运行中的会话已被自动压缩的次数。首次压缩触发后出现。 |
| ▶ N | **活跃的后台任务数** — 当前会话中仍在运行的 `/background` 提示数量。只要至少有一个任务在执行，就会显示。 |
| 持续时间 | 已用会话时间 |
| ⚠ YOLO | **YOLO 模式警告** — 每当 `HERMES_YOLO_MODE` 开启时显示（启动时 `hermes --yolo` 或会话中 `/yolo` 切换）。与横幅行警告同步，确保您不会忘记处于自动批准模式。 |

状态栏会根据终端宽度自适应 — 宽度 ≥ 76 列时显示完整布局，52–75 列时紧凑显示，低于 52 列时显示最小化布局（模型 + 持续时间，以及 YOLO 徽章（如激活））。

**上下文颜色编码：**

| 颜色 | 阈值 | 含义 |
|-------|-----------|---------|
| 绿色 | < 50% | 空间充足 |
| 黄色 | 50–80% | 逐渐填满 |
| 橙色 | 80–95% | 接近限制 |
| 红色 | ≥ 95% | 即将溢出 — 考虑使用 `/compress` |

使用 `/usage` 查看详细分解，包括每个类别的成本（输入与输出 token）。

### 会话恢复显示

当恢复之前的会话时（`hermes -c` 或 `hermes --resume <id>`），横幅和输入提示之间会出现一个“先前对话”面板，显示对话历史的紧凑摘要。详细信息及配置请参阅 [会话 — 恢复时的对话摘要](sessions.md#conversation-recap-on-resume)。

## 快捷键

| 按键 | 操作 |
|-----|--------|
| `Enter` | 发送消息 |
| `Alt+Enter`、`Ctrl+J` 或 `Shift+Enter` | 换行（多行输入）。`Shift+Enter` 需要终端能够区分它与 `Enter` — 见下文。在 Windows 终端上，`Alt+Enter` 会被终端捕获（全屏切换）；请改用 `Ctrl+Enter` 或 `Ctrl+J`。 |
| `Alt+V` | 从剪贴板粘贴图像（终端支持时） |
| `Ctrl+V` | 粘贴文本，并有機會附上剪贴板中的图像 |
| `Ctrl+B` | 开始/停止语音录制（语音模式启用时，`voice.record_key`，默认：`ctrl+b`） |
| `Ctrl+G` | 在 `$EDITOR`（vim/nvim/nano/VS Code 等）中打开当前输入缓冲区。保存并退出后，编辑的文本将作为下一条提示发送 — 适用于长段落的多行提示。 |
| `Ctrl+X Ctrl+E` | Emacs 风格的外部编辑器备用绑定（与 `Ctrl+G` 行为相同）。 |
| `Ctrl+C` | 中断代理（2 秒内双击强制退出） |
| `Ctrl+D` | 退出 |
| `Ctrl+Z` | 将 Hermes 挂起到后台（仅 Unix）。在 shell 中运行 `fg` 恢复。 |
| `Tab` | 接受自动建议（幽灵文本）或自动补全斜杠命令 |

**多行粘贴预览。** 当您粘贴多行文本块时，CLI 会回显一个紧凑的单行预览（`[pasted: 47 lines, 1,842 chars — press Enter to send]`），而不是将整个负载倒入回滚缓冲区。发送的内容仍然是完整的文本；这只是显示层面的优化。

**最终响应的 Markdown 剥离。** CLI 会从*最终*的代理回复中剥离最冗长的 Markdown 围栏和 `**bold**` / `*italic*` 包装，使其呈现为可读的终端散文，而非原始源码。代码块和列表会保留。这不会影响网关平台或工具结果 — 它们会保留 Markdown 以用于原生渲染。

## 斜杠命令

输入 `/` 可查看自动补全下拉列表。Hermes 支持大量 CLI 斜杠命令、动态技能命令和用户定义的快速命令。

常见示例：

| 命令 | 描述 |
|---------|-------------|
| `/help` | 显示命令帮助 |
| `/model` | 显示或更改当前模型 |
| `/tools` | 列出当前可用的工具 |
| `/skills browse` | 浏览技能中心以及官方可选技能 |
| `/background <prompt>` | 在独立的后台会话中运行提示 |
| `/skin` | 显示或切换活动 CLI 皮肤 |
| `/voice on` | 启用 CLI 语音模式（按 `Ctrl+B` 录制） |
| `/voice tts` | 切换 Hermes 回复的语音播放 |
| `/reasoning high` | 增加推理努力程度 |
| `/title My Session` | 为当前会话命名 |
| `/status` | 显示会话信息 — 模型/配置文件/token/持续时间 — 后跟本地**会话摘要**块（最近的轮次数量、使用最多的工具、涉及的文件、最近用户提示 + 助手回复）。纯本地计算；无 LLM 调用。 |
| `/sessions` | 在经典 CLI 中直接打开交互式会话选择器（与 TUI 使用的界面相同）。输入进行过滤，方向键导航，Enter 恢复。 |

有关完整的内置 CLI 和消息列表，请参阅 [斜杠命令参考](../reference/slash-commands.md)。

有关设置、提供商、静音调优以及消息/Discord 语音用法，请参阅 [语音模式](features/voice-mode.md)。

:::tip
命令不区分大小写 — `/HELP` 与 `/help` 效果相同。安装的技能也会自动成为斜杠命令。
:::

## 快速命令

您可以定义自定义命令，这些命令会立即运行 shell 命令，无需调用 LLM。这些命令在 CLI 和消息平台（Telegram、Discord 等）中都可用。

```yaml
# ~/.hermes/config.yaml
quick_commands:
  status:
    type: exec
    command: systemctl status hermes-agent
  gpu:
    type: exec
    command: nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader
  restart:
    type: alias
    target: /gateway restart
```

然后在任何聊天中输入 `/status`、`/gpu` 或 `/restart`。更多示例请参阅 [配置指南](/user-guide/configuration#quick-commands)。

## 启动时预加载技能

如果您已经知道会话中需要哪些技能，可以在启动时传入：

```bash
hermes -s hermes-agent-dev,github-auth
hermes chat -s github-pr-workflow -s github-auth
```

Hermes 会在第一轮对话之前将每个命名技能加载到会话提示中。该标志在交互模式和单次查询模式下都有效。

## 技能斜杠命令

`~/.hermes/skills/` 中的每个已安装技能都会自动注册为斜杠命令。技能名称成为命令：

```
/gif-search funny cats
/axolotl help me fine-tune Llama 3 on my dataset
/github-pr-workflow create a PR for the auth refactor

# 仅技能名称将加载技能，并让代理询问您的需求：
/excalidraw
```

## 人格

设置预定义的人格以改变代理的语气：

```
/personality pirate
/personality kawaii
/personality concise
```

内置人格包括：`helpful`、`concise`、`technical`、`creative`、`teacher`、`kawaii`、`catgirl`、`pirate`、`shakespeare`、`surfer`、`noir`、`uwu`、`philosopher`、`hype`。

您还可以在 `~/.hermes/config.yaml` 中定义自定义人格：

```yaml
personalities:
  helpful: "You are a helpful, friendly AI assistant."
  kawaii: "You are a kawaii assistant! Use cute expressions..."
  pirate: "Arrr! Ye be talkin' to Captain Hermes..."
  # 添加您自己的！
```

## 多行输入

有两种方法可以输入多行消息：

1. **`Alt+Enter`、`Ctrl+J` 或 `Shift+Enter`** — 插入新行
2. **反斜杠续行** — 使用 `\` 结束一行以继续：

```
❯ Write a function that:\
  1. Takes a list of numbers\
  2. Returns the sum
```

:::info
支持粘贴多行文本 — 使用上述任何换行键，或直接粘贴内容。
:::

### Shift+Enter 兼容性

大多数终端默认情况下对 `Enter` 和 `Shift+Enter` 发送相同的字节序列，因此应用程序无法区分它们。Hermes 仅在终端通过 [Kitty 键盘协议](https://sw.kovidgoyal.net/kitty/keyboard-protocol/) 或 xterm 的 `modifyOtherKeys` 模式发送不同的序列时识别 `Shift+Enter`。

| 终端 | 状态 |
|---|---|
| Kitty、foot、WezTerm、Ghostty | 默认启用不同的 `Shift+Enter` |
| iTerm2（较新版本）、Alacritty、VS Code 终端、Warp | 在设置中启用 Kitty 协议后支持 |
| Windows Terminal Preview 1.25+ | 在设置中启用 Kitty 协议后支持 |
| macOS Terminal.app、标准 Windows Terminal（稳定版） | 不支持 — `Shift+Enter` 与 `Enter` 无法区分 |

在终端无法区分它们的情况下，`Alt+Enter` 和 `Ctrl+J` 在任何地方都可用。**在 Windows 终端上，`Alt+Enter` 会被终端捕获（切换全屏）且不会传递给 Hermes — 请使用 `Ctrl+Enter`（作为 `Ctrl+J` 传递）或直接使用 `Ctrl+J` 换行。**

## 中断代理

您可以随时中断代理：

- **在代理工作时输入新消息 + Enter** — 它会中断并处理您的新指示
- **`Ctrl+C`** — 中断当前操作（2 秒内按两次强制退出）
- 正在进行的终端命令会立即终止（先 SIGTERM，1 秒后 SIGKILL）
- 中断期间输入的多个消息会合并为一个提示

### 忙碌输入模式

`display.busy_input_mode` 配置键控制当代理工作时按下 Enter 时的行为：

| 模式 | 行为 |
|------|----------|
| `"interrupt"`（默认） | 您的消息中断当前操作并立即处理 |
| `"queue"` | 您的消息会被静默排队，在代理完成之后作为下一轮发送 |
| `"steer"` | 您的消息通过 `/steer` 注入当前运行，在下一个工具调用后到达代理 — 不中断，不产生新轮次 |

```yaml
# ~/.hermes/config.yaml
display:
  busy_input_mode: "steer"   # 或 "queue" 或 "interrupt"（默认）
```

`"queue"` 模式在您希望准备后续消息而不意外取消正在进行的操作时很有用。`"steer"` 模式在您希望在不中断的情况下中途重定向代理任务时很有用 — 例如，在代理仍在编辑代码时说“实际上，也检查一下测试”。未知值回退到 `"interrupt"`。

`"steer"` 有两个自动回退：如果代理尚未开始，或者附带了图像，则消息会回退到 `"queue"` 行为，以确保不会丢失内容。

您也可以在 CLI 中更改它：

```text
/busy queue
/busy steer
/busy interrupt
/busy status
```

:::tip 首次接触提示
当您在 Hermes 工作时第一次按下 Enter 时，Hermes 会打印一行提醒，解释 `/busy` 选项（`"(tip) Your message interrupted the current run…"`）。每个安装仅触发一次 — `config.yaml` 中 `onboarding.seen.busy_input_prompt` 下的标志会锁定它。删除该键可再次看到提示。
:::

### 挂起到后台

在 Unix 系统上，按 **`Ctrl+Z`** 可将 Hermes 挂起到后台 — 如同任何终端进程。Shell 会打印确认信息：

```
Hermes Agent has been suspended. Run `fg` to bring Hermes Agent back.
```

在 Shell 中输入 `fg` 可完全从离开的地方恢复会话。Windows 上不支持此功能。

## 工具进度显示

CLI 在代理工作时显示动画反馈：

**思考动画**（API 调用期间）：
```
  ◜ (｡•́︿•̀｡) pondering... (1.2s)
  ◠ (⊙_⊙) contemplating... (2.4s)
  ✧٩(ˊᗜˋ*)و✧ got it! (3.1s)
```

**工具执行流：**
```
  ┊ 💻 terminal `ls -la` (0.3s)
  ┊ 🔍 web_search (1.2s)
  ┊ 📄 web_extract (2.1s)
```

使用 `/verbose` 循环切换显示模式：`off → new → all → verbose`。此命令也可以为消息平台启用 — 请参阅 [配置](/user-guide/configuration#display-settings)。

### 工具预览长度

`display.tool_preview_length` 配置键控制工具调用预览行中显示的最大字符数（例如文件路径、终端命令）。默认值为 `0`，表示无限制 — 显示完整路径和命令。

```yaml
# ~/.hermes/config.yaml
display:
  tool_preview_length: 80   # 将工具预览截断至 80 个字符（0 = 无限制）
```

这在窄终端或工具参数包含非常长的文件路径时很有用。

## 会话管理

### 恢复会话

当退出 CLI 会话时，会打印一条恢复命令：

```
Resume this session with:
  hermes --resume 20260225_143052_a1b2c3

Session:        20260225_143052_a1b2c3
Duration:       12m 34s
Messages:       28 (5 user, 18 tool calls)
```

恢复选项：

```bash
hermes --continue                          # 恢复最近的 CLI 会话
hermes -c                                  # 简短形式
hermes -c "my project"                     # 恢复一个命名会话（同源最新）
hermes --resume 20260225_143052_a1b2c3     # 按 ID 恢复特定会话
hermes --resume "refactoring auth"         # 按标题恢复
hermes -r 20260225_143052_a1b2c3           # 简短形式
```

恢复会从 SQLite 恢复完整的对话历史。代理会看到所有先前的消息、工具调用和响应 — 就像您从未离开过一样。

在聊天中使用 `/title My Session Name` 为当前会话命名，或在命令行中使用 `hermes sessions rename <id> <title>`。使用 `hermes sessions list` 浏览过去的会话。

### 会话存储

CLI 会话存储在 `~/.hermes/state.db` 的 Hermes SQLite 状态数据库中。数据库保存：

- 会话元数据（ID、标题、时间戳、token 计数器）
- 消息历史
- 跨压缩/恢复会话的谱系
- 由 `session_search` 使用的全文搜索索引

某些消息适配器也会在数据库旁保留每个平台的消息记录文件，但 CLI 本身从 SQLite 会话存储恢复。

### 上下文压缩

长对话会在接近上下文限制时自动进行摘要：

```yaml
# 在 ~/.hermes/config.yaml 中
compression:
  enabled: true
  threshold: 0.50    # 默认在上下文限制的 50% 时压缩

# 摘要模型在 auxiliary 下配置：
auxiliary:
  compression:
    model: ""  # 留空以使用主聊天模型（默认）。或指定一个便宜快速的模型，例如 "google/gemini-3-flash-preview"。
```

当压缩触发时，中间轮次会被摘要，而前 3 轮和后 20 轮始终保留。

## 后台会话

在独立的后台会话中运行提示，同时继续使用 CLI 进行其他工作：

```
/background Analyze the logs in /var/log and summarize any errors from today
```

Hermes 立即确认任务并将提示交还给您：

```
🔄 Background task #1 started: "Analyze the logs in /var/log and summarize..."
   Task ID: bg_143022_a1b2c3
```

### 工作原理

每个 `/background` 提示会在守护线程中生成一个**完全独立的代理会话**：

- **隔离对话** — 后台代理对当前会话的历史一无所知。它仅接收您提供的提示。
- **相同配置** — 后台代理继承当前会话的模型、提供商、工具集、推理设置和回退模型。
- **非阻塞** — 您的前台会话保持完全交互。您可以聊天、运行命令，甚至启动更多后台任务。
- **多个任务** — 您可以同时运行多个后台任务。每个任务都有一个编号 ID。

### 结果

后台任务完成时，结果会以面板形式显示在终端中：

```
╭─ ⚕ Hermes (background #1) ──────────────────────────────────╮
│ Found 3 errors in syslog from today:                         │
│ 1. OOM killer invoked at 03:22 — killed process nginx        │
│ 2. Disk I/O error on /dev/sda1 at 07:15                      │
│ 3. Failed SSH login attempts from 192.168.1.50 at 14:30      │
╰──────────────────────────────────────────────────────────────╯
```

如果任务失败，您将看到错误通知。如果配置中启用了 `display.bell_on_complete`，任务完成时终端会响铃。

### 使用场景

- **长时间研究** — “/background research the latest developments in quantum error correction” 同时编写代码
- **文件处理** — “/background analyze all Python files in this repo and list any security issues” 同时继续对话
- **并行调查** — 启动多个后台任务同时探索不同角度

:::info
后台会话不会出现在您的主对话历史中。它们是独立的会话，具有自己的任务 ID（例如 `bg_143022_a1b2c3`）。
:::

## 安静模式

默认情况下，CLI 以安静模式运行，该模式：
- 抑制工具的详细日志记录
- 启用萌风格动画反馈
- 保持输出干净、用户友好

如需调试输出：
```bash
hermes chat --verbose
```