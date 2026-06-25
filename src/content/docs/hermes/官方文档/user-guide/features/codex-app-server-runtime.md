```yaml
---
title: Codex App-Server 运行时（可选）
sidebar_label: Codex App-Server Runtime
---
```

# Codex App-Server 运行时

Hermes 可以选择将 `openai/*` 和 `openai-codex/*` 的交互交由 [Codex CLI app-server](https://github.com/openai/codex) 处理，而不是运行自己的工具循环。启用后，终端命令、文件编辑、沙箱和 MCP 工具调用全部在 Codex 的运行时内执行——Hermes 成为其外围外壳（会话数据库、斜杠命令、网关、记忆和技能审查）。

这是**选择性加入**的。除非你主动切换标记，否则 Hermes 的默认行为不会改变。Hermes 不会自动将你路由到这个运行时。

:::tip
不使用 OpenAI Codex？`hermes setup --portal` 一步配置非 Codex 的后端（使用 Claude/Gemini 等）。参见 [Nous Portal](/integrations/nous-portal)。
:::

## 为什么

- 使用与 Codex CLI 相同的认证流程，通过你的**ChatGPT 订阅**运行 OpenAI 代理交互（无需 API 密钥）。
- 使用 **Codex 自己的工具集和沙箱**——`shell` 用于终端/读写/搜索，`apply_patch` 用于结构化编辑，`update_plan` 用于规划，全部在 seatbelt/landlock 沙箱内运行。
- **原生 Codex 插件**——Linear、GitHub、Gmail、Calendar、Canva 等——通过 `codex plugin` 安装后，会自动迁移并在你的 Hermes 会话中生效。
- **Hermes 更丰富的工具也一并可用**——web_search、web_extract、浏览器自动化、视觉、图像生成、技能和 TTS 通过 MCP 回调工作。Codex 会回调 Hermes 以获取其内置不包含的工具。
- **记忆和技能提醒继续工作**——Codex 的事件被投射为 Hermes 的常规消息格式，使自我改进循环能读取正常的对话记录。

## 模型实际拥有的工具

这是大多数用户想提前了解的部分。当此运行时启用时，运行你交互的模型拥有三个独立的工具来源：

### 1. Codex 内置工具集（始终开启）

这些随 `codex app-server` 一起提供——无需 Hermes 介入，无需 MCP，无需插件。运行时启动后，以下五种工具即可使用：

- **`shell`**——在沙箱内执行任意 shell 命令。模型通过它读取文件（`cat`、`head`、`tail`）、写入文件（`echo > foo`、heredoc）、搜索文件（`find`、`rg`、`grep`）、导航目录（`ls`、`cd`）、运行构建、管理进程以及任何你会在 bash 中做的事情。
- **`apply_patch`**——以 Codex 的补丁格式应用结构化的多文件差异。模型用于非平凡的代码编辑（添加函数、跨文件重构）；简单的写入仍可使用 shell heredoc。
- **`update_plan`**——Codex 内部的待办/计划追踪器。相当于 Hermes 的 `todo` 工具，但完全在 Codex 运行时内管理。
- **`view_image`**——将本地图片文件载入对话，使模型能够查看。
- **`web_search`**——配置后，Codex 有自己的内置网络搜索。Hermes 也通过下面的回调暴露 `web_search`（基于 Firecrawl）；模型会优先选择自己喜欢的方式。

因此，**任何你通过终端做的事情——读写/搜索/查找/运行——Codex 都能原生完成**。沙箱配置文件（启用运行时后默认为 `:workspace`）控制哪些路径可写入。

### 2. 原生 Codex 插件（从你的 `codex plugin` 安装中自动迁移）

当你启用运行时，Hermes 会查询 Codex 的 `plugin/list` RPC 并为每个已安装的插件写入 `[plugins."<name>@openai-curated"]` 条目。插件本身由 Codex 管理，并仅在 Codex 自己的 UI 中授权一次。

示例（OpenClaw 线程中强调过“YouTube 视频级别的”插件）：

- **Linear**——查找/更新 issue
- **GitHub**——搜索代码、查看 PR、评论
- **Gmail**——读取/发送邮件
- **Google Calendar**——创建/查找事件
- **Outlook calendar/email**——通过 Microsoft 连接器提供类似功能
- **Canva**——设计生成
- ……以及其他通过 `codex plugin marketplace add openai-curated` + `codex plugin install ...` 安装的工具。

**不会被迁移的内容：**
- 你尚未安装的插件——请先在 Codex 中安装。
- ChatGPT 应用市场条目（`app/list`）——这些已经通过你的账户认证在 Codex 中启用。

### 3. Hermes 工具回调（MCP 服务器，注册于 `~/.codex/config.toml`）

Hermes 将自己注册为一个 MCP 服务器，以便 Codex 可以回调已获取其不提供的工具。通过回调可用的工具有：

- **`web_search`** / **`web_extract`**——基于 Firecrawl；对于结构化内容，通常比直接抓取更干净。
- **`browser_navigate` / `browser_click` / `browser_type` / `browser_press` / `browser_snapshot` / `browser_scroll` / `browser_back` / `browser_get_images` / `browser_console` / `browser_vision`**——通过 Camofox 或 Browserbase 实现的完整浏览器自动化。
- **`vision_analyze`**——调用单独的视觉模型检查图片（与 Codex 的 `view_image` 不同，后者将图片载入对话）。
- **`image_generate`**——通过 Hermes 的 image_gen 插件链生成图像。
- **`skill_view` / `skills_list`**——读取 Hermes 的技能库。
- **`text_to_speech`**——通过 Hermes 配置的提供商进行 TTS。

当模型需要这些工具之一时，Codex 会通过 stdio MCP 生成 `hermes_tools_mcp_server` 子进程，调用通过 `model_tools.handle_function_call()` 分发（与 Hermes 默认运行时相同的代码路径），结果像任何其他 MCP 响应一样返回给 Codex。

### 此运行时不可用的工具

以下四种 Hermes 工具需要运行中的 AIAgent 上下文（中间循环状态）来分发，无状态的 MCP 回调无法驱动它们。当你需要这些工具时，请切换回默认运行时（`/codex-runtime auto`）：

- **`delegate_task`**——生成子代理
- **`memory`**——Hermes 的持久记忆存储
- **`session_search`**——跨会话搜索
- **`todo`**——Hermes 的待办存储（Codex 的 `update_plan` 是运行时的等效物）

## 工作流功能（`/goal`、看板、定时任务）

### `/goal`（Ralph 循环）

**此运行时支持。** 目标存储在 `state_meta` 中（以会话 ID 为键），延续提示通过 `run_conversation()` 作为普通用户消息反馈，Codex 原生执行下一步。目标评判通过辅助客户端（在 config.yaml 中由 `auxiliary.goal_judge` 配置）运行，与当前激活的运行时无关。如果 Codex 在批准上停滞，评判的“阻塞，需要用户输入”裁决是一个干净的退出路径。

**需要注意的一点：** 每条延续提示都是一个全新的 Codex 交互，这意味着 Codex 会从头重新评估命令批准策略。如果你正在执行一个包含大量写入的长期目标，预计会比在单个会话任务中看到更多批准提示。设置 `default_permissions = ":workspace"`（启用运行时后 Hermes 会自动设置）以便简单的工作区写入不需要提示。

### 看板（多代理工作树调度）

**此运行时支持，有一个细微的依赖。** 看板调度器将每个工作器生成为一个独立的 `hermes chat -q` 子进程，该进程读取用户配置——这意味着如果全局设置了 `model.openai_runtime: codex_app_server`，工作器也会在 Codex 运行时上启动。

在 Codex 运行时工作器内可用的功能：
- Codex 的完整工具集（shell、apply_patch、update_plan、view_image、web_search）——工作器原生执行实际任务。
- 已迁移的 Codex 插件——Linear、GitHub 等。
- Hermes 工具回调（用于 browser_*、vision、image_gen、skills、TTS）。

因为 MCP 回调暴露了这些工具，所以以下工具也可用：
- **`kanban_complete` / `kanban_block` / `kanban_comment` / `kanban_heartbeat`**——工作器交接工具。它们从环境变量 `HERMES_KANBAN_TASK`（由调度器设置）读取，正确进行门控，并写入由 `HERMES_KANBAN_DB` 指定的每个看板 SQLite 数据库。如果回调中没有这些工具，此运行时上的工作器可以完成任务但无法报告状态，直到调度器超时。
- **`kanban_show` / `kanban_list`**——工作器用于检查自身上下文的只读看板查询。
- **`kanban_create` / `kanban_unblock` / `kanban_link`**——仅编排器操作。对于需要在 Codex 运行时上调度新任务的编排器代理可用。

看板工具由调度器设置的 `HERMES_KANBAN_TASK` 环境变量门控——该变量传播给 Codex 子进程（Codex 继承环境变量），并进一步传播给生成的 `hermes-tools` MCP 服务器子进程。因此工具可以看到正确的任务 ID 并正确进行门控。对于 Codex app-server 工作器，当存在 `HERMES_KANBAN_TASK` 时，Hermes 还会传递窄化的 app-server 沙箱覆盖：保持 `workspace-write` 沙箱，添加**看板数据库目录以及调度器固定的每个看板路径**作为额外的可写根目录（`HERMES_KANBAN_WORKSPACES_ROOT`、`HERMES_KANBAN_WORKSPACE`、旧版 `HERMES_KANBAN_ROOT`——去重后，数据库目录优先），并默认禁用网络。这避免了脆弱的 `:danger-no-sandbox` 变通方法，同时允许 `kanban_complete` / `kanban_block` 更新看板数据库，并允许工作器在数据库目录之外的工作区挂载下编写报告/工件（例如，在单独驱动器上的 `/media/.../kanban-workspaces/...`——[issue #27941](https://github.com/NousResearch/hermes-agent/issues/27941)）。

### 定时任务

**未专门测试。** 定时任务通过 `cronjob` → `AIAgent.run_conversation` 运行，与 CLI 相同的代码路径。如果定时任务的配置中包含 `openai_runtime: codex_app_server`，它将在 Codex 上运行。同样的工具可用性规则适用——Codex 内置工具 + 插件 + MCP 回调有效，代理循环工具（delegate_task、memory、session_search、todo）无效。如果你的定时任务依赖这些工具，请将定时任务范围限定为使用默认运行时的配置文件。

## 权衡

| 特性 | Hermes 默认运行时 | Codex app-server（可选） |
|---|---|---|
| `delegate_task` 子代理 | 是 | 不可用——需要代理循环上下文 |
| `memory`、`session_search`、`todo` | 是 | 不可用——需要代理循环上下文 |
| `web_search`、`web_extract` | 是 | 是（通过 MCP 回调） |
| 浏览器自动化（Camofox/Browserbase） | 是 | 是（通过 MCP 回调） |
| `vision_analyze`、`image_generate` | 是 | 是（通过 MCP 回调） |
| `skill_view`、`skills_list` | 是 | 是（通过 MCP 回调） |
| `text_to_speech` | 是 | 是（通过 MCP 回调） |
| Codex `shell`（终端/读写/搜索/查找/运行） | — | 是（Codex 内置） |
| Codex `apply_patch`（结构化多文件编辑） | — | 是（Codex 内置） |
| Codex `update_plan`（运行时待办） | — | 是（Codex 内置） |
| Codex `view_image`（将图片载入对话） | — | 是（Codex 内置） |
| Codex 沙箱（seatbelt/landlock、配置文件） | — | 是（Codex 内置） |
| ChatGPT 订阅认证 | — | 是（通过 `openai-codex` 提供商） |
| 原生 Codex 插件（Linear、GitHub 等） | — | 是（自动迁移） |
| 用户 MCP 服务器 | 是 | 是（自动迁移到 Codex） |
| 记忆 + 技能审查（后台） | 是 | 是（通过条目投射） |
| 多轮对话 | 是 | 是 |
| `/goal`（Ralph 循环） | 是 | 是 |
| 看板工作器调度 | 是 | 是（通过回调） |
| 看板编排器工具 | 是 | 是（通过回调） |
| 所有网关平台 | 是 | 是 |
| 非 OpenAI 提供商 | 是 | 不适用——限于 OpenAI/Codex |

## 前提条件

1. **安装 Codex CLI：**
   ```bash
   npm i -g @openai/codex
   codex --version   # 0.130.0 或更新版本
   ```
2. **Codex OAuth 登录。** Codex 子进程读取 `~/.codex/auth.json`。两种方法填充它：
   ```bash
   codex login                  # 将令牌写入 ~/.codex/auth.json
   ```
   Hermes 自己的 `hermes auth login codex` 写入 `~/.hermes/auth.json`——那是单独的会话。如果你还没有，**请单独运行 `codex login`**。

3. **（可选）安装你想要的 Codex 插件。** 当你启用运行时，Hermes 会自动迁移你已经通过 Codex CLI 安装的策展插件：
   ```bash
   codex plugin marketplace add openai-curated
   # 然后通过 Codex 的 TUI 安装 Linear / GitHub / Gmail 等
   ```
   Hermes 会自动发现它们，并为它们向 `~/.codex/config.toml` 写入 `[plugins."<name>@openai-curated"]` 条目。

## 启用

在 Hermes 会话中：

```
/codex-runtime codex_app_server
```

该命令将：
- 检查 `codex` CLI 是否已安装（如果未安装，则显示安装提示并阻止）。
- 将 `model.openai_runtime: codex_app_server` 持久化到你的 config.yaml 中。
- 将用户 MCP 服务器从 `~/.hermes/config.yaml` 迁移到 `~/.codex/config.toml`。
- **发现并迁移已安装的原生 Codex 插件**（Linear、GitHub、Gmail、Calendar、Canva 等），通过查询 Codex 的 `plugin/list` RPC。
- **将 Hermes 自己的工具注册为 MCP 服务器**，以便 Codex 子进程可以回调获取其不提供的工具。
- **写入 `default_permissions = ":workspace"`**，使沙箱允许在工作区内写入而无需每次操作都提示。
- 告知你已迁移的内容。在**下一次**会话生效——当前缓存的代理保留先前的运行时，以保持提示缓存有效。

同义词：`/codex-runtime on`、`/codex-runtime off`、`/codex-runtime auto`。

要检查当前状态而不做任何更改：
```
/codex-runtime
```

你也可以在 `~/.hermes/config.yaml` 中手动设置：
```yaml
model:
  openai_runtime: codex_app_server   # 默认是 "auto"（= Hermes 运行时）
```

## 自我改进循环（记忆 + 技能提醒）

Hermes 的后台自我改进在达到计数器阈值时触发：

- 每 10 次用户提示 → 一个分支审查代理查看对话，并决定是否有内容应保存到记忆。
- 每 10 次单轮交互中的工具迭代 → 相同想法，但针对技能（`skill_manage` 写入）。

**两者在 Codex 运行时上继续工作。** Codex 代码路径将每个完成的 `commandExecution` / `fileChange` / `mcpToolCall` / `dynamicToolCall` 条目投射为合成 `assistant tool_call` + `tool` 结果消息，因此当审查运行时，它看到的形状与在默认 Hermes 运行时上相同。

连接保持等效的方式：

|  | 默认运行时 | Codex 运行时 |
|---|---|---|
| `_turns_since_memory` 递增 | 每次用户提示，在 run_conversation 前循环中 | 相同代码路径，在早期返回之前 |
| `_iters_since_skill` 递增 | 在聊天补全循环中每次工具迭代 | 通过 `turn.tool_iterations` 在 Codex 交互返回后 |
| 记忆触发器（`_turns_since_memory >= _memory_nudge_interval`） | 在循环前计算，在响应后触发 | 在循环前计算，传递给 codex 助手 |
| 技能触发器（`_iters_since_skill >= _skill_nudge_interval`） | 在循环后计算 | 在 Codex 交互后计算 |
| `_spawn_background_review(messages_snapshot=..., review_memory=..., review_skills=...)` | 任一触发器触发时调用 | 任一触发器触发时相同方式调用 |

一个细节：审查分支本身需要调用 Hermes 的代理循环工具（`memory`、`skill_manage`），这些工具需要 Hermes 自己的分发。因此，当父代理在 `codex_app_server` 上时，审查分支会被**降级为 `codex_responses`**——相同的 OAuth 凭证、相同的 `openai-codex` 提供商，但直接与 OpenAI 的 Responses API 通信，使 Hermes 拥有循环控制权，代理循环工具也能工作。这对用户是不可见的。

最终效果：启用 Codex 运行时后，你的记忆和技能提醒会像往常一样继续触发。

## 批准如何工作

Codex 在执行命令或应用补丁之前请求批准。这些被转换为 Hermes 标准的“危险命令”提示：

```
╭───────────────────────────────────────╮
│ 危险命令                              │
│                                       │
│ /bin/bash -lc 'echo hello > foo.txt'  │
│                                       │
│ ❯ 1. 允许一次                         │
│   2. 此会话内允许                     │
│   3. 拒绝                             │
│                                       │
│ Codex 请求在 /your/cwd 中执行         │
╰───────────────────────────────────────╯
```

- **允许一次** → 批准此单一命令。
- **此会话内允许** → Codex 不会对类似命令再次提示。
- **拒绝** → 命令被拒绝；Codex 继续以只读模式运行。

对于 `apply_patch`（文件编辑）批准，当 Codex 通过相应的 `fileChange` 条目提供数据时，Hermes 会显示变更摘要（例如 `1 个添加，1 个更新：/tmp/new.py, /tmp/old.py`）。

## 权限配置文件

Codex 有三种内置权限配置文件：
- `:read-only`——禁止写入；每个 shell 命令都需要批准
- `:workspace`——允许在当前工作区内写入而不提示（启用运行时后 Hermes 的默认设置）
- `:danger-no-sandbox`——完全没有沙箱（除非你理解它，否则不要使用）

你可以在 `~/.codex/config.toml` 中 Hermes 管理块之外覆盖默认设置：

```toml
default_permissions = ":read-only"
```

（只要你的覆盖位于 `# managed by hermes-agent` 标记之外，Hermes 在重新迁移时会保留它。）

## 辅助任务与 ChatGPT 订阅令牌消耗

当此运行时与 `openai-codex` 提供商一起启用时，**辅助任务（标题生成、上下文压缩、视觉自动检测、后台自我改进审查分支）默认也会通过你的 ChatGPT 订阅流转**，因为 Hermes 的辅助客户端在没有每个任务覆盖设置的情况下使用主提供商/模型。

这不是 `codex_app_server` 特有的——对于现有的 `codex_responses` 路径也是如此——但在这里更明显，因为你明确选择了订阅计费。

要将特定辅助任务路由到更便宜/不同的模型，在 `~/.hermes/config.yaml` 中设置显式覆盖：

```yaml
auxiliary:
  title_generation:
    provider: openrouter
    model: google/gemini-3-flash-preview
  compression:
    provider: openrouter
    model: google/gemini-3-flash-preview
  vision:
    provider: openrouter
    model: google/gemini-3-flash-preview
  goal_judge:
    provider: openrouter
    model: google/gemini-3-flash-preview
```

自我改进审查分支通过 `_current_main_runtime()` 继承主运行时，Hermes 会自动将其从 `codex_app_server` 降级为 `codex_responses`（这样分支实际上可以调用 `memory` 和 `skill_manage`——Hermes 自己的代理循环工具）。该分支仍然使用你的订阅认证，除非你已将辅助任务路由到其他地方。

## 安全编辑 `~/.codex/config.toml`

Hermes 将其管理的所有内容包裹在两个标记注释之间：

```toml
# managed by hermes-agent — `hermes codex-runtime migrate` regenerates this section
default_permissions = ":workspace"
[mcp_servers.filesystem]
...
[plugins."github@openai-curated"]
...
# end hermes-agent managed section
```

该块**之外**的任何内容都是你的。重新运行迁移（通过 `/codex-runtime codex_app_server` 或切换运行时）会就地替换管理块，但精确保留其上下的用户内容。这意味着你可以：

- 添加 Hermes 不知道的你自己的 MCP 服务器
- 将 `default_permissions` 覆盖为 `:read-only`（如果你希望被提示）
- 配置仅 Codex 的选项（model、providers、otel 等）
- 在 `[permissions.<name>]` 表中添加用户定义的权限配置文件

你在管理块**内部**添加的任何内容将在下次迁移时被覆盖。如果需要对管理块进行编辑，请提交 issue，我们会添加相应开关。

## 多配置文件/多租户设置

默认情况下，无论激活的是哪个 Hermes 配置文件，Hermes 都将 Codex 子进程指向 `~/.codex/`。这意味着 `hermes -p work` 和 `hermes -p personal` 共享相同的 Codex 认证、插件和配置。对于大多数用户来说，这是正确的行为——与直接运行 `codex` CLI 的行为一致。

如果你希望每个配置文件有独立的 Codex 隔离（独立的认证、独立安装的插件、独立配置），请为每个配置文件显式设置 `CODEX_HOME`。最干净的方式是指向 `HERMES_HOME` 下的一个目录：

```bash
# 在 work 配置文件中，你可以包装 hermes：
CODEX_HOME=~/.hermes/profiles/work/codex hermes chat
```

你需要使用该 `CODEX_HOME` 设置重新运行一次 `codex login`，以便 OAuth 令牌落入配置文件作用域的位置。之后，`hermes -p work` 将操作独立的 Codex 状态。

我们不自动限定作用域，因为移动现有用户的 `~/.codex/` 会静默地使他们的 Codex CLI 认证失效——任何已经运行过 `codex login` 的用户都必须重新认证。选择加入感觉比让用户意外更安全。

## HOME 环境变量传递

Hermes 在生成 Codex app-server 子进程时**不会**重写 `HOME`（我们使用 `os.environ.copy()`，只覆盖 `CODEX_HOME` 和 `RUST_LOG`）。这意味着：

- Codex 通过其 `shell` 工具运行的命令会看到真实的用户 `HOME`，并正确找到 `~/.gitconfig`、`~/.gh/`、`~/.aws/`、`~/.npmrc` 等。
- Codex 的内部状态通过 `CODEX_HOME` 保持隔离（默认指向 `~/.codex/`）。

这与 OpenClaw 在早期实验后确定的边界一致：隔离 Codex 的状态，保留用户主目录不变。（参见 openclaw/openclaw#81562。）

## MCP 服务器迁移

Hermes 的 `mcp_servers` 配置会被自动翻译为 Codex 期望的 TOML 格式。每次启用运行时都会运行迁移，且是幂等的——重新运行会替换管理部分，但保留任何用户编辑过的 Codex 配置。

转换规则：

| Hermes（`config.yaml`） | Codex（`config.toml`） |
|---|---|
| `command` + `args` + `env` | stdio 传输 |
| `url` + `headers` | streamable_http 传输 |
| `timeout` | `tool_timeout_sec` |
| `connect_timeout` | `startup_timeout_sec` |
| `enabled: false` | `enabled = false` |

未迁移的内容：
- Hermes 特定的键，如 `sampling`（Codex 的 MCP 客户端没有等效项——这些会被丢弃，并为每个服务器显示警告）。

## 原生 Codex 插件迁移

通过 `codex plugin` 安装的插件（Linear、GitHub、Gmail、Calendar、Canva 等）通过 Codex 的 `plugin/list` RPC 发现。对于每个 `installed: true` 的插件，Hermes 会写入一个 `[plugins."<name>@openai-curated"]` 块，使其在你的 Hermes 会话中启用。

这意味着：当你的朋友说“我在 Codex CLI 中设置了 Calendar 和 GitHub”并启用了 Hermes 的 Codex 运行时，Hermes 会自动激活这些插件。无需重新配置。

**不会被迁移的内容：**
- 你尚未安装的插件——请先在 Codex 中安装。
- Codex 报告 `availability != AVAILABLE` 的插件（安装损坏、OAuth 过期、已从市场移除等）。这些会被跳过，以避免写入会在激活时失败的配置。
- ChatGPT 应用市场条目（每个账户的 `app/list` 结果——这些已经通过你的账户认证在 Codex 中启用）。
- 插件 OAuth——你只需在 Codex 本身中为每个插件授权一次；Hermes 不会接触凭证。

## Hermes 工具回调（新的 MCP 服务器）

Codex 的内置工具集涵盖 shell/文件操作/补丁，但不包括网络搜索、浏览器自动化、视觉、图像生成等。为了在 Codex 交互中保持这些工具可用，Hermes 在 `~/.codex/config.toml` 中将自己注册为 MCP 服务器：

```toml
[mcp_servers.hermes-tools]
command = "/path/to/python"
args = ["-m", "agent.transports.hermes_tools_mcp_server"]
env = { HERMES_HOME = "/your/.hermes", PYTHONPATH = "...", HERMES_QUIET = "1" }
startup_timeout_sec = 30.0
tool_timeout_sec = 600.0
```

当模型调用 `web_search`（或另一个暴露的 Hermes 工具）时，Codex 会通过 stdio 生成 `hermes_tools_mcp_server` 子进程，请求通过 `model_tools.handle_function_call()` 分发，结果像任何其他 MCP 响应一样投射回 Codex。

**通过回调可用的工具：** `web_search`、`web_extract`、`browser_navigate`、`browser_click`、`browser_type`、`browser_press`、`browser_snapshot`、`browser_scroll`、`browser_back`、`browser_get_images`、`browser_console`、`browser_vision`、`vision_analyze`、`image_generate`、`skill_view`、`skills_list`、`text_to_speech`。

**不可用的工具：** `delegate_task`、`memory`、`session_search`、`todo`。这些需要运行中的 AIAgent 上下文（中间循环状态）来分发，无状态的 MCP 回调无法驱动它们。当你需要这些工具时，请使用默认 Hermes 运行时（`/codex-runtime auto`）。

## 禁用

随时切换回来：

```
/codex-runtime auto
```

下一次会话生效。Codex 管理块会保留在 `~/.codex/config.toml` 中，以便你以后可以重新启用而无需丢失配置——如果你愿意，也可以手动删除。

## 局限性

此运行时是**选择性加入的测试版**。在 Hermes Agent 2026.5 + Codex CLI 0.130.0 上工作：

- 多轮对话
- 通过 Hermes UI 批准 `commandExecution` 和 `fileChange`（apply_patch）
- MCP 工具调用（已验证与 `@modelcontextprotocol/server-filesystem` 和新的 `hermes-tools` 回调配合使用）
- 原生 Codex 插件迁移（已验证与 Linear / GitHub / Calendar 清单）
- 拒绝/取消路径
- 切换开/关循环
- 记忆和技能提醒计数器（通过集成测试现场验证）
- Hermes web_search 通过 Codex（现场验证：“OpenAI Codex CLI – Getting Started” 完整返回）

已知局限性：

- **Hermes 认证和 Codex 认证是独立的会话。** 你需要同时有 `codex login` 和 `hermes auth login codex` 以获得最干净的 UX（LLM 调用使用 Codex 的会话）。这是 Hermes 的 `_import_codex_cli_tokens` 中有意的设计选择——Hermes 不会与 Codex CLI 共享 OAuth 状态，以避免在令牌刷新时相互冲突。
- **`delegate_task`、`memory`、`session_search`、`todo` 在此运行时上不可用。** 它们需要运行中的 AIAgent 上下文，无状态的 MCP 回调无法提供。当你需要这些工具时，请使用 `/codex-runtime auto`。
- **当 Codex 不追踪变更集时，批准提示中没有内联补丁预览。** Codex 的 `fileChange` 批准参数并不总是携带变更集。Hermes 会在可能时从相应的 `item/started` 通知中缓存数据，但如果批准在条目流式传输之前到达，提示会回退到 Codex 提供的任何 `reason`。
- **不保证亚秒级取消。** 流中断（在 Codex 响应时 Ctrl+C）通过 `turn/interrupt` 发送，但如果 Codex 已经刷出了最终消息，你仍然会收到响应。

如果你发现 bug，请[提交 issue](https://github.com/NousResearch/hermes-agent/issues)，附带 `hermes logs --since 5m` 的输出。在标题中提及 `codex-runtime` 以便于分类。

## 架构

```
                ┌─── Hermes shell (CLI / TUI / gateway) ───┐
                │  sessions DB · slash commands · memory   │
                │  & skill review · cron · session pickers │
                └──┬──────────────────────────────────────┬┘
                   │ user_message               final     │
                   ▼                            text +    │
        ┌──────────────────────────────────┐   projected  │
        │  AIAgent.run_conversation()       │   messages   │
        │   if api_mode == codex_app_server │              │
        │     → CodexAppServerSession       │              │
        │   else: chat_completions / codex_responses (default)
        └────┬─────────────────────────────┘              │
             │ JSON-RPC over stdio                        │
             ▼                                            │
        ┌──────────────────────────────────┐              │
        │  codex app-server (subprocess)    │──────────────┘
        │   thread/start, turn/start        │
        │   item/* notifications            │
        │   shell + apply_patch + update_plan│
        │   view_image + sandbox            │
        │   ┌─────────────────────────┐     │
        │   │  MCP client             │     │
        │   │  ├─ user MCP servers    │     │
        │   │  ├─ native plugins      │     │
        │   │  │   (linear, github,   │     │
        │   │  │    gmail, calendar,  │     │
        │   │  │    canva, ...)       │     │
        │   │  └─ hermes-tools ───────┼─────────────────┐
        │   │       (callback to     │     │           │
        │   │        Hermes' richer  │     │           │
        │   │        tools)          │     │           │
        │   └─────────────────────────┘     │           │
        └──────────────────────────────────┘           │
                                                        │
                                                        ▼
        ┌──────────────────────────────────────────────────────────┐
        │  hermes_tools_mcp_server.py (subprocess on demand)        │
        │   web_search, web_extract, browser_*, vision_analyze,    │
        │   image_generate, skill_view, skills_list, text_to_speech│
        └──────────────────────────────────────────────────────────┘
```

有关实现细节，请参见 [PR #24182](https://github.com/NousResearch/hermes-agent/pull/24182) 和 [Codex app-server 协议 README](https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md)。