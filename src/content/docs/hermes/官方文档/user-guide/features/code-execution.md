---
title: Code Execution
---

sidebar_position: 8
title: "代码执行（Code Execution）"
description: "通过提供 RPC 工具调用的编程式 Python 执行，将多步工作流压缩为单次对话"
---

--- body ---
# 代码执行（程序化工具调用）

`execute_code` 工具让代理（Agent）能够编写 Python 脚本，以程序化方式调用 Hermes 工具，从而将多步工作流压缩为单次 LLM 对话。脚本在代理主机上的子进程中运行，通过 Unix 域套接字 RPC 与 Hermes 通信。

## 工作原理

1. 代理编写 Python 脚本，使用 `from hermes_tools import ...`
2. Hermes 生成一个包含 RPC 函数的 `hermes_tools.py` 存根模块
3. Hermes 打开一个 Unix 域套接字并启动 RPC 监听线程
4. 脚本在子进程中运行——工具调用通过套接字传回 Hermes
5. 只有脚本的 `print()` 输出返回给 LLM；中间工具结果从不进入上下文窗口

```python
# 代理可以编写如下脚本：
from hermes_tools import web_search, web_extract

results = web_search("Python 3.13 features", limit=5)
for r in results["data"]["web"]:
    content = web_extract([r["url"]])
    # ... 过滤和处理 ...
print(summary)
```

**脚本内可用的工具：** `web_search`, `web_extract`, `read_file`, `write_file`, `search_files`, `patch`, `terminal`（仅前台模式）。

## 代理何时使用此功能

当存在以下情况时，代理会使用 `execute_code`：

- **3 次以上工具调用**，且调用之间需要处理逻辑
- 批量数据过滤或条件分支
- 对结果进行循环

关键优势：中间工具结果从不进入上下文窗口——只有最终的 `print()` 输出返回，大幅减少 Token 使用量。

## 实用示例

### 数据处理流水线

```python
from hermes_tools import search_files, read_file
import json

# 查找所有配置文件并提取数据库设置
matches = search_files("database", path=".", file_glob="*.yaml", limit=20)
configs = []
for match in matches.get("matches", []):
    content = read_file(match["path"])
    configs.append({"file": match["path"], "preview": content["content"][:200]})

print(json.dumps(configs, indent=2))
```

### 多步网络调研

```python
from hermes_tools import web_search, web_extract
import json

# 在一次对话中完成搜索、提取和摘要
results = web_search("Rust async runtime comparison 2025", limit=5)
summaries = []
for r in results["data"]["web"]:
    page = web_extract([r["url"]])
    for p in page.get("results", []):
        if p.get("content"):
            summaries.append({
                "title": r["title"],
                "url": r["url"],
                "excerpt": p["content"][:500]
            })

print(json.dumps(summaries, indent=2))
```

### 批量文件重构

```python
from hermes_tools import search_files, read_file, patch

# 查找所有使用已弃用 API 的 Python 文件并修复
matches = search_files("old_api_call", path="src/", file_glob="*.py")
fixed = 0
for match in matches.get("matches", []):
    result = patch(
        path=match["path"],
        old_string="old_api_call(",
        new_string="new_api_call(",
        replace_all=True
    )
    if "error" not in str(result):
        fixed += 1

print(f"Fixed {fixed} files out of {len(matches.get('matches', []))} matches")
```

### 构建与测试流水线

```python
from hermes_tools import terminal, read_file
import json

# 运行测试，解析结果并报告
result = terminal("cd /project && python -m pytest --tb=short -q 2>&1", timeout=120)
output = result.get("output", "")

# 解析测试输出
passed = output.count(" passed")
failed = output.count(" failed")
errors = output.count(" error")

report = {
    "passed": passed,
    "failed": failed,
    "errors": errors,
    "exit_code": result.get("exit_code", -1),
    "summary": output[-500:] if len(output) > 500 else output
}

print(json.dumps(report, indent=2))
```

## 执行模式

`execute_code` 有两种执行模式，由 `~/.hermes/config.yaml` 中的 `code_execution.mode` 控制：

| 模式 | 工作目录 | Python 解释器 |
|------|----------|--------------|
| **`project`**（默认） | 会话的工作目录（与 `terminal()` 相同） | 活动中的 `VIRTUAL_ENV` / `CONDA_PREFIX` 下的 Python，回退到 Hermes 自身的 Python |
| `strict` | 临时暂存目录，与用户项目隔离 | `sys.executable`（Hermes 自身的 Python） |

**何时保持 `project` 模式：** 你希望 `import pandas`、`from my_project import foo` 或相对路径如 `open(".env")` 像在 `terminal()` 中一样工作。这几乎总是你想要的。

**何时切换到 `strict` 模式：** 你需要最大的可重现性——你希望无论用户激活了哪个虚拟环境，每次会话都使用相同的解释器，并且希望脚本与项目树隔离（不会因相对路径意外读取项目文件）。

```yaml
# ~/.hermes/config.yaml
code_execution:
  mode: project   # 或 "strict"
```

`project` 模式下的回退行为：如果 `VIRTUAL_ENV` / `CONDA_PREFIX` 未设置、损坏或指向低于 3.8 的 Python 版本，解析器会干净地回退到 `sys.executable`——它绝不会让代理没有可用的解释器。

两种模式下安全关键的不变属性完全相同：

- 环境清理（API 密钥、令牌、凭据被剥离）
- 工具白名单（脚本不能递归调用 `execute_code`、`delegate_task` 或 MCP 工具）
- 资源限制（超时、标准输出上限、工具调用上限）

切换模式会改变脚本运行的位置以及运行它们的解释器，但不会改变脚本能看到的凭据或能调用的工具。

## 资源限制

| 资源 | 限制 | 说明 |
|------|------|------|
| **超时** | 5 分钟（300 秒） | 脚本先收到 SIGTERM，5 秒宽限期后收到 SIGKILL |
| **标准输出** | 50 KB | 输出被截断，显示 `[output truncated at 50KB]` 提示 |
| **标准错误** | 10 KB | 当退出码非零时包含在输出中，用于调试 |
| **工具调用** | 每次执行 50 次 | 达到限制时返回错误 |

所有限制可通过 `config.yaml` 配置：

```yaml
# 在 ~/.hermes/config.yaml 中
code_execution:
  mode: project      # project（默认）| strict
  timeout: 300       # 每个脚本的最大秒数（默认：300）
  max_tool_calls: 50 # 每次执行的最大工具调用次数（默认：50）
```

## 脚本中的工具调用如何工作

当你的脚本调用诸如 `web_search("query")` 这样的函数时：

1. 调用被序列化为 JSON，通过 Unix 域套接字发送到父进程
2. 父进程通过标准的 `handle_function_call` 处理程序进行调度
3. 结果通过套接字发送回来
4. 函数返回解析后的结果

这意味着脚本内的工具调用与正常工具调用的行为完全相同——相同的速率限制、相同的错误处理、相同的功能。唯一的限制是 `terminal()` 仅支持前台模式（不支持 `background` 或 `pty` 参数）。

## 错误处理

当脚本失败时，代理会收到结构化的错误信息：

- **非零退出码**：标准错误包含在输出中，代理可以看到完整的回溯信息
- **超时**：脚本被杀死，代理看到 `"Script timed out after 300s and was killed."`
- **中断**：如果用户在脚本执行期间发送新消息，脚本会被终止，代理看到 `[execution interrupted — user sent a new message]`
- **工具调用限制**：达到 50 次调用限制后，后续的工具调用会返回错误信息

响应始终包含 `status`（success/error/timeout/interrupted）、`output`、`tool_calls_made` 和 `duration_seconds`。

## 安全性

:::danger 安全模型
子进程在**最小化环境**中运行。默认情况下，API 密钥、令牌和凭据被剥离。脚本仅通过 RPC 通道访问工具——除非明确允许，否则无法从环境变量中读取秘密信息。
:::

名称中包含 `KEY`、`TOKEN`、`SECRET`、`PASSWORD`、`CREDENTIAL`、`PASSWD` 或 `AUTH` 的环境变量会被排除。仅传递安全的系统变量（`PATH`、`HOME`、`LANG`、`SHELL`、`PYTHONPATH`、`VIRTUAL_ENV` 等）。

### 技能（Skill）环境变量透传

当技能在其 frontmatter 中声明了 `required_environment_variables` 时，在技能加载后，这些变量会**自动透传**给 `execute_code` 和 `terminal` 子进程。这使得技能可以使用它们声明的 API 密钥，同时不会削弱任意代码的安全态势。

对于非技能使用场景，你可以在 `config.yaml` 中显式添加白名单变量：

```yaml
terminal:
  env_passthrough:
    - MY_CUSTOM_KEY
    - ANOTHER_TOKEN
```

完整详情请参阅[安全指南](/user-guide/security#environment-variable-passthrough)。

### 子进程中的 `HERMES_*` 变量

子进程仅接收一小部分固定的、操作性的 `HERMES_*` 变量（通过精确名称匹配）：

- `HERMES_HOME`
- `HERMES_PROFILE`
- `HERMES_CONFIG`
- `HERMES_ENV`

（另外还有 `HERMES_RPC_DIR` / `HERMES_RPC_SOCKET` / `TZ` / `HOME`，Hermes 显式注入这些变量以确保 RPC 通道正常工作。）

:::note 行为变更
早期版本会将**任何**名称以 `HERMES_` 开头的变量传递到子进程。出于安全加固考虑，已移除这种宽泛的前缀匹配：它可能将名称不包含秘密关键字的 `HERMES_*` 配置（例如 `HERMES_BASE_URL`、`HERMES_KANBAN_DB` 或 `HERMES_*_WEBHOOK` 端点）泄露到任意沙箱代码中。

如果某个 `execute_code` 脚本——或者它在导入时加载的仓库/插件模块——依赖于上述四个操作性名称之外的 `HERMES_*` 变量，那么该变量在子进程中将**未设置**。这种舍弃是有意为之，并非缺陷。
:::

**解决方案——显式重新引入该变量。** 两种途径都可以将变量透传给 `execute_code` *和* `terminal` 子进程，并且两者都不会削弱密钥剥离保证（Hermes 管理的提供者凭据永远不能通过这种方式重新允许）：

1. **每台机器上，在 `config.yaml` 中**——将确切的变量名称添加到透传白名单：

   ```yaml
   terminal:
     env_passthrough:
       - HERMES_KANBAN_DB
       - HERMES_BASE_URL
   ```

2. **每个技能中，在技能 frontmatter 中**——声明该变量，这样每当技能加载时就会自动注册：

   ```yaml
   required_environment_variables:
     - HERMES_KANBAN_DB
   ```

**诊断方法。** 当子进程丢弃了一个或多个未在白名单中的 `HERMES_*` 变量时，Hermes 会输出一行 `debug` 日志，指明这些变量并指向 `env_passthrough` 转义通道。使用调试日志运行（`hermes logs --level DEBUG`，或查看 `~/.hermes/logs/agent.log`），如果脚本表现异常（好像缺少某个 `HERMES_*` 变量），请查找 `execute_code: dropped N non-allowlisted HERMES_* var(s)`。

Hermes 始终将脚本和自动生成的 `hermes_tools.py` RPC 存根写入临时暂存目录，该目录在执行后会被清理。在 `strict` 模式下，脚本也在该目录下运行；在 `project` 模式下，它在会话的工作目录中运行（暂存目录保留在 `PYTHONPATH` 上，因此导入仍然有效）。子进程在自己的进程组中运行，以便在超时或中断时可以被干净地杀死。

## execute_code 与 terminal 对比

| 使用场景 | execute_code | terminal |
|----------|-------------|----------|
| 多步工作流，之间包含工具调用 | ✅ | ❌ |
| 简单的 shell 命令 | ❌ | ✅ |
| 过滤/处理大量工具输出 | ✅ | ❌ |
| 运行构建或测试套件 | ❌ | ✅ |
| 对搜索结果循环处理 | ✅ | ❌ |
| 交互式/后台进程 | ❌ | ✅ |
| 环境中需要 API 密钥 | ⚠️ 仅通过[透传](/user-guide/security#environment-variable-passthrough) | ✅（大部分透传） |

**经验法则：** 当需要在调用之间使用逻辑调用 Hermes 工具时，使用 `execute_code`。当需要运行 shell 命令、构建和进程时，使用 `terminal`。

## 平台支持

代码执行需要 Unix 域套接字，仅在 **Linux 和 macOS 上可用**。在 Windows 上会自动禁用——代理会回退到常规的顺序工具调用。