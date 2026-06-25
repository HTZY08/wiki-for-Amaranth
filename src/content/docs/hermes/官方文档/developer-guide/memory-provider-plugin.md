--- frontmatter ---
---
sidebar_position: 8
title: "记忆提供者插件"
description: "如何为 Hermes Agent 构建一个记忆提供者插件"
---

--- body ---
# 构建记忆提供者插件

记忆提供者插件赋予 Hermes Agent 持久化、跨会话的知识，超越了内置的 MEMORY.md 和 USER.md。本指南介绍了如何构建一个。

:::tip
记忆提供者是两种**提供者插件**类型之一。另一种是[上下文引擎插件](/developer-guide/context-engine-plugin)，它取代了内置的上下文压缩器。两者遵循相同的模式：单选、配置驱动、通过 `hermes plugins` 管理。
:::

## 目录结构

每个记忆提供者位于 `plugins/memory/<name>/` 中：

```
plugins/memory/my-provider/
├── __init__.py      # MemoryProvider 实现 + register() 入口点
├── plugin.yaml      # 元数据（名称、描述、钩子）
└── README.md        # 设置说明、配置参考、工具
```

## MemoryProvider 抽象基类

你的插件实现了来自 `agent/memory_provider.py` 的 `MemoryProvider` 抽象基类：

```python
from agent.memory_provider import MemoryProvider

class MyMemoryProvider(MemoryProvider):
    @property
    def name(self) -> str:
        return "my-provider"

    def is_available(self) -> bool:
        """检查此提供者是否可以激活。不可进行网络调用。"""
        return bool(os.environ.get("MY_API_KEY"))

    def initialize(self, session_id: str, **kwargs) -> None:
        """在智能体启动时调用一次。

        kwargs 始终包含：
          hermes_home (str): 当前的 HERMES_HOME 路径。用于存储。
        """
        self._api_key = os.environ.get("MY_API_KEY", "")
        self._session_id = session_id

    # ... 实现其余方法
```

## 必需方法

### 核心生命周期

| 方法 | 调用时机 | 必须实现？ |
|--------|-----------|-----------------|
| `name` (属性) | 始终 | **是** |
| `is_available()` | 智能体初始化、激活前 | **是** — 不可进行网络调用 |
| `initialize(session_id, **kwargs)` | 智能体启动 | **是** |
| `get_tool_schemas()` | 初始化后，用于工具注入 | **是** |
| `handle_tool_call(tool_name, args, **kwargs)` | 智能体使用你的工具时 | **是**（如果你有工具） |

### 配置

| 方法 | 目的 | 必须实现？ |
|--------|---------|-----------------|
| `get_config_schema()` | 声明用于 `hermes memory setup` 的配置字段 | **是** |
| `save_config(values, hermes_home)` | 将非机密配置写入本地位置 | **是**（除非仅通过环境变量） |

### 可选钩子

| 方法 | 调用时机 | 使用场景 |
|--------|-----------|----------|
| `system_prompt_block()` | 系统提示组装 | 静态提供者信息 |
| `prefetch(query, *, session_id="")` | 每次 API 调用前 | 返回回忆的上下文 |
| `queue_prefetch(query)` | 每次轮次后 | 为下一轮预热 |
| `sync_turn(user, assistant, *, session_id="")` | 每次完成的轮次后 | 持久化对话 |
| `on_session_end(messages)` | 对话结束 | 最终提取/刷新 |
| `on_pre_compress(messages)` | 上下文压缩前 | 在丢弃前保存见解 |
| `on_memory_write(action, target, content)` | 内置内存写入 | 镜像到你的后端 |
| `shutdown()` | 进程退出 | 清理连接 |

## 配置模式

`get_config_schema()` 返回一个字段描述符列表，供 `hermes memory setup` 使用：

```python
def get_config_schema(self):
    return [
        {
            "key": "api_key",
            "description": "My Provider API 密钥",
            "secret": True,           # → 写入 .env
            "required": True,
            "env_var": "MY_API_KEY",   # 明确的环境变量名
            "url": "https://my-provider.com/keys",  # 获取位置
        },
        {
            "key": "region",
            "description": "服务器区域",
            "default": "us-east",
            "choices": ["us-east", "eu-west", "ap-south"],
        },
        {
            "key": "project",
            "description": "项目标识符",
            "default": "hermes",
        },
    ]
```

带有 `secret: True` 和 `env_var` 的字段放入 `.env`。非机密字段传递给 `save_config()`。

:::tip 最小与完整模式
`get_config_schema()` 中的每个字段都会在 `hermes memory setup` 期间被提示。拥有大量选项的提供者应保持模式最小化——只包含用户**必须**配置的字段（API 密钥、必需的凭据）。将可选设置记录在配置文件中（例如 `$HERMES_HOME/myprovider.json`），而不是在设置期间全部提示。这样既保持设置向导快速，又支持高级配置。参见 Supermemory 提供者作为示例——它只提示 API 密钥；所有其他选项都在 `supermemory.json` 中。
:::

## 保存配置

```python
def save_config(self, values: dict, hermes_home: str) -> None:
    """将非机密配置写入本地位置。"""
    import json
    from pathlib import Path
    config_path = Path(hermes_home) / "my-provider.json"
    config_path.write_text(json.dumps(values, indent=2))
```

对于仅环境变量的提供者，保留默认的空操作。

## 插件入口点

```python
def register(ctx) -> None:
    """由记忆插件发现系统调用。"""
    ctx.register_memory_provider(MyMemoryProvider())
```

## plugin.yaml

```yaml
name: my-provider
version: 1.0.0
description: "简短描述此提供者的功能。"
hooks:
  - on_session_end    # 列出你实现的钩子
```

## 线程契约

**`sync_turn()` 必须是非阻塞的。** 如果你的后端有延迟（API 调用、LLM 处理），请在一个守护线程中执行工作：

```python
def sync_turn(self, user_content, assistant_content, *, session_id="", messages=None):
    def _sync():
        try:
            self._api.ingest(user_content, assistant_content, session_id=session_id, messages=messages)
        except Exception as e:
            logger.warning("同步失败: %s", e)

    if self._sync_thread and self._sync_thread.is_alive():
        self._sync_thread.join(timeout=5.0)
    self._sync_thread = threading.Thread(target=_sync, daemon=True)
    self._sync_thread.start()
```

`messages` 是可选的 OpenAI 风格对话上下文，在完成的轮次后提供。当存在时，它包括用户/助手消息、助手工具调用和工具结果消息。不需要原始轮次上下文的提供者可以省略 `messages` 参数；Hermes 将继续使用旧签名调用它们。

云提供者应记录 `messages` 的哪些部分被发送到设备外。工具调用和工具结果可能包含文件路径、命令输出或其他工作区数据。

## 配置文件隔离

所有存储路径**必须**使用来自 `initialize()` 的 `hermes_home` 参数，而不是硬编码的 `~/.hermes`：

```python
# 正确 — 配置文件作用域
from hermes_constants import get_hermes_home
data_dir = get_hermes_home() / "my-provider"

# 错误 — 所有配置文件共享
data_dir = Path("~/.hermes/my-provider").expanduser()
```

## 测试

参见 `tests/agent/test_memory_provider.py` 及相邻的记忆测试（`tests/agent/test_memory_session_switch.py`、`tests/agent/test_memory_user_id.py`、`tests/run_agent/test_memory_provider_init.py`）以获取端到端模式。

```python
from agent.memory_manager import MemoryManager

mgr = MemoryManager()
mgr.add_provider(my_provider)
mgr.initialize_all(session_id="test-1", platform="cli")

# 测试工具路由
result = mgr.handle_tool_call("my_tool", {"action": "add", "content": "test"})

# 测试生命周期
mgr.sync_all("user msg", "assistant msg")
mgr.on_session_end([])
mgr.shutdown_all()
```

## 添加 CLI 命令

记忆提供者插件可以注册自己的 CLI 子命令树（例如 `hermes my-provider status`、`hermes my-provider config`）。这使用基于约定的发现系统——无需修改核心文件。

### 工作原理

1. 在你的插件目录中添加一个 `cli.py` 文件
2. 定义一个 `register_cli(subparser)` 函数，构建 argparse 树
3. 记忆插件系统在启动时通过 `discover_plugin_cli_commands()` 发现它
4. 你的命令出现在 `hermes <provider-name> <subcommand>` 下

**活跃提供者门控：** 仅当你的提供者是配置中活跃的 `memory.provider` 时，你的 CLI 命令才会出现。如果用户尚未配置你的提供者，你的命令不会在 `hermes --help` 中显示。

### 示例

```python
# plugins/memory/my-provider/cli.py

def my_command(args):
    """由 argparse 调用的处理器。"""
    sub = getattr(args, "my_command", None)
    if sub == "status":
        print("提供者已激活并已连接。")
    elif sub == "config":
        print("显示配置...")
    else:
        print("用法: hermes my-provider <status|config>")

def register_cli(subparser) -> None:
    """构建 hermes my-provider argparse 树。

    在 argparse 设置时由 discover_plugin_cli_commands() 调用。
    """
    subs = subparser.add_subparsers(dest="my_command")
    subs.add_parser("status", help="显示提供者状态")
    subs.add_parser("config", help="显示提供者配置")
    subparser.set_defaults(func=my_command)
```

### 参考实现

参见 `plugins/memory/honcho/cli.py` 获取包含 13 个子命令、跨配置文件管理（`--target-profile`）和配置读写的完整示例。

### 带 CLI 的目录结构

```
plugins/memory/my-provider/
├── __init__.py      # MemoryProvider 实现 + register()
├── plugin.yaml      # 元数据
├── cli.py           # register_cli(subparser) — CLI 命令
└── README.md        # 设置说明
```

## 单一提供者规则

一次只能有一个**外部**记忆提供者处于活动状态。如果用户尝试注册第二个，MemoryManager 会拒绝并发出警告。这可以防止工具模式膨胀和后端冲突。