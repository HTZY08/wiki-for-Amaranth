--- frontmatter ---
---
sidebar_position: 7
title: "网关内部机制"
description: "消息网关如何启动、授权用户、路由会话和传递消息"
---

--- body ---
# 网关内部机制

消息网关（messaging gateway）是一个长期运行的后台进程，通过统一架构将 Hermes 连接到 20 多个外部消息平台。

## 关键文件

| 文件 | 用途 |
|------|------|
| `gateway/run.py` | `GatewayRunner` — 主循环、斜杠命令、消息调度（大文件；请用 git 查看当前行数） |
| `gateway/session.py` | `SessionStore` — 对话持久化和会话键构建 |
| `gateway/delivery.py` | 向目标平台/频道发送出站消息 |
| `gateway/pairing.py` | 用于用户授权的 DM 配对流程 |
| `gateway/channel_directory.py` | 将聊天 ID 映射为人类可读的名称，用于 cron 投递 |
| `gateway/hooks.py` | 钩子发现、加载和生命周期事件调度 |
| `gateway/mirror.py` | 用于 `send_message` 的跨会话消息镜像 |
| `gateway/status.py` | 令牌锁管理，用于按配置文件（profile）作用域的网关实例 |
| `gateway/builtin_hooks/` | 始终注册的钩子的扩展点（未随发行版提供任何钩子） |
| `gateway/platforms/` | 平台适配器（每个消息平台一个） |

## 架构概览

```text
┌─────────────────────────────────────────────────┐
│                  GatewayRunner                  │
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Telegram │  │ Discord  │  │  Slack   │       │
│  │ Adapter  │  │ Adapter  │  │ Adapter  │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │             │             │
│       └─────────────┼─────────────┘             │
│                     ▼                           │
│              _handle_message()                  │
│                     │                           │
│         ┌───────────┼───────────┐               │
│         ▼           ▼           ▼               │
│  Slash command   AIAgent    Queue/BG            │
│    dispatch      creation   sessions            │
│                     │                           │
│                     ▼                           │
│                 SessionStore                    │
│              (SQLite persistence)               │
└───────┴─────────────┴─────────────┴─────────────┘
```

## 消息流

当来自任何平台的消息到达时：

1. **平台适配器（Platform adapter）** 接收原始事件，将其标准化为 `MessageEvent`
2. **基础适配器（Base adapter）** 检查活动会话（active session）守卫：
   - 如果该会话的代理（agent）正在运行 → 将消息加入队列，设置中断事件
   - 如果是 `/approve`、`/deny`、`/stop` → 绕过守卫（内联调度）
3. **GatewayRunner._handle_message()** 接收事件：
   - 通过 `_session_key_for_source()` 解析会话键（格式：`agent:main:{platform}:{chat_type}:{chat_id}`）
   - 检查授权（见下方授权部分）
   - 检查是否为斜杠命令 → 调度到命令处理器
   - 检查代理是否已在运行 → 拦截 `/stop`、`/status` 等命令
   - 否则 → 创建 `AIAgent` 实例并运行对话
4. **响应** 通过平台适配器发送回去

### 会话键格式

会话键编码了完整的路由上下文：

```
agent:main:{platform}:{chat_type}:{chat_id}
```

例如：`agent:main:telegram:private:123456789`

支持线程的平台（Telegram 论坛主题、Discord 线程、Slack 线程）可能将线程 ID 包含在 chat_id 部分。**切勿手动构建会话键** — 始终使用 `gateway/session.py` 中的 `build_session_key()`。

### 两级消息守卫

当代理正在运行时，传入的消息会通过两个顺序守卫：

1. **第一级 — 基础适配器**（`gateway/platforms/base.py`）：检查 `_active_sessions`。如果会话活跃，则将消息排队到 `_pending_messages` 并设置中断事件。这会在消息*到达*网关运行器（gateway runner）之前就捕获它们。

2. **第二级 — 网关运行器**（`gateway/run.py`）：检查 `_running_agents`。拦截特定命令（`/stop`、`/new`、`/queue`、`/status`、`/approve`、`/deny`）并进行相应路由。其他所有消息都会触发 `running_agent.interrupt()`。

在代理阻塞期间必须到达运行器的命令（如 `/approve`）会通过 `await self._message_handler(event)` **内联**调度 — 它们绕过后台任务系统以避免竞态条件。

## 授权

网关使用多层授权检查，按顺序评估：

1. **按平台允许所有**（例如 `TELEGRAM_ALLOW_ALL_USERS`） — 如果设置，该平台上的所有用户均被授权
2. **平台允许列表**（例如 `TELEGRAM_ALLOWED_USERS`） — 逗号分隔的用户 ID
3. **DM 配对** — 已认证用户可以通过配对码让新用户配对
4. **全局允许所有**（`GATEWAY_ALLOW_ALL_USERS`） — 如果设置，所有平台上的所有用户均被授权
5. **默认：拒绝** — 未经授权的用户被拒绝

### DM 配对流程

```text
管理员: /pair
网关: "配对码: ABC123。将该码分享给用户。"
新用户: ABC123
网关: "配对成功！您现在已获得授权。"
```

配对状态保存在 `gateway/pairing.py` 中，重启后仍然有效。

## 斜杠命令调度

网关中的所有斜杠命令都流经相同的解析管道：

1. `hermes_cli/commands.py` 中的 `resolve_command()` 将输入映射到规范名称（处理别名、前缀匹配）
2. 在 `GATEWAY_KNOWN_COMMANDS` 中检查规范名称
3. `_handle_message()` 中的处理器根据规范名称调度
4. 某些命令受配置门控（`CommandDef` 上的 `gateway_config_gate`）

### 运行中代理守卫

当代理正在处理时，禁止执行的命令会被提前拒绝：

```python
if _quick_key in self._running_agents:
    if canonical == "model":
        return "⏳ Agent is running — wait for it to finish or /stop first."
```

绕过命令（`/stop`、`/new`、`/approve`、`/deny`、`/queue`、`/status`）有特殊处理。

## 配置来源

网关从多个来源读取配置：

| 来源 | 提供的内容 |
|------|-----------|
| `~/.hermes/.env` | API 密钥、机器人令牌、平台凭据 |
| `~/.hermes/config.yaml` | 模型设置、工具配置、显示选项 |
| 环境变量 | 覆盖以上任何配置 |

与 CLI（使用带有硬编码默认值的 `load_cli_config()`）不同，网关通过 YAML 加载器直接读取 `config.yaml`。这意味着存在于 CLI 默认值字典中但不在用户配置文件中的配置键，在 CLI 和网关之间可能表现不同。

## 平台适配器

大多数消息平台作为插件适配器位于 `plugins/platforms/<name>/adapter.py` 下；少数旧适配器仍然直接位于 `gateway/platforms/` 下。所有适配器都继承自 `gateway/platforms/base.py` 中的 `BasePlatformAdapter`：

```text
plugins/platforms/                  # 插件打包的适配器（每个一个目录）
├── telegram/adapter.py     # Telegram Bot API（长轮询或 webhook）
├── discord/adapter.py      # 通过 discord.py 的 Discord 机器人
├── slack/adapter.py        # Slack Socket 模式
├── whatsapp/adapter.py     # WhatsApp Business Cloud API
├── matrix/adapter.py       # 通过 mautrix 的 Matrix（可选 E2EE）
├── mattermost/adapter.py   # Mattermost WebSocket API
├── email/adapter.py        # 通过 IMAP/SMTP 的电子邮件
├── sms/adapter.py          # 通过 Twilio 的短信
├── dingtalk/adapter.py     # 钉钉 WebSocket
├── feishu/adapter.py       # 飞书/Lark WebSocket 或 webhook
├── wecom/adapter.py        # 企业微信回调
├── line/adapter.py         # LINE 消息 API
├── teams/adapter.py        # Microsoft Teams
├── irc/adapter.py          # IRC（规范的作域锁示例）
├── homeassistant/adapter.py # Home Assistant 会话集成
└── …                       # google_chat, ntfy, photon, raft, simplex, …

gateway/platforms/                  # 核心基础 + 遗留直接适配器
├── base.py              # BasePlatformAdapter — 所有平台的共享逻辑
├── signal.py            # 通过 signal-cli REST API 的 Signal
├── weixin.py            # 通过 iLink Bot API 的微信（个人微信）
├── bluebubbles.py       # 通过 BlueBubbles macOS 服务器的 Apple iMessage
├── qqbot/               # 通过官方 API v2 的 QQ 机器人（子包）
├── yuanbao.py           # 腾讯元宝 DM/群聊适配器
├── msgraph_webhook.py   # Microsoft Graph 变更通知 webhook（Teams、Outlook 等）
├── webhook.py           # 入站/出站 webhook 适配器
└── api_server.py        # REST API 服务器适配器
```

实验性的连接器（connector）支持的平台使用 `gateway/relay/` 中的通用中继适配器，而不是直接使用平台模块。当配置了 `GATEWAY_RELAY_URL` 或 `gateway.relay_url` 时，网关注册 `relay` 平台，通过出站 WebSocket 拨号连接器，并在同一条套接字上接收 `descriptor`、`inbound` 和 `interrupt_inbound` 帧。连接器通告 `CapabilityDescriptor`；Hermes 可以通过中继发送正常的出站回复、无令牌的 `follow_up` 操作以及中断帧。源端接地的线路合约位于 [`docs/relay-connector-contract.md`](https://github.com/NousResearch/hermes-agent/blob/main/docs/relay-connector-contract.md)。

适配器实现通用接口：
- `connect()` / `disconnect()` — 生命周期管理
- `send_message()` — 出站消息投递
- `on_message()` — 入站消息标准化 → `MessageEvent`

### 令牌锁

使用唯一凭据连接的适配器在 `connect()` 中调用 `acquire_scoped_lock()`，在 `disconnect()` 中调用 `release_scoped_lock()`。这防止两个配置文件同时使用同一个机器人令牌。

## 投递路径

出站投递（`gateway/delivery.py`）处理：

- **直接回复** — 将响应发送回原始聊天
- **主页频道投递** — 将 cron 作业输出和后台结果路由到配置的主页频道
- **显式目标投递** — `send_message` 工具指定 `telegram:-1001234567890`，或包装相同工具用于 shell 脚本的 [`hermes send` CLI](/guides/pipe-script-output)
- **跨平台投递** — 投递到不同于原始消息的平台

Cron 作业的投递不会镜像到网关会话历史记录中 — 它们仅存在于自己的 cron 会话中。这是一个有意为之的设计选择，以避免消息交替违规。

## 钩子

网关钩子（Hook）是响应生命周期事件的 Python 模块：

### 网关钩子事件

| 事件 | 触发时机 |
|------|---------|
| `gateway:startup` | 网关进程启动 |
| `session:start` | 新的对话会话开始 |
| `session:end` | 会话完成或超时 |
| `session:reset` | 用户使用 `/new` 重置会话 |
| `agent:start` | 代理开始处理消息 |
| `agent:step` | 代理完成一次工具调用迭代 |
| `agent:end` | 代理完成并返回响应 |
| `command:*` | 任何斜杠命令被执行 |

钩子从 `gateway/builtin_hooks/`（一个扩展点 — 在发行版中当前为空；`_register_builtin_hooks()` 是一个空操作存根）和 `~/.hermes/hooks/`（用户安装）中发现。每个钩子是一个目录，包含 `HOOK.yaml` 清单和 `handler.py`。

## 记忆提供程序集成

当启用记忆提供程序（memory provider）插件（例如 Honcho）时：

1. 网关为每条消息创建一个带有会话 ID 的 `AIAgent`
2. `MemoryManager` 使用会话上下文初始化提供程序
3. 提供程序工具（例如 `honcho_profile`、`viking_search`）通过以下路径路由：

```text
AIAgent._invoke_tool()
  → self._memory_manager.handle_tool_call(name, args)
    → provider.handle_tool_call(name, args)
```

4. 会话结束/重置时，触发 `on_session_end()` 以进行清理和最终数据刷新

### 记忆刷新生命周期

当会话被重置、恢复或过期时：
1. 内置记忆刷新到磁盘
2. 记忆提供程序的 `on_session_end()` 钩子触发
3. 一个临时的 `AIAgent` 运行一次仅记忆的对话轮次
4. 然后上下文被丢弃或归档

## 后台维护

网关在消息处理的同时运行周期性维护：

- **Cron 定时** — 检查作业计划并触发到期的作业
- **会话过期** — 超时后清理遗弃的会话
- **记忆刷新** — 在会话过期前主动刷新记忆
- **缓存刷新** — 刷新模型列表和提供程序状态

## 进程管理

网关作为长时间运行的进程运行，通过以下方式管理：

- `hermes gateway start` / `hermes gateway stop` — 手动控制
- `systemctl`（Linux）或 `launchctl`（macOS） — 服务管理
- PID 文件位于 `~/.hermes/gateway.pid` — 按配置文件的作用域进程跟踪

**按配置文件 vs 全局**：`start_gateway()` 使用按配置文件的 PID 文件。`hermes gateway stop` 仅停止当前配置文件的网关。`hermes gateway stop --all` 使用全局 `ps aux` 扫描杀死所有网关进程（用于更新期间）。

## 相关文档

- [会话存储](./session-storage.md)
- [Cron 内部机制](./cron-internals.md)
- [ACP 内部机制](./acp-internals.md)
- [代理循环内部机制](./agent-loop.md)
- [消息网关（用户指南）](/user-guide/messaging)