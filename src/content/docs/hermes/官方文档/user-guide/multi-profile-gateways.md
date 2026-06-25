--- frontmatter ---
---
sidebar_position: 4
---

--- body ---
# 一次运行多个网关（Gateway）

在同一台机器上，以托管服务的方式操作多个[配置文件（Profiles）](./profiles.md) —— 每个配置文件拥有自己的机器人令牌（bot tokens）、会话（sessions）和记忆（memory）。本页涵盖运维层面的注意事项：一起启动它们、查看跨配置文件的日志、防止主机休眠，以及从常见的 launchd/systemd 问题中恢复。

如果你只运行一个 Hermes 代理（Agent），则不需要本页内容 —— 基本知识请参阅[配置文件（Profiles）](./profiles.md)。

## 何时使用此功能

当你希望两个或更多 Hermes 代理同时在线时，需要此设置。常见原因：

- 一个 Telegram 机器人上的个人助手，另一个机器人上的编码代理（Coding Agent）
- 每个家庭成员一个代理，或每个 Slack 工作区一个代理
- 同一配置的沙盒（Sandbox）实例和生产（Production）实例
- 一个研究代理（Research Agent）+ 一个写作代理（Writing Agent）+ 一个定时任务驱动的机器人（Cron-driven Bot） —— 每个都有独立的记忆和技能（Skills）

每个配置文件已经拥有自己的跨平台 LaunchAgent（`ai.hermes.gateway-<name>.plist`）或 systemd 用户服务（`hermes-gateway-<name>.service`）。本指南补充了集体管理它们的模式。

## 快速开始

```bash
# 创建配置文件（一次性操作）
hermes profile create coder
hermes profile create personal-bot
hermes profile create research

# 配置每个配置文件
coder setup
personal-bot setup
research setup

# 将每个网关安装为托管服务
coder gateway install
personal-bot gateway install
research gateway install

# 启动所有网关
coder gateway start
personal-bot gateway start
research gateway start
```

就这样 —— 三个独立的代理，各自运行在自己的进程中，崩溃后和用户登录时自动重启。

## 备选方案：为所有配置文件使用一个网关（复用，Multiplexing）

上面的模型是**每个配置文件运行一个进程**。这是默认方式，也是大多数场景的正确选择。但在拥有很多配置文件的主机上，或者在容器部署中每个配置文件一个进程在运维上很沉重时，你可以改为运行**单个复用网关（multiplexing gateway）**：默认配置文件的网关成为唯一的入站进程，并为该机器上的**每个**配置文件提供消息服务。

这是**选择加入（opt-in）** 且**默认关闭**的。当关闭时，本页的任何内容都不会改变 —— 下面的所有行为都处于非激活状态。

### 何时选择复用

- 容器/VPS 部署中，N 个监督单元、N 个端口和 N 个 PID 文件成为负担。
- 有许多低流量的配置文件，每个配置文件单独运行一个进程不值得。
- 你希望只有一个东西需要启动、监控和重启。

当你需要配置文件之间严格的进程级隔离（独立内存占用、独立崩溃域、能够在不影响其他配置文件的情况下重启一个配置文件）时，请坚持使用每个配置文件一个进程。

### 如何选择加入

在**默认配置文件**（它拥有复用器）上设置标志并重启其网关：

```bash
hermes config set gateway.multiplex_profiles true
hermes gateway restart
```

或者，在默认配置文件的 `~/.hermes/config.yaml` 中：

```yaml
gateway:
  multiplex_profiles: true
```

（为了方便，该标志也接受顶层 `multiplex_profiles: true`。）下次启动时，默认网关会枚举每个配置文件，使用每个配置文件自己的凭据拉起每个配置文件已启用的平台，并将每条入站消息路由到其所属的配置文件。每次轮询时解析被路由配置文件的配置、技能、记忆、SOUL **以及供应商密钥（provider keys）** —— 凭据不会跨配置文件共享。

对于次要配置文件，你**不**需要运行 `hermes gateway start` —— 默认网关会为它们服务。请参阅下面的合约变更。

### 启用复用时会发生什么变化

启用该标志会改变一些行为。一旦标志关闭，所有这些都会恢复。

#### 1. 次要配置文件不得启动自己的网关

当复用器运行时，对命名配置文件执行 `hermes gateway start` / `run` 会产生**硬错误**，并将你指向复用器：

```
默认网关正在以配置文件复用器运行，并且已经服务于配置文件 'coder'。...
```

复用器是唯一的入站进程；第二个配置文件网关会使该配置文件的平台产生双重绑定。仅当你故意希望该配置文件有一个单独的进程时，才传递 `--force`（不建议在复用器运行时这样做）。因此，本页前面的跨配置文件生命周期包装脚本**不**在复用模式下使用 —— 你只管理默认网关。

#### 2. HTTP 入站平台通过 `/p/<profile>/` URL 前缀访问

次要配置文件的 Webhook（以及其他 HTTP 入站）流量到达默认监听器上的一个配置文件前缀下，**而不是**第二个端口：

```
# 默认配置文件
POST http://host:8644/webhooks/<route>
# "coder" 配置文件，同一个监听器
POST http://host:8644/p/coder/webhooks/<route>
```

前缀中的未知或未配置配置文件返回 `404`。由于这一个共享监听器已经以这种方式服务于每个配置文件，因此**次要配置文件不得自行启用端口绑定平台** —— 这样做是配置错误，网关会拒绝启动，并指明配置文件和平台：

```
配置文件 'coder' 启用了端口绑定平台 'webhook'，但
gateway.multiplex_profiles 已开启。... 从配置文件 'coder' 的 config.yaml 中删除 platforms.webhook
（仅在默认配置文件上配置它）。
```

此规则涵盖的端口绑定平台：`webhook`、`api_server`、`msgraph_webhook`、`feishu`、`wecom_callback`、`bluebubbles`、`sms`。**仅在默认配置文件上**配置其中任何一个；每个配置文件都可通过其 `/p/<profile>/` 前缀访问。

#### 3. 每个凭据的平台仍然需要每个配置文件自己的令牌

轮询/连接平台（Telegram、Discord、Slack、Matrix、Signal 等）在复用下工作良好，但每个启用了该平台的配置文件必须提供**自己的**机器人令牌 —— 同一个令牌不能被两个配置文件同时轮询。如果两个配置文件配置了相同的 `(平台, 令牌)`，启动时会快速失败并指出这两个配置文件（参见[令牌冲突安全性](#令牌冲突安全性) —— 规则不变，只是现在在一个进程内部强制执行）。

#### 4. 会话密钥按配置文件命名空间化

每个配置文件的会话存在于 `agent:<profile>:…` 命名空间下，这样同一平台/聊天中的两个配置文件在共享会话存储中永远不会冲突。**默认**配置文件保持历史上的 `agent:main:…` 命名空间字节不变，因此现有的默认配置文件会话不受影响 —— 无需迁移，也不会产生孤立的历史记录。

#### 5. 一个 PID/锁和一个状态表面

有一个单一的进程级 PID 和锁（复用器，在默认主目录下）。`hermes status` 报告复用器及其服务的配置文件；`hermes status -p <name>` 切分到单个配置文件。每个配置文件仍在自己的主目录下写入自己的 `runtime_status.json`，因此现有的按配置文件读取器继续工作。

#### **没有**改变的内容

按配置文件的 `.env` 凭据隔离得到保留，并且如果有更严格的倾向：配置文件的密钥从其自身作用域解析，永远不会合并到共享环境（这也意味着子进程如 MCP 服务器和看板（Kanban）工作者只看到自己配置文件的密钥）。看板、配置文件范围的技能/记忆/SOUL 以及模型路由都像单独网关一样按配置文件行为不变。

## 一次性启动、停止或重启所有网关

CLI 附带单配置文件的生命周期命令。要跨每个配置文件执行操作，可以将它们包装在 shell 循环中。将下面的代码片段放入 `~/.local/bin/hermes-gateways` 并 `chmod +x`：

```sh
#!/bin/sh
set -eu

# 随着你创建/删除配置文件，在此添加或删除配置文件名称
profiles="default coder personal-bot research"

usage() {
  echo "用法: hermes-gateways {start|stop|restart|status|list}"
}

run_for_profile() {
  profile="$1"
  action="$2"
  if [ "$profile" = "default" ]; then
    hermes gateway "$action"
  else
    hermes -p "$profile" gateway "$action"
  fi
}

action="${1:-}"
case "$action" in
  start|stop|restart|status)
    for profile in $profiles; do
      echo "==> $action $profile"
      run_for_profile "$profile" "$action"
    done
    ;;
  list)
    hermes gateway list
    ;;
  *)
    usage
    exit 2
    ;;
esac
```

然后：

```bash
hermes-gateways start      # 启动每个已配置的配置文件
hermes-gateways stop       # 停止每个已配置的配置文件
hermes-gateways restart    # 重启所有
hermes-gateways status     # 所有配置文件的状态
hermes-gateways list       # 委托给 `hermes gateway list`
```

:::tip
`default` 配置文件使用 `hermes gateway <action>`（无 `-p`）操作，而不是 `hermes -p default gateway <action>`。上面的包装器处理了两种形式。
:::

## 管理单个配置文件

每个配置文件安装的快捷命令：

```bash
coder gateway run        # 前台运行（Ctrl-C 停止）
coder gateway start      # 启动托管服务
coder gateway stop       # 停止托管服务
coder gateway restart    # 重启
coder gateway status     # 状态
coder gateway install    # 创建 LaunchAgent / systemd 单元
coder gateway uninstall  # 删除服务文件
```

这些等同于 `hermes -p coder gateway <action>` —— 如果配置文件别名不在 `PATH` 中或者你从脚本动态指定配置文件时很有用。

## 服务文件

每个配置文件安装自己的服务，具有唯一名称，因此安装不会冲突：

| 平台    | 路径                                                                 |
| ------- | -------------------------------------------------------------------- |
| macOS   | `~/Library/LaunchAgents/ai.hermes.gateway-<profile>.plist`          |
| Linux   | `~/.config/systemd/user/hermes-gateway-<profile>.service`           |

默认配置文件保持历史名称：`ai.hermes.gateway.plist` / `hermes-gateway.service`。

## 查看日志

每个配置文件写入自己的日志文件：

```bash
# 默认配置文件
tail -f ~/.hermes/logs/gateway.log
tail -f ~/.hermes/logs/gateway.error.log

# 命名配置文件
tail -f ~/.hermes/profiles/<name>/logs/gateway.log
tail -f ~/.hermes/profiles/<name>/logs/gateway.error.log
```

同时流式查看每个配置文件的日志：

```bash
tail -f ~/.hermes/logs/gateway.log ~/.hermes/profiles/*/logs/gateway.log
```

CLI 还有一个结构化的日志查看器：

```bash
hermes logs -f                  # 跟随默认配置文件
hermes -p coder logs -f         # 跟随一个配置文件
hermes logs --help              # 过滤器、级别、JSON 输出
```

## 识别实际正在运行的内容

```bash
hermes profile list             # 配置文件 + 模型 + 网关状态
hermes-gateways status          # 跨所有配置文件的完整状态
launchctl list | grep hermes    # macOS — PID 和标签
systemctl --user list-units 'hermes-gateway-*'   # Linux — 单元
```

## 编辑配置

每个配置文件的配置保存在自己的目录中：

```
~/.hermes/profiles/<name>/
├── .env              # API 密钥、机器人令牌（chmod 600）
├── config.yaml       # 模型、供应商、工具集、网关设置
└── SOUL.md           # 个性/系统提示
```

默认配置文件直接使用 `~/.hermes/`，包含相同的三个文件。

使用任何编辑器或通过 CLI 编辑它们：

```bash
hermes config set model.model anthropic/claude-sonnet-4    # 默认配置文件
coder config set model.model openai/gpt-5                  # 命名配置文件
```

编辑 `.env` 或 `config.yaml` 后，重启受影响的网关：

```bash
coder gateway restart
# 或者适用于所有：
hermes-gateways restart
```

## 保持主机唤醒

网关进程可以全天运行，但操作系统在空闲时仍会尝试睡眠。两种模式：

### macOS — `caffeinate`

`caffeinate` 是 macOS 的内置工具，运行期间阻止睡眠。无需安装。

```bash
caffeinate -dis                    # 阻止显示、空闲和系统睡眠
caffeinate -dis -t 28800           # 同上，8 小时后自动退出
caffeinate -i -w $(cat ~/.hermes/gateway.pid) &   # 默认网关运行时保持唤醒

# 持久运行：后台运行并遗忘
nohup caffeinate -dis >/dev/null 2>&1 &
disown

# 检查/停止
pmset -g assertions | grep -iE 'caffeinate|prevent|user is active'
pkill caffeinate
```

| 标志   | 效果                                                    |
| ------ | ------------------------------------------------------- |
| `-d`   | 阻止显示睡眠                                              |
| `-i`   | 阻止空闲系统睡眠（默认）                                  |
| `-m`   | 阻止磁盘睡眠                                              |
| `-s`   | 阻止系统睡眠（仅限交流供电的 Mac）                        |
| `-u`   | 模拟用户活动（阻止屏幕锁定）                              |
| `-t N` | 在 `N` 秒后自动退出                                       |
| `-w P` | 当 PID `P` 退出时退出                                     |

:::warning 合盖仍然会使 Mac 睡眠
`caffeinate` 无法覆盖 MacBook 上由硬件触发的合盖睡眠。如需合盖运行，请更改“节能器”/“电池”偏好设置或使用第三方工具。
:::

### Linux — `systemd-inhibit` 或 `loginctl`

```bash
# 在命令运行时阻止挂起
systemd-inhibit --what=idle:sleep --who=hermes --why="gateways running" \
  sleep infinity &

# 允许用户服务在注销后继续运行（推荐）
sudo loginctl enable-linger "$USER"
```

启用 linger 后，你的 systemd 用户单元（包括 `hermes-gateway-<profile>.service`）会在 SSH 断开连接和重启后继续运行。

## 令牌冲突安全性

每个配置文件必须为每个平台使用唯一的机器人令牌。如果两个配置文件共享相同的 Telegram、Discord、Slack、WhatsApp 或 Signal 令牌，第二个网关将拒绝启动，并显示命名冲突配置文件的错误。

要审计：

```bash
grep -H 'TELEGRAM_BOT_TOKEN\|DISCORD_BOT_TOKEN' \
     ~/.hermes/.env ~/.hermes/profiles/*/.env
```

## 更新代码

`hermes update` 一次性拉取最新代码，并将新捆绑的技能同步到每个配置文件：

```bash
hermes update
hermes-gateways restart
```

用户修改过的技能永远不会被覆盖。

## 故障排除

### "Could not find service in domain for user gui: 501"

你在之前的 `hermes gateway stop` 之后运行了 `hermes gateway start`。CLI 的 `stop` 执行完整的 `launchctl unload`，这会将服务从 launchd 的注册表中移除。CLI 在 `start` 时捕获此特定错误并自动重新加载 plist（`↻ launchd 作业已被卸载；正在重新加载服务定义`）。服务会正常启动。无需修复。

### 崩溃后 PID 过时

如果配置文件的网关显示 `not running`，但进程仍然存在：

```bash
ps -ef | grep "hermes_cli.*-p <profile>"
cat ~/.hermes/profiles/<profile>/gateway.pid
kill -TERM <pid>          # 优雅终止
kill -KILL <pid>          # 如果几秒后仍未终止
<profile> gateway start
```

### 强制硬重置一个服务

```bash
# macOS
launchctl unload ~/Library/LaunchAgents/ai.hermes.gateway-<profile>.plist
launchctl load   ~/Library/LaunchAgents/ai.hermes.gateway-<profile>.plist

# Linux
systemctl --user restart hermes-gateway-<profile>.service
```

### 健康检查

```bash
hermes doctor                  # 默认配置文件
hermes -p <profile> doctor     # 一个配置文件
```