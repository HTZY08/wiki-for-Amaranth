```yaml
---
name: security-reviewer
description: 安全导向的代码审查
model: opus
tools: [Read, Bash]
---

你是一名高级安全工程师。审查代码中以下方面：
- 注入漏洞（SQL、XSS、命令注入）
- 身份验证/授权缺陷
- 代码中的密钥
- 不安全的反序列化
```

通过以下方式调用：`@security-reviewer review the auth module`

### 通过 CLI 使用动态代理（Agent）
```
terminal(command="claude --agents '{\"reviewer\": {\"description\": \"Reviews code\", \"prompt\": \"You are a code reviewer focused on performance\"}}' -p 'Use @reviewer to check auth.py'", timeout=120)
```

Claude 可以编排多个代理：“Use @db-expert to optimize queries, then @security to audit the changes.”

## 钩子（Hook）——事件自动化

在 `.claude/settings.json`（项目）或 `~/.claude/settings.json`（全局）中配置：

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write(*.py)",
      "hooks": [{"type": "command", "command": "ruff check --fix $CLAUDE_FILE_PATHS"}]
    }],
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{"type": "command", "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -q 'rm -rf'; then echo 'Blocked!' && exit 2; fi"}]
    }],
    "Stop": [{
      "hooks": [{"type": "command", "command": "echo 'Claude finished a response' >> /tmp/claude-activity.log"}]
    }]
  }
}
```

### 所有 8 种钩子类型
| 钩子（Hook） | 触发时机 | 常见用途 |
|------|--------------|------------|
| `UserPromptSubmit` | 在Claude处理用户提示之前 | 输入验证、日志记录 |
| `PreToolUse` | 在执行工具之前 | 安全门控、阻止危险命令（exit 2 = 阻止） |
| `PostToolUse` | 在工具完成之后 | 自动格式化代码、运行linter |
| `Notification` | 在权限请求或输入等待时 | 桌面通知、警报 |
| `Stop` | 当Claude完成一次响应时 | 完成日志记录、状态更新 |
| `SubagentStop` | 当子代理完成时 | 代理编排 |
| `PreCompact` | 在上下文内存清除之前 | 备份会话记录 |
| `SessionStart` | 当会话开始时 | 加载开发上下文（例如 `git status`） |

### 钩子环境变量
| 变量 | 内容 |
|----------|---------|
| `CLAUDE_PROJECT_DIR` | 当前项目路径 |
| `CLAUDE_FILE_PATHS` | 正在修改的文件 |
| `CLAUDE_TOOL_INPUT` | 工具参数（JSON格式） |

### 安全钩子示例
```json
{
  "PreToolUse": [{
    "matcher": "Bash",
    "hooks": [{"type": "command", "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'rm -rf|git push.*--force|:(){ :|:& };:'; then echo 'Dangerous command blocked!' && exit 2; fi"}]
  }]
}
```

## MCP 集成

添加用于数据库、API和服务的外部工具服务器：

```
# GitHub 集成
terminal(command="claude mcp add -s user github -- npx @modelcontextprotocol/server-github", timeout=30)

# PostgreSQL 查询
terminal(command="claude mcp add -s local postgres -- npx @anthropic-ai/server-postgres --connection-string postgresql://localhost/mydb", timeout=30)

# Puppeteer 用于 Web 测试
terminal(command="claude mcp add puppeteer -- npx @anthropic-ai/server-puppeteer", timeout=30)
```

### MCP 作用域（Scope）
| 标志 | 作用域 | 存储位置 |
|------|-------|---------|
| `-s user` | 全局（所有项目） | `~/.claude.json` |
| `-s local` | 当前项目（个人） | `.claude/settings.local.json`（被 gitignore） |
| `-s project` | 当前项目（团队共享） | `.claude/settings.json`（被 git 跟踪） |

### 打印模式/CI 模式下的 MCP
```
terminal(command="claude --bare -p 'Query database' --mcp-config mcp-servers.json --strict-mcp-config", timeout=60)
```
`--strict-mcp-config` 会忽略除 `--mcp-config` 中指定的 MCP 服务器以外的所有服务器。

在聊天中引用 MCP 资源：`@github:issue://123`

### MCP 限制与调优
- **工具描述（Tool descriptions）：** 每个服务器的工具描述和服务器指令的上限为 2KB
- **结果大小（Result size）：** 默认有上限；使用 `maxResultSizeChars` 注解可允许大型输出最多 **500K** 字符
- **输出令牌（Output tokens）：** `export MAX_MCP_OUTPUT_TOKENS=50000` —— 限制 MCP 服务器的输出以防止上下文淹没
- **传输协议（Transports）：** `stdio`（本地进程）、`http`（远程）、`sse`（服务器推送事件）

## 监控交互式会话

### 读取 TUI 状态
```
# 定期捕获以检查 Claude 是否仍在工作或等待输入
terminal(command="tmux capture-pane -t dev -p -S -10")
```

查看以下指示：
- 底部的 `❯` = 等待你的输入（Claude 已完成或正在询问问题）
- `●` 行 = Claude 正在积极使用工具（读取、写入、运行命令）
- `⏵⏵ bypass permissions on` = 状态栏显示权限模式
- `◐ medium · /effort` = 状态栏中当前的努力级别
- `ctrl+o to expand` = 工具输出被截断（可交互展开）

### 上下文窗口健康状态
在交互模式下使用 `/context` 查看上下文使用情况的彩色网格。关键阈值：
- **< 70%** —— 正常操作，高精度
- **70-85%** —— 精度开始下降，考虑使用 `/compact`
- **> 85%** —— 幻觉风险显著增加，使用 `/compact` 或 `/clear`

## 环境变量

| 变量 | 效果 |
|----------|--------|
| `ANTHROPIC_API_KEY` | 用于身份验证的 API 密钥（OAuth 的替代方案） |
| `CLAUDE_CODE_EFFORT_LEVEL` | 默认努力级别：`low`、`medium`、`high`、`max` 或 `auto` |
| `MAX_THINKING_TOKENS` | 限制思考令牌（设置为 `0` 可完全禁用思考） |
| `MAX_MCP_OUTPUT_TOKENS` | 限制来自 MCP 服务器的输出（默认值因情况而异；例如设置为 `50000`） |
| `CLAUDE_CODE_NO_FLICKER=1` | 启用 alt-screen 渲染以消除终端闪烁 |
| `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` | 从子进程中移除凭据以增强安全性 |

## 成本与性能提示

1. 在打印模式下使用 `--max-turns` 以防止无限循环。大多数任务从 5-10 次开始。
2. 使用 `--max-budget-usd` 设置成本上限。注意：系统提示缓存创建的最低费用约为 $0.05。
3. 对于简单任务使用 `--effort low`（更快、更便宜）。对于复杂推理使用 `high` 或 `max`。
4. 在 CI/脚本中使用 `--bare` 以跳过插件/钩子发现开销。
5. 使用 `--allowedTools` 限制为仅需要的工具（例如，仅 `Read` 用于审查）。
6. 在交互式会话中，当上下文变得庞大时使用 `/compact`。
7. 如果只需要分析已知内容，可以通过管道输入，而不是让 Claude 读取文件。
8. 对于简单任务使用 `--model haiku`（更便宜），对于复杂的多步骤工作使用 `--model opus`。
9. 在打印模式下使用 `--fallback-model haiku` 以优雅处理模型过载。
10. 为不同任务启动新会话——会话持续 5 小时；新鲜上下文更高效。
11. 在 CI 中使用 `--no-session-persistence` 以避免在磁盘上累积保存的会话。

## 陷阱与注意事项

1. **交互模式需要 tmux** —— Claude Code 是一个完整的 TUI 应用。在 Hermes 终端中单独使用 `pty=true` 可行，但 tmux 提供 `capture-pane` 用于监控和 `send-keys` 用于输入，这对编排至关重要。
2. **`--dangerously-skip-permissions` 对话框默认选择“否，退出”** —— 你必须发送 Down 然后 Enter 才能接受。打印模式（`-p`）完全跳过此步骤。
3. **`--max-budget-usd` 最低约为 $0.05** —— 仅系统提示缓存创建就需要这么多。设置更低的值会立即报错。
4. **`--max-turns` 仅适用于打印模式** —— 在交互式会话中被忽略。
5. **Claude 可能使用 `python` 而不是 `python3`** —— 在没有 `python` 符号链接的系统上，Claude 的 bash 命令首次会失败，但会自动修正。
6. **会话恢复需要相同的目录** —— `--continue` 会查找当前工作目录的最近会话。
7. **`--json-schema` 需要足够的 `--max-turns`** —— Claude 在生成结构化输出之前必须读取文件，这需要多次交互。
8. **信任对话框每个目录只出现一次** —— 仅首次出现，然后被缓存。
9. **后台 tmux 会话会持久存在** —— 完成后始终使用 `tmux kill-session -t <name>` 清理。
10. **斜杠命令（如 `/commit`）仅适用于交互模式** —— 在 `-p` 模式下，用自然语言描述任务。
11. **`--bare` 跳过 OAuth** —— 需要 `ANTHROPIC_API_KEY` 环境变量或 settings 中的 `apiKeyHelper`。
12. **上下文退化是真实存在的** —— 当上下文窗口使用超过 70% 时，AI 输出质量会明显下降。使用 `/context` 监控并主动使用 `/compact`。

## Hermes 代理的规则

1. **对于单次任务，优先使用打印模式（`-p`）** —— 更简洁，无需处理对话框，结构化输出
2. **对于多轮交互工作，使用 tmux** —— 编排 TUI 的唯一可靠方式
3. **始终设置 `workdir`** —— 保持 Claude 专注于正确的项目目录
4. **在打印模式下设置 `--max-turns`** —— 防止无限循环和成本失控
5. **监控 tmux 会话** —— 使用 `tmux capture-pane -t <session> -p -S -50` 检查进度
6. **查看 `❯` 提示符** —— 表示 Claude 正在等待输入（已完成或正在提问）
7. **清理 tmux 会话** —— 完成后将其终止以避免资源泄漏
8. **向用户报告结果** —— 完成后，总结 Claude 做了什么以及有哪些变化
9. **不要终止速度慢的会话** —— Claude 可能正在进行多步骤工作；请检查进度
10. **使用 `--allowedTools`** —— 将能力限制为任务实际所需的范围
```