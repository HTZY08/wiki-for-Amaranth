---
title: Web Dashboard
---

sidebar_position: 15
title: "Web Dashboard"
description: "基于浏览器的管理面板，用于管理配置、API 密钥、MCP 服务器、消息配对、Webhooks、网关、内存、凭证、会话、日志、分析、定时任务和技能"
---

--- body ---
# Web 仪表盘 (Web Dashboard)

Web 仪表盘是一个基于浏览器的 UI，用于管理您的 Hermes Agent 安装。您无需编辑 YAML 文件或运行 CLI 命令，而是可以通过一个简洁的 Web 界面来配置设置、管理 API 密钥和监控会话。

:::tip
托管模式认证使用 Nous Portal OAuth；如果您还希望仪表盘与真实后端通信，`hermes setup --portal` 也会连接模型和工具网关。请参阅 [Nous Portal](/integrations/nous-portal)。
:::

## 快速入门

```bash
hermes dashboard
```

这将启动一个本地 Web 服务器，并在浏览器中打开 `http://127.0.0.1:9119`。仪表盘完全运行在您的机器上——没有数据离开 localhost。

### 选项

| 标志 | 默认值 | 描述 |
|------|---------|-------------|
| `--port` | `9119` | Web 服务器运行的端口 |
| `--host` | `127.0.0.1` | 绑定地址 |
| `--no-open` | — | 不自动打开浏览器 |
| `--insecure` | 关闭 | 允许绑定到非 localhost 主机 (**危险**——会在网络上暴露 API 密钥；请配合防火墙和强认证使用) |
| `--isolated` | 关闭 | 当从命名配置文件（`worker dashboard`）启动时，运行专用按配置文件服务器，而不是路由到机器仪表盘 |

```bash
# 自定义端口
hermes dashboard --port 8080

# 绑定到所有接口（在共享网络上请谨慎使用）
hermes dashboard --host 0.0.0.0

# 启动时不打开浏览器
hermes dashboard --no-open
```

## 管理多个配置文件

仪表盘是一个**机器级别**的管理界面：一个服务器管理机器上的每个[配置文件](../profiles.md)。侧边栏中的配置文件切换器（当存在多个配置文件时可见）决定管理页面读写哪个配置文件——配置、API 密钥、技能、MCP、模型和聊天选项卡都遵循它。当选择了仪表盘自身配置文件以外的配置文件时，会显示一个琥珀色横幅，指明被管理的配置文件，从而确保写入目标明确。

选择信息存在于 URL 中（`?profile=<name>`），因此像 `http://127.0.0.1:9119/skills?profile=worker` 这样的深度链接会在页面加载时预先选中切换器，并且在刷新后依然保持。

从配置文件别名启动仪表盘会路由到机器仪表盘，而不是启动第二个服务器：

```bash
worker dashboard
# → 如果已运行：在浏览器中打开，URL 为 ?profile=worker
# → 如果未运行：启动机器仪表盘，并预先选中 "worker"
```

传递 `--isolated` 标志可退出此行为，并运行一个仅限该配置文件的专用服务器（即统一前的行为——如果您有意通过不同认证暴露不同配置文件的仪表盘，则很有用）。

**聊天**选项卡也遵循切换器的选择：作用域内的聊天会使用所选配置文件的 `HERMES_HOME` 来生成其 PTY 子进程，因此对话将使用该配置文件的模型、技能、内存和会话历史。切换配置文件会启动一个新的终端会话。

哪些内容是按配置文件管理且**不被**切换器吸收的：网关进程（通过 `hermes -p <name> gateway …` 管理）、每个配置文件的会话数据库以及 cron 调度器（Cron 页面已经使用自己的过滤器跨配置文件汇总）。

## 前提条件

默认的 `hermes-agent` 安装不包含 HTTP 栈或 PTY 辅助程序——这些都是可选的额外组件。**Web 仪表盘**需要 FastAPI 和 Uvicorn（`web` 额外组件）。**聊天**选项卡还需要 `ptyprocess`，以便在伪终端后生成嵌入式 TUI（POSIX 上的 `pty` 额外组件）。同时安装两者：

```bash
cd ~/.hermes/hermes-agent && uv pip install -e ".[web,pty]"
```

`web` 额外组件拉取 FastAPI/Uvicorn；`pty` 拉取 `ptyprocess`（POSIX）或 `pywinpty`（原生 Windows——注意嵌入式 TUI 本身仍然需要 WSL）。`cd ~/.hermes/hermes-agent && uv pip install -e ".[all]"` 包含这两个额外组件，如果您也需要消息/语音等功能，这是最简单的方式。

当您在没有依赖项的情况下运行 `hermes dashboard` 时，它会告诉您需要安装什么。如果前端尚未构建且 `npm` 可用，它会在首次启动时自动构建。

聊天选项卡是每次 `hermes dashboard` 启动的一部分——嵌入式浏览器聊天面板（通过 PTY/WebSocket 运行 TUI）始终可用，无需额外的标志。

## 页面

### 状态

着陆页显示您的安装情况的实时概览：

- **Agent 版本**和发布日期
- **网关状态**——运行中/已停止，PID，连接的平台及其状态
- **活动会话**——过去 5 分钟内活跃的会话数
- **近期会话**——最近 20 个会话的列表，包含模型、消息数、令牌使用量以及对话的预览

状态页面每 5 秒自动刷新一次。

### 聊天

**聊天**选项卡将完整的 Hermes TUI（与您从 `hermes --tui` 获得的界面相同）直接嵌入到浏览器中。您在终端 TUI 中可以做的所有事情——斜杠命令、模型选择器、工具调用卡片、Markdown 流式输出、clarify/sudo/approval 提示、皮肤主题——在这里都完全相同，因为仪表盘正在运行真正的 TUI 二进制文件，并通过 [xterm.js](https://xtermjs.org/) 及其 WebGL 渲染器渲染其 ANSI 输出，以实现像素完美的单元格布局。

**工作原理：**

- `/api/pty` 打开一个 WebSocket，使用仪表盘的会话令牌进行认证
- 服务器在 POSIX 伪终端后生成 `hermes --tui`
- 按键事件发送到 PTY；ANSI 输出流式传输回浏览器
- xterm.js 的 WebGL 渲染器将每个单元格绘制到整数像素网格上；鼠标跟踪（SGR 1006）、宽字符（Unicode 11）和制表符绘制字形都原生渲染
- 调整浏览器窗口大小会通过 `@xterm/addon-fit` 附加组件调整 TUI 大小

**恢复现有会话：** 从**会话**选项卡中，单击任何会话旁边的播放图标（▶）。这将跳转到 `/chat?resume=<id>`，并使用 `--resume` 启动 TUI，加载完整历史记录。

**会话切换器（右侧栏）：** 聊天选项卡在终端旁边带有一个自己的 ChatGPT 风格对话列表，位于右侧的窄栏中，因此您无需离开页面即可切换对话。该栏将模型选择器放在顶部，会话列表直接放在其下方；终端占据大部分屏幕。列表显示活动配置文件的最近会话——标题（回退到消息预览）、相对上次活动时间、消息数以及非 CLI 会话的源渠道。单击任何行即可就地恢复它（终端会使用该对话的历史记录重新生成）；活动会话会高亮显示。**新建聊天**启动一个新会话，刷新控件重新拉取列表。该栏是只读的，仅用于切换——删除、重命名、导出和批量清理仍位于**会话**选项卡中。在窄屏幕上，它会折叠成一个滑出面板。

**前提条件：**

- Node.js（与 `hermes --tui` 相同的要求；TUI 捆绑包在首次启动时构建）
- `ptyprocess`——由 `pty` 额外组件安装（`cd ~/.hermes/hermes-agent && uv pip install -e ".[web,pty]"`，或者 `[all]` 涵盖两者）
- POSIX 内核（Linux、macOS 或 WSL2）。`/chat` 终端面板特别需要 POSIX PTY——原生 Windows Python 没有等效项，因此在原生 Windows 安装上，仪表盘的其余部分（会话、任务、指标、配置编辑器）可以工作，但 `/chat` 选项卡会显示一个横幅，告诉您为此功能使用 WSL2。

关闭浏览器选项卡后，服务器上的 PTY 会被干净地回收。重新打开会生成一个新的会话。

要将 [Hermes Desktop](#connecting-hermes-desktop-to-a-remote-backend) 指向另一台机器上运行的仪表盘，而不是其自己的捆绑后端，请参阅下面的远程后端部分。

### 将 Hermes Desktop 连接到远程后端

Hermes Desktop 通常启动自己的本地后端，但它也可以通过**设置 → 网关 → 远程网关**连接到远程机器（VM、家庭实验室机器等）上运行的仪表盘。这是 "Desktop 说后端已就绪但聊天始终无法工作" 报告的最常见原因，因为 Desktop 的就绪检查验证的内容少于实时聊天连接实际需要的内容。

:::info 前提条件：远程主机上必须运行 `hermes dashboard`
Desktop 连接到的 "远程后端" **就是**在远程机器上运行的 `hermes dashboard` 进程——本文档介绍的同一个服务器。在任何后续步骤之前，它必须已启动并可访问；Desktop 会连接到它，而不是为您启动它。请将其保持在 `systemd`/`tmux` 等环境下运行，以便在注销和重启后仍然存在。**网关**（Telegram/Discord/Slack 等）是一个*独立*的长期运行进程——如果您依赖消息渠道，请独立启动它；桌面应用连接的不是它。
:::

Desktop 的 "远程后端已就绪" 探测仅访问 `GET /api/status`，这是一个公共端点——只要主机上运行*任何*仪表盘，它就会响应。实时聊天连接是到 `/api/ws`（和 `/api/pty`）的一个**独立** WebSocket，该套接字受到状态探测从未触及的两个额外检查的限制：

1. **您必须通过身份验证。** 当仪表盘绑定到非回环地址时，它会启用其认证门。使用用户名和密码保护它（捆绑的 [用户名/密码提供程序](#usernamepassword-provider-no-oauth-idp)）；Desktop 登录一次，并通过一次性票据重用生成的会话用于 WebSocket。如果没有配置提供程序，非回环仪表盘**在启动时失败关闭**。
2. **绑定主机必须允许客户端并匹配 Host 头。** 回环绑定（`127.0.0.1`）仅接受回环客户端，因此无论凭证如何，远程机器都会在套接字层被拒绝。绑定到非回环地址（`--host 0.0.0.0`）以便对等 IP 守卫允许远程客户端通过。您在 Desktop 中输入的远程 URL 必须通过仪表盘绑定的同一主机访问它——DNS 重新绑定守卫要求 Host 头匹配。

#### 远程仪表盘设置

设置用户名和密码，然后运行绑定到可达地址的仪表盘。对于 `systemd` 服务：

```ini
[Service]
EnvironmentFile=%h/.hermes/.env
ExecStart=/path/to/venv/bin/python -m hermes_cli.main dashboard \
    --host 0.0.0.0 --port 9119 --no-open
```

其中 `~/.hermes/.env` 包含：

```bash
HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin
HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=choose-a-strong-password
HERMES_DASHBOARD_BASIC_AUTH_SECRET=<32+ random bytes; openssl rand -base64 32>
```

然后在 Desktop 中输入**远程 URL**（例如 `http://VM_IP:9119`）并使用该用户名和密码**登录**。有关完整的配置表面，请参阅 [用户名/密码提供程序](#usernamepassword-provider-no-oauth-idp) 部分。

:::tip 在重试 Desktop 之前验证门已开启
从任何机器上检查仪表盘是否宣告了用户名/密码提供程序：

```bash
curl -s http://VM_IP:9119/api/status | jq '.auth_required, .auth_providers'
# true
# ["basic"]
```

- `auth_required: true` 且提供程序列表中包含 `"basic"` → Desktop 的**登录**流程将正常工作。
- `auth_required: false` → 绑定是回环，或者门未启用。请绑定到非回环地址。
- `auth_required: true` 但没有 `"basic"` 提供程序 → 用户名/密码环境变量未加载。请先修复这些问题。
:::

如果 `/api/status` 显示门已开启且包含 `"basic"` 提供程序，但 Desktop *仍然*在登录后无法连接，则问题超出了基本设置——获取一个新的 `desktop.log`（设置 → 网关 → 打开日志）以及相同重试窗口内的仪表盘日志，并查找 `/api/ws` 关闭代码（4403 = 聊天 WS 被请求守卫拒绝，例如 Host/对等端不匹配；4401 = WS 票据未通过认证）。

### 配置

用于编辑 `config.yaml` 的基于表单的编辑器。所有 150+ 个配置字段都从 `DEFAULT_CONFIG` 自动发现，并按标签页分类组织：

![配置管理页面——左侧是部分筛选器，右侧是自动发现的字段](/img/dashboard/admin-config.png)


- **模型** — 默认模型、提供程序、基础 URL、推理设置
- **终端** — 后端（本地/容器/SSH/Modal）、超时、shell 偏好
- **显示** — 皮肤、工具进度、恢复显示、微调器设置
- **Agent** — 最大迭代次数、网关超时、服务层级
- **委托** — 子代理限制、推理努力
- **内存** — 提供程序选择、上下文注入设置
- **审批** — 危险命令审批模式（ask/yolo/deny）
- 以及更多——config.yaml 的每个部分都有对应的表单字段

具有已知有效值的字段（终端后端、皮肤、审批模式等）呈现为下拉菜单。布尔值呈现为开关。其他所有内容都是文本输入。

**操作：**

- **保存** — 立即将更改写入 `config.yaml`
- **重置为默认值** — 将所有字段恢复为其默认值（直到单击保存才会保存）
- **导出** — 将当前配置下载为 JSON
- **导入** — 上传 JSON 配置文件以替换当前值

:::tip
配置更改将在下一次 Agent 会话或网关重启时生效。Web 仪表盘编辑的是同一个 `config.yaml` 文件，`hermes config set` 和网关也读取该文件。
:::

### API 密钥

管理存储 API 密钥和凭证的 `.env` 文件。密钥按类别分组：

- **LLM 提供程序** — OpenRouter、Anthropic、OpenAI、DeepSeek 等
- **工具 API 密钥** — Browserbase、Firecrawl、Tavily、ElevenLabs 等
- **消息平台** — Telegram、Discord、Slack 机器人令牌等
- **Agent 设置** — 非秘密的环境变量，如 `API_SERVER_ENABLED`

每个密钥显示：
- 是否已设置（带有值的脱敏预览）
- 用途描述
- 指向提供程序注册/密钥页面的链接
- 用于设置或更新值的输入字段
- 删除按钮以移除它

高级/不常用的密钥默认隐藏在切换开关后面。

### 会话

浏览和检查所有 Agent 会话。每行显示会话标题、来源平台图标（CLI、Telegram、Discord、Slack、cron）、模型名称、消息数、工具调用数以及上次活动时间。活动会话标有脉动徽章。

- **搜索** — 使用 FTS5 对所有消息内容进行全文搜索。结果显示高亮片段，展开时会自动滚动到第一个匹配的消息。
- **统计** — 摘要栏显示总会话数、存储中活动的会话数、归档计数、总消息数以及按来源的细分。
- **展开** — 单击会话以加载其完整消息历史。消息按角色（用户、助手、系统、工具）颜色编码，并渲染为带有语法高亮的 Markdown。
- **工具调用** — 带有工具调用的助手消息显示可折叠块，其中包含函数名称和 JSON 参数。
- **重命名** — 内联设置或清除会话标题（铅笔图标）。
- **导出** — 将会话（元数据 + 完整消息历史）下载为 JSON（下载图标）。
- **修剪** — 标题中的 "修剪旧会话" 按钮删除早于 N 天的已结束会话。
- **删除** — 使用垃圾箱图标删除会话及其消息历史。

![会话管理页面——统计栏、修剪以及每行的重命名/导出/删除](/img/dashboard/admin-sessions.png)

### 日志

查看 Agent、网关和错误日志文件，支持过滤和实时跟踪。

- **文件** — 在 `agent`、`errors` 和 `gateway` 日志文件之间切换
- **级别** — 按日志级别过滤：ALL、DEBUG、INFO、WARNING 或 ERROR
- **组件** — 按来源组件过滤：所有、网关、Agent、工具、CLI 或 cron
- **行数** — 选择显示多少行（50、100、200 或 500）
- **自动刷新** — 切换实时跟踪，每 5 秒轮询一次新的日志行
- **颜色编码** — 日志行按严重性着色（红色表示错误，黄色表示警告，暗淡表示调试）

### 分析

根据会话历史计算的使用情况和成本分析。选择一个时间段（7、30 或 90 天）以查看：

- **摘要卡片** — 总令牌（输入/输出）、缓存命中百分比、总估计或实际成本、总会话数及日均值
- **每日令牌图表** — 堆积条形图，显示每天的输入和输出令牌使用量，带有悬停工具提示显示细分和成本
- **每日细分表** — 日期、会话数、输入令牌、输出令牌、缓存命中率和每天的成本
- **按模型细分** — 表格显示使用的每个模型、其会话数、令牌使用量和估计成本

### Cron

创建和管理按计划重复运行 Agent 提示的定时 cron 任务。

- **创建** — 填写名称（可选）、提示、cron 表达式（例如 `0 9 * * *`）和传递目标（本地、Telegram、Discord、Slack 或电子邮件）
- **任务列表** — 每个任务显示其名称、提示预览、计划表达式、状态徽章（已启用/暂停/错误）、传递目标、上次运行时间和下次运行时间
- **暂停/恢复** — 在活动状态和暂停状态之间切换任务
- **编辑** — 打开预填充的模态框以更改任务的提示、计划、名称或传递目标
- **立即触发** — 在正常计划之外立即执行任务
- **删除** — 永久移除 cron 任务

### 配置文件

创建和管理[配置文件](../profiles.md)——具有自己的配置、技能和会话的隔离 Hermes 实例。

- **配置文件卡片** — 每个显示其模型/提供程序、技能数量、网关状态、描述和徽章（活动、默认、别名）
- **创建** — 名称 + 可选从默认克隆/克隆所有内容/无捆绑技能、描述和模型；专用的配置文件生成器页面（`/profiles/new`）提供完整流程（模型、MCP、技能）
- **管理技能和工具** — 跳转到限定于该配置文件的技能页面（设置侧边栏配置文件切换器）
- **设为活动** — 切换粘性默认值，**将来的 CLI/网关运行**会选取（与 `hermes profile use` 相同）。这*不*会更改仪表盘管理的内容——那是配置文件切换器的工作
- **编辑模型/描述/SOUL** — 内联编辑器，写入该配置文件
- **重命名/删除** — 仅限命名配置文件

### 技能

浏览、搜索和切换已安装的技能和工具集，并从中心安装新的技能和工具集。技能从 `~/.hermes/skills/` 加载，并按类别分组。

- **搜索** — 按名称、描述或类别过滤已安装的技能和工具集
- **类别筛选器** — 单击类别药丸以缩小列表（例如 MLOps、MCP、红队、AI）
- **切换** — 使用开关启用或禁用单个技能。更改将在下一次会话时生效。
- **工具集** — 一个单独的视图显示内置工具集（文件操作、网页浏览等），包含其活动/非活动状态、设置要求和包含的工具列表
- **浏览中心** — 第三个视图跨所有来源搜索技能中心（与 `hermes skills search` 相同），通过标识符安装任何结果并显示实时安装日志，并提供"全部更新"按钮以刷新已安装的技能。

![技能管理页面——浏览中心视图：搜索、安装和更新](/img/dashboard/admin-skills-hub.png)

### MCP

无需 CLI 即可管理 [MCP](/integrations/mcp) 服务器。与 `hermes mcp` 读取的 `mcp_servers` 块相同，位于 `config.yaml` 中。

**您的 MCP 服务器：**

- **添加** — 注册 HTTP/SSE 服务器（URL）或 stdio 服务器（命令 + 参数），可选的 `KEY=VALUE` 环境变量用于 stdio 服务器
- **启用/禁用** — 切换服务器开启或关闭而不删除它。禁用的服务器保留在配置中，以便稍后可以重新启用。更改在下一次网关重启时生效。
- **测试** — 连接到服务器，列出其工具，然后断开连接——在 Agent 依赖它之前验证连接
- **移除** — 从配置中删除服务器
- 秘密形式的环境值在列表视图中被脱敏

**目录：** 浏览 Nous 批准的 MCP 服务器（捆绑的 `optional-mcps/` 目录），并一键安装其中任何一个。需要 API 密钥的条目会内联提示输入这些密钥；值会进入 `.env`。这与 `hermes mcp catalog` / `hermes mcp install` 使用的目录相同。

![MCP 管理页面——您的服务器带有启用/禁用开关，以及安装目录](/img/dashboard/admin-mcp.png)

### Webhooks

管理动态 [Webhook 订阅](/user-guide/messaging/webhooks)。必须先在消息设置中启用 Webhook 平台；如果未启用，页面会显示提示。

- **创建** — 名称、描述、事件筛选器、传递目标、可选的直接传递模式以及 Agent 提示。创建后，页面会显示路由 URL 和一次性 HMAC 密钥供您复制。
- **启用/禁用** — 切换订阅开启或关闭。禁用的路由保留在订阅文件中，但网关会拒绝其传入事件（403）。网关会热重载该文件，因此更改会在下一个事件时生效——无需重启。
- **列表** — 每个订阅显示其 URL、事件和传递目标
- **删除** — 移除订阅

![Webhooks 管理页面——带有启用/禁用开关的订阅](/img/dashboard/admin-webhooks.png)

### 配对

无需 CLI 即可批准和撤销消息用户——远程管理员如何将 Telegram/Discord 等用户引入配对网关。与 `hermes pairing` 功能完全一致。

- **待处理请求** — 每个显示平台、代码、用户和年龄，带有批准按钮
- **已批准的用户** — 每个显示平台和用户，带有撤销按钮
- **清除待处理** — 删除所有未完成的配对代码

![配对管理页面](/img/dashboard/admin-pairing.png)

### 渠道

从浏览器将 Hermes 连接到任何消息平台——与 `hermes setup gateway` 功能完全一致。页面列出每个支持的渠道（Telegram、Discord、Slack、Matrix、Mattermost、WhatsApp、Signal、BlueBubbles/iMessage、电子邮件、SMS/Twilio、钉钉、飞书/Lark、企业微信、微信、QQ Bot、元宝，以及 API 服务器和 Webhook 端点），并显示其实时连接状态。

- **配置** — 打开一个按平台定制的表单，其中包含该渠道所需的精确字段（机器人令牌、应用令牌、服务器 URL、允许列表等）。秘密渲染为密码输入字段，并存储为脱敏值；将字段留空会保留现有值。必填字段会标记并验证。"设置指南" 链接指向平台的凭证文档。
- **启用/禁用** — 切换渠道开启或关闭。凭证保留在磁盘上；只有活动状态发生变化。
- **测试** — 检查渠道是否已配置、已启用，并且网关报告了实时连接。
- **重启网关** — 凭证写入 `~/.hermes/.env`，启用标志写入 `config.yaml`；网关在下次重启时连接每个启用的渠道，您可以直接从页面触发重启。

![渠道管理页面——每个消息平台带有状态、启用开关和按平台的设置表单](/img/dashboard/admin-channels.png)

### 系统

用于安装范围操作的综合管理面板：

- **主机** — 实时系统统计信息：操作系统/内核、架构、主机名、Python 和 Hermes 版本、CPU 核心数 + 利用率、内存、Hermes 主目录的磁盘使用量、运行时间和负载平均值。（CPU/内存/磁盘在安装了 `psutil` 时显示；标识字段始终显示。）Hermes 版本显示一个**更新状态徽章**（最新 / 落后 N 个提交）和一个**检查更新**按钮。当通过 git 或 pip 安装存在可用更新时，一个**立即更新**按钮会打开一个确认对话框——显示将拉取多少个提交——然后在后台运行 `hermes update`。在 Docker/Nix/Homebrew 安装中，仪表盘无法就地应用更新，因此它会显示正确的带外命令。
- **Nous Portal** — 登录状态、活动推理提供程序以及工具网关路由表（哪些工具通过 Portal 运行，哪些本地运行），带有一个管理您的订阅的链接。`hermes portal` 的只读镜像。
- **技能管理者** — 后台技能维护状态（活动/暂停、间隔、上次运行），带有暂停/恢复和立即运行按钮。镜像 `hermes curator`。
- **网关** — 启动、停止和重启消息网关，带有实时状态（运行中/已停止、PID、状态）
- **内存** — 选择外部内存提供程序（或仅内置），并重置内置的 `MEMORY.md` / `USER.md` 存储
- **凭证池** — 添加和删除 Agent 轮询使用的轮换 API 密钥（按提供程序）。密钥在列表中脱敏；原始值仅到达 Agent。
- **操作** — 运行 `doctor`、安全审计、创建备份、从备份归档恢复、更新技能、显示系统提示大小明细、生成支持转储或迁移已弃用设置的配置。每个操作启动一个后台操作，其实时日志会流式传输到页面中。
- **检查点** — 查看 `/rollback` 影子存储的大小并修剪它
- **Shell 钩子** — 列出已配置的钩子及其同意 + 可执行状态，**创建**一个钩子（事件、命令、匹配器、超时，带有一个选择加入的同意授予），并移除一个。钩子运行任意命令，因此创建表单带有安全警告，并且只有在授予同意后钩子才会触发。

![系统管理页面——主机统计信息和 Nous Portal 状态](/img/dashboard/admin-system-top.png)

![系统管理页面——技能管理者、网关、内存和凭证池](/img/dashboard/admin-system-curator.png)

![系统管理页面——操作、检查点和 Shell 钩子](/img/dashboard/admin-system-ops.png)

创建 Shell 钩子（注意同意复选框和运行任意命令的警告）：

![新建 Shell 钩子模态框](/img/dashboard/admin-hook-create.png)

:::warning 安全性
Web 仪表盘会读取和写入您的 `.env` 文件，其中包含 API 密钥和秘密。它默认绑定到 `127.0.0.1`——只能从本地机器访问。如果您绑定到 `0.0.0.0`，您网络上的任何人都可以查看和修改您的凭证。仪表盘本身没有认证机制。
:::

## `/reload` 斜杠命令

仪表盘 PR 还为交互式 CLI 添加了一个 `/reload` 斜杠命令。通过 Web 仪表盘更改 API 密钥（或直接编辑 `.env`）后，在活动 CLI 会话中使用 `/reload` 以拾取更改而无需重启：

```
You → /reload
  Reloaded .env (3 var(s) updated)
```

这会重新将 `~/.hermes/.env` 读入运行进程的环境。当您通过仪表盘添加了新的提供程序密钥并希望立即使用它时，这很有用。

## REST API

Web 仪表盘公开了前端使用的 REST API。您也可以直接调用这些端点以实现自动化：

:::tip 按配置文件划分的端点
管理端点系列——`/api/config`、`/api/env`、`/api/skills`、
`/api/tools/toolsets`、`/api/mcp` 和 `/api/model/{info,options,auxiliary,set}`——
接受一个可选的 `?profile=<name>` 查询参数（或写入时在 JSON 主体中的 `"profile"`），将读取/写入限定于该配置文件的 `HERMES_HOME`。省略 = 仪表盘自己的配置文件。未知的配置文件名称返回 `404`。`/api/pty` WebSocket 接受相同的参数以在所选配置文件下生成聊天。
:::

### GET /api/status

返回 Agent 版本、网关状态、平台状态和活动会话数。

### GET /api/sessions

返回最近的 20 个会话及其元数据（模型、令牌计数、时间戳、预览）。

### GET /api/config

以 JSON 格式返回当前的 `config.yaml` 内容。

### GET /api/config/defaults

返回默认配置值。

### GET /api/config/schema

返回描述每个配置字段的模式——类型、描述、类别以及在适用情况下的选择选项。前端使用此信息为每个字段渲染正确的输入控件。

### PUT /api/config

保存新配置。主体：`{"config": {...}}`。

### GET /api/env

返回所有已知的环境变量，包含其设置/未设置状态、脱敏值、描述和类别。

### PUT /api/env

设置一个环境变量。主体：`{"key": "VAR_NAME", "value": "secret"}`。

### DELETE /api/env

移除一个环境变量。主体：`{"key": "VAR_NAME"}`。

### GET /api/sessions/\{session_id\}

返回单个会话的元数据。

### GET /api/sessions/\{session_id\}/messages

返回会话的完整消息历史，包括工具调用和时间戳。

### GET /api/sessions/search

跨消息内容进行全文搜索。查询参数：`q`。返回匹配的会话 ID 及高亮片段。

### DELETE /api/sessions/\{session_id\}

删除会话及其消息历史。

### GET /api/logs

返回日志行。查询参数：`file`（agent/errors/gateway）、`lines`（计数）、`level`、`component`。

### GET /api/analytics/usage

返回令牌使用量、成本和会话分析。查询参数：`days`（默认 30）。响应包含每日细分和按模型的聚合。

### GET /api/cron/jobs

返回所有已配置的 cron 任务及其状态、计划和运行历史。

### POST /api/cron/jobs

创建一个新的 cron 任务。主体：`{"prompt": "...", "schedule": "0 9 * * *", "name": "...", "deliver": "local"}`。

### POST /api/cron/jobs/\{job_id\}/pause

暂停一个 cron 任务。

### POST /api/cron/jobs/\{job_id\}/resume

恢复一个暂停的 cron 任务。

### POST /api/cron/jobs/\{job_id\}/trigger

立即在计划外触发一个 cron 任务。

### DELETE /api/cron/jobs/\{job_id\}

删除一个 cron 任务。

### GET /api/skills

返回所有技能，包含其名称、描述、类别和启用状态。

### PUT /api/skills/toggle

启用或禁用一个技能。主体：`{"name": "skill-name", "enabled": true}`。

### GET /api/tools/toolsets

返回所有工具集，包含其标签、描述、工具列表和活动/已配置状态。

### 管理端点

这些为 MCP、渠道、Webhooks、配对和系统页面提供支持。它们都位于与 `/api/` 其余部分相同的认证门后面。

| 方法 & 路径 | 用途 |
|---------------|---------|
| `GET /api/mcp/servers` | 列出已配置的 MCP 服务器（环境值脱敏） |
| `POST /api/mcp/servers` | 添加服务器。主体：`{name, url?, command?, args?, env?, auth?}` |
| `POST /api/mcp/servers/{name}/test` | 连接、列出工具、断开连接 |
| `PUT /api/mcp/servers/{name}/enabled` | 启用/禁用服务器 |
| `DELETE /api/mcp/servers/{name}` | 移除服务器 |
| `GET /api/mcp/catalog` | 浏览 Nous 批准的 MCP 目录 |
| `POST /api/mcp/catalog/install` | 安装目录条目（含所需环境变量） |
| `GET /api/messaging/platforms` | 列出每个消息渠道及其状态 + 按平台的设置字段 |
| `PUT /api/messaging/platforms/{id}` | 配置渠道。主体：`{enabled?, env?, clear_env?}`（env 写入 `.env`，enabled 写入 `config.yaml`） |
| `POST /api/messaging/platforms/{id}/test` | 报告渠道是否已配置、已启用且已连接 |
| `GET /api/pairing` | 列出待处理 + 已批准的消息用户 |
| `POST /api/pairing/approve` | 批准一个代码。主体：`{platform, code}` |
| `POST /api/pairing/revoke` | 撤销一个用户。主体：`{platform, user_id}` |
| `POST /api/pairing/clear-pending` | 删除所有待处理代码 |
| `GET /api/webhooks` | 列出订阅 + 平台启用状态 |
| `POST /api/webhooks` | 创建订阅（返回一次性密钥） |
| `DELETE /api/webhooks/{name}` | 移除订阅 |
| `GET /api/credentials/pool` | 列出池化的轮换密钥（脱敏） |
| `POST /api/credentials/pool` | 添加一个密钥。主体：`{provider, api_key, label?}` |
| `DELETE /api/credentials/pool/{provider}/{index}` | 移除一个密钥（基于 1 的索引） |
| `GET /api/memory` | 活动提供程序 + 可用提供程序 + 内置文件大小 |
| `PUT /api/memory/provider` | 选择一个提供程序（空 = 仅内置） |
| `POST /api/memory/reset` | 重置内置内存。主体：`{target: all\|memory\|user}` |
| `POST /api/gateway/start` · `/stop` · `/restart` | 网关生命周期（后台运行） |
| `POST /api/ops/doctor` · `/security-audit` · `/backup` · `/import` | 诊断和维护（后台运行；通过 `/api/actions/{name}/status` 跟踪） |
| `GET /api/ops/hooks` | 已配置的 Shell 钩子 + 允许列表状态 |
| `GET /api/ops/checkpoints` · `POST .../prune` | 检查/修剪 `/rollback` 存储 |
| `POST /api/ops/hooks` · `DELETE /api/ops/hooks` | 创建/移除 Shell 钩子（需同意） |
| `GET /api/system/stats` | 主机统计信息——操作系统、CPU、内存、磁盘、运行时间 |
| `GET /api/hermes/update/check` | 报告更新可用性（落后提交数、安装方法），不应用更新。对于落后的 git/pip 安装，还返回 `commits` 列表（`sha`、`summary`、`author`、`at`），显示更改内容。`?force=1` 会绕过 6 小时缓存 |
| `GET /api/curator` · `PUT .../paused` · `POST .../run` | 技能管理者状态 + 暂停/恢复 + 运行 |
| `GET /api/portal` | Nous Portal 认证 + 工具网关路由（只读） |
| `POST /api/ops/prompt-size` · `/dump` · `/config-migrate` | 诊断（后台运行） |
| `PUT /api/webhooks/{name}/enabled` | 启用/禁用 webhook 路由 |
| `POST /api/skills/hub/install` · `/uninstall` · `/update` | 技能中心操作（后台运行） |
| `GET /api/skills/hub/search` | 跨所有来源搜索技能中心 |
| `GET /api/sessions/stats` | 会话存储统计信息 |
| `PATCH /api/sessions/{id}` | 重命名/归档会话 |
| `GET /api/sessions/{id}/export` | 将会话（元数据 + 消息）导出为 JSON |
| `POST /api/sessions/prune` | 删除早于 N 天的已结束会话 |
| `PUT /api/cron/jobs/{id}` | 编辑 cron 任务的提示/计划/名称/传递 |

## 认证（门控模式）

当仪表盘绑定到公共地址或非回环地址——任何不是 `127.0.0.1` / `localhost` 的地址时，Hermes Agent 会启用一个认证门。每个请求都必须带有经过验证的会话 cookie，否则会被重定向到登录页面。系统内置了三个提供程序：

- **[用户名/密码](#usernamepassword-provider-no-oauth-idp)** — 在自托管/本地/家庭实验室仪表盘上添加认证的最简单方法。无需外部身份提供程序。**仅可在受信任的网络或 VPN 后使用——不能暴露在公共互联网上。**
- **[OAuth (Nous Portal)](#default-provider-nous-research)** — 用于托管部署和任何可通过公共互联网访问的仪表盘，也是 [远程 Hermes Desktop 连接](#connecting-hermes-desktop-to-a-remote-backend) 的推荐路径。每次登录都针对您的 Nous 账户进行验证，因此这是适用于面向互联网的提供程序。
- **[自托管 OIDC](#self-hosted-oidc-provider)** — 用于通过标准 OpenID Connect 引入您自己的身份提供程序（Keycloak、Auth0、Okta、Google、GitHub 通过 OIDC 桥接等）。不涉及 Nous Portal；当通过符合要求的 OIDC 服务器前置时，适用于公共互联网暴露。

绑定到回环的操作者拥有的仪表盘不受影响——无需认证，无登录页面。

### 门何时启用

| 标志 | 认证门 | 用例 |
|-------|-----------|----------|
| `hermes dashboard`（默认——绑定到 `127.0.0.1`） | 关闭 | 本地开发 |
| `hermes dashboard --host 0.0.0.0` | **开启** | 远程/生产——使用用户名/密码提供程序或 OAuth 保护 |

门仅在以下情况下开启：
1. 绑定主机不是 `127.0.0.1`、`::1`、`localhost` 或 `0.0.0.0` **且**
2. 未设置 `--insecure` 标志。

:::danger `--insecure` 完全禁用认证
`--insecure` 跳过认证门，提供一个未经认证的仪表盘，可以读取和写入您的 `.env`（API 密钥、秘密）并运行 Agent 命令。**不要将其用于远程连接。** 要将仪表盘暴露给另一台机器，请配置[用户名/密码提供程序](#usernamepassword-provider-no-oauth-idp)（或 OAuth），并保持 `--insecure` 关闭。该标志仅作为完全受信任、已防火墙的单主机网络上的最后应急逃生通道存在。
:::

### 失败关闭语义

如果门会启用但**没有**注册 `DashboardAuthProvider`（没有 Nous 插件，没有自定义插件），`hermes dashboard` 会拒绝绑定并显示明确的错误消息。没有 "默认拒绝但接受所有" 的备选方案——配置错误的门控仪表盘永远不会启动。

当您**交互式**运行 `hermes dashboard --host 0.0.0.0`（在真实的终端中）且尚未配置提供程序时，Hermes 不会直接失败——它会提供现场设置一个：选择**用户名和密码**（将 `dashboard.basic_auth` 写入 `config.yaml`，几秒钟内即可运行）或 **OAuth**（将您指向 `hermes dashboard register`）。非交互式调用者——Docker/s6、CI、管道运行——会跳过提示并遇到上述失败关闭错误，因此无人值守的部署仍然不会在没有认证的情况下启动。

### 默认提供程序：Nous Research

捆绑的 `plugins/dashboard_auth/nous` 插件**始终安装**并自动加载。当配置了客户端 ID 时，它会自动注册一个名为 `nous` 的 `DashboardAuthProvider`。

由于每次登录都针对 Nous Portal 进行验证，并由您的 Nous 账户保护，**Nous 提供程序是适合将仪表盘暴露在公共互联网上的提供程序。**

#### 注册仪表盘

要使用 Nous 提供程序，您需要一个 OAuth 客户端 ID（形状为 `agent:{id}`）。有两种获取方式：

- **CLI — `hermes dashboard register`。** 在仪表盘所在的主机上运行它。它会解析您现有的 Nous 登录（如果您尚未登录，请先运行 `hermes setup`），向 Portal 注册一个自托管的 OAuth 客户端，并将 `HERMES_DASHBOARD_OAUTH_CLIENT_ID` 写入 `~/.hermes/.env`。可选标志：`--name`（人类可读的标签，否则自动生成）和 `--redirect-uri`（面向互联网的主机的公共 HTTPS 回调 URL）。

  ```bash
  hermes dashboard register
  # ✓ Registered dashboard "swift_falcon"
  # …writes HERMES_DASHBOARD_OAUTH_CLIENT_ID to ~/.hermes/.env
  ```

- **GUI — 本地仪表盘页面。** 在 Nous Portal 中打开 [`/local-dashboards`](https://portal.nousresearch.com/local-dashboards)，在浏览器中注册、命名、管理和撤销自托管的仪表盘。将生成的 `agent:{id}` 客户端 ID 复制到 `HERMES_DASHBOARD_OAUTH_CLIENT_ID`（环境变量）或 `dashboard.oauth.client_id`（config.yaml）中。这也是您撤销通过 CLI 注册的仪表盘的地方。

#### 配置

该插件从两个表面读取，当环境变量非空时，环境变量获胜：

**`config.yaml`** — 规范表面：

```yaml
dashboard:
  oauth:
    client_id: agent:01HXYZ…             # 启用门所需
```

**环境变量** — 操作者覆盖：

| 环境变量 | 覆盖 | 格式 | 由...提供 |
|---------|-----------|--------|----------------|
| `HERMES_DASHBOARD_OAUTH_CLIENT_ID` | `dashboard.oauth.client_id` | `agent:{instance_id}` | `hermes dashboard register` |

根据 Hermes Agent 约定（`~/.hermes/.env` 仅用于 API 密钥/秘密），**`config.yaml` 是设置这些值的推荐位置**，适用于本地开发、本地部署和任何您直接控制的部署。环境变量路径的存在是为了让托管平台的秘密注入可以推送每次部署的 `client_id`，而无需任何人编辑镜像内的 `config.yaml`——这是其主要目的。

空的环境值被视为未设置，因此已配置但未填充的平台秘密不会意外地遮蔽有效的 `config.yaml` 条目。

如果两个来源都没有提供 client_id，插件会报告具体原因，仪表盘的失败关闭绑定错误会告诉您需要修复什么：

```
Refusing to bind dashboard to 0.0.0.0 — the OAuth auth gate engages on
non-loopback binds, but no auth providers are registered.

Bundled providers reported these issues:
  • nous: HERMES_DASHBOARD_OAUTH_CLIENT_ID is not set (and
    dashboard.oauth.client_id in config.yaml is empty). The Nous Portal
    provisions this env var (shape 'agent:{instance_id}') when it
    deploys a Hermes Agent instance — set it to your provisioned
    client id (either as an env var or under dashboard.oauth.client_id
    in config.yaml), or pass --insecure to skip the OAuth gate entirely.

Or pass --insecure to skip the auth gate (NOT recommended on untrusted
networks).
```

#### 完整示例：Nous Research

从已登录的 Hermes 安装到 Nous 门控仪表盘，仅需三步。

**1. 登录并注册仪表盘。** `hermes dashboard register` 使用您现有的 Nous 登录来提供一个 OAuth 客户端，并将 `HERMES_DASHBOARD_OAUTH_CLIENT_ID` 写入 `~/.hermes/.env`：

```bash
hermes setup            # 如果您尚未登录 Nous Portal
hermes dashboard register
# ✓ Registered dashboard "swift_falcon"
# …writes HERMES_DASHBOARD_OAUTH_CLIENT_ID to ~/.hermes/.env
```

**2. 在可达地址上运行仪表盘。** 不带 `--insecure` 的非回环绑定会启用 OAuth 门，并且刚写入的 `client_id` 会激活 `nous` 提供程序：

```bash
hermes dashboard --host 0.0.0.0 --port 9119 --no-open
```

**3. 登录。** 打开 `http://<host>:9119/`，您将被重定向到 `/login`。点击 **使用 Nous Research 登录** → 在 Portal 进行认证 → 返回已认证的仪表盘。从任何机器验证门：

```bash
curl -s http://<host>:9119/api/status | jq '.auth_required, .auth_providers'
# true
# ["nous"]
```

`GET /api/auth/me` 随后返回经过验证的会话（`provider: nous`）。对于面向互联网的主机，使用 `--redirect-uri https://hermes.example.com/auth/callback` 注册，并设置 `HERMES_DASHBOARD_PUBLIC_URL`，以便 OAuth 回调解析到您的公共 URL（请参阅 [公共 URL 覆盖](#public-url-override)）。

### 用户名/密码提供程序（无 OAuth IDP）

如果您不想连接 OAuth 身份提供程序——一个自托管的 "just put a password on my dashboard" 部署——捆绑的 `plugins/dashboard_auth/basic` 插件会注册一个名为 `basic` 的 `DashboardAuthProvider`，它使用**用户名和密码**进行认证，而不是 OAuth 重定向。

它插入与 OAuth 提供程序相同的门：不带 `--insecure` 的非回环绑定会启用门，登录页面为此提供程序渲染一个凭据表单（而不是 "使用 X 登录" 按钮），并且登录之后的所有内容——会话 cookie、透明刷新、WS 票据、注销、审计日志——与 OAuth 路径相同。会话是无状态的 HMAC 签名令牌，由提供程序自行生成，因此**没有数据库，也没有外部 IDP**。密码哈希使用标准库 `scrypt`（无第三方依赖）。

:::warning 仅在受信任的网络中使用——不要用于公共互联网
用户名/密码提供程序适用于**受信任网络**上的自托管/本地/家庭实验室仪表盘，或仅通过 **VPN** 可访问的仪表盘。它使用单个共享凭据进行保护，没有外部身份提供程序、MFA 或背后的每个用户账户，因此**不适合将仪表盘直接暴露于公共互联网**。对于面向互联网的仪表盘，请改用 [Nous Research 提供程序](#default-provider-nous-research)（或您自己的[自托管 OIDC](#self-hosted-oidc-provider) / [自定义 OAuth](#custom-providers) 提供程序）。
:::

#### 配置

与 Nous 提供程序一样，它从 `config.yaml`（规范）读取，当环境变量非空时，环境变量获胜。它仅在配置了 `username` 加上 `password_hash`（首选）或 `password` 时激活——否则它是一个无操作，因此 OAuth 用户和回环/`--insecure` 操作者不受影响。

**`config.yaml`：**

```yaml
dashboard:
  basic_auth:
    username: admin
    # 首选——无明文静态存储。计算方式：
    #   python -c "from plugins.dashboard_auth.basic import hash_password; print(hash_password('PW'))"
    password_hash: "scrypt$16384$8$1$…$…"
    # ...或明文密码（加载时在内存中哈希；静态存储时安全性较低）：
    # password: "s3cret"
    secret: "<32+ random bytes, base64 or hex>"  # 令牌签名密钥
    session_ttl_seconds: 43200                    # 可选；访问令牌生命周期（默认 12 小时）
```

**环境变量覆盖：**

| 环境变量 | 覆盖 | 说明 |
|---------|-----------|-------|
| `HERMES_DASHBOARD_BASIC_AUTH_USERNAME` | `dashboard.basic_auth.username` | 激活所需 |
| `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD_HASH` | `dashboard.basic_auth.password_hash` | 首选（无明文静态存储） |
| `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD` | `dashboard.basic_auth.password` | 明文；**覆盖配置中的 `password_hash`**，因此您可以通过环境变量轮换 |
| `HERMES_DASHBOARD_BASIC_AUTH_SECRET` | `dashboard.basic_auth.secret` | 令牌签名密钥 |
| `HERMES_DASHBOARD_BASIC_AUTH_TTL_SECONDS` | `dashboard.basic_auth.session_ttl_seconds` | 访问令牌生命周期 |

:::caution 设置显式 `secret` 以实现稳定的会话
当 `secret` 为空时，会生成一个随机的每进程签名密钥。这对于单个进程没问题，但这意味着**每次重启都会使所有会话失效**，并且会话**不能跨多个工作进程**。为重启持久/多工作进程部署设置显式的 `secret`。
:::

`/auth/password-login` 端点按客户端 IP 进行速率限制（默认 10 次尝试/分钟 → HTTP 429），并且对于未知用户和错误密码都会返回单一的通用 `401 Invalid credentials` 响应，因此不能用作用户名枚举的预言机。

#### 完整示例：用户名/密码

从零到受密码保护的仪表盘，在受信任网络上仅需三步。

**1. 在 `~/.hermes/.env` 中设置凭据。** 哈希密码，以便没有明文静态存储；设置稳定的签名密钥，以便会话在重启后仍然存在：

```bash
# 计算所选密码的 scrypt 哈希：
HASH=$(python -c "from plugins.dashboard_auth.basic import hash_password; print(hash_password('choose-a-strong-password'))")

cat >> ~/.hermes/.env <<EOF
HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin
HERMES_DASHBOARD_BASIC_AUTH_PASSWORD_HASH=$HASH
HERMES_DASHBOARD_BASIC_AUTH_SECRET=$(openssl rand -base64 32)
EOF
chmod 600 ~/.hermes/.env
```

**2. 在可达地址上运行仪表盘。** 不带 `--insecure` 的非回环绑定会启用门，并且用户名 + 哈希会激活 `basic` 提供程序：

```bash
hermes dashboard --host 0.0.0.0 --port 9119 --no-open
```

**3. 登录。** 打开 `http://<host>:9119/`，您将被重定向到 `/login`——一个**凭据表单**（而不是 "使用 X 登录" 按钮）。输入 `admin` / 您的密码 → 进入已认证的仪表盘。从任何机器验证门：

```bash
curl -s http://<host>:9119/api/status | jq '.auth_required, .auth_providers'
# true
# ["basic"]
```

`GET /api/auth/me` 随后返回经过验证的会话（`provider: basic`）。请将其保留在 VPN 后面——请参阅上面的警告；对于公共主机，请改用 [Nous Research](#default-provider-nous-research) 或[自托管 OIDC](#self-hosted-oidc-provider) 提供程序。

#### 编写您自己的密码提供程序

`basic` 只是一个扩展点的实现。任何插件都可以注册密码提供程序：在您的 `DashboardAuthProvider` 子类上设置 `supports_password = True`，并实现 `complete_password_login(*, username, password) -> Session`（在拒绝时引发 `InvalidCredentialsError`，如果后端存储不可用则引发 `ProviderError`）。对于纯密码提供程序，`start_login` / `complete_login` 方法可以作为 `NotImplementedError` 存根保留。这是用于 LDAP 绑定、凭据数据库或任何其他非重定向认证方案的路径——框架负责处理表单、路由、cookie 和刷新。

### 自托管 OIDC 提供程序

如果您运行自己的身份提供程序，捆绑的 `plugins/dashboard_auth/self_hosted` 插件使用**标准 OpenID Connect** 对仪表盘进行认证——无需每个 IDP 的代码，不涉及 Nous Portal。它已经过验证，可与任何符合要求的 OIDC 服务器一起使用：

> **Authentik · Keycloak · Zitadel · Authelia · Auth0 · Okta · Google · …**

与 Nous 提供程序一样，它会自动加载，并且仅在配置后注册自身，因此对于回环/`--insecure` 仪表盘来说是无操作的。

#### 配置

配置一个 **issuer** 和一个 **client_id**（一个公共 PKCE 客户端——无需客户端密钥）。插件从 `{issuer}/.well-known/openid-configuration` 获取 IDP 的 `authorization_endpoint`、`token_endpoint` 和 `jwks_uri`，因此您永远不必硬编码端点 URL。

**`config.yaml`** — 规范表面：

```yaml
dashboard:
  oauth:
    provider: self-hosted
    self_hosted:
      issuer: https://auth.example.com/application/o/hermes/   # 必需
      client_id: hermes-dashboard                              # 必需
      scopes: "openid profile email"                           # 可选（这是默认值）
```

**环境变量** — 操作者覆盖（当非空时，环境变量覆盖 `config.yaml`；空值视为未设置）：

| 环境变量 | 覆盖 | 说明 |
|---------|-----------|-------|
| `HERMES_DASHBOARD_OIDC_ISSUER` | `dashboard.oauth.self_hosted.issuer` | OIDC issuer URL — 必需 |
| `HERMES_DASHBOARD_OIDC_CLIENT_ID` | `dashboard.oauth.self_hosted.client_id` | 公共客户端 id — 必需 |
| `HERMES_DASHBOARD_OIDC_SCOPES` | `dashboard.oauth.self_hosted.scopes` | 默认值为 `openid profile email` |

在您的 IDP 中，注册一个**公共**应用/客户端，使用授权码 + PKCE（S256）授权，并将仪表盘的回调添加为允许的重定向 URI。回调是 `<dashboard public URL>/auth/callback`（有关仪表盘如何在代理后派生其公共 URL，请参阅[公共 URL 覆盖](#public-url-override)）。

#### 验证内容

提供程序针对发现的 `jwks_uri` 验证 OpenID Connect **ID 令牌**（RS256/ES256），并将 `iss` 和 `aud` 声明固定到您配置的 `issuer` 和 `client_id`。标准 OIDC 声明会映射到仪表盘会话：

| 会话字段 | 声明 |
|---------------|----------|
| `user_id` | `sub`（必需） |
| `email` | `email` |
| `display_name` | `name` → `preferred_username` → `nickname` → `email` |
| `org_id` | `org_id` / `organization`，否则连接 `groups` |

ID 令牌是确立身份的——访问令牌被视为不透明的（OIDC 规范不要求它是 JWT）。端点 URL 必须是 HTTPS（对于本地开发 IDP，允许回环 `http://`），并且发现文档声明的 `issuer` 必须与您配置的匹配（末尾斜杠的差异被容忍）。当 IDP 颁发刷新令牌时，它们会通过标准的 `refresh_token` 授权用于静默重新认证；注销会调用 IDP 的 RFC 7009 `revocation_endpoint`（如果已声明）。

> **机密客户端**（带有 `client_secret` 的客户端）尚不支持——请配置一个公共 + PKCE 客户端，这对于面向浏览器的仪表盘来说是典型选择。

#### 完整示例：Keycloak

[Keycloak](https://www.keycloak.org/) 是最容易搭建本地测试的自托管 OIDC 服务器之一——它以开发模式（内存数据库）作为单个容器运行，并公开了教科书式的 OIDC 发现。此演练将带您在几分钟内从零到工作的仪表盘登录。

**1. 运行预配置领域的 Keycloak。** 将此领域导出保存为 `realm-hermes.json`——它定义了一个 `hermes` 领域、一个**公共 PKCE 客户端**（`hermes-dashboard`）和一个测试用户，所有这些都在启动时导入，因此无需在管理 UI 中点击任何内容：

```json
{
  "realm": "hermes",
  "enabled": true,
  "clients": [
    {
      "clientId": "hermes-dashboard",
      "name": "Hermes Agent Dashboard",
      "enabled": true,
      "publicClient": true,
      "standardFlowEnabled": true,
      "protocol": "openid-connect",
      "redirectUris": ["http://localhost:9119/auth/callback"],
      "webOrigins": ["http://localhost:9119"],
      "attributes": { "pkce.code.challenge.method": "S256" }
    }
  ],
  "users": [
    {
      "username": "testuser",
      "enabled": true,
      "emailVerified": true,
      "email": "testuser@example.com",
      "firstName": "Test",
      "lastName": "User",
      "credentials": [
        { "type": "password", "value": "testpassword", "temporary": false }
      ]
    }
  ]
}
```

启动它（Keycloak 26+），将该文件挂载到导入目录：

```bash
docker run --rm -p 8080:8080 \
  -e KC_BOOTSTRAP_ADMIN_USERNAME=admin \
  -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin \
  -v "$PWD/realm-hermes.json:/opt/keycloak/data/import/realm-hermes.json:ro" \
  quay.io/keycloak/keycloak:26.0 \
  start-dev --import-realm
```

启动后，领域在 `http://localhost:8080/realms/hermes/.well-known/openid-configuration` 处声明标准的 OIDC 发现（issuer 为 `http://localhost:8080/realms/hermes`）。管理控制台位于 `http://localhost:8080/`（`admin` / `admin`）。

**2. 将仪表盘指向它。** 自托管插件允许回环 `http://` issuer（对于任何非回环 issuer 都需要 HTTPS），因此本地 Keycloak 可直接使用：

```bash
export HERMES_DASHBOARD_OIDC_ISSUER="http://localhost:8080/realms/hermes"
export HERMES_DASHBOARD_OIDC_CLIENT_ID="hermes-dashboard"
export HERMES_DASHBOARD_PUBLIC_URL="http://localhost:9119"
hermes dashboard --host 0.0.0.0 --port 9119 --no-open
```

`HERMES_DASHBOARD_PUBLIC_URL` 告诉仪表盘其 OAuth 回调是 `http://localhost:9119/auth/callback`——即上面领域注册的重定向 URI。绑定到 `0.0.0.0`（非回环绑定）且不带 `--insecure` 正是启用 OAuth 门的原因。

**3. 登录。** 打开 `http://localhost:9119/`，您将被重定向到 `/login`。点击 **使用自托管 OIDC 登录** → 在 Keycloak 上以 `testuser` / `testpassword` 进行认证 → 返回已认证的仪表盘。侧边栏显示 `Logged in as Test User via self-hosted`，并且 `GET /api/auth/me` 返回经过验证的会话（`provider: self-hosted`，`email: testuser@example.com`）。

> 如果您在不同的主机/端口上绑定或浏览，请将该来源的 `…/auth/callback` 添加到 Keycloak 管理控制台（客户端 → hermes-dashboard → 设置）中客户端的**有效重定向 URI**。相同的模式适用于 Authentik、Zitadel、Authelia 和其他 OIDC 服务器——只有 issuer URL 和客户端注册 UI 不同。

### 公共 URL 覆盖

默认情况下，仪表盘从请求中重建 OAuth 回调 URL——`X-Forwarded-Host` + `X-Forwarded-Proto` + `X-Forwarded-Prefix`（当 uvicorn 配置了 `proxy_headers=True` 时，`start_server` 在门控下启用此功能）。这在正确设置所有这三个标头的反向代理后直接可用。

对于不能可靠转发这些标头的反向代理之后的部署（手动 nginx 设置、本地入口、具有部分代理链的自定义域名部署），请将 `dashboard.public_url`（或 `HERMES_DASHBOARD_PUBLIC_URL`）设置为访问仪表盘的**完整公共 URL**：

```yaml
dashboard:
  public_url: "https://dashboard.example.com/hermes"
```

设置后，OAuth 回调 URL 将直接变为 `<public_url>/auth/callback`——在该代码路径上忽略 `X-Forwarded-Prefix`，因为操作者已显式声明了公共 URL。这是有意为之：如果前缀已包含在 `public_url` 中，再将前缀叠加会导致双重前缀，这是常见情况。

与其他仪表盘设置相同的优先级——环境变量覆盖 `config.yaml`：

| 表面 | 覆盖路径 | 何时使用 |
|---------|---------------|-------------|
| `dashboard.public_url` in `config.yaml` | `HERMES_DASHBOARD_PUBLIC_URL` | 本地开发/本地部署（规范） |
| `HERMES_DASHBOARD_PUBLIC_URL` 环境变量 | — | 托管平台秘密/CI |
| （未设置） | — | 默认——从 `X-Forwarded-*` 标头重建 |

验证会拒绝缺少 `http://` / `https://` 方案、缺少主机或包含引号、尖括号、空格或控制字符的值。格式错误的值会静默回退到标头重建，以便登录流程继续工作，而不是将用户发送到恶意 URL。

> **注意：** `public_url` 仅覆盖 OAuth 回调 URL。`Secure` cookie 标志仍由 `request.url.scheme` 控制（在 `proxy_headers` 下为 `X-Forwarded-Proto`），因此 TLS 终止的公共部署上的 `http://` `public_url` 会产生非安全 cookie。这是操作者需要注意的问题——请将 `public_url` 与正确的上游 TLS 终止配合使用。

### OAuth 流程

提供程序实现了 [Nous Portal OAuth 合同 v1](https://github.com/NousResearch/nous-account-service/blob/main/docs/agent-dashboard-oauth-contract.md)——授权码授权 + PKCE（S256）：

1. 用户访问 `/` 时没有会话 cookie → 门重定向到 `/login`。
2. 登录页面显示 "使用 Nous Research 继续" 按钮 → `/auth/login?provider=nous`。
3. 服务器将 PKCE 状态存储在短期 cookie 中，并将用户重定向到 `https://portal.nousresearch.com/oauth/authorize?…`。
4. 用户在 Portal 进行认证，到达 `/auth/callback?code=…&state=…`。
5. 服务器在 `POST /api/oauth/token` 处将代码交换为访问令牌，根据 Portal 的 JWKS（`/.well-known/jwks.json`）验证 JWT 签名，并设置 `hermes_session_at` cookie。
6. 用户被重定向到 `/`（或通过 `next=` 查询参数重定向到原始深度链接路径）。

访问令牌的 TTL 为 15 分钟。**合同 v1 中没有刷新令牌**——当令牌过期时，SPA 的 fetch 包装器会检测到 401 信封并整页导航回 `/login` 以重新运行流程。

### 设置的 Cookie

| 名称 | 生命周期 | 说明 |
|------|----------|-------|
| `hermes_session_at` | 令牌 TTL（15 分钟） | HttpOnly, SameSite=Lax, Secure-when-HTTPS |
| `hermes_session_pkce` | 10 分钟 | HttpOnly；在往返过程中保存 PKCE 验证器 + 提供程序提示 |
| `hermes_session_rt` | v1 中未使用 | 保留用于向前兼容；当 `refresh_token` 为空时不写入 |

所有三个都是 `Path=/` 和 `SameSite=Lax`。当仪表盘通过 HTTPS 访问时（通过请求 URL 方案检测——在 `proxy_headers=True` 下，尊重来自上游 TLS 终结器的 `X-Forwarded-Proto`），会设置 `Secure` 标志。

### 注销

侧边栏小部件显示 `Logged in as <user_id…> via nous`，带有一个注销图标。点击它会发送 POST 到 `/auth/logout`，清除所有仪表盘认证 cookie，并重定向回 `/login`。

### 审计日志

每次登录开始、成功、失败和会话验证失败都会以 JSON 行的形式写入 `$HERMES_HOME/logs/dashboard-auth.log`。敏感字段（`access_token`、`refresh_token`、`code`、`code_verifier`、`state`、`Authorization` 标头）在记录前会被脱敏。

### 自定义提供程序

要插入非 Nous 的 OAuth 提供程序（例如 Google、GitHub、自定义 OIDC），请创建一个注册 `DashboardAuthProvider` 的插件：

```python
# ~/.hermes/plugins/dashboard-auth-myidp/__init__.py
from hermes_cli.dashboard_auth import DashboardAuthProvider, Session, LoginStart

class MyIdPProvider(DashboardAuthProvider):
    name = "myidp"
    display_name = "My Identity Provider"

    def start_login(self, *, redirect_uri): ...
    def complete_login(self, *, code, state, code_verifier, redirect_uri): ...
    def verify_session(self, *, access_token): ...
    def refresh_session(self, *, refresh_token): ...
    def revoke_session(self, *, refresh_token): ...

def register(ctx):
    ctx.register_dashboard_auth_provider(MyIdPProvider())
```

登录页面列出所有已注册的提供程序；可以堆叠多个提供程序，用户在 `/login` 处选择一个。

### 验证门已开启

```bash
# 快速环境变量路径。
HERMES_DASHBOARD_OAUTH_CLIENT_ID=agent:test \
  hermes dashboard --host 0.0.0.0

# 或通过 config.yaml 等效（推荐用于本地开发/本地部署）：
#
#   dashboard:
#     oauth:
#       client_id: agent:test
#
# 然后只需：
hermes dashboard --host 0.0.0.0

# 访问 /api/status 查看门状态：
curl -s http://127.0.0.1:9119/api/status | jq '.auth_required, .auth_providers'
# true
# ["nous"]
```

仪表盘的 React StatusPage 在 "Web 服务器" 下显示相同的字段。侧边栏的 AuthWidget 在您登录后显示当前身份。

## 将 Hermes Desktop 连接到远程后端

Hermes Desktop 可以驱动在另一台机器（VPS、家庭服务器、Tailscale 后的小型设备）上运行的 Hermes 后端。在应用中，这位于**设置 → 网关 → 远程网关**下，它要求输入**远程 URL** 和**登录**方式。（有关桌面应用本身——安装、设置、聊天——请参阅 [Hermes Desktop](/user-guide/desktop) 页面。）

您使用内置的认证提供程序之一保护远程仪表盘，桌面应用会针对后端宣告的任何提供程序进行登录。对于可访问范围超出您自己机器的后端——VPS、公共主机、任何面向互联网的设备——推荐的提供程序是 **OAuth (Nous Portal)**（使用 [`hermes dashboard register`](#registering-a-dashboard) 注册，并使用 *使用 Nous Research 登录* 登录）。当后端在受信任的 LAN 上或仅通过 VPN 可达时，捆绑的[用户名/密码提供程序](#usernamepassword-provider-no-oauth-idp)是最快的选择，但**不适合直接暴露在公共互联网上**。将仪表盘绑定到非回环地址会启用其认证门；登录后，Desktop 会自动为聊天 WebSocket 重用会话——无需复制或粘贴令牌。

以下配方使用用户名/密码路径，因为这是在受信任网络上最快搭建的方式；有关 OAuth 路径，请参阅 [默认提供程序：Nous Research](#default-provider-nous-research)。

### 在后端（远程机器）

```bash
# 1. 在 ~/.hermes/.env 中设置仪表盘登录凭据（秘密文件，0600）。
cat >> ~/.hermes/.env <<'EOF'
HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin
HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=choose-a-strong-password
# 推荐：一个稳定的签名密钥，以便会话在重启后仍然存在。
HERMES_DASHBOARD_BASIC_AUTH_SECRET=$(openssl rand -base64 32)
EOF
chmod 600 ~/.hermes/.env

# 2. 运行绑定到可达地址的仪表盘。非回环绑定会启用认证门；
#    用户名/密码提供程序处理登录。
hermes dashboard --no-open --host 0.0.0.0 --port 9119
```

更喜欢静态存储时无明文？请改用 `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD_HASH` 配合 scrypt 哈希——有关完整表面，请参阅[用户名/密码提供程序](#usernamepassword-provider-no-oauth-idp)。

如果您将仪表盘作为 systemd 服务运行，当单元具有 `EnvironmentFile=%h/.hermes/.env` 时，`~/.hermes/.env` 会自动加载，因此凭据在启动时就在环境中。

:::warning
仪表盘会读取和写入您的 `.env`（API 密钥、秘密）并可以运行 Agent 命令。此处展示的**用户名/密码**设置适用于受信任的网络——切勿将受密码保护的仪表盘直接暴露到开放互联网。将其置于 VPN 之后。[Tailscale](https://tailscale.com/) 是一个干净的选择：绑定到机器的 tailscale IP（`--host <tailscale-ip>`），并使用 `http://<tailscale-ip>:9119` 作为远程 URL。只有您的 tailnet 上的设备可以访问它。要通过公共互联网访问后端，请改用 **OAuth (Nous Portal)** 提供程序。
:::

### 在 Hermes Desktop 中

**设置 → 网关 → 远程网关：**

- **远程 URL** — `http://<backend-host>:9119`（如果您使用反向代理前置，也支持像 `/hermes` 这样的路径前缀）
- **登录** — 应用检测到用户名/密码网关，并显示一个**登录**按钮；点击它并输入步骤 1 中的凭据
- **保存并重新连接** — 将桌面 shell 切换到远程后端

当在后台设置了 `HERMES_DASHBOARD_BASIC_AUTH_SECRET` 时，会话会自动刷新并在重启后仍然存在。

### 环境变量覆盖

无需在应用内设置，您可以在启动桌面之前使用环境变量将其指向后端。当设置了 `HERMES_DESKTOP_REMOTE_URL` 时，它会覆盖保存的应用内 URL（网关设置