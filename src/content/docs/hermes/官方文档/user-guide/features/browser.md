--- frontmatter ---
---
title: 浏览器自动化
description: 通过多种后端服务控制浏览器：通过 CDP 控制本地 Chromium 系列浏览器，或使用云浏览器进行网页交互、表单填写、数据抓取等。
sidebar_label: 浏览器
sidebar_position: 5
---

--- body ---
# 浏览器自动化

Hermes 代理（Agent）包含一套完整的浏览器自动化工具集，支持多种后端选项：

- **Browserbase 云模式**：通过 [Browserbase](https://browserbase.com) 提供托管云浏览器和反机器人工具
- **Browser Use 云模式**：通过 [Browser Use](https://browser-use.com) 作为替代云浏览器提供商
- **Firecrawl 云模式**：通过 [Firecrawl](https://firecrawl.dev) 提供内置数据抓取的云浏览器
- **Camofox 本地模式**：通过 [Camofox](https://github.com/jo-inc/camofox-browser) 进行本地反检测浏览（基于 Firefox 的指纹伪装）
- **本地 Chromium 系列 CDP**：使用 `/browser connect` 将浏览器工具连接到您自己的 Chrome、Brave、Chromium 或 Edge 实例
- **本地浏览器模式**：通过 `agent-browser` CLI 和本地 Chromium 安装

在所有模式下，代理都可以导航网站、与页面元素交互、填写表单和提取信息。

## 概览

页面被表示为**无障碍树（accessibility trees）**（基于文本的快照），使其非常适合 LLM 代理（Agent）。交互式元素会获得 ref ID（如 `@e1`、`@e2`），代理使用这些 ID 进行点击和输入。

主要功能：

- **多提供商云执行** — Browserbase、Browser Use 或 Firecrawl — 无需本地浏览器
- **本地 Chromium 系列集成** — 通过 CDP 连接到您正在运行的 Chrome、Brave、Chromium 或 Edge 浏览器，进行实操浏览
- **内置隐蔽性** — 随机指纹、验证码解决、住宅代理（Browserbase）
- **会话隔离** — 每个任务拥有独立的浏览器会话
- **自动清理** — 非活动会话在超时后关闭
- **视觉分析** — 截图 + AI 分析，用于视觉理解

## 设置

:::tip Nous 订阅用户
如果您拥有付费的 [Nous Portal](https://portal.nousresearch.com) 订阅，您可以通过 **[工具网关（Tool Gateway）](tool-gateway.md)** 使用浏览器自动化，无需单独的 API 密钥。新安装可运行 `hermes setup --portal` 登录并一次启用所有网关工具；现有安装可通过 `hermes model` 或 `hermes tools` 选择 **Nous 订阅（Nous Subscription）** 作为浏览器提供商。
:::

### Browserbase 云模式

要使用 Browserbase 管理的云浏览器，请添加：

```bash
# 添加到 ~/.hermes/.env
BROWSERBASE_API_KEY=***
BROWSERBASE_PROJECT_ID=your-project-id-here
```

在 [browserbase.com](https://browserbase.com) 获取您的凭证。

### Browser Use 云模式

要使用 Browser Use 作为云浏览器提供商，请添加：

```bash
# 添加到 ~/.hermes/.env
BROWSER_USE_API_KEY=***
```

在 [browser-use.com](https://browser-use.com) 获取您的 API 密钥。Browser Use 通过其 REST API 提供云浏览器。如果同时设置了 Browserbase 和 Browser Use 的凭证，Browserbase 优先。

### Firecrawl 云模式

要使用 Firecrawl 作为云浏览器提供商，请添加：

```bash
# 添加到 ~/.hermes/.env
FIRECRAWL_API_KEY=fc-***
```

在 [firecrawl.dev](https://firecrawl.dev) 获取您的 API 密钥。然后选择 Firecrawl 作为您的浏览器提供商：

```bash
hermes setup tools
# → 浏览器自动化（Browser Automation） → Firecrawl
```

可选设置：

```bash
# 自托管 Firecrawl 实例（默认：https://api.firecrawl.dev）
FIRECRAWL_API_URL=http://localhost:3002

# 会话生存时间（秒）（默认：300）
FIRECRAWL_BROWSER_TTL=600
```

### 混合路由：公共 URL 使用云服务，本地 / localhost 使用本地服务

当配置了云提供商时，Hermes 会自动为解析到私有/回环/LAN 地址（`localhost`、`127.0.0.1`、`192.168.x.x`、`10.x.x.x`、`172.16-31.x.x`、`*.local`、`*.lan`、`*.internal`、IPv6 回环 `::1`、链路本地 `169.254.x.x`）的 URL 启动一个**本地 Chromium 辅助进程（sidecar）**。公共 URL 在同一个对话中继续使用云提供商。

这解决了常见的“我在本地开发但使用 Browserbase”的工作流程问题——代理可以截图您的 `http://localhost:3000` 仪表盘，同时也可以抓取 `https://github.com`，而无需您切换提供商或禁用 SSRF 防护。云提供商永远不会看到私有 URL。

该功能**默认开启**。要禁用它（所有 URL 都像以前一样发送到配置的云提供商）：

```yaml
# ~/.hermes/config.yaml
browser:
  cloud_provider: browserbase
  auto_local_for_private_urls: false
```

禁用自动路由后，私有 URL 将被拒绝，并返回 `"Blocked: URL targets a private or internal address"`，除非您同时设置了 `browser.allow_private_urls: true`（这会让云提供商尝试访问它们——通常不起作用，因为 Browserbase 等无法访问您的 LAN）。

要求：本地辅助进程（sidecar）使用与纯本地模式相同的 `agent-browser` CLI，因此您需要安装它（`hermes setup tools → 浏览器自动化（Browser Automation）` 会自动安装）。从公共 URL 重定向到私有地址的导航后重定向仍会被阻止（您无法通过重定向到内部地址的技巧通过公共路径到达您的 LAN）。

### Camofox 本地模式

[Camofox](https://github.com/jo-inc/camofox-browser) 是一个自托管的 Node.js 服务器，包装了 Camoufox（一个具有 C++ 指纹伪装的 Firefox 分支）。它提供本地反检测浏览，无需依赖云服务。

```bash
# 首先克隆 Camofox 浏览器服务器
git clone https://github.com/jo-inc/camofox-browser
cd camofox-browser

# 使用默认容器设置构建并启动 Docker
# （自动检测架构：M1/M2 上为 aarch64，Intel 上为 x86_64）
make up

# 停止并移除默认容器
make down

# 强制进行干净的重新构建（例如，在升级 VERSION/RELEASE 后）
make reset

# 仅下载二进制文件，不构建
make fetch

# 显式覆盖架构或版本
make up ARCH=x86_64
make up VERSION=135.0.1 RELEASE=beta.24
```

`make up` 会立即启动默认容器。如果您想要自定义运行时设置，例如更大的 Node 堆、VNC 或持久化配置文件目录，请先构建镜像，然后自行运行：

```bash
# 构建镜像，不启动默认容器
make build

# 使用持久化、VNC 实时查看和更大的 Node 堆启动
mkdir -p ~/.camofox-docker
docker run -d \
  --name camofox-browser \
  --restart unless-stopped \
  -p 9377:9377 \
  -p 6080:6080 \
  -p 5901:5900 \
  -e CAMOFOX_PORT=9377 \
  -e ENABLE_VNC=1 \
  -e VNC_BIND=0.0.0.0 \
  -e VNC_RESOLUTION=1920x1080 \
  -e MAX_OLD_SPACE_SIZE=2048 \
  -v ~/.camofox-docker:/root/.camofox \
  camofox-browser:135.0.1-aarch64
```

启用 VNC 后，浏览器以有头模式运行，可以在您的浏览器中通过 `http://localhost:6080`（noVNC）实时观看。您还可以将原生 VNC 客户端连接到 `localhost:5901`。

如果您已经运行了 `make up`，请在启动自定义容器之前停止并移除该默认容器：

```bash
make down
# 然后运行上面的自定义 docker run 命令
```

然后在 `~/.hermes/.env` 中设置：

```bash
CAMOFOX_URL=http://localhost:9377
```

如果 Camofox 在 Docker 中运行，并且您希望它打开宿主机器上提供的 Web 应用程序，请启用回环重写。`CAMOFOX_URL` 仍应指向宿主发布的控制 API，但页面 URL（例如 `http://127.0.0.1:3000`）必须从容器内部以 `http://host.docker.internal:3000` 的形式打开：

```yaml
# ~/.hermes/config.yaml
browser:
  camofox:
    rewrite_loopback_urls: true
    loopback_host_alias: host.docker.internal  # 默认；如果需要，可以使用 LAN IP
```

等效的环境变量：

```bash
CAMOFOX_REWRITE_LOOPBACK_URLS=true
CAMOFOX_LOOPBACK_HOST_ALIAS=host.docker.internal
```

重写仅适用于回环主机（`localhost`、`127.0.0.1`、`::1`）的页面导航 URL。它不会改变 `CAMOFOX_URL`。对于非 Docker 的 Camofox 安装，请禁用此功能，因为浏览器已经在宿主机上运行，回环 URL 是正确的。

或者通过 `hermes tools` → 浏览器自动化（Browser Automation） → Camofox 进行配置。

当设置了 `CAMOFOX_URL` 时，所有浏览器工具将自动通过 Camofox 路由，而不是 Browserbase 或 agent-browser。

#### 持久化浏览器会话

默认情况下，每个 Camofox 会话都会获得一个随机身份——Cookie 和登录状态不会在代理重启后保留。要启用持久化浏览器会话，请在 `~/.hermes/config.yaml` 中添加以下内容：

```yaml
browser:
  camofox:
    managed_persistence: true
```

然后完全重启 Hermes，以便应用新配置。

:::warning 嵌套路径很重要
Hermes 读取 `browser.camofox.managed_persistence`，**而不是**顶层的 `managed_persistence`。一个常见错误是写成：

```yaml
# ❌ 错误 — Hermes 会忽略此项
managed_persistence: true
```

如果标志放在了错误的路径下，Hermes 会静默地回退到随机的临时 `userId`，您的登录状态会在每次会话中丢失。
:::

##### Hermes 做了什么
- 向 Camofox 发送一个确定性的、与配置文件作用域相关的 `userId`，以便服务器可以在会话间重用相同的 Firefox 配置文件。
- 在清理时跳过服务器端的上下文销毁，以便 Cookie 和登录状态在代理任务间得以保留。
- 将 `userId` 作用域限定在活动的 Hermes 配置文件中，因此不同的 Hermes 配置文件会获得不同的浏览器配置文件（配置文件隔离）。

##### Hermes 不做什么
- 它不会强制 Camofox 服务器进行持久化。Hermes 仅发送一个稳定的 `userId`；服务器必须通过将该 `userId` 映射到一个持久的 Firefox 配置文件目录来遵守它。
- 如果您的 Camofox 服务器构建将每个请求都视为临时性的（例如，总是调用 `browser.newContext()` 而不加载存储的配置文件），Hermes 无法使这些会话持久化。请确保您正在运行一个实现了基于 userId 的配置文件持久化的 Camofox 构建版本。

##### 验证其工作

1. 启动 Hermes 和您的 Camofox 服务器。
2. 在浏览器任务中打开 Google（或任何登录网站）并手动登录。
3. 正常结束浏览器任务。
4. 启动一个新的浏览器任务。
5. 再次打开同一个网站——您应该仍然保持登录状态。

如果第 5 步将您登出，则说明 Camofox 服务器没有遵守稳定的 `userId`。请仔细检查您的配置路径，确认在编辑 `config.yaml` 后完全重启了 Hermes，并验证您的 Camofox 服务器版本支持持久的每用户配置文件。

##### 状态存储位置

Hermes 从配置文件作用域的目录 `~/.hermes/browser_auth/camofox/`（或非默认配置文件下的 `$HERMES_HOME` 等效目录）派生出稳定的 `userId`。实际的浏览器配置文件数据存储在 Camofox 服务器端，由该 `userId` 作为键。要完全重置一个持久化配置文件，请在 Camofox 服务器上清除它，并移除相应的 Hermes 配置文件的配置状态目录。

#### 外部管理的 Camofox 会话

当另一个应用驱动可见的 Camofox 浏览器（例如桌面助手、自定义集成、另一个代理）时，配置 Hermes 在该相同身份内操作，而不是生成其自己的隔离配置文件。

三个控制旋钮：

| 设置 | 环境变量 | 效果 |
|------|---------|------|
| `browser.camofox.user_id` | `CAMOFOX_USER_ID` | Hermes 在创建标签时使用的 Camofox `userId`。设置此项会将会话置于“外部管理”模式。 |
| `browser.camofox.session_key` | `CAMOFOX_SESSION_KEY` | 在创建标签时发送的 `sessionKey`（也称为 `listItemId`）。用于在采纳（adoption）时匹配现有标签。如果未设置，则默认为每任务一个值。 |
| `browser.camofox.adopt_existing_tab` | `CAMOFOX_ADOPT_EXISTING_TAB` | 当为 true 时，Hermes 在首次使用时调用 `GET /tabs?userId=<user_id>`，并在创建新标签之前重用现有标签。 |

环境变量优先于 `config.yaml`。两种形式均可：

```yaml
browser:
  camofox:
    user_id: shared-camofox
    session_key: visible-tab
    adopt_existing_tab: true
```

```bash
CAMOFOX_USER_ID=shared-camofox
CAMOFOX_SESSION_KEY=visible-tab
CAMOFOX_ADOPT_EXISTING_TAB=true
```

**当设置了 `user_id` 时会发生什么变化：**

- Hermes 在任务结束时跳过破坏性清理（与 `managed_persistence: true` 相同）。其他应用的标签/Cookie/配置文件得以保留。
- Hermes **不会**调用 `DELETE /sessions/<user_id>`——该端点会清除所有用户数据，因此如果调用，将摧毁外部应用的会话。

**标签采纳（tab adoption）的工作原理（当 `adopt_existing_tab: true` 时）：**

1. 在进程启动后的第一次浏览器工具调用时，Hermes 发出 `GET /tabs?userId=<user_id>`（5 秒超时）。
2. 如果响应中的任何标签具有 `listItemId == session_key`，Hermes 会采纳该组中最近创建的一个。
3. 否则，Hermes 会为该用户采纳最近创建的标签（任何 `listItemId`）。
4. 如果没有标签存在或请求失败，Hermes 会在下一次操作时回退到创建新标签。

采纳仅在会话的 `tab_id` 被填充之前触发。如果外部应用在运行过程中关闭了已采纳的标签，下一次浏览器工具调用将返回 Camofox 错误——Hermes 不会在每次调用时重新轮询新标签。

**选择 `session_key`：** 如果您希望 Hermes 可靠地附加到一个*特定*的现有标签，请将 `session_key` 设置为外部应用在创建该标签时使用的 `listItemId`。如果您不设置 `session_key`，只设置 `user_id`，Hermes 会生成一个每任务的 `session_key`（`task_<id>`）——Hermes 将与外部应用共享 Cookie 和配置文件，但会打开自己的标签而不是重用。

**并发注意事项：** 外部应用和 Hermes 可以同时驱动同一个 Camofox `userId`，但 Camofox 不会在客户端之间协调每标签的焦点。请在应用层协调所有权（例如，外部应用在 Hermes 运行时暂停）。

#### VNC 实时查看

当 Camofox 以有头模式运行（带有可见的浏览器窗口）时，它会在健康检查响应中暴露一个 VNC 端口。Hermes 会自动发现此端口，并将 VNC URL 包含在导航响应中，以便代理可以分享一个链接供您实时观看浏览器。

### 通过 CDP 使用本地 Chromium 系列浏览器（`/browser connect`）

除了云提供商之外，您还可以通过 Chrome DevTools 协议（CDP）将 Hermes 浏览器工具附加到您正在运行的 Chrome、Brave、Chromium 或 Edge 实例。当您希望实时查看代理正在做什么、与需要您自己的 Cookie/会话的页面交互，或避免云浏览器成本时，这非常有用。

:::note
`/browser connect` 是一个**交互式 CLI 斜杠命令**——它不会由网关分派。如果您尝试在 WebUI、Telegram、Discord 或其他网关聊天中运行它，该消息将作为纯文本发送给代理，并且命令不会执行。请从终端启动 Hermes（`hermes` 或 `hermes chat`），然后在那里发出 `/browser connect`。
:::

在 CLI 中，使用：

```
/browser connect                 # 自动启动/连接到本地 Chromium 系列浏览器，地址为 http://127.0.0.1:9222
/browser connect ws://host:port  # 连接到特定的 CDP 端点
/browser status                  # 检查当前连接
/browser disconnect              # 分离并返回云/本地模式
```

如果浏览器尚未通过远程调试运行，Hermes 将尝试自动启动一个支持的 Chromium 系列浏览器，并附带 `--remote-debugging-port=9222`。检测包括 Brave、Google Chrome、Chromium 和 Microsoft Edge，常见的 Linux 安装路径如 `/opt/brave-bin/brave` 和 `/snap/bin/brave`。

:::tip
要手动启动一个启用了 CDP 的 Chromium 系列浏览器，请使用专用用户数据目录，这样即使浏览器已经使用您的正常配置文件运行，调试端口也能正常启动：

```bash
# Linux — Brave
brave-browser \
  --remote-debugging-port=9222 \
  --user-data-dir=$HOME/.hermes/chrome-debug \
  --no-first-run \
  --no-default-browser-check &

# Linux — Google Chrome
google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=$HOME/.hermes/chrome-debug \
  --no-first-run \
  --no-default-browser-check &

# macOS — Brave
"/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.hermes/chrome-debug" \
  --no-first-run \
  --no-default-browser-check &

# macOS — Google Chrome
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.hermes/chrome-debug" \
  --no-first-run \
  --no-default-browser-check &
```

然后启动 Hermes CLI 并运行 `/browser connect`。

**为什么需要 `--user-data-dir`？** 如果没有它，在常规实例已经在运行时启动 Chromium 系列浏览器通常会在现有进程上打开一个新窗口——而该现有进程启动时并未附带 `--remote-debugging-port`，因此端口 9222 永远不会打开。专用用户数据目录强制启动一个新的浏览器进程，调试端口会真正监听。`--no-first-run --no-default-browser-check` 会跳过新配置文件的首次启动引导。
:::

当通过 CDP 连接时，所有浏览器工具（`browser_navigate`、`browser_click` 等）将在您的实时浏览器实例上操作，而不是启动云会话。

### WSL2 + Windows Chrome：优先使用 MCP 而非 `/browser connect`

如果 Hermes 在 WSL2 内部运行，但您想要控制的 Chrome 窗口在 Windows 宿主机上运行，那么 `/browser connect` 通常不是最佳路径。

原因：

- `/browser connect` 期望 Hermes 本身能够到达一个可用的 CDP 端点
- 现代 Chrome 的实时调试会话通常暴露一个仅宿主本地的端点，无法像经典的 `9222` 端口那样直接从 WSL2 访问
- 即使 Windows Chrome 是可调试的，最干净的集成方式通常是让 Windows 端的浏览器 MCP 服务器附加到 Chrome，然后让 Hermes 与该 MCP 服务器通信

对于这种设置，建议通过 Hermes 的 MCP 支持使用 `chrome-devtools-mcp`。

有关实际设置，请参阅 MCP 指南：

- [在 Hermes 中使用 MCP（Use MCP with Hermes）](../../guides/use-mcp-with-hermes.md#wsl2-bridge-hermes-in-wsl-to-windows-chrome)

### 本地浏览器模式

如果您**没有**设置任何云凭证，也没有使用 `/browser connect`，Hermes 仍然可以通过由 `agent-browser` 驱动的本地 Chromium 安装来使用浏览器工具。

### 可选环境变量

```bash
# 用于更好验证码解决的住宅代理（默认："true"）
BROWSERBASE_PROXIES=true

# 使用自定义 Chromium 的高级隐蔽模式 — 需要 Scale Plan（默认："false"）
BROWSERBASE_ADVANCED_STEALTH=false

# 断开连接后的会话重连 — 需要付费计划（默认："true"）
BROWSERBASE_KEEP_ALIVE=true

# 自定义会话超时时间（秒）（最大 21600 = 6 小时）（默认：项目默认值）
# 示例：600（10 分钟），1800（30 分钟），21600（6 小时最大）
BROWSERBASE_SESSION_TIMEOUT=1800

# 自动清理前的非活动超时时间（秒）（默认：120）
BROWSER_INACTIVITY_TIMEOUT=120

# 额外的 Chromium 启动标志（逗号或换行分隔）。Hermes 在检测到 root 或受 AppArmor 限制的非特权用户命名空间（Ubuntu 23.10+，DGX Spark，许多容器镜像）时会自动注入
# `--no-sandbox,--disable-dev-shm-usage`，因此大多数用户不需要设置此项。仅在您需要 Hermes 不会自动添加的标志时手动设置；设置此项会禁用自动注入。
AGENT_BROWSER_ARGS=--no-sandbox
```

### 安装 agent-browser CLI

```bash
npm install -g agent-browser
# 或者在仓库本地安装：
npm install
```

:::info
`browser` 工具集必须包含在您的配置的 `toolsets` 列表中，或者通过 `hermes config set toolsets '["hermes-cli", "browser"]'` 启用。
:::

## 可用工具

### `browser_navigate`

导航到 URL。必须在任何其他浏览器工具之前调用。初始化 Browserbase 会话。

```
Navigate to https://github.com/NousResearch
```

:::tip
对于简单的信息检索，建议优先使用 `web_search` 或 `web_extract`——它们更快且更便宜。当您需要**与页面交互**（点击按钮、填写表单、处理动态内容）时，请使用浏览器工具。
:::

### `browser_snapshot`

获取当前页面无障碍树的文本快照。返回具有 ref ID（如 `@e1`、`@e2`）的交互式元素，供 `browser_click` 和 `browser_type` 使用。

- **`full=false`**（默认）：紧凑视图，仅显示交互式元素
- **`full=true`**：完整页面内容

超过 8000 字符的快照会自动由 LLM 总结。

### `browser_click`

通过快照中的 ref ID 点击一个元素。

```
Click @e5 to press the "Sign In" button
```

### `browser_type`

在输入字段中输入文本。先清空字段，然后输入新文本。

```
Type "hermes agent" into the search field @e3
```

### `browser_scroll`

向上或向下滚动页面以显示更多内容。

```
Scroll down to see more results
```

### `browser_press`

按下一个键盘按键。对于提交表单或导航非常有用。

```
Press Enter to submit the form
```

支持的按键：`Enter`、`Tab`、`Escape`、`ArrowDown`、`ArrowUp` 等。

### `browser_back`

返回浏览器历史记录中的上一页。

### `browser_get_images`

列出当前页面上所有图片及其 URL 和 alt 文本。用于查找要分析的图片。

### `browser_vision`

截图并使用视觉 AI 进行分析。当文本快照无法捕获重要的视觉信息时使用——特别适用于验证码、复杂布局或视觉验证挑战。

截图会被持久保存，文件路径会与 AI 分析结果一起返回。在消息平台（Telegram、Discord、Slack、WhatsApp）上，您可以要求代理分享截图——它会通过 `MEDIA:` 机制作为原生照片附件发送。

```
What does the chart on this page show?
```

截图存储在 `~/.hermes/cache/screenshots/` 中，并在 24 小时后自动清理。

### `browser_console`

从当前页面获取浏览器控制台输出（日志/警告/错误消息）和未捕获的 JavaScript 异常。对于检测无障碍树中未显示的无静默 JS 错误至关重要。

```
Check the browser console for any JavaScript errors
```

使用 `clear=True` 在读取后清除控制台，以便后续调用仅显示新消息。

当使用 `expression` 参数调用时，`browser_console` 还会评估 JavaScript——与 DevTools 控制台相同的形态，结果会以解析后的形式返回（JSON 序列化的对象变为字典；原始值保持原始类型）。

```
browser_console(expression="document.querySelector('h1').textContent")
browser_console(expression="JSON.stringify(performance.timing)")
```

当当前会话有活动的 CDP 主管器（supervisor）时（典型情况：对支持 CDP 的后端运行过 `browser_navigate` 的任何会话），评估会在主管器的持久 WebSocket 上运行——没有子进程启动开销。否则，会回退到标准的 agent-browser CLI 路径。行为完全相同；只有延迟会改变。

### `browser_cdp`

原始 Chrome DevTools 协议透传——用于其他工具未涵盖的浏览器操作的逃生窗口。用于原生对话框处理、iframe 作用域的评估、Cookie/网络控制或代理需要的任何 CDP 动词。

**仅在会话启动时可访问 CDP 端点时才可用**——意味着 `/browser connect` 已附加到正在运行的 Chrome、Brave、Chromium 或 Edge 浏览器，或者已在 `config.yaml` 中设置了 `browser.cdp_url`。默认的本地 agent-browser 模式、Camofox 和云提供商（Browserbase、Browser Use、Firecrawl）目前不向此工具暴露 CDP——云提供商有每会话的 CDP URL，但实时会话路由是后续功能。

**CDP 方法参考：** https://chromedevtools.github.io/devtools-protocol/——代理可以使用 `web_extract` 提取特定方法的页面以查找参数和返回形状。

常见模式：

```
# 列出标签（浏览器级别，无 target_id）
browser_cdp(method="Target.getTargets")

# 处理标签上的原生 JS 对话框
browser_cdp(method="Page.handleJavaScriptDialog",
            params={"accept": true, "promptText": ""},
            target_id="<tabId>")

# 在特定标签中评估 JS
browser_cdp(method="Runtime.evaluate",
            params={"expression": "document.title", "returnByValue": true},
            target_id="<tabId>")

# 获取所有 Cookie
browser_cdp(method="Network.getAllCookies")
```

浏览器级别的方法（`Target.*`、`Browser.*`、`Storage.*`）省略 `target_id`。页面级别的方法（`Page.*`、`Runtime.*`、`DOM.*`、`Emulation.*`）需要来自 `Target.getTargets` 的 `target_id`。每个无状态调用都是独立的——会话不会在调用之间持久化。

**跨域 iframe：** 传递 `frame_id`（来自 `browser_snapshot.frame_tree.children[]`，其中 `is_oopif=true`）以通过主管器的实时会话将该 iframe 的 CDP 调用路由。这是如何在 Browserbase 上实现在跨域 iframe 内进行 `Runtime.evaluate` 的方法，因为无状态 CDP 连接会遇到签名的 URL 过期。示例：

```
browser_cdp(
  method="Runtime.evaluate",
  params={"expression": "document.title", "returnByValue": True},
  frame_id="<frame_id from browser_snapshot>",
)
```

同源 iframe 不需要 `frame_id`——使用来自顶层 `Runtime.evaluate` 的 `document.querySelector('iframe').contentDocument` 替代。

### `browser_dialog`

响应原生 JS 对话框（`alert` / `confirm` / `prompt` / `beforeunload`）。在此工具存在之前，对话框会静默地阻塞页面的 JavaScript 线程，后续的 `browser_*` 调用会挂起或抛出；现在代理可以在 `browser_snapshot` 输出中看到挂起的对话框并显式响应。

**工作流程：**
1. 调用 `browser_snapshot`。如果对话框正在阻塞页面，它会显示为 `pending_dialogs: [{"id": "d-1", "type": "alert", "message": "..."}]`。
2. 调用 `browser_dialog(action="accept")` 或 `browser_dialog(action="dismiss")`。对于 `prompt()` 对话框，传递 `prompt_text="..."` 以提供响应。
3. 重新快照——`pending_dialogs` 为空；页面的 JS 线程已恢复。

**检测通过持久的 CDP 主管器自动完成**——每个任务一个 WebSocket，订阅 Page/Runtime/Target 事件。主管器还在快照中填充 `frame_tree` 字段，以便代理可以看到当前页面的 iframe 结构，包括跨域（OOPIF）iframe。

**可用性矩阵：**

| 后端 | 通过 `pending_dialogs` 检测 | 响应（`browser_dialog` 工具） |
|------|---------------------------|------------------------------|
| 通过 `/browser connect` 或 `browser.cdp_url` 的本地 Chrome | ✓ | ✓ 完整工作流程 |
| Browserbase | ✓ | ✓ 完整工作流程（通过注入的 XHR 桥） |
| Camofox / 默认本地 agent-browser | ✗ | ✗（无 CDP 端点） |

**在 Browserbase 上的工作原理。** Browserbase 的 CDP 代理会在服务器端大约 10 毫秒内自动消除真正的原生对话框，因此我们无法使用 `Page.handleJavaScriptDialog`。主管器通过 `Page.addScriptToEvaluateOnNewDocument` 注入一个小脚本，该脚本用同步 XHR 覆盖 `window.alert`/`confirm`/`prompt`。我们通过 `Fetch.enable` 拦截这些 XHR——页面的 JS 线程会一直阻塞在 XHR 上，直到我们使用代理的响应调用 `Fetch.fulfillRequest`。`prompt()` 的返回值会原样传回页面 JS。

**对话框策略** 在 `config.yaml` 中的 `browser.dialog_policy` 下配置：

| 策略 | 行为 |
|------|------|
| `must_respond`（默认） | 捕获，在快照中显示，等待显式的 `browser_dialog()` 调用。在 `browser.dialog_timeout_s`（默认 300 秒）后安全自动消除，因此有 bug 的代理不会永远卡住。 |
| `auto_dismiss` | 捕获，立即消除。代理仍然会在 `browser_state` 历史中看到对话框，但无需操作。 |
| `auto_accept` | 捕获，立即接受。用于导航具有激进的 `beforeunload` 提示的页面时。 |

**快照中的帧树（frame tree）** `browser_snapshot.frame_tree` 限制为 30 帧和 OOPIF 深度 2，以在广告繁重的页面上保持负载可控。当达到限制时，会显示 `truncated: true` 标志；需要完整帧树的代理可以使用 `browser_cdp` 和 `Page.getFrameTree`。

## 实际示例

### 填写 Web 表单

```
用户：用我的邮箱 john@example.com 在 example.com 上注册一个账户

代理工作流程：
1. browser_navigate("https://example.com/signup")
2. browser_snapshot()  → 看到带有 ref 的表单字段
3. browser_type(ref="@e3", text="john@example.com")
4. browser_type(ref="@e5", text="SecurePass123")
5. browser_click(ref="@e8")  → 点击“创建账户”
6. browser_snapshot()  → 确认成功
```

### 研究动态内容

```
用户：目前 GitHub 上最热门的仓库是哪些？

代理工作流程：
1. browser_navigate("https://github.com/trending")
2. browser_snapshot(full=true)  → 读取趋势仓库列表
3. 返回格式化结果
```

## 会话录制

自动将浏览器会话录制为 WebM 视频文件：

```yaml
browser:
  record_sessions: true  # 默认：false
```

启用后，录制会在第一次 `browser_navigate` 时自动开始，并在会话关闭时保存到 `~/.hermes/browser_recordings/`。可在本地和云（Browserbase）模式下工作。超过 72 小时的录制文件会自动清理。

## 隐蔽功能

Browserbase 提供自动隐蔽功能：

| 功能 | 默认 | 备注 |
|------|------|------|
| 基本隐蔽 | 始终开启 | 随机指纹、视口随机化、验证码解决 |
| 住宅代理 | 开启 | 通过住宅 IP 路由，以获得更好的访问 |
| 高级隐蔽 | 关闭 | 自定义 Chromium 构建，需要 Scale Plan |
| 保持连接 | 开启 | 网络中断后的会话重连 |

:::note
如果付费功能在您的计划中不可用，Hermes 会自动降级——首先禁用 `keepAlive`，然后是代理——因此即使在免费计划上浏览仍然可用。
:::

## 会话管理

- 每个任务通过 Browserbase 获得一个独立的浏览器会话
- 会话在非活动后自动清理（默认：2 分钟）
- 后台线程每 30 秒检查一次失效会话
- 进程退出时执行紧急清理，以防止孤儿会话
- 会话通过 Browserbase API（`REQUEST_RELEASE` 状态）释放

## 限制

- **基于文本的交互** — 依赖无障碍树，而非像素坐标
- **快照大小** — 大页面可能被截断或由 LLM 在 8000 字符处总结
- **会话超时** — 云会话根据提供商计划设置过期
- **成本** — 云会话消耗提供商积分；当对话结束或非活动时，会话会自动清理。使用 `/browser connect` 进行免费的本地浏览。
- **无文件下载** — 无法从浏览器下载文件