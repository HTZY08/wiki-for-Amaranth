---
title: Docker
---

sidebar_position: 7
title: "Docker"
description: "在 Docker 中运行 Hermes Agent 并将 Docker 用作终端后端"
---

--- body ---

# Hermes Agent — Docker

Docker 与 Hermes Agent 的交互有两种不同的方式：

1. **在 Docker 中运行 Hermes** — 代理（Agent）本身在容器内运行（本页主要关注点）
2. **Docker 作为终端后端** — 代理（Agent）在宿主机上运行，但每个命令都在一个单一的、持久的 Docker 沙箱容器中执行，该容器在整个 Hermes 进程生命周期内跨工具调用、`/new` 和子代理（subagents）存活（参见 [配置 → Docker 后端](./configuration.md#docker-backend)）

本页涵盖选项 1。容器将所有用户数据（配置、API 密钥、会话、技能（skills）、记忆（memories））存储在宿主机挂载的单个目录 `/opt/data` 中。镜像本身是无状态的，可以通过拉取新版本进行升级而不会丢失任何配置。

## 快速入门

如果你是第一次运行 Hermes Agent，请在宿主机上创建一个数据目录并以交互方式启动容器来运行设置向导：

:::caution 避免在基于浏览器的 VPS 控制台中执行安装命令
部分 VPS 提供商（Hetzner Cloud 等）提供基于浏览器的控制台来管理主机。这些控制台会错误地传输特殊字符——`:` 可能变成 `;`，`@` 可能错误渲染，非英语键盘布局更糟——这会悄悄破坏 `docker run` 参数，例如 `-v ~/.hermes:/opt/data`、`-e KEY=value` 以及粘贴的 API 密钥/令牌。

**请改用 SSH 连接**（`ssh root@<host>`）以确保复制粘贴安全的命令输入。如果你必须使用浏览器控制台，请手动输入命令而不是粘贴，并在按 Enter 之前仔细检查结果中的每个 `:`、`@`、`=` 和 `/`。
:::

```sh
mkdir -p ~/.hermes
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent setup
```

这会进入设置向导，提示你输入 API 密钥并将其写入 `~/.hermes/.env`。你只需执行一次。强烈建议在此时为网关（gateway）设置一个聊天系统。

:::tip
在容器内部，运行 `hermes setup --portal` 一次——刷新令牌会持久化保存在挂载的 `~/.hermes` 卷中。参见 [Nous Portal](/integrations/nous-portal)。
:::

## 以网关模式运行

配置完成后，以后台持久网关（Telegram、Discord、Slack、WhatsApp 等）的方式运行容器：

```sh
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  -p 8642:8642 \
  nousresearch/hermes-agent gateway run
```

端口 8642 暴露网关（gateway）的 [兼容 OpenAI 的 API 服务器](./features/api-server.md) 和健康检查端点。如果你只使用聊天平台（Telegram、Discord 等），该端口是可选的；但如果你需要仪表板（dashboard）或外部工具访问网关，则必须暴露。

:::tip 网关（gateway）在监督下运行
在官方 Docker 镜像内部，`gateway run` **默认由 s6-overlay 自动监督**：如果网关进程崩溃，它会在几秒钟内重新启动，不会丢失容器，并且仪表板（当设置了 `HERMES_DASHBOARD=1` 时）也与之并列被监督。`gateway run` CMD 进程本身是一个 `sleep infinity` 心跳，它在 s6 管理实际网关进程的同时保持容器存活——因此 `docker stop` 仍然会干净地关闭所有内容，但 `docker logs` 会显示被监督的网关输出。

你会在 `docker logs` 中看到一行面包屑信息确认升级。若要退出该机制——并恢复之前的“网关是容器的主进程，容器退出 = 网关退出”语义——请传递 `--no-supervise` 或设置 `HERMES_GATEWAY_NO_SUPERVISE=1`。退出机制对于希望容器以网关退出码退出的 CI 冒烟测试很有用；对于生产部署，默认的监督机制严格更优。

此行为仅适用于基于 s6 的镜像。早期（基于 tini）的镜像仍然将 `gateway run` 作为前台主进程运行。
:::

:::note 网关日志的去向
请参见下面的 [日志去向](#where-the-logs-go) 部分，了解完整的路由映射（每个配置文件的网关、仪表板、启动协调器、容器范围的 `docker logs`）。
:::

:::note 无人值守网关（gateway）的工具循环硬停止
`tool_loop_guardrails.hard_stop_enabled` 设置默认为 `false`，这对于交互式 CLI 和 TUI 会话是合理的，因为用户可以看到重复的工具调用警告。在无人值守的网关或服务器部署中，仅靠警告可能无法阻止陷入重复工具调用循环的代理（Agent）。希望使用断路器行为的操作员应在其配置文件的 `config.yaml` 中显式启用硬停止：

```yaml
tool_loop_guardrails:
  hard_stop_enabled: true
  hard_stop_after:
    exact_failure: 5
    idempotent_no_progress: 5
```
:::

注意：API 服务器受 `API_SERVER_ENABLED=true` 控制。为了将其暴露给容器内 `127.0.0.1` 之外，还需要设置 `API_SERVER_HOST=0.0.0.0` 和一个 `API_SERVER_KEY`（至少 8 个字符——用 `openssl rand -hex 32` 生成）。示例：

```sh
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  -p 8642:8642 \
  -e API_SERVER_ENABLED=true \
  -e API_SERVER_HOST=0.0.0.0 \
  -e API_SERVER_KEY="$(openssl rand -hex 32)" \
  -e API_SERVER_CORS_ORIGINS='*' \
  nousresearch/hermes-agent gateway run
```

在面向互联网的机器上打开任何端口都存在安全风险。除非你了解风险，否则不应这样做。

## 运行仪表板（Dashboard）

内置的 Web 仪表板（dashboard）作为受监督的 s6-rc 服务与网关（gateway）在同一容器中一起运行。设置 `HERMES_DASHBOARD=1` 以启动它：

```sh
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  -p 8642:8642 \
  -p 9119:9119 \
  -e HERMES_DASHBOARD=1 \
  nousresearch/hermes-agent gateway run
```

仪表板由 s6 监督——如果崩溃，`s6-supervise` 会在短暂的退避后自动重启它。仪表板的标准输出/标准错误被转发到 `docker logs <container>`（无前缀；网关自己的输出现在位于每个配置文件的 s6-log 文件中——请参见下面的 [日志去向](#where-the-logs-go)——因此两个流不会冲突）。

| 环境变量 | 描述 | 默认值 |
|---------------------|-------------|---------|
| `HERMES_DASHBOARD` | 设置为 `1`（或 `true` / `yes`）以启用受监督的仪表板服务 | *（未设置——服务已注册但保持关闭）* |
| `HERMES_DASHBOARD_HOST` | 仪表板 HTTP 服务器的绑定地址 | `0.0.0.0` |
| `HERMES_DASHBOARD_PORT` | 仪表板 HTTP 服务器的端口 | `9119` |
| `HERMES_DASHBOARD_INSECURE` | **已弃用 / 无操作。** 以前绕过身份验证门；自 2026 年 6 月强化后，它不再禁用身份验证。非回环绑定始终需要身份验证提供者 | *（忽略——改为配置一个提供者）* |

容器内的仪表板默认绑定 `0.0.0.0`——否则，发布的 `-p 9119:9119` 端口将无法从宿主机访问。要将绑定限制为容器回环（用于 sidecar / 反向代理设置），请设置 `HERMES_DASHBOARD_HOST=127.0.0.1`。

当以下两个条件都为真时，仪表板的身份验证门会自动启用：

1. 绑定主机是非回环的（例如容器内默认的 `0.0.0.0`），**并且**
2. 注册了一个 `DashboardAuthProvider` 插件。

有三种内置方式来满足第二个条件：

- **用户名/密码** — 对于在可信网络或 VPN 之后的自托管 / 本地 / 家用服务器容器，这是最简单的：设置 `HERMES_DASHBOARD_BASIC_AUTH_USERNAME` + `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD`（以及用于重启稳定会话的 `HERMES_DASHBOARD_BASIC_AUTH_SECRET`）。不适合直接暴露于公共互联网。
- **OAuth（Nous Portal）** — 用于托管/公共部署：每当设置了 `HERMES_DASHBOARD_OAUTH_CLIENT_ID` 时，`dashboard_auth/nous` 提供者会激活。
- **自托管 OIDC** — 通过标准 OpenID Connect 验证你自己的身份提供者：当设置了 `HERMES_DASHBOARD_OIDC_ISSUER` + `HERMES_DASHBOARD_OIDC_CLIENT_ID` 时，`dashboard_auth/self_hosted` 提供者会激活。

无论你选择哪种，门都会在调用者访问任何受保护路由之前将其重定向到登录页面。有关所有三个提供者的详细信息，请参见 [Web 仪表板 → 身份验证](features/web-dashboard.md#authentication-gated-mode)。

如果没有注册提供者且绑定是非回环的，仪表板会在启动时**失败关闭**，并显示指向缺失环境变量的特定错误。不再有在公共绑定上未经身份验证提供仪表板的逃生通道：`HERMES_DASHBOARD_INSECURE=1` 现在是一个已弃用的无操作（它记录一条警告并忽略）。配置一个提供者，或者绑定 `HERMES_DASHBOARD_HOST=127.0.0.1` 并通过 SSH 隧道 / Tailscale 访问仪表板。

:::warning 为什么移除了 `--insecure`
未经身份验证的公共仪表板是 2026 年 6 月 MCP 配置持久化活动的入口点：互联网扫描器到达暴露的仪表板（以及 OpenAI API 服务器）并驱动代理（Agent）植入 SSH 密钥后门。现在每个非回环绑定都必须有身份验证门。对于可信 LAN / 家用服务器，捆绑的用户名/密码提供者（`HERMES_DASHBOARD_BASIC_AUTH_USERNAME` + `_PASSWORD`）是零基础设施的满足方式。
::：

将仪表板作为单独容器运行**是支持的**，前提是该容器共享宿主机的 PID 和网络命名空间（例如 `network_mode: host`，如同仓库自身的 `docker-compose.yml` 所做的那样——参见其 `dashboard` 服务）。其网关（gateway）活性检测需要与网关进程共享 PID 命名空间，因此该限制仅适用于在隔离的桥接网络容器中运行且没有共享 PID 命名空间的仪表板。

## 交互式运行（CLI 聊天）

要针对运行中的数据目录打开交互式聊天会话：

```sh
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent
```

或者，如果你已经在正在运行的容器中打开了终端（例如通过 Docker Desktop），只需运行：

```sh
/opt/hermes/.venv/bin/hermes
```

## 持久卷

`/opt/data` 卷是所有 Hermes 状态的单一数据源。它映射到宿主机的 `~/.hermes/` 目录，包含：

| 路径 | 内容 |
|------|----------|
| `.env` | API 密钥和机密 |
| `config.yaml` | 所有 Hermes 配置 |
| `SOUL.md` | 代理（Agent）个性/身份 |
| `sessions/` | 对话历史 |
| `memories/` | 持久记忆存储 |
| `skills/` | 已安装的技能（skills） |
| `home/` | 每个配置文件的 HOME，用于 Hermes 工具子进程（`git`、`ssh`、`gh`、`npm` 和技能 CLI） |
| `cron/` | 定时任务定义 |
| `hooks/` | 事件钩子 |
| `logs/` | 运行时日志 |
| `skins/` | 自定义 CLI 皮肤 |

### 不可变的安装树

在托管和发布的 Docker 镜像中，`/opt/hermes` 是已安装的应用程序树。它归 root 所有，并且对运行时 `hermes` 用户为只读，因此代理（Agent）轮次、网关（gateway）会话、仪表板（dashboard）操作以及正常的 `docker exec hermes hermes ...` 命令无法就地编辑核心源代码、捆绑的 `.venv`、`node_modules` 或 TUI 包。

所有可变的 Hermes 状态都属于 `/opt/data`：配置、`.env`、配置文件、技能（skills）、记忆（memories）、会话（sessions）、日志、仪表板上传、插件和其他用户管理的文件。该镜像还禁用了运行时 `.pyc` 写入以及 Hermes 对 `/opt/hermes` 的惰性依赖安装；发布镜像所需的可选平台依赖应烘焙到镜像中或通过新的镜像构建安装。

在托管/发布的镜像上，代理（Agent）的自我改进范围限定在 `/opt/data` 下的技能、记忆、插件和配置。安装在 `/opt/hermes` 下的核心源代码是不可变的；核心更改通过向仓库提交 PR 并通过更新镜像（而非实时编辑运行中的安装）来实现。

如果操作员需要修复或检查 `/opt/data` 之外的文件，请有意使用 root shell。`hermes` 包装程序通常会将 `docker exec hermes hermes ...` 降级为运行时用户；当你明确需要 root 语义时，设置 `HERMES_DOCKER_EXEC_AS_ROOT=1` 以进行一次性 root 调用。

在 `~` 下存储凭据的技能 CLI 必须针对子进程 HOME（而不是仅数据卷根目录）进行初始化。例如，[xurl 技能](./skills/bundled/social-media/social-media-xurl.md) 将 OAuth 状态存储在 `~/.xurl` 中；在官方 Docker 布局中，Hermes 工具调用将其读取为 `/opt/data/home/.xurl`，因此使用 `HOME=/opt/data/home` 运行手动 xurl 身份验证，并使用 `HOME=/opt/data/home xurl auth status` 进行验证。

:::warning
切勿同时针对同一数据目录运行两个 Hermes **网关（gateway）** 容器——会话文件和记忆存储未设计为支持并发写入访问。
:::

## 多配置文件支持

Hermes 支持 [多个配置文件（profiles）](../reference/profile-commands.md)——单独的 `~/.hermes/` 子目录，允许你从单个安装运行独立的代理（Agent）（不同的 SOUL、技能、记忆、会话、凭据）。**在官方 Docker 镜像内部，s6 监督树将每个配置文件视为一等监督服务**，因此推荐的部署方式是**一个容器托管所有配置文件**。

使用 `hermes profile create <name>` 创建的每个配置文件都会获得：

- 在 `/run/service/gateway-<name>/` 的一个专用 s6 服务槽，由运行时动态注册——无需重建容器。
- 崩溃时自动重启，由 `s6-supervise` 管理退避。
- 每个配置文件的轮换日志位于 `${HERMES_HOME}/logs/gateways/<name>/current`（10 个归档文件 × 每个 1 MB）。
- 跨容器重启的状态持久化：启动协调器读取每个配置文件目录中的 `gateway_state.json`，并仅为上次记录状态为 `running` 的配置文件重新启动该槽。只有你显式停止的网关（`hermes gateway stop`）会在重启后保持关闭——容器重启、镜像升级或意外退出会将记录状态保留为 `running`，因此网关会在下次启动时自动启动。

你在宿主机上使用的生命周期命令在容器内部运行方式相同：

```sh
# 创建一个配置文件——注册 gateway-<name> 的 s6 槽。
docker exec hermes hermes profile create coder

# 启动 / 停止 / 重启——调度 s6-svc；网关生命周期在 docker 重启后仍然存活。
docker exec hermes hermes -p coder gateway start
docker exec hermes hermes -p coder gateway stop
docker exec hermes hermes -p coder gateway restart

# 状态——在容器内报告 `Manager: s6 (container supervisor)`。
docker exec hermes hermes -p coder gateway status

# 删除一个配置文件——同时拆除 s6 槽。
docker exec hermes hermes profile delete coder
```

在底层，容器内的 `hermes gateway start/stop/restart` 会被拦截并路由到针对正确服务目录的 `s6-svc`；你不需要直接学习 s6 命令。要查看原始监督者状态，请使用 `/command/s6-svstat /run/service/gateway-<name>`（注意 `/command/` 仅在监督树生成的进程的 PATH 中——当从 `docker exec` 调用时，请传递绝对路径）。

### 从容器外部访问多个配置文件

两个不同的表面从外部到达配置文件的网关，它们的行为不同——不要混淆：

**Hermes Desktop（以及 Web 仪表板）。** Desktop 应用的**远程网关**连接与 `hermes dashboard` 后端（默认**端口 9119**，由 `HERMES_DASHBOARD=1` 启用）通信——*不是* OpenAI API 服务器。一个仪表板后端为**每个**共置的配置文件提供服务：应用的配置文件切换器随每个请求发送目标配置文件，后端会在磁盘上打开该配置文件的 `HERMES_HOME`。因此，对于 Desktop，你**不需要**为每个配置文件使用第二个端口或第二个连接；通过切换器，一个 `:9119` 连接即可覆盖所有配置文件。

**兼容 OpenAI 的 API 客户端（Open WebUI、LobeChat、`/v1/...`）。** 这些客户端与每个配置文件的**API 服务器**通信，该服务器绑定**每个配置文件的端口 8642**（从 `API_SERVER_PORT` / `platforms.api_server.extra.port` 解析——没有自动分配，也没有 `config.yaml`/`gateway.port` 键）。如果你希望客户端到达特定的第二个配置文件，请在该配置文件的**自身** `.env` 中为其指定一个不同的 `API_SERVER_PORT`，否则其网关也会尝试绑定 8642 并与默认配置文件冲突：

```sh
# 创建配置文件（注册其 gateway-<name> 的 s6 槽）
docker exec hermes hermes profile create work

# 将其 API 服务器指向一个空闲端口（写入配置文件自身的 .env）
cat >> /opt/data/profiles/work/.env <<'EOF'
API_SERVER_ENABLED=true
API_SERVER_PORT=8643
EOF

docker exec hermes hermes -p work gateway restart
```

将 `API_SERVER_PORT` 放在每个配置文件**自身**的 `.env` 中，永远不要放在容器范围的 `environment:` 块中——全局值会强制每个配置文件使用同一端口并导致冲突。对于桥接网络，在 `docker-compose.yml` 中发布额外端口（`- "8643:8643"`）；对于 `network_mode: host`，它已经可以在宿主机上访问。默认配置文件的 8642 连接不受影响。

### 为什么一个容器托管多个配置文件，而不是多个容器

在 s6 迁移之前，“每个配置文件一个容器”是推荐的模式，因为没有容器内监督者来管理多个网关。有了 s6 作为 PID 1，这就不再必要了，并且单容器布局在几乎所有方面都更简单：

| | 一个容器，多个配置文件 | 每个配置文件一个容器 |
|---|---|---|
| 磁盘开销 | 一个镜像，一个捆绑的 venv，一个 Playwright 缓存 | N 个镜像 / N 个缓存 |
| 内存开销 | 共享 Python 解释器缓存，共享 node_modules | 每个容器重复 |
| 配置文件创建 | `docker exec ... hermes profile create <name>`（秒级） | 新的 `docker run` 调用 + 端口分配 + 绑定挂载配置 |
| 每个配置文件的崩溃恢复 | `s6-supervise` 自动重启 | Docker 的 `--restart unless-stopped`（更慢，会杀死兄弟工作） |
| 日志 | 通过 `s6-log` 的每个配置文件轮换文件，加上容器启动审计日志 | 每个容器 `docker logs <name>`——无内置轮换 |
| 备份 | 一个 `~/.hermes` 目录 | 需要协调的 N 个目录 |

默认配置文件（`default`）总是在首次启动时注册，因此新容器开箱即用即带有一个受监督的网关。其他配置文件纯粹是运行时添加的。

### 何时确实需要单独的容器

配置文件在容器内是默认方式。仅在你有特定理由时，才为每个配置文件运行一个单独的容器：

- **每个工作负载的资源隔离**——例如，配置文件 A 中不受控制的浏览器工具会话不应导致配置文件 B 的 OOM。容器每个配置文件提供 `--memory` / `--cpus`。
- **独立的镜像固定**——不同上游镜像标签用于不同工作负载。
- **网络分段**——每个配置文件使用不同的 Docker 网络（例如一个面向客户，一个内部）。
- **合规 / 爆炸半径**——不同的凭据绝不共享 OS 级进程树。

在这些情况下，为每个配置文件声明一个服务，具有不同的 `container_name`、`volumes` 和 `ports`：

```yaml
services:
  hermes-work:
    image: nousresearch/hermes-agent:latest
    container_name: hermes-work
    restart: unless-stopped
    command: gateway run
    ports:
      - "8642:8642"
    volumes:
      - ~/.hermes-work:/opt/data

  hermes-personal:
    image: nousresearch/hermes-agent:latest
    container_name: hermes-personal
    restart: unless-stopped
    command: gateway run
    ports:
      - "8643:8642"
    volumes:
      - ~/.hermes-personal:/opt/data
```

来自[持久卷](#persistent-volumes)的警告仍然适用：永远不要同时将两个容器指向同一个 `~/.hermes` 目录。每个容器内的 s6 监督者管理自己的配置文件集；跨容器共享数据卷会损坏会话文件和记忆存储。

## 日志去向

s6 容器有四个不同的日志表面，“为什么我的网关在 `docker logs` 中什么也没显示”是一个常见的意外。速查表：

| 来源 | 去向 | 如何阅读 |
|---|---|---|
| **每个配置文件的网关**（`hermes gateway run` 以及 s6 下的每个配置文件网关） | 同时输出到两个地方：`docker logs <container>`（实时，无额外前缀）**以及** `${HERMES_HOME}/logs/gateways/<profile>/current`（轮换，带 ISO-8601 时间戳，10 个归档文件 × 每个 1 MB） | `docker logs -f hermes` 或在宿主机上使用 `tail -F ~/.hermes/logs/gateways/default/current` |
| **仪表板**（当 `HERMES_DASHBOARD=1` 时） | `docker logs <container>`（无前缀） | `docker logs -f hermes`——与网关行交错显示 |
| **启动协调器**（记录每次容器启动时恢复了哪些配置文件网关） | `${HERMES_HOME}/logs/container-boot.log`（追加式审计日志） | `tail -F ~/.hermes/logs/container-boot.log` |
| **通用 Hermes 日志**（`agent.log`、`errors.log`） | `${HERMES_HOME}/logs/`（感知配置文件） | `docker exec hermes hermes logs --follow [--level WARNING] [--session <id>]` |

两个值得了解的实际后果：

- `logs/gateways/<profile>/current` 的文件副本是在容器重启后仍然存在的内容。`docker logs` 仅保留当前容器生命周期内的输出（并且在 `docker rm` 时被清除）；轮换的文件会持久保存在绑定挂载的卷上。
- 启动协调器的审计行格式为 `<iso-timestamp> profile=<name> prior_state=<state> action=<registered|started>`，因此一个快速的 `grep profile=coder ~/.hermes/logs/container-boot.log` 可以揭示特定配置文件上次恢复的时间以及 s6 是否自动启动了它。

## 环境变量转发

API 密钥从容器内的 `/opt/data/.env` 读取。你也可以直接传递环境变量：

```sh
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  -e ANTHROPIC_API_KEY="sk-ant-..." \
  -e OPENAI_API_KEY="sk-..." \
  nousresearch/hermes-agent
```

直接 `-e` 标志会覆盖 `.env` 中的值。这对于 CI/CD 或密钥管理器集成（你不希望将密钥存储在磁盘上）非常有用。

:::note 寻找 Docker 作为**终端后端**？
本页涵盖 Hermes 本身在 Docker 中运行。如果你希望 Hermes 在 Docker 沙箱容器中执行代理（Agent）的 `terminal` / `execute_code` 调用（一个跨多个 Hermes 进程共享的长生命周期容器——参见 issue #20561），那是一个单独的配置块——`terminal.backend: docker` 加上 `terminal.docker_image`、`terminal.docker_volumes`、`terminal.docker_forward_env`、`terminal.docker_env`、`terminal.docker_run_as_host_user`、`terminal.docker_extra_args`、`terminal.docker_persist_across_processes` 和 `terminal.docker_orphan_reaper`。参见 [配置 → Docker 后端](configuration.md#docker-backend) 获取包括容器生命周期规则在内的完整集合。
:::

## Docker Compose 示例

对于同时使用网关（gateway）和仪表板（dashboard）的持久部署，`docker-compose.yaml` 很方便：

```yaml
services:
  hermes:
    image: nousresearch/hermes-agent:latest
    container_name: hermes
    restart: unless-stopped
    command: gateway run
    ports:
      - "8642:8642"   # 网关 API
      - "9119:9119"   # 仪表板（仅在设置 HERMES_DASHBOARD=1 时可达）
    volumes:
      - ~/.hermes:/opt/data
    environment:
      - HERMES_DASHBOARD=1
      # 取消注释以转发特定环境变量，而不是使用 .env 文件：
      # - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      # - OPENAI_API_KEY=${OPENAI_API_KEY}
      # - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: "2.0"
```

使用 `docker compose up -d` 启动，并使用 `docker compose logs -f` 查看日志。受监督的网关的标准输出也会被输出到卷上的 `${HERMES_HOME}/logs/gateways/<profile>/current`——请参见 [日志去向](#where-the-logs-go) 获取完整路由映射。

## 可选：Linux 桌面音频桥

Docker 中的语音模式需要两个独立的东西才能工作：Hermes 必须被允许在容器内探测音频设备，并且容器必须能够访问你的宿主音频服务器。下面的设置涵盖了 Linux 桌面（暴露与 PulseAudio 兼容的套接字，包括许多 PipeWire 设置）的宿主音频管道。

:::caution
这是一个 Linux 桌面变通方法，不是通用的 Docker Desktop 功能。当你已经有宿主音频工作并且希望在 Hermes 容器内使用 CLI 语音模式时，它很有用。如果 Hermes 仍然报告 `Running inside Docker container -- no audio devices`，请使用包含对 `PULSE_SERVER` / `PIPEWIRE_REMOTE` 的 Docker 音频探测支持的构建。
:::

首先，在 Compose 文件旁边创建一个 ALSA 配置：

```conf title="asound.conf"
pcm.!default {
    type pulse
    hint {
        show on
        description "Default ALSA Output (PulseAudio)"
    }
}

pcm.pulse {
    type pulse
}

ctl.!default {
    type pulse
}
```

然后构建一个安装了 ALSA PulseAudio 插件的小型派生镜像：

```dockerfile title="Dockerfile.audio"
FROM nousresearch/hermes-agent:latest

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends libasound2-plugins \
    && rm -rf /var/lib/apt/lists/*
```

在 Compose 中使用该镜像，并传递宿主用户的 PulseAudio 套接字和 cookie：

```yaml
services:
  hermes:
    build:
      context: .
      dockerfile: Dockerfile.audio
    image: hermes-agent-audio
    container_name: hermes
    restart: unless-stopped
    command: gateway run
    volumes:
      - ~/.hermes:/opt/data
      - /run/user/${HERMES_UID}/pulse:/run/user/${HERMES_UID}/pulse
      - ~/.config/pulse/cookie:/tmp/pulse-cookie:ro
      - ./asound.conf:/etc/asound.conf:ro
    environment:
      - HERMES_UID=${HERMES_UID}
      - HERMES_GID=${HERMES_GID}
      - XDG_RUNTIME_DIR=/run/user/${HERMES_UID}
      - PULSE_SERVER=unix:/run/user/${HERMES_UID}/pulse/native
      - PULSE_COOKIE=/tmp/pulse-cookie
```

使用宿主 UID/GID 启动它，以便容器进程可以访问每个用户的音频套接字：

```sh
export HERMES_UID="$(id -u)"
export HERMES_GID="$(id -g)"
docker compose up -d --build
```

要验证 PortAudio 在容器内看到的内容：

```sh
docker exec hermes /opt/hermes/.venv/bin/python -c "import sounddevice as sd; print(sd.query_devices())"
```

## 资源限制

Hermes 容器需要适中的资源。推荐的最低配置：

| 资源 | 最低要求 | 推荐配置 |
|----------|---------|-------------|
| 内存 | 1 GB | 2–4 GB |
| CPU | 1 核 | 2 核 |
| 磁盘（数据卷） | 500 MB | 2+ GB（随着会话/技能增长）|

浏览器自动化（Playwright/Chromium）是最消耗内存的功能。如果不需要浏览器工具，1 GB 就足够了。如果启用了浏览器工具，至少分配 2 GB。

在 Docker 中设置限制：

```sh
docker run -d \
  --name hermes \
  --restart unless-stopped \
  --memory=4g --cpus=2 \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

## Dockerfile 的作用

官方镜像基于 `debian:13.4`，包含：

- Python 3.13，依赖项从锁定文件通过 `uv sync --frozen --no-install-project` 同步，用于烘焙的额外项（`all`、`messaging`、Anthropic/Bedrock/Azure 身份、Hindsight、Matrix），然后进行 Hermes 本身的无依赖可编辑安装。
- Node.js 22 + npm（用于浏览器自动化、WhatsApp 桥、TUI/Desktop 包和工作区构建工具）
- Playwright 与 Chromium（`npx playwright install --with-deps chromium --only-shell`）
- ripgrep、ffmpeg、git 和 `xz-utils` 作为系统工具
- **`docker-cli`**——使容器内运行的代理（Agent）能够驱策宿主机的 Docker 守护进程（绑定挂载 `/var/run/docker.sock` 以选择加入），用于 `docker build`、`docker run`、容器检查等。
- **`openssh-client`**——允许从容器内使用 [SSH 终端后端](/user-guide/configuration#ssh-backend)。SSH 后端会调用系统的 `ssh` 二进制文件；没有它，在容器化安装中会静默失败。
- WhatsApp 桥（`scripts/whatsapp-bridge/`）
- **[`s6-overlay`](https://github.com/just-containers/s6-overlay) v3** 作为 PID 1（替换较旧的 `tini`）——监督仪表板和每个配置文件的网关，崩溃时自动重启，回收僵尸子进程，并转发信号。

该镜像将 `/opt/hermes` 视为运行时的不可变安装树。可选的 Python 额外项、Node 工作区和必须在 Docker 内部可用的 TUI 资产需要在镜像构建期间烘焙；运行时惰性安装被禁用，因此受监督的网关和 `docker exec hermes …` 命令不会尝试将依赖工件写回只读源树。

容器的 `ENTRYPOINT` 是 s6-overlay 的 `/init`。启动时它会：
1. 以 root 身份运行 `/etc/cont-init.d/01-hermes-setup`（= `docker/stage2-hook.sh`）：可选的 UID/GID 重新映射，修复卷所有权，首次启动时种子化 `.env` / `config.yaml` / `SOUL.md`，除非设置了 `HERMES_SKIP_CONFIG_MIGRATION=1`，否则运行非交互式配置模式迁移，同步捆绑的技能。
2. 运行 `/etc/cont-init.d/02-reconcile-profiles`（= `hermes_cli.container_boot`）：遍历 `$HERMES_HOME/profiles/<name>/`，在 `/run/service/gateway-<profile>/` 下重新创建每个配置文件的网关 s6 服务槽，并且仅自动启动那些最后记录状态为 `running` 的（参见 [每个配置文件的网关监督](#per-profile-gateway-supervision)）。
3. 启动静态的 `main-hermes` 和 `dashboard` s6-rc 服务。
4. 以主程序方式执行容器的 CMD（`/opt/hermes/docker/main-wrapper.sh`），该脚本路由用户传递给 `docker run` 的参数：
   - 无参数 → `hermes`（默认）
   - 第一个参数是 PATH 上的可执行文件（例如 `sleep`、`bash`）→ 直接执行它
   - 其他内容 → `hermes <args>`（子命令直通）
   当主程序退出时，容器以该退出码退出。

:::warning 与 s6 之前的镜像的破坏性变更
容器的 ENTRYPOINT 现在是 `/init`（s6-overlay），而不是 `/usr/bin/tini`。所有五种记录的 `docker run` 调用模式（无参数、`chat -q "…"`、`sleep infinity`、`bash`、`--tui`）与基于 tini 的镜像行为相同。如果你的下游包装程序依赖于 tini 特定的信号行为或将 `/usr/bin/tini --` 调用硬编码，请锁定到先前的镜像标签。
:::

:::warning 特权模型
除非你在命令链中保留 `/init`（或者等效地，旧的 `docker/entrypoint.sh` 包装程序，它转发到 stage2 钩子），否则不要覆盖镜像入口点。s6-overlay 的 `/init` 以 root 身份运行，以便它可以在首次启动时 `chown` 卷，然后通过 `s6-setuidgid` 降级为 `hermes` 用户，用于每个受监督的服务以及主程序。在官方镜像内部以 root 身份启动 `hermes gateway run` 默认会被拒绝，因为它可能在 `/opt/data` 中留下 root 拥有的文件，并破坏后续的仪表板或网关启动。仅在你明确接受该风险时设置 `HERMES_ALLOW_ROOT_GATEWAY=1`。
:::

### `docker exec` 自动降级为 `hermes` 用户

`docker exec hermes <cmd>` 默认在容器内以 root 身份运行，但镜像提供了一个位于 `/opt/hermes/bin/hermes`（PATH 上最早）的薄包装程序，它会检测 root 调用者并透明地通过 `s6-setuidgid hermes` 重新执行。因此，`docker exec hermes login`、`docker exec hermes profile create …`、`docker exec hermes setup` 等都以 UID 10000 写入文件——即受监督的网关可读取——无需额外的 `--user` 标志。非 root 调用者（受监督的进程本身、`docker exec --user hermes`、看板子代理容器内）会命中短路路径，直接执行 venv 二进制文件，因此在热路径上没有开销。

如果你特别需要一个保留 root 语义的 `docker exec`（诊断会话、检查仅 root 状态、root 碰巧拥有的 `/opt/data` 之外的文件），可以按调用退出：

```sh
docker exec -e HERMES_DOCKER_EXEC_AS_ROOT=1 hermes <cmd>
```

该包装程序接受 `1` / `true` / `yes`（不区分大小写）。其他任何值——包括像 `=0` 这样的拼写错误——都会落入降级路径，因此无法静默退出。如果 `s6-setuidgid` 不可用（自定义构建剥离了 s6-overlay），包装程序会拒绝以 root 身份运行并退出 126，而不是退回到历史上的陷阱（即 `docker exec hermes login` 会将 `auth.json` 写为 `root:root`，并破坏每个聊天平台消息上受监督网关的身份验证）。

### 每个配置文件的网关监督

使用 `hermes profile create <name>` 创建的每个配置文件自动获得一个 s6 监督的网关服务，注册在 `/run/service/gateway-<name>/` 下，具有跨容器重启的状态持久化自动重启。有关面向用户的工作流和生命周期命令，请参见上面的 [多配置文件支持](#multi-profile-support)。

**与 s6 之前镜像相比的监督优势：**

- 网关崩溃由 `s6-supervise` 在大约 1 秒退避后自动重启。
- 仪表板（当使用 `HERMES_DASHBOARD=1` 启用时）在同一监督树上被监督，并得到相同的自动重启处理。
- `docker restart`、镜像升级（`docker compose up -d --force-recreate`）和意外退出会保留正在运行的网关：cont-init 协调器读取 `$HERMES_HOME/profiles/<name>/gateway_state.json`，如果最后记录的状态是 `running`，则重新启动该槽。只有显式的 `hermes gateway stop` 会记录 `stopped` 并保持网关在重启后关闭；容器/s6 在重启或升级时发送的 SIGTERM 被视为“仍在运行”并自动启动。
- 每个配置文件的网关日志持久保存在 `$HERMES_HOME/logs/gateways/<profile>/current`（由 `s6-log` 轮换），协调器的操作在每次启动时追加到 `$HERMES_HOME/logs/container-boot.log`。请参见 [日志去向](#where-the-logs-go) 获取完整路由映射。

容器内的 `hermes status` 报告 `Manager: s6 (container supervisor)`。使用 `/command/s6-svstat /run/service/gateway-<name>` 查看原始监督者视图（注意 `/command/` 仅在监督树进程的 PATH 上；从 `docker exec` 调用时传递绝对路径）。

## 升级

拉取最新镜像并重新创建容器。你的数据目录会被保留，并且容器在启动网关（gateway）之前会对挂载的 `$HERMES_HOME/config.yaml` 运行非交互式配置模式迁移。当需要迁移时，Hermes 会先编写带有时间戳的备份到 `config.yaml` 和 `.env` 旁边。

```sh
docker pull nousresearch/hermes-agent:latest
docker rm -f hermes
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

或者使用 Docker Compose：

```sh
docker compose pull
docker compose up -d
```

只有在需要在新镜像重写之前手动检查或迁移持久配置时，才设置 `HERMES_SKIP_CONFIG_MIGRATION=1`。

## 技能（Skills）和凭据文件

当使用 Docker 作为执行环境（不是上述方法，而是当代理（Agent）在 Docker 沙箱内运行命令时——参见 [配置 → Docker 后端](./configuration.md#docker-backend)），Hermes 会重用单个长生命周期容器进行所有工具调用，并自动将技能目录（`~/.hermes/skills/`）和技能声明的任何凭据文件作为只读卷绑定挂载到该容器中。技能脚本、模板和引用在沙箱内可用，无需手动配置，并且由于该容器在 Hermes 进程的整个生命周期内持续存在，你安装的任何依赖项或写入的任何文件都会保留到下一个工具调用。

SSH 和 Modal 后端也会发生相同的同步——技能和凭据文件在每条命令之前通过 rsync 或 Modal 挂载 API 上传。

## 在容器中安装更多工具

官方镜像附带了一组精选的工具（参见 [Dockerfile 的作用](#what-the-dockerfile-does)），但并非代理（Agent）可能需要的每个工具都已预安装。有五种推荐的方法，按努力程度和持久性递增排列。

### npm 或 Python 工具——使用 `npx` 或 `uvx`

对于任何发布到 npm 或 PyPI 的工具，指示 Hermes 通过 `npx`（npm）或 `uvx`（Python）运行它，并将该命令记住在其持久记忆（memory）中。如果工具需要配置文件或凭据，指示它将其放在 `/opt/data` 下（例如 `/opt/data/<tool>/config.yaml`）。

依赖项按需获取并缓存在容器的生命周期内。写在 `/opt/data` 下的配置会在容器重启后继续存在，因为它位于绑定挂载的宿主机目录上。包缓存在 `docker rm` 后会重建，但 `npx` 和 `uvx` 会在下次工具运行时透明地重新获取。

### 其他工具（apt 包、二进制文件）——安装并记住

对于 npm 或 PyPI 之外的任何工具——`apt` 包、预编译的二进制文件、镜像中尚未包含的语言运行时——指示 Hermes 如何安装它（例如 `apt-get update && apt-get install -y <package>`）并告诉它记住安装命令。该工具在容器剩余生命周期内持续存在，并且 Hermes 会在下次需要该工具时在容器重启后重新运行安装命令。

这对于安装速度快且偶尔使用的工具非常适用。对于经常使用的工具，请优先选择下一种方法。

### 持久安装——构建派生镜像

当某个工具必须在每次容器启动时立即可用且无需重新安装延迟时，可以构建一个继承自 `nousresearch/hermes-agent` 的新镜像，并在一个层中安装该工具：

```dockerfile
FROM nousresearch/hermes-agent:latest

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends <your-package> \
    && rm -rf /var/lib/apt/lists/*
USER hermes
```

构建它并替换官方镜像使用：

```sh
docker build -t my-hermes:latest .
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  -p 8642:8642 \
  my-hermes:latest gateway run
```

入口点脚本和 `/opt/data` 语义保持不变地被继承，因此本页其余部分仍然适用。记得在拉取更新的上游 `nousresearch/hermes-agent` 时重建镜像。

### 复杂工具或多服务堆栈——运行 sidecar 容器

对于带有自己服务的工具（数据库、Web 服务器、队列、无头浏览器集群）或太重而无法放在 Hermes 容器中的工具，将其作为在共享 Docker 网络上的单独容器运行。Hermes 通过容器名称到达 sidecar，就像到达本地推理服务器一样（参见 [连接到本地推理服务器](#connecting-to-local-inference-servers-vllm-ollama-etc)）。

```yaml
services:
  hermes:
    image: nousresearch/hermes-agent:latest
    container_name: hermes
    restart: unless-stopped
    command: gateway run
    ports:
      - "8642:8642"
    volumes:
      - ~/.hermes:/opt/data
    networks:
      - hermes-net

  my-tool:
    image: example/my-tool:latest
    container_name: my-tool
    restart: unless-stopped
    networks:
      - hermes-net

networks:
  hermes-net:
    driver: bridge
```

从 Hermes 容器内部，sidecar 可通过 `http://my-tool:<port>` 访问（或任何其服务的协议）。这种模式保持每个服务的生命周期、资源限制和升级节奏独立，并避免用仅一个工具需要的依赖项膨胀 Hermes 镜像。

### 广泛有用的工具——提出问题或拉取请求

如果某个工具很可能对大多数 Hermes Agent 用户有用，请考虑向上游贡献，而不是在私有派生镜像中携带它。在 [hermes-agent 仓库](https://github.com/NousResearch/hermes-agent) 中提出问题或拉取请求，描述该工具及其用例。捆绑到官方镜像中的工具将使每个用户受益，并避免下游分支的维护开销。

## 连接到本地推理服务器（vLLM、Ollama 等）

当在 Docker 中运行 Hermes 并且你的推理服务器（vLLM、Ollama、text-generation-inference 等）也运行在宿主机或其他容器中时，网络连接需要额外注意。

### Docker Compose（推荐）

将两个服务放在同一个 Docker 网络上。这是最可靠的方法：

```yaml
services:
  vllm:
    image: vllm/vllm-openai:latest
    container_name: vllm
    command: >
      --model Qwen/Qwen2.5-7B-Instruct
      --served-model-name my-model
      --host 0.0.0.0
      --port 8000
    ports:
      - "8000:8000"
    networks:
      - hermes-net
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]

  hermes:
    image: nousresearch/hermes-agent:latest
    container_name: hermes
    restart: unless-stopped
    command: gateway run
    ports:
      - "8642:8642"
    volumes:
      - ~/.hermes:/opt/data
    networks:
      - hermes-net

networks:
  hermes-net:
    driver: bridge
```

然后在你的 `~/.hermes/config.yaml` 中，使用**容器名称**作为主机名：

```yaml
model:
  provider: custom
  model: my-model
  base_url: http://vllm:8000/v1
  api_key: "none"
```

:::tip 关键点
- 使用**容器名称**（`vllm`）作为主机名——而不是 `localhost` 或 `127.0.0.1`，它们指的是 Hermes 容器本身。
- `model` 值必须与你传递给 vLLM 的 `--served-model-name` 匹配。
- 将 `api_key` 设置为任何非空字符串（vLLM 需要该标头但默认不验证它）。
- 不要在 `base_url` 中包含尾部斜杠。
:::

### 独立 Docker 运行（无 Compose）

如果你的推理服务器直接在宿主机上（不在 Docker 中），在 macOS/Windows 上使用 `host.docker.internal`，或在 Linux 上使用 `--network host`：

**macOS / Windows：**

```sh
docker run -d \
  --name hermes \
  -v ~/.hermes:/opt/data \
  -p 8642:8642 \
  nousresearch/hermes-agent gateway run
```

```yaml
# config.yaml
model:
  provider: custom
  model: my-model
  base_url: http://host.docker.internal:8000/v1
  api_key: "none"
```

**Linux（主机网络）：**

```sh
docker run -d \
  --name hermes \
  --network host \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

```yaml
# config.yaml
model:
  provider: custom
  model: my-model
  base_url: http://127.0.0.1:8000/v1
  api_key: "none"
```

:::warning 使用 `--network host` 时，`-p` 标志被忽略——所有容器端口都直接暴露在宿主机上。
:::

### 验证连接

从 Hermes 容器内部，确认推理服务器可达：

```sh
docker exec hermes curl -s http://vllm:8000/v1/models
```

你应该看到列出你提供的模型的 JSON 响应。如果失败，请检查：

1. 两个容器是否在同一个 Docker 网络上（`docker network inspect hermes-net`）
2. 推理服务器是否在监听 `0.0.0.0`，而不是 `127.0.0.1`
3. 端口号是否匹配

### Ollama

Ollama 的工作方式相同。如果 Ollama 在宿主机上运行，请使用 `host.docker.internal:11434`（macOS/Windows）或 `127.0.0.1:11434`（Linux 使用 `--network host`）。如果 Ollama 在自己的容器中运行在同一个 Docker 网络上：

```yaml
model:
  provider: custom
  model: llama3
  base_url: http://ollama:11434/v1
  api_key: "none"
```

## 故障排除

### 容器立即退出

检查日志：`docker logs hermes`。常见原因：
- `.env` 文件缺失或无效——先以交互方式运行完成设置
- 如果以暴露端口方式运行，则端口冲突

### “Permission denied” 错误

容器的 stage2 钩子通过每个受监督服务内的 `s6-setuidgid` 将特权降级到非 root 的 `hermes` 用户（UID 10000）。如果你的宿主机 `~/.hermes/` 由不同的 UID 拥有，请设置 `HERMES_UID`/`HERMES_GID`——或其别名 `PUID`/`PGID`，以与 LinuxServer.io 和 NAS 镜像兼容——以匹配你的宿主机用户，或者确保数据目录可写：

```sh
chmod -R 755 ~/.hermes
```

在 NAS（UGOS、Synology、unRAID）上，数据目录通常是宿主 UID 拥有的**绑定挂载**，容器无法 `chown`。设置 `PUID`/`PGID`（或 `HERMES_UID`/`HERMES_GID`）为该宿主机用户，以便运行时以挂载的所有者身份运行，而不是 UID 10000：

```sh
docker run -d \
  --name hermes \
  -e PUID=1000 -e PGID=10 \
  -v /volume1/docker/hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

`docker exec hermes <cmd>` 会自动降级到 UID 10000——详见 [`docker exec` 自动降级为 `hermes` 用户](#docker-exec-automatically-drops-to-the-hermes-user) 以及每次调用的退出选项。

### 浏览器工具无法工作

Playwright 需要共享内存。在 Docker 运行命令中添加 `--shm-size=1g`：

```sh
docker run -d \
  --name hermes \
  --shm-size=1g \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

### 网络问题后网关（gateway）无法重新连接

`--restart unless-stopped` 标志可处理大多数瞬时故障。如果网关卡住，请重启容器：

```sh
docker restart hermes
```

### 检查容器健康状态

```sh
docker logs --tail 50 hermes          # 最近的日志
docker run -it --rm nousresearch/hermes-agent:latest version     # 验证版本
docker stats hermes                    # 资源使用情况
```