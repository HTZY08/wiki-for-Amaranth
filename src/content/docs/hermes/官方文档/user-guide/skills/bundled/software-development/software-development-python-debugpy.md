--- frontmatter ---
---
title: "Python Debugpy — 调试 Python：pdb REPL + debugpy 远程（DAP）"
sidebar_label: "Python Debugpy"
description: "调试 Python：pdb REPL + debugpy 远程（DAP）"
---

--- body ---
--- body ---
{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Python Debugpy

调试 Python：pdb REPL + debugpy 远程（DAP）。

## 技能元数据（Skill metadata）

| | |
|---|---|
| 来源（Source） | 内置（默认安装） |
| 路径（Path） | `skills/software-development/python-debugpy` |
| 版本（Version） | `1.0.0` |
| 作者（Author） | Hermes Agent |
| 许可证（License） | MIT |
| 平台（Platforms） | linux, macos |
| 标签（Tags） | `debugging`, `python`, `pdb`, `debugpy`, `breakpoints`, `dap`, `post-mortem` |
| 相关技能（Related skills） | [`systematic-debugging`](/docs/user-guide/skills/bundled/software-development/software-development-systematic-debugging), [`node-inspect-debugger`](/docs/user-guide/skills/bundled/software-development/software-development-node-inspect-debugger), `debugging-hermes-tui-commands` |

## 参考：完整 SKILL.md

:::info
以下为 Hermes 在该技能被触发时加载的完整技能定义。这是技能激活时代理所见的指令内容。
:::

# Python 调试器（pdb + debugpy）

## 概述

三种工具，根据具体情况选用：

| 工具（Tool） | 使用场景（When） |
|---|---|
| **`breakpoint()` + pdb** | 本地、交互式、最简单。在源码中添加 `breakpoint()`，正常运行，即可在该行获得 REPL。 |
| **`python -m pdb`** | 以 pdb 启动现有脚本，无需修改源码。适用于快速探查。 |
| **`debugpy`** | 远程 / 无头 / "附加到正在运行的进程"。使用 DAP 协议，可通过终端脚本化，适用于长期运行的进程（网关、守护进程、PTY 子进程）。 |

**从 `breakpoint()` 开始。** 这是最简便且有效的方法。

## 何时使用

- 测试失败，但回溯信息无法揭示某个值错误的原因
- 需要单步执行函数并观察集合的修改情况
- 长期运行的进程（hermes gateway, tui_gateway）行为异常且无法重启
- 事后调试（post-mortem）：生产代码中发生异常，希望在崩溃点检查局部变量
- 子进程 / 子项（`_SlashWorker`, PTY 桥 worker）是实际 bug 所在点

**不适用于：** `print()` / `logging.debug` 在一分钟内就能解决的问题，或 `pytest -vv --tb=long --showlocals` 已经揭示的情况。

## pdb 快速参考

在任何 pdb 提示符 (`(Pdb)`) 下：

| 命令（Command） | 作用（Action） |
|---|---|
| `h` / `h cmd` | 帮助 |
| `n` | 下一行（单步跳过） |
| `s` | 步入 |
| `r` | 从当前函数返回 |
| `c` | 继续执行 |
| `unt N` | 继续执行直到第 N 行 |
| `j N` | 跳转到第 N 行（仅限同一函数） |
| `l` / `ll` | 列出当前行附近的源码 / 完整函数 |
| `w` | 在哪里（堆栈跟踪） |
| `u` / `d` | 在堆栈中向上 / 向下移动 |
| `a` | 打印当前函数的参数 |
| `p expr` / `pp expr` | 打印 / 漂亮打印表达式 |
| `display expr` | 每次停止时自动打印表达式 |
| `b file:line` | 设置断点 |
| `b func` | 在函数入口设置断点 |
| `b file:line, cond` | 条件断点 |
| `cl N` | 清除第 N 个断点 |
| `tbreak file:line` | 一次性断点 |
| `!stmt` | 执行任意 Python 代码（包括赋值） |
| `interact` | 在当前作用域内进入完整的 Python REPL（Ctrl+D 退出） |
| `q` | 退出 |

`interact` 命令最为强大——你可以导入任何内容，检查复杂对象，甚至调用会修改状态的方法。局部变量默认只读；在 `(Pdb)` 提示符下使用 `!x = 42` 进行修改。

## 方案 1：本地断点 (breakpoint)

最简单。编辑文件：

```python
def compute(x, y):
    result = some_helper(x)
    breakpoint()           # <-- 在此处进入 pdb
    return result + y
```

正常运行代码。你将停在与 `breakpoint()` 所在行，可以完全访问局部变量。

**提交前不要忘记删除 `breakpoint()`。** 使用 `git diff` 或提交前 grep：
```bash
rg -n 'breakpoint\(\)' --type py
```

## 方案 2：在 pdb 下启动脚本（无需修改源码）

```bash
python -m pdb path/to/script.py arg1 arg2
# 在脚本的第一行停止
(Pdb) b path/to/script.py:42
(Pdb) c
```

## 方案 3：调试 pytest 测试

Hermes 测试运行器和 pytest 均支持此方法：

```bash
# 在失败时（或任何抛出的异常）进入 pdb：
scripts/run_tests.sh tests/path/to/test_file.py::test_name --pdb

# 在测试开始时进入 pdb：
scripts/run_tests.sh tests/path/to/test_file.py::test_name --trace

# 显示回溯中的局部变量，不进入 pdb：
scripts/run_tests.sh tests/path/to/test_file.py --showlocals --tb=long
```

注意：`scripts/run_tests.sh` 默认使用 xdist（`-n 4`），而 pdb 在 xdist 下无法工作。添加 `-p no:xdist` 或使用 `-n 0` 运行单个测试：

```bash
scripts/run_tests.sh tests/foo_test.py::test_bar --pdb -p no:xdist
# 或
source .venv/bin/activate
python -m pytest tests/foo_test.py::test_bar --pdb
```

这样会绕过封闭环境保证——适用于调试，但在推送前需在包装器下重新运行确认。

## 方案 4：任何异常的事后调试（Post-mortem）

```python
import pdb, sys
try:
    run_the_thing()
except Exception:
    pdb.post_mortem(sys.exc_info()[2])
```

或者包装整个脚本：

```bash
python -m pdb -c continue script.py
# 当崩溃时，pdb 捕获它，你停留在异常的帧中
```

或者在 repl/jupyter 中设置全局钩子：

```python
import sys
def excepthook(etype, value, tb):
    import pdb; pdb.post_mortem(tb)
sys.excepthook = excepthook
```

## 方案 5：使用 debugpy 远程调试（附加到正在运行的进程）

适用于长期运行的进程：Hermes gateway, tui_gateway, 守护进程，以及已经行为异常且无法正常重启的进程。

### 设置

```bash
source /home/bb/hermes-agent/.venv/bin/activate
pip install debugpy
```

### 模式 A：修改源码——进程在启动时等待调试器

在入口点顶部（或要调试的函数内部）添加：

```python
import debugpy
debugpy.listen(("127.0.0.1", 5678))
print("debugpy listening on 5678, waiting for client...", flush=True)
debugpy.wait_for_client()
debugpy.breakpoint()       # 可选：在附加后立即暂停
```

启动进程；它会在 `wait_for_client()` 处阻塞。

### 模式 B：不修改源码——使用 `-m debugpy` 启动

```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client your_script.py arg1
```

模块入口的等效命令：

```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client -m your.module
```

### 模式 C：附加到已运行的进程

需要 PID 且 debugpy 已预先安装在目标环境中：

```bash
python -m debugpy --listen 127.0.0.1:5678 --pid <pid>
# debugpy 将自身注入到进程中。然后如下附加客户端。
```

某些内核/安全配置会阻止基于 ptrace 的注入（`/proc/sys/kernel/yama/ptrace_scope`）。修复方式：
```bash
echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope
```

### 从终端连接客户端

最简单的终端侧 DAP 客户端是 VS Code CLI 或一个小脚本。在 Hermes 内部，你有两个实用选项：

**选项 1：`debugpy` 自身的 CLI REPL**——不是官方功能，而是一个小型 DAP 客户端脚本：

```python
# /tmp/dap_client.py
import socket, json, itertools, time, sys

HOST, PORT = "127.0.0.1", 5678
s = socket.create_connection((HOST, PORT))
seq = itertools.count(1)

def send(msg):
    msg["seq"] = next(seq)
    body = json.dumps(msg).encode()
    s.sendall(f"Content-Length: {len(body)}\r\n\r\n".encode() + body)

def recv():
    header = b""
    while b"\r\n\r\n" not in header:
        header += s.recv(1)
    length = int(header.decode().split("Content-Length:")[1].split("\r\n")[0].strip())
    body = b""
    while len(body) < length:
        body += s.recv(length - len(body))
    return json.loads(body)

send({"type": "request", "command": "initialize", "arguments": {"adapterID": "python"}})
print(recv())
send({"type": "request", "command": "attach", "arguments": {}})
print(recv())
send({"type": "request", "command": "setBreakpoints",
      "arguments": {"source": {"path": sys.argv[1]},
                    "breakpoints": [{"line": int(sys.argv[2])}]}})
print(recv())
send({"type": "request", "command": "configurationDone"})
# ... 循环读取事件并发送 continue/stepIn 等
```

这对于一次性自动化不错，但作为交互式用户体验来说很痛苦。

**选项 2：从 VS Code / Cursor / Zed 附加**——如果用户打开了其中一个，可以添加一个 `launch.json`：

```json
{
  "name": "Attach to Hermes",
  "type": "debugpy",
  "request": "attach",
  "connect": { "host": "127.0.0.1", "port": 5678 },
  "justMyCode": false,
  "pathMappings": [
    { "localRoot": "${workspaceFolder}", "remoteRoot": "/home/bb/hermes-agent" }
  ]
}
```

**选项 3：放弃 DAP，使用 `remote-pdb`**——通常这才是终端代理真正需要的：

```bash
pip install remote-pdb
```

在代码中：
```python
from remote_pdb import set_trace
set_trace(host="127.0.0.1", port=4444)   # 阻塞直到连接
```

然后从终端：
```bash
nc 127.0.0.1 4444
# 你会得到一个 (Pdb) 提示符，就像本地调试一样。
```

当 `debugpy` 的 DAP 协议过于复杂时，`remote-pdb` 是最简洁且友好的代理选择。仅在确实需要 IDE 集成时才使用 `debugpy`。

## 调试 Hermes 特定进程

### 测试
参见方案 3。始终添加 `-p no:xdist` 或无需 xdist 运行单个测试。

### `run_agent.py` / CLI——一次性运行
最简单：在可疑行附近添加 `breakpoint()`，然后正常运行 `hermes`。在暂停点控制权会返回给你的终端。

### `tui_gateway` 子进程（由 `hermes --tui` 派生）
网关作为 Node TUI 的子进程运行。选项：

**A. 修改网关源码：**
```python
# tui_gateway/server.py 在 serve() 顶部附近
import debugpy
debugpy.listen(("127.0.0.1", 5678))
debugpy.wait_for_client()
```
启动 `hermes --tui`。TUI 会看起来冻结（其后端正在等待）。附加一个客户端；当你 `continue` 后执行恢复。

**B. 在特定处理程序中使用 `remote-pdb`：**
```python
from remote_pdb import set_trace
set_trace(host="127.0.0.1", port=4444)   # 在你要捕获的 RPC 处理程序中
```
从 TUI 触发对应的斜杠命令，然后在另一个终端中执行 `nc 127.0.0.1 4444`。

### `_SlashWorker` 子进程
相同模式——在 worker 的 `exec` 路径内使用 `remote-pdb` 的 `set_trace()`。worker 在斜杠命令之间保持持久，因此第一次触发会阻塞直到你连接；除非重新激活，后续的斜杠命令将正常通过。

### 网关（`gateway/run.py`）
长期运行。在处理程序中使用 `remote-pdb`，或者如果你无论如何都要重启网关，则使用带 `--wait-for-client` 的 `debugpy`。

## 常见陷阱

1. **pdb 在 pytest-xdist 下静默地什么都不做。** 你不会看到提示符，测试只会挂起。始终使用 `-p no:xdist` 或 `-n 0`。

2. **`breakpoint()` 在 CI / 非 TTY 上下文中会挂起进程。** 只在本地安全；切勿提交。添加一个提交前 grep 作为安全网。

3. **`PYTHONBREAKPOINT=0`** 禁用所有 `breakpoint()` 调用。如果你的断点未命中，检查环境变量：
   ```bash
   echo $PYTHONBREAKPOINT
   ```

4. **`debugpy.listen` 仅在你同时调用 `wait_for_client()` 时才会阻塞。** 没有它，执行会继续，你的第一个断点可能在客户端附加之前触发。

5. **在强化内核上附加 PID 会失败。** `ptrace_scope=1`（Ubuntu 默认）只允许同一用户对子进程进行 ptrace。解决方法：`echo 0 > /proc/sys/kernel/yama/ptrace_scope`（需要 root）或从一开始就用 `debugpy` 启动。

6. **线程。** `pdb` 仅调试当前线程。对于多线程代码，使用 `debugpy`（线程感知的 DAP）或为每个线程设置 `threading.settrace()`。

7. **asyncio。** `pdb` 可以在协程中工作，但在 pdb 内部使用 `await` 需要 Python 3.13+，或在旧版本上通过 `interact` 模式使用 `await`。对于 3.11/3.12，使用 `asyncio.run_coroutine_threadsafe` 技巧或通过 `asyncio.ensure_future` 基于 `!stmt` 的 await。

8. **`scripts/run_tests.sh` 会剥离凭据并设置 `HOME=<tmpdir>`。** 如果你的 bug 依赖于用户配置或真实 API 密钥，它不会在包装器下重现。首先使用原始 `pytest` 调试以重现，然后在包装器下重新确认。

9. **Fork / multiprocessing。** pdb 不会跟随 fork。每个子进程需要自己的 `breakpoint()` 或 `set_trace()`。对于 Hermes 子代理，一次调试一个进程。

## 验证清单

- [ ] 安装 `pip install debugpy` 后，确认：`python -c "import debugpy; print(debugpy.__version__)"`
- [ ] 对于远程调试，确认端口确实在监听：`ss -tlnp | grep 5678`
- [ ] 第一个断点确实触发了（如果没触发，可能是 `PYTHONBREAKPOINT=0`、你在 xdist 下，或执行在附加前已完成）
- [ ] `where` / `w` 显示预期的调用栈
- [ ] 调试后清理：提交的代码中没有残留的 `breakpoint()` / `set_trace()`
  ```bash
  rg -n 'breakpoint\(\)|set_trace\(|debugpy\.listen' --type py
  ```

## 一次性使用方案

**“这个 dict 为什么缺少一个 key？”**
```python
# 在 KeyError 位置上方添加
breakpoint()
# 然后在 pdb 中：
(Pdb) pp d
(Pdb) pp list(d.keys())
(Pdb) w                # 我们是怎么到这里来的
```

**“这个测试单独通过但在套件中失败。”**
```bash
scripts/run_tests.sh tests/the_test.py --pdb -p no:xdist
# 但如果它只与其他测试一起失败：
source .venv/bin/activate
python -m pytest tests/ -x --pdb -p no:xdist
# 现在它会在积累状态后刚好在失败的测试处进入 pdb 陷阱。
```

**“我的异步处理程序死锁了。”**
```python
# 在处理程序入口添加
import remote_pdb; remote_pdb.set_trace(host="127.0.0.1", port=4444)
```
触发处理程序。执行 `nc 127.0.0.1 4444`，然后 `w` 查看挂起的帧，`!import asyncio; asyncio.all_tasks()` 查看还有哪些任务等待中。

**“Ink 子进程 / 子进程崩溃后的事后调试。”**
```bash
PYTHONFAULTHANDLER=1 python -m pdb -c continue path/to/entrypoint.py
# 崩溃时，pdb 停留在异常的帧中，并包含完整的局部变量
```