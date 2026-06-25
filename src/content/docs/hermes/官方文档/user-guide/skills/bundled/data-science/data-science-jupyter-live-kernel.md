---
title: Jupyter Live Kernel
---

title: "Jupyter Live Kernel — 通过实时 Jupyter 内核进行迭代 Python 编程 (hamelnb)"
sidebar_label: "Jupyter Live Kernel"
description: "通过实时 Jupyter 内核进行迭代 Python 编程 (hamelnb)"
---

--- body ---
{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Jupyter Live Kernel

通过实时 Jupyter 内核（Jupyter kernel）进行迭代 Python 编程（hamelnb）。

## 技能元数据（Skill metadata）

| | |
|---|---|
| 来源（Source） | 捆绑（默认安装） |
| 路径（Path） | `skills/data-science/jupyter-live-kernel` |
| 版本（Version） | `1.0.0` |
| 作者（Author） | Hermes Agent |
| 许可证（License） | MIT |
| 平台（Platforms） | linux, macos, windows |
| 标签（Tags） | `jupyter`, `notebook`, `repl`, `data-science`, `exploration`, `iterative` |

## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发该技能时加载的完整技能定义。这是代理（Agent）在技能激活时看到的指令。
:::

# Jupyter Live Kernel (hamelnb)

通过实时 Jupyter 内核（Jupyter kernel）为您提供一个**有状态的 Python REPL（stateful Python REPL）**。变量在多次执行之间持续存在。当您需要增量构建状态、探索 API、检查 DataFrame 或迭代复杂代码时，请使用此技能代替 `execute_code`。

## 何时使用此技能与其他工具

| 工具（Tool） | 使用场景（Use When） |
|------|----------|
| **本技能（This skill）** | 迭代探索、跨步骤状态、数据科学、机器学习、“让我试试这个并检查一下” |
| `execute_code` | 需要 hermes 工具访问（web_search、文件操作）的一次性脚本。无状态。 |
| `terminal` | Shell 命令、构建、安装、git、进程管理 |

**经验法则：** 如果您希望为此任务使用 Jupyter notebook，请使用此技能。

## 前置条件（Prerequisites）

1. **必须安装 uv**（检查：`which uv`）
2. **必须安装 JupyterLab**：`uv tool install jupyterlab`
3. 必须运行一个 Jupyter 服务器（参见下方设置）

## 设置（Setup）

hamelnb 脚本位置：
```
SCRIPT="$HOME/.agent-skills/hamelnb/skills/jupyter-live-kernel/scripts/jupyter_live_kernel.py"
```

如果尚未克隆：
```
git clone https://github.com/hamelsmu/hamelnb.git ~/.agent-skills/hamelnb
```

### 启动 JupyterLab

检查服务器是否已在运行：
```
uv run "$SCRIPT" servers
```

如果未找到服务器，启动一个：
```
jupyter-lab --no-browser --port=8888 --notebook-dir=$HOME/notebooks \
  --IdentityProvider.token='' --ServerApp.password='' > /tmp/jupyter.log 2>&1 &
sleep 3
```

注意：为本地代理访问禁用了令牌/密码。服务器以无界面（headless）模式运行。

### 创建用于 REPL 的 Notebook

如果您仅需要一个 REPL（无需现有 notebook），请创建一个最小的 notebook 文件：
```
mkdir -p ~/notebooks
```
写入一个包含一个空代码单元格的最小 .ipynb JSON 文件，然后通过 Jupyter REST API 启动一个内核会话（kernel session）：
```
curl -s -X POST http://127.0.0.1:8888/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"path":"scratch.ipynb","type":"notebook","name":"scratch.ipynb","kernel":{"name":"python3"}}'
```

## 核心工作流（Core Workflow）

所有命令均返回结构化 JSON。始终使用 `--compact` 以节省令牌（tokens）。

### 1. 发现服务器和 notebook

```
uv run "$SCRIPT" servers --compact
uv run "$SCRIPT" notebooks --compact
```

### 2. 执行代码（主要操作）

```
uv run "$SCRIPT" execute --path <notebook.ipynb> --code '<python code>' --compact
```

状态在多次执行调用之间持续存在。变量、导入、对象均保留。

多行代码可通过 `$'...'` 引用实现：
```
uv run "$SCRIPT" execute --path scratch.ipynb --code $'import os\nfiles = os.listdir(".")\nprint(f"Found {len(files)} files")' --compact
```

### 3. 检查实时变量（Inspect live variables）

```
uv run "$SCRIPT" variables --path <notebook.ipynb> list --compact
uv run "$SCRIPT" variables --path <notebook.ipynb> preview --name <varname> --compact
```

### 4. 编辑 notebook 单元格（Edit notebook cells）

```
# 查看当前单元格
uv run "$SCRIPT" contents --path <notebook.ipynb> --compact

# 插入新单元格
uv run "$SCRIPT" edit --path <notebook.ipynb> insert \
  --at-index <N> --cell-type code --source '<code>' --compact

# 替换单元格源（使用 contents 输出中的 cell-id）
uv run "$SCRIPT" edit --path <notebook.ipynb> replace-source \
  --cell-id <id> --source '<new code>' --compact

# 删除单元格
uv run "$SCRIPT" edit --path <notebook.ipynb> delete --cell-id <id> --compact
```

### 5. 验证（Verification）：重新启动并运行所有单元格（restart + run all）

仅当用户要求进行干净验证，或您需要确认 notebook 能从头到尾运行时使用：
```
uv run "$SCRIPT" restart-run-all --path <notebook.ipynb> --save-outputs --compact
```

## 实践经验（Practical Tips from Experience）

1. **服务器启动后的首次执行可能超时**——内核需要一点时间初始化。如果遇到超时，只需重试。

2. **内核 Python 是 JupyterLab 的 Python**——必须在该环境中安装包。如果您需要额外包，请先将其安装到 JupyterLab 工具环境中。

3. **--compact 标志可显著节省令牌**——始终使用它。不使用该标志时，JSON 输出会非常冗长。

4. **对于纯 REPL 使用**，创建一个 scratch.ipynb，无需理会单元格编辑。只需重复使用 `execute`。

5. **参数顺序很重要**——子命令标志如 `--path` 应放在子子命令之前。例如：`variables --path nb.ipynb list`，而不是 `variables list --path nb.ipynb`。

6. **如果会话（session）尚未存在**，您需要通过 REST API 启动一个（参见设置部分）。没有实时内核会话，工具无法执行。

7. **错误以 JSON 形式返回并附带回溯（traceback）**——阅读 `ename` 和 `evalue` 字段以了解出了什么问题。

8. **偶尔的 WebSocket 超时**——某些操作在首次尝试时可能超时，尤其是在内核重启之后。先重试一次，不要立即升级问题。

## 超时默认值（Timeout Defaults）

该脚本每次执行默认超时时间为 30 秒。对于长时间运行的操作，请传递 `--timeout 120`。对于初始设置或繁重计算，请使用慷慨的超时值（60 秒以上）。