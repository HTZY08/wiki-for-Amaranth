---
sidebar_position: 2
title: "ACP 内部机制"
description: "ACP 适配器的工作原理：生命周期、会话、事件桥、审批和工具渲染"
---

# ACP 内部机制

ACP 适配器将 Hermes 的同步 `AIAgent` 封装在一个异步 JSON-RPC stdio 服务器中。

关键实现文件：

- `acp_adapter/entry.py`
- `acp_adapter/server.py`
- `acp_adapter/session.py`
- `acp_adapter/events.py`
- `acp_adapter/permissions.py`
- `acp_adapter/tools.py`
- `acp_adapter/auth.py`
- `acp_registry/agent.json`

## 启动流程

```text
hermes acp / hermes-acp / python -m acp_adapter
  -> acp_adapter.entry.main()
  -> 解析 --version / --check / --setup（在服务器启动前）
  -> 加载 ~/.hermes/.env
  -> 配置 stderr 日志
  -> 构造 HermesACPAgent
  -> acp.run_agent(agent, use_unstable_protocol=True)
```

Zed ACP Registry 路径通过 `uvx --from 'hermes-agent[acp]==<version>' hermes-acp` 启动相同的适配器，指向 `hermes-agent` PyPI 发布版本。

标准输出保留用于 ACP JSON-RPC 传输。人类可读的日志输出到 stderr。

## 主要组件

### `HermesACPAgent`

`acp_adapter/server.py` 实现了 ACP 代理（Agent）协议。

职责：

- 初始化 / 认证
- new/load/resume/fork/list/cancel 会话方法
- 提示（Prompt）执行
- 会话模型切换
- 将同步 AIAgent 回调连接到 ACP 异步通知

### `SessionManager`

`acp_adapter/session.py` 跟踪活动的 ACP 会话。

每个会话存储：

- `session_id`
- `agent`
- `cwd`
- `model`
- `history`
- `cancel_event`

管理器是线程安全的，支持：

- create
- get
- remove
- fork
- list
- cleanup
- cwd 更新

### 事件桥

`acp_adapter/events.py` 将 AIAgent 回调转换为 ACP `session_update` 事件。

桥接的回调：

- `tool_progress_callback`
- `thinking_callback`（目前在 ACP 桥中设置为 `None`——推理内容通过 `step_callback` 转发）
- `step_callback`

由于 `AIAgent` 在工作线程中运行，而 ACP I/O 位于主事件循环上，桥使用：

```python
asyncio.run_coroutine_threadsafe(...)
```

### 权限桥

`acp_adapter/permissions.py` 将危险的终端审批提示转换为 ACP 权限请求。

映射：

- `allow_once` -> Hermes `once`
- `allow_always` -> Hermes `always`
- 拒绝选项 -> Hermes `deny`

超时和桥接失败默认拒绝。

### 工具渲染辅助函数

`acp_adapter/tools.py` 将 Hermes 工具映射到 ACP 工具类型，并构建面向编辑器的显示内容。

示例：

- `patch` / `write_file` -> 文件差异
- `terminal` -> shell 命令文本
- `read_file` / `search_files` -> 文本预览
- 大结果 -> 为 UI 安全截断的文本块

## 会话生命周期

```text
new_session(cwd)
  -> 创建 SessionState
  -> 创建 AIAgent(platform="acp", enabled_toolsets=["hermes-acp"])
  -> 绑定 task_id/session_id 到 cwd 覆盖

prompt(..., session_id)
  -> 从 ACP 内容块中提取文本
  -> 重置取消事件
  -> 安装回调 + 审批桥
  -> 在 ThreadPoolExecutor 中运行 AIAgent
  -> 更新会话历史
  -> 发送最终的代理消息块
```

### 取消

`cancel(session_id)`：

- 设置会话取消事件
- 当可用时调用 `agent.interrupt()`
- 导致提示响应返回 `stop_reason="cancelled"`

### 分叉

`fork_session()` 将消息历史深拷贝到新的活动会话中，保留对话状态，同时为分叉赋予自己的会话 ID 和 cwd。

## 提供者/认证行为

ACP 没有实现自己的认证存储。

而是重用 Hermes 的运行时解析器：

- `acp_adapter/auth.py`
- `hermes_cli/runtime_provider.py`

因此 ACP 通告并使用当前配置的 Hermes 提供者/凭证。它还会始终通告终端设置认证方法（`hermes-setup`，参数 `--setup`），以便首次运行的注册中心客户端在启动正常 ACP 会话之前打开 Hermes 的交互式模型/提供者配置。

## 工作目录绑定

ACP 会话携带编辑器的 cwd。

会话管理器通过任务范围内的终端/文件覆盖将该 cwd 绑定到 ACP 会话 ID，因此文件和终端工具相对于编辑器工作空间运行。

## 重复的同名工具调用

事件桥按工具名称使用 FIFO 队列跟踪工具 ID，而不是每个名称仅一个 ID。这很重要，用于：

- 并行的同名调用
- 一个步骤中重复的同名调用

如果没有 FIFO 队列，完成事件会附加到错误的工具调用上。

## 审批回调恢复

ACP 在提示执行期间临时在终端工具上安装一个审批回调，然后在之后恢复之前的回调。这避免将 ACP 会话特定的审批处理程序全局永久保留。

## 当前限制

- ACP 会话持久化到共享的 `~/.hermes/state.db`（SessionDB），并在进程重启后透明恢复；它们出现在 `session_search` 中
- 非文本提示块目前被忽略（用于请求文本提取）
- 编辑器特定的用户体验因 ACP 客户端实现而异

## 相关文件

- `tests/acp/` — ACP 测试套件
- `toolsets.py` — `hermes-acp` 工具集定义
- `hermes_cli/main.py` — `hermes acp` CLI 子命令
- `pyproject.toml` — `[acp]` 可选依赖 + `hermes-acp` 脚本