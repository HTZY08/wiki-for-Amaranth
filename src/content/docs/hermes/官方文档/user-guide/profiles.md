```markdown
---
sidebar_position: 2
---

# 配置文件（Profiles）：运行多个代理（Agent）

在同一台机器上运行多个独立的Hermes代理——每个代理拥有独立的配置、API密钥、记忆、会话、技能（Skill）和网关状态。

## 什么是配置文件？

配置文件是一个独立的Hermes主目录。每个配置文件拥有自己的目录，包含独立的 `config.yaml`、`.env`、`SOUL.md`、记忆、会话、技能、定时任务和状态数据库。配置文件让你可以为不同用途运行独立的代理——例如代码助手、个人机器人、研究代理——而不会混淆Hermes的状态。

当你创建一个配置文件时，它会自动成为一条独立的命令。创建一个名为 `coder` 的配置文件，你就立即拥有了 `coder chat`、`coder setup`、`coder gateway start` 等命令。

## 快速开始

```bash
hermes profile create coder       # 创建配置文件 + "coder"命令别名
coder setup                       # 配置API密钥和模型
coder chat                        # 开始对话
```

就这样。`coder` 现在是一个独立的Hermes配置文件，拥有自己的配置、记忆和状态。

## 创建配置文件

:::tip
最快速的设置方式：在新配置文件内运行 `hermes setup --portal` 以同时配置模型和工具。详见 [Nous Portal](/integrations/nous-portal)。
:::

### 空白配置文件

```bash
hermes profile create mybot
```

创建一个新的配置文件，其中已植入捆绑技能。运行 `mybot setup` 来配置API密钥、模型和网关令牌。

如果你计划将此配置文件用作看板（Kanban）工作节点（或者希望看板编排器向其分配任务），请在创建时传入 `--description "<角色>"`，以便编排器了解其擅长的工作：

```bash
hermes profile create researcher --description "读取源代码和外部文档，撰写发现结果。"
```

你也可以稍后使用 `hermes profile describe` 设置或自动生成描述——完整的路由模型请参阅[看板指南](./features/kanban#auto-vs-manual-orchestration)。

### 仅克隆配置（`--clone`）

```bash
hermes profile create work --clone
```

将当前配置文件的 `config.yaml`、`.env`、`SOUL.md` 和技能复制到新配置文件中。API密钥、模型和能力相同，但会话和记忆是全新的。编辑 `~/.hermes/profiles/work/.env` 以设置不同的API密钥，或编辑 `~/.hermes/profiles/work/SOUL.md` 以设置不同的个性。

### 克隆全部（`--clone-all`）

```bash
hermes profile create backup --clone-all
```

复制**所有内容**——配置、API密钥、个性、所有记忆、技能、定时任务、插件。这是一个完整的可工作快照。不包括每个配置文件的历史记录（会话历史、`state.db`、`backups/`、`state-snapshots/`、`checkpoints/`）——这些属于源配置文件，可能达到数十GB。如需包含历史记录的完整备份，请使用 `hermes profile export` 或 `hermes backup`。

### 从特定配置文件克隆

```bash
hermes profile create work --clone-from coder
```

`--clone-from <源>` 直接选择源配置文件，并执行配置/技能/SOUL克隆。结合 `--clone-all` 可以进行该源配置文件的完整副本：

```bash
hermes profile create work-backup --clone-from coder --clone-all
```

:::tip Honcho记忆与配置文件
启用Honcho时，克隆操作会自动为新配置文件创建一个专用的AI同伴，同时共享同一个用户工作区。每个配置文件都会构建自己的观察和身份。详见 [Honcho —— 多代理 / 配置文件](./features/memory-providers.md#honcho)。
:::

## 使用配置文件

### 命令别名

每个配置文件会自动在 `~/.local/bin/<名称>` 获得一个命令别名：

```bash
coder chat                    # 与coder代理对话
coder setup                   # 配置coder的设置
coder gateway start           # 启动coder的网关
coder doctor                  # 检查coder的健康状态
coder skills list             # 列出coder的技能
coder config set model.default anthropic/claude-sonnet-4
```

该别名适用于所有hermes子命令——其底层只是 `hermes -p <名称>`。

### `-p` 标志

你也可以在任何命令中显式指定配置文件：

```bash
hermes -p coder chat
hermes --profile=coder doctor
hermes chat -p coder -q "hello"    # 可以在任何位置使用
```

### 粘性默认值（`hermes profile use`）

```bash
hermes profile use coder
hermes chat                   # 现在目标为coder
hermes tools                  # 配置coder的工具
hermes profile use default    # 切换回默认
```

设置一个默认值，使得普通的 `hermes` 命令指向该配置文件。类似于 `kubectl config use-context`。

### 知道你在哪里

CLI 始终显示当前活动的配置文件：

- **提示符**：`coder ❯` 而不是 `❯`
- **横幅**：启动时显示 `Profile: coder`
- **`hermes profile`**：显示当前配置文件的名称、路径、模型、网关状态

## 配置文件 vs 工作区 vs 沙箱

配置文件通常与工作区或沙箱混淆，但它们是不同的概念：

- **配置文件**为Hermes提供自己的状态目录：`config.yaml`、`.env`、`SOUL.md`、会话、记忆、日志、定时任务和网关状态。
- **工作区**或**工作目录**是终端命令的启动位置。这由 `terminal.cwd` 单独控制。
- **沙箱**用于限制文件系统访问。配置文件**不会**对代理进行沙箱化。

在默认的 `local` 终端后端，代理仍然拥有与用户账户相同的文件系统访问权限。配置文件不会阻止其访问配置文件目录之外的文件夹。

如果你希望配置文件从特定的项目文件夹启动，请在该配置文件的 `config.yaml` 中设置显式的绝对路径 `terminal.cwd`：

```yaml
terminal:
  backend: local
  cwd: /absolute/path/to/project
```

在本地后端使用 `cwd: "."` 表示“Hermes启动时的目录”，而不是“配置文件目录”。

另外请注意：

- `SOUL.md` 可以指导模型，但它不会强制工作区边界。
- 对 `SOUL.md` 的修改会在新会话中干净地生效。现有会话可能仍在使用旧的提示状态。
- 向模型询问“你在哪个目录？”不是可靠的隔离测试。如果你需要工具的可预测起始目录，请显式设置 `terminal.cwd`。

## 运行网关

每个配置文件作为独立进程运行自己的网关，拥有自己的机器人令牌：

```bash
coder gateway start           # 启动coder的网关
assistant gateway start       # 启动assistant的网关（独立进程）
```

### 不同的机器人令牌

每个配置文件拥有自己的 `.env` 文件。在每个文件中配置不同的Telegram/Discord/Slack机器人令牌：

```bash
# 编辑coder的令牌
nano ~/.hermes/profiles/coder/.env

# 编辑assistant的令牌
nano ~/.hermes/profiles/assistant/.env
```

### 安全性：令牌锁

如果两个配置文件意外使用了同一个机器人令牌，第二个网关将被阻止，并显示清晰的错误信息，指出冲突的配置文件名称。支持Telegram、Discord、Slack、WhatsApp和Signal。

### 持久化服务

```bash
coder gateway install         # 创建hermes-gateway-coder systemd/launchd服务
assistant gateway install     # 创建hermes-gateway-assistant服务
```

每个配置文件获得独立的服务名称。它们独立运行。

:::note 在官方Docker镜像内部
每个配置文件的网关由 [s6-overlay](https://github.com/just-containers/s6-overlay) 管理（容器中的PID 1），因此 `hermes profile create <名称>` 会自动在 `/run/service/gateway-<名称>/` 注册一个s6服务插槽。`hermes -p <名称> gateway start/stop/restart` 将调度到 `s6-svc` 而不是生成裸进程——崩溃会自动重启，`docker restart` 会保留之前正在运行的网关集合。详见[每个配置文件的网关管理](/user-guide/docker#per-profile-gateway-supervision)。
:::

## 配置配置文件

每个配置文件拥有自己的：

- **`config.yaml`** —— 模型、提供商、工具集、所有设置
- **`.env`** —— API密钥、机器人令牌
- **`SOUL.md`** —— 个性和指令

```bash
coder config set model.default anthropic/claude-sonnet-4
echo "你是一个专注的编码助手。" > ~/.hermes/profiles/coder/SOUL.md
```

如果你希望此配置文件默认在特定项目中工作，还要设置其自己的 `terminal.cwd`：

```bash
coder config set terminal.cwd /absolute/path/to/project
```

### 从仪表盘

[Web仪表盘](features/web-dashboard.md#managing-multiple-profiles) 是一个机器级别界面，可以通过侧边栏中的配置文件切换器管理**任何**配置文件的配置、API密钥、技能、MCP和模型——无需每个配置文件单独的仪表盘。 `coder dashboard` 会路由到机器仪表盘，并预选 `coder` 配置文件。仪表盘的“聊天”选项卡也会跟随切换器，在所选配置文件的主目录下启动对话。

注意：仪表盘“配置文件”页面上的“设为活动”是针对**未来CLI/网关运行**的粘性默认值（等同于 `hermes profile use`）——要从仪表盘编辑配置文件，请改用切换器。

## 更新

`hermes update` 只拉取一次代码（共享），并自动将新的捆绑技能同步到**所有**配置文件：

```bash
hermes update
# → 代码已更新（12次提交）
# → 技能同步：default（已是最新），coder（+2个新技能），assistant（+2个新技能）
```

用户修改过的技能永远不会被覆盖。

## 管理配置文件

```bash
hermes profile list           # 显示所有配置文件及其状态
hermes profile show coder     # 显示单个配置文件的详细信息
hermes profile rename coder dev-bot   # 重命名（更新别名和服务）
hermes profile export coder   # 导出为coder.tar.gz
hermes profile import coder.tar.gz   # 从归档导入
```

## 删除配置文件

```bash
hermes profile delete coder
```

这将停止网关，移除systemd/launchd服务，移除命令别名，并删除所有配置文件数据。你需要输入配置文件名称以确认。

使用 `--yes` 跳过确认：`hermes profile delete coder --yes`

:::note
你不能删除默认配置文件（`~/.hermes`）。要删除所有内容，请使用 `hermes uninstall`。
:::

## 选项卡补全

```bash
# Bash
eval "$(hermes completion bash)"

# Zsh
eval "$(hermes completion zsh)"
```

将上述行添加到你的 `~/.bashrc` 或 `~/.zshrc` 中以实现持久补全。可补全 `-p` 后的配置文件名称、配置文件子命令以及顶级命令。

## 工作原理

配置文件使用 `HERMES_HOME` 环境变量。当你运行 `coder chat` 时，包装脚本在启动hermes前将 `HERMES_HOME` 设置为 `~/.hermes/profiles/coder`。由于代码库中的119+个文件都通过 `get_hermes_home()` 解析路径，Hermes状态会自动限定在该配置文件的目录内——配置、会话、记忆、技能、状态数据库、网关PID、日志和定时任务。

这与终端工作目录是分开的。工具执行从 `terminal.cwd`（或在本地后端 `cwd: "."` 时从启动目录）开始，而非自动从 `HERMES_HOME` 开始。

在主机安装中，工具子进程默认保留真实操作系统用户的 `HOME`，因此 `~` 下现有的CLI凭据可以跨配置文件正常工作。配置文件数据通过 `HERMES_HOME` 隔离，而不是通过更改 `HOME`。容器后端仍使用 `{HERMES_HOME}/home` 保存持久化工具状态；需要严格按配置文件隔离工具配置的主机用户可以在 `config.yaml` 中设置 `terminal.home_mode: profile`。

这意味着容易混淆的两点：

- `HERMES_HOME` 是配置文件的边界。它控制Hermes的配置、`.env`、记忆、会话、技能、日志、定时任务、网关状态以及其他Hermes数据。
- `HOME` 是外部CLI所期望的操作系统/用户主目录。在主机安装中，Hermes默认将其保持为真实用户主目录，以便 `git`、`ssh`、`gh`、`az`、`npm`、Claude Code、Codex 等工具能找到它们在你普通shell中使用的相同凭据。

这样做的代价是，主机配置文件默认共享普通用户级别的CLI状态。如果你需要每个配置文件拥有独立的CLI身份，可以在该配置文件的 `config.yaml` 中设置 `terminal.home_mode: profile`。在此模式下，Hermes会以 `HOME={HERMES_HOME}/home` 启动工具子进程；然后你需要在该配置文件的主目录内初始化或链接配置文件特定的 `~/.ssh`、`~/.gitconfig`、`~/.config/gh`、云CLI认证、Claude/Codex认证、npm状态等文件。

Hermes还会将 `HERMES_REAL_HOME` 暴露给子进程，以便在启用 `home_mode: profile` 时脚本仍能找到实际账户的主目录。

默认配置文件就是 `~/.hermes` 本身。无需迁移——现有安装可以原样工作。

## 将配置文件作为发行版共享

你在某台机器上构建的配置文件可以打包为**git仓库**，并通过一条命令在另一台机器上安装——无论是你自己的工作站、队友的笔记本电脑，还是社区用户的环境。共享的软件包包括SOUL、配置、技能、定时任务和MCP连接。凭据、记忆和会话保留在每台机器本地。

```bash
# 从git仓库安装整个代理
hermes profile install github.com/you/research-bot --alias

# 稍后当作者发布新版本时更新（保留你的记忆和.env）
hermes profile update research-bot
```

请参阅 **[配置文件发行版：共享整个代理](./profile-distributions.md)** 以获取完整指南——包括编写、发布、更新语义、安全模型和用例。
```