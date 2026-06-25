---
sidebar_position: 1
title: "架构"
description: "Hermes Agent 内部结构 — 主要子系统、执行路径、数据流以及后续阅读指南"
---

# 架构

本页是 Hermes Agent 内部结构的总览图。利用此图在代码库中定位自己，然后深入各个子系统的文档了解实现细节。

## 系统概览

```text
┌─────────────────────────────────────────────────────────────────────┐
│                        入口点                                        │
│                                                                      │
│  CLI (cli.py)    Gateway (gateway/run.py)    ACP (acp_adapter/)     │
│  批量运行器      API 服务器                    Python 库              │
└──────────┬──────────────┬───────────────────────┬───────────────────┘
           │              │                       │
           ▼              ▼                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     AIAgent (run_agent.py)                          │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │ Prompt       │  │ Provider     │  │ Tool         │               │
│  │ 构建器       │  │ 解析         │  │ 分发         │               │
│  │ (prompt_     │  │ (runtime_    │  │ (model_      │               │
│  │  builder.py) │  │  provider.py)│  │  tools.py)   │               │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘               │
│         │                 │                 │                       │
│  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐               │
│  │ 压缩与缓存   │  │ 3 种 API 模式 │  │ 工具注册表   │               │
│  │              │  │ chat_compl.  │  │ (registry.py)│               │
│  │              │  │ codex_resp.  │  │ 70+ 工具     │               │
│  │              │  │ anthropic    │  │ 28 工具集    │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└─────────┴─────────────────┴─────────────────┴───────────────────────┘
           │                                    │
           ▼                                    ▼
┌───────────────────┐              ┌──────────────────────┐
│ 会话存储          │              │ 工具后端              │
│ (SQLite + FTS5)   │              │ 终端 (6 种后端)      │
│ hermes_state.py   │              │ 浏览器 (5 种后端)    │
│ gateway/session.py│              │ 网页 (4 种后端)      │
└───────────────────┘              │ MCP (动态)           │
                                   │ 文件、视觉等          │
                                   └──────────────────────┘
```

## 目录结构

```text
hermes-agent/
├── run_agent.py              # AIAgent — 核心对话循环（大文件）
├── cli.py                    # HermesCLI — 交互式终端 UI（大文件）
├── model_tools.py            # 工具发现、模式收集、分发
├── toolsets.py               # 工具分组和平台预设
├── hermes_state.py           # 基于 SQLite 的会话/状态数据库，支持 FTS5
├── hermes_constants.py       # HERMES_HOME、profile 感知路径
├── batch_runner.py           # 批量轨迹生成
│
├── agent/                    # Agent 内部
│   ├── prompt_builder.py     # 系统提示组装
│   ├── context_engine.py     # ContextEngine 抽象基类（可插拔）
│   ├── context_compressor.py # 默认引擎 — 有损摘要
│   ├── prompt_caching.py     # Anthropic 提示缓存
│   ├── auxiliary_client.py   # 辅助 LLM 用于辅助任务（视觉、摘要）
│   ├── model_metadata.py     # 模型上下文长度、token 估算
│   ├── models_dev.py         # models.dev 注册表集成
│   ├── anthropic_adapter.py  # Anthropic Messages API 格式转换
│   ├── display.py            # KawaiiSpinner，工具预览格式化
│   ├── skill_commands.py     # 技能斜杠命令
│   ├── memory_manager.py     # 记忆管理器编排
│   ├── memory_provider.py    # 记忆提供者抽象基类
│   └── trajectory.py         # 轨迹保存辅助工具
│
├── hermes_cli/               # CLI 子命令和设置
│   ├── main.py               # 入口点 — 所有 `hermes` 子命令（大文件）
│   ├── config.py             # DEFAULT_CONFIG、OPTIONAL_ENV_VARS、迁移
│   ├── commands.py           # COMMAND_REGISTRY — 中心斜杠命令定义
│   ├── auth.py               # PROVIDER_REGISTRY、凭据解析
│   ├── runtime_provider.py   # Provider → api_mode + 凭据
│   ├── models.py             # 模型目录、提供者模型列表
│   ├── model_switch.py       # /model 命令逻辑（CLI + gateway 共享）
│   ├── setup.py              # 交互式设置向导（大文件）
│   ├── skin_engine.py        # CLI 主题引擎
│   ├── skills_config.py      # hermes skills — 按平台启用/禁用
│   ├── skills_hub.py         # /skills 斜杠命令
│   ├── tools_config.py       # hermes tools — 按平台启用/禁用
│   ├── plugins.py            # PluginManager — 发现、加载、钩子
│   ├── callbacks.py          # 终端回调（澄清、sudo、审批）
│   └── gateway.py            # hermes gateway 启动/停止
│
├── tools/                    # 工具实现（每个工具一个文件）
│   ├── registry.py           # 中心工具注册表
│   ├── approval.py           # 危险命令检测
│   ├── terminal_tool.py      # 终端编排
│   ├── process_registry.py   # 后台进程管理
│   ├── file_tools.py         # read_file、write_file、patch、search_files
│   ├── web_tools.py          # web_search、web_extract
│   ├── browser_tool.py       # 10 个浏览器自动化工具
│   ├── code_execution_tool.py # execute_code 沙箱
│   ├── delegate_tool.py      # 子代理委托
│   ├── mcp_tool.py           # MCP 客户端（大文件）
│   ├── credential_files.py   # 基于文件的凭据透传
│   ├── env_passthrough.py    # 环境变量透传（用于沙箱）
│   ├── ansi_strip.py         # ANSI 转义序列剥离
│   └── environments/         # 终端后端（local、docker、ssh、modal、daytona、singularity）
│
├── gateway/                  # 消息平台网关
│   ├── run.py                # GatewayRunner — 消息分发（大文件）
│   ├── session.py            # SessionStore — 会话持久化
│   ├── delivery.py           # 出站消息投递
│   ├── pairing.py            # DM 配对授权
│   ├── hooks.py              # 钩子发现和生命周期事件
│   ├── mirror.py             # 跨会话消息镜像
│   ├── status.py             # token 锁、profile 范围进程跟踪
│   ├── builtin_hooks/        # 始终注册的钩子的扩展点（未提供）
│   └── platforms/            # 20 个适配器：telegram、discord、slack、whatsapp、
│                             #   signal、matrix、mattermost、email、sms、
│                             #   dingtalk、feishu、wecom、wecom_callback、weixin、
│                             #   bluebubbles、qqbot、homeassistant、webhook、api_server、
│                             #   yuanbao
│
├── acp_adapter/              # ACP 服务器（VS Code / Zed / JetBrains）
├── cron/                     # 调度器（jobs.py、scheduler.py）
├── plugins/memory/           # 记忆提供者插件
├── plugins/context_engine/   # 上下文引擎插件
├── skills/                   # 捆绑技能（始终可用）
├── optional-skills/          # 官方可选技能（需显式安装）
├── website/                  # Docusaurus 文档站点
└── tests/                    # Pytest 测试套件（约 25,000 个测试，分布在约 1,250 个文件中）
```

## 数据流

### CLI 会话

```text
用户输入 → HermesCLI.process_input()
  → AIAgent.run_conversation()
    → prompt_builder.build_system_prompt()
    → runtime_provider.resolve_runtime_provider()
    → API 调用 (chat_completions / codex_responses / anthropic_messages)
    → tool_calls? → model_tools.handle_function_call() → 循环
    → 最终响应 → 显示 → 保存到 SessionDB
```

### 网关消息

```text
平台事件 → Adapter.on_message() → MessageEvent
  → GatewayRunner._handle_message()
    → 授权用户
    → 解析会话键
    → 使用会话历史创建 AIAgent
    → AIAgent.run_conversation()
    → 通过适配器传递回响应
```

### 定时任务

```text
调度器 tick → 从 jobs.json 加载到期的任务
  → 创建新的 AIAgent（无历史记录）
  → 注入附加的技能作为上下文
  → 执行任务提示
  → 将响应投递到目标平台
  → 更新任务状态和下一次运行时间
```

## 推荐阅读顺序

如果你是代码库新手：

1. **本页** — 定位自己
2. **[Agent 循环内部](./agent-loop.md)** — AIAgent 如何工作
3. **[提示组装](./prompt-assembly.md)** — 系统提示构建
4. **[提供者运行时解析](./provider-runtime.md)** — 如何选择提供者
5. **[添加提供者](./adding-providers.md)** — 添加新提供者的实用指南
6. **[工具运行时](./tools-runtime.md)** — 工具注册表、分发、环境
7. **[会话存储](./session-storage.md)** — SQLite 模式、FTS5、会话谱系
8. **[网关内部](./gateway-internals.md)** — 消息平台网关
9. **[上下文压缩与提示缓存](./context-compression-and-caching.md)** — 压缩和缓存
10. **[ACP 内部](./acp-internals.md)** — IDE 集成

## 主要子系统

### Agent 循环

同步编排引擎（`run_agent.py` 中的 `AIAgent`）。处理提供者选择、提示构建、工具执行、重试、回退、回调、压缩和持久化。支持三种 API 模式以适配不同的提供者后端。

→ [Agent 循环内部](./agent-loop.md)

### 提示系统

对话生命周期中的提示构建和维护：

- **`system_prompt.py` + `prompt_builder.py`** — 组装有序的系统提示层级（`stable` → `context` → `volatile`）：身份/工具指导/技能、上下文文件，然后是记忆/profile/时间戳块
- **`prompt_caching.py`** — 应用 Anthropic 缓存断点实现前缀缓存
- **`context_compressor.py`** — 当上下文超过阈值时压缩中间对话轮次

→ [提示组装](./prompt-assembly.md)，[上下文压缩与提示缓存](./context-compression-and-caching.md)

### 提供者解析

CLI、网关、定时任务、ACP 和辅助调用共享的运行时解析器。将 `(provider, model)` 元组映射到 `(api_mode, api_key, base_url)`。处理 18+ 个提供者、OAuth 流程、凭据池和别名解析。

→ [提供者运行时解析](./provider-runtime.md)

### 工具系统

中心工具注册表（`tools/registry.py`），拥有 70+ 个已注册工具，分布在大约 28 个工具集中。每个工具文件在导入时自行注册。注册表处理模式收集、分发、可用性检查和错误包装。终端工具支持 6 种后端（本地、Docker、SSH、Daytona、Modal、Singularity）。

→ [工具运行时](./tools-runtime.md)

### 会话持久化

基于 SQLite 的会话存储，支持 FTS5 全文搜索。会话具有谱系跟踪（跨压缩的父子关系）、按平台隔离以及带有争用处理的原子写入。

→ [会话存储](./session-storage.md)

### 消息网关

长时间运行的进程，包含 20 个平台适配器、统一会话路由、用户授权（白名单 + DM 配对）、斜杠命令分发、钩子系统、定时任务和后台维护。

→ [网关内部](./gateway-internals.md)

### 插件系统

三个发现源：`~/.hermes/plugins/`（用户）、`.hermes/plugins/`（项目）和 pip 入口点。插件通过上下文 API 注册工具、钩子和 CLI 命令。存在两种专门的插件类型：记忆提供者（`plugins/memory/`）和上下文引擎（`plugins/context_engine/`）。两者都是单选 — 每种类型一次只能激活一个，通过 `hermes plugins` 或 `config.yaml` 配置。

→ [插件指南](/guides/build-a-hermes-plugin)，[记忆提供者插件](./memory-provider-plugin.md)

### 定时任务 (Cron)

一等公民的 agent 任务（而非 shell 任务）。任务存储在 JSON 中，支持多种调度格式，可附加技能和脚本，并投递到任何平台。

→ [定时任务内部](./cron-internals.md)

### ACP 集成

将 Hermes 作为编辑器原生 agent 通过 stdio/JSON-RPC 暴露给 VS Code、Zed 和 JetBrains。

→ [ACP 内部](./acp-internals.md)

### 轨迹

从 agent 会话生成 ShareGPT 格式的轨迹，用于训练数据生成。

→ [轨迹与训练格式](./trajectory-format.md)

## 设计原则

| 原则 | 实际含义 |
|-----------|--------------------------|
| **提示稳定性** | 系统提示在对话中不会改变。除了显式用户操作（`/model`）外，没有破坏缓存的变更。 |
| **可观察执行** | 每个工具调用都通过回调对用户可见。CLI 中显示进度（旋转器），网关中显示聊天消息。 |
| **可中断** | API 调用和工具执行可以通过用户输入或信号在中途取消。 |
| **平台无关核心** | 一个 AIAgent 类服务于 CLI、网关、ACP、批处理和 API 服务器。平台差异位于入口点，而非 agent 内部。 |
| **松散耦合** | 可选子系统（MCP、插件、记忆提供者、RL 环境）使用注册表模式和 check_fn 门控，而非硬依赖。 |
| **Profile 隔离** | 每个 profile（`hermes -p <name>`）拥有自己的 HERMES_HOME、配置、记忆、会话和网关 PID。多个 profile 可并发运行。 |

## 文件依赖链

```text
tools/registry.py  （无依赖 — 被所有工具文件导入）
       ↑
tools/*.py  （每个文件在导入时调用 registry.register()）
       ↑
model_tools.py  （导入 tools/registry + 触发工具发现）
       ↑
run_agent.py、cli.py、batch_runner.py、environments/
```

这意味着工具注册发生在导入时，在任何 agent 实例创建之前。任何包含顶级 `registry.register()` 调用的 `tools/*.py` 文件都会被自动发现 — 无需手动导入列表。