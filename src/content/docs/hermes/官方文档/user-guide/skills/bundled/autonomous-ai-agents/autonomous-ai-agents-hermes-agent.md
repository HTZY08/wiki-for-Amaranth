---
title: Hermes Agent
---

## 贡献者快速参考

适用于偶尔贡献者和 PR 作者。完整的开发者文档：https://hermes-agent.nousresearch.com/docs/developer-guide/

### 项目布局

<!-- ascii-guard-ignore -->
```
hermes-agent/
├── run_agent.py          # AIAgent — 核心对话循环
├── model_tools.py        # 工具发现与调度
├── toolsets.py           # 工具集定义
├── cli.py                # 交互式 CLI (HermesCLI)
├── hermes_state.py       # SQLite 会话存储
├── agent/                # 提示构建、上下文压缩、记忆、模型路由、凭据池、技能调度
├── hermes_cli/           # CLI 子命令、配置、设置、命令
│   ├── commands.py       # 斜杠命令注册表 (CommandDef)
│   ├── config.py         # DEFAULT_CONFIG、环境变量定义
│   └── main.py           # CLI 入口点和 argparse
├── tools/                # 每个工具一个文件
│   └── registry.py       # 中心工具注册表
├── gateway/              # 消息网关
│   └── platforms/        # 平台适配器 (telegram, discord 等)
├── cron/                 # 作业调度器
├── tests/                # 约 3000 个 pytest 测试
└── website/              # Docusaurus 文档站点
```
<!-- ascii-guard-ignore-end -->

配置：`~/.hermes/config.yaml`（设置）、`~/.hermes/.env`（API 密钥）——当设置了 `$HERMES_HOME` 时，两者都在 `$HERMES_HOME` 下。

### 添加一个工具（涉及 3 个文件）

**1. 创建 `tools/your_tool.py`：**
```python
import json, os
from tools.registry import registry

def check_requirements() -> bool:
    return bool(os.getenv("EXAMPLE_API_KEY"))

def example_tool(param: str, task_id: str = None) -> str:
    return json.dumps({"success": True, "data": "..."})

registry.register(
    name="example_tool",
    toolset="example",
    schema={"name": "example_tool", "description": "...", "parameters": {...}},
    handler=lambda args, **kw: example_tool(
        param=args.get("param", ""), task_id=kw.get("task_id")),
    check_fn=check_requirements,
    requires_env=["EXAMPLE_API_KEY"],
)
```

**2. 添加到 `toolsets.py`** → 在 `_HERMES_CORE_TOOLS` 列表中。

自动发现：任何 `tools/*.py` 文件，如果包含顶层的 `registry.register()` 调用，都会被自动导入——无需手动添加。

所有处理器（handler）必须返回 JSON 字符串。使用 `get_hermes_home()` 获取路径，切勿硬编码 `~/.hermes`。

### 添加一个斜杠命令

1. 在 `hermes_cli/commands.py` 的 `COMMAND_REGISTRY` 中添加 `CommandDef`
2. 在 `cli.py` 的 `process_command()` 中添加处理器
3. （可选）在 `gateway/run.py` 中添加网关处理器

所有消费者（帮助文本、自动补全、Telegram 菜单、Slack 映射）都会自动从中心注册表派生。

### 代理循环（高级）

```
run_conversation():
  1. 构建系统提示（system prompt）
  2. 当迭代次数 < 最大值时循环：
     a. 调用 LLM（OpenAI 格式消息 + 工具结构）
     b. 如果有 tool_calls → 通过 handle_function_call() 调度每个调用 → 追加结果 → 继续
     c. 如果是文本响应 → 返回
  3. 接近令牌限制时自动触发上下文压缩
```

### 测试

```bash
python -m pytest tests/ -o 'addopts=' -q   # 全量测试套件
python -m pytest tests/tools/ -q            # 特定区域
```

- 测试会自动将 `HERMES_HOME` 重定向到临时目录——绝不会触碰真实的 `~/.hermes/`
- 提交任何更改前请运行全量测试套件
- 使用 `-o 'addopts='` 清除任何内置的 pytest 标志

**Windows 贡献者：** `scripts/run_tests.sh` 当前仅查找 POSIX 虚拟环境（`.venv/bin/activate` / `venv/bin/activate`），在 Windows 上布局是 `venv/Scripts/activate` + `python.exe`，因此会报错。Hermes 安装在 `venv/Scripts/` 下的虚拟环境没有 `pip` 或 `pytest`——为了减小最终用户的安装体积已被精简。解决方法：将 pytest + pytest-xdist + pyyaml 安装到系统 Python 3.11 的用户站点中（`/c/Program Files/Python311/python -m pip install --user pytest pytest-xdist pyyaml`），然后直接运行测试：

```bash
export PYTHONPATH="$(pwd)"
"/c/Program Files/Python311/python" -m pytest tests/tools/test_foo.py -v --tb=short -n 0
```

使用 `-n 0`（而不是 `-n 4`），因为 `pyproject.toml` 的默认 `addopts` 已经包含了 `-n`，并且包装脚本的 CI 一致性逻辑不适用于非 POSIX 环境。

**跨平台测试保护：** 使用仅适用于 POSIX 系统调用的测试需要添加跳过标记。代码库中常见的例子：
- 符号链接创建 → `@pytest.mark.skipif(sys.platform == "win32", reason="Symlinks require elevated privileges on Windows")`（见 `tests/cron/test_cron_script.py`）
- POSIX 文件模式（0o600 等） → `@pytest.mark.skipif(sys.platform.startswith("win"), reason="POSIX mode bits not enforced on Windows")`（见 `tests/hermes_cli/test_auth_toctou_file_modes.py`）
- `signal.SIGALRM` → 仅 Unix（见 `tests/conftest.py::_enforce_test_timeout`）
- 实时的 Winsock / Windows 特定回归测试 → `@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific regression")`

**仅 monkeypatch `sys.platform` 是不够的**，当被测试代码还调用了 `platform.system()` / `platform.release()` / `platform.mac_ver()` 时。这些函数会独立地重新读取真实的 OS 信息，因此在 Windows 运行器上设置 `sys.platform = "linux"` 后，被测试代码仍然会看到 `platform.system() == "Windows"` 并走 Windows 分支。需要同时修补这三个：

```python
monkeypatch.setattr(sys, "platform", "linux")
monkeypatch.setattr(platform, "system", lambda: "Linux")
monkeypatch.setattr(platform, "release", lambda: "6.8.0-generic")
```

参见 `tests/agent/test_prompt_builder.py::TestEnvironmentHints` 中的完整示例。

### 扩展系统提示中的执行环境块

关于主机操作系统、用户主目录、当前工作目录、终端后端和 shell（Windows 下是 bash 还是 PowerShell）的事实性指导信息，由 `agent/prompt_builder.py::build_environment_hints()` 发出。WSL 提示和每个后端的探测逻辑也在这里。约定如下：

- **本地终端后端** → 输出主机信息（操作系统、`$HOME`、当前工作目录）+ Windows 特定说明（主机名 ≠ 用户名，`terminal` 使用 bash 而不是 PowerShell）。
- **远程终端后端**（属于 `_REMOTE_TERMINAL_BACKENDS` 的任何一种：`docker, singularity, modal, daytona, ssh, managed_modal`） → **抑制**主机信息，仅描述后端。在后端内部通过 `tools.environments.get_environment(...).execute(...)` 执行实时的 `uname`/`whoami`/`pwd` 探测，结果按进程缓存在 `_BACKEND_PROBE_CACHE` 中，如果探测超时则使用静态回退值。
- **编写提示时的重要事实：** 当 `TERMINAL_ENV != "local"` 时，*每个*文件工具（`read_file`、`write_file`、`patch`、`search_files`）都在后端容器内运行，而不是在主机上。系统提示（system prompt）在这种情况下绝不能描述主机——代理根本无法触及主机。

完整的设计说明、确切的输出字符串以及测试陷阱：
`references/prompt-builder-environment-hints.md`。

**重构安全性模式（POSIX 等价性保护）：** 当你将内联逻辑提取到添加 Windows/平台特定行为的辅助函数中时，在测试文件中保留一个 `_legacy_<名称>` 预言函数，它是旧代码的逐字副本，然后通过参数化进行差异比较。示例：`tests/tools/test_code_execution_windows_env.py::TestPosixEquivalence`。这样可以锁定 POSIX 行为完全一致的恒等式，任何未来的偏差都会以清晰的差异失败并发出警告。

### 提交约定

```
type: concise subject line

Optional body.
```

类型：`fix:`、`feat:`、`refactor:`、`docs:`、`chore:`

### 关键规则

- **绝不能破坏提示缓存（prompt caching）** ——不要在对话中途更改上下文、工具或系统提示
- **消息角色交替** ——不能连续出现两条助手（assistant）消息或两条用户（user）消息
- 所有路径使用 `hermes_constants` 中的 `get_hermes_home()`（配置文件安全）
- 配置值放在 `config.yaml` 中，密钥放在 `.env` 中
- 新工具需要提供 `check_fn`，以便仅在满足要求时出现