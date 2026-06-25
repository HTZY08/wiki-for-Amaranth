---
title: Context Engine Plugin
---

sidebar_position: 9
title: "上下文引擎插件"
description: "如何构建一个替代内置 ContextCompressor 的上下文引擎插件"
---

--- body ---
# 构建上下文引擎插件

上下文引擎插件用另一种管理对话上下文的策略替换内置的 `ContextCompressor`。例如，一种无损上下文管理（Lossless Context Management, LCM）引擎，它构建知识有向无环图（DAG）而不是有损摘要。

## 工作原理

代理的上下文管理构建在 `ContextEngine` 抽象基类（ABC）上（`agent/context_engine.py`）。内置的 `ContextCompressor` 是默认实现。插件引擎必须实现相同的接口。

一次只能激活**一个**上下文引擎。选择通过配置驱动：

```yaml
# config.yaml
context:
  engine: "compressor"    # default built-in
  engine: "lcm"           # activates a plugin engine named "lcm"
```

插件引擎**从不自动激活**——用户必须显式地将 `context.engine` 设置为插件的名称。

## 目录结构

每个上下文引擎位于 `plugins/context_engine/<name>/`：

```
plugins/context_engine/lcm/
├── __init__.py      # exports the ContextEngine subclass
├── plugin.yaml      # metadata (name, description, version)
└── ...              # any other modules your engine needs
```

## ContextEngine 抽象基类（ABC）

你的引擎必须实现以下**必需**方法：

```python
from agent.context_engine import ContextEngine

class LCMEngine(ContextEngine):

    @property
    def name(self) -> str:
        """Short identifier, e.g. 'lcm'. Must match config.yaml value."""
        return "lcm"

    def update_from_response(self, usage: dict) -> None:
        """Called after every LLM call with the usage dict.

        Update self.last_prompt_tokens, self.last_completion_tokens,
        self.last_total_tokens from the response.
        """

    def should_compress(self, prompt_tokens: int = None) -> bool:
        """Return True if compaction should fire this turn."""

    def compress(self, messages: list, current_tokens: int = None,
                 focus_topic: str = None) -> list:
        """Compact the message list and return a new (possibly shorter) list.

        The returned list must be a valid OpenAI-format message sequence.

        ``focus_topic`` is an optional topic string from manual
        ``/compress <focus>``; engines that support guided compression should
        prioritise preserving information related to it, others may ignore it.
        """
```

### 你的引擎必须维护的类属性

代理直接读取这些属性用于显示和日志记录：

```python
last_prompt_tokens: int = 0
last_completion_tokens: int = 0
last_total_tokens: int = 0
threshold_tokens: int = 0        # when compression triggers
context_length: int = 0          # model's full context window
compression_count: int = 0       # how many times compress() has run
```

### 可选方法

这些方法在抽象基类中有合理的默认值。根据需要覆盖：

| 方法 | 默认值 | 何时覆盖 |
|------|--------|----------|
| `on_session_start(session_id, **kwargs)` | 无操作 | 你需要加载持久化状态（DAG, DB） |
| `on_session_end(session_id, messages)` | 无操作 | 你需要刷新状态，关闭连接 |
| `on_session_reset()` | 重置令牌计数器 | 你有需要清除的每会话状态 |
| `update_model(model, context_length, ...)` | 更新 context_length + threshold | 你需要在模型切换时重新计算预算 |
| `get_tool_schemas()` | 返回 `[]` | 你的引擎提供可被代理调用的工具（例如 `lcm_grep`） |
| `handle_tool_call(name, args, **kwargs)` | 返回错误JSON | 你实现工具处理器 |
| `should_compress_preflight(messages)` | 返回 `False` | 你可以进行低成本的预API调用估计 |
| `get_status()` | 标准令牌/阈值字典 | 你有自定义指标要暴露 |

## 引擎工具

上下文引擎可以暴露代理直接调用的工具。从 `get_tool_schemas()` 返回模式，并在 `handle_tool_call()` 中处理调用：

```python
def get_tool_schemas(self):
    return [{
        "name": "lcm_grep",
        "description": "Search the context knowledge graph",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"],
        },
    }]

def handle_tool_call(self, name, args, **kwargs):
    if name == "lcm_grep":
        results = self._search_dag(args["query"])
        return json.dumps({"results": results})
    return json.dumps({"error": f"Unknown tool: {name}"})
```

引擎工具在启动时被注入到代理的工具列表中，并自动分发——无需注册表注册。

## 注册

### 通过目录（推荐）

将你的引擎放置在 `plugins/context_engine/<name>/` 下。`__init__.py` 必须导出一个 `ContextEngine` 子类。发现系统会自动查找并实例化它。

### 通过通用插件系统

通用插件也可以注册上下文引擎：

```python
def register(ctx):
    engine = LCMEngine(context_length=200000)
    ctx.register_context_engine(engine)
```

只能注册一个引擎。第二个尝试注册的插件将被拒绝并显示警告。

## 生命周期

```
1. Engine instantiated (plugin load or directory discovery)
2. on_session_start() — conversation begins
3. update_from_response() — after each API call
4. should_compress() — checked each turn
5. compress() — called when should_compress() returns True
6. on_session_end() — session boundary (CLI exit, /reset, gateway expiry)
```

`on_session_reset()` 在 `/new` 或 `/reset` 时调用，用于清除每会话状态而无需完全关闭。

## 配置

用户通过 `hermes plugins` → 提供者插件 → 上下文引擎，或编辑 `config.yaml` 来选择你的引擎：

```yaml
context:
  engine: "lcm"   # must match your engine's name property
```

`compression` 配置块（`compression.threshold`、`compression.protect_last_n` 等）是内置 `ContextCompressor` 特有的。如果需要，你的引擎应该定义自己的配置格式，在初始化期间从 `config.yaml` 读取。

## 测试

```python
from agent.context_engine import ContextEngine

def test_engine_satisfies_abc():
    engine = YourEngine(context_length=200000)
    assert isinstance(engine, ContextEngine)
    assert engine.name == "your-name"

def test_compress_returns_valid_messages():
    engine = YourEngine(context_length=200000)
    msgs = [{"role": "user", "content": "hello"}]
    result = engine.compress(msgs)
    assert isinstance(result, list)
    assert all("role" in m for m in result)
```

参见 `tests/agent/test_context_engine.py` 获取完整的抽象基类契约测试套件。

## 另请参阅

- [上下文压缩与缓存](/developer-guide/context-compression-and-caching) — 内置压缩器的工作原理
- [记忆提供者插件](/developer-guide/memory-provider-plugin) — 类似的单选项插件系统用于记忆
- [插件](/user-guide/features/plugins) — 通用插件系统概述