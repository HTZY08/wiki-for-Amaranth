---
title: 上下文压缩与缓存
description: Hermes Agent 官方文档汉化版
---

# 上下文压缩与缓存

Hermes Agent 使用双重压缩系统和 Anthropic 提示缓存（prompt caching）来高效管理长对话中的上下文窗口使用。

源文件：`agent/context_engine.py`（ABC）、`agent/context_compressor.py`（默认引擎）、`agent/prompt_caching.py`、`gateway/run.py`（会话卫生）、`run_agent.py`（搜索 `_compress_context`）

## 可插拔上下文引擎

上下文管理基于 `ContextEngine` ABC（`agent/context_engine.py`）。内置的 `ContextCompressor` 是默认实现，但插件可替换为其他引擎（例如，无损上下文管理 Lossless Context Management）。

```yaml
context:
  engine: "compressor"    # 默认 — 内置的有损摘要
  engine: "lcm"           # 示例 — 提供无损上下文的插件
```

引擎负责：
- 决定何时应该触发压缩（`should_compress()`）
- 执行压缩（`compress()`）
- 可选地暴露代理可调用的工具（例如 `lcm_grep`）
- 跟踪来自 API 响应的令牌使用量

选择通过 `config.yaml` 中的 `context.engine` 配置驱动。解析顺序：
1. 检查 `plugins/context_engine/<name>/` 目录
2. 检查通用插件系统（`register_context_engine()`）
3. 回退到内置 `ContextCompressor`

插件引擎**永远不会自动激活**——用户必须显式地将 `context.engine` 设置为插件的名称。默认的 `"compressor"` 始终使用内置引擎。

通过 `hermes plugins` → Provider Plugins → Context Engine 配置，或直接编辑 `config.yaml`。

有关构建上下文引擎插件，请参阅 [Context Engine Plugins](/developer-guide/context-engine-plugin)。

## 双重压缩系统

Hermes 具有两个独立运行的压缩层：

```
                     ┌──────────────────────────┐
  传入消息            │  网关会话卫生             │  在上下文容量的 85% 触发
  ─────────────────► │  (pre-agent, rough est.) │  大型会话的安全网
                     └─────────────┬────────────┘
                                   │
                                   ▼
                     ┌──────────────────────────┐
                     │  代理 ContextCompressor   │  在上下文容量的 50% 触发（默认）
                     │  (in-loop, real tokens)  │  常规上下文管理
                     └──────────────────────────┘
```

### 1. 网关会话卫生（85% 阈值）

位于 `gateway/run.py`（搜索 `Session hygiene: auto-compress`）。这是一个**安全网**，在代理处理消息之前运行。它防止会话轮次之间增长过大时出现 API 失败（例如，Telegram/Discord 中的隔夜累积）。

- **阈值**：固定为模型上下文长度的 85%
- **令牌来源**：优先使用上一轮实际报告的 API 令牌；回退到基于字符的粗略估算（`estimate_messages_tokens_rough`）
- **触发时机**：仅当 `len(history) >= 4` 且压缩启用时
- **目的**：捕获逃过代理自身压缩器的会话

网关卫生阈值故意高于代理的压缩器。将其设置为 50%（与代理相同）会导致在长网关会话中的每一轮都过早压缩。

### 2. 代理 ContextCompressor（50% 阈值，可配置）

位于 `agent/context_compressor.py`。这是**主要压缩系统**，在代理的工具循环内运行，可以访问准确的、API 报告的令牌计数。

## 配置

所有压缩设置从 `config.yaml` 的 `compression` 键下读取：

```yaml
compression:
  enabled: true              # 启用/禁用压缩（默认：true）
  threshold: 0.50            # 上下文窗口的百分比（默认：0.50 = 50%）
  target_ratio: 0.20         # 保留尾部占阈值的比例（默认：0.20）
  protect_last_n: 20         # 最小保护的尾部消息数（默认：20）
  codex_gpt55_autoraise: true  # Codex OAuth 上的 gpt-5.5：将触发阈值提高到 85%（默认：true）

# 在 auxiliary 下配置摘要模型/提供商：
auxiliary:
  compression:
    model: null              # 覆盖摘要模型（默认：自动检测）
    provider: auto           # 提供商："auto"、"openrouter"、"nous"、"main" 等
    base_url: null           # 自定义 OpenAI 兼容端点
```

### 参数详情

| 参数 | 默认值 | 范围 | 描述 |
|-----------|---------|-------|-------------|
| `threshold` | `0.50` | 0.0-1.0 | 当提示令牌 ≥ `threshold × context_length` 时触发压缩 |
| `target_ratio` | `0.20` | 0.10-0.80 | 控制尾部保护令牌预算：`threshold_tokens × target_ratio` |
| `protect_last_n` | `20` | ≥1 | 始终保留的最近消息的最小数量 |
| `protect_first_n` | `3` | (硬编码) | 始终保留系统提示和第一次对话 |
| `codex_gpt55_autoraise` | `true` | 布尔 | 将 ChatGPT Codex OAuth 路由上的 gpt-5.5 触发阈值提高到 85%（见下文）。设置为 `false` 以保持全局 `threshold` |

### Codex gpt-5.5 阈值自动提高

ChatGPT Codex OAuth 后端将 gpt-5.5 的上下文窗口硬限制为 **272K**（相同的 slug 在 OpenAI 直接 API 和 OpenRouter 上暴露 1.05M，在 GitHub Copilot 上暴露 400K）。在默认的 50% 触发阈值下，压缩将在约 136K 处触发——模型实际可用窗口的一半。当活动路由是 Codex OAuth（`provider: openai-codex`）且模型是 gpt-5.5 时，Hermes 将触发阈值提高到 **85%**（约 231K），并打印一次性通知以及退出命令。仅此确切路由受影响；任何其他提供商上的 gpt-5.5 保持您的全局 `threshold`。要回退到全局值：

```bash
hermes config set compression.codex_gpt55_autoraise false
```

### 计算值（对于默认设置下的 200K 上下文模型）

```
context_length       = 200,000
threshold_tokens     = 200,000 × 0.50 = 100,000
tail_token_budget    = 100,000 × 0.20 = 20,000
max_summary_tokens   = min(200,000 × 0.05, 12,000) = 10,000
```

:::note 阈值源自主模型的上下文窗口
`threshold_tokens` 始终是 `threshold × context_length`，其中 `context_length` 是**主代理模型**的上下文窗口——绝不是辅助/摘要模型的。在一个 262,144 令牌模型上，默认的 `0.50` 下，阈值为 `262,144 × 0.50 = 131,072`。这个数字接近常见的 "128K 上下文" 是百分比的巧合，并非表示辅助模型的窗口是触发器。辅助模型的上下文窗口是另一个问题——参见下面的 "摘要模型上下文长度" 警告，了解它如何影响是否能够生成摘要，而不是压缩何时触发。
:::


## 压缩算法

`ContextCompressor.compress()` 方法遵循 4 阶段算法：

### 阶段 1：修剪旧工具结果（廉价，无 LLM 调用）

保护尾部之外的旧工具结果（>200 个字符）被替换为：
```
[Old tool output cleared to save context space]
```

这是一个廉价的预处理，从冗长的工具输出（文件内容、终端输出、搜索结果）中节省了大量令牌。

### 阶段 2：确定边界

```
┌─────────────────────────────────────────────────────────────┐
│  消息列表                                                   │
│                                                             │
│  [0..2]  ← protect_first_n（系统 + 第一次对话）              │
│  [3..N]  ← 中间轮次 → 被摘要                                 │
│  [N..end] ← 尾部（根据令牌预算或 protect_last_n）            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

尾部保护**基于令牌预算**：从末尾向后走，累积令牌直到预算耗尽。如果预算保护的消息数量少于 `protect_last_n`，则回退到固定的 `protect_last_n` 数量。

边界对齐以避免拆分 tool_call/tool_result 组。`_align_boundary_backward()` 方法会跨过连续的 tool_result 以找到父助手消息，保持组完整。

### 阶段 3：生成结构化摘要

:::warning 摘要模型上下文长度
摘要模型的上下文窗口必须**至少与主代理模型一样大**。整个中间部分在单个 `call_llm(task="compression")` 调用中发送给摘要模型。如果摘要模型的上下文较小，API 将返回上下文长度错误——`_generate_summary()` 捕获该错误，记录警告，并返回 `None`。然后压缩器**在没有摘要的情况下**丢弃中间轮次，静默丢失对话上下文。这是压缩质量下降的最常见原因。
:::

中间轮次使用辅助 LLM 进行摘要，采用结构化模板：

```
## 目标
[用户试图完成什么]

## 约束与偏好
[用户偏好、编码风格、约束、重要决策]

## 进展
### 已完成
[已完成的工作——具体文件路径、运行的命令、结果]
### 进行中
[当前正在进行的工��]
### 受阻
[遇到的任何阻碍或问题]

## 关键决策
[重要的技术决策及原因]

## 相关文件
[已读取、修改或创建的文件——每个文件附简短说明]

## 下一步
[接下来需要做什么]

## 关键上下文
[具体的数值、错误消息、配置细节]
```

摘要预算随被压缩内容的大小缩放：
- 公式：`content_tokens × 0.20`（`_SUMMARY_RATIO` 常量）
- 最小值：2,000 令牌
- 最大值：`min(context_length × 0.05, 12,000)` 令牌

### 阶段 4：组装压缩消息

压缩后的消息列表为：
1. 头部消息（首次压缩时在系统提示后附加一条说明）
2. 摘要消息（角色选择以避免连续相同角色的违规）
3. 尾部消息（未修改）

孤立的 tool_call/tool_result 对由 `_sanitize_tool_pairs()` 清理：
- 引用已删除调用的 tool_result → 删除
- 结果已被删除的 tool_call → 注入存根结果

### 迭代重新压缩

在后续压缩中，之前的摘要会传递给 LLM，并附上**更新**指示，而不是从头开始摘要。这样可以在多次压缩中保留信息——项目从"进行中"移动到"已完成"，添加新进展，移除过时信息。

压缩器实例上的 `_previous_summary` 字段为此目的存储最后的摘要文本。


## 压缩前后示例

### 压缩前（45 条消息，约 95K 令牌）

```
[0] system:    "You are a helpful assistant..." （系统提示）
[1] user:      "Help me set up a FastAPI project"
[2] assistant: <tool_call> terminal: mkdir project </tool_call>
[3] tool:      "directory created"
[4] assistant: <tool_call> write_file: main.py </tool_call>
[5] tool:      "file written (2.3KB)"
    ... 另外 30 轮文件编辑、测试、调试 ...
[38] assistant: <tool_call> terminal: pytest </tool_call>
[39] tool:      "8 passed, 2 failed\n..." （5KB 输出）
[40] user:      "Fix the failing tests"
[41] assistant: <tool_call> read_file: tests/test_api.py </tool_call>
[42] tool:      "import pytest\n..." （3KB）
[43] assistant: "I see the issue with the test fixtures..."
[44] user:      "Great, also add error handling"
```

### 压缩后（25 条消息，约 45K 令牌）

```
[0] system:    "You are a helpful assistant...
               [注意：一些较早的对话轮次已被压缩...]"
[1] user:      "Help me set up a FastAPI project"
[2] assistant: "[CONTEXT COMPACTION] Earlier turns were compacted...

               ## 目标
               设置一个带测试和错误处理的 FastAPI 项目

               ## 进展
               ### 已完成
               - 创建项目结构：main.py, tests/, requirements.txt
               - 在 main.py 中实现了 5 个 API 端点
               - 在 tests/test_api.py 中编写了 10 个测试用例
               - 8/10 测试通过

               ### 进行中
               - 修复 2 个失败的测试（test_create_user, test_delete_user）

               ## 相关文件
               - main.py — 包含 5 个端点的 FastAPI 应用
               - tests/test_api.py — 10 个测试用例
               - requirements.txt — fastapi, pytest, httpx

               ## 下一步
               - 修复失败的测试固件
               - 添加错误处理"
[3] user:      "Fix the failing tests"
[4] assistant: <tool_call> read_file: tests/test_api.py </tool_call>
[5] tool:      "import pytest\n..."
[6] assistant: "I see the issue with the test fixtures..."
[7] user:      "Great, also add error handling"
```


## 提示缓存（Anthropic）

来源：`agent/prompt_caching.py`

通过缓存对话前缀，将多轮对话的输入令牌成本降低约 75%。使用 Anthropic 的 `cache_control` 断点。

### 策略：system_and_3

Anthropic 每次请求最多允许 4 个 `cache_control` 断点。Hermes 使用 "system_and_3" 策略：

```
断点 1：系统提示            （所有轮次稳定）
断点 2：倒数第 3 条非系统消息  ─┐
断点 3：倒数第 2 条非系统消息   ├─ 滚动窗口
断点 4：最后一条非系统消息     ─┘
```

### 工作原理

`apply_anthropic_cache_control()` 深度复制消息并注入 `cache_control` 标记：

```python
# 缓存标记格式
marker = {"type": "ephemeral"}
# 或 1 小时 TTL：
marker = {"type": "ephemeral", "ttl": "1h"}
```

标记根据内容类型不同应用：

| 内容类型 | 标记放置位置 |
|-------------|-------------------|
| 字符串内容 | 转换为 `[{"type": "text", "text": ..., "cache_control": ...}]` |
| 列表内容 | 添加到最后一个元素的字典 |
| None/空 | 添加为 `msg["cache_control"]` |
| 工具消息 | 添加为 `msg["cache_control"]`（仅原生 Anthropic） |

### 缓存感知设计模式

1. **稳定的系统提示**：系统提示是断点 1，并在所有轮次中缓存。避免在对话中途更改它（压缩仅在首次压缩时追加一条说明）。

2. **消息顺序很重要**：缓存命中需要前缀匹配。在中间添加或删除消息会使之后的所有缓存失效。

3. **压缩缓存交互**：压缩后，压缩区域的缓存失效，但系统提示缓存保留。滚动 3 消息窗口会在 1-2 轮内重新建立缓存。

4. **TTL 选择**：默认为 `5m`（5 分钟）。对于用户轮次之间休息的长运行会话，使用 `1h`。

### 启用提示缓存

当以下条件满足时，提示缓存自动启用：
- 模型是 Anthropic Claude 模型（通过模型名称检测）
- 提供商支持 `cache_control`（原生 Anthropic API 或 OpenRouter）

```yaml
# config.yaml — TTL 可配置（必须是 "5m" 或 "1h"）
prompt_caching:
  cache_ttl: "5m"
```

CLI 在启动时显示缓存状态：
```
💾 Prompt caching: ENABLED (Claude via OpenRouter, 5m TTL)
```


## 上下文压力警告

中间上下文压力警告已被移除（参见 `run_agent.py` 中的迭代预算块，其中注明："没有中间压力警告——它们会导致模型在复杂任务中过早'放弃'"）。当提示令牌达到配置的 `compression.threshold`（默认 50%）时，压缩触发，无事先警告步骤；网关会话卫生作为辅助安全网在模型上下文窗口的 85% 处触发。