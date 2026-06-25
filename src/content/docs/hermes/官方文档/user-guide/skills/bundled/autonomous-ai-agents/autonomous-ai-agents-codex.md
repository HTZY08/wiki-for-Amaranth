--- frontmatter ---
---
title: "Codex — 将编码委托给 OpenAI Codex CLI（功能、PR）"
sidebar_label: "Codex"
description: "将编码委托给 OpenAI Codex CLI（功能、PR）"
---

--- body ---
{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Codex

将编码委托给 OpenAI Codex CLI（功能、PR）。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/autonomous-ai-agents/codex` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Coding-Agent`, `Codex`, `OpenAI`, `Code-Review`, `Refactoring` |
| 相关技能 | [`claude-code`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code), [`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) |

## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时代理（Agent）看到的指令。
:::

# Codex CLI

通过 Hermes 终端将编码任务委托给 [Codex](https://github.com/openai/codex)。Codex 是 OpenAI 的自主编码代理 CLI。

## 何时使用

- 构建功能
- 重构
- PR 审查
- 批量问题修复

需要安装 codex CLI 并拥有一个 git 仓库。

## 前提条件

- 已安装 Codex：`npm install -g @openai/codex`
- 配置了 OpenAI 认证：`OPENAI_API_KEY` 或通过 Codex CLI 登录流程获得的 Codex OAuth 凭据
- **必须在 git 仓库内运行** — Codex 拒绝在非 git 目录外运行
- 在终端调用中使用 `pty=true` — Codex 是一个交互式终端应用

对于 Hermes 自身，使用 `model.provider: openai-codex` 会利用 `~/.hermes/auth.json` 中由 `hermes auth add openai-codex` 管理的 Hermes 托管 Codex OAuth。对于独立的 Codex CLI，有效的 CLI OAuth 会话可能位于 `~/.codex/auth.json`；不要仅因缺少 `OPENAI_API_KEY` 就断定 Codex 认证缺失。

## 一次性任务

```
terminal(command="codex exec 'Add dark mode toggle to settings'", workdir="~/project", pty=true)
```

用于临时工作（Codex 需要 git 仓库）：
```
terminal(command="cd $(mktemp -d) && git init && codex exec 'Build a snake game in Python'", pty=true)
```

## 后台模式（长时间任务）

```
# 在后台启动，使用 PTY
terminal(command="codex exec --full-auto 'Refactor the auth module'", workdir="~/project", background=true, pty=true)
# 返回 session_id

# 监控进度
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# 如果 Codex 提出问题，发送输入
process(action="submit", session_id="<id>", data="yes")

# 如果需要，终止
process(action="kill", session_id="<id>")
```

## 关键标志

| 标志 | 效果 |
|------|--------|
| `exec "prompt"` | 一次性执行，完成后退出 |
| `--full-auto` | 沙盒模式，但自动批准工作区中的文件更改 |
| `--yolo` | 无沙盒，无批准（最快，最危险） |
| `--sandbox danger-full-access` | 无 Codex 沙盒；当宿主服务上下文破坏 bubblewrap 时有用 |

## Hermes 网关注意事项

当从 Hermes 网关/服务上下文（例如 Telegram 驱动的代理会话）调用 Codex CLI 时，即使相同的命令在用户交互式 shell 中正常工作，Codex 的 `workspace-write` 沙盒化也可能失败。典型症状是 bubblewrap/user-namespace 错误，例如 `setting up uid map: Permission denied` 或 `loopback: Failed RTM_NEWADDR: Operation not permitted`。

在这种情况下，建议使用：

```
codex exec --sandbox danger-full-access "<task>"
```

改用进程边界作为安全层：明确的 `workdir`、启动前干净的 git 状态、窄范围的任务提示、`git diff` 审查、有针对性的测试，以及在提交大范围更改前由人工/代理确认。

## PR 审查

克隆到临时目录进行安全审查：

```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && codex review --base origin/main", pty=true)
```

## 使用工作树进行并行问题修复

```
# 创建工作树
terminal(command="git worktree add -b fix/issue-78 /tmp/issue-78 main", workdir="~/project")
terminal(command="git worktree add -b fix/issue-99 /tmp/issue-99 main", workdir="~/project")

# 在每个工作树中启动 Codex
terminal(command="codex --yolo exec 'Fix issue #78: <description>. Commit when done.'", workdir="/tmp/issue-78", background=true, pty=true)
terminal(command="codex --yolo exec 'Fix issue #99: <description>. Commit when done.'", workdir="/tmp/issue-99", background=true, pty=true)

# 监控
process(action="list")

# 完成后，推送并创建 PR
terminal(command="cd /tmp/issue-78 && git push -u origin fix/issue-78")
terminal(command="gh pr create --repo user/repo --head fix/issue-78 --title 'fix: ...' --body '...'")

# 清理
terminal(command="git worktree remove /tmp/issue-78", workdir="~/project")
```

## 批量 PR 审查

```
# 获取所有 PR 引用
terminal(command="git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'", workdir="~/project")

# 并行审查多个 PR
terminal(command="codex exec 'Review PR #86. git diff origin/main...origin/pr/86'", workdir="~/project", background=true, pty=true)
terminal(command="codex exec 'Review PR #87. git diff origin/main...origin/pr/87'", workdir="~/project", background=true, pty=true)

# 发布结果
terminal(command="gh pr comment 86 --body '<review>'", workdir="~/project")
```

## 规则

1. **始终使用 `pty=true`** — Codex 是交互式终端应用，没有 PTY 会挂起
2. **需要 git 仓库** — Codex 无法在 git 目录外运行。对于临时工作，使用 `mktemp -d && git init`
3. **一次性使用 `exec`** — `codex exec "prompt"` 运行后干净退出
4. **构建时使用 `--full-auto`** — 自动批准沙盒内的更改
5. **长时间任务使用后台** — 使用 `background=true` 并通过 `process` 工具监控
6. **不要干扰** — 使用 `poll`/`log` 监控，对长时间运行的任务保持耐心
7. **可以并行** — 同时运行多个 Codex 进程进行批量工作