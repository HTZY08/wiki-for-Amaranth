---
title: Adding Providers
---

sidebar_position: 5
title: "添加提供者"
description: "如何向 Hermes Agent 添加新的推理提供者——身份验证、运行时解析、CLI 流程、适配器、测试和文档"
---

--- body ---
# 添加提供者（Adding Providers）

Hermes 已经能够通过自定义提供者路径与任何兼容 OpenAI 的端点通信。**除非你希望为该服务提供一流的用户体验**，否则不要添加内置提供者（Provider）：

- 提供者特定的身份验证或令牌刷新
- 精选的模型目录
- 设置/`hermes model` 菜单条目
- `provider:model` 语法的提供者别名
- 需要适配器的非 OpenAI API 形态

如果提供者只是"另一个兼容 OpenAI 的基础 URL 和 API 密钥"，那么一个命名的自定义提供者可能就足够了。

## 心智模型（Mental model）

内置提供者需要在多个层面保持一致：

1. `hermes_cli/auth.py` 决定如何查找凭据。
2. `hermes_cli/runtime_provider.py` 将其转换为运行时数据：
   - `provider`
   - `api_mode`
   - `base_url`
   - `api_key`
   - `source`
3. `run_agent.py` 使用 `api_mode` 来决定如何构建和发送请求。
4. `hermes_cli/models.py` 和 `hermes_cli/main.py` 使提供者出现在 CLI 中。（`hermes_cli/setup.py` 会自动委托给 `main.py` —— 无需修改。）
5. `agent/auxiliary_client.py` 和 `agent/model_metadata.py` 确保辅助任务和令牌预算正常工作。

重要的抽象是 `api_mode`。

- 大多数提供者使用 `chat_completions`。
- Codex 使用 `codex_responses`。
- Anthropic 使用 `anthropic_messages`。
- 新的非 OpenAI 协议通常意味着添加新的适配器和新的 `api_mode` 分支。

## 首先选择实现路径

### 路径 A —— 兼容 OpenAI 的提供者

当提供者接受标准的聊天补全（chat-completions）风格的请求时，使用此路径。

典型工作：

- 添加身份验证元数据
- 添加模型目录/别名
- 添加运行时解析
- 添加 CLI 菜单连接
- 添加辅助模型默认值
- 添加测试和用户文档

通常不需要新的适配器或新的 `api_mode`。

### 路径 B —— 原生提供者（Native provider）

当提供者行为与 OpenAI 聊天补全不同时，使用此路径。

当前代码库中的示例：

- `codex_responses`
- `anthropic_messages`

此路径包含路径 A 的所有内容，外加：

- `agent/` 中的提供者适配器
- `run_agent.py` 中的请求构建、分发、用量提取、中断处理和响应规范化分支
- 适配器测试

## 文件清单

### 每个内置提供者都需要

1. `hermes_cli/auth.py`
2. `hermes_cli/models.py`
3. `hermes_cli/runtime_provider.py`
4. `hermes_cli/main.py`
5. `agent/auxiliary_client.py`
6. `agent/model_metadata.py`
7. 测试
8. `website/docs/` 下的用户文档

:::tip
`hermes_cli/setup.py` **不**需要修改。设置向导会将提供者/模型选择委托给 `main.py` 中的 `select_provider_and_model()` —— 在那里添加的任何提供者都会自动在 `hermes setup` 中可用。
:::

### 原生/非 OpenAI 提供者额外需要

10. `agent/<provider>_adapter.py`
11. `run_agent.py`
12. 如果需要提供者 SDK，则修改 `pyproject.toml`

## 快速路径：简单的 API 密钥提供者

如果你的提供者只是一个使用单个 API 密钥进行身份验证的兼容 OpenAI 的端点，则无需修改 `auth.py`、`runtime_provider.py`、`main.py` 或下面完整清单中的任何其他文件。

你只需要：

1. 在 `plugins/model-providers/<your-provider>/` 下创建一个插件目录，包含：
   - `__init__.py` —— 在模块级别调用 `register_provider(profile)`
   - `plugin.yaml` —— 清单（name, kind: model-provider, version, description）
2. 就是这样。提供者插件会在首次调用 `get_provider_profile()` 或 `list_providers()` 时自动加载 —— 捆绑插件（此 repo）和位于 `$HERMES_HOME/plugins/model-providers/` 的用户插件都会被加载。

当你添加一个插件并调用 `register_provider()` 时，以下内容会自动连接：

1. `PROVIDER_REGISTRY` 条目在 `auth.py` 中（凭据解析，环境变量查找）
2. `api_mode` 设置为 `chat_completions`
3. `base_url` 从配置或声明的环境变量中获取
4. 按优先级顺序检查 `env_vars` 以获取 API 密钥
5. 为提供者注册 `fallback_models` 列表
6. `--provider` CLI 标志接受提供者 ID
7. `hermes model` 菜单包含该提供者
8. `hermes setup` 向导自动委托给 `main.py`
9. `provider:model` 别名语法有效
10. 运行时解析器返回正确的 `base_url` 和 `api_key`
11. `--provider <name>` CLI 标志接受提供者 ID
12. 后备模型激活可以干净地切换到该提供者

`$HERMES_HOME/plugins/model-providers/<name>/` 下的用户插件会覆盖同名的捆绑插件（`register_provider()` 中最后写入者获胜）—— 因此第三方无需编辑仓库即可修补或替换任何内置配置文件。

请参阅 `plugins/model-providers/nvidia/` 或 `plugins/model-providers/gmi/` 作为模板，以及完整的 [模型提供者插件指南](/developer-guide/model-provider-plugin) 了解字段参考、钩子惯用法和端到端示例。

## 完整路径：OAuth 和复杂提供者

当你的提供者需要以下任何一项时，请使用下面的完整清单：

- OAuth 或令牌刷新（Nous Portal, Codex, Qwen Portal, Copilot）
- 需要新适配器的非 OpenAI API 形态（Anthropic Messages, Codex Responses）
- 自定义端点检测或多区域探测（z.ai, Kimi）
- 精选的静态模型目录或实时 `/models` 获取
- 提供者特定的 `hermes model` 菜单条目，带有自定义身份验证流程

## 步骤 1：选择一个规范的提供者 ID

选择一个提供者 ID 并在所有地方使用它。

仓库中的示例：

- `openai-codex`
- `kimi-coding`
- `minimax-cn`

相同的 ID 应出现在：

- `hermes_cli/auth.py` 中的 `PROVIDER_REGISTRY`
- `hermes_cli/models.py` 中的 `_PROVIDER_LABELS`
- `hermes_cli/auth.py` 和 `hermes_cli/models.py` 中的 `_PROVIDER_ALIASES`
- `hermes_cli/main.py` 中的 CLI `--provider` 选项
- 设置/模型选择分支
- 辅助模型默认值
- 测试

如果 ID 在这些文件中不同，提供者会感觉半连接：身份验证可能有效，而 `/model`、设置或运行时解析会静默失败。

## 步骤 2：在 `hermes_cli/auth.py` 中添加身份验证元数据

对于 API 密钥提供者，向 `PROVIDER_REGISTRY` 添加一个 `ProviderConfig` 条目，包含：

- `id`
- `name`
- `auth_type="api_key"`
- `inference_base_url`
- `api_key_env_vars`
- 可选的 `base_url_env_var`

同时将别名添加到 `_PROVIDER_ALIASES`。

使用现有提供者作为模板：

- 简单 API 密钥路径：Z.AI, MiniMax
- 带有端点检测的 API 密钥路径：Kimi, Z.AI
- 原生令牌解析：Anthropic
- OAuth / 身份验证存储路径：Nous, OpenAI Codex

这里需要回答的问题：

- Hermes 应检查哪些环境变量，优先级顺序如何？
- 提供者是否需要基础 URL 覆盖？
- 它是否需要端点探测或令牌刷新？
- 凭据缺失时，身份验证错误消息应显示什么？

如果提供者需要比"查找一个 API 密钥"更复杂的内容，请添加一个专用的凭据解析器，而不是将逻辑强行塞入无关的分支。

## 步骤 3：在 `hermes_cli/models.py` 中添加模型目录和别名

更新提供者目录，使提供者在菜单和 `provider:model` 语法中工作。

典型编辑：

- `_PROVIDER_MODELS`
- `_PROVIDER_LABELS`
- `_PROVIDER_ALIASES`
- `list_available_providers()` 中的提供者显示顺序
- 如果提供者支持实时 `/models` 获取，则修改 `provider_model_ids()`

如果提供者公开了实时模型列表，优先使用它，并将 `_PROVIDER_MODELS` 保留为静态后备。

该文件还使以下输入生效：

```text
anthropic:claude-sonnet-4-6
kimi:model-name
```

如果这里缺少别名，提供者可能能够正确验证，但在 `/model` 解析中仍然失败。

## 步骤 4：在 `hermes_cli/runtime_provider.py` 中解析运行时数据

`resolve_runtime_provider()` 是 CLI、网关、cron、ACP 和辅助客户端使用的共享路径。

添加一个分支，返回一个至少包含以下内容的字典：

```python
{
    "provider": "your-provider",
    "api_mode": "chat_completions",  # 或你的原生模式
    "base_url": "https://...",
    "api_key": "...",
    "source": "env|portal|auth-store|explicit",
    "requested_provider": requested_provider,
}
```

如果提供者是兼容 OpenAI 的，`api_mode` 通常应保持为 `chat_completions`。

注意 API 密钥的优先级。Hermes 已包含逻辑，避免将 OpenRouter 密钥泄露给无关端点。新的提供者应同样明确哪个密钥指向哪个基础 URL。

## 步骤 5：在 `hermes_cli/main.py` 中连接 CLI

直到提供者出现在交互式 `hermes model` 流程中，它才能被发现。

在 `hermes_cli/main.py` 中更新以下内容：

- `provider_labels` 字典
- `select_provider_and_model()` 中的 `providers` 列表
- 提供者调度（`if selected_provider == ...`）
- `--provider` 参数选项
- 如果提供者支持登录/登出流程，则更新登录/登出选项
- 一个 `_model_flow_<provider>()` 函数，或者如果合适，重用 `_model_flow_api_key_provider()`

:::tip
`hermes_cli/setup.py` 不需要修改 —— 它调用 `main.py` 中的 `select_provider_and_model()`，因此你的新提供者会自动出现在 `hermes model` 和 `hermes setup` 中。
:::

## 步骤 6：保持辅助调用正常工作

这里涉及两个文件：

### `agent/auxiliary_client.py`

如果这是一个直接的 API 密钥提供者，向 `_API_KEY_PROVIDER_AUX_MODELS` 添加一个便宜/快速的默认辅助模型。

辅助任务包括：

- 视觉摘要
- 网页提取摘要
- 上下文压缩摘要
- 会话搜索摘要
- 内存刷新

如果提供者没有合理的辅助默认值，辅助任务可能会回退失败，或意外使用昂贵的主模型。

### `agent/model_metadata.py`

添加提供者模型的上下文长度，以便令牌预算、压缩阈值和限制保持合理。

## 步骤 7：如果提供者是原生的，添加适配器和 `run_agent.py` 支持

如果提供者不是普通的聊天补全（chat completions），将提供者特定的逻辑隔离到 `agent/<provider>_adapter.py` 中。

保持 `run_agent.py` 专注于编排。它应调用适配器辅助函数，而不是在整个文件中内联手工构建提供者负载。

原生提供者通常需要在以下位置进行工作：

### 新的适配器文件

典型职责：

- 构建 SDK / HTTP 客户端
- 解析令牌
- 将 OpenAI 风格的对话消息转换为提供者的请求格式
- 如果需要，转换工具架构
- 将提供者响应规范化回 `run_agent.py` 期望的格式
- 提取用量和完成原因数据

### `run_agent.py`

搜索 `api_mode` 并检查每个切换点。至少验证：

- `__init__` 选择了新的 `api_mode`
- 客户端构建设置适用于提供者
- `_build_api_kwargs()` 知道如何格式化请求
- `_interruptible_api_call()` 分发到正确的客户端调用
- 中断 / 客户端重建路径正常工作
- 响应验证接受提供者的形状
- 完成原因提取正确
- 令牌用量提取正确
- 后备模型激活可以干净地切换到新提供者
- 摘要生成和内存刷新路径仍然有效

同时在 `run_agent.py` 中搜索 `self.client.`。任何假设标准 OpenAI 客户端存在的代码路径，在原生提供者使用不同的客户端对象或 `self.client = None` 时都可能失败。

### 提示缓存和提供者特定的请求字段

提示缓存和提供者特定的旋钮容易退化。

代码库中已有的示例：

- Anthropic 有原生的提示缓存路径
- OpenRouter 接收提供者路由字段
- 并非每个提供者都应接收每个请求端选项

当你添加原生提供者时，请双重检查 Hermes 仅发送该提供者实际理解的字段。

## 步骤 8：测试

至少修改那些保护提供者连接的测试。

常见位置：

- `tests/hermes_cli/test_runtime_provider_resolution.py`
- `tests/cli/test_cli_provider_resolution.py`
- `tests/hermes_cli/test_model_switch_custom_providers.py`（以及相邻的 `tests/hermes_cli/test_model_switch_*.py`）
- `tests/hermes_cli/test_setup_model_provider.py`
- `tests/run_agent/test_provider_parity.py`
- `tests/run_agent/test_run_agent.py`
- `tests/test_<provider>_adapter.py`（对于原生提供者）

对于仅文档示例，确切文件集可能有所不同。关键是要覆盖：

- 身份验证解析
- CLI 菜单 / 提供者选择
- 运行时提供者解析
- 代理执行路径
- `provider:model` 解析
- 任何适配器特定的消息转换

使用禁用 xdist 的方式运行测试：

```bash
source venv/bin/activate
python -m pytest tests/hermes_cli/test_runtime_provider_resolution.py tests/cli/test_cli_provider_resolution.py tests/hermes_cli/test_setup_model_provider.py tests/run_agent/test_provider_parity.py -n0 -q
```

对于更深度的更改，在推送前运行完整套件：

```bash
source venv/bin/activate
python -m pytest tests/ -n0 -q
```

## 步骤 9：实时验证

测试之后，运行一个真正的冒烟测试。

```bash
source venv/bin/activate
python -m hermes_cli.main chat -q "Say hello" --provider your-provider --model your-model
```

如果更改了菜单，也要测试交互式流程：

```bash
source venv/bin/activate
python -m hermes_cli.main model
python -m hermes_cli.main setup
```

对于原生提供者，还要验证至少一次工具调用，而不仅仅是纯文本响应。

## 步骤 10：更新用户文档

如果提供者旨在作为一等选项发布，也要更新用户文档：

- `website/docs/getting-started/quickstart.md`
- `website/docs/user-guide/configuration.md`
- `website/docs/reference/environment-variables.md`

开发者可以完美地连接提供者，但仍然让用户无法发现所需的环境变量或设置流程。

## 兼容 OpenAI 的提供者清单

如果提供者是标准的聊天补全，请使用此清单。

- [ ] 在 `hermes_cli/auth.py` 中添加了 `ProviderConfig`
- [ ] 在 `hermes_cli/auth.py` 和 `hermes_cli/models.py` 中添加了别名
- [ ] 在 `hermes_cli/models.py` 中添加了模型目录
- [ ] 在 `hermes_cli/runtime_provider.py` 中添加了运行时分支
- [ ] 在 `hermes_cli/main.py` 中添加了 CLI 连接（setup.py 自动继承）
- [ ] 在 `agent/auxiliary_client.py` 中添加了辅助模型
- [ ] 在 `agent/model_metadata.py` 中添加了上下文长度
- [ ] 更新了运行时 / CLI 测试
- [ ] 更新了用户文档

## 原生提供者清单

当提供者需要新的协议路径时，请使用此清单。

- [ ] 已完成兼容 OpenAI 的清单中的所有内容
- [ ] 在 `agent/<provider>_adapter.py` 中添加了适配器
- [ ] 在 `run_agent.py` 中支持新的 `api_mode`
- [ ] 中断 / 重建路径正常工作
- [ ] 用量和完成原因提取正常工作
- [ ] 后备路径正常工作
- [ ] 添加了适配器测试
- [ ] 实时冒烟测试通过

## 常见陷阱

### 1. 将提供者添加到身份验证但未添加到模型解析

这会导致凭据正确解析，但 `/model` 和 `provider:model` 输入失败。

### 2. 忘记 `config["model"]` 可以是字符串或字典

许多提供者选择代码需要规范化这两种形式。

### 3. 假设需要内置提供者

如果服务只是兼容 OpenAI，自定义提供者可能以更少的维护成本解决用户问题。

### 4. 忘记辅助路径

主要聊天路径可以正常工作，而由于辅助路由从未更新，摘要、内存刷新或视觉辅助程序可能失败。

### 5. 原生提供者分支隐藏在 `run_agent.py` 中

搜索 `api_mode` 和 `self.client.`。不要假设明显的请求路径是唯一的。

### 6. 将仅限 OpenRouter 的旋钮发送给其他提供者

像提供者路由这样的字段只应属于支持它们的提供者。

### 7. 更新了 `hermes model` 但未更新 `hermes setup`

两个流程都需要知道提供者。

## 实现时的良好搜索目标

如果你在查找提供者涉及的所有位置，搜索这些符号：

- `PROVIDER_REGISTRY`
- `_PROVIDER_ALIASES`
- `_PROVIDER_MODELS`
- `resolve_runtime_provider`
- `_model_flow_`
- `select_provider_and_model`
- `api_mode`
- `_API_KEY_PROVIDER_AUX_MODELS`
- `self.client.`

## 相关文档

- [提供者运行时解析](./provider-runtime.md)
- [架构](./architecture.md)
- [贡献指南](./contributing.md)