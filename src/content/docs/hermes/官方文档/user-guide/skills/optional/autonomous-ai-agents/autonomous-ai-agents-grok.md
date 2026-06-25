--- frontmatter ---
---
title: "Grok — 将编码任务委托给 xAI Grok Build CLI（功能、PR）"
sidebar_label: "Grok"
description: "将编码任务委托给 xAI Grok Build CLI（功能、PR 审查）"
---

--- body ---
--- body ---
{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非本页面。 */}

# Grok

将编码任务委托给 xAI Grok Build CLI（功能、PR 审查）。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/autonomous-ai-agents/grok` 安装 |
| 路径 | `optional-skills/autonomous-ai-agents/grok` |
| 版本 | `0.1.0` |
| 作者 | Matt Maximo (MattMaximo), Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Coding-Agent`, `Grok`, `xAI`, `Code-Review`, `Refactoring`, `Automation` |
| 相关技能 | [`codex`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex), [`claude-code`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code), [`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) |

## 参考：完整 SKILL.md

:::info
以下是当该技能被触发时 Hermes 加载的完整技能定义。这是技能生效时代理所看到的指令。
:::

# Grok Build CLI — Hermes 编排指南

通过 Hermes 终端将编码任务委托给 [Grok Build](https://docs.x.ai/build/overview)（xAI 的自主编码代理 CLI，即 `grok` 命令）。Grok 可以读取文件、编写代码、运行 shell 命令、生成子代理以及管理 git 工作流。它以三种方式运行：交互式 TUI、**无头模式（headless mode）**（`-p`）以及作为基于 JSON-RPC 的 **ACP 代理**。

这是 `codex` 和 `claude-code` 的第三个兄弟技能。编排模式几乎相同——**对于一次性任务，优先使用无头 `-p` 模式**，对于交互式会话则使用 PTY。

## 何时使用

- 构建功能
- 重构
- PR 审查
- 批量问题修复
- 任何你原本会使用 Codex / Claude Code 但希望使用 Grok 的任务

## 前提条件

- **安装（推荐）：** `npm install -g @xai-official/grok`
  - 官方安装器 `curl -fsSL https://x.ai/cli/install.sh | bash` 也可用，但 `x.ai` 主机在某些环境中受到 Cloudflare 限制。npm 路径完全避免了该依赖。
- **认证 — SuperGrok / X Premium+ 订阅（主要路径）：**
  - 运行 `grok login` 一次 → 打开浏览器进行 OAuth → 令牌缓存在 `~/.grok/auth.json` 中。这将使用你的 **SuperGrok 或 X Premium+** 订阅（无需按令牌 API 计费）。
  - 通过检查 `~/.grok/auth.json` 是否存在或运行一个简单的无头冒烟测试来检查登录状态：`grok --no-auto-update -p "Say ok."`
  - 在 TUI 中，`/logout` 登出，`/login`（或重新启动）重新登录。
- **不需要 git 仓库** — 与 Codex 不同，Grok 在 git 目录外也能正常运行（适用于临时/一次性任务）。
- **与 Claude Code / AGENTS.md 零配置兼容** — Grok 自动读取 `CLAUDE.md`、`.claude/`（技能、代理、MCP、钩子、规则）以及 `AGENTS.md` 家族文件。已有的项目上下文开箱即用。

> **API 密钥回退（非此用户的默认方式）：** Grok 也支持设置 `XAI_API_KEY` 环境变量，通过 `api.x.ai` 按量付费。仅在 `grok login` / SuperGrok 认证不可用时使用此方式。订阅路径（`grok login`）是此处预期的设置方式。

## 两种编排模式

### 模式 1：无头模式（`-p`）— 非交互式（推荐）

运行一次性任务，打印结果并退出。无需 PTY，无需处理交互式对话框。这是最简洁的集成路径——相当于 `claude -p` 和 `codex exec`。

```
terminal(command="grok --no-auto-update -p 'Add a dark mode toggle to settings'", workdir="/path/to/project", timeout=180)
```

在自动化中始终传递 `--no-auto-update` 以跳过后台更新检查。

**何时使用无头模式：**
- 一次性编码任务（修复 bug、添加功能、重构）
- CI/CD 自动化和脚本编写
- 使用 `--output-format json` 的结构化输出解析
- 任何无需多轮对话的任务

### 模式 2：交互式 PTY — 多轮 TUI 会话

TUI 是一个全屏、鼠标交互的应用程序。使用 `pty=true` 驱动它。对于可靠的监控/输入，请使用 tmux（与 `claude-code` 技能相同的模式）。

```
# 在 tmux 会话中启动以进行 capture-pane 监控
terminal(command="tmux new-session -d -s grok-work -x 140 -y 40")
terminal(command="tmux send-keys -t grok-work 'cd /path/to/project && grok' Enter")

# 等待启动，然后发送任务
terminal(command="sleep 5 && tmux send-keys -t grok-work 'Refactor the auth module to use JWT' Enter")

# 监控进度
terminal(command="sleep 15 && tmux capture-pane -t grok-work -p -S -50")

# 完成后退出
terminal(command="tmux send-keys -t grok-work '/quit' Enter && sleep 1 && tmux kill-session -t grok-work")
```

**无头但内联输出的提示：** 如果你希望获得类 TUI 输出但不希望全屏 alt-screen 接管（例如，为了更干净的日志），请添加 `--no-alt-screen`。对于纯自动化，无头 `-p` 模式仍然比 TUI 更简洁。

## 无头模式深入解析

### 常用标志

| 标志 | 效果 |
|------|--------|
| `-p, --single <PROMPT>` | 发送一条提示，无头运行，退出 |
| `-m, --model <MODEL>` | 选择模型 |
| `-s, --session-id <ID>` | 创建或恢复一个命名的无头会话 |
| `-r, --resume <ID>` | 恢复现有会话 |
| `-c, --continue` | 继续当前目录中最近的会话 |
| `--cwd <PATH>` | 设置工作目录 |
| `--output-format <FMT>` | `plain`（默认）、`json` 或 `streaming-json` |
| `--always-approve` | 自动批准所有工具执行（等同于 `--full-auto` / `--yolo`） |
| `--no-alt-screen` | 内联运行，不进行全屏 TUI 接管 |
| `--no-auto-update` | 跳过后台更新检查（在所有自动化中使用） |

### 输出格式

- `plain` — 人类可读的文本（默认）
- `json` — 运行结束时的一个 JSON 对象（可清晰解析结果）
- `streaming-json` — 以换行符分隔的 JSON 事件流

```
# 用于解析的结构化结果
terminal(command="grok --no-auto-update -p 'List all TODO comments in src/' --output-format json", workdir="/project", timeout=120)

# 自动批准用于自主构建
terminal(command="grok --no-auto-update --always-approve -p 'Refactor the database layer and run the tests'", workdir="/project", timeout=300)
```

### 后台模式（长时间任务）

```
# 在后台启动无头模式
terminal(command="grok --no-auto-update --always-approve -p 'Refactor the auth module'", workdir="/project", background=true, notify_on_complete=true)
# 返回 session_id

# 监控
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# 必要时终止
process(action="kill", session_id="<id>")
```

对于交互式（TUI）后台会话，请使用 `pty=true` + tmux 并通过 `tmux capture-pane` 监控，与 `claude-code` / `codex` 技能完全相同。

### 会话延续

```
# 启动一个命名会话
terminal(command="grok --no-auto-update -s refactor-db -p 'Start refactoring the database layer' --always-approve", workdir="/project", timeout=240)

# 稍后恢复
terminal(command="grok --no-auto-update -r refactor-db -p 'Now add connection pooling' --always-approve", workdir="/project", timeout=180)

# 或继续此目录中的最近会话
terminal(command="grok --no-auto-update -c -p 'What did you change last time?'", workdir="/project", timeout=60)
```

## 只读审计 → Markdown 笔记模式

让 Grok 审查本地工件并返回干净的 Markdown 笔记（用于 Obsidian 或仓库）而不修改任何内容：

1. 首先使用 Hermes 工具（`read_file`、`write_file`）准备稳定的输入文件。仅将相关上下文快照到临时文件中，而不是直接使用原始路径。
2. 无头运行 Grok，**不使用** `--always-approve`，使其无法自动写入，并要求输出为 `markdown only, no preamble`。
3. 使用 `write_file()` 将 Grok 的标准输出直接保存到目标笔记中。

```
grok --no-auto-update -p "Read /tmp/current.md and /tmp/inventory.md. Produce markdown only, no preamble. Output a clean note titled 'Cleanup Review'." --output-format plain
```

**陷阱（与 Claude Code 相同）：** 对于文档重写，一个松散的“重写此内容”提示可能会返回更改摘要而不是完整文件。解决方法：通过管道传入文件，并要求 `Return ONLY the full revised markdown document. No intro, no explanation, no code fences. Start immediately with '# Title'.` 在覆盖目标文件之前，使用 `read_file()` 验证前几行。

## PR 审查模式

### 快速审查（无头模式）

```
terminal(command="cd /path/to/repo && git diff main...feature-branch | grok --no-auto-update -p 'Review this diff for bugs, security issues, and style problems. Be thorough.'", timeout=120)
```

### 克隆到临时目录审查（安全，不修改仓库）

```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && grok --no-auto-update -p 'Review the changes vs origin/main. Check bugs, security, race conditions, missing tests.'", pty=true, timeout=300)
```

### 发布审查意见

```
terminal(command="gh pr comment 42 --body '<review text>'", workdir="/path/to/repo")
```

## 使用工作树（Worktrees）并行修复问题

```
# 创建工作树
terminal(command="git worktree add -b fix/issue-78 /tmp/issue-78 main", workdir="~/project")
terminal(command="git worktree add -b fix/issue-99 /tmp/issue-99 main", workdir="~/project")

# 在每个工作树中启动无头 Grok（后台）
terminal(command="grok --no-auto-update --always-approve -p 'Fix issue #78: <description>. Commit when done.'", workdir="/tmp/issue-78", background=true, notify_on_complete=true)
terminal(command="grok --no-auto-update --always-approve -p 'Fix issue #99: <description>. Commit when done.'", workdir="/tmp/issue-99", background=true, notify_on_complete=true)

# 监控
process(action="list")

# 完成后：推送并打开 PR
terminal(command="cd /tmp/issue-78 && git push -u origin fix/issue-78")
terminal(command="gh pr create --repo user/repo --head fix/issue-78 --title 'fix: ...' --body '...'")

# 清理
terminal(command="git worktree remove /tmp/issue-78", workdir="~/project")
```

## 有用的子命令与 TUI 命令

| 命令 | 用途 |
|---------|---------|
| `grok` | 启动交互式 TUI |
| `grok -p "query"` | 无头一次性任务 |
| `grok login` / `grok logout` | 登录/登出（SuperGrok / X Premium+ OAuth） |
| `grok inspect` | 显示 Grok 在当前工作目录中发现的内容：配置源、指令、技能、插件、钩子、MCP 服务器 |
| `grok agent stdio` | 作为基于 JSON-RPC 的 ACP 代理运行（用于 IDE/工具集成） |
| `grok update` | 更新 CLI（需要 `x.ai` 主机；在自动化中跳过） |

TUI 斜杠命令（仅交互式）：`/model <name>`、`/always-approve`、`/plan`、`/context`、`/compact`、`/resume`、`/sessions`、`/fork`、`/usage`、`/quit`。`Shift+Tab` 循环切换会话模式（包括计划模式，该模式会阻止写入工具，但会话计划文件除外）。

## 配置（`~/.grok/config.toml`）

```toml
[cli]
auto_update = false          # 持久跳过后台更新检查

[ui]
permission_mode = "ask"      # 或 "always-approve" 以默认跳过工具提示

[models]
default = "grok-build-0.1"
```

将全局首选项放在 `~/.grok/config.toml` 中（而不是项目范围的 `.grok/config.toml`）。`permission_mode` 取代了旧的 `approval_mode` / `yolo = true` 键。

## 陷阱与注意事项

1. **认证受订阅限制。** `grok login` 需要 SuperGrok 或 X Premium+ 订阅。如果登录失败或没有 `~/.grok/auth.json`，请确认订阅处于活动状态，然后再回退到 `XAI_API_KEY`。
2. **不要将 Hermes 的 xAI 认证与 `grok` CLI 的认证混淆。** Hermes 的 `x_search` 使用自己的 xAI OAuth 运行；独立的 `grok` CLI 在 `~/.grok/auth.json` 中有单独的令牌。一个正常工作的 `x_search` 并不意味着 `grok` 已登录。
3. **在自动化中始终传递 `--no-auto-update`** — 否则 Grok 会尝试更新检查（且 `x.ai`/`storage.googleapis.com` 可能无法访问）。
4. **优先使用 npm 安装而不是 curl 安装器** — `npm install -g @xai-official/grok` 避免了受 Cloudflare 限制的 `x.ai` 主机。
5. **`--always-approve` 是自主构建的开关。** 没有它，无头运行可能会因等待工具批准提示而停滞。仅在需只读审查/审计工作时特意省略它，以便 Grok 无法修改文件。
6. **无头 `-p` 模式跳过 TUI 对话框；** TUI 需要 `pty=true`（+ 用于监控的 tmux），就像 Claude Code 一样。
7. **使用 `--no-alt-screen`** 如果内联运行 TUI 且全屏 alt-screen 接管会干扰捕获的输出。
8. **不需要 git 仓库**，但对于 PR/提交工作流程，你仍然需要一个仓库——对于临时提交任务，请使用 `mktemp -d && git init`。
9. **完成后清理 tmux 会话**，使用 `tmux kill-session -t <name>`。

## Hermes 代理规则

1. **对于单次任务，优先使用无头 `-p` 模式** — 最简洁的集成，通过 `--output-format json` 提供结构化输出。
2. **始终设置 `workdir`**（或 `--cwd`），以便 Grok 定位到正确的项目。
3. **在每次自动调用时传递 `--no-auto-update`**。
4. **仅在 Grok 应自主写入时使用 `--always-approve`**；对于只读审查和审计工作，省略它。
5. **将长时间任务放入后台**，使用 `background=true, notify_on_complete=true` 并通过 `process` 工具监控。
6. **对于多轮交互式工作，使用 tmux** 并通过 `tmux capture-pane -t <session> -p -S -50` 监控。
7. **在使用认证前验证其状态** — 检查 `~/.grok/auth.json` 或运行简单的 `grok -p "Say ok."` 冒烟测试；不要假设 Hermes 的 xAI 认证会延续。
8. **向用户报告结果** — 总结 Grok 更改了哪些内容以及哪些内容未完成。