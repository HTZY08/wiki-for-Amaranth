---
title: Tui
---

sidebar_position: 2
title: "TUI（终端用户界面）"
description: "启动 Hermes 的现代终端用户界面——支持鼠标操作、丰富覆盖层和非阻塞输入。"
---

--- body ---
# TUI（终端用户界面）

TUI 是 Hermes 的现代前端——一种终端用户界面，底层使用与[经典 CLI（命令行界面）](cli.md)相同的 Python 运行时。相同的代理（Agent）、相同的会话（Session）、相同的斜杠命令；但提供了更简洁、响应更快的交互界面。

这是推荐以交互方式运行 Hermes 的方式。

## 启动

```bash
# 启动 TUI
hermes --tui

# 恢复最近的 TUI 会话（如果无则回退到最近的经典会话）
hermes --tui -c
hermes --tui --continue

# 按 ID 或标题恢复特定会话
hermes --tui -r 20260409_000000_aa11bb
hermes --tui --resume "my t0p session"

# 直接运行源码——跳过预构建步骤（适用于 TUI 贡献者）
hermes --tui --dev
```

你也可以通过环境变量启用：

```bash
export HERMES_TUI=1
hermes          # 现在会使用 TUI
hermes chat     # 同样
```

或者将其设置为 `~/.hermes/config.yaml` 中的持久化默认值：

```yaml
display:
  interface: tui   # "cli"（默认）或 "tui"
```

当 `display.interface: tui` 时，仅运行 `hermes`（及 `hermes chat`）会启动 TUI。显式标志始终优先——运行 `hermes --cli` 可单次回退到经典 REPL（读取-求值-打印循环）；或者当配置默认值为 `cli` 时，使用 `hermes --tui` / `HERMES_TUI=1` 强制启用 TUI。

经典 CLI 仍是默认发布的版本。任何在 [CLI 接口](cli.md) 中记录的斜杠命令、快捷命令、技能（Skill）预加载、人格（Personality）、多行输入、中断等功能，在 TUI 中均以相同方式工作。

## 为何选择 TUI

- **即时首帧**——应用加载完成前即可显示标题横幅，因此 Hermes 启动时终端绝不会卡住。
- **非阻塞输入**——在会话就绪前即可输入并排队消息。当代理上线时，你的第一个提示将立即发送。
- **丰富覆盖层**——模型选择器、会话选择器、批准提示和澄清提示均以模态面板（Modal Panel）形式呈现，而非内联流。
- **实时会话面板**——工具和技能在初始化时逐步填充显示。
- **支持鼠标的选择**——拖动以统一背景色高亮，而非 SGR 反色。使用终端正常的复制手势进行复制。
- **备用屏幕渲染**——差异更新意味着流式输出时无闪烁，退出后无滚动历史混乱。
- **编辑器辅助功能**：内联粘贴折叠长代码段、`Cmd+V` / `Ctrl+V` 粘贴文本（含剪贴板图片兜底）、括号粘贴安全以及图片/文件路径附件标准化。

相同的[皮肤（Skin）](features/skins.md)和[人格（Personality）](features/personality.md)均适用。会话中可用 `/skin ares`、`/personality pirate` 切换，界面将实时重绘。查看[皮肤与主题](features/skins.md)获取完整的可自定义键列表，以及哪些适用于经典 CLI 与 TUI——TUI 支持横幅调色板（banner palette）、UI 颜色、提示符字形/颜色、会话显示、补全菜单、选择背景色、工具前缀（tool_prefix）和帮助头部（help_header）。

### 可折叠的横幅分区

TUI 启动横幅将运行时信息分为四个可折叠分区，每个分区标题旁带有 `▸` / `▾` 箭头：

| 分区 | 默认状态 |
|---------|---------------|
| 工具（Tools） | 展开 |
| 技能（Skills） | 折叠 |
| 系统提示（System Prompt） | 折叠 |
| MCP 服务器（MCP Servers） | 折叠 |

点击分区标题（或其箭头）任意位置可切换其状态。工具列表默认展开，因为它是会话启动时最常查看的分区；技能、系统提示和 MCP 服务器默认折叠，这样即使安装了数十个技能或连接了许多 MCP 服务器，横幅也能保持紧凑。状态仅针对当前横幅实例有效，因此下次启动时将重置为默认值。

## 要求

- **Node.js** ≥ 20——TUI 作为由 Python CLI 启动的子进程运行。`hermes doctor` 会检查此项。
- **TTY（终端设备）**——与经典 CLI 类似，当 stdin 被重定向或在非交互环境中运行时，将回退到单查询模式。

首次启动时，Hermes 会将 TUI 的 Node 依赖项安装到 `ui-tui/node_modules`（一次性，耗时几秒）。后续启动很快。如果你拉取新的 Hermes 版本，当源码比 dist 更新时，TUI 包将自动重建。

### 外部预构建

携带预构建包的分发版本（如 Nix、系统包）可将 Hermes 指向该位置：

```bash
export HERMES_TUI_DIR=/path/to/prebuilt/ui-tui
hermes --tui
```

该目录必须包含 `dist/entry.js`。

## 按键绑定

按键绑定与[经典 CLI](cli.md#keybindings) 完全一致。唯一的行为差异：

- **鼠标拖动**：使用统一的选择背景色高亮文本。
- **`Cmd+V` / `Ctrl+V`**：首先尝试普通文本粘贴，然后回退到 OSC52/原生剪贴板读取，最后当剪贴板或粘贴内容解析为图片时进行图片附件操作。
- **`/terminal-setup`**：安装本地 VS Code / Cursor / Windsurf 终端绑定，以获得更好的 `Cmd+Enter` 和撤销/重做在 macOS 上的一致性。
- **斜杠命令自动补全**：以浮动画板形式打开，附带描述信息，而非内联下拉列表。
- **`Ctrl+X`**：打开实时会话切换器。当高亮的是排队消息（在代理仍在运行时发送）时，它仍然会删除该排队消息。**`Esc`** 取消编辑并取消高亮，但不删除。
- **`Ctrl+G` / `Ctrl+X Ctrl+E`**：在 `$EDITOR` 中打开当前输入缓冲区，用于多行/长提示编辑；保存并退出将内容作为提示发送。

## 斜杠命令

所有斜杠命令均保持不变。部分命令为 TUI 特有——它们产生更丰富的输出，或以覆盖层而非内联面板形式呈现：

| 命令 | TUI 行为 |
|---------|--------------|
| `/help` | 覆盖层显示分类命令，可用方向键导航 |
| `/sessions`（别名 `/switch`） | 实时会话切换器——列出当前打开的 TUI 会话，可在其间切换、关闭或启动新会话 |
| `/model` | 按供应商分组的模态模型选择器，附带成本提示 |
| `/skin` | 实时预览——浏览时主题更改即应用 |
| `/details` | 切换详细工具调用信息（全局或按分区） |
| `/usage` | 丰富的令牌/成本/上下文面板 |
| `/agents`（别名 `/tasks`） | 可观测性覆盖层——实时子代理树，包含杀死/暂停控制、每个分支的成本/令牌/文件汇总、逐轮历史 |
| `/reload` | 重新读取 `~/.hermes/.env` 到正在运行的 TUI 进程，以便新添加的 API 密钥无需重启即可生效 |
| `/mouse [on\|off\|toggle\|wheel\|buttons\|all]` | 运行时选择鼠标跟踪预设（也会持久化到 `config.yaml` 的 `display.mouse_tracking` 中）。`wheel`（1000+1006）保留滚轮滚动功能，但关闭悬停事件（避免 tmux 在提示行上频繁显示“No image in clipboard”）；`buttons` 增加拖拽选择功能；`all` 为默认值，包含悬停驱动的 UI。 |

其他所有斜杠命令（包括已安装的技能、快捷命令和人格切换）均与经典 CLI 相同。参见[斜杠命令参考](../reference/slash-commands.md)。

## 实时会话切换器

当你想用一个终端作为多个 TUI 会话的分发器时，可使用实时会话切换器。它仅列出当前在此 TUI 进程中活跃的会话；已关闭的会话将保存为记录，仍可通过 `/resume` 或 `hermes --tui --resume <id-or-title>` 重新打开。

通过以下任一方式打开：

- 在 TUI 中按 `Ctrl+X`。
- 输入 `/sessions` 或 `/switch`。
- 输入 `/sessions new` 立即创建一个新的活跃会话。
- 点击状态行中的 `N live sessions` 计数。

<img alt="Hermes TUI 会话编排器，显示一个活跃会话和一行 +new" src="/img/docs/tui-session-orchestrator/session-orchestrator.png" />

<video controls muted loop playsInline src="/img/docs/tui-session-orchestrator/session-orchestrator-demo.mp4" title="Hermes TUI 会话编排器演示" />

在切换器内：

- `↑` / `↓` 移动选择；鼠标点击也可选择行。
- `Enter` 切换到选中的活跃会话。
- `Ctrl+D` 关闭选中的活跃会话。
- `Ctrl+N` 启动一个新的空白活跃会话。
- `Ctrl+R` 刷新活跃会话列表。
- `Esc` 关闭切换器。
- 选择 `+new`，输入提示，按 `Enter` 即可分发一个新的活跃会话。如果希望仅为该新会话选择模型，可先按 `Tab`。

## LaTeX 数学渲染

TUI 的 Markdown 管道可内联渲染 LaTeX 数学公式：`$E = mc^2$` 和 `$$\frac{a}{b}$$` 会渲染为 Unicode 格式的数学表达式，而非原始 TeX 源码。支持内联和块级数学公式；不支持语法会回退显示字面 TeX，并包裹在代码 span 中以便复制。

此功能始终开启——无需配置。经典 CLI 保留原始 TeX。

## 浅色终端检测

TUI 自动检测浅色终端并相应切换到浅色主题。检测分三层：

1. `HERMES_TUI_THEME` 环境变量——最高优先级。取值：`light`、`dark` 或原始 6 字符背景十六进制值（例如 `ffffff`、`1a1a2e`）。
2. `COLORFGBG` 环境变量——xterm 派生终端使用的经典“我的背景色是什么？”提示。
3. 通过 OSC 11 进行终端背景探测——适用于现代终端（Ghostty、Warp、iTerm2、WezTerm、Kitty）未设置 `COLORFGBG` 的情况。

如果你想永久使用浅色主题，无论终端如何：

```bash
export HERMES_TUI_THEME=light
```

## 忙碌指示器样式

状态栏的忙碌指示器是可插拔的——默认在代理工作期间每 2.5 秒轮换 Hermes 的可爱脸谱调色板。可通过配置或 `/indicator` 斜杠命令选择不同样式：

```yaml
display:
  tui_status_indicator: kaomoji   # kaomoji | emoji | unicode | ascii
```

或在会话中：`/indicator emoji`（等等）。每种样式都附带配对的字形宽度，以确保状态栏其余部分在轮换时不抖动。

## 自动恢复

默认情况下，`hermes --tui` 每次启动都会创建一个新会话。如果需要自动重新连接到最近的 TUI 会话（当终端或 SSH 连接意外断开时很有用），可选择启用：

```bash
export HERMES_TUI_RESUME=1          # 最近的 TUI 会话
# 或：
export HERMES_TUI_RESUME=<session-id>   # 特定会话
```

取消设置该变量或显式传递 `--resume <id>` 可在每次启动时覆盖。

## 状态行

TUI 的状态行实时跟踪代理状态：

| 状态 | 含义 |
|--------|---------|
| `starting agent…` | 会话 ID 已激活；工具和技能仍在加载中。你可以输入——消息会排队，准备就绪时发送。 |
| `ready` | 代理空闲，等待输入。 |
| `thinking…` / `running…` | 代理正在推理或运行工具。 |
| `interrupted` | 当前轮次已取消；按 Enter 重新发送。 |
| `forging session…` / `resuming…` | 初始连接或 `--resume` 握手。 |

每个皮肤的状态栏颜色和阈值与经典 CLI 共享——参见[皮肤](features/skins.md)了解自定义。

状态行还显示：

- **包含 Git 分支的工作目录**——`~/projects/hermes-agent (docs/two-week-gap-sweep)`。当你在侧边终端执行 `git checkout` 时，分支后缀会更新（基于 mtime 缓存），因此 TUI 反映的是实际活跃分支，而非启动时的分支。
- **每个提示的已用时间**——`⏱ 12s/3m 45s` 在轮次进行中（实时更新），轮次完成后冻结为 `⏲ 32s / 3m 45s`。第一个数字是自上次用户消息以来的时间；第二个是会话总时长。每次新提示时重置。
- **`🗜️ N`**——当前运行会话自动压缩的次数。首次压缩触发后出现。
- **`▶ N`**——当前会话中正在运行的 `/background` 任务数。只要至少有一个任务在运行就会显示。
- **`⚠ YOLO`**——YOLO 模式启用时的可见警告（`hermes --yolo`、`/yolo` 或 `HERMES_YOLO_MODE=1`）。启动横幅中也显示相同徽章，确保你不会在不知情的情况下启动自动批准会话。

## 配置

TUI 遵守所有标准的 Hermes 配置：`~/.hermes/config.yaml`、配置文件（Profiles）、人格（Personalities）、皮肤（Skins）、快捷命令（Quick Commands）、凭据池（Credential Pools）、记忆提供者（Memory Providers）、工具/技能启用。没有 TUI 特定的配置文件。

以下键专门调整 TUI 界面：

```yaml
display:
  skin: default              # 任何内置或自定义皮肤
  personality: helpful
  details_mode: collapsed    # hidden | collapsed | expanded — 全局手风琴默认值
  sections:                  # 可选：按分区覆盖（任意子集）
    thinking: expanded       # 始终展开
    tools: expanded          # 始终展开
    activity: collapsed      # 重新启用活动面板（默认隐藏）
  mouse_tracking: all        # off | wheel | buttons | all（或 true/false 以向后兼容）。
                             #   wheel   — 1000+1006（滚动+单击；无拖拽、无悬停）
                             #              — 推荐在 tmux 内使用，以避免悬停事件引起的提示行 "No image in clipboard" 乱刷
                             #   buttons — 增加 1002 用于终端端拖拽选择
                             #   all     — 增加 1003 用于悬停（滚动条悬停分页、链接鼠标进入等）
```

运行时切换：

- `/details [hidden|collapsed|expanded|cycle]` — 设置全局模式
- `/details <section> [hidden|collapsed|expanded|reset]` — 覆盖特定分区
  （分区：`thinking`、`tools`、`subagents`、`activity`）

**默认可见性**

TUI 为每个分区提供了有意见的默认值，使轮次以直播记录而非一堵箭头墙的形式呈现：

- `thinking` — **展开**。推理过程随着模型输出而内联显示。
- `tools` — **展开**。工具调用及其结果以展开形式渲染。
- `subagents` — 回退到全局 `details_mode`（默认折叠在箭头下——除非实际发生委派，否则保持静默）。
- `activity` — **隐藏**。环境元信息（网关提示、终端一致性提示、后台通知）对于日常使用来说通常是噪音。工具失败仍会在失败的工具行内渲染；环境错误/警告会通过浮动警报后备显示（当所有面板都隐藏时）。

按分区覆盖优先于分区默认值和全局 `details_mode`。要重新调整布局：

- `display.sections.thinking: collapsed` — 将推理放回箭头下
- `display.sections.tools: collapsed` — 将工具调用放回箭头下
- `display.sections.activity: collapsed` — 重新启用活动面板
- 运行时使用 `/details <section> <mode>`

任何在 `display.sections` 中显式设置的值都将覆盖默认值，因此现有配置可以无更改继续使用。

## 会话

TUI 和经典 CLI 共享会话——两者都写入同一个 `~/.hermes/state.db`。你可以在一个界面中启动会话，在另一个界面中恢复。会话选择器会显示来自两者的会话，并带有来源标签。

关于会话的生命周期、搜索、压缩和导出，请参见[会话](sessions.md)。

## TUI 如何与网关通信

默认情况下，TUI 会生成自己的进程内网关，因此每个 TUI 实例都是自包含的——无需配置。

你可能会在代码库或日志中看到 `HERMES_TUI_GATEWAY_URL` 环境变量。这是**Web 仪表板的内部连接细节**，并非用户可见的远程附加开关。当你打开仪表板的“聊天”选项卡（`hermes dashboard` → `/chat`）时，仪表板的 Web 服务器会生成一个嵌入式 TUI 子进程，并注入 `HERMES_TUI_GATEWAY_URL`，以便该子进程通过 loopback WebSocket（`/api/ws`）连接到仪表板自身的进程内 `tui_gateway`。`/api/ws` 端点仅存在于仪表板服务器内部（`hermes_cli/web_server.py`），并绑定到该进程的生命周期和认证。

没有通用的“将任意 TUI 指向任意独立网关端口”模式。特别是，兼容 OpenAI API 的服务器（`hermes gateway` / `api_server` 平台）**不**提供 `/api/ws`——它用于模型后端接口（`/v1/chat/completions`、`/v1/models` 等），并且故意不暴露 TUI 的 JSON-RPC 控制通道。将 `HERMES_TUI_GATEWAY_URL` 设置为该端口将会返回 404。

如果你希望多个界面共享同一组会话，请使用共享的 `~/.hermes/state.db`（参见[会话](sessions.md)）或 Web 仪表板的嵌入式聊天（参见[Web 仪表板](features/web-dashboard.md#chat)）——而不是手动设置的网关 URL。

## 回退到经典 CLI

运行 `hermes`（不带 `--tui`）默认使用经典 CLI。若要让某台机器优先使用 TUI，请在 `~/.hermes/config.yaml` 中设置 `display.interface: tui`（持久化）或在 shell 配置文件中设置 `HERMES_TUI=1`（按 shell）。要恢复，请设置 `interface: cli` / 取消环境变量，或运行 `hermes --cli` 进行单次切换。

如果 TUI 启动失败（无 Node、缺少包、TTY 问题），Hermes 会打印诊断信息并回退——不会让你束手无策。

## 参见

- [CLI 接口](cli.md)——完整的斜杠命令和按键绑定参考（共享）
- [会话](sessions.md)——恢复、分支和历史
- [皮肤与主题](features/skins.md)——为主题横幅、状态栏和覆盖层设置主题
- [语音模式](features/voice-mode.md)——两个界面均适用
- [配置](configuration.md)——所有配置键