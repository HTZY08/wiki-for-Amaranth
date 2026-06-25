--- frontmatter ---
---
sidebar_position: 1
title: "工具与工具集"
description: "Hermes 代理工具的概览——可用工具、工具集工作原理及终端后端"
---

--- body ---
# 工具与工具集

工具（Tool）是扩展代理（Agent）能力的函数。它们被组织成逻辑上的**工具集（Toolset）**，可以按平台启用或禁用。

## 可用工具

Hermes 附带一个广泛的内置工具注册表，涵盖网页搜索、浏览器自动化、终端执行、文件编辑、记忆、委派、强化学习训练、消息投递、Home Assistant 等。

:::note
**Honcho 跨会话记忆**作为记忆提供者插件（`plugins/memory/honcho/`）提供，不是内置工具集。安装请参见[插件](./plugins.md)。
:::

高层分类：

| 分类 | 示例 | 描述 |
|----------|----------|-------------|
| **Web** | `web_search`, `web_extract` | 搜索网页并提取页面内容。 |
| **X 搜索** | `x_search` | 通过 xAI 内置的 `x_search` 响应工具搜索 X（Twitter）帖子与话题——需 xAI 凭据（SuperGrok OAuth 或 `XAI_API_KEY`）；默认关闭，通过 `hermes tools` → 🐦 X（Twitter）搜索手动开启。 |
| **终端与文件** | `terminal`, `process`, `read_file`, `patch` | 执行命令和操作文件。 |
| **浏览器** | `browser_navigate`, `browser_snapshot`, `browser_vision` | 支持文本和视图的交互式浏览器自动化。 |
| **媒体** | `vision_analyze`, `image_generate`, `text_to_speech` | 多模态分析与生成。 |
| **代理编排** | `todo`, `clarify`, `execute_code`, `delegate_task` | 规划、澄清、代码执行和子代理委派。 |
| **记忆与回忆** | `memory`, `session_search` | 持久化记忆和会话搜索。 |
| **自动化与投递** | `cronjob`, `send_message` | 支持创建/列出/更新/暂停/恢复/运行/移除操作的定时任务，以及外发消息投递。 |
| **集成** | `ha_*`, MCP 服务器工具 | Home Assistant、MCP 及其他集成。 |

权威的代码派生注册表请参见[内置工具参考](/reference/tools-reference)和[工具集参考](/reference/toolsets-reference)。

:::tip Nous 工具网关
付费 [Nous Portal](https://portal.nousresearch.com) 订阅用户可通过 **[工具网关](tool-gateway.md)** 使用网页搜索、图片生成、TTS 和浏览器自动化——无需单独 API 密钥。运行 `hermes model` 启用，或通过 `hermes tools` 单独配置工具。
:::

## 使用工具集

```bash
# 使用特定工具集
hermes chat --toolsets "web,terminal"

# 查看所有可用工具
hermes tools

# 按平台交互式配置工具
hermes tools
```

常见的工具集包括 `web`, `search`, `terminal`, `file`, `browser`, `vision`, `image_gen`, `moa`, `skills`, `tts`, `todo`, `memory`, `session_search`, `cronjob`, `code_execution`, `delegation`, `clarify`, `homeassistant`, `messaging`, `spotify`, `discord`, `discord_admin`, `debugging`, 和 `safe`。

完整列表请参见[工具集参考](/reference/toolsets-reference)，包括平台预设（如 `hermes-cli`、`hermes-telegram`）以及动态 MCP 工具集（如 `mcp-<server>`）。

## 终端后端

终端工具可以在不同环境中执行命令：

| 后端 | 描述 | 使用场景 |
|---------|-------------|----------|
| `local` | 在本地机器上运行（默认） | 开发、信任任务 |
| `docker` | 隔离容器 | 安全、可复现性 |
| `ssh` | 远程服务器 | 沙盒化、避免代理接触自身代码 |
| `singularity` | HPC 容器 | 集群计算、无根环境 |
| `modal` | 云端执行 | 无服务器、可伸缩 |
| `daytona` | 云端沙盒工作区 | 持久化远程开发环境 |

### 配置

```yaml
# 在 ~/.hermes/config.yaml 中
terminal:
  backend: local    # 或: docker, ssh, singularity, modal, daytona
  cwd: "."          # 工作目录
  timeout: 180      # 命令超时秒数
```

### Docker 后端

```yaml
terminal:
  backend: docker
  docker_image: python:3.11-slim
```

**一个持久化容器，跨整个进程共享。** Hermes 在首次使用时启动一个长期运行的容器（`docker run -d ... sleep 2h`），并通过 `docker exec` 将所有终端、文件和 `execute_code` 调用路由到同一个容器中。工作目录变更、安装的包、环境调整以及写入 `/workspace` 的文件都会在工具调用之间（包括 `/new`、`/reset` 和 `delegate_task` 子代理）持续保留，贯穿整个 Hermes 进程的生命周期。容器在关闭时会被停止并移除。

这意味着 Docker 后端的行为类似于一个持久化沙盒虚拟机，而不是每条命令都重新创建新容器。如果你执行了 `pip install foo`，它在整个会话中都会存在。如果你执行了 `cd /workspace/project`，后续的 `ls` 会看到那个目录。有关完整生命周期详情，以及控制 `/workspace` 和 `/root` 在 Hermes 重启后是否保留的 `container_persistent` 标志，请参见[配置 → Docker 后端](../configuration.md#docker-backend)。

### SSH 后端

推荐用于安全场景——代理无法修改自身代码：

```yaml
terminal:
  backend: ssh
```
```bash
# 在 ~/.hermes/.env 中设置凭据
TERMINAL_SSH_HOST=my-server.example.com
TERMINAL_SSH_USER=myuser
TERMINAL_SSH_KEY=~/.ssh/id_rsa
```

### Singularity/Apptainer

```bash
# 预构建 SIF 用于并行工作器
apptainer build ~/python.sif docker://python:3.11-slim

# 配置
hermes config set terminal.backend singularity
hermes config set terminal.singularity_image ~/python.sif
```

### Modal（无服务器云端）

```bash
uv pip install modal
modal setup
hermes config set terminal.backend modal
```

### 容器资源

为所有容器后端配置 CPU、内存、磁盘和持久性：

```yaml
terminal:
  backend: docker  # 或 singularity, modal, daytona
  container_cpu: 1              # CPU 核心数（默认：1）
  container_memory: 5120        # 内存 MB（默认：5GB）
  container_disk: 51200         # 磁盘 MB（默认：50GB）
  container_persistent: true    # 文件系统跨会话持久化（默认：true）
```

当 `container_persistent: true` 时，安装的包、文件和配置会在会话之间保留。

### 容器安全

所有容器后端都启用安全加固：

- 只读根文件系统（Docker）
- 丢弃所有 Linux 能力
- 无权限提升
- PID 限制（256 个进程）
- 完全命名空间隔离
- 通过卷实现的持久化工作区，而非可写根层

Docker 可选择通过 `terminal.docker_forward_env` 接收显式环境变量允许列表，但转发的变量对容器内的命令可见，应视为暴露给该会话。

## 后台进程管理

启动后台进程并进行管理：

```python
terminal(command="pytest -v tests/", background=true)
# 返回：{"session_id": "proc_abc123", "pid": 12345}

# 然后通过 process 工具进行管理：
process(action="list")       # 显示所有运行中的进程
process(action="poll", session_id="proc_abc123")   # 检查状态
process(action="wait", session_id="proc_abc123")   # 阻塞直到完成
process(action="log", session_id="proc_abc123")    # 完整输出
process(action="kill", session_id="proc_abc123")   # 终止
process(action="write", session_id="proc_abc123", data="y")  # 发送输入
```

PTY 模式（`pty=true`）可启用交互式 CLI 工具，如 Codex 和 Claude Code。

## Sudo 支持

如果命令需要 sudo，系统会提示你输入密码（会话中会缓存）。或者在 `~/.hermes/.env` 中设置 `SUDO_PASSWORD`。

:::warning
在消息平台上，如果 sudo 失败，输出中会包含一条提示，建议在 `~/.hermes/.env` 中添加 `SUDO_PASSWORD`。
:::