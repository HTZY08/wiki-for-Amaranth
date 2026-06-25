---
sidebar_position: 4
title: "提供者运行时解析"
description: "Hermes 如何在运行时解析提供者、凭证、API 模式和辅助模型"
---

# 提供者运行时解析

Hermes 拥有一个共享的提供者运行时解析器，用于以下场景：

- CLI
- 网关（gateway）
- 定时任务（cron jobs）
- ACP
- 辅助模型（auxiliary model）调用

主要实现：

- `hermes_cli/runtime_provider.py` — 凭证解析，`_resolve_custom_runtime()`
- `hermes_cli/auth.py` — 提供者注册，`resolve_provider()`
- `hermes_cli/model_switch.py` — 共享的 `/model` 切换管道（CLI + 网关）
- `agent/auxiliary_client.py` — 辅助模型路由
- `providers/` — 抽象基类（ABC）和注册入口（`ProviderProfile`，`register_provider`，`get_provider_profile`，`list_providers`）
- `plugins/model-providers/<name>/` — 每个提供者的插件（内置），声明 `api_mode`、`base_url`、`env_vars`、`fallback_models`，并在首次访问时注册到注册表中。用户插件位于 `$HERMES_HOME/plugins/model-providers/<name>/`，会覆盖同名的内置插件。

`providers/` 中的 `get_provider_profile()` 根据给定的提供者 ID 返回一个 `ProviderProfile`。`runtime_provider.py` 在解析时调用它以获取规范的 `base_url`、`env_vars` 优先级列表、`api_mode` 和 `fallback_models`，无需在多个文件中重复这些数据。在 `plugins/model-providers/<your-provider>/`（或 `$HERMES_HOME/plugins/model-providers/<your-provider>/`）下添加一个调用 `register_provider()` 的新插件，就足以让 `runtime_provider.py` 识别它——解析器本身无需分支。

如果你尝试添加一个新的顶级推理提供者，请同时阅读 [添加提供者](./adding-providers.md) 和 [模型提供者插件指南](./model-provider-plugin.md) 以及本页。

## 解析优先级

在高层面上，提供者解析使用：

1. 显式的 CLI/运行时请求
2. `config.yaml` 中的模型/提供者配置
3. 环境变量
4. 提供者特定的默认值或自动解析

这个顺序很重要，因为 Hermes 将保存的模型/提供者选择视为正常运行时的真实来源。这可以防止过时的 shell 导出变量静默地覆盖用户在 `hermes model` 中最后选择的端点。

## 提供者

当前的提供者家族包括（有关完整的内置集合，请参见 `plugins/model-providers/`）：

- OpenRouter
- Nous Portal
- OpenAI Codex
- Copilot / Copilot ACP
- Anthropic（原生）
- Google / Gemini（`gemini`）
- Alibaba / DashScope（`alibaba`，`alibaba-coding-plan`）
- DeepSeek
- Z.AI
- Kimi / Moonshot（`kimi-coding`，`kimi-coding-cn`）
- MiniMax（`minimax`，`minimax-cn`，`minimax-oauth`）
- Kilo Code
- Hugging Face
- OpenCode Zen / OpenCode Go
- AWS Bedrock
- Azure Foundry
- NVIDIA NIM
- xAI (Grok)
- Arcee
- GMI Cloud
- StepFun
- Qwen OAuth
- Xiaomi
- Ollama Cloud
- LM Studio
- Tencent TokenHub
- 自定义（`provider: custom`）——适用于任何兼容 OpenAI 的端点的顶级提供者
- 命名自定义提供者（`config.yaml` 中的 `custom_providers` 列表）

## 运行时解析的输出

运行时解析器返回如下数据：

- `provider`
- `api_mode`
- `base_url`
- `api_key`
- `source`
- 提供者特定的元数据，如过期/刷新信息

## 为何重要

这个解析器是 Hermes 能够在以下场景之间共享认证/运行时逻辑的主要原因：

- `hermes chat`
- 网关消息处理
- 在新会话中运行的定时任务
- ACP 编辑器会话
- 辅助模型任务

## OpenRouter 和自定义兼容 OpenAI 的基础 URL

Hermes 包含逻辑，以避免在存在多个提供者密钥（例如 `OPENROUTER_API_KEY` 和 `OPENAI_API_KEY`）时将错误的 API 密钥泄漏到自定义端点。

每个提供者的 API 密钥都限定在其自己的基础 URL 中：

- `OPENROUTER_API_KEY` 仅发送到 `openrouter.ai` 端点
- `OPENAI_API_KEY` 用于自定义端点并作为后备

Hermes 还区分了：

- 用户选择的真正自定义端点
- 未配置自定义端点时使用的 OpenRouter 后备路径

这种区分对于以下情况尤其重要：

- 本地模型服务器
- 非 OpenRouter 的兼容 OpenAI API
- 无需重新运行设置即可切换提供者
- 配置中保存的自定义端点，即使当前 shell 中没有导出 `OPENAI_BASE_URL`，也应保持工作

## 原生 Anthropic 路径

Anthropic 不再仅仅“通过 OpenRouter”。

当提供者解析选择 `anthropic` 时，Hermes 使用：

- `api_mode = anthropic_messages`
- 原生 Anthropic Messages API
- `agent/anthropic_adapter.py` 进行转换

原生 Anthropic 的凭证解析现在优先选择可刷新的 Claude Code 凭证，而不是拷贝的环境变量令牌（当两者都存在时）。实际意味着：

- 当 Claude Code 凭证文件包含可刷新认证时，它们被视为首选来源
- 手动的 `ANTHROPIC_TOKEN` / `CLAUDE_CODE_OAUTH_TOKEN` 值仍然可以作为显式覆盖
- Hermes 在原生 Messages API 调用前会预检 Anthropic 凭证刷新
- 在后备路径中，Hermes 在重建 Anthropic 客户端后仍会在返回 401 时重试一次

## OpenAI Codex 路径

Codex 使用单独的 Responses API 路径：

- `api_mode = codex_responses`
- 专用凭证解析和认证存储（auth store）支持

## 辅助模型路由

辅助任务，例如：

- 视觉（vision）
- 网页提取摘要（web extraction summarization）
- 上下文压缩摘要（context compression summaries）
- 技能中枢操作（skills hub operations）
- MCP 辅助操作（MCP helper operations）
- 内存刷新（memory flushes）

可以使用它们自己的提供者/模型路由，而不是主对话模型。

当辅助任务配置了提供者 `main` 时，Hermes 会通过与普通聊天相同的共享运行时路径进行解析。实际意味着：

- 环境变量驱动的自定义端点仍然有效
- 通过 `hermes model` / `config.yaml` 保存的自定义端点也有效
- 辅助路由可以区分真正保存的自定义端点和 OpenRouter 后备路径

## 后备模型（Fallback models）

Hermes 支持配置的后备提供者链——当主模型遇到错误时，按顺序尝试的 `(provider, model)` 条目列表。为了向后兼容，仍然接受旧的单对 `fallback_model` 字典（并在首次写入时迁移）。

### 内部工作原理

1. **存储**：`AIAgent.__init__` 存储 `fallback_model` 字典，并设置 `_fallback_activated = False`。

2. **触发点**：`_try_activate_fallback()` 在 `run_agent.py` 的主重试循环中的三个位置被调用：
   - 在无效 API 响应（None choices、内容缺失）达到最大重试次数后
   - 在不可重试的客户端错误（HTTP 401、403、404）上
   - 在临时错误（HTTP 429、500、502、503）达到最大重试次数后

3. **激活流程**（`_try_activate_fallback`）：
   - 如果已经激活或未配置，立即返回 `False`
   - 调用 `auxiliary_client.py` 中的 `resolve_provider_client()` 以构建带有正确认证的新客户端
   - 确定 `api_mode`：对于 openai-codex 为 `codex_responses`，对于 anthropic 为 `anthropic_messages`，其他所有情况为 `chat_completions`
   - 原地替换：`self.model`、`self.provider`、`self.base_url`、`self.api_mode`、`self.client`、`self._client_kwargs`
   - 对于 anthropic 后备：构建原生 Anthropic 客户端而不是兼容 OpenAI 的
   - 重新评估提示缓存（针对 OpenRouter 上的 Claude 模型启用）
   - 设置 `_fallback_activated = True`——防止再次触发
   - 将重试计数重置为 0 并继续循环

4. **配置流程**：
   - CLI：`cli.py` 读取 `CLI_CONFIG["fallback_model"]` → 传递给 `AIAgent(fallback_model=...)`
   - 网关：`gateway/run.py._load_fallback_model()` 读取 `config.yaml` → 传递给 `AIAgent`
   - 验证：`provider` 和 `model` 键都必须非空，否则禁用后备

### 不支持后备的情况

- **子代理委托**（`tools/delegate_tool.py`）：子代理继承父提供者，但不继承后备配置
- **辅助任务**：使用自己独立的提供者自动检测链（请参见上面的辅助模型路由）

定时任务**支持**后备：`run_job()` 从 `config.yaml` 读取 `fallback_providers`（或旧的 `fallback_model`）并将其传递给 `AIAgent(fallback_model=...)`，匹配网关的 `_load_fallback_model()` 模式。请参见 [Cron 内部](./cron-internals.md)。

### 测试覆盖

后备行为在多个测试套件中进行了测试：

- `tests/run_agent/test_fallback_credential_isolation.py` — 主提供者和后备之间的凭证隔离
- `tests/hermes_cli/test_fallback_cmd.py` — `/fallback` CLI 命令
- `tests/gateway/test_fallback_eviction.py` — 网关驱逐失败的提供者

## 相关文档

- [代理循环内部](./agent-loop.md)
- [ACP 内部](./acp-internals.md)
- [上下文压缩与提示缓存](./context-compression-and-caching.md)