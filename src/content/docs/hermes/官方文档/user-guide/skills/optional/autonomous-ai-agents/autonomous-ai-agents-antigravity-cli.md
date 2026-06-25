--- frontmatter ---
---
title: "Antigravity Cli – 操作 Antigravity CLI (agy)：插件、认证、沙箱"
sidebar_label: "Antigravity Cli"
description: "操作 Antigravity CLI (agy)：插件、认证、沙箱"
---

--- body ---
--- body ---
{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源 SKILL.md 而非此页面。 */}

# Antigravity Cli

操作 Antigravity CLI (agy)：插件、认证、沙箱。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/autonomous-ai-agents/antigravity-cli` 安装 |
| 路径 | `optional-skills/autonomous-ai-agents/antigravity-cli` |
| 版本 | `0.1.0` |
| 作者 | Tony Simons (asimons81), Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Coding-Agent`, `Antigravity`, `CLI`, `Auth`, `Plugins`, `Sandbox` |
| 相关技能 | [`grok`](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-grok), [`codex`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex), [`claude-code`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code), [`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) |

## 参考：完整 SKILL.md

:::info
以下是在触发此技能时 Hermes 加载的完整技能定义。这是技能激活时代理看到的指令。
:::

# Antigravity CLI (`agy`)

Antigravity CLI 的操作指南，通过 `agy` 调用。所有 `agy` 命令均通过 Hermes `terminal` 工具运行；使用 `read_file` 检查其配置和日志。此技能是参考 + 过程——它不封装网络 API，因此无需从 Hermes 本身进行身份验证。

## 何时使用

- 安装、更新或冒烟测试 `agy` 二进制文件
- 驱动非交互式 `agy --print` / `agy -p` 单次命令
- 调试 Antigravity 的认证、沙箱、权限或插件状态
- 读取 Antigravity 设置、键绑定、对话或日志

## 心智模型

Antigravity 分为两层——请区分清楚，否则指导将出错：

1. **Shell 包装命令** — `agy help`、`agy install`、`agy plugin`、`agy update`、`agy changelog`。通过 `terminal` 工具运行这些命令。
2. **交互式会话内斜杠命令** — `/config`、`/permissions`、`/skills`、`/agents` 等。这些仅存在于正在运行的 `agy` TUI 会话中，而非 shell 包装中。

`agy help` 显示的是 shell 包装表面，而不是会话内斜杠命令。

## 先决条件

- `agy` 二进制文件位于 PATH 中。通过 `terminal` 工具验证：`command -v agy && agy --version`。
- 此技能不需要环境变量或 API 密钥——Antigravity 通过操作系统密钥环 / 浏览器登录管理其自身的认证（参见下面的认证部分）。

## 如何运行

所有 `agy` 命令均通过 `terminal` 工具调用。示例：

```
terminal(command="agy --version")
terminal(command="agy help")
terminal(command="agy plugin list")
terminal(command="agy --print '用三点概括该仓库'", workdir="/path/to/project")
```

对于交互式多轮 TUI 会话，使用 `pty=true`（以及 tmux 用于捕获/监控）启动 `agy`，与 `codex` / `claude-code` 技能相同的模式。对于单次冒烟测试和脚本化提示，推荐使用 `agy --print`（非交互式）。

要检查 Antigravity 自身的文件，请使用 `read_file` 读取下方核心路径中的路径——不要在终端中通过 `cat` 读取。

## 核心路径

- 二进制 / 入口点：`agy`
- 应用数据目录：`~/.gemini/antigravity-cli/`
- 设置文件：`~/.gemini/antigravity-cli/settings.json`
- 键绑定文件：`~/.gemini/antigravity-cli/keybindings.json`
- 日志：`~/.gemini/antigravity-cli/log/cli-*.log`
- 对话：`~/.gemini/antigravity-cli/conversations/`
- 脑工件：`~/.gemini/antigravity-cli/brain/`
- 历史：`~/.gemini/antigravity-cli/history.jsonl`
- 插件暂存：`~/.gemini/antigravity-cli/plugins/<plugin_name>/`

## 快速参考

### 包装命令
- `agy changelog`
- `agy help`
- `agy install`
- `agy plugin` / `agy plugins`
- `agy update`

### 有用标志
- `--add-dir`
- `--continue` / `-c`
- `--conversation`
- `--dangerously-skip-permissions`
- `--print` / `-p`
- `--print-timeout`
- `--prompt`
- `--prompt-interactive` / `-i`
- `--sandbox`
- `--log-file`
- `--version`

### 插件子命令 (`agy plugin --help`)
- `list`, `import [source]`, `install <target>`, `uninstall <name>`,
  `enable <name>`, `disable <name>`, `validate [path]`, `link <mp> <target>`,
  `help`

### 安装标志 (`agy install --help`)
- `--dir`, `--skip-aliases`, `--skip-path`

### 会话内斜杠命令
- **对话控制：** `/resume` (`/switch`), `/rewind` (`/undo`), `/rename <name>`, `/clear`, `/fork`, `/reset`, `/new`
- **设置及工具：** `/config`, `/settings`, `/permissions`, `/model`, `/keybindings`, `/statusline`, `/tasks`, `/skills`, `/mcp`, `/open <path>`, `/usage`, `/logout`, `/agents`
- **提示辅助：** `@` 路径自动补全，`esc esc` 清除提示（未流式传输时），`!` 直接运行终端命令，`?` 打开帮助

## 设置和权限

### 常用设置键 (`settings.json`)
- `allowNonWorkspaceAccess`
- `colorScheme`
- `permissions.allow`
- `trustedWorkspaces`

### 权限模式
`request-review`, `always-proceed`, `strict`, `proceed-in-sandbox`.

### 沙箱行为
- `enableTerminalSandbox` 是 `settings.json` 中的一个布尔值；默认值为 `false`。
- 启动时覆盖（`--sandbox`, `--dangerously-skip-permissions`）可以覆盖当前会话的持久设置。

## 认证行为

- CLI 首先尝试 OS 安全密钥环。
- 如果没有保存的会话，则回退到基于浏览器的 Google 登录。
- 本地环境中会打开默认浏览器；在 SSH 环境下会打印授权 URL 并等待粘贴认证码。
- `/logout` 移除已保存的凭据。

## 插件

- 插件暂存于 `~/.gemini/antigravity-cli/plugins/<plugin_name>/` 下。
- 它们可以捆绑技能、代理、规则、MCP 服务器和钩子。
- `agy plugin list` 返回无导入插件是有效的空状态。

## 易错点

- `agy help` 显示的是包装命令，而非交互式斜杠命令。
- `agy --version` 是安全的非交互式版本检查；`agy version` 是交互式的，在无真实 TTY 时可能失败。
- 故障排查首选位置：`~/.gemini/antigravity-cli/log/cli-*.log`（使用 `read_file` 读取）。
- 不要混淆持久 JSON 设置与启动时覆盖。
- `~/.gemini/antigravity-cli/bin/agentapi` 是 `agy agentapi` 的薄包装。
- 在 WSL 上，令牌存储基于文件，因此认证问题通常是本地文件/会话状态问题，而非浏览器问题。
- 工作区标识可能取决于启动目录和 `.antigravitycli` 项目标记。

## 验证

通过 `terminal` 工具确认安装真实且可用（使用 `read_file` 读取文件）：

1. `terminal(command="command -v agy")`
2. `terminal(command="agy --version")`
3. `terminal(command="agy help")`
4. `terminal(command="agy plugin list")`
5. 使用 `read_file` 读取 `~/.gemini/antigravity-cli/settings.json`
6. 使用 `read_file` 读取最新的 `~/.gemini/antigravity-cli/log/cli-*.log`
7. 如有需要，使用 `read_file` 读取 `~/.gemini/antigravity-cli/keybindings.json`

## 支持文件

- `references/cli-docs.md` — 来自入门、使用和功能文档的简化笔记。