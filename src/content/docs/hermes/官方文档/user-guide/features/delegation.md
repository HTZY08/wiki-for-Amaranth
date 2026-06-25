--- frontmatter ---
---
sidebar_position: 7
title: "子代理委托（Subagent Delegation）"
description: "通过 delegate_task 为并行工作流生成隔离的子代理"
---

--- body ---
# 子代理委托（Subagent Delegation）

`delegate_task` 工具会生成具有隔离上下文、受限工具集以及各自终端会话的子 AIAgent 实例。每个子代理获得全新的会话并独立工作——只有其最终摘要才会进入父代理的上下文。

## 单任务

```python
delegate_task(
    goal="Debug why tests fail",
    context="Error: assertion in test_foo.py line 42",
    toolsets=["terminal", "file"]
)
```

## 并行批处理

默认最多 3 个并发子代理（可配置，无硬上限）：

```python
delegate_task(tasks=[
    {"goal": "Research topic A", "toolsets": ["web"]},
    {"goal": "Research topic B", "toolsets": ["web"]},
    {"goal": "Fix the build", "toolsets": ["terminal", "file"]}
])
```

## 子代理上下文如何工作

:::warning 关键：子代理一无所知
子代理以**完全全新的会话**启动。它们对父代理的会话历史、之前的工具调用或委托前讨论的任何内容一无所知。子代理的唯一上下文来自父代理调用 `delegate_task` 时填充的 `goal` 和 `context` 字段。
:::

这意味着父代理必须在调用中将子代理所需的**所有内容**传递过去：

```python
# 不好 - 子代理不知道"那个错误"是什么
delegate_task(goal="Fix the error")

# 好 - 子代理拥有所需的所有上下文
delegate_task(
    goal="Fix the TypeError in api/handlers.py",
    context="""文件 api/handlers.py 在第 47 行出现 TypeError：
    'NoneType' object has no attribute 'get'。
    函数 process_request() 从 parse_body() 接收一个 dict，
    但当 Content-Type 缺失时，parse_body() 返回 None。
    项目位于 /home/user/myproject，使用 Python 3.11。"""
)
```

子代理会收到一个基于你的目标和上下文构建的集中式系统提示，指示它完成任务，并提供结构化的摘要，说明它做了什么、发现了什么、修改了哪些文件以及遇到了哪些问题。

## 实用示例

### 并行研究

同时研究多个主题并收集摘要：

```python
delegate_task(tasks=[
    {
        "goal": "Research the current state of WebAssembly in 2025",
        "context": "Focus on: browser support, non-browser runtimes, language support",
        "toolsets": ["web"]
    },
    {
        "goal": "Research the current state of RISC-V adoption in 2025",
        "context": "Focus on: server chips, embedded systems, software ecosystem",
        "toolsets": ["web"]
    },
    {
        "goal": "Research quantum computing progress in 2025",
        "context": "Focus on: error correction breakthroughs, practical applications, key players",
        "toolsets": ["web"]
    }
])
```

### 代码审查 + 修复

将审查并修复的工作流委托给一个新的上下文：

```python
delegate_task(
    goal="Review the authentication module for security issues and fix any found",
    context="""项目位于 /home/user/webapp。
    认证模块文件：src/auth/login.py, src/auth/jwt.py, src/auth/middleware.py。
    项目使用 Flask、PyJWT 和 bcrypt。
    重点检查：SQL注入、JWT验证、密码处理、会话管理。
    修复发现的任何问题，并运行测试套件（pytest tests/auth/）。""",
    toolsets=["terminal", "file"]
)
```

### 多文件重构

将可能会淹没父代理上下文的大型重构任务委托出去：

```python
delegate_task(
    goal="Refactor all Python files in src/ to replace print() with proper logging",
    context="""项目位于 /home/user/myproject。
    使用 'logging' 模块，logger = logging.getLogger(__name__)。
    将 print() 调用替换为适当的日志级别：
    - print(f"Error: ...") -> logger.error(...)
    - print(f"Warning: ...") -> logger.warning(...)
    - print(f"Debug: ...") -> logger.debug(...)
    - 其他 print -> logger.info(...)
    不要更改测试文件或 CLI 输出中的 print()。
    之后运行 pytest 以验证没有破坏任何内容。""",
    toolsets=["terminal", "file"]
)
```

## 批处理模式详情

当你提供一个 `tasks` 数组时，子代理使用线程池**并行**运行：

- **最大并发数：** 默认 3 个任务（可通过 `delegation.max_concurrent_children` 或 `DELEGATION_MAX_CONCURRENT_CHILDREN` 环境变量配置；最小为 1，无硬上限）。超过限制的批次会返回工具错误，而不是静默截断。
- **线程池：** 使用 `ThreadPoolExecutor`，最大工作线程数为配置的并发限制。
- **进度展示：** 在 CLI 模式下，会以树形视图实时显示每个子代理的工具调用，并带有每个任务的完成行。在网关模式下，进度会分批转发给父代理的进度回调。
- **结果排序：** 结果按任务索引排序以匹配输入顺序，无论完成顺序如何。
- **中断传播：** 中断父代理（例如发送新消息）会中断所有活跃的子代理。

单任务委托直接运行，没有线程池开销。

## 模型覆盖

你可以通过 `config.yaml` 为子代理配置不同的模型——这对于将简单任务委托给更便宜/更快的模型非常有用：

```yaml
# 在 ~/.hermes/config.yaml 中
delegation:
  model: "google/gemini-flash-2.0"    # 子代理使用更便宜的模型
  provider: "openrouter"              # 可选：将子代理路由到不同的提供商
```

如果省略，子代理使用与父代理相同的模型。

## 工具集选择技巧

`toolsets` 参数控制子代理可以访问的工具。根据任务进行选择：

| 工具集模式 | 使用场景 |
|----------------|----------|
| `["terminal", "file"]` | 代码工作、调试、文件编辑、构建 |
| `["web"]` | 研究、事实核查、文档查找 |
| `["terminal", "file", "web"]` | 全栈任务（默认） |
| `["file"]` | 只读分析、代码审查（不执行） |
| `["terminal"]` | 系统管理、进程管理 |

无论你指定什么，某些工具集对子代理都会被阻止：
- `delegation` — 对叶子子代理（默认）阻止。对于 `role="orchestrator"` 的子代理保留，受 `max_spawn_depth` 限制——请参见下面的[深度限制与嵌套编排](#depth-limit-and-nested-orchestration)。
- `clarify` — 子代理无法与用户交互
- `memory` — 不允许写入共享持久内存
- `code_execution` — 子代理应逐步推理
- `send_message` — 无跨平台副作用（例如发送 Telegram 消息）

## 最大迭代次数

每个子代理都有一个迭代限制（默认 50），控制它可以进行的工具调用轮数：

```python
delegate_task(
    goal="Quick file check",
    context="Check if /etc/nginx/nginx.conf exists and print its first 10 lines",
    max_iterations=10  # 简单任务，不需要太多轮次
)
```

## 子代理超时

默认情况下，子代理**没有挂钟超时**。子代理只会因为实际做的事情而失败——API 错误、工具错误或达到迭代预算——永远不会因为委托级别的倒计时而死亡。早期版本有一个硬上限（300 秒，后来 600 秒），这常常在中途杀死真正忙碌的子代理：深入的代码审查、大规模的研究扩展和慢速推理模型通常需要超过 10 分钟，同时持续稳步推进。

真正卡住的子代理仍然会被检测到：当子代理没有进展时（没有 API 调用，没有工具启动），心跳陈旧性监视器会停止刷新父代理的活动，从而让网关非活动超时在一个真正卡住的工作器上触发。

如果你无论如何都想要一个硬上限（例如在无人值守的 cron 驱动的委托中进行成本控制），可以在每个安装中启用：

```yaml
delegation:
  child_timeout_seconds: 0     # 默认：0 = 无超时
  # child_timeout_seconds: 1800  # 选择加入的硬上限（最小 30 秒）
```

一个正值会对每个子代理强制施加一个硬挂钟限制；`0` 或负值会禁用它。

:::tip 零调用超时的诊断转储
在配置了硬上限的情况下，如果子代理在进行了**零次** API 调用（通常是：提供商不可达、认证失败或工具模式被拒绝）的情况下超时，`delegate_task` 会将结构化诊断写入 `~/.hermes/logs/subagent-timeout-<session>-<timestamp>.log`，其中包含子代理的配置快照、凭据解析跟踪以及任何早期错误消息。比起之前的静默超时行为，这更容易排查根本原因。
:::

## 监控运行中的子代理（`/agents`）

TUI 带有一个 `/agents` 覆盖（别名 `/tasks`），将递归的 `delegate_task` 展开变成一个一流的审计面板：

- 运行中和最近完成的子代理的实时树形视图，按父代理分组
- 每个分支的成本、令牌和文件接触汇总
- 杀死和暂停控制——在不中断其兄弟的情况下中途取消特定子代理
- 事后审查：即使在子代理返回父代理后，也可以逐步查看每个子代理的逐轮历史

经典 CLI 只是将 `/agents` 打印为文本摘要；覆盖层在 TUI 中才大放异彩。请参见 [TUI — 斜杠命令](/user-guide/tui#slash-commands)。

## 深度限制与嵌套编排

默认情况下，委托是**扁平的**：父代理（深度 0）生成子代理（深度 1），这些子代理无法进一步委托。这可以防止失控的递归委托。

对于多阶段工作流（研究 → 综合，或对子问题进行并行编排），父代理可以生成**编排器（orchestrator）** 子代理，这些子代理*可以*委托自己的工作器：

```python
delegate_task(
    goal="Survey three code review approaches and recommend one",
    role="orchestrator",  # 允许此子代理生成自己的工作器
    context="...",
)
```

- `role="leaf"`（默认）：子代理不能进一步委托——与扁平委托行为相同。
- `role="orchestrator"`：子代理保留 `delegation` 工具集。受 `delegation.max_spawn_depth`（默认 **1** = 扁平，因此默认情况下 `role="orchestrator"` 无效）控制。将 `max_spawn_depth` 提高到 2 以允许编排器子代理生成叶子孙代理；3+ 用于更深的树。没有上限——成本是实际限制。
- `delegation.orchestrator_enabled: false`：全局关闭开关，无论 `role` 参数如何，都强制每个子代理为 `leaf`。

**成本警告：** 使用 `max_spawn_depth: 3` 和 `max_concurrent_children: 3`，树可以达到 3×3×3 = 27 个并发叶子代理。每多一层都会增加开销——请有意识地提高 `max_spawn_depth`。

## 生命周期与持久性

:::warning delegate_task 是同步的——不可持久
`delegate_task` 在**父代理的当前轮次内部**运行。它会阻塞父代理，直到每个子代理完成（或被取消）。它**不是**后台任务队列：

- 如果父代理被中断（用户发送新消息、`/stop`、`/new`），所有活跃子代理都会被取消并返回 `status="interrupted"`。它们正在进行的工作会被丢弃。
- 子代理在父代理轮次结束后**不会**继续运行。
- 被取消的子代理返回结构化结果（`status="interrupted"`, `exit_reason="interrupted"`），但由于父代理也被中断了，该结果通常永远不会出现在用户可见的回复中。

对于必须能在中断后存活或超出当前轮次的**持久性长时间运行工作**，请使用：

- `cronjob` (action=`create`) — 安排一个单独的代理运行；不受父代理轮次中断的影响。
- `terminal(background=True, notify_on_complete=True)` — 长时间运行的 shell 命令，当代理做其他事情时继续运行。
:::

## 关键属性

- 每个子代理获得**自己的终端会话**（与父代理分离）
- **嵌套委托是可选的**——只有 `role="orchestrator"` 的子代理才能进一步委托，并且只有当 `max_spawn_depth` 从默认值 1（扁平）提高时才允许。通过 `orchestrator_enabled: false` 全局禁用。
- 叶子子代理**不能**调用：`delegate_task`、`clarify`、`memory`、`send_message`、`execute_code`。编排器子代理保留 `delegate_task`，但仍然不能使用其他四个。
- **中断传播**——中断父代理会中断所有活跃的子代理（包括编排器下的孙代理）
- 只有最终摘要进入父代理的上下文，使令牌使用保持高效
- 子代理继承父代理的 **API 密钥、提供商配置和凭据池**（允许在速率限制时进行密钥轮换）

## 委托 vs execute_code

| 因素 | delegate_task | execute_code |
|--------|--------------|-------------|
| **推理** | 完整的 LLM 推理循环 | 仅 Python 代码执行 |
| **上下文** | 全新的隔离会话 | 无会话，仅脚本 |
| **工具访问** | 所有非阻塞工具，带推理 | 通过 RPC 的 7 个工具，无推理 |
| **并行性** | 默认 3 个并发子代理（可配置） | 单个脚本 |
| **最佳用途** | 需要判断的复杂任务 | 机械的多步骤管道 |
| **令牌成本** | 较高（完整 LLM 循环） | 较低（仅返回 stdout） |
| **用户交互** | 无（子代理无法澄清） | 无 |

**经验法则：** 当子任务需要推理、判断或多步骤问题解决时，使用 `delegate_task`。当你需要机械的数据处理或脚本化工作流时，使用 `execute_code`。

## 配置

```yaml
# 在 ~/.hermes/config.yaml 中
delegation:
  max_iterations: 50                        # 每个子代理的最大轮次（默认：50）
  # max_concurrent_children: 3              # 每批的并行子代理数（默认：3）
  # max_spawn_depth: 1                      # 树深度（最小 1，无上限，默认 1 = 扁平）。提高到 2 以允许编排器子代理生成叶子；3+ 用于更深的树。
  # orchestrator_enabled: true              # 禁用以强制所有子代理为叶子角色。
  model: "google/gemini-3-flash-preview"             # 可选的提供商/模型覆盖
  provider: "openrouter"                             # 可选的内置提供商
  api_mode: anthropic_messages                       # 可选；对于 anthropic_messages 端点，从 base_url 自动检测

# 或者使用直接的自定义端点而不是提供商：
delegation:
  model: "qwen2.5-coder"
  base_url: "http://localhost:1234/v1"
  api_key: "local-key"
  # api_mode: "anthropic_messages"  # 可选。针对 base_url 的线协议覆盖（"chat_completions"、"codex_responses" 或 "anthropic_messages"）。空值 = 从 URL 自动检测（例如 /anthropic 后缀）。对于启发式无法分类的端点（Azure AI Foundry、MiniMax、Zhipu GLM、LiteLLM 代理等），显式设置。
```

当 `base_url` 指向一个兼容 Anthropic 的端点——例如以 `/anthropic` 结尾的路径、Azure Foundry Claude 路由或 MiniMax `/anthropic` 代理——`api_mode` 会被自动检测为 `anthropic_messages`，子代理无需设置即可使用正确的线格式。当自动检测猜测错误时（很少见），显式设置 `api_mode`。

:::tip
代理会根据任务复杂度自动处理委托。你无需明确要求它委托——它会在有意义的时候这样做。
:::