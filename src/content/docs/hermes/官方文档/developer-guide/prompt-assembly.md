--- frontmatter ---
---
sidebar_position: 5
title: "提示组装（Prompt Assembly）"
description: "Hermes 如何构建系统提示（system prompt）、保持缓存稳定性以及注入临时层（ephemeral layers）"
---

--- body ---
# 提示组装（Prompt Assembly）

Hermes 有意识地将以下内容分开：

- **缓存的系统提示状态（cached system prompt state）**
- **临时的 API 调用时添加项（ephemeral API-call-time additions）**

这是项目中最关键的设计决策之一，因为它会影响：

- token 使用量
- 提示缓存（prompt caching）效率
- 会话连续性（session continuity）
- 记忆正确性（memory correctness）

主要文件：

- `run_agent.py`
- `agent/prompt_builder.py`
- `tools/memory_tool.py`

## 缓存的系统提示层（Cached system prompt layers）

缓存的系统提示按三个有序层级组装（参见 `agent/system_prompt.py`）：

1. **稳定层（stable）** — 身份（`SOUL.md` 或后备）、工具/模型指导、技能（skills）提示、环境提示、平台提示
2. **上下文层（context）** — 调用者提供的 `system_message` 加上项目上下文文件（`.hermes.md` / `AGENTS.md` / `CLAUDE.md` / `.cursorrules`）
3. **易变层（volatile）** — 内置记忆快照（`MEMORY.md`）、用户档案快照（`USER.md`）、外部记忆提供者块、时间戳/会话/模型/提供者行

最终的 system prompt 按以下顺序拼接：`stable` → `context` → `volatile`。

此顺序在优先级讨论中具有重要意义：
- 技能（skills）属于**稳定层**
- 记忆/档案快照属于**易变层**
- 两者仍位于缓存的 system prompt 中（它们不会被作为临时中间转叠加注入）

当设置 `skip_context_files` 时（例如子代理委托），不会加载 `SOUL.md`，而是使用硬编码的 `DEFAULT_AGENT_IDENTITY`。

### 具体示例：组装后的 system prompt

以下是所有层都存在时最终 system prompt 的简化视图（注释显示各部分的来源）：

```
# 第1层：代理身份（来自 ~/.hermes/SOUL.md）
你是一个名为 Hermes 的 AI 助手，由 Nous Research 创建。
你是一名专业软件工程师和研究员。
你重视正确性、清晰度和效率。
...

# 第2层：工具感知行为指导
你在多个会话中拥有持久记忆。请使用记忆工具保存持久性事实：
用户偏好、环境细节、工具特性以及稳定的约定。
记忆会被注入每一轮对话中，因此请保持简洁，专注于以后仍然重要的事实。
...
当用户引用过去对话中的内容，或者你怀疑存在相关的跨会话上下文时，
请先使用 session_search 回忆，而不是让用户重复。

# 工具使用强制（仅适用于 GPT/Codex 模型）
你必须使用工具来采取行动——不要仅仅描述你会做什么或计划做什么而不实际执行。
...

# 第3层：Honcho 静态块（当活动时）
[Honcho 个性/上下文数据]

# 第4层：可选的系统消息（来自配置或 API）
[用户配置的系统消息覆盖]

# 第5层：冻结的 MEMORY 快照
## 持久记忆
- 用户偏好 Python 3.12，使用 pyproject.toml
- 默认编辑器为 nvim
- 正在处理项目 "atlas"，位于 ~/code/atlas
- 时区：US/Pacific

# 第6层：冻结的 USER 档案快照
## 用户档案
- 姓名：Alice
- GitHub：alice-dev

# 第7层：技能索引
## 技能（必备）
在回复之前，扫描以下技能。如果其中一项明确匹配你的任务，
请使用 skill_view(name) 加载它并遵循其指示。
...
<available_skills>
  software-development:
    - code-review: 结构化代码审查工作流
    - test-driven-development: TDD 方法论
  research:
    - arxiv: 搜索并总结 arXiv 论文
</available_skills>

# 第8层：上下文文件（来自项目目录）
# 项目上下文
已加载以下项目上下文文件，应遵循：

## AGENTS.md
这是 atlas 项目。请使用 pytest 进行测试。主入口点为
src/atlas/main.py。在提交前务必运行 `make lint`。

# 第9层：时间戳 + 会话
当前时间：2026-03-30T14:30:00-07:00
会话：abc123

# 第10层：平台提示
你是一个 CLI AI 代理。尽量不使用 markdown，而是使用简单的文本渲染，
以便在终端内显示。
```

## 自定义平台提示

平台提示（上述第10层）是 Hermes 为 Telegram、WhatsApp、Slack、CLI 及其他平台注入的每层面指导——例如“你处于终端环境中，避免使用 Markdown”。内置默认值位于 `PLATFORM_HINTS`（`agent/system_prompt.py`）；插件提供的平台通过平台注册表提供其提示。

管理员可以通过 `config.yaml` 中的顶层 `platform_hints` 键，在不影响其他平台的情况下，为单个平台追加或替换提示：

```yaml
platform_hints:
  whatsapp:
    append: >
      当需要表格输出时，调用 table_formatting 技能，而不是发出 Markdown 表格。
  slack:
    replace: "你处于 Slack 中。保持回复紧凑，避免宽表格。"
  telegram: "偏好简短消息；拆分长回复。"   # 简写形式 = append
```

- `append` — 保留内置提示，并在其后添加额外文本。
- `replace` — 完全替换内置提示。
- 纯字符串 — `append` 的简写形式。
- 当同时存在 `replace` 和 `append` 时，`replace` 优先。
- 格式错误的条目会被防御性地忽略，并回退到未修改的默认值，因此错误的配置值永远不会破坏提示组装或泄露到其他平台。

覆盖值在构建 system prompt 时（会话开始时，以及压缩时因为会重建提示）解析。对于固定配置，它会生成一个字节稳定的提示，因此它位于**稳定层**中，与内置提示一起，不会破坏提示缓存——它不是会话中对冻结提示的实时更改。

## SOUL.md 如何在提示中显示

`SOUL.md` 位于 `~/.hermes/SOUL.md`，用作代理的身份标识——system prompt 的第一部分。`prompt_builder.py` 中的加载逻辑如下：

```python
# 来自 agent/prompt_builder.py（简化版）
def load_soul_md() -> Optional[str]:
    soul_path = get_hermes_home() / "SOUL.md"
    if not soul_path.exists():
        return None
    content = soul_path.read_text(encoding="utf-8").strip()
    content = _scan_context_content(content, "SOUL.md")  # 安全扫描
    content = _truncate_content(content, "SOUL.md")       # 上限默认为 20000 字符，可配置
    return content
```

当 `load_soul_md()` 返回内容时，它会替换硬编码的 `DEFAULT_AGENT_IDENTITY`。然后调用 `build_context_files_prompt()` 并传入 `skip_soul=True`，以防止 `SOUL.md` 出现两次（一次作为身份，一次作为上下文文件）。

如果 `SOUL.md` 不存在，系统会回退到：

```
You are Hermes Agent, an intelligent AI assistant created by Nous Research.
You are helpful, knowledgeable, and direct. You assist users with a wide
range of tasks including answering questions, writing and editing code,
analyzing information, creative work, and executing actions via your tools.
You communicate clearly, admit uncertainty when appropriate, and prioritize
being genuinely useful over being verbose unless otherwise directed below.
Be targeted and efficient in your exploration and investigations.
```

## 上下文文件如何注入

`build_context_files_prompt()` 使用**优先级系统**——只加载一种项目上下文类型（第一个匹配者获胜）：

```python
# 来自 agent/prompt_builder.py（简化版）
def build_context_files_prompt(cwd=None, skip_soul=False):
    cwd_path = Path(cwd).resolve()

    # 优先级：第一个匹配者获胜——只加载一个项目上下文
    project_context = (
        _load_hermes_md(cwd_path)       # 1. .hermes.md / HERMES.md（遍历到 git 根目录）
        or _load_agents_md(cwd_path)    # 2. AGENTS.md（仅当前工作目录）
        or _load_claude_md(cwd_path)    # 3. CLAUDE.md（仅当前工作目录）
        or _load_cursorrules(cwd_path)  # 4. .cursorrules / .cursor/rules/*.mdc
    )

    sections = []
    if project_context:
        sections.append(project_context)

    # 来自 HERMES_HOME 的 SOUL.md（独立于项目上下文）
    if not skip_soul:
        soul_content = load_soul_md()
        if soul_content:
            sections.append(soul_content)

    if not sections:
        return ""

    return (
        "# Project Context\n\n"
        "The following project context files have been loaded "
        "and should be followed:\n\n"
        + "\n".join(sections)
    )
```

### 上下文文件发现细节

| 优先级 | 文件 | 搜索范围 | 说明 |
|----------|-------|-------------|-------|
| 1 | `.hermes.md`, `HERMES.md` | 从当前工作目录到 git 根目录 | Hermes 原生项目配置 |
| 2 | `AGENTS.md` | 仅当前工作目录 | 通用代理指令文件 |
| 3 | `CLAUDE.md` | 仅当前工作目录 | Claude Code 兼容性 |
| 4 | `.cursorrules`, `.cursor/rules/*.mdc` | 仅当前工作目录 | Cursor 兼容性 |

所有上下文文件都会：
- **安全扫描** — 检查提示注入模式（不可见 Unicode、"忽略之前的指令"、凭据窃取尝试）
- **截断** — 限制为 `context_file_max_chars` 字符（默认 20000），使用 70/20 头部/尾部比例，并带有截断标记
- **移除 YAML frontmatter** — `.hermes.md` 的 frontmatter 会被移除（保留用于将来的配置覆盖）

## 仅 API 调用时层（API-call-time-only layers）

以下内容故意**不**持久化为缓存的 system prompt 的一部分：

- `ephemeral_system_prompt`
- 预填充（prefill）消息
- 网关派生的会话上下文叠加
- 后续轮次的 Honcho/外部召回，注入到当前轮次的用户消息中

`pre_llm_call` 插件上下文也位于此 API 调用时路径中：它被附加到当前轮次的**用户消息**中，而不是写入缓存的 system prompt。当多个插件返回上下文时，Hermes 会连接这些上下文块（参见 [Hooks → `pre_llm_call`](../user-guide/features/hooks.md#pre_llm_call)）。

这种分离确保了稳定前缀对于缓存保持稳定。

## 记忆快照（Memory snapshots）

本地记忆和用户档案数据被捕获到 system prompt 的**易变层**中。会话中的写入会更新磁盘状态，但不会更改已构建的缓存 system prompt，直到触发重建路径（新会话或显式的无效/重建流程，如压缩触发的重建）。

## 上下文文件

`agent/prompt_builder.py` 使用**优先级系统**扫描并清理项目上下文文件——只加载一种类型（第一个匹配者获胜）：

1. `.hermes.md` / `HERMES.md`（遍历到 git 根目录）
2. `AGENTS.md`（启动时的当前工作目录；在会话期间通过 `agent/subdirectory_hints.py` 逐步发现子目录）
3. `CLAUDE.md`（仅当前工作目录）
4. `.cursorrules` / `.cursor/rules/*.mdc`（仅当前工作目录）

`SOUL.md` 通过 `load_soul_md()` 单独加载用于身份插槽。当成功加载时，`build_context_files_prompt(skip_soul=True)` 防止它出现两次。

长文件在注入前会被截断。

## 技能索引（Skills index）

当技能工具可用时，技能系统会向提示中贡献一个紧凑的技能索引。

## 支持的提示自定义表面（Supported prompt customization surfaces）

大多数用户应将 `agent/prompt_builder.py` 视为实现代码，而不是配置表面。支持的自定义路径是更改 Hermes 已加载的提示输入，而不是原地编辑 Python 模板。

### 优先使用这些表面

- `~/.hermes/SOUL.md` — 将内置的默认身份块替换为你自己的代理角色和常态行为。
- `~/.hermes/MEMORY.md` 和 `~/.hermes/USER.md` — 提供持久性的跨会话事实和用户档案数据，这些数据会被快照到新会话中。
- 项目上下文文件，如 `.hermes.md`、`HERMES.md`、`AGENTS.md`、`CLAUDE.md` 或 `.cursorrules` — 注入仓库特定的工作规则。
- 技能（skills） — 打包可重用的工作流和参考资料，无需编辑核心提示代码。
- 可选的系统提示配置 / API 覆盖 — 添加部署特定的指令文本，而无需分叉 Hermes。
- 临时覆盖层，如 `HERMES_EPHEMERAL_SYSTEM_PROMPT` 或预填充消息 — 添加轮次范围的指导，不应成为缓存提示前缀的一部分。

### 何时改为编辑代码

仅当你故意维护一个分支或向上游贡献行为变更时，才编辑 `agent/prompt_builder.py`。该文件为每个会话组装提示管道、缓存边界和注入顺序。直接在此处编辑是全局产品变更，而非针对用户的提示自定义。

换句话说：

- 如果你想要不同的助手身份，编辑 `SOUL.md`
- 如果你想要不同的仓库规则，编辑项目上下文文件
- 如果你想要可重用的操作流程，添加或修改技能
- 如果你想要改变 Hermes 为所有人组装提示的方式，更改 Python 并将其视为代码贡献

## 为什么提示要这样拆分

该架构有意优化了：

- 保留提供者端的提示缓存
- 避免不必要地修改历史记录
- 使记忆语义易于理解
- 让网关/ACP/CLI 添加上下文而不污染持久提示状态

## 相关文档

- [上下文压缩与提示缓存（Context Compression & Prompt Caching）](./context-compression-and-caching.md)
- [会话存储（Session Storage）](./session-storage.md)
- [网关内部原理（Gateway Internals）](./gateway-internals.md)