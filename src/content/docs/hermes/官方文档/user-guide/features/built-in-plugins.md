---
sidebar_position: 12
sidebar_label: "内置插件"
title: "内置插件"
description: "Hermes Agent 随附的插件，通过生命周期钩子自动运行——磁盘清理等"
---

# 内置插件

Hermes 附带了一小组与仓库捆绑的插件。它们位于 `<repo>/plugins/<name>/` 下，并与用户安装的 `~/.hermes/plugins/` 中的插件一起自动加载。它们使用与第三方插件相同的插件接口——钩子（hooks）、工具（tools）、斜杠命令（slash commands），只是代码维护在树内。

请参见[插件](/user-guide/features/plugins)页面了解通用插件系统，以及[构建 Hermes 插件](/guides/build-a-hermes-plugin)来编写你自己的插件。

## 发现机制如何工作

`PluginManager` 按顺序扫描四个来源：

1. **捆绑** — `<repo>/plugins/<name>/`（本文档所述）
2. **用户** — `~/.hermes/plugins/<name>/`
3. **项目** — `./.hermes/plugins/<name>/`（需要 `HERMES_ENABLE_PROJECT_PLUGINS=1`）
4. **Pip 入口点** — `hermes_agent.plugins`

名字冲突时，后扫描的源获胜——一个名为 `disk-cleanup` 的用户插件将替换捆绑的插件。

`plugins/memory/` 和 `plugins/context_engine/` 被有意排除在捆绑扫描之外。这些目录使用自己的发现路径，因为记忆提供者（memory providers）和上下文引擎（context engines）是通过 `hermes memory setup` / 配置中的 `context.engine` 配置的单选提供者。

## 内置插件是选择加入的

内置插件在默认情况下是禁用的。发现机制会找到它们（它们会出现在 `hermes plugins list` 和交互式 `hermes plugins` UI 中），但除非你明确启用，否则不会加载任何插件：

```bash
hermes plugins enable disk-cleanup
```

或者通过 `~/.hermes/config.yaml`：

```yaml
plugins:
  enabled:
    - disk-cleanup
```

这与用户安装的插件使用相同的机制。内置插件永远不会自动启用——无论是全新安装，还是对于升级到更新 Hermes 的现有用户。你总是需要明确选择加入。

要再次关闭内置插件：

```bash
hermes plugins disable disk-cleanup
# 或者：从 config.yaml 的 plugins.enabled 中移除它
```

## 当前随附的插件

仓库在 `plugins/` 下提供了以下捆绑插件。所有插件都是选择加入的——通过 `hermes plugins enable <name>` 启用。

| 插件 | 类型 | 用途 |
|---|---|---|
| `disk-cleanup` | 钩子 + 斜杠命令 | 自动跟踪临时文件并在会话结束时清理 |
| `security-guidance` | 钩子 | 在 `write_file`/`patch` 上模式匹配危险代码并附加安全警告（或阻止）—— 25 条规则（Anthropic 的 `claude-plugins-official` 模式的 Apache-2.0 分支） |
| `observability/langfuse` | 钩子 | 将回合 / LLM 调用 / 工具追踪到 [Langfuse](https://langfuse.com) |
| `observability/nemo_relay` | 钩子 | 将可观测性事件（回合 / LLM 调用 / 工具）中继到 NVIDIA NeMo 端点 |
| `teams_pipeline` | 独立 | Microsoft Teams 会议流程——基于 Graph、以转录为先的会议摘要 |
| `spotify` | 后端（7 个工具） | 原生 Spotify 播放、队列、搜索、播放列表、专辑、库 |
| `google_meet` | 独立 | 加入 Meet 通话、实时字幕转录、可选的实时双工音频 |
| `image_gen/openai` | 图像后端 | OpenAI `gpt-image-2` 图像生成后端（FAL 的替代） |
| `image_gen/openai-codex` | 图像后端 | 通过 Codex OAuth 进行 OpenAI 图像生成 |
| `image_gen/xai` | 图像后端 | xAI `grok-2-image` 后端 |
| `hermes-achievements` | 仪表盘标签页 | 基于你真实的 Hermes 会话历史生成的 Steam 风格可收集徽章 |
| `kanban/dashboard` | 仪表盘标签页 | 用于多代理调度器的看板 UI——任务、评论、扇出、切换面板。请参见[看板多代理](./kanban.md)。 |

记忆提供者（`plugins/memory/*`）和上下文引擎（`plugins/context_engine/*`）分别在[记忆提供者](./memory-providers.md)上列出——它们通过 `hermes memory` 和 `hermes plugins` 分别管理。以下详细介绍两个基于钩子的长期运行插件。

### disk-cleanup

自动跟踪并删除会话期间创建的临时文件——测试脚本、临时输出、cron 日志、过时的 Chrome 配置文件——无需代理记住调用某个工具。

**工作原理：**

| 钩子 | 行为 |
|---|---|
| `post_tool_call` | 当 `write_file` / `terminal` / `patch` 创建一个匹配 `test_*`、`tmp_*` 或 `*.test.*` 的文件，且位于 `HERMES_HOME` 或 `/tmp/hermes-*` 内时，自动将其跟踪为 `test` / `temp` / `cron-output`。 |
| `on_session_end` | 如果在该回合期间自动跟踪了任何测试文件，则运行安全的 `quick` 清理并记录一行摘要。否则保持静默。 |

**删除规则：**

| 类别 | 阈值 | 确认 |
|---|---|---|
| `test` | 每次会话结束时 | 从不 |
| `temp` | 跟踪后超过 7 天 | 从不 |
| `cron-output` | 跟踪后超过 14 天 | 从不 |
| HERMES_HOME 下的空目录 | 始终 | 从不 |
| `research` | 超过 30 天，且最新 10 个之外 | 始终（仅深度清理） |
| `chrome-profile` | 跟踪后超过 14 天 | 始终（仅深度清理） |
| 大于 500 MB 的文件 | 从不自动 | 始终（仅深度清理） |

**斜杠命令** — `/disk-cleanup` 在 CLI 和网关会话中均可用：

```
/disk-cleanup status                     # 分类统计 + 前 10 个大文件
/disk-cleanup dry-run                    # 预览但不删除
/disk-cleanup quick                      # 立即运行安全清理
/disk-cleanup deep                       # 快速清理 + 列出需要确认的项目
/disk-cleanup track <path> <category>    # 手动跟踪
/disk-cleanup forget <path>              # 停止跟踪（不删除文件）
```

**状态** — 所有内容存放在 `$HERMES_HOME/disk-cleanup/`：

| 文件 | 内容 |
|---|---|
| `tracked.json` | 跟踪的路径，包含类别、大小和时间戳 |
| `tracked.json.bak` | 上述文件的原子写入备份 |
| `cleanup.log` | 仅追加的审计日志，记录每次跟踪/跳过/拒绝/删除 |

**安全性** — 清理仅触及 `HERMES_HOME` 或 `/tmp/hermes-*` 下的路径。Windows 挂载点（`/mnt/c/...`）被拒绝。已知的顶级状态目录（`logs/`、`memories/`、`sessions/`、`cron/`、`cache/`、`skills/`、`plugins/`、`disk-cleanup/` 本身）即使为空也永远不会被移除——全新安装不会在第一次会话结束时被掏空。

**启用：** `hermes plugins enable disk-cleanup`（或在 `hermes plugins` 中勾选复选框）。

**再次禁用：** `hermes plugins disable disk-cleanup`。

### security-guidance

对文件写入进行快速模式匹配的安全警告。当代理的 `write_file` / `patch` / `skill_manage` 调用包含与已知危险代码模式匹配的内容时——`pickle.load`、`yaml.load`（无 `SafeLoader`）、`eval(`、`os.system`、`subprocess(..., shell=True)`、JS `child_process.exec`、React `dangerouslySetInnerHTML`、原始 `.innerHTML =` / `.outerHTML =` / `document.write`、Node `crypto.createCipher`、AES ECB 模式、禁用 TLS 验证、易受 XXE 攻击的 `xml.etree` / `minidom` 解析器、无 SRI 的 `<script src="//..." >`、无 `weights_only=True` 的 `torch.load`、GitHub Actions `${{ github.event.* }}` 注入——插件会向工具的结果附加一个 `⚠️ Security guidance` 块。

文件仍会被写入。模型会在下一轮的工具消息中读取该警告，然后可以选择修复代码，或者说明该构造在此上下文中为何安全。模式匹配存在非平凡的误报率，因此默认是警告（而非阻止）。

**覆盖范围：** 共 25 条规则，涵盖不安全的反序列化、命令注入、XSS 汇点、加密陷阱、XXE、供应链（SRI）和 CI/CD 工作流注入。模式数据是 [Anthropic 的 `claude-plugins-official`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/security-guidance/hooks) 的逐字 Apache-2.0 分支——请参见插件的 `LICENSE` 和 `NOTICE` 文件以了解归属声明。

**模式：**

| 环境变量 | 效果 |
|---|---|
| （未设置） | **警告模式**（默认）——文件被写入，警告附加到结果中 |
| `SECURITY_GUIDANCE_BLOCK=1` | **阻止模式**——拒绝写入，警告作为阻止原因返回 |
| `SECURITY_GUIDANCE_DISABLE=1` | 终止开关——插件加载但不做任何事 |

**启用：** `hermes plugins enable security-guidance`（或在 `hermes plugins` 中勾选复选框）。

**再次禁用：** `hermes plugins disable security-guidance`。

**它不做的事情（尚未）：** 上游 Anthropic 插件还有两层——在每次代理修改文件的回合时进行 LLM 差异审查，以及一个代理性的提交时审查，跟踪跨文件的数据流。两者均未移植。代理已经可以通过 `delegate_task` 按需运行这些审查。

### observability/langfuse

将 Hermes 回合、LLM 调用和工具调用追踪到 [Langfuse](https://langfuse.com)——一个开源 LLM 可观测性平台。每个回合一个跨度（span），每次 API 调用一个生成（generation），每次工具调用一个工具观察（tool observation）。使用量总计、按类型划分的 token 计数和成本估算均来自 Hermes 规范的 `agent.usage_pricing` 数字，因此 Langfuse 仪表盘可以看到相同的细分（输入/输出/`cache_read_input_tokens`/`cache_creation_input_tokens`/`reasoning_tokens`），与 `hermes logs` 中显示的一致。

该插件是故障开放的：没有安装 SDK、没有凭据，或者出现短暂的 Langfuse 错误——所有这些都将在钩子中静默地变为无操作。代理循环永远不会受到影响。

**设置（交互式——推荐）：**

```bash
hermes tools          # → Langfuse 可观测性 → 云端或自托管
```

向导会收集你的密钥，`pip install` 安装 `langfuse` SDK，并自动将 `observability/langfuse` 添加到 `plugins.enabled`。重启 Hermes，下一个回合就会发送一个追踪。

**设置（手动）：**

```bash
pip install langfuse
hermes plugins enable observability/langfuse
```

然后将凭据放入 `~/.hermes/.env`：

```bash
HERMES_LANGFUSE_PUBLIC_KEY=pk-lf-...
HERMES_LANGFUSE_SECRET_KEY=sk-lf-...
HERMES_LANGFUSE_BASE_URL=https://cloud.langfuse.com   # 或你的自托管 URL
```

**工作原理：**

| 钩子 | 行为 |
|---|---|
| `pre_api_request` / `pre_llm_call` | 打开（或重用）一个每回合的根跨度 "Hermes turn"。为此 API 调用启动一个 `generation` 子观察，以序列化的最近消息作为输入。 |
| `post_api_request` / `post_llm_call` | 关闭生成，附加 `usage_details`、`cost_details`、`finish_reason`、助手输出和工具调用。如果没有工具调用且内容非空，则关闭该回合。 |
| `pre_tool_call` | 启动一个 `tool` 子观察，带有清理过的 `args`。 |
| `post_tool_call` | 关闭工具观察，带有清理过的 `result`。`read_file` 的有效载荷会被摘要（头部 + 尾部 + 省略的行数），这样大文件读取保持在 `HERMES_LANGFUSE_MAX_CHARS` 以下。 |

会话分组基于 Hermes 会话 ID（或子代理的任务 ID），通过 `langfuse.propagate_attributes` 实现，因此单个 `hermes chat` 会话中的所有内容都位于一个 Langfuse 会话下。

**验证：**

```bash
hermes plugins list                 # observability/langfuse 应显示 "enabled"
hermes chat -q "hello"              # 在 Langfuse UI 中检查是否有一个 "Hermes turn" 追踪
```

**可选调优**（在 `.env` 中）：

| 变量 | 默认值 | 用途 |
|---|---|---|
| `HERMES_LANGFUSE_ENV` | — | 追踪的环境标签（`production`、`staging` 等） |
| `HERMES_LANGFUSE_RELEASE` | — | 发布/版本标签 |
| `HERMES_LANGFUSE_SAMPLE_RATE` | `1.0` | 传递给 SDK 的采样率（0.0–1.0） |
| `HERMES_LANGFUSE_MAX_CHARS` | `12000` | 消息内容/工具参数/工具结果的每个字段截断字符数 |
| `HERMES_LANGFUSE_DEBUG` | `false` | 将详细的插件日志记录到 `agent.log` |

Hermes 前缀和标准 SDK 环境变量（`LANGFUSE_PUBLIC_KEY`、`LANGFUSE_SECRET_KEY`、`LANGFUSE_BASE_URL`）均可接受——两者都设置时，Hermes 前缀优先。

**性能：** Langfuse 客户端在第一次钩子调用后缓存。如果凭据或 SDK 缺失，该决定也会被缓存——后续钩子快速返回，无需重新检查环境变量或重新加载配置。

**禁用：** `hermes plugins disable observability/langfuse`。插件模块仍会被发现，但在你重新启用之前，不会有模块代码运行。

### google_meet

允许代理**加入、转录和参与 Google Meet 通话**——在会议上做笔记、之后总结对话、跟进特定点，以及（可选地）通过 TTS 将回复播报回通话中。

**它添加的内容：**

- 一个无头虚拟参与者，使用浏览器自动化加入 Meet URL
- 通过配置的 STT 提供者对会议音频进行实时转录
- 代理调用的一套工具 `meet_summarize` / `meet_speak` / `meet_followup`，以对其听到的内容采取行动
- 会后工件（转录稿、按发言者标注的笔记、行动项）保存在 `~/.hermes/cache/google_meet/<meeting_id>/` 下

**设置：**

```bash
hermes plugins enable google_meet
# 首次使用时提示您通过插件的 OAuth 流程登录——
# 需要一个具有 Meet 访问权限的 Google 帐户。如果会议强制要求
# "只有受邀参与者才能加入"，则可能需要主持人批准。
```

通过聊天使用：

> "加入 meet.google.com/abc-defg-hij 并做笔记。通话结束后，给我一份包含行动项的摘要。"

代理会启动会议加入，随着通话进行将转录流式传输回其上下文，并在会议结束（或您告诉它停止）时生成结构化的摘要。

**何时使用：** 定期站会，您希望机器人转录并为异步参与者总结；类似证词采访的场景，您希望获得结构化笔记；任何否则您需要 Fireflies / Otter / Grain 的情况。当您不希望 AI 监听时——请不要启用它。

**禁用：** `hermes plugins disable google_meet`。任何缓存的转录稿和录音会保留在 `~/.hermes/cache/google_meet/` 中，直到您删除它们。

### hermes-achievements

在仪表盘中添加一个**Steam 风格成就标签页**——60 多个可收集的分层徽章，基于您真实的 Hermes 会话历史生成。工具链成就、调试模式、代码氛围连续记录、技能/记忆使用、模型/提供者多样性、生活习惯（周末和夜间会话）。最初由 [@PCinkusz](https://github.com/PCinkusz) 作为外部插件编写；集成到树内以与 Hermes 功能变更保持同步。

**工作原理：**

- 在仪表盘后端扫描您的整个 `~/.hermes/state.db` 会话历史
- 每个会话的统计信息通过 `(started_at, last_active)` 指纹缓存，因此只有新的或更改的会话会在后续扫描中重新分析
- 首次扫描在后台线程中运行——仪表盘永远不会等待它，即使在拥有数千个会话的数据库上也是如此
- 解锁状态持久化到 `$HERMES_HOME/plugins/hermes-achievements/state.json`

**等级进度：** 铜 → 银 → 金 → 钻石 → 奥运。每张卡片显示一个 "统计内容" 部分，列出被跟踪的具体指标。

**成就状态：**

| 状态 | 含义 |
|---|---|
| 已解锁 | 至少达到一个等级 |
| 已发现 | 已知成就，可看到进度，尚未获得 |
| 秘密 | 隐藏，直到 Hermes 在您的历史中检测到第一个相关信号 |

**API** — 路由挂载在 `/api/plugins/hermes-achievements/` 下：

| 端点 | 用途 |
|---|---|
| `GET /achievements` | 完整目录，包含每个徽章的解锁状态（在首次冷扫描运行时返回一个待定占位符） |
| `GET /scan-status` | 后台扫描器的状态：`idle` / `running` / `failed`，上次持续时间，运行次数 |
| `GET /recent-unlocks` | 最近解锁的二十个徽章，最新在前 |
| `GET /sessions/{id}/badges` | 主要在某个特定会话中获得的徽章 |
| `POST /rescan` | 手动同步重新扫描（阻塞；当用户点击重新扫描按钮时使用） |
| `POST /reset-state` | 清除解锁历史和缓存的快照 |

**状态文件** — 位于 `$HERMES_HOME/plugins/hermes-achievements/` 下：

| 文件 | 内容 |
|---|---|
| `state.json` | 解锁历史：您获得的徽章及其获得时间。在 Hermes 更新中保持稳定。 |
| `scan_snapshot.json` | 上次完成的扫描有效载荷（在仪表盘加载时立即提供） |
| `scan_checkpoint.json` | 按指纹键缓存的每个会话统计信息（使重新扫描更快） |

**性能说明：**

- 对约 8000 个会话的冷扫描需要几分钟。它在第一个仪表盘请求时在后台线程中运行；UI 会看到一个待定占位符并轮询 `/scan-status`。
- **冷扫描期间的增量结果** — 扫描器每扫描约 250 个会话发布一个部分快照，因此每次仪表盘刷新时都会显示更多已解锁的徽章。不会再盯着零等待几分钟。
- 热重新扫描会重用每个与会话指纹（`started_at` + `last_active`）匹配的会话统计信息——即使在大历史记录上也能在几秒钟内完成。
- 内存中快照的 TTL 为 120 秒；过期的请求会立即提供旧快照，并触发后台刷新。您永远不会因为 TTL 过期而等待旋转图标。

**启用：** 无需启用——`hermes-achievements` 是一个仅仪表盘的插件（没有生命周期钩子，没有模型可见的工具栏）。它在首次启动时自动注册为 `hermes dashboard` 中的标签页。`plugins.enabled` 配置仅控制生命周期/工具栏插件；仪表盘插件纯粹通过其 `dashboard/manifest.json` 被发现。

**选择退出：** 删除或重命名 `plugins/hermes-achievements/dashboard/manifest.json`，或者用 `~/.hermes/plugins/hermes-achievements/` 中同名的用户插件覆盖它，该插件不提供仪表盘。插件的状态文件（位于 `$HERMES_HOME/plugins/hermes-achievements/` 下）会保留——重新安装将保留您的解锁历史。

## 添加内置插件

内置插件的编写方式与任何其他 Hermes 插件完全一样——请参见[构建 Hermes 插件](/guides/build-a-hermes-plugin)。唯一的区别是：

- 目录位于 `<repo>/plugins/<name>/` 而不是 `~/.hermes/plugins/<name>/`
- 清单源在 `hermes plugins list` 中报告为 `bundled`
- 同名的用户插件会覆盖捆绑版本

以下情况的插件适合捆绑：

- 没有可选依赖项（或者已经是 `pip install .[all]` 依赖项）
- 其行为对大多数用户有益，并且是选择退出而非选择加入
- 其逻辑与生命周期钩子相关联，否则代理必须记得调用这些钩子
- 它补充了核心功能，但没有扩展模型可见的工具表面

反例——应保持为用户可安装插件而非内置插件的内容：带有 API 密钥的第三方集成、小众工作流、大型依赖树、任何会显著改变代理默认行为的插件。