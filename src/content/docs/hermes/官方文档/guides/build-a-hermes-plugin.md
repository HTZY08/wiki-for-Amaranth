--- frontmatter ---
---
sidebar_position: 9
sidebar_label: "构建插件"
title: "构建 Hermes 插件"
description: "构建一个完整的 Hermes 插件的逐步指南，包含工具、钩子（hooks）、数据文件和技能（skills）"
---

--- body ---
# 构建 Hermes 插件

本指南将逐步指导你从零开始构建一个完整的 Hermes 插件。最终你将拥有一个可工作的插件，包含多个工具、生命周期钩子（lifecycle hooks）、附带的数据文件以及一个捆绑的技能（skill）——插件系统支持的所有一切。

:::info 不确定需要哪个指南？
Hermes 有多个不同的可插拔接口——有些使用 Python `register_*` API，其他的则是配置驱动或直接放入目录。先用这张表来定位：

| 如果你想添加… | 请阅读 |
|---|---|
| 自定义工具、钩子（hooks）、斜杠命令（slash commands）、技能（skills）或 CLI 子命令 | **本指南**（通用插件表面） |
| 一个 **LLM / 推理后端**（新提供商） | [模型提供商插件](/developer-guide/model-provider-plugin) |
| 一个**网关通道**（Discord/Telegram/IRC/Teams 等） | [添加平台适配器](/developer-guide/adding-platform-adapters) |
| 一个**记忆后端**（Honcho/Mem0/Supermemory 等） | [记忆提供商插件](/developer-guide/memory-provider-plugin) |
| 一个**上下文压缩引擎** | [上下文引擎插件](/developer-guide/context-engine-plugin) |
| 一个**图像生成后端** | [图像生成提供商插件](/developer-guide/image-gen-provider-plugin) |
| 一个**视频生成后端** | [视频生成提供商插件](/developer-guide/video-gen-provider-plugin) |
| 一个 **TTS 后端**（任意 CLI — Piper, VoxCPM, Kokoro, 声音克隆, …） | [TTS 自定义命令提供商](/user-guide/features/tts#custom-command-providers) — 配置驱动，无需 Python |
| 一个 **STT 后端**（自定义 whisper / ASR CLI） | [语音消息转录](/user-guide/features/tts#voice-message-transcription-stt) — 设置 `HERMES_LOCAL_STT_COMMAND` 为 shell 模板 |
| 通过 **MCP** 的外部工具（文件系统、GitHub、Linear、任意 MCP 服务器） | [MCP](/user-guide/features/mcp) — 在 `config.yaml` 中声明 `mcp_servers.<name>` |
| **网关事件钩子**（在启动、会话事件、命令时触发） | [事件钩子](/user-guide/features/hooks#gateway-event-hooks) — 将 `HOOK.yaml` + `handler.py` 放入 `~/.hermes/hooks/<name>/` |
| **Shell 钩子**（在事件发生时运行 shell 命令） | [Shell 钩子](/user-guide/features/hooks#shell-hooks) — 在 `config.yaml` 中 `hooks:` 下声明 |
| **额外的技能来源**（自定义 GitHub 仓库、私有技能索引） | [技能](/user-guide/features/skills) — `hermes skills tap add <repo>` · [发布一个 tap](/user-guide/features/skills#publishing-a-custom-skill-tap) |
| 一个一流的**核心**推理提供商（不是插件） | [添加提供商](/developer-guide/adding-providers) |

查看完整的[可插拔接口表](/user-guide/features/plugins#pluggable-interfaces--where-to-go-for-each)以获得所有扩展面的综合视图，包括配置驱动（TTS、STT、MCP、shell 钩子）和放入目录（网关钩子）风格。
:::

## 你将构建什么

一个**计算器**插件，包含两个工具：
- `calculate` — 计算数学表达式（`2**16`、`sqrt(144)`、`pi * 5**2`）
- `unit_convert` — 单位换算（`100 F → 37.78 C`、`5 km → 3.11 mi`）

此外还有一个钩子（hook），记录每次工具调用，以及一个捆绑的技能文件。

## 第一步：创建插件目录

```bash
mkdir -p ~/.hermes/plugins/calculator
cd ~/.hermes/plugins/calculator
```

## 第二步：编写清单文件

创建 `plugin.yaml`：

```yaml
name: calculator
version: 1.0.0
description: 数学计算器 — 计算表达式和单位换算
provides_tools:
  - calculate
  - unit_convert
provides_hooks:
  - post_tool_call
```

这告诉 Hermes："我是一个名为 calculator 的插件，我提供工具和钩子。" `provides_tools` 和 `provides_hooks` 字段是插件注册内容的列表。

你可以添加的可选字段：
```yaml
author: 你的名字
requires_env:          # 根据环境变量控制加载；安装时提示
  - SOME_API_KEY       # 简单格式 — 如果缺少则禁用插件
  - name: OTHER_KEY    # 丰富格式 — 安装时显示描述/URL
    description: "其他服务的密钥"
    url: "https://other.com/keys"
    secret: true
```

## 第三步：编写工具模式（schema）

创建 `schemas.py` — 这是 LLM 读取的内容，用于决定何时调用你的工具：

```python
"""工具模式 — LLM 看到的内容。"""

CALCULATE = {
    "name": "calculate",
    "description": (
        "计算一个数学表达式并返回结果。"
        "支持算术运算（+, -, *, /, **）、函数（sqrt, sin, cos, "
        "log, abs, round, floor, ceil）和常量（pi, e）。"
        "用于用户询问的任何数学问题。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "要计算的数学表达式（例如 '2**10'、'sqrt(144)'）",
            },
        },
        "required": ["expression"],
    },
}

UNIT_CONVERT = {
    "name": "unit_convert",
    "description": (
        "在单位之间转换一个值。支持长度（m, km, mi, ft, in）、"
        "重量（kg, lb, oz, g）、温度（C, F, K）、数据（B, KB, MB, GB, TB）"
        "和时间（s, min, hr, day）。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "value": {
                "type": "number",
                "description": "要转换的数值",
            },
            "from_unit": {
                "type": "string",
                "description": "源单位（例如 'km'、'lb'、'F'、'GB'）",
            },
            "to_unit": {
                "type": "string",
                "description": "目标单位（例如 'mi'、'kg'、'C'、'MB'）",
            },
        },
        "required": ["value", "from_unit", "to_unit"],
    },
}
```

**为什么模式重要：** `description` 字段是 LLM 决定何时使用你的工具的依据。请具体说明它的功能和适用场景。`parameters` 定义了 LLM 会传递哪些参数。

## 第四步：编写工具处理器

创建 `tools.py` — 这是当 LLM 调用你的工具时实际执行的代码：

```python
"""工具处理器 — 当 LLM 调用每个工具时运行的代码。"""

import json
import math

# 用于表达式求值的安全全局变量 — 无文件/网络访问
_SAFE_MATH = {
    "abs": abs, "round": round, "min": min, "max": max,
    "pow": pow, "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
    "tan": math.tan, "log": math.log, "log2": math.log2, "log10": math.log10,
    "floor": math.floor, "ceil": math.ceil,
    "pi": math.pi, "e": math.e,
    "factorial": math.factorial,
}


def calculate(args: dict, **kwargs) -> str:
    """安全地计算一个数学表达式。

    处理器的规则：
    1. 接收 args (dict) — LLM 传递的参数
    2. 执行工作
    3. 返回 JSON 字符串 — 始终如此，即使在错误时也要返回
    4. 接受 **kwargs 以实现向前兼容
    """
    expression = args.get("expression", "").strip()
    if not expression:
        return json.dumps({"error": "未提供表达式"})

    try:
        result = eval(expression, {"__builtins__": {}}, _SAFE_MATH)
        return json.dumps({"expression": expression, "result": result})
    except ZeroDivisionError:
        return json.dumps({"expression": expression, "error": "除以零"})
    except Exception as e:
        return json.dumps({"expression": expression, "error": f"无效: {e}"})


# 转换表 — 值以基础单位表示
_LENGTH = {"m": 1, "km": 1000, "mi": 1609.34, "ft": 0.3048, "in": 0.0254, "cm": 0.01}
_WEIGHT = {"kg": 1, "g": 0.001, "lb": 0.453592, "oz": 0.0283495}
_DATA = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
_TIME = {"s": 1, "ms": 0.001, "min": 60, "hr": 3600, "day": 86400}


def _convert_temp(value, from_u, to_u):
    # 标准化为摄氏度
    c = {"F": (value - 32) * 5/9, "K": value - 273.15}.get(from_u, value)
    # 转换为目标单位
    return {"F": c * 9/5 + 32, "K": c + 273.15}.get(to_u, c)


def unit_convert(args: dict, **kwargs) -> str:
    """在单位之间转换。"""
    value = args.get("value")
    from_unit = args.get("from_unit", "").strip()
    to_unit = args.get("to_unit", "").strip()

    if value is None or not from_unit or not to_unit:
        return json.dumps({"error": "需要 value、from_unit 和 to_unit"})

    try:
        # 温度
        if from_unit.upper() in {"C","F","K"} and to_unit.upper() in {"C","F","K"}:
            result = _convert_temp(float(value), from_unit.upper(), to_unit.upper())
            return json.dumps({"input": f"{value} {from_unit}", "result": round(result, 4),
                             "output": f"{round(result, 4)} {to_unit}"})

        # 基于比例的转换
        for table in (_LENGTH, _WEIGHT, _DATA, _TIME):
            lc = {k.lower(): v for k, v in table.items()}
            if from_unit.lower() in lc and to_unit.lower() in lc:
                result = float(value) * lc[from_unit.lower()] / lc[to_unit.lower()]
                return json.dumps({"input": f"{value} {from_unit}",
                                 "result": round(result, 6),
                                 "output": f"{round(result, 6)} {to_unit}"})

        return json.dumps({"error": f"无法转换 {from_unit} → {to_unit}"})
    except Exception as e:
        return json.dumps({"error": f"转换失败: {e}"})
```

**处理器的关键规则：**
1. **签名：** `def my_handler(args: dict, **kwargs) -> str`
2. **返回值：** 始终是一个 JSON 字符串，成功和错误都要返回。
3. **永远不要抛出异常：** 捕获所有异常，返回错误 JSON。
4. **接受 `**kwargs`：** Hermes 将来可能会传递额外的上下文。

## 第五步：编写注册代码

创建 `__init__.py` — 这里将模式（schemas）连接到处理器（handlers）：

```python
"""计算器插件 — 注册。"""

import logging

from . import schemas, tools

logger = logging.getLogger(__name__)

# 通过钩子跟踪工具使用情况
_call_log = []

def _on_post_tool_call(tool_name, args, result, task_id, **kwargs):
    """钩子：在每次工具调用后运行（不仅限于我们的工具）。"""
    _call_log.append({"tool": tool_name, "session": task_id})
    if len(_call_log) > 100:
        _call_log.pop(0)
    logger.debug("工具被调用: %s (会话 %s)", tool_name, task_id)


def register(ctx):
    """将模式连接到处理器并注册钩子。"""
    ctx.register_tool(name="calculate",    toolset="calculator",
                      schema=schemas.CALCULATE,    handler=tools.calculate)
    ctx.register_tool(name="unit_convert", toolset="calculator",
                      schema=schemas.UNIT_CONVERT, handler=tools.unit_convert)

    # 这个钩子会在所有工具调用时触发，不仅仅是我们的
    ctx.register_hook("post_tool_call", _on_post_tool_call)
```

**`register()` 的作用：**
- 在启动时恰好被调用一次
- `ctx.register_tool()` 将你的工具放入注册表 — 模型会立即看到它
- `ctx.register_hook()` 订阅生命周期事件
- `ctx.register_cli_command()` 注册一个 CLI 子命令（例如 `hermes my-plugin <subcommand>`）
- `ctx.register_command()` 注册一个会话内的斜杠命令（例如在 CLI / 网关聊天中键入 `/myplugin <args>`）— 参见下方的[注册斜杠命令](#注册斜杠命令)
- `ctx.dispatch_tool(name, arguments)` — 调用任何其他工具（内置或其他插件提供的），并自动连接父代理的上下文（审批、凭证、task_id）。在需要调用 `terminal`、`read_file` 或任何其他工具（好像模型直接调用了它一样）的斜杠命令处理器中非常有用。
- 如果此函数崩溃，插件将被禁用，但 Hermes 会继续正常运行

**`dispatch_tool` 示例 — 一个运行工具的斜杠命令：**

```python
def handle_scan(ctx, raw_args: str):
    """通过调用注册表中的 terminal 工具来实现 /scan。"""
    result = ctx.dispatch_tool("terminal", {"command": f"find . -name '{raw_args}'"})
    return result  # 返回给调用者的聊天 UI

def register(ctx):
    # 处理器接收一个 raw_args 字符串；通过 lambda 闭包捕获 ctx。
    ctx.register_command(
        "scan",
        lambda raw: handle_scan(ctx, raw),
        description="查找与 glob 模式匹配的文件",
    )
```

分派的工具会经过正常的审批、编辑（redaction）和预算管道——它是一个真正的工具调用，而不是绕过它们的捷径。

## 第六步：测试

启动 Hermes：

```bash
hermes
```

你应该会在横幅的工具列表中看到 `calculator: calculate, unit_convert`。

尝试以下提示：
```
2 的 16 次方是多少？
将 100 华氏度转换为摄氏度
2 乘以 pi 的平方根是多少？
1.5 TB 是多少 GB？
```

检查插件状态：
```
/plugins
```

输出：
```
插件 (1):
  ✓ calculator v1.0.0 (2 个工具, 1 个钩子)
```

### 调试插件发现

如果你的插件没有显示 — 或者显示但无法加载 — 设置 `HERMES_PLUGINS_DEBUG=1` 可以在 stderr 上获取详细的发现日志：

```bash
HERMES_PLUGINS_DEBUG=1 hermes plugins list
```

你将看到，对于每个插件来源（捆绑、用户、项目、入口点）：

- 扫描了哪些目录，每个目录生成了多少个清单
- 每个清单：解析的键、名称、种类、来源、磁盘路径
- 跳过原因：`通过配置禁用`、`未在配置中启用`、`独占插件`、`没有 plugin.yaml，达到深度上限`
- 加载时：正在导入的插件，以及 `register(ctx)` 注册内容的摘要（工具、钩子、斜杠命令、CLI 命令）
- 解析失败时：异常完整的回溯（YAML 扫描器错误等）
- `register()` 失败时：完整的回溯，指向你 `__init__.py` 中引发异常的行

当设置了环境变量时，同样的日志也会以 WARNING 级别（仅失败）和 DEBUG 级别（所有内容）写入 `~/.hermes/logs/agent.log`。因此，如果你无法在运行环境变量（例如在网关内部），可以改为跟踪该日志文件：

```bash
hermes logs --level WARNING | grep -i plugin
```

插件不出现的常见原因：

- **未在配置中启用** — 插件是选择性加入的。运行 `hermes plugins enable <name>`（名称来自 `plugins list` 输出，对于嵌套布局可能是 `<category>/<plugin>`）。
- **目录布局错误** — 必须是 `~/.hermes/plugins/<plugin-name>/plugin.yaml`（扁平）或 `~/.hermes/plugins/<category>/<plugin-name>/plugin.yaml`（最多一层类别嵌套）。更深的目录将被忽略。
- **缺少 `__init__.py`** — 插件目录需要同时包含 `plugin.yaml` 和带有 `register(ctx)` 函数的 `__init__.py`。
- **`kind` 错误** — 网关适配器需要在清单中设置 `kind: platform`。记忆提供商会被自动检测为 `kind: exclusive`，并通过 `memory.provider` 配置路由，而不是 `plugins.enabled`。

## 你插件的最终结构

```
~/.hermes/plugins/calculator/
├── plugin.yaml      # "我是计算器，我提供工具和钩子"
├── __init__.py      # 接线：模式（schema）→ 处理器（handler），注册钩子
├── schemas.py       # LLM 读取的内容（描述 + 参数规格）
└── tools.py         # 实际运行的代码（calculate、unit_convert 函数）
```

四个文件，清晰的分离：
- **清单（Manifest）** 声明插件是什么
- **模式（Schema）** 为 LLM 描述工具
- **处理器（Handler）** 实现实际逻辑
- **注册（Registration）** 连接所有内容

## 插件还能做什么？

### 附带数据文件

将任何文件放入插件目录中，并在导入时读取它们：

```python
# 在 tools.py 或 __init__.py 中
from pathlib import Path

_PLUGIN_DIR = Path(__file__).parent
_DATA_FILE = _PLUGIN_DIR / "data" / "languages.yaml"

with open(_DATA_FILE) as f:
    _DATA = yaml.safe_load(f)
```

### 捆绑技能

插件可以附带技能文件，代理可以通过 `skill_view("plugin:skill")` 加载它们。在 `__init__.py` 中注册它们：

```
~/.hermes/plugins/my-plugin/
├── __init__.py
├── plugin.yaml
└── skills/
    ├── my-workflow/
    │   └── SKILL.md
    └── my-checklist/
        └── SKILL.md
```

```python
from pathlib import Path

def register(ctx):
    skills_dir = Path(__file__).parent / "skills"
    for child in sorted(skills_dir.iterdir()):
        skill_md = child / "SKILL.md"
        if child.is_dir() and skill_md.exists():
            ctx.register_skill(child.name, skill_md)
```

现在代理可以使用它们的命名空间名称加载你的技能：

```python
skill_view("my-plugin:my-workflow")   # → 插件的版本
skill_view("my-workflow")              # → 内置版本（保持不变）
```

**关键属性：**
- 插件技能是**只读的** — 它们不会进入 `~/.hermes/skills/`，也不能通过 `skill_manage` 编辑。
- 插件技能不会在系统提示的 `<available_skills>` 索引中列出 — 它们是手动显式加载的。
- 裸技能名称不受影响 — 命名空间防止与内置技能冲突。
- 当代理加载一个插件技能时，会预先添加一个包上下文横幅，列出同一插件的兄弟技能。

:::tip 旧模式
旧的 `shutil.copy2` 模式（将技能复制到 `~/.hermes/skills/`）仍然有效，但会造成与内置技能名称冲突的风险。对于新插件，首选 `ctx.register_skill()`。
:::

### 根据环境变量控制加载

如果你的插件需要 API 密钥：

```yaml
# plugin.yaml — 简单格式（向后兼容）
requires_env:
  - WEATHER_API_KEY
```

如果未设置 `WEATHER_API_KEY`，插件将被禁用并显示明确消息。不会崩溃，也不会在代理中报错 — 只是显示"插件 weather 被禁用（缺少：WEATHER_API_KEY）"。

当用户运行 `hermes plugins install` 时，他们会被**交互式地提示**输入所有缺失的 `requires_env` 变量。值会自动保存到 `.env` 中。

为了更好的安装体验，请使用带描述和注册 URL 的丰富格式：

```yaml
# plugin.yaml — 丰富格式
requires_env:
  - name: WEATHER_API_KEY
    description: "OpenWeather 的 API 密钥"
    url: "https://openweathermap.org/api"
    secret: true
```

| 字段 | 必需 | 描述 |
|-------|----------|-------------|
| `name` | 是 | 环境变量名称 |
| `description` | 否 | 在安装提示时向用户显示 |
| `url` | 否 | 获取凭证的位置 |
| `secret` | 否 | 如果为 `true`，输入将被隐藏（如密码字段） |

两种格式可以在同一列表中混合使用。已设置的变量会被静默跳过。

### 延迟安装可选 Python 依赖

如果你的插件包装了一个并非每个用户都会安装的 SDK（供应商 SDK、重型 ML 库、平台特定包），不要在模块顶部 `import` 它。在工具处理器内部使用 `tools.lazy_deps.ensure(...)` 辅助函数 — Hermes 会在首次使用时安装该包，并由用户的 `security.allow_lazy_installs` 配置控制。

```python
# tools.py
from tools.lazy_deps import ensure, FeatureUnavailable

def my_tool_handler(args, **kwargs):
    try:
        ensure("my-plugin.my-backend")   # 键必须在 LAZY_DEPS 中
    except FeatureUnavailable as exc:
        return {"error": str(exc)}

    import my_backend_sdk   # 现在安全了
    ...
```

来自 `tools/lazy_deps.py` 安全模型的两条规则：

| 规则 | 原因 |
|---|---|
| 你的功能键必须出现在树内 `LAZY_DEPS` 允许列表中 | 防止恶意配置诱使 Hermes 安装任意包 — 只有 Hermes 自身提供的规格才符合条件 |
| 规格仅限 PyPI 按名称匹配 | 不支持 `--index-url`、`git+https://` 或 `file:` 路径。在允许列表条目内使用 PEP 440 固定版本（`"my-sdk>=1.2,<2"`） |

对于通过 pip 分发的第三方插件，请在你的 `pyproject.toml` 中将可选依赖声明为 `[project.optional-dependencies]` 附加项，并告诉用户 `pip install your-plugin[backend]` — 该路径不经过 `lazy_deps`。延迟安装机制对于**捆绑**插件最有用，因为在每次安装中包含硬依赖会膨胀基本的 Hermes 占用空间。

当全局设置 `security.allow_lazy_installs: false` 时，`ensure()` 会立即抛出 `FeatureUnavailable` 并附带修复提示 — 你的插件应该捕获它并优雅降级（返回错误结果，而不是使工具循环崩溃）。

### 线程安全的延迟单例

插件经常在模块级变量中缓存一个昂贵的对象 — SDK 客户端、HTTP 会话、连接池 — 在首次使用时构建：

```python
_client = None

def get_client():
    global _client
    if _client is not None:
        return _client
    _client = ExpensiveClient(...)   # ← TOCTOU 竞态条件
    return _client
```

这是一个隐患。Hermes 在单个进程中运行多个线程（分派的工具调用、后台工作线程、自我改进分支），因此两个线程可能在设置 `_client` 之前同时调用 `get_client()`，**都**通过 `is not None` 检查，**都**运行昂贵的构建，并且第二个写入覆盖第一个 — 泄漏失败者打开的任何资源（连接、文件句柄、后台线程）。

不要手动编写锁。使用 `plugins/plugin_utils.py` 中的辅助函数：

```python
from plugins.plugin_utils import lazy_singleton, SingletonSlot

# 零参数访问器 → 装饰它：
@lazy_singleton
def get_client():
    return ExpensiveClient(load_config())   # 恰好运行一次

client = get_client()    # 跨线程安全
get_client.reset()       # 丢弃实例（测试/清理）


# 接受构建参数的访问器 → 使用槽（slot）：
_slot: SingletonSlot = SingletonSlot()

def get_client(config=None):
    return _slot.get(lambda: ExpensiveClient(resolve(config)))

def reset_client():
    _slot.reset()
```

两者都通过双重检查锁定序列化并发的第一次调用，并且工厂最多运行一次。如果工厂抛出异常，不会缓存任何内容，下一次调用会重试。honcho 记忆插件（`plugins/memory/honcho/client.py`）是参考实现。

> 经验法则：每当你写下 `global _something` 后跟 `is None` 检查和构建时，请改用这些工具之一。

### 条件工具可用性

对于依赖于可选库的工具：

```python
ctx.register_tool(
    name="my_tool",
    schema={...},
    handler=my_handler,
    check_fn=lambda: _has_optional_lib(),  # False = 从模型中隐藏工具
)
```

### 覆盖内置工具

要用你自己的实现替换内置工具（例如，将默认浏览器工具替换为有头 Chrome CDP 后端，或将 `web_search` 替换为自定义企业索引），请传递 `override=True`：

```python
def register(ctx):
    ctx.register_tool(
        name="browser_navigate",             # 与内置工具同名
        toolset="plugin_my_browser",         # 你自己的工具集命名空间
        schema={...},
        handler=my_custom_navigate,
        override=True,                       # 显式选择加入
    )
```

如果没有 `override=True`，注册表会拒绝任何会遮蔽来自不同工具集的现有工具的注册 — 这可以防止意外覆盖。覆盖操作会以 INFO 级别记录，因此在 `~/.hermes/logs/agent.log` 中可审计。插件在内置工具之后加载，因此注册顺序是正确的：你的处理器替换了内置的。

### 注册多个钩子

```python
def register(ctx):
    ctx.register_hook("pre_tool_call", before_any_tool)
    ctx.register_hook("post_tool_call", after_any_tool)
    ctx.register_hook("pre_llm_call", inject_memory)
    ctx.register_hook("on_session_start", on_new_session)
    ctx.register_hook("on_session_end", on_session_end)
```

### 钩子参考

每个钩子的详细文档在 **[事件钩子参考](/user-guide/features/hooks#plugin-hooks)** 中 — 回调签名、参数表、每个钩子何时触发以及示例。以下是概要：

| 钩子 | 触发时机 | 回调签名 | 返回值 |
|------|-----------|-------------------|---------|
| [`pre_tool_call`](/user-guide/features/hooks#pre_tool_call) | 在任何工具执行之前 | `tool_name: str, args: dict, task_id: str` | 忽略 |
| [`post_tool_call`](/user-guide/features/hooks#post_tool_call) | 在任何工具返回之后 | `tool_name: str, args: dict, result: str, task_id: str, duration_ms: int` | 忽略 |
| [`pre_llm_call`](/user-guide/features/hooks#pre_llm_call) | 每轮一次，在工具调用循环之前 | `session_id: str, user_message: str, conversation_history: list, is_first_turn: bool, model: str, platform: str` | [上下文注入](#pre_llm_call-上下文注入) |
| [`post_llm_call`](/user-guide/features/hooks#post_llm_call) | 每轮一次，在工具调用循环之后（仅成功轮次） | `session_id: str, user_message: str, assistant_response: str, conversation_history: list, model: str, platform: str` | 忽略 |
| [`on_session_start`](/user-guide/features/hooks#on_session_start) | 创建新会话时（仅第一轮） | `session_id: str, model: str, platform: str` | 忽略 |
| [`on_session_end`](/user-guide/features/hooks#on_session_end) | 每次 `run_conversation` 调用结束时 + CLI 退出 | `session_id: str, completed: bool, interrupted: bool, model: str, platform: str` | 忽略 |
| [`on_session_finalize`](/user-guide/features/hooks#on_session_finalize) | CLI/网关拆除活动会话时 | `session_id: str \| None, platform: str` | 忽略 |
| [`on_session_reset`](/user-guide/features/hooks#on_session_reset) | 网关交换新会话键时（`/new`、`/reset`） | `session_id: str, platform: str` | 忽略 |
| `kanban_task_claimed` | 看板任务被认领时（调度器进程，在工作线程产生之前） | `task_id: str, board: str \| None, assignee: str \| None, run_id: int \| None, profile_name: str` | 忽略 |
| `kanban_task_completed` | 看板任务完成时（工作线程进程） | `task_id, board, assignee, run_id, profile_name, summary: str \| None` | 忽略 |
| `kanban_task_blocked` | 看板任务被阻塞时（工作线程进程） | `task_id, board, assignee, run_id, profile_name, reason: str \| None` | 忽略 |

大多数钩子是即用即弃的观察者——它们的返回值被忽略。例外是 `pre_llm_call`，它可以向对话注入上下文。

所有回调应该接受 `**kwargs` 以实现向前兼容。如果钩子回调崩溃，它会被记录并跳过。其他钩子和代理继续正常运行。

看板生命周期钩子在看板数据库更改提交**之后**触发，因此回调始终看到持久状态，并且永远不会持有 SQLite 写锁。由于看板工作线程作为独立的 `hermes -p <profile> chat -q` 子进程运行，`kanban_task_claimed` 在**调度器**进程中触发，而 `kanban_task_completed` / `kanban_task_blocked` 在**工作线程**进程中触发——在调度器中挂钩以集中观察每次转换，或在工作线程中挂钩以获得每个任务的会话内上下文。

### `pre_llm_call` 上下文注入

这是唯一一个返回值有意义的钩子。当 `pre_llm_call` 回调返回一个包含 `"context"` 键的字典（或纯字符串）时，Hermes 会将该文本注入到**当前轮次的用户消息**中。这是记忆插件、RAG 集成、护栏和任何需要向模型提供额外上下文的插件的机制。

#### 返回格式

```python
# 包含 context 键的字典
return {"context": "回忆的记忆:\n- 用户偏好深色模式\n- 上一个项目: hermes-agent"}

# 纯字符串（等同于上面的字典形式）
return "回忆的记忆:\n- 用户偏好深色模式"

# 返回 None 或不返回 → 不注入（仅观察者）
return None
```

任何非 None、非空且包含 `"context"` 键（或一个非空纯字符串）的返回值都会被收集并追加到当前轮次的用户消息中。

#### 注入如何工作

注入的上下文被追加到**用户消息**，而不是系统提示。这是经过深思熟虑的设计决策：

- **提示缓存保留** — 系统提示在各轮次之间保持不变。Anthropic 和 OpenRouter 会缓存系统提示前缀，因此保持其稳定可以在多轮对话中节省 75% 以上的输入 token。如果插件修改了系统提示，每一轮都会缓存未命中。
- **临时性** — 注入仅在 API 调用时发生。对话历史中的原始用户消息永远不会被修改，也不会持久化到会话数据库中。
- **系统提示是 Hermes 的领域** — 它包含模型特定的指导、工具执行规则、个性指令和缓存的技能内容。插件提供上下文时是与用户输入并行，而不是通过更改代理的核心指令。

#### 示例：记忆召回插件

```python
"""记忆插件 — 从向量存储中召回相关上下文。"""

import httpx

MEMORY_API = "https://your-memory-api.example.com"

def recall_context(session_id, user_message, is_first_turn, **kwargs):
    """在每次 LLM 轮次前调用。返回召回的回忆。"""
    try:
        resp = httpx.post(f"{MEMORY_API}/recall", json={
            "session_id": session_id,
            "query": user_message,
        }, timeout=3)
        memories = resp.json().get("results", [])
        if not memories:
            return None  # 无需注入

        text = "从先前会话中召回的上下文:\n"
        text += "\n".join(f"- {m['text']}" for m in memories)
        return {"context": text}
    except Exception:
        return None  # 静默失败，不要中断代理

def register(ctx):
    ctx.register_hook("pre_llm_call", recall_context)
```

#### 示例：护栏插件

```python
"""护栏插件 — 强制执行内容策略。"""

POLICY = """对于此会话，你 MUST 遵守以下内容策略：
- 切勿生成访问工作目录之外文件系统的代码
- 在执行破坏性操作前始终发出警告
- 拒绝涉及个人数据提取的请求"""

def inject_guardrails(**kwargs):
    """向每一轮注入策略文本。"""
    return {"context": POLICY}

def register(ctx):
    ctx.register_hook("pre_llm_call", inject_guardrails)
```

#### 示例：仅观察者钩子（无注入）

```python
"""分析插件 — 跟踪轮次元数据，不注入上下文。"""

import logging
logger = logging.getLogger(__name__)

def log_turn(session_id, user_message, model, is_first_turn, **kwargs):
    """在每次 LLM 调用前触发。返回 None — 不注入上下文。"""
    logger.info("轮次: session=%s model=%s first=%s msg_len=%d",
                session_id, model, is_first_turn, len(user_message or ""))
    # 无返回 → 不注入

def register(ctx):
    ctx.register_hook("pre_llm_call", log_turn)
```

#### 多个插件返回上下文

当多个插件从 `pre_llm_call` 返回上下文时，它们的输出会用双换行符连接并一起追加到用户消息中。顺序遵循插件发现顺序（按插件目录名称字母顺序）。

### 注册 CLI 命令

插件可以添加自己的 `hermes <plugin>` 子命令树：

```python
def _my_command(args):
    """hermes my-plugin <subcommand> 的处理器。"""
    sub = getattr(args, "my_command", None)
    if sub == "status":
        print("一切正常！")
    elif sub == "config":
        print("当前配置: ...")
    else:
        print("用法: hermes my-plugin <status|config>")

def _setup_argparse(subparser):
    """为 hermes my-plugin 构建 argparse 树。"""
    subs = subparser.add_subparsers(dest="my_command")
    subs.add_parser("status", help="显示插件状态")
    subs.add_parser("config", help="显示插件配置")
    subparser.set_defaults(func=_my_command)

def register(ctx):
    ctx.register_tool(...)
    ctx.register_cli_command(
        name="my-plugin",
        help="管理我的插件",
        setup_fn=_setup_argparse,
        handler_fn=_my_command,
    )
```

注册后，用户可以运行 `hermes my-plugin status`、`hermes my-plugin config` 等。

**记忆提供商插件**使用基于约定的方法：将 `register_cli(subparser)` 函数添加到插件的 `cli.py` 文件中。记忆插件发现系统会自动找到它 — 无需调用 `ctx.register_cli_command()`。有关详细信息，请参阅[记忆提供商插件指南](/developer-guide/memory-provider-plugin#adding-cli-commands)。

**活动提供商门控：** 记忆插件 CLI 命令仅在它们的提供商是配置中的活动 `memory.provider` 时显示。如果用户未设置你的提供商，你的 CLI 命令不会使帮助输出变得杂乱。

### 注册斜杠命令

插件可以注册会话内的斜杠命令 — 用户在对话期间键入的命令（如 `/lcm status` 或 `/ping`）。这些命令在 CLI 和网关（Telegram、Discord 等）中都有效。

```python
def _handle_status(raw_args: str) -> str:
    """/mystatus 的处理器 — 使用命令名称后的所有内容调用。"""
    if raw_args.strip() == "help":
        return "用法: /mystatus [help|check]"
    return "插件状态: 所有系统正常"

def register(ctx):
    ctx.register_command(
        "mystatus",
        handler=_handle_status,
        description="显示插件状态",
    )
```

注册后，用户可以在任何会话中键入 `/mystatus`。该命令会出现在自动完成、`/help` 输出和 Telegram 机器人菜单中。

**签名：** `ctx.register_command(name: str, handler: Callable, description: str = "", args_hint: str = "")`

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `name` | `str` | 不带前导斜杠的命令名称（例如 `"lcm"`、`"mystatus"`） |
| `handler` | `Callable[[str], str \| None]` | 用原始参数字符串调用。也可以是 `async`。 |
| `description` | `str` | 显示在 `/help`、自动完成和 Telegram 机器人菜单中 |

**与 `register_cli_command()` 的关键区别：**

| | `register_command()` | `register_cli_command()` |
|---|---|---|
| 调用方式 | 会话中的 `/name` | 终端中的 `hermes name` |
| 作用位置 | CLI 会话、Telegram、Discord 等 | 仅终端 |
| 处理器接收 | 原始参数字符串 | argparse `Namespace` |
| 使用场景 | 诊断、状态、快速操作 | 复杂子命令树、设置向导 |

**冲突保护：** 如果插件尝试注册与内置命令冲突的名称（`help`、`model`、`new` 等），注册会被静默拒绝并记录警告。内置命令始终优先。

**异步处理器：** 网关分派会自动检测并等待异步处理器，因此你可以使用同步或异步函数：

```python
async def _handle_check(raw_args: str) -> str:
    result = await some_async_operation()
    return f"检查结果: {result}"

def register(ctx):
    ctx.register_command("check", handler=_handle_check, description="运行异步检查")
```

### 从斜杠命令分派工具

需要编排工具（通过 `delegate_task` 产生子代理、调用 `file_edit` 等）的斜杠命令处理器应该使用 `ctx.dispatch_tool()` 而不是直接操作框架内部。父代理上下文（工作区提示、旋转器、模型继承）会自动连接。

```python
def register(ctx):
    def _handle_deliver(raw_args: str):
        result = ctx.dispatch_tool(
            "delegate_task",
            {
                "goal": raw_args,
                "toolsets": ["terminal", "file", "web"],
            },
        )
        return result

    ctx.register_command(
        "deliver",
        handler=_handle_deliver,
        description="将目标委托给子代理",
    )
```

**签名：** `ctx.dispatch_tool(name: str, args: dict, *, parent_agent=None) -> str`

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `name` | `str` | 工具名称，如工具注册表中注册的那样（例如 `"delegate_task"`、`"file_edit"`） |
| `args` | `dict` | 工具参数，与模型会发送的形状相同 |
| `parent_agent` | `Agent \| None` | 可选覆盖。省略时，从当前 CLI 代理解析（或在网关模式下优雅降级） |

**运行时行为：**

- **CLI 模式：** `parent_agent` 从活动 CLI 代理解析，因此工作区提示、旋转器和模型选择按预期继承。
- **网关模式：** 没有 CLI 代理，因此工具会优雅降级 — 工作区从配置的终端工作目录读取，并且不显示旋转器。
- **显式覆盖：** 如果调用者显式传递 `parent_agent=`，则该值会被尊重且不会被覆盖。

这是从插件命令分派工具的公共稳定接口。插件不应接触 `ctx._cli_ref.agent` 或类似的私有状态。

### 从钩子内部进行操作（配置文件名 + 工具）

`ctx._cli_ref` 仅在**交互式 CLI** 会话中填充。它在网关、非交互式 `hermes chat -q` 运行以及**看板产生的工作线程会话**中为 `None` — 因此任何通过 `_cli_ref` 的插件逻辑都会在那些上下文中静默无操作。两个稳定、与会话无关的 API 涵盖了钩子实际需要的功能：

- **`ctx.profile_name`** — 活动配置文件名称（例如 `"default"`，或在看板工作线程中为受指派人配置文件）。派生自 `HERMES_HOME`，因此在任何地方都能工作，不依赖 `_cli_ref`。
- **`ctx.dispatch_tool(name, args)`** — 调用任何已注册的工具（内置或插件），包括 `kanban_*` 工具、`delegate_task`、`terminal`、`read_file` 等。无论钩子在哪个进程中触发，都可以从钩子回调中工作。

这两者一起让看板生命周期钩子可以观察一次转换并在看板上采取行动，而无需接触框架内部：

```python
def register(ctx):
    def on_blocked(*, task_id, reason=None, **kw):
        # 在工作线程进程中运行；此处 ctx._cli_ref 为 None。
        ctx.dispatch_tool("kanban_comment", {
            "task_id": task_id,
            "comment": f"[{ctx.profile_name}] 自动记录阻塞: {reason}",
        })
    ctx.register_hook("kanban_task_blocked", on_blocked)
```

要运行完整的 `hermes <subcommand>`（例如 `hermes kanban show`），通过 `ctx.dispatch_tool("terminal", {"command": "hermes kanban show ..."})` 使用 `terminal` 工具进行 shell 调用 — 对于无头工作线程会话没有进程内斜杠命令桥接，而工具是从钩子驱动 Hermes 的受支持方式。

### 处理 Slack Block Kit 按钮点击

发布带有交互元素（按钮、溢出菜单、日期选择器等）的 Block Kit 消息的插件可以直接使用 Slack 适配器注册点击处理器 — 无需对 `slack_bolt.AsyncApp` 进行猴子补丁。

```python
def register(ctx):
    async def _on_approve(ack, body, action):
        # 在 3 秒内 ack — slack_bolt 要求。
        await ack()
        # body["channel"]["id"], body["user"]["id"], body["message"]["ts"]
        # action["action_id"], action["value"]
        sweep_id = (action.get("value") or "").split("|", 1)[-1]
        # ...执行确定性工作，然后发布后续消息。

    ctx.register_slack_action_handler("inbox_sweep_approve", _on_approve)
```

**签名：** `ctx.register_slack_action_handler(action_id, callback) -> None`

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `action_id` | `str \| re.Pattern \| dict` | `slack_bolt.App.action()` 接受的任何内容：字面 `action_id`、匹配多个 id 的编译正则表达式，或约束字典如 `{"action_id": "...", "block_id": "..."}` |
| `callback` | 异步可调用 | 按照 slack_bolt 约定接收 `(ack, body, action)` |

**运行时行为：**

- 处理器在插件加载时排队，并在 Slack 平台连接时挂接到适配器的 `slack_bolt.AsyncApp` 中。
- 每个回调都被防御性地包装：如果你的处理器抛出异常，网关会记录错误并尽力 ack 点击，以便 Slack 停止重试。
- 标准 slack_bolt 规则适用 — 在 3 秒内 `await ack()`，然后执行较长时间的工作。
- 对于多工作区部署，处理器会触发来自任何已连接工作区的点击；如果需要限定行为范围，使用 `body["team"]["id"]`。

这是插件参与 Slack 交互性的公共方式。较旧的插件可能会修补 `SlackAdapter.connect`；请优先使用此 API。

:::tip
本指南涵盖**通用插件**（工具、钩子、斜杠命令、CLI 命令）。下面的部分简要概述了每种专用插件类型的编写模式；每个部分都链接到其完整指南，以便查阅字段参考和示例。
:::

## 专用插件类型

除了通用表面之外，Hermes 还有五种专用的插件类型。每种类型都作为 `plugins/<category>/<name>/` 下的一个目录（捆绑）或 `~/.hermes/plugins/<category>/<name>/`（用户）提供。约定因类别而异 — 选择你需要的，然后阅读相应的完整指南。

### 模型提供商插件 — 添加 LLM 后端

将配置文件放入 `plugins/model-providers/<name>/`：

```python
# plugins/model-providers/acme/__init__.py
from providers import register_provider
from providers.base import ProviderProfile

register_provider(ProviderProfile(
    name="acme",
    aliases=("acme-inference",),
    display_name="Acme 推理服务",
    env_vars=("ACME_API_KEY", "ACME_BASE_URL"),
    base_url="https://api.acme.example.com/v1",
    auth_type="api_key",
    default_aux_model="acme-small-fast",
    fallback_models=("acme-large-v3", "acme-medium-v3"),
))
```

```yaml
# plugins/model-providers/acme/plugin.yaml
name: acme-provider
kind: model-provider
version: 1.0.0
description: Acme 推理 — 与 OpenAI 兼容的直接 API
```

在首次调用 `get_provider_profile()` 或 `list_providers()` 时延迟发现 — `auth.py`、`config.py`、`doctor.py`、`models.py`、`runtime_provider.py` 和 chat_completions 传输会自动连接到它。用户插件通过名称覆盖捆绑插件。

**完整指南：** [模型提供商插件](/developer-guide/model-provider-plugin) — 字段参考、可覆盖的钩子（`prepare_messages`、`build_extra_body`、`build_api_kwargs_extras`、`fetch_models`）、api_mode 选择、认证类型、测试。

### 平台插件 — 添加网关通道

将适配器放入 `plugins/platforms/<name>/`：

```python
# plugins/platforms/myplatform/adapter.py
from gateway.platforms.base import BasePlatformAdapter

class MyPlatformAdapter(BasePlatformAdapter):
    async def connect(self): ...
    async def send(self, chat_id, text): ...
    async def disconnect(self): ...

def check_requirements():
    import os
    return bool(os.environ.get("MYPLATFORM_TOKEN"))

def _env_enablement():
    import os
    tok = os.getenv("MYPLATFORM_TOKEN", "").strip()
    if not tok:
        return None
    return {"token": tok}

def register(ctx):
    ctx.register_platform(
        name="myplatform",
        label="MyPlatform",
        adapter_factory=lambda cfg: MyPlatformAdapter(cfg),
        check_fn=check_requirements,
        required_env=["MYPLATFORM_TOKEN"],
        # 自动从环境填充 PlatformConfig.extra，以便仅使用环境的设置
        # 在无需 SDK 实例化的情况下显示在 `hermes gateway status` 中。
        env_enablement_fn=_env_enablement,
        # 选择加入 cron 投递：`deliver=myplatform` 路由到此变量。
        cron_deliver_env_var="MYPLATFORM_HOME_CHANNEL",
        emoji="💬",
        platform_hint="你正在通过 MyPlatform 聊天。请保持回复简洁。",
    )
```

```yaml
# plugins/platforms/myplatform/plugin.yaml
name: myplatform-platform
label: MyPlatform
kind: platform
version: 1.0.0
description: MyPlatform 网关适配器
requires_env:
  - name: MYPLATFORM_TOKEN
    description: "MyPlatform 控制台的机器人令牌"
    password: true
optional_env:
  - name: MYPLATFORM_HOME_CHANNEL
    description: "cron 投递的默认频道"
    password: false
```

**完整指南：** [添加平台适配器](/developer-guide/adding-platform-adapters) — 完整的 `BasePlatformAdapter` 约定、消息路由、认证门控、设置向导集成。查看 `plugins/platforms/irc/` 以获取仅使用标准库的工作示例。

### 记忆提供商插件 — 添加跨会话知识后端

将 `MemoryProvider` 的实现放入 `plugins/memory/<name>/`：

```python
# plugins/memory/my-memory/__init__.py
from agent.memory_provider import MemoryProvider

class MyMemoryProvider(MemoryProvider):
    @property
    def name(self) -> str:
        return "my-memory"

    def is_available(self) -> bool:
        import os
        return bool(os.environ.get("MY_MEMORY_API_KEY"))

    def initialize(self, session_id: str, **kwargs) -> None:
        self._session_id = session_id

    def sync_turn(self, user_content, assistant_content, *,
                  session_id="", messages=None) -> None:
        ...

    def prefetch(self, query, *, session_id="") -> str:
        ...

    def get_tool_schemas(self) -> list[dict]:
        return []   # 必需的 @abstractmethod — 参见完整指南

def register(ctx):
    ctx.register_memory_provider(MyMemoryProvider())
```

记忆提供商是单选 — 一次只能激活一个，通过 `config.yaml` 中的 `memory.provider` 选择。

**完整指南：** [记忆提供商插件](/developer-guide/memory-provider-plugin) — 完整的 `MemoryProvider` ABC、线程约定、配置文件隔离、通过 `cli.py` 注册 CLI 命令。

### 上下文引擎插件 — 替换上下文压缩器

```python
# plugins/context_engine/my-engine/__init__.py
from agent.context_engine import ContextEngine

class MyContextEngine(ContextEngine):
    @property
    def name(self) -> str:
        return "my-engine"

    def update_from_response(self, usage) -> None: ...
    def should_compress(self, prompt_tokens: int = None) -> bool: ...
    def compress(self, messages, current_tokens=None, focus_topic=None) -> list: ...

def register(ctx):
    ctx.register_context_engine(MyContextEngine())
```

上下文引擎是单选 — 通过 `config.yaml` 中的 `context.engine` 选择。

**完整指南：** [上下文引擎插件](/developer-guide/context-engine-plugin)。

### 图像生成后端

将提供商放入 `plugins/image_gen/<name>/`：

```python
# plugins/image_gen/my-imggen/__init__.py
from agent.image_gen_provider import ImageGenProvider

class MyImageGenProvider(ImageGenProvider):
    @property
    def name(self) -> str:
        return "my-imggen"

    def is_available(self) -> bool: ...
    def generate(self, prompt: str, aspect_ratio="landscape", **kwargs) -> dict:
        # 返回 success_response(...) / error_response(...)
        ...

def register(ctx):
    ctx.register_image_gen_provider(MyImageGenProvider())
```

```yaml
# plugins/image_gen/my-imggen/plugin.yaml
name: my-imggen
kind: backend
version: 1.0.0
description: 自定义图像生成后端
```

**完整指南：** [图像生成提供商插件](/developer-guide/image-gen-provider-plugin) — 完整的 `ImageGenProvider` ABC、`list_models()` / `get_setup_schema()` 元数据、`success_response()`/`error_response()` 辅助函数、base64 vs URL 输出、用户覆盖、pip 分发。

**参考示例：** `plugins/image_gen/openai/`（通过 OpenAI SDK 的 DALL-E / GPT-Image）、`plugins/image_gen/openai-codex/`、`plugins/image_gen/xai/`（Grok 图像生成）。

## 非 Python 扩展表面

Hermes 也接受根本不是 Python 插件的扩展。这些在[可插拔接口表](/user-guide/features/plugins#pluggable-interfaces--where-to-go-for-each)中列出；下面的部分简要描述了每种编写风格。

### MCP 服务器 — 注册外部工具

模型上下文协议（MCP）服务器将自己的工具注册到 Hermes，无需任何 Python 插件。在 `~/.hermes/config.yaml` 中声明它们：

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
    timeout: 120

  linear:
    url: "https://mcp.linear.app/sse"
    auth:
      type: "oauth"
```

Hermes 在启动时连接到每个服务器，列出其工具，并将它们与内置工具一起注册。LLM 像对待任何其他工具一样看待它们。**完整指南：** [MCP](/user-guide/features/mcp)。

### 网关事件钩子 — 在生命周期事件时触发

将清单和处理器放入 `~/.hermes/hooks/<name>/`：

```yaml
# ~/.hermes/hooks/long-task-alert/HOOK.yaml
name: long-task-alert
description: 长时间任务完成时发送推送通知
events:
  - agent:end
```

```python
# ~/.hermes/hooks/long-task-alert/handler.py
async def handle(event_type: str, context: dict) -> None:
    if context.get("duration_seconds", 0) > 120:
        # 发送通知 …
        pass
```

事件包括 `gateway:startup`、`session:start`、`session:end`、`session:reset`、`agent:start`、`agent:step`、`agent:end` 和通配符 `command:*`。钩子中的错误会被捕获并记录 — 它们不会阻塞主流水线。

**完整指南：** [网关事件钩子](/user-guide/features/hooks#gateway-event-hooks)。

### Shell 钩子 — 在工具调用时运行 shell 命令

如果你只想在工具触发时运行一个脚本（通知、审计日志、桌面提醒、自动格式化工具），请在 `config.yaml` 中使用 shell 钩子 — 无需 Python：

```yaml
hooks:
  - event: post_tool_call
    command: "notify-send '工具运行了: {tool_name}'"
    when:
      tools: [terminal, patch, write_file]
```

支持与 Python 插件钩子相同的事件（`pre_tool_call`、`post_tool_call`、`pre_llm_call`、`post_llm_call`、`on_session_start`、`on_session_end`、`pre_gateway_dispatch`）以及用于 `pre_tool_call` 阻止决策的结构化 JSON 输出。

**完整指南：** [Shell 钩子](/user-guide/features/hooks#shell-hooks)。

### 技能来源 — 添加自定义技能注册表

如果你维护一个技能 GitHub 仓库（或想从内置来源之外的社区索引拉取），将它添加为一个 **tap**：

```bash
hermes skills tap add myorg/skills-repo
hermes skills search my-workflow --source myorg/skills-repo
hermes skills install myorg/skills-repo/my-workflow
```

发布你自己的 tap 只是一个带有 `skills/<skill-name>/SKILL.md` 目录的 GitHub 仓库 — 无需服务器或注册表注册。

**完整指南：** [技能中心](/user-guide/features/skills#skills-hub) · [发布自定义 tap](/user-guide/features/skills#publishing-a-custom-skill-tap)（仓库布局、最小示例、非默认路径、信任级别）。

### 通过命令模板的 TTS / STT

任何读/写音频或文本的 CLI 都可以通过 `config.yaml` 插入 — 无需 Python 代码：

```yaml
tts:
  provider: voxcpm
  providers:
    voxcpm:
      type: command
      command: "voxcpm --ref ~/voice.wav --text-file {input_path} --out {output_path}"
      output_format: mp3
      voice_compatible: true
```

对于 STT，将 `HERMES_LOCAL_STT_COMMAND` 指向一个 shell 模板。支持的占位符：`{input_path}`、`{output_path}`、`{format}`、`{voice}`、`{model}`、`{speed}`（TTS）；`{input_path}`、`{output_dir}`、`{language}`、`{model}`（STT）。任何与路径交互的 CLI 都会自动成为插件。

**完整指南：** [TTS 自定义命令提供商](/user-guide/features/tts#custom-command-providers) · [STT](/user-guide/features/tts#voice-message-transcription-stt)。

## 通过 pip 分发

要公开分享插件，请将入口点添加到你的 Python 包中：

```toml
# pyproject.toml
[project.entry-points."hermes_agent.plugins"]
my-plugin = "my_plugin_package"
```

```bash
pip install hermes-plugin-calculator
# 下次启动 Hermes 时自动发现插件
```

## 为 NixOS 分发

如果你提供带有入口点的 `pyproject.toml`，NixOS 用户可以通过声明方式安装你的插件：

**入口点插件（推荐用于分发）：**
```nix
# 用户的 configuration.nix
services.hermes-agent.extraPythonPackages = [
  (pkgs.python312Packages.buildPythonPackage {
    pname = "my-plugin";
    version = "1.0.0";
    src = pkgs.fetchFromGitHub {
      owner = "you";
      repo = "hermes-my-plugin";
      rev = "v1.0.0";
      hash = "sha256-...";  # nix-prefetch-url --unpack
    };
    format = "pyproject";
    build-system = [ pkgs.python312Packages.setuptools ];
  })
];
```

**目录插件（无需 `pyproject.toml`）：**
```nix
services.hermes-agent.extraPlugins = [
  (pkgs.fetchFromGitHub {
    owner = "you";
    repo = "hermes-my-plugin";
    rev = "v1.0.0";
    hash = "sha256-...";
  })
];
```

有关包括覆盖使用和冲突检查在内的完整文档，请参阅 [Nix 设置指南](/getting-started/nix-setup#plugins)。

## 常见错误

**处理器不返回 JSON 字符串：**
```python
# 错误 — 返回字典
def handler(args, **kwargs):
    return {"result": 42}

# 正确 — 返回 JSON 字符串
def handler(args, **kwargs):
    return json.dumps({"result": 42})
```

**处理器签名中缺少 `**kwargs`：**
```python
# 错误 — 如果 Hermes 传递额外上下文会崩溃
def handler(args):
    ...

# 正确
def handler(args, **kwargs):
    ...
```

**处理器抛出异常：**
```python
# 错误 — 异常传播，工具调用失败
def handler(args, **kwargs):
    result = 1 / int(args["value"])  # ZeroDivisionError!
    return json.dumps({"result": result})

# 正确 — 捕获并返回错误 JSON
def handler(args, **kwargs):
    try:
        result = 1 / int(args.get("value", 0))
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": str(e)})
```

**模式描述过于模糊：**
```python
# 错误 — 模型不知道何时使用
"description": "做事情"

# 正确 — 模型清楚知道何时以及如何使用
"description": "计算一个数学表达式。用于算术、三角、对数。支持: +, -, *, /, **, sqrt, sin, cos, log, pi, e."
```