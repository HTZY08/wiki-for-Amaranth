---
description: Hermes如何检测和响应原生JS对话框，并通过持久化的CDP连接与跨源iframe交互。
sidebar_position: 18
title: 浏览器CDP监管器 (Browser CDP Supervisor)
---

# 浏览器CDP监管器

CDP监管器填补了Hermes浏览器工具中长期存在的两个空白：

1. **原生JS对话框**（`alert`/`confirm`/`prompt`/`beforeunload`）会阻塞页面的JS线程。若无监管，代理（Agent）无法知道对话框已打开——后续工具调用会挂起或抛出含义不明的错误。
2. **跨源iframe（OOPIF）** 对顶层 `Runtime.evaluate` 不可见。代理可以在DOM快照中看到iframe节点，但如果没有附加到子目标的CDP会话，则无法在iframe内点击、输入或执行eval。

监管器通过为每个浏览器任务持有一个到后端CDP端点的持久WebSocket来解决这两个问题，将待处理的对话框和框架结构呈现到 `browser_snapshot` 中，并提供一个用于显式响应的 `browser_dialog` 工具。

## 后端支持

| 后端 | 对话框检测 | 对话框响应 | 框架树 | 通过 `browser_cdp(frame_id=...)` 的OOPIF `Runtime.evaluate` |
|---|---|---|---|---|
| 本地Chrome（`--remote-debugging-port`）/ `/browser connect` | ✓ | ✓ 完整工作流 | ✓ | ✓ |
| Browserbase | ✓（通过桥接） | ✓ 完整工作流（通过桥接） | ✓ | ✓ |
| Camofox | ✗ 无CDP（仅REST） | ✗ | 通过DOM快照部分支持 | ✗ |

**Browserbase 特性。** Browserbase 的CDP代理内部使用Playwright，会在约10ms内自动关闭原生对话框，因此 `Page.handleJavaScriptDialog` 无法跟上。监管器通过 `Page.addScriptToEvaluateOnNewDocument` 注入一个桥接脚本，将 `window.alert`/`confirm`/`prompt` 重写为对魔术主机（`hermes-dialog-bridge.invalid`）的同步XHR请求。`Fetch.enable` 在这些XHR到达网络之前拦截它们——对话框变为监管器捕获的 `Fetch.requestPaused` 事件，而 `respond_to_dialog` 通过 `Fetch.fulfillRequest` 响应一个JSON主体，该主体由注入的脚本解码。

从页面的角度看，`prompt()` 仍然返回代理提供的字符串。从代理的角度看，无论哪种方式，都是同一个 `browser_dialog(action=...)` API。

Camofox 不受支持——无CDP表面，仅REST。

## 架构

### CDP监管器 (CDPSupervisor)

每个 Hermes `task_id` 对应一个运行在后台守护线程中的 `asyncio.Task`。持有一个到后端CDP端点的持久WebSocket。维护：

- **对话框队列（Dialog queue）** — `List[PendingDialog]` 包含 `{id, type, message, default_prompt, session_id, opened_at}`
- **框架树（Frame tree）** — `Dict[frame_id, FrameInfo]` 包含父级关系、URL、源（origin）、是否为跨源子会话
- **会话映射（Session map）** — `Dict[session_id, SessionInfo]`，以便交互工具可以路由到正确的附加会话以进行OOPIF操作
- **近期控制台错误** — 最近50条错误环形缓冲区，用于诊断

附加时订阅：

- `Page.enable` — `javascriptDialogOpening`、`frameAttached`、`frameNavigated`、`frameDetached`
- `Runtime.enable` — `executionContextCreated`、`consoleAPICalled`、`exceptionThrown`
- `Target.setAutoAttach {autoAttach: true, flatten: true}` — 暴露子OOPIF目标；监管器在每个子目标上启用 `Page`+`Runtime`

通过快照锁实现线程安全的状态访问；工具处理程序（同步）读取冻结的快照而无需等待。

### 生命周期

- **启动：** `SupervisorRegistry.get_or_start(task_id, cdp_url)` — 由 `browser_navigate`、Browserbase会话创建、`/browser connect` 调用。幂等。
- **停止：** 会话拆除或 `/browser disconnect`。取消asyncio任务，关闭WebSocket，丢弃状态。
- **重新绑定：** 如果CDP URL发生变化（用户重新连接到新的Chrome），旧监管器停止，启动新监管器——状态不会跨端点重用。

### 对话框策略

可通过 `config.yaml` 在 `browser.dialog_policy` 下配置：

- **`must_respond`**（默认）— 捕获，在 `browser_snapshot` 中呈现，等待显式 `browser_dialog(action=...)` 调用。如果没有响应，则在300s安全超时后自动关闭并记录日志。防止有缺陷的代理无限期停滞。
- `auto_dismiss` — 记录并立即关闭；代理事后通过 `browser_snapshot` 中的 `browser_state` 查看。
- `auto_accept` — 记录并接受（适用于 `beforeunload`，工作流希望干净地导航离开）。

策略按任务设定；没有按对话框的重写。

## 代理接口

### `browser_dialog` 工具

```
browser_dialog(action, prompt_text=None, dialog_id=None)
```

- `action="accept"` / `"dismiss"` → 响应指定或唯一的待处理对话框（必需）
- `prompt_text=...` → 提供给 `prompt()` 对话框的文本
- `dialog_id=...` → 当多个对话框排队时用于区分（很少见）

该工具仅用于响应。代理在调用之前从 `browser_snapshot` 输出中读取待处理对话框。

### `browser_snapshot` 扩展

当监管器附加时，向现有快照输出添加三个可选字段：

```json
{
  "pending_dialogs": [
    {"id": "d-1", "type": "alert", "message": "Hello", "opened_at": 1650000000.0}
  ],
  "recent_dialogs": [
    {"id": "d-1", "type": "alert", "message": "...", "opened_at": 1650000000.0,
     "closed_at": 1650000000.1, "closed_by": "remote"}
  ],
  "frame_tree": {
    "top": {"frame_id": "FRAME_A", "url": "https://example.com/", "origin": "https://example.com"},
    "children": [
      {"frame_id": "FRAME_B", "url": "about:srcdoc", "is_oopif": false},
      {"frame_id": "FRAME_C", "url": "https://ads.example.net/", "is_oopif": true, "session_id": "SID_C"}
    ],
    "truncated": false
  }
}
```

- **`pending_dialogs`** — 当前阻塞页面JS线程的对话框。代理必须调用 `browser_dialog(action=...)` 来响应。在Browserbase上为空，因为它们的CDP代理会在约10ms内自动关闭。
- **`recent_dialogs`** — 最多20个最近关闭的对话框环形缓冲区，带有 `closed_by` 标签：`"agent"`（我们响应了）、`"auto_policy"`（本地auto_dismiss/auto_accept）、`"watchdog"`（must_respond超时触发）、或 `"remote"`（浏览器/后端关闭了它，例如Browserbase）。这是Browserbase上的代理仍然能查看发生了什么的方式。
- **`frame_tree`** — 框架结构，包括跨源（OOPIF）子框架。限制为30个条目 + OOPIF深度2，以限制广告繁重页面上的快照大小。`truncated: true` 表示达到了限制；需要完整树的代理可以使用 `browser_cdp` 并调用 `Page.getFrameTree`。

这些字段没有新的工具模式接口——代理读取它已经请求的快照。

### 可用性门控

两个接口都通过 `_browser_cdp_check` 门控（监管器仅在CDP端点可到达时运行）。在Camofox/无后端会话上，对话框工具隐藏，快照省略新字段——不会导致模式膨胀。

## 跨源iframe交互

`browser_cdp(frame_id=...)` 通过监管器已连接的WebSocket，使用OOPIF的子 `sessionId` 路由CDP调用（特别是 `Runtime.evaluate`）。代理从 `browser_snapshot.frame_tree.children[]` 中选取 `is_oopif=true` 的frame_id，然后将其传递给 `browser_cdp`。对于同源iframe（没有专用CDP会话），代理改用顶层 `Runtime.evaluate` 中的 `contentWindow`/`contentDocument`——当 `frame_id` 属于非OOPIF时，监管器会抛出指向该回退的错误。

在Browserbase上，这是iframe交互的唯一可靠路径——无状态CDP连接（每次 `browser_cdp` 调用打开）会遇到签名URL过期，而监管器的长连接保持有效会话。

## 文件布局

- `tools/browser_supervisor.py` — `CDPSupervisor`、`SupervisorRegistry`、`PendingDialog`、`FrameInfo`
- `tools/browser_dialog_tool.py` — `browser_dialog` 工具处理程序
- `tools/browser_tool.py` — `browser_navigate` 启动钩子、`browser_snapshot` 合并、`/browser connect` 重新附加、`_cleanup_browser_session` 拆除
- `toolsets.py` — 在 `browser`、`hermes-acp`、`hermes-api-server` 和核心工具集中注册 `browser_dialog`（门控于CDP可到达性）
- `hermes_cli/config.py` — `browser.dialog_policy` 和 `browser.dialog_timeout_s` 默认值

## 非目标

- 对Camofox的检测/交互（上游差距；单独跟踪）
- 将对话框/框架事件实时流式传输给用户（需要网关钩子）
- 跨会话持久化对话框历史（仅内存）
- 每个iframe的对话框策略（代理可以通过 `dialog_id` 表达）
- 替换 `browser_cdp`——它仍然作为长尾场景（cookie、视口、网络节流）的逃生舱口

## 测试

单元测试（`tests/tools/test_browser_supervisor.py`）使用一个asyncio模拟CDP服务器，该服务器实现了足够的协议以执行所有状态转换：附加、启用、导航、对话框触发、对话框关闭、框架附加/分离、子目标附加、会话拆除。真实后端端到端测试（Browserbase + 本地Chromium系列浏览器）是手动的——通过 `/browser connect` 连接到运行的Chromium系列浏览器，并执行上述对话框/框架测试用例。
```