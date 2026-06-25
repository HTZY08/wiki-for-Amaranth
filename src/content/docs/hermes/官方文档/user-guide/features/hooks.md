### `transform_llm_output`

在工具调用循环完成且模型生成最终响应后**每轮触发一次**，**在此响应传递给用户之前**（CLI、网关或编程调用方）。允许插件使用传统编程方法重写助手的最终文本——不会因SOUL风格文本或技能驱动转换而消耗额外的推理令牌。

**回调签名：**

```python
def my_callback(
    response_text: str,
    session_id: str,
    model: str,
    platform: str,
    **kwargs,
) -> str | None:
```

| 参数 | 类型 | 描述 |
|------|------|------|
| `response_text` | `str` | 助手本轮最终响应文本。 |
| `session_id` | `str` | 此会话的会话ID（对于一次性运行可能为空）。 |
| `model` | `str` | 生成响应的模型名称（例如 `anthropic/claude-sonnet-4.6`）。 |
| `platform` | `str` | 交付平台（`cli`、`telegram`、`discord`……未设置时为空）。 |

**返回值：** 非空 `str` 用于替换响应文本，`None` 或空字符串保持原样。**当多个插件注册时，第一个非空字符串获胜**——与 `transform_tool_result` 规则相同。

**用例：** 应用个性/词汇转换（海盗语、海绵宝宝风格）、从最终文本中隐藏用户特定标识符、添加项目特定签名页脚、在不消耗SOOL指令令牌的情况下强制执行内部风格指南。

```python
import os, re

def spongebob(response_text, **kwargs):
    if os.environ.get("SPONGEBOB_MODE") != "on":
        return None  # 原样传递
    return re.sub(r"!", "!! Tartar sauce!", response_text)

def register(ctx):
    ctx.register_hook("transform_llm_output", spongebob)
```

该钩子仅在非空、非中断的响应上触发——不会在停止按钮中断或空轮次触发。异常会记录为警告，不会中断代理执行。

---

--- body ---
--- body ---
## Shell 钩子

在 `cli-config.yaml` 中声明 shell 脚本钩子，Hermes 会在相应的插件钩子事件触发时将其作为子进程运行——无论是在 CLI 还是网关会话中。无需编写 Python 插件。

当您希望使用即插即用的单文件脚本（Bash、Python 或任何带有 shebang 的语言）时，可以使用 shell 钩子：

- **阻止工具调用**——拒绝危险的 `terminal` 命令，强制实施按目录策略，要求对破坏性 `write_file` / `patch` 操作进行批准。
- **在工具调用后运行**——自动格式化代理刚刚编写的 Python 或 TypeScript 文件，记录 API 调用，触发 CI 工作流。
- **向下一轮 LLM 注入上下文**——将 `git status` 输出、当前星期几或检索到的文档附加到用户消息（参见 [`pre_llm_call`](#pre_llm_call)）。
- **观察生命周期事件**——当子代理完成（`subagent_stop`）或会话启动（`on_session_start`）时写入日志行。

Shell 钩子通过调用 `agent.shell_hooks.register_from_config(cfg)` 在 CLI 启动（`hermes_cli/main.py`）和网关启动（`gateway/run.py`）时注册。它们与 Python 插件钩子自然组合——两者都通过同一个调度器。

### 快速对比

| 维度 | Shell 钩子 | [插件钩子](#plugin-hooks) | [网关钩子](#gateway-event-hooks) |
|-----------|-------------|-------------------------------|---------------------------------------|
| 声明位置 | `hooks:` 块，位于 `~/.hermes/config.yaml` | `register()` 在 `plugin.yaml` 插件中 | `HOOK.yaml` + `handler.py` 目录 |
| 存放位置 | `~/.hermes/agent-hooks/`（惯例） | `~/.hermes/plugins/<name>/` | `~/.hermes/hooks/<name>/` |
| 语言 | 任意（Bash、Python、Go 二进制等） | 仅 Python | 仅 Python |
| 运行环境 | CLI + 网关 | CLI + 网关 | 仅网关 |
| 事件 | `VALID_HOOKS`（包括 `subagent_stop`） | `VALID_HOOKS` | 网关生命周期（`gateway:startup`，`agent:*`，`command:*`） |
| 能否阻止工具调用 | 是（`pre_tool_call`） | 是（`pre_tool_call`） | 否 |
| 能否注入 LLM 上下文 | 是（`pre_llm_call`） | 是（`pre_llm_call`） | 否 |
| 同意 | 每个 `(event, command)` 对首次使用时提示 | 隐式（信任 Python 插件） | 隐式（信任目录） |
| 进程间隔离 | 是（子进程） | 否（进程内） | 否（进程内） |

### 配置模式

```yaml
hooks:
  <event_name>:                  # 必须在 VALID_HOOKS 中
    - matcher: "<regex>"         # 可选；仅用于 pre/post_tool_call
      command: "<shell command>" # 必需；通过 shlex.split 运行，shell=False
      timeout: <seconds>         # 可选；默认 60，上限 300

hooks_auto_accept: false         # 参见下面的“同意模型”
```

事件名称必须是[插件钩子事件](#plugin-hooks)之一；拼写错误会产生“您是否指的是 X？”的警告并跳过。单个条目中的未知键将被忽略；缺少 `command` 则会跳过并发出警告。`timeout > 300` 会被限制并发出警告。

### JSON 线路协议

每次事件触发时，Hermes 会为每个匹配的钩子（匹配器允许时）生成一个子进程，将 JSON 负载通过 **stdin** 管道传入，并读取 **stdout** 返回的 JSON。

**stdin — 脚本接收的负载：**

```json
{
  "hook_event_name": "pre_tool_call",
  "tool_name":       "terminal",
  "tool_input":      {"command": "rm -rf /"},
  "session_id":      "sess_abc123",
  "cwd":             "/home/user/project",
  "extra":           {"task_id": "...", "tool_call_id": "..."}
}
```

对于非工具事件（`pre_llm_call`、`subagent_stop`、会话生命周期），`tool_name` 和 `tool_input` 为 `null`。`extra` 字典携带所有事件特定的 kwargs（`user_message`、`conversation_history`、`child_role`、`duration_ms`……）。不可序列化的值会被字符串化，而非省略。

**stdout — 可选响应：**

```jsonc
// 阻止 pre_tool_call（两种格式均可接受；内部规范化）：
{"decision": "block", "reason":  "Forbidden: rm -rf"}   // Claude-Code 风格
{"action":   "block", "message": "Forbidden: rm -rf"}   // Hermes 规范格式

// 为 pre_llm_call 注入上下文：
{"context": "Today is Friday, 2026-04-17"}

// 静默无操作——任何空输出或不匹配的输出均可：
```

格式错误的 JSON、非零退出代码和超时会记录警告，但不会终止代理循环。

### 工作示例

#### 1. 每次写入后自动格式化 Python 文件

```yaml
# ~/.hermes/config.yaml
hooks:
  post_tool_call:
    - matcher: "write_file|patch"
      command: "~/.hermes/agent-hooks/auto-format.sh"
```

```bash
#!/usr/bin/env bash
# ~/.hermes/agent-hooks/auto-format.sh
payload="$(cat -)"
path=$(echo "$payload" | jq -r '.tool_input.path // empty')
[[ "$path" == *.py ]] && command -v black >/dev/null && black "$path" 2>/dev/null
printf '{}\n'
```

代理在上下文中看到的文件**不会自动重新读取**——重新格式化仅影响磁盘上的文件。后续的 `read_file` 调用会获取格式化后的版本。

#### 2. 阻止破坏性 `terminal` 命令

```yaml
hooks:
  pre_tool_call:
    - matcher: "terminal"
      command: "~/.hermes/agent-hooks/block-rm-rf.sh"
      timeout: 5
```

```bash
#!/usr/bin/env bash
# ~/.hermes/agent-hooks/block-rm-rf.sh
payload="$(cat -)"
cmd=$(echo "$payload" | jq -r '.tool_input.command // empty')
if echo "$cmd" | grep -qE 'rm[[:space:]]+-rf?[[:space:]]+/'; then
  printf '{"decision": "block", "reason": "blocked: rm -rf / is not permitted"}\n'
else
  printf '{}\n'
fi
```

#### 3. 给每轮注入 `git status`（等同于 Claude-Code 的 `UserPromptSubmit`）

```yaml
hooks:
  pre_llm_call:
    - command: "~/.hermes/agent-hooks/inject-cwd-context.sh"
```

```bash
#!/usr/bin/env bash
# ~/.hermes/agent-hooks/inject-cwd-context.sh
cat - >/dev/null   # 丢弃 stdin 负载
if status=$(git status --porcelain 2>/dev/null) && [[ -n "$status" ]]; then
  jq --null-input --arg s "$status" \
     '{context: ("Uncommitted changes in cwd:\n" + $s)}'
else
  printf '{}\n'
fi
```

Claude Code 的 `UserPromptSubmit` 事件并非 Hermes 单独的事件——`pre_llm_call` 在相同位置触发且已支持上下文注入。在此处使用它。

#### 4. 记录每个子代理完成

```yaml
hooks:
  subagent_stop:
    - command: "~/.hermes/agent-hooks/log-orchestration.sh"
```

```bash
#!/usr/bin/env bash
# ~/.hermes/agent-hooks/log-orchestration.sh
log=~/.hermes/logs/orchestration.log
jq -c '{ts: now, parent: .session_id, extra: .extra}' < /dev/stdin >> "$log"
printf '{}\n'
```

### 同意模型

每个唯一的 `(event, command)` 对在 Hermes 首次看到时都会向用户提示批准，然后将决定持久化到 `~/.hermes/shell-hooks-allowlist.json`。后续运行（CLI 或网关）会跳过提示。

有三种绕过交互式提示的方法——任一方法均有效：

1. CLI 上的 `--accept-hooks` 标志（例如 `hermes --accept-hooks chat`）
2. 环境变量 `HERMES_ACCEPT_HOOKS=1`
3. `cli-config.yaml` 中的 `hooks_auto_accept: true`

非 TTY 运行（网关、cron、CI）需要上述方法之一——否则任何新添加的钩子会静默地保持未注册状态并记录警告。

**脚本编辑被静默信任。** 允许列表的键是确切的命令字符串，而非脚本哈希，因此编辑磁盘上的脚本不会使同意失效。`hermes hooks doctor` 会标记 mtime 变动，以便您发现编辑并决定是否重新批准。

#### 手动允许列表

手动允许列表对于非 TTY 或服务账户部署非常有用，这类场景下操作员无法交互式地回答首次使用提示。允许列表文件是 `~/.hermes/shell-hooks-allowlist.json`，预期格式是一个 `approvals` 数组。每个批准记录钩子的 `event` 和确切的 `command` 字符串：

```json
{
  "approvals": [
    {
      "event": "post_llm_call",
      "command": "/home/hermes/.hermes/hooks/my-hook.py"
    }
  ]
}
```

命令字符串必须与配置的钩子命令完全匹配。一个以路径为键并带有 `sha256` 字段的对象不是预期格式，不会批准该钩子。使用 `hermes hooks list` 验证手动条目。

### `hermes hooks` CLI

| 命令 | 功能 |
|---------|------|
| `hermes hooks list` | 列出已配置的钩子，包括匹配器、超时和同意状态 |
| `hermes hooks test <event> [--for-tool X] [--payload-file F]` | 针对合成负载触发每个匹配的钩子，并打印解析后的响应 |
| `hermes hooks revoke <command>` | 移除所有与 `<command>` 匹配的允许列表条目（下次重启生效） |
| `hermes hooks doctor` | 针对每个配置的钩子：检查执行位、允许列表状态、mtime 漂移、JSON 输出有效性以及大致执行时间 |

### 安全

Shell 钩子**使用您的完整用户凭据运行**——与 cron 条目或 shell 别名相同的信任边界。将 `config.yaml` 中的 `hooks:` 块视为特权配置：

- 仅引用您编写或全面审查过的脚本。
- 将脚本保留在 `~/.hermes/agent-hooks/` 内，以便路径易于审计。
- 在拉取共享配置后重新运行 `hermes hooks doctor`，以便在钩子注册前发现新添加的钩子。
- 如果您的 config.yaml 在团队中进行版本控制，请像审查 CI 配置一样审查更改 `hooks:` 部分的 PR。

### 排序与优先级

Python 插件钩子和 shell 钩子都流经同一个 `invoke_hook()` 调度器。Python 插件先注册（`discover_and_load()`），然后是 shell 钩子（`register_from_config()`），因此在平局情况下，Python `pre_tool_call` 的阻止决定优先。第一个有效的阻止胜出——一旦任何回调产生带有非空消息的 `{"action": "block", "message": str}`，聚合器就会返回。