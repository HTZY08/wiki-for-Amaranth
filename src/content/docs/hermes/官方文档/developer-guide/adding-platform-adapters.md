---
title: Adding Platform Adapters
---

# 添加平台适配器

本指南介绍如何向 Hermes 网关添加新的消息平台。平台适配器将 Hermes 连接到外部消息服务（Telegram、Discord、WeCom 等），以便用户通过该服务与代理交互。

:::tip
有两种添加平台的方式：
- **插件**（推荐用于社区/第三方）：将插件目录放入 `~/.hermes/plugins/` — 无需修改核心代码。请参见下文中的[插件路径](#plugin-path-recommended)。
- **内置**：修改代码、配置和文档中的 20 多个文件。请参见下文中的[内置检查清单](#step-by-step-checklist-built-in-path)。
:::

## 架构概览

```
用户 ↔ 消息平台 ↔ 平台适配器 ↔ 网关运行器 ↔ AIAgent
```

每个适配器都扩展自 `gateway/platforms/base.py` 中的 `BasePlatformAdapter`，并实现：

- **`connect()`** — 建立连接（WebSocket、长轮询、HTTP 服务器等）*(抽象)*
- **`disconnect()`** — 清理关闭 *(抽象)*
- **`send()`** — 向聊天发送文本消息 *(抽象)*
- **`send_typing()`** — 显示输入指示器（可选覆盖）
- **`get_chat_info()`** — 返回聊天元数据（可选覆盖）

入站消息由适配器接收，并通过 `self.handle_message(event)` 转发，基类将其路由到网关运行器。

## 插件路径（推荐）

插件系统允许您在不修改任何 Hermes 核心代码的情况下添加平台适配器。您的插件是一个包含两个文件的目录：

```
~/.hermes/plugins/my-platform/
  plugin.yaml      # 插件元数据
  adapter.py       # 适配器类 + register() 入口点
```

### plugin.yaml

插件元数据。`requires_env` 和 `optional_env` 块会自动填充 `hermes config` UI 条目（请参见下文[在 Hermes 配置中展示环境变量](#surfacing-env-vars-in-hermes-config)）。

```yaml
name: my-platform
label: My Platform
kind: platform
version: 1.0.0
description: My custom messaging platform adapter
author: Your Name
requires_env:
  - MY_PLATFORM_TOKEN          # 裸字符串也可以
  - name: MY_PLATFORM_CHANNEL  # 或使用富字典以获得更好的用户体验
    description: "Channel to join"
    prompt: "Channel"
    password: false
optional_env:
  - name: MY_PLATFORM_HOME_CHANNEL
    description: "Default channel for cron delivery"
    password: false
```

### adapter.py

```python
import os
from gateway.platforms.base import (
    BasePlatformAdapter, SendResult, MessageEvent, MessageType,
)
from gateway.config import Platform, PlatformConfig


class MyPlatformAdapter(BasePlatformAdapter):
    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform("my_platform"))
        extra = config.extra or {}
        self.token = os.getenv("MY_PLATFORM_TOKEN") or extra.get("token", "")

    async def connect(self) -> bool:
        # Connect to the platform API, start listeners
        self._mark_connected()
        return True

    async def disconnect(self) -> None:
        self._mark_disconnected()

    async def send(self, chat_id, content, reply_to=None, metadata=None):
        # Send message via platform API
        return SendResult(success=True, message_id="...")

    async def get_chat_info(self, chat_id):
        return {"name": chat_id, "type": "dm"}


def check_requirements() -> bool:
    return bool(os.getenv("MY_PLATFORM_TOKEN"))


def validate_config(config) -> bool:
    extra = getattr(config, "extra", {}) or {}
    return bool(os.getenv("MY_PLATFORM_TOKEN") or extra.get("token"))


def _env_enablement() -> dict | None:
    token = os.getenv("MY_PLATFORM_TOKEN", "").strip()
    channel = os.getenv("MY_PLATFORM_CHANNEL", "").strip()
    if not (token and channel):
        return None
    seed = {"token": token, "channel": channel}
    home = os.getenv("MY_PLATFORM_HOME_CHANNEL")
    if home:
        seed["home_channel"] = {"chat_id": home, "name": "Home"}
    return seed


def register(ctx):
    """Plugin entry point — called by the Hermes plugin system."""
    ctx.register_platform(
        name="my_platform",
        label="My Platform",
        adapter_factory=lambda cfg: MyPlatformAdapter(cfg),
        check_fn=check_requirements,
        validate_config=validate_config,
        required_env=["MY_PLATFORM_TOKEN"],
        install_hint="pip install my-platform-sdk",
        # Env-driven auto-configuration — seeds PlatformConfig.extra from
        # env vars before adapter construction. See "Env-Driven Auto-
        # Configuration" section below.
        env_enablement_fn=_env_enablement,
        # Cron home-channel delivery support. Lets deliver=my_platform cron
        # jobs route without editing cron/scheduler.py. See "Cron Delivery"
        # section below.
        cron_deliver_env_var="MY_PLATFORM_HOME_CHANNEL",
        # Per-platform user authorization env vars
        allowed_users_env="MY_PLATFORM_ALLOWED_USERS",
        allow_all_env="MY_PLATFORM_ALLOW_ALL_USERS",
        # Message length limit for smart chunking (0 = no limit)
        max_message_length=4000,
        # LLM guidance injected into system prompt
        platform_hint=(
            "You are chatting via My Platform. "
            "It supports markdown formatting."
        ),
        # Display
        emoji="💬",
    )

    # Optional: register platform-specific tools
    ctx.register_tool(
        name="my_platform_search",
        toolset="my_platform",
        schema={...},
        handler=my_search_handler,
    )
```

### 配置

用户在 `config.yaml` 中配置平台：

```yaml
gateway:
  platforms:
    my_platform:
      enabled: true
      extra:
        token: "..."
        channel: "#general"
```

或通过环境变量（适配器在 `__init__` 中读取）。

### 插件系统自动处理的内容

当您调用 `ctx.register_platform()` 时，以下集成点会自动处理 — 无需更改核心代码：

| 集成点 | 工作原理 |
|---|---|
| 网关适配器创建 | 在内置 if/elif 链之前检查注册表 |
| 配置解析 | `Platform._missing_()` 接受任何平台名称 |
| 已连接平台验证 | 调用注册表的 `validate_config()` |
| 用户授权 | 检查 `allowed_users_env` / `allow_all_env` |
| 仅环境变量自动启用 | `env_enablement_fn` 为 `PlatformConfig.extra` + `home_channel` 提供种子值 |
| YAML 配置桥接 | `apply_yaml_config_fn` 将 `config.yaml` 键转换为环境变量 / extras |
| Cron 投递 | `cron_deliver_env_var` 使 `deliver=<name>` 生效 |
| `hermes config` UI 条目 | `plugin.yaml` 中的 `requires_env` / `optional_env` 自动填充 |
| send_message 工具 | 通过活动的网关适配器路由 |
| Webhook 跨平台投递 | 检查注册表中已知的平台 |
| `/update` 命令访问 | `allow_update_command` 标志 |
| 频道目录 | 枚举中包括插件平台 |
| 系统提示提示 | `platform_hint` 注入到 LLM 上下文中 |
| 消息分块 | `max_message_length` 用于智能分割 |
| PII 编辑 | `pii_safe` 标志 |
| `hermes status` | 使用 `(plugin)` 标签显示插件平台 |
| `hermes gateway setup` | 插件平台出现在设置菜单中 |
| `hermes tools` / `hermes skills` | 插件平台在按平台配置中 |
| 令牌锁定（多配置文件） | 在 `connect()` 中使用 `acquire_scoped_lock()` |
| 孤立配置警告 | 当插件缺失时，显示描述性日志 |

## 环境变量驱动的自动配置

大多数用户通过将环境变量放入 `~/.hermes/.env` 来设置平台，而不是编辑 `config.yaml`。`env_enablement_fn` 钩子允许您的插件在适配器构建之前收集这些环境变量，因此 `hermes gateway status`、`get_connected_platforms()` 和 cron 投递无需实例化平台 SDK 即可看到正确的状态。

```python
def _env_enablement() -> dict | None:
    """Seed PlatformConfig.extra from env vars.

    Called by the platform registry during load_gateway_config().
    Return None when the platform isn't minimally configured — the
    caller then skips auto-enabling. Return a dict to seed extras.

    The special 'home_channel' key is extracted and becomes a proper
    HomeChannel dataclass on the PlatformConfig; every other key is
    merged into PlatformConfig.extra.
    """
    token = os.getenv("MY_PLATFORM_TOKEN", "").strip()
    channel = os.getenv("MY_PLATFORM_CHANNEL", "").strip()
    if not (token and channel):
        return None
    seed = {"token": token, "channel": channel}
    home = os.getenv("MY_PLATFORM_HOME_CHANNEL")
    if home:
        seed["home_channel"] = {
            "chat_id": home,
            "name": os.getenv("MY_PLATFORM_HOME_CHANNEL_NAME", "Home"),
        }
    return seed


def register(ctx):
    ctx.register_platform(
        name="my_platform",
        label="My Platform",
        adapter_factory=lambda cfg: MyPlatformAdapter(cfg),
        check_fn=check_requirements,
        validate_config=validate_config,
        env_enablement_fn=_env_enablement,
        # ... other fields
    )
```


## YAML→环境变量 配置桥接

一些用户更喜欢在 `config.yaml` 中设置键（`my_platform.require_mention`、`my_platform.allowed_channels` 等）而不是使用环境变量。`apply_yaml_config_fn` 钩子允许您的插件处理此转换，而无需强制核心 `gateway/config.py` 知道您平台的 YAML 模式。

```python
import os

def _apply_yaml_config(yaml_cfg: dict, platform_cfg: dict) -> dict | None:
    """Translate config.yaml `my_platform:` keys into env vars / extras.

    yaml_cfg     — the full top-level parsed config.yaml dict
    platform_cfg — the platform's own sub-dict (yaml_cfg.get("my_platform", {}))

    May mutate os.environ directly (use `not os.getenv(...)` guards to
    preserve env > YAML precedence) and/or return a dict to merge into
    PlatformConfig.extra. Return None or {} for no extras.
    """
    if "require_mention" in platform_cfg and not os.getenv("MY_PLATFORM_REQUIRE_MENTION"):
        os.environ["MY_PLATFORM_REQUIRE_MENTION"] = str(platform_cfg["require_mention"]).lower()
    allowed = platform_cfg.get("allowed_channels")
    if allowed is not None and not os.getenv("MY_PLATFORM_ALLOWED_CHANNELS"):
        if isinstance(allowed, list):
            allowed = ",".join(str(v) for v in allowed)
        os.environ["MY_PLATFORM_ALLOWED_CHANNELS"] = str(allowed)
    return None  # nothing extra to merge into PlatformConfig.extra

def register(ctx):
    ctx.register_platform(
        name="my_platform",
        ...,
        apply_yaml_config_fn=_apply_yaml_config,
    )
```

该钩子在 `load_gateway_config()` 期间被调用，在通用共享键循环（处理常见键如 `unauthorized_dm_behavior`、`notice_delivery`、`reply_prefix`、`require_mention` 等）之后，在 `_apply_env_overrides()` 之前，因此您的插件只需要桥接**平台特定**的键。

钩子抛出的异常会被吞掉并记录在调试级别 — 行为异常的插件绝不会中止网关配置加载。


## Cron 投递

为了让 `deliver=my_platform` 的 cron 作业路由到已配置的主频道，将 `cron_deliver_env_var` 设置为保存默认聊天/房间/频道 ID 的环境变量名称：

```python
ctx.register_platform(
    name="my_platform",
    ...
    cron_deliver_env_var="MY_PLATFORM_HOME_CHANNEL",
)
```

调度器在解析 `deliver=my_platform` 作业的主目标时读取此环境变量，并且在 `_KNOWN_DELIVERY_PLATFORMS` 样式的检查中也会将该平台视为有效的 cron 目标。如果您的 `env_enablement_fn` 提供了 `home_channel` 字典（见上文），则它优先 — `cron_deliver_env_var` 是在环境变量提供之前运行的 cron 作业的后备方案。

### 进程外 Cron 投递

`cron_deliver_env_var` 使您的平台成为被认可的 `deliver=` 目标。当 cron 作业在与网关不同的进程中运行时（即 `hermes cron run` 与 `hermes gateway` 分开运行），要使实际发送成功，请注册一个 `standalone_sender_fn`：

```python
async def _standalone_send(
    pconfig,
    chat_id,
    message,
    *,
    thread_id=None,
    media_files=None,
    force_document=False,
):
    """Open an ephemeral connection / acquire a fresh token, send, and close."""
    # ... open connection, send message, return result ...
    return {"success": True, "message_id": "..."}
    # or {"error": "..."}

ctx.register_platform(
    name="my_platform",
    ...
    cron_deliver_env_var="MY_PLATFORM_HOME_CHANNEL",
    standalone_sender_fn=_standalone_send,
)
```

为什么需要这个钩子：内置平台（Telegram、Discord、Slack 等）在 `tools/send_message_tool.py` 中提供了直接的 REST 辅助函数，因此 cron 可以在不保持网关在同一进程中的情况下投递。插件平台历史上依赖于 `_gateway_runner_ref()`，该函数在网关进程之外返回 `None`，因此如果没有 `standalone_sender_fn`，cron 端的发送会失败，并提示 `No live adapter for platform '<name>'`。

该函数接收与活动适配器相同的 `pconfig` 和 `chat_id`，以及可选的 `thread_id`、`media_files` 和 `force_document` 关键字参数。返回 `{"success": True, "message_id": ...}` 被视为成功投递；返回 `{"error": "..."}` 会将消息显示在 cron 的 `delivery_errors` 中。函数内抛出的异常会被调度器捕获并报告为 `Plugin standalone send failed: <reason>`。参考实现见 `plugins/platforms/{irc,teams,google_chat}/adapter.py`。

## 在 hermes config 中展示环境变量

`hermes_cli/config.py` 在导入时扫描 `plugins/platforms/*/plugin.yaml`，并从 `requires_env` 和（可选的）`optional_env` 块自动填充 `OPTIONAL_ENV_VARS`。使用富字典形式可以提供适当的描述、提示、密码标志和 URL — CLI 设置 UI 会自动拾取它们。

```yaml
# plugins/platforms/my_platform/plugin.yaml
name: my_platform-platform
label: My Platform
kind: platform
version: 1.0.0
description: >
  My Platform gateway adapter for Hermes Agent.
author: Your Name
requires_env:
  - name: MY_PLATFORM_TOKEN
    description: "Bot API token from the My Platform console"
    prompt: "My Platform bot token"
    url: "https://my-platform.example.com/bots"
    password: true
  - name: MY_PLATFORM_CHANNEL
    description: "Channel to join (e.g. #hermes)"
    prompt: "Channel"
    password: false
optional_env:
  - name: MY_PLATFORM_HOME_CHANNEL
    description: "Default channel for cron delivery (defaults to MY_PLATFORM_CHANNEL)"
    prompt: "Home channel (or empty)"
    password: false
  - name: MY_PLATFORM_ALLOWED_USERS
    description: "Comma-separated user IDs allowed to talk to the bot"
    prompt: "Allowed users (comma-separated)"
    password: false
```

**支持的字典键：** `name`（必需）、`description`、`prompt`、`url`、`password`（布尔值；当省略时，从 `*_TOKEN` / `*_SECRET` / `*_KEY` / `*_PASSWORD` / `*_JSON` 后缀自动检测）、`category`（默认为 `"messaging"`）。

裸字符串条目（`- MY_PLATFORM_TOKEN`）仍然有效 — 它们会从插件的 `label` 自动派生出一个通用描述。如果 `OPTIONAL_ENV_VARS` 中已存在同名的硬编码条目，则该条目优先（向后兼容）；`plugin.yaml` 形式作为后备。

## 平台特定的慢速 LLM 用户体验

某些平台具有约束条件，会改变慢速 LLM 响应应如何呈现的方式：

- **LINE** 发出一个一次性*回复令牌*，在入站事件后大约 60 秒过期。使用该令牌回复是免费的；回退到按量计费的推送 API 则不是。如果 LLM 在截止时间前未完成，选择是“消耗付费推送配额”或“在回复令牌过期前做一些更巧妙的事情。”
- **WhatsApp** 在 24 小时后将会话标记为不活跃，之后只接受模板消息。
- **SMS** 没有输入指示器或渐进更新的概念 — 长响应看起来就像机器人离线了。

这些是基类 `BasePlatformAdapter` 无法预见的真实约束。插件界面特意留出了空间，允许适配器在基本输入循环之上分层实现平台特定的用户体验，而无需扩展 kwargs 列表。

### 模式：子类化 `_keep_typing` 以分层飞行中用户体验

`BasePlatformAdapter._keep_typing` 是输入指示器的心跳 — 它在 LLM 生成时作为后台任务运行，并在响应交付时被取消。要在阈值处分层平台特定行为（例如在 45 秒时发送“仍在思考”气泡），在适配器中覆盖 `_keep_typing`，并在 `super()._keep_typing()` 旁边调度您自己的任务，并在 `finally` 中将其拆除：

```python
class LineAdapter(BasePlatformAdapter):
    async def _keep_typing(self, chat_id: str, *args, **kwargs) -> None:
        if self.slow_response_threshold <= 0:
            await super()._keep_typing(chat_id, *args, **kwargs)
            return

        async def _fire_at_threshold() -> None:
            try:
                await asyncio.sleep(self.slow_response_threshold)
            except asyncio.CancelledError:
                raise
            # Platform-specific work here — for LINE, send a Template
            # Buttons "Get answer" bubble using the cached reply token
            # so the user can fetch the cached response later via a
            # fresh (free) reply token from the postback callback.
            await self._send_slow_response_button(chat_id)

        side_task = asyncio.create_task(_fire_at_threshold())
        try:
            await super()._keep_typing(chat_id, *args, **kwargs)
        finally:
            if not side_task.done():
                side_task.cancel()
                try:
                    await side_task
                except (asyncio.CancelledError, Exception):
                    pass
```

关键点：

- **始终 `await super()._keep_typing(...)`。** 输入心跳本身是有用的 — 不要替换它，而是在其之上分层。
- **在 `finally` 中拆除辅助任务。** 当 LLM 完成（或 `/stop` 取消运行）时，网关取消输入任务。您的辅助任务也必须观察该取消，否则它会持续存在并可能在响应交付后触发。
- **与 `interrupt_session_activity` 配对** 以解决用户发出 `/stop` 时的任何孤立用户体验状态。对于 LINE，这意味着将回传缓存条目从 `PENDING` 转换为 `ERROR`，以便持久的“获取答案”按钮发送“运行已被中断”消息而不是循环执行。

### 模式：子类化 `send` 以通过缓存路由而不是立即发送

如果您的慢速响应用户体验将响应缓存起来以供以后检索（LINE 的回传流程），您的 `send` 覆盖需要识别三种模式：

1. **此聊天的待处理回传处于活动状态** → 将响应缓存在 request_id 下，不发送任何可见内容。
2. **系统忙碌确认**（`⚡ Interrupting`、`⏳ Queued`、`⏩ Steered`）→ 绕过缓存并可见地发送，以便用户看到网关对其输入的响应。
3. **正常响应** → 照常通过回复令牌或推送发送。

```python
async def send(self, chat_id: str, content: str, **kw) -> SendResult:
    if _is_system_bypass(content):
        return await self._send_text_chunks(chat_id, content, force_push=False)
    pending_rid = self._pending_buttons.get(chat_id)
    if pending_rid:
        self._cache.set_ready(pending_rid, content)
        return SendResult(success=True, message_id=pending_rid)
    return await self._send_text_chunks(chat_id, content, force_push=False)
```

`_SYSTEM_BYPASS_PREFIXES` 是网关自己的忙碌确认前缀（`⚡`、`⏳`、`⏩`、`💾`）。无论缓存的用户体验状态如何，始终让这些可见地通过。

### 此模式何时适用

在以下情况下使用输入循环覆盖方法：

- 平台的出站 API 具有严格的时间窗口约束（一次性回复令牌、过期的粘性会话等）且
- 在该平台上*可见的飞行中气泡*是可接受的用户体验。

在以下情况下使用更简单的 `slow_response_threshold = 0` 始终推送路径：

- 平台没有有意义的免费与付费区分，或
- 用户社区更喜欢“加载中… 加载中… 完成”静默然后响应的方式，而不是交互式中间气泡。

LINE 支持两者：阈值默认为 45 秒用于免费回传获取，而 `LINE_SLOW_RESPONSE_THRESHOLD=0` 恢复到“始终推送后备”。

### 参考实现

有关完整的 LINE 回传实现，请参阅 `plugins/platforms/line/adapter.py` — 一个 `RequestCache` 状态机（`PENDING → READY → DELIVERED`，加上用于 `/stop` 的 `ERROR`），一个在阈值处触发模板按钮气泡的 `_keep_typing` 覆盖，一个通过缓存路由的 `send` 覆盖，以及一个解决孤立 PENDING 条目的 `interrupt_session_activity` 覆盖。

### 参考实现（插件路径）

有关完整的可工作示例，请参阅仓库中的 `plugins/platforms/irc/` — 一个零外部依赖的完整异步 IRC 适配器。`plugins/platforms/teams/` 涵盖 Bot Framework / Adaptive Cards，`plugins/platforms/google_chat/` 涵盖基于 OAuth 的 REST API，`plugins/platforms/line/` 涵盖具有平台特定慢速 LLM 用户体验的 webhook 驱动消息 API。

---

--- body ---
## 逐步检查清单（内置路径）

:::note
此检查清单用于直接将平台添加到 Hermes 核心代码库 — 通常由核心贡献者为官方支持的平台完成。社区/第三方平台应使用上面的[插件路径](#plugin-path-recommended)。
:::

### 1. 平台枚举

在 `gateway/config.py` 中向 `Platform` 枚举添加您的平台：

```python
class Platform(str, Enum):
    # ... existing platforms ...
    NEWPLAT = "newplat"
```

### 2. 适配器文件

创建 `plugins/platforms/newplat/adapter.py`：

```python
from gateway.config import Platform, PlatformConfig
from gateway.platforms.base import (
    BasePlatformAdapter, MessageEvent, MessageType, SendResult,
)

def check_newplat_requirements() -> bool:
    """Return True if dependencies are available."""
    return SOME_SDK_AVAILABLE

class NewPlatAdapter(BasePlatformAdapter):
    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform.NEWPLAT)
        # Read config from config.extra dict
        extra = config.extra or {}
        self._api_key = extra.get("api_key") or os.getenv("NEWPLAT_API_KEY", "")

    async def connect(self) -> bool:
        # Set up connection, start polling/webhook
        self._mark_connected()
        return True

    async def disconnect(self) -> None:
        self._running = False
        self._mark_disconnected()

    async def send(self, chat_id, content, reply_to=None, metadata=None):
        # Send message via platform API
        return SendResult(success=True, message_id="...")

    async def get_chat_info(self, chat_id):
        return {"name": chat_id, "type": "dm"}
```

对于入站消息，构建一个 `MessageEvent` 并调用 `self.handle_message(event)`：

```python
source = self.build_source(
    chat_id=chat_id,
    chat_name=name,
    chat_type="dm",  # or "group"
    user_id=user_id,
    user_name=user_name,
)
event = MessageEvent(
    text=content,
    message_type=MessageType.TEXT,
    source=source,
    message_id=msg_id,
)
await self.handle_message(event)
```

### 3. 网关配置（`gateway/config.py`）

三个接触点：

1. **`get_connected_platforms()`** — 添加对平台所需凭据的检查
2. **`load_gateway_config()`** — 添加令牌环境映射条目：`Platform.NEWPLAT: "NEWPLAT_TOKEN"`
3. **`_apply_env_overrides()`** — 将所有 `NEWPLAT_*` 环境变量映射到配置

### 4. 网关运行器（`gateway/run.py`）

五个接触点：

1. **`_create_adapter()`** — 添加 `elif platform == Platform.NEWPLAT:` 分支
2. **`_is_user_authorized()` allowed_users 映射** — `Platform.NEWPLAT: "NEWPLAT_ALLOWED_USERS"`
3. **`_is_user_authorized()` allow_all 映射** — `Platform.NEWPLAT: "NEWPLAT_ALLOW_ALL_USERS"`
4. **早期环境检查 `_any_allowlist` 元组** — 添加 `"NEWPLAT_ALLOWED_USERS"`
5. **早期环境检查 `_allow_all` 元组** — 添加 `"NEWPLAT_ALLOW_ALL_USERS"`
6. **`_UPDATE_ALLOWED_PLATFORMS` 冻结集合** — 添加 `Platform.NEWPLAT`

### 5. 跨平台投递

1. **`gateway/platforms/webhook.py`** — 将 `"newplat"` 添加到投递类型元组
2. **`cron/scheduler.py`** — 添加到 `_KNOWN_DELIVERY_PLATFORMS` 冻结集合和 `_deliver_result()` 平台映射

### 6. CLI 集成

1. **`hermes_cli/config.py`** — 将所有 `NEWPLAT_*` 变量添加到 `_EXTRA_ENV_KEYS`
2. **`hermes_cli/gateway.py`** — 向 `_PLATFORMS` 列表添加条目，包括键、标签、表情符号、token_var、设置说明和变量
3. **`hermes_cli/platforms.py`** — 添加 `PlatformInfo` 条目，包括标签和默认工具集（由 `skills_config` 和 `tools_config` TUI 使用）
4. **`hermes_cli/setup.py`** — 添加 `_setup_newplat()` 函数（可以委托给 `gateway.py`），并将元组添加到消息平台列表
5. **`hermes_cli/status.py`** — 添加平台检测条目：`"NewPlat": ("NEWPLAT_TOKEN", "NEWPLAT_HOME_CHANNEL")`
6. **`hermes_cli/dump.py`** — 将 `"newplat": "NEWPLAT_TOKEN"` 添加到平台检测字典

### 7. 工具

1. **`tools/send_message_tool.py`** — 将 `"newplat": Platform.NEWPLAT` 添加到平台映射
2. **`tools/cronjob_tools.py`** — 将 `newplat` 添加到投递目标描述字符串

### 8. 工具集

1. **`toolsets.py`** — 使用 `_HERMES_CORE_TOOLS` 添加 `"hermes-newplat"` 工具集定义
2. **`toolsets.py`** — 将 `"hermes-newplat"` 添加到 `"hermes-gateway"` 包含列表

### 9. 可选：平台提示

**`agent/prompt_builder.py`** — 如果您的平台有特定的渲染限制（无 markdown、消息长度限制等），请向 `_PLATFORM_HINTS` 字典添加条目。这会将平台特定的指导注入到系统提示中：

```python
_PLATFORM_HINTS = {
    # ...
    "newplat": (
        "You are chatting via NewPlat. It supports markdown formatting "
        "but has a 4000-character message limit."
    ),
}
```

并非所有平台都需要提示 — 仅当代理的行为应有所差异时才添加。

### 10. 测试

创建 `tests/gateway/test_newplat.py`，涵盖：

- 基于配置的适配器构建
- 消息事件构建
- Send 方法（模拟外部 API）
- 平台特定功能（加密、路由等）

### 11. 文档

| 文件 | 要添加的内容 |
|------|-------------|
| `website/docs/user-guide/messaging/newplat.md` | 完整的平台设置页面 |
| `website/docs/user-guide/messaging/index.md` | 平台比较表、架构图、工具集表、安全部分、下一步链接 |
| `website/docs/reference/environment-variables.md` | 所有 NEWPLAT_* 环境变量 |
| `website/docs/reference/toolsets-reference.md` | hermes-newplat 工具集 |
| `website/docs/integrations/index.md` | 平台链接 |
| `website/sidebars.ts` | 文档页面的侧边栏条目 |
| `website/docs/developer-guide/architecture.md` | 适配器数量 + 列表 |
| `website/docs/developer-guide/gateway-internals.md` | 适配器文件列表 |

## 对等审计

在将新平台 PR 标记为完成之前，请对照已有平台运行对等审计：

```bash
# Find every .py file mentioning the reference platform
search_files "bluebubbles" output_mode="files_only" file_glob="*.py"

# Find every .py file mentioning the new platform
search_files "newplat" output_mode="files_only" file_glob="*.py"

# Any file in the first set but not the second is a potential gap
```

对 `.md` 和 `.ts` 文件重复。调查每个差距 — 它是平台枚举（需要更新）还是平台特定引用（跳过）？

## 常见模式

### 长轮询适配器

如果您的适配器使用长轮询（如 Telegram 或微信），请使用轮询循环任务：

```python
async def connect(self):
    self._poll_task = asyncio.create_task(self._poll_loop())
    self._mark_connected()

async def _poll_loop(self):
    while self._running:
        messages = await self._fetch_updates()
        for msg in messages:
            await self.handle_message(self._build_event(msg))
```

### 回调/Webhook 适配器

如果平台将消息推送到您的端点（如企业微信回调），请运行一个 HTTP 服务器：

```python
async def connect(self):
    self._app = web.Application()
    self._app.router.add_post("/callback", self._handle_callback)
    # ... start aiohttp server
    self._mark_connected()

async def _handle_callback(self, request):
    event = self._build_event(await request.text())
    await self._message_queue.put(event)
    return web.Response(text="success")  # 立即确认
```

对于具有严格响应截止时间的平台（例如企业微信的 5 秒限制），始终立即确认，并在稍后主动通过 API 交付代理的回复。代理会话运行 3–30 分钟 — 在回调响应窗口内进行内联回复是不可行的。

### 令牌锁定

如果适配器持有具有唯一凭据的持久连接，请添加一个作用域锁，以防止两个配置文件使用相同的凭据：

```python
from gateway.status import acquire_scoped_lock, release_scoped_lock

async def connect(self):
    if not acquire_scoped_lock("newplat", self._token):
        logger.error("Token already in use by another profile")
        return False
    # ... connect

async def disconnect(self):
    release_scoped_lock("newplat", self._token)
```

## 参考实现

| 适配器 | 模式 | 复杂度 | 适合参考 |
|---------|---------|------------|-------------------|
| `bluebubbles.py` | REST + webhook | 中等 | 简单的 REST API 集成 |
| `weixin.py` | 长轮询 + CDN | 高 | 媒体处理、加密 |
| `wecom_callback.py` | 回调/webhook | 中等 | HTTP 服务器、AES 加密、多应用 |
| `plugins/platforms/irc/adapter.py` | 长轮询 + IRC 协议 | 高 | 功能齐全的插件适配器，带有作用域令牌锁 |