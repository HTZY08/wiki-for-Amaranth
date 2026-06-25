---
title: Configuration
---

sidebar_position: 2
title: "配置"
description: "配置 Hermes Agent — config.yaml、提供商、模型、API 密钥等"
---

--- body ---
# 配置

所有设置都存储在 `~/.hermes/` 目录中，以便于访问。

:::tip 让 `config.yaml` 正常工作的最简单路径
运行 `hermes setup --portal` — 一次 OAuth 即可获得一个模型提供商以及所有四个 Tool Gateway 工具，无需手动编辑 YAML。Portal 订阅者还可享受按令牌计费提供商 10% 的折扣。参见 [Nous Portal](/integrations/nous-portal)。
:::

## 目录结构

```text
~/.hermes/
├── config.yaml     # 设置（模型、终端、TTS、压缩等）
├── .env            # API 密钥和密钥
├── auth.json       # OAuth 提供商凭据（Nous Portal 等）
├── SOUL.md         # 主代理身份（系统提示中的插槽 #1）
├── memories/       # 持久记忆（MEMORY.md, USER.md）
├── skills/         # 代理创建的技能（通过 skill_manage 工具管理）
├── cron/           # 定时任务
├── sessions/       # 网关会话
└── logs/           # 日志（errors.log、gateway.log — 密钥自动隐藏）
```

## 管理配置

```bash
hermes config              # 查看当前配置
hermes config edit         # 在编辑器中打开 config.yaml
hermes config set KEY VAL  # 设置特定值
hermes config check        # 检查缺失的选项（更新后）
hermes config migrate      # 交互式添加缺失选项

# 示例：
hermes config set model anthropic/claude-opus-4
hermes config set terminal.backend docker
hermes config set OPENROUTER_API_KEY sk-or-...  # 保存到 .env
```

:::tip
`hermes config set` 命令自动将值路由到正确的文件 — API 密钥保存到 `.env`，其他所有内容保存到 `config.yaml`。
:::

## 配置优先级

设置按以下顺序解析（优先级从高到低）：

1. **CLI 参数** — 例如 `hermes chat --model anthropic/claude-sonnet-4`（每次调用时覆盖）
2. **`~/.hermes/config.yaml`** — 所有非机密设置的主配置文件
3. **`~/.hermes/.env`** — 环境变量的后备；**必需**用于机密（API 密钥、令牌、密码）
4. **内置默认值** — 当未设置其他内容时，硬编码的安全默认值

:::info 经验法则
机密（API 密钥、机器人令牌、密码）放在 `.env` 中。其他所有内容（模型、终端后端、压缩设置、内存限制、工具集）放在 `config.yaml` 中。当两者都设置时，对于非机密设置，`config.yaml` 优先。
:::

:::tip 组织部署
管理员可以通过系统级托管目录固定特定配置和机密值，普通用户无法覆盖。参见 [托管作用域](/user-guide/managed-scope)。
:::

## 环境变量替换

你可以使用 `${VAR_NAME}` 语法在 `config.yaml` 中引用环境变量：

```yaml
auxiliary:
  vision:
    api_key: ${GOOGLE_API_KEY}
    base_url: ${CUSTOM_VISION_URL}

delegation:
  api_key: ${DELEGATION_KEY}
```

单个值中支持多个引用：`url: "${HOST}:${PORT}"`。如果引用的变量未设置，占位符将原样保留（`${UNDEFINED_VAR}` 保持不变）。仅支持 `${VAR}` 语法 — 裸的 `$VAR` 不会展开。

有关 AI 提供商设置（OpenRouter、Anthropic、Copilot、自定义端点、自托管 LLM、备用模型等），请参见 [AI 提供商](/integrations/providers)。

### 提供商超时

你可以设置 `providers.<id>.request_timeout_seconds` 作为提供商的全局请求超时，以及 `providers.<id>.models.<model>.timeout_seconds` 作为特定模型的超时覆盖。适用于每种传输方式（OpenAI-wire、原生 Anthropic、Anthropic 兼容）的主轮询客户端、备用链、凭据轮换后的重建，以及（对于 OpenAI-wire）每个请求的超时 kwargs — 因此配置值优先于旧的 `HERMES_API_TIMEOUT` 环境变量。

你还可以设置 `providers.<id>.stale_timeout_seconds` 用于非流式陈旧调用检测器，以及 `providers.<id>.models.<model>.stale_timeout_seconds` 用于特定模型的覆盖。这优先于旧的 `HERMES_API_CALL_STALE_TIMEOUT` 环境变量。

保持未设置将沿用旧的默认值（`HERMES_API_TIMEOUT=1800` 秒，`HERMES_API_CALL_STALE_TIMEOUT=90` 秒，原生 Anthropic 900 秒）。非流式陈旧检测器在隐式未设置时对本地端点自动禁用，并且对于非常大的上下文可以向上扩展。目前不适用于 AWS Bedrock（`bedrock_converse` 和 AnthropicBedrock SDK 路径都使用带有自己超时配置的 boto3）。参见 [`cli-config.yaml.example`](https://github.com/NousResearch/hermes-agent/blob/main/cli-config.yaml.example) 中的注释示例。

## 更新行为

`hermes update` 设置位于 `config.yaml` 的 `updates` 下：

```yaml
updates:
  pre_update_backup: false       # 每次更新前创建完整的 HERMES_HOME 压缩包
  backup_keep: 5                 # 保留这么多更新前的备份压缩包
  non_interactive_local_changes: stash  # stash | discard
```

对于 git 安装，Hermes 在检出更新分支或拉取之前，会自动贮藏脏的跟踪文件和未跟踪文件。交互式终端更新在恢复贮藏之前会提示。非交互式更新（桌面/聊天应用、网关或 `--yes`）使用 `updates.non_interactive_local_changes`：`stash` 在成功拉取后恢复本地源代码编辑，而 `discard` 在成功拉取后丢弃更新创建的贮藏。仅在托管安装中使用 `discard`，这种安装中本地源代码编辑永远不会持久。

在该贮藏步骤之前，Hermes 还会恢复由 npm install/build 变更留下的跟踪 `package-lock.json` 差异。在更新之前，提交或手动贮藏有意的锁定文件编辑。

## 终端后端配置

Hermes 支持六种终端后端。每种后端决定了代理的 shell 命令实际执行的位置 — 你的本地机器、Docker 容器、通过 SSH 的远程服务器、Modal 云沙箱（直接或通过 Nous 管理的网关）、Daytona 工作区或 Singularity/Apptainer 容器。

```yaml
terminal:
  backend: local    # local | docker | ssh | modal | daytona | singularity
  cwd: "."          # 网关/cron 工作目录（CLI 始终使用启动目录）
  timeout: 180      # 每个命令的超时时间（秒）
  home_mode: auto   # auto | real | profile — 子进程 HOME 策略
  env_passthrough: []  # 转发到沙箱执行的环境变量名称（terminal + execute_code）
  singularity_image: "docker://nikolaik/python-nodejs:python3.11-nodejs20"  # Singularity 后端的容器镜像
  modal_image: "nikolaik/python-nodejs:python3.11-nodejs20"                 # Modal 后端的容器镜像
  daytona_image: "nikolaik/python-nodejs:python3.11-nodejs20"               # Daytona 后端的容器镜像
```

对于云沙箱（如 Modal 和 Daytona），`container_persistent: true` 意味着 Hermes 将尝试在沙箱重新创建时保留文件系统状态。它不保证相同的实时沙箱、PID 空间或后台进程稍后仍会运行。

### 后端概览

| 后端 | 命令运行位置 | 隔离性 | 最佳用途 |
|---------|-------------------|-----------|----------|
| **local** | 直接在你的机器上 | 无 | 开发、个人使用 |
| **docker** | 单个持久 Docker 容器（会话、`/new`、子代理共享） | 完全（命名空间、cap-drop） | 安全沙箱、CI/CD |
| **ssh** | 通过 SSH 的远程服务器 | 网络边界 | 远程开发、强大硬件 |
| **modal** | Modal 云沙箱 | 完全（云 VM） | 临时云计算、评估 |
| **daytona** | Daytona 工作区 | 完全（云容器） | 托管云开发环境 |
| **singularity** | Singularity/Apptainer 容器 | 命名空间（--containall） | HPC 集群、共享机器 |

### 本地后端

默认值。命令直接在你的机器上运行，无隔离。无需特殊设置。

```yaml
terminal:
  backend: local
```

默认情况下，本地工具子进程保留你真实的 OS 用户 `HOME`。这使得外部 CLI（如 `git`、`ssh`、`gh`、`az`、`npm`、Claude Code 和 Codex）能够找到它们在你的普通 shell 中已经使用的凭据和配置。Hermes 状态仍然通过 `HERMES_HOME` 进行配置文件作用域限定；`HOME` 不是配置文件选择配置、记忆、会话或技能的方式。

Hermes **不会**更改你的系统范围的 `HOME`、你的 shell 启动文件或操作系统账户主目录。此设置仅控制传递给 Hermes 通过工具（如 `terminal`、后台终端进程、`execute_code` 和 ACP 辅助进程）启动的子进程的环境。

#### `terminal.home_mode`

| 模式 | 主机安装 | 容器 | 权衡 |
|---|---|---|---|
| `auto` | 保留真实的 OS 用户 `HOME` | 使用 `{HERMES_HOME}/home` | 推荐默认值。主机 CLI 继续工作；容器状态持久。 |
| `real` | 强制使用真实的 OS 用户 `HOME` | 如果可见则强制使用真实的 OS 用户 `HOME` | 如果父进程意外启动时将 `HOME` 指向配置文件主目录，则很有用。 |
| `profile` | 当存在时使用 `{HERMES_HOME}/home` | 当存在时使用 `{HERMES_HOME}/home` | 严格的每个配置文件 CLI 配置隔离，但正常的 `~/.ssh`、`~/.gitconfig`、`~/.azure`、`~/.config/gh`、Claude/Codex 认证、npm 状态等，除非你在配置文件主目录中初始化或链接它们，否则将不可见。 |

默认的缺点是主机配置文件共享相同的普通用户级 CLI 凭据/配置（在 `~` 下）。如果你需要一个具有独立 git 身份、SSH 密钥、GitHub CLI 登录、npm 配置或云 CLI 登录的配置文件，请使用 `home_mode: profile` 并在该配置文件主目录中专门初始化这些工具。

如果你有意想要严格的每个配置文件工具配置隔离，请设置：

```yaml
terminal:
  home_mode: profile
```

在该模式下，工具子进程使用 `{HERMES_HOME}/home` 作为 `HOME`。Hermes 还设置 `HERMES_REAL_HOME`，以便脚本在需要时仍能定位实际的用户主目录。在后端中，`auto` 模式下继续使用 `{HERMES_HOME}/home`，因为该目录位于持久化的 Hermes 数据卷上。

需要区分配置文件状态和真实用户主目录的脚本应优先使用 `HERMES_HOME` 获取 Hermes 数据，使用 `HERMES_REAL_HOME` 获取账户主目录：

```python
from pathlib import Path
import os

hermes_home = Path(os.environ["HERMES_HOME"])
real_home = Path(os.environ.get("HERMES_REAL_HOME", os.environ["HOME"]))
```

:::warning
代理与你的用户账户具有相同的文件系统访问权限。使用 `hermes tools` 禁用你不希望使用的工具，或切换到 Docker 以进行沙箱化。
:::

### Docker 后端

在 Docker 容器内运行命令，并应用安全加固（所有 capability 被丢弃，无特权升级，PID 限制）。

**单个持久容器，跨 Hermes 进程共享。** Hermes 在首次使用时会启动一个长期运行的容器，并通过 `docker exec` 将每个终端、文件和 `execute_code` 调用路由到该同一容器 — 跨会话、`/new`、`/reset` 和 `delegate_task` 子代理。工作目录更改、已安装的包、`/workspace` 中的文件以及**后台进程**都会从一个工具调用延续到下一个，从一个 Hermes 进程延续到下一个。当你关闭 TUI 会话、运行 `/quit` 或启动新的 `hermes` 调用时，容器继续运行，下一个 Hermes 进程通过标签查找重用它。有关确切的拆除规则，请参见下面的 **容器生命周期**。

```yaml
terminal:
  backend: docker
  docker_image: "nikolaik/python-nodejs:python3.11-nodejs20"
  docker_mount_cwd_to_workspace: false  # 将启动目录挂载到 /workspace
  docker_run_as_host_user: false   # 参见下面的“以主机用户身份运行容器”
  docker_forward_env:              # 要转发到容器的主机环境变量
    - "GITHUB_TOKEN"
  docker_env:                      # 要注入的字面环境变量（KEY=value）
    DEBUG: "1"
    PYTHONUNBUFFERED: "1"
  docker_volumes:                  # 主机的目录挂载
    - "/home/user/projects:/workspace/projects"
    - "/home/user/data:/data:ro"   # :ro 表示只读
  docker_extra_args:               # 附加标志，原样追加到 `docker run`
    - "--gpus=all"
    - "--network=host"

  # 资源限制
  container_cpu: 1                 # CPU 核心数（0 = 无限制）
  container_memory: 5120           # MB（0 = 无限制）
  container_disk: 51200            # MB（需要 overlay2 和 XFS+pquota）
  container_persistent: true       # 持久化 /workspace 和 /root 绑定挂载目录

  # 跨进程容器重用（默认匹配“跨会话共享一个长期运行的容器”的契约 — 参见容器生命周期）。
  docker_persist_across_processes: true   # 跨 Hermes 重启重用容器
  docker_orphan_reaper: true              # 启动时清理已退出的废弃容器

  # 跨后端生命周期设置（也适用于 docker）
  timeout: 180                     # 每个命令的超时时间（秒）
  lifetime_seconds: 300            # 空闲回收器窗口；也是孤儿回收器阈值的 2 倍
```

**`docker_env` 与 `docker_forward_env`**：前者注入你在配置中指定的字面 `KEY=value` 对（值存在于你的 `config.yaml` 中，或通过 JSON 字典 `TERMINAL_DOCKER_ENV='{"DEBUG":"1"}'` 传递）。后者从你的 shell 或 `~/.hermes/.env` 中转发值，因此实际的机密永远不会出现在配置文件中。对于令牌使用 `docker_forward_env`，对于容器需要的静态旋钮使用 `docker_env`。

**`terminal.docker_extra_args`**（也可通过 `TERMINAL_DOCKER_EXTRA_ARGS='["--gpus=all"]'` 覆盖）允许你传递 Hermes 不公开为一级键的任意 `docker run` 标志 — `--gpus`、`--network`、`--add-host`、替代的 `--security-opt` 覆盖等。每个条目必须是一个字符串；列表最后追加到组合的 `docker run` 调用中，因此如果需要，它可以覆盖 Hermes 的默认设置。谨慎使用 — 与沙箱加固（capability 丢弃、`--user`、工作区绑定挂载）冲突的标志将静默削弱隔离性。

**要求：** Docker Desktop 或 Docker Engine 已安装并运行。Hermes 探测 `$PATH` 以及常见的 macOS 安装位置（`/usr/local/bin/docker`、`/opt/homebrew/bin/docker`、Docker Desktop 应用包）。Podman 开箱即用：设置 `HERMES_DOCKER_BINARY=podman`（或完整路径）以强制使用（当两者都安装时）。

#### 容器生命周期

每个由 Hermes 管理的容器都带有三个标签，以便后续进程（和孤儿回收器）可以识别它：

- `hermes-agent=1` — 标记为 Hermes 管理
- `hermes-task-id=<sanitized task_id>` — 键控每个任务的重用探测
- `hermes-profile=<sanitized profile name>` — 将重用和回收限定到活动的 Hermes 配置文件

启动时，Hermes 运行 `docker ps --filter label=hermes-task-id=<id> --filter label=hermes-profile=<profile>`，并在找到现有容器时**附加到该容器**。如果容器已退出（例如在 Docker 守护进程重启后），则将其 `docker start` 并重用 — 文件系统状态和任何已安装的包都会保留，但容器内的后台进程不会保留。

当 Hermes 进程退出时 — `/quit`、关闭 TUI 会话、网关关闭，甚至 SIGKILL — 清理路径在默认模式下对于容器是**无操作**。容器继续运行。下一个 Hermes 进程通过标签探测在毫秒内附加到它。这是“跨会话共享一个长期运行的容器”契约所要求的行为：它是后台进程（npm watcher、开发服务器、长时间运行的 pytest）跨会话存活的唯一方式。

**容器仅在以下情况下被拆除（停止并 `docker rm -f`）：**

| 触发条件 | 何时触发 |
|---|---|
| `docker_persist_across_processes: false` | 显式的每个进程隔离。每次 `cleanup()` 执行 `stop` + `rm -f`。匹配 issue-#20561 之前的行为。 |
| 空闲回收器（`lifetime_seconds`，默认 300 秒） | 仅当环境为 `persist_across_processes=false` 时。持久模式下环境为无操作；容器在空闲清理中存活。 |
| 下次启动时的孤儿回收器 | 清理**已退出**的 Hermes 标签容器（年龄大于 `2 × lifetime_seconds`（默认 600 秒 = 10 分钟）），限定在当前配置文件内。**正在运行的容器永远不会被触及** — 兄弟进程安全。设置 `docker_orphan_reaper: false` 以禁用。 |
| 直接用户操作 | `docker rm -f`、`docker system prune`、Docker Desktop 重启。我们没有设置 `--restart=always`，因此主机重启会将容器置于 `Exited` 状态（其 CoW 层保留并在下次启动时重用，但后台进程丢失）。 |

值得注意的边缘情况：

- **容器内 PID 1 的 OOM 杀死**会将容器转换为 `Exited` 状态。下次重用时将 `docker start` 它；文件系统状态保留，后台进程不保留。
- **切换配置文件**会隔离彼此的容器 — 标记为 `hermes-profile=work` 的容器对于在 `hermes-profile=research` 下运行的 Hermes 进程是不可见的。孤儿回收器也受配置文件作用域限制，因此跨配置文件的容器不会意外被回收，但它们也不会自动清理，直到你在其原始配置文件下再次启动 Hermes。

通过 `delegate_task(tasks=[...])` 生成的并行子代理共享这一个容器 — 并发的 `cd`、环境变量突变以及对同一路径的写入将发生冲突。如果子代理需要隔离的沙箱，它必须通过 `register_task_env_overrides()` 注册每个任务的镜像覆盖，RL 和基准环境（TerminalBench2、HermesSweEnv 等）会自动为其每个任务的 Docker 镜像执行此操作。

**安全加固：**
- `--cap-drop ALL`，仅添加回 `DAC_OVERRIDE`、`CHOWN`、`FOWNER`
- `--security-opt no-new-privileges`
- `--pids-limit 256`
- 大小限制的 tmpfs 用于 `/tmp`（512MB）、`/var/tmp`（256MB）、`/run`（64MB）

**凭据转发：** `docker_forward_env` 中列出的环境变量首先从你的 shell 环境中解析，然后从 `~/.hermes/.env` 中解析。技能也可以声明 `required_environment_variables`，这些变量会自动合并。

#### 环境变量覆盖

`terminal:` 下的每个键都有一个形式为 `TERMINAL_<KEY_UPPERCASE>` 的环境变量覆盖。Docker 后端最有用的几个：

| 环境变量 | 映射到 | 备注 |
|---|---|---|
| `TERMINAL_DOCKER_IMAGE` | `docker_image` | 基础镜像 |
| `TERMINAL_DOCKER_FORWARD_ENV` | `docker_forward_env` | JSON 数组：`'["GITHUB_TOKEN","OPENAI_API_KEY"]'` |
| `TERMINAL_DOCKER_ENV` | `docker_env` | JSON 字典：`'{"DEBUG":"1"}'` |
| `TERMINAL_DOCKER_VOLUMES` | `docker_volumes` | JSON 数组，每个元素为 `"host:container[:ro]"` 字符串 |
| `TERMINAL_DOCKER_EXTRA_ARGS` | `docker_extra_args` | JSON 数组 |
| `TERMINAL_DOCKER_MOUNT_CWD_TO_WORKSPACE` | `docker_mount_cwd_to_workspace` | `true` / `false` |
| `TERMINAL_DOCKER_RUN_AS_HOST_USER` | `docker_run_as_host_user` | `true` / `false` |
| `TERMINAL_DOCKER_PERSIST_ACROSS_PROCESSES` | `docker_persist_across_processes` | `true` / `false` — 默认 `true` |
| `TERMINAL_DOCKER_ORPHAN_REAPER` | `docker_orphan_reaper` | `true` / `false` — 默认 `true` |
| `TERMINAL_CONTAINER_CPU` | `container_cpu` | CPU 核心数 |
| `TERMINAL_CONTAINER_MEMORY` | `container_memory` | MB |
| `TERMINAL_CONTAINER_DISK` | `container_disk` | MB |
| `TERMINAL_CONTAINER_PERSISTENT` | `container_persistent` | `true` / `false` — 控制绑定挂载的工作区目录，与 `docker_persist_across_processes` 不同 |
| `TERMINAL_LIFETIME_SECONDS` | `lifetime_seconds` | 空闲回收器窗口 |
| `TERMINAL_TIMEOUT` | `timeout` | 每个命令的超时时间 |
| `HERMES_DOCKER_BINARY` | _none_ | 强制使用特定的 docker/podman 二进制路径 |

### SSH 后端

通过 SSH 在远程服务器上运行命令。使用 ControlMaster 进行连接重用（5 分钟空闲保活）。默认启用持久 shell — 状态（cwd、环境变量）跨命令保留。

```yaml
terminal:
  backend: ssh
  persistent_shell: true           # 保持长期存在的 bash 会话（默认：true）
```

**必需的环境变量：**

```bash
TERMINAL_SSH_HOST=my-server.example.com
TERMINAL_SSH_USER=ubuntu
```

**可选的：**

| 变量 | 默认值 | 描述 |
|----------|---------|-------------|
| `TERMINAL_SSH_PORT` | `22` | SSH 端口 |
| `TERMINAL_SSH_KEY` | （系统默认） | SSH 私钥路径 |
| `TERMINAL_SSH_PERSISTENT` | `true` | 启用持久 shell |

**工作原理：** 初始化时以 `BatchMode=yes` 和 `StrictHostKeyChecking=accept-new` 连接。持久 shell 在远程主机上保持单个 `bash -l` 进程存活，通过临时文件进行通信。需要 `stdin_data` 或 `sudo` 的命令会自动回退到一次性模式。

### Modal 后端

在 [Modal](https://modal.com) 云沙箱中运行命令。每个任务获得一个具有可配置 CPU、内存和磁盘的隔离 VM。文件系统可以跨会话快照/恢复。

```yaml
terminal:
  backend: modal
  container_cpu: 1                 # CPU 核心数
  container_memory: 5120           # MB (5GB)
  container_disk: 51200            # MB (50GB)
  container_persistent: true       # 快照/恢复文件系统
```

**必需：** 环境变量 `MODAL_TOKEN_ID` + `MODAL_TOKEN_SECRET`，或 `~/.modal.toml` 配置文件。

**持久化：** 启用时，沙箱文件系统在清理时快照，并在下次会话时恢复。快照在 `~/.hermes/modal_snapshots.json` 中跟踪。这保留了文件系统状态，而不是实时进程、PID 空间或后台作业。

**凭据文件：** 自动从 `~/.hermes/` 挂载（OAuth 令牌等），并在每个命令之前同步。

### Daytona 后端

在 [Daytona](https://daytona.io) 托管的工作区中运行命令。支持停止/恢复以实现持久化。

```yaml
terminal:
  backend: daytona
  container_cpu: 1                 # CPU 核心数
  container_memory: 5120           # MB → 转换为 GiB
  container_disk: 10240            # MB → 转换为 GiB（最大 10 GiB）
  container_persistent: true       # 停止/恢复而不是删除
```

**必需：** `DAYTONA_API_KEY` 环境变量。

**持久化：** 启用时，沙箱在清理时停止（而不是删除），并在下次会话时恢复。沙箱名称遵循模式 `hermes-{task_id}`。

**磁盘限制：** Daytona 强制最大 10 GiB。超过此值的请求会被限制并给出警告。

### Singularity/Apptainer 后端

在 [Singularity/Apptainer](https://apptainer.org) 容器中运行命令。专为 HPC 集群和共享机器设计，这些地方 Docker 不可用。

```yaml
terminal:
  backend: singularity
  singularity_image: "docker://nikolaik/python-nodejs:python3.11-nodejs20"
  container_cpu: 1                 # CPU 核心数
  container_memory: 5120           # MB
  container_persistent: true       # 可写覆盖层跨会话持久化
```

**要求：** `apptainer` 或 `singularity` 二进制文件在 `$PATH` 中。

**镜像处理：** Docker URL（`docker://...`）会自动转换为 SIF 文件并缓存。现有的 `.sif` 文件直接使用。

**临时目录：** 按以下顺序解析：`TERMINAL_SCRATCH_DIR` → `TERMINAL_SANDBOX_DIR/singularity` → `/scratch/$USER/hermes-agent`（HPC 惯例） → `~/.hermes/sandboxes/singularity`。

**隔离：** 使用 `--containall --no-home` 进行完整的命名空间隔离，而不挂载主机主目录。

### 常见终端后端问题

如果终端命令立即失败，或者终端工具报告已禁用：

- **Local** — 没有特殊要求。入门时最安全的默认值。
- **Docker** — 运行 `docker version` 以验证 Docker 是否正常工作。如果失败，修复 Docker 或 `hermes config set terminal.backend local`。
- **SSH** — 必须同时设置 `TERMINAL_SSH_HOST` 和 `TERMINAL_SSH_USER`。Hermes 会记录清晰的错误信息，如果其中任何一个缺失。
- **Modal** — 需要 `MODAL_TOKEN_ID` 环境变量或 `~/.modal.toml`。运行 `hermes doctor` 检查。
- **Daytona** — 需要 `DAYTONA_API_KEY`。Daytona SDK 处理服务器 URL 配置。
- **Singularity** — 需要在 `$PATH` 中有 `apptainer` 或 `singularity`。常见于 HPC 集群。

如有疑问，将 `terminal.backend` 设置回 `local` 并首先验证命令在那里运行。

### 拆除时远程到主机的文件同步

对于 **SSH**、**Modal** 和 **Daytona** 后端（当代理的工作树位于与运行 Hermes 的主机不同的机器上时），Hermes 会跟踪代理在远程沙箱中触摸过的文件，并在会话拆除/沙箱清理时，将修改后的文件**同步回主机**，放在 `~/.hermes/cache/remote-syncs/<session-id>/` 下。

- 触发条件：会话关闭、`/new`、`/reset`、网关消息超时、`delegate_task` 子代理完成（当子代理使用了远程后端时）。
- 覆盖代理修改的整个树，而不仅仅是它显式打开的文件。添加、编辑和删除都会被捕获。
- 远程沙箱可能在你查看时已被拆除；本地 `~/.hermes/cache/remote-syncs/…` 副本是代理更改的权威记录。
- 大型二进制输出（模型检查点、原始数据集）受大小限制 — 同步会跳过超过 `file_sync_max_mb`（默认 `100`）的文件。如果你期望更大的工件返回，请增加该值。

```yaml
terminal:
  file_sync_max_mb: 100     # 默认 — 同步每个最大 100 MB 的文件
  file_sync_enabled: true   # 默认 — 设置 false 以完全跳过同步
```

这就是你如何从会话结束后被销毁的临时云沙箱中恢复结果，而无需告诉代理显式地 `scp` 或 `modal volume put` 每个工件。

### Docker 卷挂载

使用 Docker 后端时，`docker_volumes` 允许你与容器共享主机目录。每个条目使用标准的 Docker `-v` 语法：`host_path:container_path[:options]`。

```yaml
terminal:
  backend: docker
  docker_volumes:
    - "/home/user/projects:/workspace/projects"   # 读写（默认）
    - "/home/user/datasets:/data:ro"              # 只读
    - "/home/user/.hermes/cache/documents:/output" # 网关可见的导出
```

这对于以下情况很有用：
- **提供文件**给代理（数据集、配置、参考代码）
- **接收文件**来自代理（生成的代码、报告、导出）
- **共享工作区**，你和代理都访问相同的文件

如果你使用消息网关并希望代理通过 `MEDIA:/...` 发送生成的文件，请优先使用专用的主机可见导出挂载，例如 `/home/user/.hermes/cache/documents:/output`。

- 在 Docker 内将文件写入 `/output/...`
- 在 `MEDIA:` 中发出**主机路径**，例如：
  `MEDIA:/home/user/.hermes/cache/documents/report.txt`
- 不要发出 `/workspace/...` 或 `/output/...`，除非该确切路径在主机上对网关进程也存在。

:::warning
YAML 重复键会静默覆盖较早的键。如果已有 `docker_volumes:` 块，请将新的挂载合并到同一列表中，而不是稍后在文件中添加另一个 `docker_volumes:` 键。
:::

也可以通过环境变量设置：`TERMINAL_DOCKER_VOLUMES='["/host:/container"]'`（JSON 数组）。

### Docker 凭据转发

默认情况下，Docker 终端会话不会继承任意主机凭据。如果你需要容器内的特定令牌，请将其添加到 `terminal.docker_forward_env`。

```yaml
terminal:
  backend: docker
  docker_forward_env:
    - "GITHUB_TOKEN"
    - "NPM_TOKEN"
```

Hermes 首先从当前 shell 解析每个列出的变量，如果使用 `hermes config set` 保存过，则回退到 `~/.hermes/.env`。

:::warning
`docker_forward_env` 中列出的任何内容都会对容器内运行的命令可见。仅转发你愿意向终端会话暴露的凭据。
:::

### 以你的主机用户身份运行容器

默认情况下，Docker 容器以 `root`（UID 0）身份运行。在 `/workspace` 或其他绑定挂载中创建的文件最终由主机上的 root 拥有，因此在会话之后，你必须使用 `sudo chown` 才能从主机编辑器中编辑它们。`terminal.docker_run_as_host_user` 标志解决了这个问题：

```yaml
terminal:
  backend: docker
  docker_run_as_host_user: true   # 默认：false
```

启用后，Hermes 将 `--user $(id -u):$(id -g)` 追加到 `docker run` 命令，因此写入绑定挂载目录（`/workspace`、`/root`、`docker_volumes` 中的任何内容）的文件由你的主机用户拥有，而不是 root。权衡：容器不能再执行 `apt install` 或写入 root 拥有的路径，如 `/root/.npm` — 如果您需要两者，请使用其 `HOME` 由非 root 用户拥有的基础镜像（或在镜像构建时添加所需的工具）。

保持此设置为 `false`（默认值）以获得向后兼容的行为。当你的工作流主要是“编辑已挂载的主机文件”并且你厌倦了 `sudo chown -R` 时，请将其打开。

### 可选：将启动目录挂载到 `/workspace`

默认情况下，Docker 沙箱保持隔离。Hermes **不会**将当前主机工作目录传递给容器，除非你明确选择加入。

在 `config.yaml` 中启用它：

```yaml
terminal:
  backend: docker
  docker_mount_cwd_to_workspace: true
```

启用后：
- 如果你从 `~/projects/my-app` 启动 Hermes，该主机目录将绑定挂载到 `/workspace`
- Docker 后端从 `/workspace` 开始
- 文件工具和终端命令都看到相同的已挂载项目

禁用时，除非你通过 `docker_volumes` 显式挂载某些内容，否则 `/workspace` 保持沙箱拥有。

安全权衡：
- `false` 保留沙箱边界
- `true` 允许沙箱直接访问你启动 Hermes 的目录

仅当你明确希望容器处理实时主机文件时，才选择加入。

### 持久 Shell

默认情况下，每个终端命令在自己的子进程中运行 — 工作目录、环境变量和 shell 变量在命令之间重置。当启用**持久 shell** 时，单个长期运行的 bash 进程会在 `execute()` 调用之间保持存活，以便状态在命令之间保留。

这对于 **SSH 后端**最有用，因为它还消除了每个命令的连接开销。SSH 默认启用持久 shell，本地后端默认禁用。

```yaml
terminal:
  persistent_shell: true   # 默认 — 为 SSH 启用持久 shell
```

要禁用：

```bash
hermes config set terminal.persistent_shell false
```

**在命令之间持久化的内容：**
- 工作目录（`cd /tmp` 会保留到下一个命令）
- 导出的环境变量（`export FOO=bar`）
- Shell 变量（`MY_VAR=hello`）

**优先级：**

| 级别 | 变量 | 默认值 |
|-------|----------|---------|
| 配置 | `terminal.persistent_shell` | `true` |
| SSH 覆盖 | `TERMINAL_SSH_PERSISTENT` | 跟随配置 |
| 本地覆盖 | `TERMINAL_LOCAL_PERSISTENT` | `false` |

每个后端的环境变量具有最高优先级。如果你也想要在本地后端上使用持久 shell：

```bash
export TERMINAL_LOCAL_PERSISTENT=true
```

:::note
需要 `stdin_data` 或 sudo 的命令会自动回退到一次性模式，因为持久 shell 的标准输入已被 IPC 协议占用。
:::

有关每个后端的详细信息，请参见 [代码执行](features/code-execution.md) 和 [README 中的终端部分](features/tools.md)。

## 技能设置

技能可以通过其 SKILL.md frontmatter 声明自己的配置设置。这些是非机密值（路径、偏好、域设置），存储在 `config.yaml` 的 `skills.config` 命名空间下。

```yaml
skills:
  config:
    myplugin:
      path: ~/myplugin-data   # 示例 — 每个技能定义自己的键
```

**技能设置如何工作：**

- `hermes config migrate` 扫描所有启用的技能，找到未配置的设置，并提供提示
- `hermes config show` 在“技能设置”下显示所有技能设置及其所属技能
- 当技能加载时，其解析的配置值会自动注入到技能上下文中

**手动设置值：**

```bash
hermes config set skills.config.myplugin.path ~/myplugin-data
```

有关在你自己技能中声明配置设置的详细信息，请参见 [创建技能 — 配置设置](/developer-guide/creating-skills#config-settings-configyaml)。

### 对代理创建的技能写入进行防护

当代理使用 `skill_manage` 创建、编辑、修补或删除技能时，Hermes 可以选择扫描新/更新的内容中是否存在危险关键词模式（凭据收集、明显的提示注入、数据外泄指令）。扫描器**默认关闭** — 那些合法地接触 `~/.ssh/` 或提及 `$OPENAI_API_KEY` 的真实代理工作流过于频繁地触发了启发式规则。如果你希望在代理的技能写入落地之前让扫描器提示你，请重新打开它：

```yaml
skills:
  guard_agent_created: true   # 默认：false
```

开启后，任何被标记的 `skill_manage` 写入都会显示一个批准提示，并附上扫描器的理由。接受的写入会落地；拒绝的写入会向代理返回一个解释性错误。

### 技能写入的写入批准

独立于上述内容扫描器，`skills.write_approval` 将**每次**代理技能写入（创建/编辑/修补/删除/支持文件）都置于你的明确批准之下 — 与危险命令相同的批准/拒绝机制：

```yaml
skills:
  write_approval: false   # false = 自由写入（默认）| true = 每次写入都暂存以供审查
```

开启后，技能写入会暂存在 `~/.hermes/pending/skills/` 下，并通过 `/skills pending`、`/skills diff <id>`、`/skills approve <id>`、`/skills reject <id>` 进行审查 — 从 CLI 或任何消息平台。运行时通过 `/skills approval on|off` 切换。记忆也有相同的门控（下文中的 `memory.write_approval`）。完整演练：[门控代理技能写入](/user-guide/features/skills#gating-agent-skill-writes-skillswrite_approval)。

## 内存配置

```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200   # ~800 个令牌
  user_char_limit: 1375     # ~500 个令牌
  write_approval: false     # true = 需要批准才能进行任何内存写入
```

使用 `memory.write_approval: true`，内存写入需要你的批准才能落地：交互式 CLI 会提示内联；消息会话和后台自我改进审查阶段会将写入暂存，以便通过 `/memory pending` → `/memory approve <id>` / `/memory reject <id>` 进行审查。运行时通过 `/memory approval on|off` 切换。参见 [控制内存写入](/user-guide/features/memory#controlling-memory-writes-write_approval)。

## 上下文文件截断

控制 Hermes 在应用头/尾截断之前从每个自动上下文文件中加载多少内容。这适用于注入到系统提示中的文件，如 `SOUL.md`、`.hermes.md`、`AGENTS.md`、`CLAUDE.md` 和 `.cursorrules`。它**不影响** `read_file` 工具。

```yaml
context_file_max_chars: 20000  # 默认
```

当你有意保留较大的身份或项目上下文文件，并运行具有足够上下文窗口的模型来承载它们时，请提高此值：

```yaml
context_file_max_chars: 25000
```

## 文件读取安全

控制单个 `read_file` 调用可以返回多少内容。超过限制的读取将被拒绝，并返回错误，告知代理使用 `offset` 和 `limit` 获取较小的范围。这可以防止单个读取压缩后的 JS 包或大型数据文件淹没上下文窗口。

```yaml
file_read_max_chars: 100000  # 默认 — ~25-35K 个令牌
```

如果你使用具有大上下文窗口的模型并且经常读取大文件，请提高此值。对于小上下文模型，降低此值以保持读取效率：

```yaml
# 大上下文模型（200K+）
file_read_max_chars: 200000

# 小型本地模型（16K 上下文）
file_read_max_chars: 30000
```

代理还会自动对文件读取进行去重 — 如果同一文件区域被读取两次并且文件未更改，则会返回一个轻量级存根，而不是重新发送内容。这在上下文压缩时重置，因此代理可以在其内容被摘要掉后重新读取文件。

## 工具输出截断限制

三个相关的上限控制工具返回的原始输出量，超过后 Hermes 会截断：

```yaml
tool_output:
  max_bytes: 50000        # 终端输出上限（字符数）
  max_lines: 2000         # read_file 分页上限
  max_line_length: 2000   # read_file 带行号视图中的每行上限
```

- **`max_bytes`** — 当 `terminal` 命令产生的合并 stdout/stderr 超过此字符数时，Hermes 保留前 40% 和后 60%，并在它们之间插入 `[OUTPUT TRUNCATED]` 通知。默认值 `50000`（≈ 在典型分词器上为 12-15K 个令牌）。
- **`max_lines`** — 单个 `read_file` 调用的 `limit` 参数的上限。超出此上限的请求会被限制，以便单次读取不会淹没上下文窗口。默认值 `2000`。
- **`max_line_length`** — 当 `read_file` 发出带行号视图时应用的每行上限。超过此长度的行会被截断为该字符数，后跟 `... [truncated]`。默认值 `2000`。

对于具有大上下文窗口且每次调用可以承受更多原始输出的模型，请提高限制。对于小型上下文模型，降低限制以保持工具结果紧凑：

```yaml
# 大上下文模型（200K+）
tool_output:
  max_bytes: 150000
  max_lines: 5000

# 小型本地模型（16K 上下文）
tool_output:
  max_bytes: 20000
  max_lines: 500
```

## 全局工具集禁用

要在 CLI 和每个网关平台上一次抑制特定工具集，请在 `agent.disabled_toolsets` 下列出它们的名称：

```yaml
agent:
  disabled_toolsets:
    - memory       # 隐藏内存工具 + MEMORY_GUIDANCE 注入
    - web          # 任何地方都不使用 web_search / web_extract
```

这适用于**每个平台工具配置之后**（由 `hermes tools` 写入的 `platform_toolsets`），因此此处列出的工具集始终被移除 — 即使平台的保存配置仍然列出它。当你想要一个单一的开关来“在所有地方关闭 X”，而不是在 `hermes tools` UI 中编辑 15 多个平台行时，请使用此方法。

保持列表为空或省略该键，则无操作。

## Git 工作树隔离

启用隔离的 git 工作树以便在同一仓库上并行运行多个代理：

```yaml
worktree: true    # 始终创建工作树（等同于 hermes -w）
# worktree: false # 默认 — 仅当传递 -w 标志时
```

启用后，每个 CLI 会话会在 `.worktrees/` 下创建一个带有自己分支的新工作树。代理可以编辑文件、提交、推送和创建 PR，而不会相互干扰。干净的工作树在退出时被删除；脏的工作树保留以便手动恢复。

默认情况下，新的工作树从**最新获取的远程尖端**（当前分支的上游，否则是远程的默认分支）分支，因此它从项目的最新状态开始，而不是从本地克隆可能过时的 `HEAD` 开始。这保持了 PR 的差异范围仅限于实际更改，而不是继承本地克隆落后的任何内容。设置 `worktree_sync: false` 以从本地 `HEAD` 分支 — 对于离线情况或当你故意希望克隆的确切当前状态作为基础时很有用。如果无法访问远程，则自动回退到本地 `HEAD`。

```yaml
worktree_sync: true    # 默认 — 从获取的远程尖端分支
# worktree_sync: false # 从本地 HEAD 分支（离线/固定基础）
```

你还可以通过在仓库根目录中放置 `.worktreeinclude` 来列出要复制到工作树中的 gitignore 文件：

```
# .worktreeinclude
.env
.venv/
node_modules/
```

## 上下文压缩

Hermes 会自动压缩长对话，以保持在模型上下文窗口内。压缩摘要器是一个单独的 LLM 调用 — 你可以将其指向任何提供商或端点。

所有压缩设置都位于 `config.yaml` 中（没有环境变量）。

### 完整参考

```yaml
compression:
  enabled: true                                     # 切换压缩开/关
  threshold: 0.50                                   # 在上下文限制的此百分比时压缩
  target_ratio: 0.20                                # 要保留为最近尾部的阈值分数
  protect_last_n: 20                                # 保持未压缩的最近消息的最小数量
  protect_first_n: 3                                # 跨压缩固定的非系统头部消息（0 = 不固定任何内容）
  hygiene_hard_message_limit: 5000                  # 网关安全阀 — 见下文

# 摘要模型/提供商在 auxiliary 下配置：
auxiliary:
  compression:
    model: ""                                       # 空 = 使用主聊天模型。覆盖为例如 "google/gemini-3-flash-preview" 以实现更便宜/更快的压缩。
    provider: "auto"                                # 提供商："auto"、"openrouter"、"nous"、"codex"、"main" 等。
    base_url: null                                  # 自定义 OpenAI 兼容端点（覆盖提供商）
```

:::info 旧配置迁移
具有 `compression.summary_model`、`compression.summary_provider` 和 `compression.summary_base_url` 的旧配置会在首次加载时自动迁移到 `auxiliary.compression.*`（配置版本 17）。无需手动操作。
:::

`hygiene_hard_message_limit` 是仅限网关的**预压缩安全阀**。它的存在是为了打破死亡螺旋：当 API 调用在过大的会话中持续断开时，网关永远不会收到令牌使用数据，因此基于令牌的阈值无法触发，导致记录不断增长，断开情况恶化。这个基于计数的下限仅根据消息计数触发（始终已知，无论 API 失败如何），以强制压缩并恢复会话。默认值 `5000` — 远高于任何正常会话，包括大上下文（1M+）模型执行数千次短轮次的情况，这些模型在令牌阈值上压缩远早于此。对于不寻常的平台进一步提高它，降低它以强制更积极的压缩。在正在运行的网关上编辑此值会在下一条消息时生效（见下文）。

`protect_first_n` 控制每次压缩时固定的**非系统**头部消息数量。默认值 `3` — 开场的用户/助手交换在每次摘要器传递中存活，因此原始目标保持可见。在长时间运行的滚动压缩会话中，当开场轮次不再相关时，设置 `protect_first_n: 0` 以仅固定系统提示 + 摘要 + 尾部。系统提示本身始终被保留，无论此设置如何。

:::tip 网关热重载压缩和上下文长度
从最近的版本开始，在正在运行的网关上编辑 `config.yaml` 中的 `model.context_length` 或任何 `compression.*` 键，会在下一条消息时生效 — 无需重启网关、无需 `/reset`、无需轮换会话。缓存的代理签名包含这些键，因此网关在检测到更改时会透明地重建代理。API 密钥和工具/技能配置仍然需要通常的重载路径。
:::

### 常见设置

**默认（自动检测）— 无需配置：**
```yaml
compression:
  enabled: true
  threshold: 0.50
```
使用你的主提供商和主模型。如果你想在比主聊天模型更便宜的模型上进行压缩，可以按任务覆盖（例如 `auxiliary.compression.provider: openrouter` + `model: google/gemini-2.5-flash`）。

**强制使用特定提供商**（基于 OAuth 或 API 密钥）：
```yaml
auxiliary:
  compression:
    provider: nous
    model: gemini-3-flash
```
适用于任何提供商：`nous`、`openrouter`、`codex`、`anthropic`、`main` 等。

**自定义端点**（自托管、Ollama、zai、DeepSeek 等）：
```yaml
auxiliary:
  compression:
    model: glm-4.7
    base_url: https://api.z.ai/api/coding/paas/v4
```
指向自定义 OpenAI 兼容端点。使用 `OPENAI_API_KEY` 进行认证。

### 三个旋钮如何相互作用

| `auxiliary.compression.provider` | `auxiliary.compression.base_url` | 结果 |
|---------------------|---------------------|--------|
| `auto`（默认） | 未设置 | 自动检测最佳可用提供商 |
| `nous` / `openrouter` 等 | 未设置 | 强制使用该提供商，使用其认证 |
| 任意 | 设置 | 直接使用自定义端点（忽略提供商） |

:::warning 摘要模型上下文长度要求
摘要模型**必须**具有至少与你的主代理模型一样大的上下文窗口。压缩器将对话的完整中间部分发送给摘要模型 — 如果该模型的上下文窗口小于主模型的上下文窗口，摘要调用将因上下文长度错误而失败。当发生这种情况时，中间轮次**会被丢弃而没有摘要**，静默丢失对话上下文。如果你覆盖模型，请验证其上下文长度满足或超过你的主模型。
:::

## 上下文引擎

上下文引擎控制在接近模型令牌限制时如何管理对话。内置的 `compressor` 引擎使用有损摘要（参见 [上下文压缩](/developer-guide/context-compression-and-caching)）。插件引擎可以用替代策略替换它。

```yaml
context:
  engine: "compressor"    # 默认 — 内置有损摘要
```

要使用插件引擎（例如 LCM 用于无损上下文管理）：

```yaml
context:
  engine: "lcm"          # 必须与插件名称匹配
```

插件引擎**永远不会自动激活** — 你必须显式设置 `context.engine` 为插件名称。可用引擎可以通过 `hermes plugins` → Provider Plugins → Context Engine 浏览和选择。

有关记忆插件的类似单选系统，请参见 [记忆提供商](/user-guide/features/memory-providers)。

## 迭代预算压力

当代理处理具有许多工具调用的复杂任务时，它可能会在未意识到预算不足的情况下耗尽迭代预算（默认：90 轮）。预算压力会在接近限制时自动警告模型：

| 阈值 | 级别 | 模型看到的内容 |
|-----------|-------|---------------------|
| **70%** | 提醒 | `[BUDGET: 63/90. 27 iterations left. Start consolidating.]` |
| **90%** | 警告 | `[BUDGET WARNING: 81/90. Only 9 left. Respond NOW.]` |

警告被注入到最后一个工具结果的 JSON 中（作为 `_budget_warning` 字段），而不是作为单独的消息 — 这保留了提示缓存，并且不会破坏对话结构。

```yaml
agent:
  max_turns: 90                # 每次对话轮次的最大迭代次数（默认：90）
  api_max_retries: 3           # 在备用启用之前每个提供商的重试次数（默认：3）
```

预算压力默认启用。代理作为工具结果的一部分自然会看到警告，鼓励它整合工作并在迭代耗尽之前响应。

当迭代预算完全耗尽时，CLI 会向用户显示通知：`⚠ Iteration budget reached (90/90) — response may be incomplete`。如果预算在活动工作期间耗尽，代理会在停止之前生成已完成工作的摘要。

`agent.api_max_retries` 控制 Hermes 在临时错误（速率限制、连接断开、5xx）上重试提供商 API 调用的次数，**然后**才进行备用提供商切换。默认值为 `3` — 总共四次尝试。如果你配置了 [备用提供商](/user-guide/features/fallback-providers) 并且希望更快地故障转移，请将其降至 `0`，以便主提供商上的第一个临时错误立即移交给备用，而不是在故障端点上一再重试。

### API 超时

Hermes 对流式传输有单独的超时层，此外还有非流式调用的陈旧检测器。只有当你将本地提供商保留在隐式默认值时，陈旧检测器才会自动调整。

| 超时 | 默认值 | 本地提供商 | 配置 / 环境变量 |
|---------|---------|----------------|--------------|
| Socket 读取超时 | 120 秒 | 自动提升到 1800 秒 | `HERMES_STREAM_READ_TIMEOUT` |
| 陈旧流检测 | 180 秒 | 自动禁用 | `HERMES_STREAM_STALE_TIMEOUT` |
| 陈旧非流检测 | 300 秒 | 隐式时自动禁用 | `providers.<id>.stale_timeout_seconds` 或 `HERMES_API_CALL_STALE_TIMEOUT` |
| API 调用（非流式） | 1800 秒 | 不变 | `providers.<id>.request_timeout_seconds` / `timeout_seconds` 或 `HERMES_API_TIMEOUT` |

**Socket 读取超时**控制 httpx 等待提供商的下一个数据块的时间。本地 LLM 在大上下文上可能需要几分钟的预填充才能产生第一个令牌，因此当检测到本地端点时，Hermes 会将此时间提升到 30 分钟。如果你显式设置 `HERMES_STREAM_READ_TIMEOUT`，则无论端点检测如何，该值始终被使用。

**陈旧流检测**会杀死接收到 SSE 保活 ping 但没有实际内容的连接。对于本地提供商，这被完全禁用，因为它们在预填充期间不会发送保活 ping。

**陈旧非流检测**会杀死在太长时间内没有产生响应的非流式调用。默认情况下，Hermes 在本地端点上禁用此功能，以避免在长预填充期间出现误报。如果你显式设置 `providers.<id>.stale_timeout_seconds`、`providers.<id>.models.<model>.stale_timeout_seconds` 或 `HERMES_API_CALL_STALE_TIMEOUT`，则该显式值即使在本地端点上也会被遵守。

## 上下文压力警告

与迭代预算压力分开，上下文压力跟踪对话接近**压缩阈值**的程度 — 上下文压缩触发以总结较旧消息的点。这有助于你和代理了解对话何时变长。

| 进度 | 级别 | 发生了什么 |
|----------|-------|-------------|
| **≥ 60%** 到阈值 | 信息 | CLI 显示青色进度条；网关发送信息通知 |
| **≥ 85%** 到阈值 | 警告 | CLI 显示粗体黄色条；网关警告压缩即将发生 |

在 CLI 中，上下文压力显示为工具输出源中的进度条：

```
  ◐ context ████████████░░░░░░░░ 62% to compaction  48k threshold (50%) · approaching compaction
```

在消息平台上，会发送纯文本通知：

```
◐ Context: ████████████░░░░░░░░ 62% to compaction (threshold: 50% of window).
```

如果自动压缩被禁用，警告会告知你上下文可能被截断。

上下文压力是自动的 — 无需配置。它纯粹作为面向用户的通知触发，并且不会修改消息流或将任何内容注入模型的上下文。

## 凭据池策略

当你有多个相同提供商的 API 密钥或 OAuth 令牌时，配置轮换策略：

```yaml
credential_pool_strategies:
  openrouter: round_robin    # 均匀循环使用密钥
  anthropic: least_used      # 始终选择最少使用的密钥
```

选项：`fill_first`（默认）、`round_robin`、`least_used`、`random`。有关完整文档，请参见 [凭据池](/user-guide/features/credential-pools)。

## 提示缓存

当活动提供商支持时，Hermes 会自动打开跨会话提示缓存 — 无需用户配置。

对于 Claude 在**原生 Anthropic**、**OpenRouter** 和 **Nous Portal** 上，Hermes 会在系统提示和技能块上附加具有 1 小时 TTL（`ttl: "1h"`）的 `cache_control` 断点。一个小时内第一次发送支付完整输入费率；同一小时内跨任何会话的后续发送从缓存中以折扣的缓存读取费率拉取。这意味着系统提示、加载的技能内容以及任何长上下文包含的早期部分会在 `hermes` 会话之间以及分叉的子代理之间在第一个小时内被重用。

Qwen Cloud（阿里云 DashScope）上游将缓存 TTL 限制为 5 分钟，因此 Hermes 在那里使用 5 分钟断点 TTL。其他通过第三方的 Claude 路径（AWS Bedrock、Azure Foundry）回退到提供商自己的缓存默认值。xAI Grok 使用单独的会话固定 conversation-id 机制 — 请参见 [xAI 提示缓存](/integrations/providers#xai-grok--responses-api--prompt-caching)。

没有禁用它的旋钮 — 缓存始终开启，即使在单轮对话中也能省钱，因为仅系统提示就占了输入令牌数量的相当大一部分。

## 辅助模型

Hermes 使用“辅助”模型进行图像分析、网页摘要、浏览器截图分析、会话标题生成和上下文压缩等辅助任务。默认情况下（`auxiliary.*.provider: "auto"`），Hermes 将每个辅助任务路由到你的**主聊天模型** — 与你在 `hermes model` 中选择的提供商/模型相同。你不需要配置任何东西即可开始使用，但请注意，在昂贵的推理模型（Opus、MiniMax M2.7 等）上，辅助任务会增加显著的成本。如果你希望无论主模型如何，辅助任务都便宜且快速，可以显式设置 `auxiliary.<task>.provider` 和 `auxiliary.<task>.model`（例如，在 OpenRouter 上使用 Gemini Flash 进行视觉和网页提取）。

:::note 为什么“auto”使用你的主模型
早期的版本将聚合器用户（OpenRouter、Nous Portal）分离到提供商的便宜默认值。这令人惊讶 — 为聚合器订阅付费的用户会看到不同的模型处理他们的辅助流量。`auto` 现在对每个人都使用主模型，并且 `config.yaml` 中的每个任务覆盖仍然优先（参见下面的 [完整辅助配置参考](#full-auxiliary-config-reference)）。
:::

### 交互式配置辅助模型

无需手动编辑 YAML，运行 `hermes model` 并从菜单中选择 **"Configure auxiliary models"**。你将获得一个交互式每个任务选择器：

```
$ hermes model
→ Configure auxiliary models

[ ] vision               currently: auto / main model
[ ] web_extract          currently: auto / main model
[ ] title_generation     currently: openrouter / google/gemini-3-flash-preview
[ ] tts_audio_tags       currently: auto / main model
[ ] compression          currently: auto / main model
[ ] approval             currently: auto / main model
[ ] triage_specifier     currently: auto / main model
[ ] kanban_decomposer    currently: auto / main model
[ ] profile_describer    currently: auto / main model
```

选择一个任务，选择一个提供商（OAuth 流程会打开浏览器；API 密钥提供商则提示），选择一个模型。更改会持久化到 `config.yaml` 中的 `auxiliary.<task>.*`。与主模型选择器相同的机制 — 无需学习额外语法。

### 视频教程

<div style={{position: 'relative', width: '100%', aspectRatio: '16 / 9', marginBottom: '1.5rem'}}>
  <iframe
    src="https://www.youtube.com/embed/NoF-YajElIM"
    title="Hermes Agent — Auxiliary Models Tutorial"
    style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 0}}
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowFullScreen
  />
</div>

### 通用配置模式

Hermes 中的每个模型槽 — 辅助任务、压缩、备用 — 都使用相同的三个旋钮：

| 键 | 功能 | 默认值 |
|-----|-------------|---------|
| `provider` | 用于认证和路由的提供商 | `"auto"` |
| `model` | 要请求的模型 | 提供商的默认模型 |
| `base_url` | 自定义 OpenAI 兼容端点（覆盖提供商） | 未设置 |

当设置了 `base_url` 时，Hermes 会忽略提供商并直接调用该端点（使用 `api_key` 或 `OPENAI_API_KEY` 进行认证）。当仅设置 `provider` 时，Hermes 使用该提供商的内置认证和基本 URL。

辅助任务可用的提供商：`auto`、`main`，以及[提供商注册表](/reference/environment-variables)中的任何提供商 — `openrouter`、`nous`、`openai-codex`、`copilot`、`copilot-acp`、`anthropic`、`gemini`、`qwen-oauth`、`zai`、`kimi-coding`、`kimi-coding-cn`、`minimax`、`minimax-cn`、`minimax-oauth`、`deepseek`、`nvidia`、`xai`、`xai-oauth`、`ollama-cloud`、`alibaba`、`bedrock`、`huggingface`、`arcee`、`xiaomi`、`kilocode`、`opencode-zen`、`opencode-go`、`azure-foundry` — 或来自 `custom_providers` 列表的任何命名自定义提供商（例如 `provider: "beans"`）。

:::tip MiniMax OAuth
`minimax-oauth` 通过浏览器 OAuth 登录（无需 API 密钥）。运行 `hermes model` 并选择 **MiniMax (OAuth)** 进行认证。辅助任务会自动使用 `MiniMax-M2.7-highspeed`。参见 [MiniMax OAuth 指南](../guides/minimax-oauth.md)。
:::

:::tip xAI Grok OAuth
`xai-oauth` 为 SuperGrok 和 X Premium+ 订阅者通过浏览器 OAuth 登录（无需 API 密钥）。运行 `hermes model` 并选择 **xAI Grok OAuth (SuperGrok / Premium+)** 进行认证。相同的 OAuth 令牌在每次直接到 xAI 的交互（聊天、辅助任务、TTS、图像生成、视频生成、转录）中被重用。参见 [xAI Grok OAuth 指南](../guides/xai-grok-oauth.md)，如果 Hermes 在远程主机上，请参见 [通过 SSH / 远程主机的 OAuth](../guides/oauth-over-ssh.md)。
:::

:::warning `"main"` 仅用于辅助任务
`"main"` 提供商选项意味着“使用我的主代理使用的任何提供商” — 它仅在 `auxiliary:`、`compression:` 和主备用条目（`fallback_providers:` 或旧版 `fallback_model:`）中有效。对于你的顶级 `model.provider` 设置，它**不是**有效值。如果你使用自定义 OpenAI 兼容端点，请在 `model:` 部分中设置 `provider: custom`。有关所有主模型提供商选项，请参见 [AI 提供商](/integrations/providers)。
:::

### 完整辅助配置参考

```yaml
auxiliary:
  # 图像分析（vision_analyze 工具 + 浏览器截图）
  vision:
    provider: "auto"           # "auto"、"openrouter"、"nous"、"codex"、"main" 等
    model: ""                  # 例如 "openai/gpt-4o"、"google/gemini-2.5-flash"
    base_url: ""               # 自定义 OpenAI 兼容端点（覆盖提供商）
    api_key: ""                # base_url 的 API 密钥（回退到 OPENAI_API_KEY）
    timeout: 120               # 秒 — LLM API 调用超时；视觉有效负载需要宽松的超时
    download_timeout: 30       # 秒 — 图像 HTTP 下载；慢速连接时增加

  # 网页摘要提取 + 浏览器页面文本提取
  web_extract:
    provider: "auto"
    model: ""                  # 例如 "google/gemini-2.5-flash"
    base_url: ""
    api_key: ""
    timeout: 360               # 秒（6分钟）— 每次尝试的 LLM 摘要

  # 危险命令批准分类器
  approval:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30                # 秒

  # Gemini 3.1 TTS 隐藏音频标签插入
  tts_audio_tags:
    provider: "auto"
    model: ""                  # 空 = 主聊天模型
    base_url: ""
    api_key: ""
    timeout: 30

  # 上下文压缩超时（与 compression.* 配置分开）
  compression:
    timeout: 120               # 秒 — 压缩总结长对话，需要更多时间
    # fallback_chain:           # 可选 — 在速率限制/连接失败时尝试的提供商
    #   - provider: nous
    #     model: deepseek/deepseek-chat
    #   - provider: openrouter
    #     model: google/gemini-2.5-flash
    #     base_url: ""
    #     api_key: ""

  # 自动生成的会话标题。空的 language 跟随对话；设置例如 "English" 或 "Japanese" 以将标题固定为一种语言。
  title_generation:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30
    language: ""

  # 技能中心 — 技能匹配和搜索
  skills_hub:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30

  # MCP 工具调度
  mcp:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30

  # Kanban 分类指定器 — `hermes kanban specify <id>`（或仪表板上 Triage 列卡的 ✨ Specify 按钮）使用此槽将一句话扩展为具体规范并将任务提升到 `todo`。便宜快速的模型在这里效果很好；规范扩展很短，不需要推理深度。
  triage_specifier:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 120
```

:::tip
每个辅助任务都有可配置的 `timeout`（秒）。默认值：vision 120 秒，web_extract 360 秒，approval 30 秒，compression 120 秒。如果你为辅助任务使用慢速本地模型，请增加这些值。Vision 还有一个单独的 `download_timeout`（默认 30 秒）用于 HTTP 图像下载 — 对于慢速连接或自托管图像服务器，请增加此值。
:::

:::info
上下文压缩有自己用于阈值的 `compression:` 块，以及用于模型/提供商设置的 `auxiliary.compression:` 块 — 请参见上面的 [上下文压缩](#上下文压缩)。主备用链使用顶级的 `fallback_providers:` 列表 — 请参见 [备用提供商](/integrations/providers#备用提供商)。三者都遵循相同的 provider/model/base_url 模式。
:::

### 辅助任务的每个任务备用链

每个辅助任务可以选择定义一个 `fallback_chain` — 一个提供商/模型条目的列表，当主要辅助提供商因速率限制、连接问题或付款限制而失败时，Hermes 会尝试这些条目：

```yaml
auxiliary:
  compression:
    provider: openrouter
    model: openai/gpt-4o-mini
    fallback_chain:
      - provider: nous
        model: deepseek/deepseek-chat
      - provider: openrouter
        model: google/gemini-2.5-flash
```

当主要辅助提供商（`openrouter` / `openai/gpt-4o-mini`）返回速率限制、连接超时或需要付款的错误时，Hermes 会按顺序遍历 `fallback_chain`。它会跳过其提供商与已失败提供商匹配的条目，并尝试每个剩余条目，直到一个成功或链耗尽。如果所有备用都失败，Hermes 会回退到主代理模型作为最终安全网。

每个条目支持与任何辅助任务配置相同的三个旋钮：

| 键 | 描述 |
|-----|-------------|
| `provider` | 提供商名称（`nous`、`openrouter`、`anthropic`、`gemini`、`main` 等） |
| `model` | 该提供商的模型名称 |
| `base_url` | （可选）自定义 OpenAI 兼容端点 |

`fallback_chain` 可用于任何辅助任务 — `compression`、`vision`、`web_extract`、`approval`、`skills_hub`、`mcp` 等。

### OpenRouter 路由 & 辅助任务的 Pareto Code

当辅助任务解析到 OpenRouter（无论是显式还是通过 `provider: "main"` 而你的主代理在 OpenRouter 上）时，主代理的 `provider_routing` 和 `openrouter.min_coding_score` 设置**不会传播** — 按设计，每个辅助任务是独立的。要为特定辅助任务设置 OpenRouter 提供商偏好或使用 [Pareto Code 路由器](/integrations/providers#openrouter-pareto-code-router)，请通过 `extra_body` 按任务设置它们：

```yaml
auxiliary:
  compression:
    provider: openrouter
    model: openrouter/pareto-code         # 为此任务使用 Pareto Code 路由器
    extra_body:
      provider:                            # OpenRouter 提供商路由偏好
        order: [anthropic, google]         # 按顺序尝试这些提供商
        sort: throughput                   # 或 "price" | "latency"
        # only: [anthropic]                # 限制到特定提供商
        # ignore: [deepinfra]              # 排除特定提供商
      plugins:                             # OpenRouter Pareto Code 路由器旋钮
        - id: pareto-router
          min_coding_score: 0.5            # 0.0–1.0；更高 = 更强的编码器
```

其形状反映了 OpenRouter 在聊天完成请求体中接受的内容。Hermes 原样转发整个 `extra_body`，因此任何其他在 [openrouter.ai/docs](https://openrouter.ai/docs) 中记录的 OpenRouter 请求体字段都以相同方式工作。

### 更改视觉模型

使用 GPT-4o 而不是 Gemini Flash 进行图像分析：

```yaml
aux