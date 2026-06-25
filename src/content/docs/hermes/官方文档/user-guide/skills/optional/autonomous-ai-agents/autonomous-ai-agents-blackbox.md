--- frontmatter ---
---
title: "Blackbox — 将编码任务委托给 Blackbox AI CLI 代理"
sidebar_label: "Blackbox"
description: "将编码任务委托给 Blackbox AI CLI 代理"
---

--- body ---

{/* 此页面由 skill 的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Blackbox

将编码任务委托给 Blackbox AI CLI 代理（Agent）。这是一个多模型代理，内置评审器（Judge），可通过多个大语言模型（LLM）运行任务并选择最佳结果。需要安装 blackbox CLI 并配置 Blackbox AI API 密钥。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/autonomous-ai-agents/blackbox` 安装 |
| 路径 | `optional-skills/autonomous-ai-agents/blackbox` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent (Nous Research) |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Coding-Agent`, `Blackbox`, `Multi-Agent`, `Judge`, `Multi-Model` |
| 相关技能 | [`claude-code`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code), [`codex`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex), [`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) |

## 参考：完整 SKILL.md

:::info
以下内容是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时代理所看到的指令。
:::

# Blackbox CLI

通过 Hermes 终端将编码任务委托给 [Blackbox AI](https://www.blackbox.ai/)。Blackbox 是一个多模型编码代理 CLI，它将任务分发给多个大语言模型（Claude、Codex、Gemini、Blackbox Pro），并使用评审器选择最佳实现。

该 CLI 是 [开源的](https://github.com/blackboxaicode/cli)（GPL-3.0，TypeScript，从 Gemini CLI 分支而来），支持交互式会话、非交互式一次性执行、检查点（checkpoint）、MCP 和视觉模型切换。

## 前置条件

- Node.js 20+ 已安装
- Blackbox CLI 已安装：`npm install -g @blackboxai/cli`
- 或从源码安装：
  ```
  git clone https://github.com/blackboxaicode/cli.git
  cd cli && npm install && npm install -g .
  ```
- API 密钥来自 [app.blackbox.ai/dashboard](https://app.blackbox.ai/dashboard)
- 配置：运行 `blackbox configure` 并输入你的 API 密钥
- 在终端调用中使用 `pty=true` — Blackbox CLI 是一个交互式终端应用

## 一次性任务

```
terminal(command="blackbox --prompt '向 Express API 添加带有刷新令牌的 JWT 认证'", workdir="/path/to/project", pty=true)
```

对于快速临时工作：
```
terminal(command="cd $(mktemp -d) && git init && blackbox --prompt '构建一个使用 SQLite 的待办事项 REST API'", pty=true)
```

## 后台模式（长时间任务）

对于耗时数分钟的任务，请使用后台模式以便监控进度：

```
# 在后台启动，使用 PTY
terminal(command="blackbox --prompt '将认证模块重构为使用 OAuth 2.0'", workdir="~/project", background=true, pty=true)
# 返回 session_id

# 监控进度
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# 如果 Blackbox 提问，发送输入
process(action="submit", session_id="<id>", data="yes")

# 如果需要，终止进程
process(action="kill", session_id="<id>")
```

## 检查点与恢复

Blackbox CLI 内置检查点支持，可暂停和恢复任务：

```
# 任务完成后，Blackbox 会显示一个检查点标签
# 通过后续任务恢复：
terminal(command="blackbox --resume-checkpoint 'task-abc123-2026-03-06' --prompt '现在为端点添加速率限制'", workdir="~/project", pty=true)
```

## 会话命令

在交互式会话中，使用以下命令：

| 命令 | 效果 |
|---------|--------|
| `/compress` | 压缩对话历史以节省令牌 |
| `/clear` | 清除历史并重新开始 |
| `/stats` | 查看当前令牌使用量 |
| `Ctrl+C` | 取消当前操作 |

## PR 审查

克隆到临时目录以避免修改工作树：

```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && blackbox --prompt '针对 main 分支审查此 PR。检查 bug、安全问题以及代码质量。'", pty=true)
```

## 并行工作

为独立任务生成多个 Blackbox 实例：

```
terminal(command="blackbox --prompt '修复登录 bug'", workdir="/tmp/issue-1", background=true, pty=true)
terminal(command="blackbox --prompt '为认证添加单元测试'", workdir="/tmp/issue-2", background=true, pty=true)

# 监控所有实例
process(action="list")
```

## 多模型模式

Blackbox 的独特之处在于通过多个模型运行相同任务并评审结果。通过 `blackbox configure` 配置要使用的模型 — 选择多个提供商以启用主席/评审工作流，CLI 将评估来自不同模型的输出并选择最佳结果。

## 关键标志

| 标志 | 效果 |
|------|--------|
| `--prompt "task"` | 非交互式一次性执行 |
| `--resume-checkpoint "tag"` | 从保存的检查点恢复 |
| `--yolo` | 自动批准所有操作和模型切换 |
| `blackbox session` | 启动交互式聊天会话 |
| `blackbox configure` | 更改设置、提供商、模型 |
| `blackbox info` | 显示系统信息 |

## 视觉支持

Blackbox 自动检测输入中的图像并可以切换到多模态分析。VLM 模式：
- `"once"` — 仅对当前查询切换模型
- `"session"` — 对整个会话切换
- `"persist"` — 保持在当前模型（不切换）

## 令牌限制

通过 `.blackboxcli/settings.json` 控制令牌使用：
```json
{
  "sessionTokenLimit": 32000
}
```

## 规则

1. **始终使用 `pty=true`** — Blackbox CLI 是一个交互式终端应用，没有 PTY 会挂起
2. **使用 `workdir`** — 让代理专注于正确的目录
3. **长时间任务使用后台** — 使用 `background=true` 并通过 `process` 工具监控
4. **不要干扰** — 使用 `poll`/`log` 监控，不要因为任务慢就终止会话
5. **报告结果** — 完成后，检查更改内容并向用户总结
6. **积分需要付费** — Blackbox 使用基于积分的系统；多模型模式消耗积分更快
7. **检查前置条件** — 在尝试委托之前，验证 `blackbox` CLI 是否已安装