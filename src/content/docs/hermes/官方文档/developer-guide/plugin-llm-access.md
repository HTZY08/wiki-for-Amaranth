---
title: Plugin Llm Access
---

sidebar_position: 11
title: "插件 LLM 访问"
description: "通过 ctx.llm 从插件内部运行任何 LLM 调用——聊天或结构化、同步或异步。主机拥有认证、故障关闭信任门、可选 JSON Schema 验证。"
---

--- body ---
# 插件 LLM 访问

`ctx.llm` 是插件进行 LLM 调用的支持方式。聊天补全、结构化提取、同步、异步、带或不带图像——相同的接口、相同的信任门、相同的主机拥有凭证。

当插件需要执行涉及模型但不属于智能体对话的任务时，就会使用这个功能。例如：一个钩子将工具错误重写为非工程师也能阅读的内容；一个网关适配器在入站消息排队前对其进行翻译；一个斜杠命令总结一长段粘贴文本；一个定时任务对昨天的活动打分并在状态板上写一行；一个预过滤器判断一条消息是否值得唤醒智能体。

这些都是智能体不应参与的工作。它们只需要一次 LLM 调用、一个类型化答案，然后结束。

## 最简单的调用

```python
result = ctx.llm.complete(messages=[{"role": "user", "content": "ping"}])
return result.text
```

这就是完整的 API，一行搞定。无需密钥、无需提供商配置、无需 SDK 初始化。插件针对用户当前使用的提供商和模型运行——当用户切换提供商时，插件会自动跟随。

## 更完整的聊天示例

```python
result = ctx.llm.complete(
    messages=[
        {"role": "system", "content": "Rewrite errors as one short sentence a non-engineer can act on."},
        {"role": "user",   "content": traceback_text},
    ],
    max_tokens=64,
    purpose="hooks.error-rewrite",
)
return result.text
```

`purpose` 是一个自由格式的审计字符串——它会出现在 `agent.log` 和 `result.audit` 中，以便运维人员查看哪个插件发起了哪个调用。可选，但推荐用于频繁触发的任务。

## 结构化输出

当插件需要类型化答案时，切换到结构化通道：

```python
result = ctx.llm.complete_structured(
    instructions="Score this support reply for urgency (0–1) and pick a category.",
    input=[{"type": "text", "text": message_body}],
    json_schema=TRIAGE_SCHEMA,
    purpose="support.triage",
    temperature=0.0,
    max_tokens=128,
)

if result.parsed["urgency"] > 0.8:
    await dispatch_to_oncall(result.parsed["category"], message_body)
```

主机向提供商请求 JSON 输出，本地解析作为后备方案，如果安装了 `jsonschema` 则根据你的 schema 进行验证，并在 `result.parsed` 上返回一个 Python 对象。如果模型无法生成有效的 JSON，则 `result.parsed` 为 `None`，`result.text` 包含原始响应。

## 这个通道给你带来什么

* **一次调用，四种形式。** `complete()` 用于聊天，`complete_structured()` 用于类型化 JSON，`acomplete()` 和 `acomplete_structured()` 用于 asyncio。相同的参数，相同的结果对象。
* **主机拥有凭证。** OAuth 令牌、刷新流程、凭证池、每个任务的辅助覆盖——Hermes 已有的每个凭证概念都适用。插件永远看不到令牌；主机会通过 `result.audit` 对调用进行归属。
* **受限的。** 单次同步或异步调用。没有流式传输、没有工具循环、没有需要管理的对话状态。陈述输入、获取结果、返回。
* **故障关闭信任。** 一个你从未配置过的插件不能选择自己的提供商、模型、智能体或存储凭证。默认姿态是“使用用户正在使用的”。运维人员在 `config.yaml` 中为每个插件选择特定的覆盖。

## 快速入门

下面两个完整的插件——一个是聊天，一个是结构化。两者都包含在单个 `register(ctx)` 函数中，无需任何外部配置即可针对用户当前激活的模型运行。

### 聊天补全 — `/tldr`

```python
def register(ctx):
    ctx.register_command(
        name="tldr",
        handler=lambda raw: _tldr(ctx, raw),
        description="Summarise the supplied text in one paragraph.",
        args_hint="<text>",
    )


def _tldr(ctx, raw_args: str) -> str:
    text = raw_args.strip()
    if not text:
        return "Usage: /tldr <text to summarise>"
    result = ctx.llm.complete(
        messages=[
            {"role": "system",
             "content": "Summarise the user's text in one tight paragraph. No preamble."},
            {"role": "user", "content": text},
        ],
        max_tokens=256,
        temperature=0.3,
        purpose="tldr",
    )
    return result.text
```

`result.text` 是模型的响应；`result.usage` 携带令牌计数；`result.provider` 和 `result.model` 携带归属信息。

### 结构化提取 — `/paste-to-tasks`

```python
def register(ctx):
    ctx.register_command(
        name="paste-to-tasks",
        handler=lambda raw: _paste_to_tasks(ctx, raw),
        description="Turn freeform meeting notes into structured tasks.",
        args_hint="<text>",
    )


_TASKS_SCHEMA = {
    "type": "object",
    "properties": {
        "tasks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "owner":  {"type": "string"},
                    "action": {"type": "string"},
                    "due":    {"type": "string", "description": "ISO date or empty"},
                },
                "required": ["action"],
            },
        },
    },
    "required": ["tasks"],
}


def _paste_to_tasks(ctx, raw_args: str) -> str:
    if not raw_args.strip():
        return "Usage: /paste-to-tasks <meeting notes>"
    result = ctx.llm.complete_structured(
        instructions=(
            "Extract concrete action items from these meeting notes. "
            "One task per actionable line. If no owner is named, leave 'owner' blank."
        ),
        input=[{"type": "text", "text": raw_args}],
        json_schema=_TASKS_SCHEMA,
        schema_name="meeting.tasks",
        purpose="paste-to-tasks",
        temperature=0.0,
        max_tokens=512,
    )
    if result.parsed is None:
        return f"Couldn't parse a response. Raw output:\n{result.text}"
    lines = [f"- [{t.get('owner') or '?'}] {t['action']}" for t in result.parsed["tasks"]]
    return "\n".join(lines) or "(no tasks found)"
```

第三个带图像输入的工作示例位于 [`hermes-example-plugins`](https://github.com/NousResearch/hermes-example-plugins/tree/main/plugin-llm-example) 仓库（参考插件伴侣仓库——未随 hermes-agent 捆绑）。关于异步接口（`acomplete()` / `acomplete_structured()` 配合 `asyncio.gather()`），请参阅同一仓库中的 [`plugin-llm-async-example`](https://github.com/NousResearch/hermes-example-plugins/tree/main/plugin-llm-async-example)。

## 何时使用哪种

| 你需要… | 使用… |
|---|---|
| 自由格式文本响应（翻译、总结、重写、生成） | `complete()` |
| 多轮提示（系统 + few-shot 示例 + 用户） | `complete()` |
| 一个类型化字典返回，并根据 schema 验证 | `complete_structured()` |
| 图像或文本输入，并返回类型化字典 | `complete_structured()` |
| 从异步代码中执行相同调用（网关适配器、异步钩子） | `acomplete()` / `acomplete_structured()` |

其他所有内容——提供商选择、模型解析、认证、后备、超时、视觉路由——在所有四种形式中都是相同的。

## API 接口

`ctx.llm` 是 `agent.plugin_llm.PluginLlm` 的一个实例。

### `complete()`

```python
result = ctx.llm.complete(
    messages=[{"role": "user", "content": "Hi"}],
    provider=None,         # optional, gated — Hermes provider id (e.g. "openrouter")
    model=None,            # optional, gated — whatever string that provider expects
    temperature=None,
    max_tokens=None,
    timeout=None,          # seconds
    agent_id=None,         # optional, gated
    profile=None,          # optional, gated — explicit auth-profile name
    purpose="optional-audit-string",
)
# → PluginLlmCompleteResult(text, provider, model, agent_id, usage, audit)
```

普通聊天补全。`messages` 是标准 OpenAI 格式——一个 `{"role": "...", "content": "..."}` 字典列表。多轮提示（系统 + few-shot 用户/助手对 + 最终用户）的工作方式与使用 OpenAI SDK 完全相同。

`provider=` 和 `model=` 是独立的，遵循与主机主配置（`model.provider` + `model.model`）相同的格式。仅设置 `model=` 可使用用户当前激活的提供商但使用不同的模型。同时设置两者可完全切换提供商。如果没有运维人员选择加入，任何一个参数都会引发 `PluginLlmTrustError`。

### `complete_structured()`

```python
result = ctx.llm.complete_structured(
    instructions="What you want extracted.",
    input=[
        {"type": "text",  "text": "..."},
        {"type": "image", "data": b"...", "mime_type": "image/png"},
        {"type": "image", "url":  "https://..."},
    ],
    json_schema={...},     # optional — triggers parsed result + validation
    json_mode=False,       # set True without a schema to ask for JSON anyway
    schema_name=None,      # optional human-readable schema name
    system_prompt=None,
    provider=None,         # optional, gated
    model=None,            # optional, gated
    temperature=None,
    max_tokens=None,
    timeout=None,
    agent_id=None,
    profile=None,
    purpose=None,
)
# → PluginLlmStructuredResult(text, provider, model, agent_id,
#                             usage, parsed, content_type, audit)
```

输入是类型化的文本或图像块（原始字节会自动以 `data:` URL 的形式进行 Base64 编码）。当提供了 `json_schema` 或 `json_mode=True` 时，主机通过 `response_format` 请求 JSON 输出，本地解析作为后备方案，如果安装了 `jsonschema` 则根据你的 schema 进行验证。

* `result.content_type == "json"` — `result.parsed` 是一个匹配你 schema 的 Python 对象。
* `result.content_type == "text"` — 解析或验证失败；检查 `result.text` 以获取原始模型响应。

### 异步

```python
result = await ctx.llm.acomplete(messages=...)
result = await ctx.llm.acomplete_structured(instructions=..., input=...)
```

参数和结果类型与其同步对应项相同。在网关适配器、异步钩子或任何已在 asyncio 事件循环上运行的插件代码中使用它们。

### 结果属性

```python
@dataclass
class PluginLlmCompleteResult:
    text: str                    # the assistant's response
    provider: str                # e.g. "openrouter", "anthropic"
    model: str                   # whatever the provider returned for this call
    agent_id: str                # whose model/auth was used
    usage: PluginLlmUsage        # tokens + cache + cost estimate
    audit: Dict[str, Any]        # plugin_id, purpose, profile

@dataclass
class PluginLlmStructuredResult(PluginLlmCompleteResult):
    parsed: Optional[Any]        # JSON object when content_type == "json"
    content_type: str            # "json" or "text"
    # audit also carries schema_name when supplied
```

`usage` 在提供商返回这些字段时包含 `input_tokens`、`output_tokens`、`total_tokens`、`cache_read_tokens`、`cache_write_tokens` 和 `cost_usd`。

## 信任门

默认行为是故障关闭。如果没有 `plugins.entries` 配置块，插件可以：

* 针对用户当前激活的提供商和模型运行四个方法中的任何一个；
* 设置请求整形参数（`temperature`、`max_tokens`、`timeout`、`system_prompt`、`purpose`、`messages`、`instructions`、`input`、`json_schema`）；

……仅此而已。`provider=`、`model=`、`agent_id=` 和 `profile=` 参数会引发 `PluginLlmTrustError`，直到运维人员选择加入。

**大多数插件不需要本部分。** 仅调用 `ctx.llm.complete(messages=...)` 且没有覆盖的插件会针对用户当前激活的模型运行，无需配置。下面的块仅当插件特别想要固定到不同于用户的模型或提供商时才相关。

```yaml
plugins:
  entries:
    my-plugin:
      llm:
        # 允许此插件选择不同的 Hermes 提供商
        # （必须是 Hermes 已知的提供商——与 `hermes model` 和 config.yaml 中的 model.provider 名称相同）。
        allow_provider_override: true

        # 可选地限制允许的提供商。使用 ["*"] 表示任何提供商。
        allowed_providers:
          - openrouter
          - anthropic

        # 允许此插件请求特定模型。
        allow_model_override: true

        # 可选地限制允许的模型。使用 ["*"] 表示任何模型。
        # 模型会与插件发送的字符串逐字匹配——Hermes 不会查找任何内容。
        allowed_models:
          - openai/gpt-4o-mini
          - anthropic/claude-3-5-haiku

        # 允许跨智能体调用（很少见）。
        allow_agent_id_override: false

        # 允许插件请求特定的存储认证配置文件
        # （例如，同一提供商上的不同 OAuth 账户）。
        allow_profile_override: false
```

插件 ID 是扁平化插件的清单 `name:` 字段，或嵌套插件的路径派生键（`image_gen/openai`、`memory/honcho` 等）。

### 门强制执行什么

| 覆盖项          | 默认值 | 配置键                            |
| --------------- | ------ | --------------------------------- |
| `provider=`     | 禁止   | `allow_provider_override: true`   |
| ↳ 允许列表      | —      | `allowed_providers: [...]`        |
| `model=`        | 禁止   | `allow_model_override: true`      |
| ↳ 允许列表      | —      | `allowed_models: [...]`           |
| `agent_id=`     | 禁止   | `allow_agent_id_override: true`   |
| `profile=`      | 禁止   | `allow_profile_override: true`    |

每个覆盖项独立受门控。授予 `allow_model_override` **并不** 同时授予 `allow_provider_override`——一个被信任选择模型的插件仍然被限制在用户当前激活的提供商上，除非它也获得提供商门。

### 门不需要强制执行什么

* 请求整形参数——`temperature`、`max_tokens`、`timeout`、`system_prompt`、`purpose`、`messages`、`instructions`、`input`、`json_schema`、`schema_name`、`json_mode`——始终允许；它们不选择凭证或路由。
* 默认拒绝姿态意味着一个未配置的插件仍然可以做有用的事情——它只是针对当前激活的提供商和模型运行。运维人员只需要为想要更细粒度路由的插件考虑 `plugins.entries`。

## 主机拥有什么

`ctx.llm` 为插件完成的所有事项的完整列表，无需你手动处理：

* **提供商解析。** 从用户的配置中读取 `model.provider` + `model.model`（或在受信任时读取显式覆盖）。
* **认证。** 从 `~/.hermes/auth.json` / 环境变量中拉取 API 密钥、OAuth 令牌或刷新令牌，包括配置了凭证池时的凭证池。插件永远不会看到它们。
* **视觉路由。** 当提供图像输入且用户当前激活的文本模型仅为文本时，主机会自动回退到配置的视觉模型。
* **后备链。** 如果用户的主提供商返回 5xx 或 429，请求会在将错误返回给插件之前经过 Hermes 通常的聚合器感知后备。
* **超时。** 尊重你的 `timeout=` 参数，回退到 `auxiliary.<task>.timeout` 配置或全局 aux 默认值。
* **JSON 整形。** 当你请求 JSON 时，向提供商发送 `response_format`，然后如果提供商返回了代码围栏响应，则从本地重新解析。
* **Schema 验证。** 当安装了 `jsonschema` 时，根据你的 `json_schema` 进行验证；否则记录一条调试行并跳过严格验证。
* **审计日志。** 每次调用都会在 `agent.log` 中写入一条 INFO 行，包含插件 ID、提供商/模型、目的和令牌总数。

## 插件拥有什么

* **请求形状。** `messages` 用于聊天，`instructions` + `input` 用于结构化。插件构建提示词；主机运行它。
* **Schema。** 无论你想要什么形状返回。主机不会为你推断。
* **错误处理。** `complete_structured()` 在输入为空时引发 `ValueError`，在 schema 验证失败时也引发。当信任门拒绝覆盖时，会触发 `PluginLlmTrustError`。其他任何错误（提供商 5xx、未配置凭证、超时）会引发 `auxiliary_client.call_llm()` 引发的任何异常。
* **成本。** 每次调用都针对用户付费的提供商运行。不要在每个网关消息上都循环调用 `complete()` 而不考虑令牌支出。

## 在插件接口中的位置

现有的 `ctx.*` 方法扩展了已有的 Hermes 子系统：

| `ctx.register_tool` | 添加一个智能体可以调用的工具（Tool） |
| `ctx.register_platform` | 连接一个新的网关（Gateway）适配器 |
| `ctx.register_image_gen_provider` | 替换图像生成后端 |
| `ctx.register_memory_provider` | 替换内存后端 |
| `ctx.register_context_engine` | 替换上下文压缩器 |
| `ctx.register_hook` | 观察生命周期事件（Hook） |

`ctx.llm` 是第一个让插件能够**带外**运行与用户正在对话的相同模型，而不需要上述任何内容的接口。这是它唯一的工作。如果你的插件需要注册一个智能体调用的工具（Tool），请使用 `register_tool`。如果需要响应生命周期事件，请使用 `register_hook`。如果需要发起自己的模型调用——无论出于何种原因，结构化或非结构化——请使用 `ctx.llm`。

## 参考

* 实现：[`agent/plugin_llm.py`](https://github.com/NousResearch/hermes-agent/blob/main/agent/plugin_llm.py)
* 测试：[`tests/agent/test_plugin_llm.py`](https://github.com/NousResearch/hermes-agent/blob/main/tests/agent/test_plugin_llm.py)
* 参考插件（伴侣仓库）：
  * [`plugin-llm-example`](https://github.com/NousResearch/hermes-example-plugins/tree/main/plugin-llm-example) — 带图像输入的同步结构化提取
  * [`plugin-llm-async-example`](https://github.com/NousResearch/hermes-example-plugins/tree/main/plugin-llm-async-example) — 配合 `asyncio.gather()` 的异步示例
* 辅助客户端（引擎底层）：请参阅 [提供商运行时](/developer-guide/provider-runtime)。