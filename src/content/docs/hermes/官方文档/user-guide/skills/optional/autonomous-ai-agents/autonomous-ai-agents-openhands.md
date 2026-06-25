---
title: Openhands
---

title: "Openhands — 将编码任务委托给 OpenHands CLI（模型无关，基于 LiteLLM）"
sidebar_label: "Openhands"
description: "将编码任务委托给 OpenHands CLI（模型无关，基于 LiteLLM）"
---

--- body ---
{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Openhands

将编码任务委托给 OpenHands CLI（模型无关，基于 LiteLLM）。

## 技能元数据（Skill metadata）

| | |
|---|---|
| 来源（Source） | 可选 — 使用 `hermes skills install official/autonomous-ai-agents/openhands` 安装 |
| 路径（Path） | `optional-skills/autonomous-ai-agents/openhands` |
| 版本（Version） | `0.1.0` |
| 作者（Author） | Tim Koepsel (xzessmedia), Hermes Agent |
| 许可证（License） | MIT |
| 平台（Platforms） | linux, macos |
| 标签（Tags） | `Coding-Agent`, `OpenHands`, `Model-Agnostic`, `LiteLLM` |
| 相关技能（Related skills） | [`claude-code`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code), [`codex`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex), [`opencode`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-opencode), [`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) |

## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。当技能处于激活状态时，代理（Agent）会看到以下指令。
:::

# OpenHands CLI

通过 `terminal` 工具将编码任务委托给 [OpenHands CLI](https://github.com/All-Hands-AI/OpenHands)。OpenHands 是模型无关的：支持任何 LiteLLM 支持的提供商（OpenAI、Anthropic、OpenRouter、DeepSeek、Ollama、vLLM 等）。

该技能是无头模式（headless-mode）的包装器，用于批处理/一次性委托。在 Hermes 中不使用交互式文本界面。

## 何时使用

- 用户希望将编码任务专门委托给 OpenHands。
- 用户希望使用可在非 Anthropic / 非 OpenAI 提供商（DeepSeek、Qwen、Ollama、vLLM、Nous 等）上运行的编码代理——兄弟技能 `claude-code` 和 `codex` 都绑定在单一供应商上。
- 在工作区内需要进行多步骤文件编辑和 shell 命令。

对于 Claude 原生场景，优先使用 `claude-code`。对于 OpenAI 原生场景，优先使用 `codex`。对于 Hermes 原生子代理，使用 `delegate_task`。

## 前置条件（Prerequisites）

1. 安装上游（需要 Python 3.12+ 和 `uv`）：

   ```
   terminal(command="uv tool install openhands --python 3.12")
   ```

   验证：`openhands --version`（截至编写时，当前版本为 `OpenHands CLI 1.16.0` / `SDK v1.21.0`）。

2. 选择一个模型，并为 `--override-with-envs` 设置环境变量：

   ```
   export LLM_MODEL=openrouter/openai/gpt-4o-mini       # 或任何 LiteLLM 的完整标识符
   export LLM_API_KEY=$OPENROUTER_API_KEY
   export LLM_BASE_URL=https://openrouter.ai/api/v1     # 如果使用原生 OpenAI 则省略
   ```

   `LLM_MODEL` 使用 LiteLLM 的完整标识符。当提供商为 OpenRouter 时，标识符是双重前缀：`openrouter/<供应商>/<模型>`（例如 `openrouter/anthropic/claude-sonnet-4.5`）。对于原生 Anthropic：`anthropic/claude-sonnet-4-5`。对于原生 OpenAI：`openai/gpt-4o-mini`。

3. 抑制启动横幅，以便 JSON 输出前不会被 ASCII 艺术画干扰：

   ```
   export OPENHANDS_SUPPRESS_BANNER=1
   ```

## 如何运行

始终通过 `terminal` 工具调用。自动化时始终传递 `--headless --json --override-with-envs --exit-without-confirmation`。

### 一次性任务

```
terminal(
  command="OPENHANDS_SUPPRESS_BANNER=1 LLM_MODEL=openrouter/openai/gpt-4o-mini LLM_API_KEY=$OPENROUTER_API_KEY LLM_BASE_URL=https://openrouter.ai/api/v1 openhands --headless --json --override-with-envs --exit-without-confirmation -t '为 src/ 中所有 API 调用添加错误处理'",
  workdir="/path/to/project",
  timeout=600
)
```

### 长时间任务（后台运行）

```
terminal(command="<同上>", workdir="/path/to/project", background=true, notify_on_complete=true)
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")
```

### 恢复之前的对话

OpenHands 会在每次运行结束时打印 `Conversation ID: <32-hex>` 和 `Hint: openhands --resume <dashed-uuid>`。使用带连字符的形式进行恢复：

```
terminal(
  command="OPENHANDS_SUPPRESS_BANNER=1 LLM_MODEL=... openhands --headless --json --override-with-envs --exit-without-confirmation --resume <dashed-uuid> -t '现在修复你发现的 bug'",
  workdir="/path/to/project"
)
```

## 实际标志列表（Real Flag List）

已验证自 `openhands --help`（CLI 1.16.0）。本表中未列出的不是标志——请通过环境变量或设置文件传递。

| 标志 | 作用 |
|------|--------|
| `--headless` | 无 UI，需要 `-t` 或 `-f`。自动批准所有操作（在此模式下无 `--llm-approve`）。 |
| `--json` | JSONL 事件流（需要 `--headless`）。 |
| `-t TEXT` | 任务提示（Task prompt）。 |
| `-f PATH` | 从文件读取任务。 |
| `--resume [ID]` | 恢复对话。无 ID 则列出最近的对话。 |
| `--last` | 恢复最近的对话（与 `--resume` 一起使用）。 |
| `--override-with-envs` | 应用 `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL` 环境变量。如果不使用此标志，OpenHands 将使用 `~/.openhands/settings.json` 并忽略环境变量。 |
| `--exit-without-confirmation` | 不显示“你确定吗？”退出对话框。 |
| `--always-approve` / `--yolo` | 自动批准每个操作（`--headless` 模式下默认）。 |
| `--llm-approve` | 基于 LLM 的安全门（仅交互模式——在无头模式下无效）。 |
| `--version` / `-v` | 打印版本并退出。 |

**没有 `--model`、`--max-iterations`、`--workspace`、`--sandbox`、`--sandbox-type` 标志。** 模型由 `LLM_MODEL` 指定。工作区是你传递给 `terminal` 工具的 `workdir`。沙箱/运行时由 `RUNTIME` 和 `SANDBOX_VOLUMES` 环境变量指定。

## JSON 事件模式（JSON Event Schema）

使用 `--json --headless` 时，OpenHands 输出 JSONL——每行一个 JSON 对象，外加一些非 JSON 状态行（`Initializing agent...`、`Agent is working`、`Agent finished`、最终的摘要框、`Goodbye!`、`Conversation ID:`、`Hint:`）。过滤以 `{` 开头的行。

顶层的 `kind` 字段区分事件：

- `MessageEvent` — 用户/代理的文本轮次。`source` 为 `user` 或 `agent`。
- `ActionEvent` — 代理选择了某个工具。读取 `tool_name`（`file_editor`、`terminal`、`finish`）和 `action.kind`（`FileEditorAction`、`TerminalAction`、`FinishAction`）。
- `ObservationEvent` — 工具结果。`observation.is_error` 是成功标志。`source` 为 `environment`。
- `ActionEvent` 中的 `FinishAction` 携带代理的最终消息，位于 `action.message`。

CLI 首先打印所有来自 LiteLLM/Authlib 的 stderr——请参阅常见陷阱（Pitfalls）。仅解析 stdout，逐行处理，忽略不以 `{` 开头的行。

## 常见陷阱（Pitfalls）

- **每次调用都会出现 LiteLLM 警告。** CLI 会向 stderr 打印 `bedrock-runtime` 和 `sagemaker-runtime` 警告，因为未安装 `botocore`。还有一个 Authlib 弃用警告。这些是噪音，并非失败。将 stderr 重定向到 `/dev/null`，或在显示给用户之前过滤掉。
- **横幅垃圾信息。** 如果没有 `OPENHANDS_SUPPRESS_BANNER=1`，每次运行都会以多行 `+--+` ASCII 框开头，宣传 SDK。始终导出它。
- **`--override-with-envs` 对于自动化是必需的。** 如果没有它，OpenHands 会忽略 `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL`，并回退到 `~/.openhands/settings.json`。在新安装的系统上，该文件不存在，CLI 会挂起等待首次运行设置。
- **模型标识符是 LiteLLM 的，而不是提供商的。** `openrouter/openai/gpt-4o-mini` 有效；`openai/gpt-4o-mini` 指向 OpenRouter 时无效。`anthropic/claude-sonnet-4-5`（连字符）是原生 Anthropic；`openrouter/anthropic/claude-sonnet-4.5`（点号）是通过 OpenRouter 的。搞错了就会收到神秘的 LiteLLM 400 错误。
- **`pip install openhands-ai` 是错误包。** 那是最老的 V0 SDK。新的 CLI 是 `uv tool install openhands --python 3.12`。没有维护的 conda 包。
- **恢复 ID 格式很麻烦。** CLI 以 `Conversation ID: f46573d9cfdb45e492ca189bde40019b`（无连字符）结尾，然后是一个 `Hint: openhands --resume f46573d9-cfdb-45e4-92ca-189bde40019b`（带连字符）。使用带连字符的形式。
- **无头模式忽略 `--llm-approve`。** 如果你传递它，会收到 argparse 错误。无头模式硬编码为始终批准。
- **上游不支持 Windows。** OpenHands 文档要求在 Windows 上使用 WSL。因此本技能在 `[linux, macos]` 平台上启用。
- **`~/.openhands/conversations/<id>/` 会累积。** 每次运行都会持久化一个轨迹。如果运行批处理，请定期清理。
- **安装较重（约 200 个包）。** 使用 `uv tool install`（隔离的 venv）避免与活动项目产生依赖冲突。

## 验证

```
terminal(
  command="OPENHANDS_SUPPRESS_BANNER=1 LLM_MODEL=openrouter/openai/gpt-4o-mini LLM_API_KEY=$OPENROUTER_API_KEY LLM_BASE_URL=https://openrouter.ai/api/v1 openhands --headless --json --override-with-envs --exit-without-confirmation -t '通过 terminal 工具向 stdout 打印字符串 OPENHANDS_OK。'",
  workdir="/tmp",
  timeout=120
)
```

如果 JSONL 流以一个 `FinishAction` 结束，且其 `action.message` 中提到 `OPENHANDS_OK`，则安装成功。

## 相关链接（Related）

- [OpenHands GitHub](https://github.com/All-Hands-AI/OpenHands)
- [OpenHands CLI 命令参考](https://docs.openhands.dev/openhands/usage/cli/command-reference)
- 兄弟技能：`claude-code`（仅 Anthropic）、`codex`（仅 OpenAI）、`opencode`（通过 OpenCode 支持多提供商）、`hermes-agent`（通过 `delegate_task` 的 Hermes 子代理）。