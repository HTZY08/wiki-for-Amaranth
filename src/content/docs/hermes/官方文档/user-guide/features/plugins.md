---
title: Plugins
---

sidebar_position: 11
sidebar_label: "插件"
title: "插件"
description: "通过插件系统使用自定义工具、钩子（Hook）和集成来扩展 Hermes 的功能"
---

# 插件

Hermes 拥有一个插件系统，用于添加自定义工具、钩子和集成，而无需修改核心代码。

如果你想为自己、团队或某个项目创建自定义工具，这通常是一条正确的路径。开发者指南中的[添加工具](/developer-guide/adding-tools)页面针对的是内置于 Hermes 核心、位于 `tools/` 和 `toolsets.py` 中的工具。

**→ [构建一个 Hermes 插件](/guides/build-a-hermes-plugin)** —— 包含完整工作示例的逐步指南。

## 快速概览

将一个包含 `plugin.yaml` 和 Python 代码的目录放入 `~/.hermes/plugins/`：

```
~/.hermes/plugins/my-plugin/
├── plugin.yaml      # 清单文件
├── __init__.py      # register() 函数 —— 将模式（schema）连接到处理程序（handler）
├── schemas.py       # 工具模式（LLM 看到的）
└── tools.py         # 工具处理程序（被调用时执行的内容）
```

启动 Hermes —— 你的工具会与内置工具一起出现。模型可以立即调用它们。

### 最小工作示例

以下是一个完整的插件，它添加了一个 `hello_world` 工具，并通过钩子记录每次工具调用。

**`~/.hermes/plugins/hello-world/plugin.yaml`**

```yaml
name: hello-world
version: "1.0"
description: 一个最小示例插件
```

**`~/.hermes/plugins/hello-world/__init__.py`**

```python
"""最小化的 Hermes 插件 —— 注册一个工具和一个钩子。"""

import json


def register(ctx):
    # --- 工具: hello_world ---
    schema = {
        "name": "hello_world",
        "description": "为给定的名称返回一个友好的问候。",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "要问候的名称",
                }
            },
            "required": ["name"],
        },
    }

    def handle_hello(params, **kwargs):
        del kwargs
        name = params.get("name", "World")
        return json.dumps({"success": True, "greeting": f"Hello, {name}!"})

    ctx.register_tool(
        name="hello_world",
        toolset="hello_world",
        schema=schema,
        handler=handle_hello,
        description="为给定的名称返回一个友好的问候。",
    )

    # --- 钩子: 记录每次工具调用 ---
    def on_tool_call(tool_name, params, result):
        print(f"[hello-world] 工具被调用: {tool_name}")

    ctx.register_hook("post_tool_call", on_tool_call)
```

将这两个文件放入 `~/.hermes/plugins/hello-world/`，重启 Hermes，模型就可以立即调用 `hello_world`。每次工具调用后，钩子会打印一条日志。

项目本地的插件位于 `./.hermes/plugins/` 下，默认是禁用的。要启用它们，仅限受信任的仓库，请在启动 Hermes 前设置 `HERMES_ENABLE_PROJECT_PLUGINS=true`。

## 插件能做什么

在插件的 `register(ctx)` 函数内部，可以使用以下所有 `ctx.*` API。

| 能力 | 方法 |
|-----------|-----|
| 添加工具 | `ctx.register_tool(name=..., toolset=..., schema=..., handler=...)` |
| 添加钩子 | `ctx.register_hook("post_tool_call", callback)` |
| 添加斜杠命令 | `ctx.register_command(name, handler, description)` —— 在 CLI 和网关会话中添加 `/name` 命令 |
| 从命令调度工具 | `ctx.dispatch_tool(name, args)` —— 调用已注册的工具，自动注入父 Agent 上下文 |
| 添加 CLI 命令 | `ctx.register_cli_command(name, help, setup_fn, handler_fn)` —— 添加 `hermes <plugin> <subcommand>` |
| 注入消息 | `ctx.inject_message(content, role="user")` —— 参见[注入消息](#injecting-messages) |
| 附带数据文件 | `Path(__file__).parent / "data" / "file.yaml"` |
| 捆绑技能（Skill） | `ctx.register_skill(name, path)` —— 命名空间为 `plugin:skill`，通过 `skill_view("plugin:skill")` 加载 |
| 基于环境变量门控 | 在 plugin.yaml 中设置 `requires_env: [API_KEY]` —— 在 `hermes plugins install` 提示 |
| 通过 pip 分发 | `[project.entry-points."hermes_agent.plugins"]` |
| 注册网关平台（Discord、Telegram、IRC 等） | `ctx.register_platform(name, label, adapter_factory, check_fn, ...)` —— 参见[添加平台适配器](/developer-guide/adding-platform-adapters) |
| 注册图像生成后端 | `ctx.register_image_gen_provider(provider)` —— 参见[图像生成提供者插件](/developer-guide/image-gen-provider-plugin) |
| 注册视频生成后端 | `ctx.register_video_gen_provider(provider)` —— 参见[视频生成提供者插件](/developer-guide/video-gen-provider-plugin) |
| 注册上下文压缩引擎 | `ctx.register_context_engine(engine)` —— 参见[上下文引擎插件](/developer-guide/context-engine-plugin) |
| 注册记忆后端 | 在 `plugins/memory/<name>/__init__.py` 中继承 `MemoryProvider` —— 参见[记忆提供者插件](/developer-guide/memory-provider-plugin)（使用独立的发现系统） |
| 发起宿主拥有的 LLM 调用 | `ctx.llm.complete(...)` / `ctx.llm.complete_structured(...)` —— 借用用户的活动模型 + 认证进行一次一次性补全，可带可选 JSON schema 验证。参见[插件 LLM 访问](/developer-guide/plugin-llm-access) |
| 注册推理后端（LLM 提供者） | 在 `plugins/model-providers/<name>/__init__.py` 中调用 `register_provider(ProviderProfile(...))` —— 参见[模型提供者插件](/developer-guide/model-provider-plugin)（使用独立的发现系统） |

## 插件发现

| 来源 | 路径 | 用途 |
|--------|------|----------|
| 捆绑 | `<repo>/plugins/` | Hermes 自带 —— 参见[内置插件](/user-guide/features/built-in-plugins) |
| 用户 | `~/.hermes/plugins/` | 个人插件 |
| 项目 | `.hermes/plugins/` | 项目特定插件（需要 `HERMES_ENABLE_PROJECT_PLUGINS=true`） |
| pip | `hermes_agent.plugins` entry_points | 分发包 |
| Nix | `services.hermes-agent.extraPlugins` / `extraPythonPackages` | NixOS 声明式安装 —— 参见[Nix 设置](/getting-started/nix-setup#plugins) |

后面的来源在名称冲突时会覆盖前面的，因此与捆绑插件同名的用户插件会替换它。

### 插件子类别

在每个来源中，Hermes 还会识别子类别目录，这些目录将插件路由到专门的发现系统：

| 子目录 | 包含内容 | 发现系统 |
|---|---|---|
| `plugins/`（根） | 通用插件 —— 工具、钩子、斜杠命令、CLI 命令、捆绑技能 | `PluginManager`（kind: `standalone` 或 `backend`） |
| `plugins/platforms/<name>/` | 网关通道适配器（`ctx.register_platform()`） | `PluginManager`（kind: `platform`，深一层） |
| `plugins/image_gen/<name>/` | 图像生成后端（`ctx.register_image_gen_provider()`） | `PluginManager`（kind: `backend`，深一层） |
| `plugins/memory/<name>/` | 记忆提供者（继承 `MemoryProvider`） | **自有加载器** 在 `plugins/memory/__init__.py`（kind: `exclusive` —— 一次只激活一个） |
| `plugins/context_engine/<name>/` | 上下文压缩引擎（`ctx.register_context_engine()`） | **自有加载器** 在 `plugins/context_engine/__init__.py`（一次只激活一个） |
| `plugins/model-providers/<name>/` | LLM 提供者配置文件（`register_provider(ProviderProfile(...))`） | **自有加载器** 在 `providers/__init__.py`（在首次 `get_provider_profile()` 调用时延迟扫描） |

位于 `~/.hermes/plugins/model-providers/<name>/` 和 `~/.hermes/plugins/memory/<name>/` 的用户插件会覆盖同名的捆绑插件 —— 在 `register_provider()` / `register_memory_provider()` 中遵循“后写者胜出”规则。只需放置一个目录，它就会替换内置插件，无需编辑仓库。

## 插件是选用的（少数例外）

**通用插件和用户安装的后端默认禁用** —— 发现（Discovery）会找到它们（因此它们会出现在 `hermes plugins` 和 `/plugins` 中），但除非你将插件名称添加到 `~/.hermes/config.yaml` 的 `plugins.enabled` 中，否则不会加载任何带有钩子或工具的内容。这可以防止未经你明确同意就运行第三方代码。

```yaml
plugins:
  enabled:
    - my-tool-plugin
    - disk-cleanup
  disabled:       # 可选拒绝列表 —— 如果名称同时出现在两个列表中，则此列表优先
    - noisy-plugin
```

三种切换状态的方式：

```bash
hermes plugins                    # 交互式切换（空格键选中/取消选中）
hermes plugins enable <name>      # 添加到允许列表
hermes plugins disable <name>     # 从允许列表移除并添加到禁用列表
```

在 `hermes plugins install owner/repo` 之后，系统会询问 `现在启用 'name' 吗？ [y/N]` —— 默认选择否。对于脚本安装，可以使用 `--enable` 或 `--no-enable` 跳过提示。

### 允许列表不控制的内容

有几类插件会绕过 `plugins.enabled` —— 它们是 Hermes 内置功能的一部分，如果默认禁用，会破坏基本功能。

| 插件类型 | 替代激活方式 |
|---|---|
| **捆绑的平台插件**（IRC、Teams 等位于 `plugins/platforms/` 下） | 自动加载，因此所有自带的网关通道都可用。实际通道通过 `config.yaml` 中的 `gateway.platforms.<name>.enabled` 开启。 |
| **捆绑的后端**（位于 `plugins/image_gen/` 下的图像生成提供者等） | 自动加载，因此默认后端“开箱即用”。通过 `config.yaml` 中的 `<category>.provider` 选择（例如 `image_gen.provider: openai`）。 |
| **记忆提供者**（`plugins/memory/`） | 所有已发现的提供者中，恰好有一个处于激活状态，由 `config.yaml` 中的 `memory.provider` 选择。 |
| **上下文引擎**（`plugins/context_engine/`） | 所有已发现的引擎中，有一个处于激活状态，由 `config.yaml` 中的 `context.engine` 选择。 |
| **模型提供者**（`plugins/model-providers/`） | `plugins/model-providers/` 下的所有捆绑提供者会在首次 `get_provider_profile()` 调用时被发现并注册。用户通过 `--provider` 或 `config.yaml` 一次选择一个。 |
| **通过 pip 安装的 `backend` 插件** | 通过 `plugins.enabled` 选择加入（与通用插件相同）。 |
| **用户安装的平台**（位于 `~/.hermes/plugins/platforms/` 下） | 通过 `plugins.enabled` 选择加入 —— 第三方网关适配器需要明确同意。 |

简而言之：**捆绑的“始终可用”基础设施会自动加载；第三方通用插件需要选择加入。** `plugins.enabled` 允许列表专门用于用户放入 `~/.hermes/plugins/` 的任意代码的门控。

### 现有用户的迁移

当你升级到具有选择加入插件的 Hermes 版本（配置 schema v21+）时，任何已经安装在 `~/.hermes/plugins/` 下且尚未在 `plugins.disabled` 中的用户插件都会**自动继承**到 `plugins.enabled` 中。你现有的设置将继续工作。捆绑的独立插件不会自动继承 —— 即使是现有用户也必须明确选择加入。（捆绑的平台/后端插件从未需要自动继承，因为它们从未被门控过。）

## 可用的钩子

插件可以为这些生命周期事件注册回调。有关完整细节、回调签名和示例，请参阅 **[事件钩子页面](/user-guide/features/hooks#plugin-hooks)**。

| 钩子 | 触发时机 |
|------|-----------|
| [`pre_tool_call`](/user-guide/features/hooks#pre_tool_call) | 在任何工具执行之前 |
| [`post_tool_call`](/user-guide/features/hooks#post_tool_call) | 在任何工具返回之后 |
| [`pre_llm_call`](/user-guide/features/hooks#pre_llm_call) | 每轮一次，在 LLM 循环之前 —— 可以返回 `{"context": "..."}` 以[将上下文注入到用户消息](/user-guide/features/hooks#pre_llm_call)中 |
| [`post_llm_call`](/user-guide/features/hooks#post_llm_call) | 每轮一次，在 LLM 循环之后（仅成功的轮次） |
| [`on_session_start`](/user-guide/features/hooks#on_session_start) | 新会话创建时（仅第一轮） |
| [`on_session_end`](/user-guide/features/hooks#on_session_end) | 每次 `run_conversation` 调用结束时 + CLI 退出处理器 |
| [`on_session_finalize`](/user-guide/features/hooks#on_session_finalize) | CLI/网关拆除活动会话时（`/new`、GC、CLI 退出） |
| [`on_session_reset`](/user-guide/features/hooks#on_session_reset) | 网关更换新会话密钥时（`/new`、`/reset`、`/clear`、空闲轮换） |
| [`subagent_stop`](/user-guide/features/hooks#subagent_stop) | 每个子 Agent 在 `delegate_task` 完成之后触发一次 |
| [`pre_gateway_dispatch`](/user-guide/features/hooks#pre_gateway_dispatch) | 网关收到用户消息后，认证和调度之前。返回 `{"action": "skip" \| "rewrite" \| "allow", ...}` 以影响流程。 |

## 插件类型

Hermes 有四种插件：

| 类型 | 功能 | 选择方式 | 位置 |
|------|-------------|-----------|----------|
| **通用插件** | 添加工具、钩子、斜杠命令、CLI 命令 | 多选（启用/禁用） | `~/.hermes/plugins/` |
| **记忆提供者** | 替换或增强内置记忆 | 单选（一次激活一个） | `plugins/memory/` |
| **上下文引擎** | 替换内置上下文压缩器 | 单选（一次激活一个） | `plugins/context_engine/` |
| **模型提供者** | 声明推理后端（OpenRouter、Anthropic 等） | 多注册，通过 `--provider` / `config.yaml` 选择 | `plugins/model-providers/` |

记忆提供者和上下文引擎是**提供者插件** —— 每种类型一次只能有一个处于激活状态。模型提供者也是插件，但多个可以同时加载；用户通过 `--provider` 或 `config.yaml` 一次选择一个。通用插件可以任意组合启用。

## 可插拔接口 —— 每种需求对应路径

上表显示了四种插件类别，但在“通用插件”内部，`PluginContext` 暴露了多个不同的扩展点 —— 并且 Hermes 也接受 Python 插件系统之外的扩展（配置驱动后端、shell 钩子命令、外部服务器等）。使用下表找到你想构建的内容对应的正确文档：

| 想添加... | 方法 | 编写指南 |
|---|---|---|
| LLM 可以调用的**工具** | Python 插件 —— `ctx.register_tool()` | [构建一个 Hermes 插件](/guides/build-a-hermes-plugin) · [添加工具](/developer-guide/adding-tools) |
| **生命周期钩子**（LLM 前后、会话开始/结束、工具过滤器） | Python 插件 —— `ctx.register_hook()` | [钩子参考](/user-guide/features/hooks) · [构建一个 Hermes 插件](/guides/build-a-hermes-plugin) |
| CLI / 网关的**斜杠命令** | Python 插件 —— `ctx.register_command()` | [构建一个 Hermes 插件](/guides/build-a-hermes-plugin) · [扩展 CLI](/developer-guide/extending-the-cli) |
| `hermes <thing>` 的**子命令** | Python 插件 —— `ctx.register_cli_command()` | [扩展 CLI](/developer-guide/extending-the-cli) |
| 插件附带的**捆绑技能** | Python 插件 —— `ctx.register_skill()` | [创建技能](/developer-guide/creating-skills) |
| **推理后端**（LLM 提供者：OpenAI 兼容、Codex、Anthropic-Messages、Bedrock） | 提供者插件 —— 在 `plugins/model-providers/<name>/` 中调用 `register_provider(ProviderProfile(...))` | **[模型提供者插件](/developer-guide/model-provider-plugin)** · [添加提供者](/developer-guide/adding-providers) |
| **网关通道**（Discord / Telegram / IRC / Teams 等） | 平台插件 —— 在 `plugins/platforms/<name>/` 中调用 `ctx.register_platform()` | [添加平台适配器](/developer-guide/adding-platform-adapters) |
| **记忆后端**（Honcho、Mem0、Supermemory 等） | 记忆插件 —— 在 `plugins/memory/<name>/` 中继承 `MemoryProvider` | [记忆提供者插件](/developer-guide/memory-provider-plugin) |
| **上下文压缩策略** | 上下文引擎插件 —— `ctx.register_context_engine()` | [上下文引擎插件](/developer-guide/context-engine-plugin) |
| **图像生成后端**（DALL·E、SDXL 等） | 后端插件 —— `ctx.register_image_gen_provider()` | [图像生成提供者插件](/developer-guide/image-gen-provider-plugin) |
| **视频生成后端**（Veo、Kling、Pixverse、Grok-Imagine、Runway 等） | 后端插件 —— `ctx.register_video_gen_provider()` | [视频生成提供者插件](/developer-guide/video-gen-provider-plugin) |
| **TTS 后端**（任意 CLI —— Piper、VoxCPM、Kokoro、xtts、语音克隆脚本等） | 配置驱动（推荐） —— 在 `config.yaml` 的 `tts.providers.<name>` 中声明，类型为 `type: command`。或 Python 后端插件 —— 对于需要更复杂模板的 Python SDK / 流式引擎，使用 `ctx.register_tts_provider()`。 | [TTS 设置](/user-guide/features/tts#custom-command-providers) · [Python 插件指南](/user-guide/features/tts#python-plugin-providers) |
| **STT 后端**（任意 CLI —— whisper.cpp、自定义 whisper 二进制、本地 ASR CLI） | 配置驱动（推荐） —— 在 `config.yaml` 的 `stt.providers.<name>` 中声明，类型为 `type: command`，或设置 `HERMES_LOCAL_STT_COMMAND` 作为旧版单命令逃生出口。或 Python 后端插件 —— 对于 Python SDK 引擎（OpenRouter、SenseAudio、Gemini-STT 等），使用 `ctx.register_transcription_provider()`。 | [STT 设置](/user-guide/features/tts#stt-custom-command-providers) · [Python 插件指南](/user-guide/features/tts#python-plugin-providers-stt) |
| **通过 MCP 的外部工具**（文件系统、GitHub、Linear、Notion、任意 MCP 服务器） | 配置驱动 —— 在 `config.yaml` 中声明 `mcp_servers.<name>`，带有 `command:` / `url:`。Hermes 自动发现服务器的工具并与内置工具一起注册。 | [MCP](/user-guide/features/mcp) |
| **额外的技能来源**（自定义 GitHub 仓库、私有技能索引） | CLI —— `hermes skills tap add <repo>` | [技能中心](/user-guide/features/skills#skills-hub) · [发布自定义 tap](/user-guide/features/skills#publishing-a-custom-skill-tap) |
| **网关事件钩子**（在 `gateway:startup`、`session:start`、`agent:end`、`command:*` 时触发） | 将 `HOOK.yaml` + `handler.py` 放入 `~/.hermes/hooks/<name>/` | [事件钩子](/user-guide/features/hooks#gateway-event-hooks) |
| **Shell 钩子**（在事件上运行 shell 命令 —— 通知、审计日志、桌面提醒） | 配置驱动 —— 在 `config.yaml` 中的 `hooks:` 下声明 | [Shell 钩子](/user-guide/features/hooks#shell-hooks) |

:::note
并非所有扩展都是 Python 插件。有些扩展表面有意使用**配置驱动的 shell 命令**（TTS、STT、shell 钩子），这样你已有的任何 CLI 都无需编写 Python 即可成为插件。另一些是**外部服务器**（MCP），Agent 连接后自动注册工具。还有一些是**直接目录放置**（网关钩子），有自己独立的清单格式。根据适合你用例的集成风格选择正确的扩展点；上表中的编写指南都涵盖了占位符、发现和示例。
:::

## NixOS 声明式插件

在 NixOS 上，可以通过模块选项声明式安装插件 —— 无需 `hermes plugins install`。完整细节请参阅 **[Nix 设置指南](/getting-started/nix-setup#plugins)**。

```nix
services.hermes-agent = {
  # 目录插件（包含 plugin.yaml 的源代码树）
  extraPlugins = [ (pkgs.fetchFromGitHub { ... }) ];
  # 入口点插件（pip 包）
  extraPythonPackages = [ (pkgs.python312Packages.buildPythonPackage { ... }) ];
  # 在配置中启用
  settings.plugins.enabled = [ "my-plugin" ];
};
```

声明式插件使用 `nix-managed-` 前缀进行符号链接 —— 它们与手动安装的插件共存，当从 Nix 配置中移除时会自动清理。

## 管理插件

```bash
hermes plugins                               # 统一交互式界面
hermes plugins list                          # 表格：已启用 / 已禁用 / 未启用
hermes plugins install user/repo             # 从 Git 安装，然后提示 启用？ [y/N]
hermes plugins install user/repo --enable    # 安装并启用（无提示）
hermes plugins install user/repo --no-enable # 安装但保持禁用（无提示）
hermes plugins update my-plugin              # 拉取最新版本
hermes plugins remove my-plugin              # 卸载
hermes plugins enable my-plugin              # 添加到允许列表
hermes plugins disable my-plugin             # 从允许列表移除并添加到禁用列表
```

### 交互式界面

运行 `hermes plugins`（不带参数）会打开一个复合交互屏幕：

```
插件
  ↑↓ 导航  SPACE 切换  ENTER 配置/确认  ESC 完成

  通用插件
 → [✓] my-tool-plugin — 自定义搜索工具
   [ ] webhook-notifier — 事件钩子
   [ ] disk-cleanup — 自动清理临时文件 [捆绑]

  提供者插件
     记忆提供者          ▸ honcho
     上下文引擎           ▸ compressor
```

- **通用插件部分** —— 复选框，用 SPACE 切换。选中 = 在 `plugins.enabled` 中，未选中 = 在 `plugins.disabled` 中（显式关闭）。
- **提供者插件部分** —— 显示当前选择。按 ENTER 进入单选选择器，在其中选择一个活跃提供者。
- 捆绑插件出现在同一列表中，带有 `[捆绑]` 标签。

提供者插件选择保存在 `config.yaml` 中：

```yaml
memory:
  provider: "honcho"      # 空字符串 = 仅内置

context:
  engine: "compressor"    # 默认内置压缩器
```

### 已启用 vs. 已禁用 vs. 未启用

插件处于三种状态之一：

| 状态 | 含义 | 在 `plugins.enabled` 中？ | 在 `plugins.disabled` 中？ |
|---|---|---|---|
| `已启用` | 下次会话加载 | 是 | 否 |
| `已禁用` | 显式关闭 —— 即使也在 `enabled` 中也不会加载 | （无关） | 是 |
| `未启用` | 已发现但从未选择加入 | 否 | 否 |

新安装的插件或捆绑插件的默认状态是 `未启用`。`hermes plugins list` 会显示所有三种不同状态，这样你就能分辨哪些是明确关闭的，哪些只是等待启用。

在运行中的会话中，`/plugins` 显示当前加载了哪些插件。

## 注入消息

插件可以使用 `ctx.inject_message()` 向活动对话中注入消息：

```python
ctx.inject_message("来自 webhook 的新数据已到达", role="user")
```

**签名：** `ctx.inject_message(content: str, role: str = "user") -> bool`

工作原理：

- 如果 Agent **空闲**（等待用户输入），则消息排队作为下一个输入并开始新的一轮。
- 如果 Agent **处于一轮中**（正在运行），则消息会中断当前操作 —— 就像用户输入新消息并按回车键一样。
- 对于非 `"user"` 角色，内容前缀为 `[role]`（例如 `[system] ...`）。
- 如果消息排队成功则返回 `True`，如果没有可用的 CLI 引用（例如在网关模式下）则返回 `False`。

这使得远程控制查看器、消息桥接或 webhook 接收器之类的插件能够从外部源向对话中注入消息。

:::note
`inject_message` 仅在 CLI 模式下可用。在网关模式下，没有 CLI 引用，该方法返回 `False`。
:::

有关处理器约定、schema 格式、钩子行为、错误处理和常见错误的完整指南，请参阅**[完整指南](/guides/build-a-hermes-plugin)**。