---
title: Model Provider Plugin
---

sidebar_position: 10
title: "模型提供插件"
description: "如何为 Hermes Agent 构建模型提供者（推理后端）插件"
---

--- body ---
# 构建模型提供插件

模型提供插件声明一个推理后端（inference backend）——一个与 OpenAI 兼容的端点、Anthropic Messages 服务器、Codex 风格的 Responses API 或 Bedrock 原生接口——Hermes 可通过这些后端路由 `AIAgent` 调用。每个内置提供者（OpenRouter、Anthropic、GMI、DeepSeek、Nvidia……）都是以这些插件的形式提供的。第三方可以通过在 `$HERMES_HOME/plugins/model-providers/` 下放置一个目录来添加自己的插件，无需对仓库进行任何更改。

:::tip
模型提供插件是第三种**提供插件（provider plugin）**。其他两类是[记忆提供插件](/developer-guide/memory-provider-plugin)（跨会话知识）和[上下文引擎插件](/developer-guide/context-engine-plugin)（上下文压缩策略）。这三类都遵循相同的模式：“放置一个目录，声明一个配置文件，无需编辑仓库”。
:::

## 发现机制

`providers/__init__.py._discover_providers()` 在代码首次调用 `get_provider_profile()` 或 `list_providers()` 时惰性执行。发现顺序：

1. **捆绑插件** — `<repo>/plugins/model-providers/<name>/` — 随 Hermes 一起提供
2. **用户插件** — `$HERMES_HOME/plugins/model-providers/<name>/` — 可放入任意目录；后续会话无需重启
3. **传统单文件** — `<repo>/providers/<name>.py` — 用于与非仓库内可编辑安装的向后兼容

**用户插件会覆盖同名的捆绑插件**，因为 `register_provider()` 采用最后写入者获胜。放置一个 `$HERMES_HOME/plugins/model-providers/gmi/` 目录即可替换内置的 GMI 配置文件，无需修改仓库。

## 目录结构

```
plugins/model-providers/my-provider/
├── __init__.py       # 在模块级别调用 register_provider(profile)
├── plugin.yaml       # kind: model-provider + 元数据（可选，但推荐）
└── README.md         # 设置说明（可选）
```

唯一必需的文件是 `__init__.py`。`plugin.yaml` 由 `hermes plugins` 用于内省，并由通用 PluginManager 将插件路由到正确的加载器；如果没有它，通用加载器会回退使用源码文本启发式方法。

## 最小示例——一个简单的 API 密钥提供者

```python
# plugins/model-providers/acme-inference/__init__.py
from providers import register_provider
from providers.base import ProviderProfile

acme = ProviderProfile(
    name="acme-inference",
    aliases=("acme",),
    display_name="Acme Inference",
    description="Acme — OpenAI 兼容的直接 API",
    signup_url="https://acme.example.com/keys",
    env_vars=("ACME_API_KEY", "ACME_BASE_URL"),
    base_url="https://api.acme.example.com/v1",
    auth_type="api_key",
    default_aux_model="acme-small-fast",
    fallback_models=(
        "acme-large-v3",
        "acme-medium-v3",
        "acme-small-fast",
    ),
)

register_provider(acme)
```

```yaml
# plugins/model-providers/acme-inference/plugin.yaml
name: acme-inference
kind: model-provider
version: 1.0.0
description: Acme Inference — OpenAI 兼容的直接 API
author: Your Name
```

就这样。在放置这两个文件后，以下集成将**自动连线**，无需任何其他编辑：

| 集成 | 位置 | 获取内容 |
|---|---|---|
| 凭据解析 | `hermes_cli/auth.py` | 从配置文件填充 `PROVIDER_REGISTRY["acme-inference"]` |
| `--provider` CLI 标志 | `hermes_cli/main.py` | 接受 `acme-inference` |
| `hermes model` 选择器 | `hermes_cli/models.py` | 出现在 `CANONICAL_PROVIDERS` 中，模型列表从 `{base_url}/models` 获取 |
| `hermes doctor` | `hermes_cli/doctor.py` | 对 `ACME_API_KEY` + `{base_url}/models` 探测进行健康检查 |
| `hermes setup` | `hermes_cli/config.py` | `ACME_API_KEY` 出现在 `OPTIONAL_ENV_VARS` 和设置向导中 |
| URL 反向映射 | `agent/model_metadata.py` | 主机名 → 提供者名称，用于自动检测 |
| 辅助模型 | `agent/auxiliary_client.py` | 使用 `default_aux_model` 进行压缩/摘要 |
| 运行时解析 | `hermes_cli/runtime_provider.py` | 返回正确的 `base_url`、`api_key`、`api_mode` |
| 传输层 | `agent/transports/chat_completions.py` | 配置文件路径通过 `prepare_messages` / `build_extra_body` / `build_api_kwargs_extras` 生成 kwargs |

## ProviderProfile 字段

完整定义在 `providers/base.py` 中。最常用的字段：

| 字段 | 类型 | 用途 |
|---|---|---|
| `name` | str | 规范标识符 — 与 `config.yaml` 中的 `model.provider` 和 `--provider` 标志匹配 |
| `aliases` | `tuple[str, ...]` | 替代名称，由 `get_provider_profile()` 解析（例如 `grok` → `xai`） |
| `api_mode` | str | `chat_completions` \| `codex_responses` \| `anthropic_messages` \| `bedrock_converse` |
| `display_name` | str | 在 `hermes model` 选择器中显示的人类可读标签 |
| `description` | str | 选择器副标题 |
| `signup_url` | str | 在首次运行设置时显示（“在此处获取 API 密钥”） |
| `env_vars` | `tuple[str, ...]` | 按优先级排序的 API 密钥环境变量；最后一个 `*_BASE_URL` 条目用作基础 URL 的用户覆盖 |
| `base_url` | str | 默认推理端点 |
| `models_url` | str | 显式的模型目录 URL（回退到 `{base_url}/models`） |
| `auth_type` | str | `api_key` \| `oauth_device_code` \| `oauth_external` \| `copilot` \| `aws_sdk` \| `external_process` |
| `fallback_models` | `tuple[str, ...]` | 当实时目录获取失败时显示的精选列表 |
| `default_headers` | `dict[str, str]` | 每次请求都发送（例如 Copilot 的 `Editor-Version`） |
| `fixed_temperature` | Any | `None` = 使用调用者的值；`OMIT_TEMPERATURE` 哨兵 = 完全不发送 temperature（Kimi） |
| `default_max_tokens` | `int \| None` | 提供者级别的 max_tokens 上限（Nvidia: 16384） |
| `default_aux_model` | str | 用于辅助任务的廉价模型（压缩、视觉、摘要） |

## 可覆盖的钩子

对于非平凡的细微差异，可继承 `ProviderProfile`：

```python
from typing import Any
from providers.base import ProviderProfile

class AcmeProfile(ProviderProfile):
    def prepare_messages(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """提供者特定的消息预处理。在 codex 清理之后、开发者角色交换之前运行。默认：透传。"""
        # 示例：Qwen 将纯文本内容规范化为部分列表并插入 cache_control；Kimi 重写工具调用 JSON
        return messages

    def build_extra_body(self, *, session_id=None, **context) -> dict:
        """提供者特定的 extra_body 字段，合并到 API 调用中。
        上下文包括：session_id、provider_preferences、model、base_url、
        reasoning_config。默认：空字典。"""
        # 示例：OpenRouter 的提供者偏好块，
        # Gemini 的 thinking_config 翻译。
        return {}

    def build_api_kwargs_extras(self, *, reasoning_config=None, **context):
        """返回 (extra_body_additions, top_level_kwargs)。当某些字段
        位于顶层（Kimi 的 reasoning_effort、OpenRouter 对自适应 Anthropic 模型的 verbosity）
        而另一些字段位于 extra_body（OpenRouter 的 reasoning 字典）时需要使用。
        默认：({}, {})."""
        return {}, {}

    def fetch_models(self, *, api_key=None, timeout=8.0) -> list[str] | None:
        """实时目录获取。默认使用 Bearer 认证访问 {models_url or base_url}/models。
        覆盖用于：自定义认证（Anthropic）、无 REST 端点（Bedrock → None）、
        或公共/无需认证的目录（OpenRouter）。"""
        return super().fetch_models(api_key=api_key, timeout=timeout)
```

## 钩子参考示例

查看这些捆绑插件以了解惯用模式：

| 插件 | 原因 |
|---|---|
| `plugins/model-providers/openrouter/` | 带提供者偏好的聚合器，公共模型目录 |
| `plugins/model-providers/gemini/` | `thinking_config` 翻译（原生 + OpenAI 兼容嵌套形式） |
| `plugins/model-providers/kimi-coding/` | `OMIT_TEMPERATURE`、`extra_body.thinking`、顶层 `reasoning_effort` |
| `plugins/model-providers/qwen-oauth/` | 消息规范化、`cache_control` 注入、VL 高分辨率 |
| `plugins/model-providers/nous/` | 归属标签、“禁用时省略推理” |
| `plugins/model-providers/custom/` | Ollama 的 `num_ctx` + `think: false` 细微差异 |
| `plugins/model-providers/bedrock/` | `api_mode="bedrock_converse"`、`fetch_models` 返回 None（无 REST 端点） |

## 用户覆盖——无需编辑仓库即可替换内置提供者

假设你想将 `gmi` 指向你的私有暂存端点以进行测试。创建 `~/.hermes/plugins/model-providers/gmi/__init__.py`：

```python
from providers import register_provider
from providers.base import ProviderProfile

register_provider(ProviderProfile(
    name="gmi",
    aliases=("gmi-cloud", "gmicloud"),
    env_vars=("GMI_API_KEY",),
    base_url="https://gmi-staging.internal.example.com/v1",
    auth_type="api_key",
    default_aux_model="google/gemini-3.1-flash-lite-preview",
))
```

下一个会话中，`get_provider_profile("gmi").base_url` 将返回暂存 URL。无需修补仓库，无需重新构建。由于用户插件在捆绑插件之后发现，用户 `register_provider()` 调用会胜出。

## api_mode 选择

支持四个值。Hermes 根据以下条件选择一个：

1. 用户显式覆盖（`config.yaml` 中的 `model.api_mode`，当设置时）
2. OpenCode 的按模型分发（对于 Zen 和 Go 的 `opencode_model_api_mode`）
3. URL 自动检测 — `/anthropic` 后缀 → `anthropic_messages`、`api.openai.com` → `codex_responses`、`api.x.ai` → `codex_responses`、Kimi 域上的 `/coding` → `chat_completions`
4. **配置文件 `api_mode`** 作为回退，当 URL 检测未找到任何内容时
5. 默认 `chat_completions`

设置 `profile.api_mode` 以匹配你的提供者默认发送的模式——它只是一个提示。用户 URL 覆盖仍然胜出。

## 认证类型

| `auth_type` | 含义 | 使用者 |
|---|---|---|
| `api_key` | 单个环境变量携带静态 API 密钥 | 大多数提供者 |
| `oauth_device_code` | 设备码 OAuth 流程 | — |
| `oauth_external` | 用户在其他地方登录，令牌落入 `auth.json` | Anthropic OAuth、MiniMax OAuth、Qwen Portal、Nous Portal |
| `copilot` | GitHub Copilot 令牌刷新周期 | 仅 `copilot` 插件 |
| `aws_sdk` | AWS SDK 凭据链（IAM 角色、配置文件、环境变量） | 仅 `bedrock` 插件 |
| `external_process` | 由代理生成的子进程处理认证 | 仅 `copilot-acp` 插件 |

`auth_type` 决定了哪些代码路径将你的提供者视为“简单的 API 密钥提供者”——如果不是 `api_key`，PluginManager 仍会记录清单，但 Hermes 的 CLI 级别自动化（doctor 检查、`--provider` 标志、设置向导委托）可能会跳过它。

## 发现时机

提供者发现是**惰性**的——由进程中第一次调用 `get_provider_profile()` 或 `list_providers()` 触发。实际上这会在启动早期发生（`auth.py` 模块加载时会急切地扩展 `PROVIDER_REGISTRY`）。如果需要验证你的插件已加载，请运行：

```bash
hermes doctor
```

——一个成功的 `auth_type="api_key"` 配置文件将出现在 Provider Connectivity 部分，并带有 `/models` 探测。

程序化检查：

```python
from providers import list_providers
for p in list_providers():
    print(p.name, p.base_url, p.api_mode)
```

## 测试你的插件

将 `HERMES_HOME` 指向一个临时目录，这样就不会污染你的真实配置：

```bash
export HERMES_HOME=/tmp/hermes-plugin-test
mkdir -p $HERMES_HOME/plugins/model-providers/my-provider
cat > $HERMES_HOME/plugins/model-providers/my-provider/__init__.py <<'EOF'
from providers import register_provider
from providers.base import ProviderProfile
register_provider(ProviderProfile(
    name="my-provider",
    env_vars=("MY_API_KEY",),
    base_url="https://api.my-provider.example.com/v1",
    auth_type="api_key",
))
EOF

export MY_API_KEY=your-test-key
hermes -z "hello" --provider my-provider -m some-model
```

## 通用 PluginManager 集成

通用 `PluginManager`（`hermes plugins` 操作的对象）**可以看到**模型提供插件，但不会导入它们——`providers/__init__.py` 管理其生命周期。管理器记录清单用于内省，并按 `kind: model-provider` 进行分类。当你将一个未标记的用户插件放入 `$HERMES_HOME/plugins/`，且该插件恰好调用了带有 `ProviderProfile` 的 `register_provider` 时，管理器会通过源码文本启发式方法自动将其强制转换为 `kind: model-provider`——因此即使没有 `plugin.yaml`，插件也能正确路由。

## 通过 pip 分发

与任何 Hermes 插件一样，模型提供者可以作为 pip 包分发。在 `pyproject.toml` 中添加一个入口点：

```toml
[project.entry-points."hermes_agent.plugins"]
acme-inference = "acme_hermes_plugin:register"
```

……其中 `acme_hermes_plugin:register` 是一个调用 `register_provider(profile)` 的函数。通用 PluginManager 在 `discover_and_load()` 期间会拾取入口点插件。对于 `kind: model-provider` 的 pip 插件，你仍然需要在清单中声明 kind（或依赖源码文本启发式方法）。

有关完整的入口点设置，请参阅[构建一个 Hermes 插件](/guides/build-a-hermes-plugin#distribute-via-pip)。

## 相关页面

- [提供者运行时](/developer-guide/provider-runtime) — 解析优先级 + 每层读取配置文件的位置
- [添加提供者](/developer-guide/adding-providers) — 针对新推理后端的端到端清单（涵盖快速插件路径和完整的 CLI/认证集成）
- [记忆提供插件](/developer-guide/memory-provider-plugin)
- [上下文引擎插件](/developer-guide/context-engine-plugin)
- [构建一个 Hermes 插件](/guides/build-a-hermes-plugin) — 通用插件创作指南