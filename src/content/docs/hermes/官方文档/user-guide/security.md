--- frontmatter ---
---
sidebar_position: 8
title: "安全"
description: "安全模型、危险命令审批、用户授权、容器隔离及生产环境部署最佳实践"
---

--- body ---

# 安全

Hermes Agent 采用纵深防御安全模型设计。本章涵盖所有安全边界——从命令审批到容器隔离，再到消息平台上的用户授权。

## 概述

安全模型包含七个层级：

1. **用户授权（User authorization）**——谁可以与代理交互（允许列表、私聊配对）
2. **危险命令审批（Dangerous command approval）**——破坏性操作的人工参与审核
3. **容器隔离（Container isolation）**——使用加固设置的 Docker/Singularity/Modal 沙箱
4. **MCP 凭证过滤（MCP credential filtering）**——针对 MCP 子进程的环境变量隔离
5. **上下文文件扫描（Context file scanning）**——项目文件中的提示注入检测
6. **跨会话隔离（Cross-session isolation）**——会话之间无法访问彼此的数据或状态；cron 任务存储路径已加固以防范路径遍历攻击
7. **输入清理（Input sanitization）**——终端工具后端的工作目录参数根据允许列表进行验证，防止 shell 注入

## 危险命令审批

在执行任何命令之前，Hermes 会对照精心策划的危险模式列表进行检查。如果匹配，用户必须明确批准。

### 审批模式

审批系统支持三种模式，通过 `~/.hermes/config.yaml` 中的 `approvals.mode` 配置：

```yaml
approvals:
  mode: manual                    # manual | smart | off
  timeout: 60                     # 等待用户响应的秒数（默认：60）
  cron_mode: deny                 # deny | approve — cron 任务遇到危险命令时的行为
  mcp_reload_confirm: true        # /reload-mcp 在使 MCP 工具缓存失效前询问
  destructive_slash_confirm: true # /clear, /new, /reset, /undo 在丢弃状态前提示
```

所有键的完整列表：

| 键 | 默认值 | 控制内容 |
|---|---|---|
| `mode` | `manual` | 危险 shell 命令的审批策略——见下方表格。 |
| `timeout` | `60` | Hermes 在超时前等待审批回复的秒数。 |
| `cron_mode` | `deny` | [cron 任务](./features/cron.md) 在无头模式下触发危险命令提示时的行为。`deny` 阻止命令（代理必须寻找其他路径）；`approve` 在 cron 上下文中自动批准所有操作。 |
| `mcp_reload_confirm` | `true` | 为 `true` 时，执行 `/reload-mcp` 前会询问是否重建 MCP 工具集。重建会使提供程序提示缓存失效（工具架构位于系统提示中），因此下一条消息会重新发送完整的输入令牌。点击 **始终允许** 的用户会将此键设为 `false`。 |
| `destructive_slash_confirm` | `true` | 为 `true` 时，破坏性会话斜杠命令（`/clear`、`/new`、`/reset`、`/undo`）在丢弃对话状态前会提示。提供三个选项的对话框（允许一次 / 始终允许 / 取消），在 Telegram、Discord 和 Slack 上通过原生是/否按钮路由；其他平台使用文本回退。点击 **始终允许** 的用户会将此键设为 `false`。TUI 使用自身的模态覆盖层（设置 `HERMES_TUI_NO_CONFIRM=1` 可在 TUI 中选择退出）。 |

| 模式 | 行为 |
|------|----------|
| **manual**（默认） | 始终提示用户批准危险命令 |
| **smart** | 使用辅助 LLM 评估风险。低风险命令（例如 `python -c "print('hello')"`）自动批准。真正危险的命令自动拒绝。不确定的案例升级为手动提示。 |
| **off** | 禁用所有审批检查——相当于使用 `--yolo` 运行。所有命令直接执行，无需提示。 |

:::warning
设置 `approvals.mode: off` 会禁用所有安全提示。仅在受信任的环境（CI/CD、容器等）中使用。
:::

## YOLO 模式

YOLO 模式会绕过当前会话中**所有**危险命令审批提示。可通过三种方式激活：

1. **CLI 标志**：使用 `hermes --yolo` 或 `hermes chat --yolo` 启动会话
2. **斜杠命令**：在会话中输入 `/yolo` 来切换开启/关闭
3. **环境变量**：设置 `HERMES_YOLO_MODE=1`

`/yolo` 命令是一个**开关**——每次使用都会切换模式的开启或关闭：

```
> /yolo
  ⚡ YOLO 模式已开启——所有命令自动批准。请谨慎使用。

> /yolo
  ⚠ YOLO 模式已关闭——危险命令需要批准。
```

YOLO 模式在 CLI 和网关会话中均可用。内部实现中，它会设置 `HERMES_YOLO_MODE` 环境变量，在执行每个命令前进行检查。

当 YOLO 激活时，Hermes 会显示两个持久的视觉提醒，以便用户不会忘记审批提示被绕过：

- 当 YOLO 已激活时，会话启动时显示红色横幅行：`⚠ YOLO 模式——所有审批提示已被绕过`。当 YOLO 关闭时隐藏，以保持默认横幅简洁。
- 状态栏中显示 `⚠ YOLO` 片段，覆盖所有宽度级别，并在您切换 YOLO 开关时实时更新（富文本渲染器和纯文本回退）。

:::danger
YOLO 模式会禁用当前会话中**所有**危险命令安全检查——但**不包括**硬性阻止列表（见下文）。仅在您完全信任所生成的命令时使用（例如，在一次性环境中经过良好测试的自动化脚本）。
:::

对于破坏性会话斜杠命令（`/clear`、`/new`、`/reset`、`/undo`、`/quit --delete`——`/exit --delete` 是其别名），CLI 在执行前也会提示确认。参见[斜杠命令 —— 破坏性命令的确认提示](../reference/slash-commands.md#破坏性命令的确认提示)。

## 硬性阻止列表（始终启用的底层防线）

某些命令极具灾难性——不可逆的文件系统清除、fork 炸弹、直接块设备写入——Hermes **无论如何**都拒绝执行：

- `--yolo` / `/yolo` 已开启
- `approvals.mode: off`
- 以无头模式运行的 cron 任务 `approve` 模式
- 用户明确点击“始终允许”

阻止列表是 `--yolo` 之下的底层防线。它在审批层甚至看到命令之前就会触发，并且没有覆盖标志。目前涵盖的模式（非穷尽；与 `tools/approval.py::UNRECOVERABLE_BLOCKLIST` 保持一致）：

| 模式 | 为何是硬性 |
|---|---|
| `rm -rf /` 及明显变体 | 清除文件系统根目录 |
| `rm -rf --no-preserve-root /` | 明确的“我就是要根目录”变体 |
| `:(){ :\|:& };:`（bash fork 炸弹） | 使主机卡死直至重启 |
| 在已挂载的根设备上执行 `mkfs.*` | 格式化运行中的系统 |
| `dd if=/dev/zero of=/dev/sd*` | 将物理磁盘清零 |
| 将不受信任的 URL 通过管道传递给根文件系统顶层的 `sh` | 远程代码执行攻击向量，太宽泛无法批准 |

如果触发阻止列表，工具调用会向代理返回一个解释性错误，并且不执行任何操作。如果合法的工作流程需要这些命令之一（例如，您是擦除并重新安装管道的操作员），请在代理之外运行它。

### 审批超时

当出现危险命令提示时，用户有可配置的响应时间。如果在超时内未收到响应，命令默认被**拒绝**（失败安全）。

在 `~/.hermes/config.yaml` 中配置超时：

```yaml
approvals:
  timeout: 60  # 秒（默认：60）
```

### 触发审批的模式

以下模式会触发审批提示（定义在 `tools/approval.py` 中）：

| 模式 | 描述 |
|---------|-------------|
| `rm -r` / `rm --recursive` | 递归删除 |
| `rm ... /` | 在根路径中删除 |
| `chmod 777/666` / `o+w` / `a+w` | 全局/其他用户可写权限 |
| `chmod --recursive` 搭配不安全权限 | 递归全局/其他用户可写（长标志） |
| `chown -R root` / `chown --recursive root` | 递归将所有者改为 root |
| `mkfs` | 格式化文件系统 |
| `dd if=` | 磁盘复制 |
| `> /dev/sd` | 写入块设备 |
| `DROP TABLE/DATABASE` | SQL DROP |
| `DELETE FROM`（无 WHERE） | 无 WHERE 条件的 SQL DELETE |
| `TRUNCATE TABLE` | SQL TRUNCATE |
| `> /etc/` | 覆盖系统配置 |
| `systemctl stop/restart/disable/mask` | 停止/重启/禁用/屏蔽系统服务 |
| `kill -9 -1` | 杀死所有进程 |
| `pkill -9` | 强制杀死进程 |
| Fork 炸弹模式 | Fork 炸弹 |
| `bash -c` / `sh -c` / `zsh -c` / `ksh -c` | 通过 `-c` 标志执行 shell 命令（包括组合标志如 `-lc`） |
| `python -e` / `perl -e` / `ruby -e` / `node -c` | 通过 `-e`/`-c` 标志执行脚本 |
| `curl ... \| sh` / `wget ... \| sh` | 将远程内容通过管道传递给 shell |
| `bash <(curl ...)` / `sh <(wget ...)` | 通过进程替换执行远程脚本 |
| `tee` 到 `/etc/`、`~/.ssh/`、`~/.hermes/.env` | 通过 tee 覆盖敏感文件 |
| `>` / `>>` 到 `/etc/`、`~/.ssh/`、`~/.hermes/.env` | 通过重定向覆盖敏感文件 |
| `xargs rm` | xargs 与 rm 搭配 |
| `find -exec rm` / `find -delete` | 带破坏性操作的 find |
| `cp`/`mv`/`install` 到 `/etc/` | 将文件复制/移动到系统配置目录 |
| `sed -i` / `sed --in-place` 作用于 `/etc/` | 对系统配置进行原地编辑 |
| `pkill`/`killall` hermes/gateway | 防止自我终止 |
| 带 `&`/`disown`/`nohup`/`setsid` 的 `gateway run` | 防止在服务管理器之外启动网关 |

:::info
**容器绕过**：当在 `docker`、`singularity`、`modal` 或 `daytona` 后端运行时，危险命令检查会被**跳过**，因为容器本身就是安全边界。容器内的破坏性命令无法危害主机。
:::

### 审批流程（CLI）

在交互式 CLI 中，危险命令会显示内联审批提示：

```
  ⚠️  危险命令：递归删除
      rm -rf /tmp/old-project

      [o]一次  |  [s]会话  |  [a]始终  |  [d]拒绝

      选择 [o/s/a/D]：
```

四个选项：

- **一次**（once）——允许本次执行
- **会话**（session）——在本次会话剩余时间内允许此模式
- **始终**（always）——添加到永久允许列表（保存到 `config.yaml`）
- **拒绝**（deny，默认）——阻止命令

### 审批流程（网关/消息平台）

在消息平台上，代理将危险命令详细信息发送到聊天中，等待用户回复：

- 回复 **yes**、**y**、**approve**、**ok** 或 **go** 批准
- 回复 **no**、**n**、**deny** 或 **cancel** 拒绝

运行网关时，环境变量 `HERMES_EXEC_ASK=1` 会被自动设置。

### 永久允许列表

通过“始终”批准的命令会保存到 `~/.hermes/config.yaml`：

```yaml
# 永久允许的危险命令模式
command_allowlist:
  - rm
  - systemctl
```

这些模式在启动时加载，并在所有未来会话中静默批准。

:::tip
使用 `hermes config edit` 查看或从永久允许列表中移除模式。
:::

## 用户授权（网关）

当运行消息网关时，Hermes 通过分层授权系统控制谁可以与机器人交互。

### 授权检查顺序

`_is_user_authorized()` 方法按以下顺序检查：

1. **各平台允许所有标志**（例如 `DISCORD_ALLOW_ALL_USERS=true`）
2. **私聊配对已批准列表**（通过配对码批准的用户）
3. **平台特定的允许列表**（例如 `TELEGRAM_ALLOWED_USERS=12345,67890`）
4. **全局允许列表**（`GATEWAY_ALLOWED_USERS=12345,67890`）
5. **全局允许所有**（`GATEWAY_ALLOW_ALL_USERS=true`）
6. **默认：拒绝**

### 平台允许列表

在 `~/.hermes/.env` 中设置允许的用户 ID，用逗号分隔：

```bash
# 平台特定允许列表
TELEGRAM_ALLOWED_USERS=123456789,987654321
DISCORD_ALLOWED_USERS=111222333444555666
WHATSAPP_ALLOWED_USERS=15551234567
SLACK_ALLOWED_USERS=U01ABC123

# 跨平台允许列表（对所有平台检查）
GATEWAY_ALLOWED_USERS=123456789

# 各平台允许所有（使用需谨慎）
DISCORD_ALLOW_ALL_USERS=true

# 全局允许所有（使用需极其谨慎）
GATEWAY_ALLOW_ALL_USERS=true
```

:::warning
如果**未配置任何允许列表**且未设置 `GATEWAY_ALLOW_ALL_USERS`，则**所有用户都被拒绝**。网关会在启动时记录一条警告：

```
未配置用户允许列表。所有未经授权的用户将被拒绝。
请在 ~/.hermes/.env 中设置 GATEWAY_ALLOW_ALL_USERS=true 以开放访问，
或配置平台允许列表（例如 TELEGRAM_ALLOWED_USERS=your_id）。
```
:::

### 私聊配对系统

为了实现更灵活的授权，Hermes 包含一个基于代码的配对系统。无需预先提供用户 ID，未知用户会收到一个一次性配对码，由机器人所有者通过 CLI 批准。

**工作原理：**

1. 未知用户向机器人发送私聊消息
2. 机器人回复一个 8 字符的配对码
3. 机器人所有者运行 `hermes pairing approve <platform> <code>` 
4. 该用户在相应平台被永久批准

控制如何处理未授权的私聊消息，在 `~/.hermes/config.yaml` 中配置：

```yaml
unauthorized_dm_behavior: pair

whatsapp:
  unauthorized_dm_behavior: ignore
```

- `pair` 是聊天式私聊平台的默认行为。未授权的私聊会收到包含配对码的回复。
- `ignore` 静默丢弃未授权的私聊。
- 电子邮件默认使用 `ignore`，除非设置了 `platforms.email.unauthorized_dm_behavior: pair`，因为收件箱可能包含不相关的未读邮件。
- 平台部分会覆盖全局默认值，因此您可以在 Telegram 上保持配对，同时让 WhatsApp 保持静默。

**安全特性**（基于 OWASP + NIST SP 800-63-4 指南）：

| 特性 | 详情 |
|---------|---------|
| 代码格式 | 8 字符，来自 32 个不混淆字符的字母表（不含 0/O/1/I） |
| 随机性 | 加密安全（`secrets.choice()`） |
| 代码有效期 | 1 小时过期 |
| 速率限制 | 每个用户每 10 分钟 1 次请求 |
| 待处理限制 | 每个平台最多 3 个待处理代码 |
| 锁定 | 5 次失败的批准尝试 → 1 小时锁定 |
| 文件安全性 | 所有配对数据文件使用 `chmod 0600` |
| 日志记录 | 代码永远不会记录到标准输出 |

**配对 CLI 命令：**

```bash
# 列出待处理和已批准的用户
hermes pairing list

# 批准一个配对码
hermes pairing approve telegram ABC12DEF

# 撤销用户的访问权限
hermes pairing revoke telegram 123456789

# 清除所有待处理代码
hermes pairing clear-pending
```

**存储：** 配对数据存储在 `~/.hermes/pairing/` 中，每个平台有独立的 JSON 文件：
- `{platform}-pending.json` — 待处理的配对请求
- `{platform}-approved.json` — 已批准的用户
- `_rate_limits.json` — 速率限制和锁定跟踪

## 容器隔离

当使用 `docker` 终端后端时，Hermes 对每个容器应用严格的安全加固。

### Docker 安全标志

每个容器都附带这些标志运行（定义在 `tools/environments/docker.py` 中）：

```python
_BASE_SECURITY_ARGS = [
    "--cap-drop", "ALL",                          # 丢弃所有 Linux 能力
    "--cap-add", "DAC_OVERRIDE",                  # root 可以写入绑定挂载的目录
    "--cap-add", "CHOWN",                         # 包管理器需要文件所有权
    "--cap-add", "FOWNER",                        # 包管理器需要文件所有权
    "--security-opt", "no-new-privileges",         # 阻止提权
    "--pids-limit", "256",                         # 限制进程数量
    "--tmpfs", "/tmp:rw,nosuid,size=512m",         # 有大小限制的 /tmp
    "--tmpfs", "/var/tmp:rw,noexec,nosuid,size=256m",  # 无执行的 /var/tmp
]
```

`SETUID`/`SETGID` **不在**基础列表中——它们会条件性地添加，当容器以 root 启动且需要一个 init/entrypoint 来降低权限时（s6 权限降低路径）。当容器已经以非 root `--user` 运行时，它们会被跳过。`/run` tmpfs 也从基础列表中拆分出来，并根据镜像挂载（默认加固为 `noexec`，仅对从 `/run` 执行程序的 s6-overlay 镜像使用 `exec`）。

### 资源限制

容器资源可在 `~/.hermes/config.yaml` 中配置：

```yaml
terminal:
  backend: docker
  docker_image: "nikolaik/python-nodejs:python3.11-nodejs20"
  docker_forward_env: []  # 仅显式允许列表；空列表使密钥不进入容器
  container_cpu: 1        # CPU 核心数
  container_memory: 5120  # MB（默认 5GB）
  container_disk: 51200   # MB（默认 50GB，需要 XFS 上的 overlay2）
  container_persistent: true  # 跨会话持久化文件系统
```

### 文件系统持久化

- **持久化模式**（`container_persistent: true`）：将 `/workspace` 和 `/root` 从 `~/.hermes/sandboxes/docker/<task_id>/` 绑定挂载
- **临时模式**（`container_persistent: false`）：工作区使用 tmpfs——清理时所有内容丢失

:::tip
对于生产网关部署，使用 `docker`、`modal` 或 `daytona` 后端来隔离代理命令与主机系统。这完全消除了危险命令审批的需求。
:::

:::warning
如果您将名称添加到 `terminal.docker_forward_env`，这些变量会被有意注入到容器中供终端命令使用。这对于任务特定凭据（如 `GITHUB_TOKEN`）很有用，但也意味着容器中运行的代码可以读取并泄露它们。
:::

## 终端后端安全对比

| 后端 | 隔离性 | 危险命令检查 | 最佳适用场景 |
|---------|-----------|-------------------|----------|
| **local** | 无——在主机上运行 | ✅ 是 | 开发、受信任用户 |
| **ssh** | 远程机器 | ✅ 是 | 在独立服务器上运行 |
| **docker** | 容器 | ❌ 跳过（容器即边界） | 生产网关 |
| **singularity** | 容器 | ❌ 跳过 | HPC 环境 |
| **modal** | 云沙箱 | ❌ 跳过 | 可扩展的云隔离 |
| **daytona** | 云沙箱 | ❌ 跳过 | 持久化云工作区 |

## 环境变量传递 {#environment-variable-passthrough}

`execute_code` 和 `terminal` 都会从子进程中剥离敏感环境变量，以防止 LLM 生成的代码泄露凭据。然而，声明了 `required_environment_variables` 的技能（Skill）需要合法访问这些变量。

### 工作原理

两种机制允许特定变量通过沙箱过滤器：

**1. 技能作用域传递（自动）**

当技能被加载（通过 `skill_view` 或 `/skill` 命令）并声明了 `required_environment_variables` 时，环境中实际设置的任何此类变量都会自动注册为传递变量。缺失的变量（仍处于需要设置状态）**不会**被注册。

```yaml
# 在技能的 SKILL.md 前置元数据中
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API key
    help: Get a key from https://developers.google.com/tenor
```

加载此技能后，`TENOR_API_KEY` 会传递到 `execute_code`、`terminal`（本地）**以及远程后端（Docker、Modal）**——无需手动配置。

:::info Docker 和 Modal
在 v0.5.1 之前，Docker 的 `forward_env` 是与技能传递分离的系统。现在它们已合并——技能声明的环境变量会自动转发到 Docker 容器和 Modal 沙箱中，无需手动添加到 `docker_forward_env`。
:::

**2. 基于配置的传递（手动）**

对于未由任何技能声明的环境变量，在 `config.yaml` 的 `terminal.env_passthrough` 中添加：

```yaml
terminal:
  env_passthrough:
    - MY_CUSTOM_KEY
    - ANOTHER_TOKEN
```

### 凭据文件传递（OAuth 令牌等） {#credential-file-passthrough}

某些技能在沙箱中需要**文件**（不仅仅是环境变量）——例如，Google Workspace 将 OAuth 令牌存储为活跃配置文件 `HERMES_HOME` 下的 `google_token.json`。技能在前置元数据中声明这些文件：

```yaml
required_credential_files:
  - path: google_token.json
    description: Google OAuth2 token（由设置脚本创建）
  - path: google_client_secret.json
    description: Google OAuth2 客户端凭据
```

加载时，Hermes 会检查这些文件是否存在于活跃配置文件的 `HERMES_HOME` 中，并注册它们以供挂载：

- **Docker**：只读绑定挂载（`-v host:container:ro`）
- **Modal**：在沙箱创建时挂载，并在每个命令前同步（处理会话中的 OAuth 设置）
- **本地**：无需操作（文件已可访问）

您也可以在 `config.yaml` 中手动列出凭据文件：

```yaml
terminal:
  credential_files:
    - google_token.json
    - my_custom_oauth_token.json
```

路径相对于 `~/.hermes/`。文件被挂载到容器内的 `/root/.hermes/`。此列表由 `tools/credential_files.py` 读取（`terminal.credential_files`）——它位于 `terminal:` 块下，但由凭据文件模块加载，而非核心终端后端，因此不包含在捆绑的 `DEFAULT_CONFIG` 快照中。

### 各沙箱过滤的内容

| 沙箱 | 默认过滤 | 传递覆盖 |
|---------|---------------|---------------------|
| **execute_code** | 阻止变量名中包含 `KEY`、`TOKEN`、`SECRET`、`PASSWORD`、`CREDENTIAL`、`PASSWD`、`AUTH` 的变量；仅允许安全前缀变量通过 | ✅ 传递变量绕过两项检查 |
| **terminal**（本地） | 阻止显式的 Hermes 基础设施变量（提供程序密钥、网关令牌、工具 API 密钥） | ✅ 传递变量绕过阻止列表 |
| **terminal**（Docker） | 默认无主机环境变量 | ✅ 传递变量 + `docker_forward_env` 通过 `-e` 转发 |
| **terminal**（Modal） | 默认无主机环境/文件 | ✅ 凭据文件被挂载；通过同步传递环境变量 |
| **MCP** | 阻止除安全系统变量 + 显式配置的 `env` 之外的所有内容 | ❌ 不受传递影响（改为使用 MCP 的 `env` 配置） |

### 安全考量

- 传递仅影响您或您的技能显式声明的变量——对于任意 LLM 生成的代码，默认安全态势保持不变
- 凭据文件以**只读**方式挂载到 Docker 容器中
- 技能护卫（Guard）在安装前会扫描技能内容，查找可疑的 env 访问模式
- 缺失/未设置的变量永远不会被注册（不存在的东西无法泄露）
- Hermes 基础设施密钥（提供程序 API 密钥、网关令牌）绝不应添加到 `env_passthrough` 中——它们有专门的机制

## MCP 凭据处理

MCP（模型上下文协议）服务器子进程接收**经过过滤的环境**，以防止意外凭据泄露。

### 安全环境变量

只有以下变量从主机传递到 MCP stdio 子进程：

```
PATH, HOME, USER, LANG, LC_ALL, TERM, SHELL, TMPDIR
```

以及任何 `XDG_*` 变量。所有其他环境变量（API 密钥、令牌、密钥）都会被**剥离**。

在 MCP 服务器的 `env` 配置中显式定义的变量会被传递：

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_..."  # 仅此变量被传递
```

### 凭据编辑

来自 MCP 工具的错误消息会在返回给 LLM 之前进行清理。以下模式会被替换为 `[REDACTED]`：

- GitHub PAT（`ghp_...`）
- OpenAI 风格的密钥（`sk-...`）
- Bearer 令牌
- `token=`、`key=`、`API_KEY=`、`password=`、`secret=` 参数

### 网站访问策略

您可以通过 web 和浏览器工具限制代理可以访问的网站。这对于防止代理访问内部服务、管理面板或其他敏感 URL 非常有用。

```yaml
# 在 ~/.hermes/config.yaml 中
security:
  website_blocklist:
    enabled: true
    domains:
      - "*.internal.company.com"
      - "admin.example.com"
    shared_files:
      - "/etc/hermes/blocked-sites.txt"
```

当请求被阻止的 URL 时，工具会返回一个错误，说明该域名已被策略阻止。阻止列表在 `web_search`、`web_extract`、`browser_navigate` 以及所有支持 URL 的工具中强制执行。

详见配置指南中的[网站阻止列表](/user-guide/configuration#网站阻止列表)。

### SSRF 保护

所有支持 URL 的工具（web 搜索、web 提取、视觉、浏览器）在获取 URL 之前都会对其进行验证，以防止服务端请求伪造攻击。被阻止的地址包括：

- **私有网络**（RFC 1918）：`10.0.0.0/8`、`172.16.0.0/12`、`192.168.0.0/16`
- **回环**：`127.0.0.0/8`、`::1`
- **链路本地**：`169.254.0.0/16`（包括 `169.254.169.254` 的云元数据）
- **CGNAT / 共享地址空间**（RFC 6598）：`100.64.0.0/10`（Tailscale、WireGuard VPN）
- **云元数据主机名**：`metadata.google.internal`、`metadata.goog`
- **保留、组播和未指定地址**

SSRF 保护在面向互联网的使用中始终处于活动状态，DNS 失败被视为已阻止（失败安全）。重定向链在每个跳点都会重新验证，以防止基于重定向的绕过。

#### 有意允许私有 URL

某些设置合法地需要访问私有/内部 URL——将 `home.arpa` 解析为 RFC 1918 地址的家庭网络、仅限局域网的 Ollama/llama.cpp 端点、内部 Wiki、云元数据调试等。针对这些情况，有一个全局选择退出选项：

```yaml
security:
  allow_private_urls: true   # 默认：false
```

启用后，web 工具、浏览器、视觉 URL 获取以及网关媒体下载不再拒绝 RFC 1918 / 回环 / 链路本地 / CGNAT / 云元数据目标。**这是一个有意的信任边界**——只有在那些代理针对本地网络运行任意提示注入的 URL 是可接受风险的机器上才启用它。面向公共的网关应保持关闭。

主机子字符串守卫（即使底层 IP 是公共的，也会阻止看似相似的 Unicode 域名技巧）无论此设置如何都保持开启。

### Tirith 预执行安全扫描

Hermes 集成了 [tirith](https://github.com/sheeki03/tirith)，用于在命令执行前进行内容级扫描。Tirith 可以检测纯模式匹配遗漏的威胁：

- 同形 URL 欺骗（国际化域名攻击）
- 管道到解释器的模式（`curl | bash`、`wget | sh`）
- 终端注入攻击

Tirith 在首次使用时从 GitHub 发布版本自动安装，并进行 SHA-256 校验和验证（如果 cosign 可用，则进行 cosign 来源验证）。

```yaml
# 在 ~/.hermes/config.yaml 中
security:
  tirith_enabled: true       # 启用/禁用 tirith 扫描（默认：true）
  tirith_path: "tirith"      # tirith 二进制文件的路径（默认：PATH 查找）
  tirith_timeout: 5          # 子进程超时秒数
  tirith_fail_open: true     # 当 tirith 不可用时允许执行（默认：true）
```

当 `tirith_fail_open` 为 `true`（默认）时，如果 tirith 未安装或超时，命令会继续执行。在高安全环境中设置为 `false`，以在 tirith 不可用时阻止命令执行。

Tirith 提供预构建的 Linux（x86_64 / aarch64）和 macOS（x86_64 / arm64）二进制文件。在没有预构建二进制文件的平台（Windows 等）上，tirith 会被静默跳过——模式匹配守卫仍会运行，CLI 不会显示“不可用”横幅。要在 Windows 上使用 tirith，请在 WSL 下运行 Hermes。

Tirith 的判定与审批流程集成：安全命令通过，而可疑或被阻止的命令会触发用户批准，并显示完整的 tirith 发现（严重性、标题、描述、更安全的替代方案）。用户可以批准或拒绝——默认选项是拒绝，以保持无人值守场景的安全性。

### 上下文文件注入防护

上下文文件（AGENTS.md、.cursorrules、SOUL.md）在包含到系统提示中之前会进行提示注入扫描。扫描器检查：

- 指示忽略/忽视先前指令的指令
- 带有可疑关键词的隐藏 HTML 注释
- 尝试读取机密（`.env`、`credentials`、`.netrc`）
- 通过 `curl` 泄露凭据
- 不可见 Unicode 字符（零宽度空格、双向覆盖）

被阻止的文件会显示警告：

```
[BLOCKED: AGENTS.md 包含潜在的提示注入（prompt_injection）。内容未加载。]
```

## 生产部署最佳实践

### 网关部署清单

1. **设置显式允许列表**——生产环境中切勿使用 `GATEWAY_ALLOW_ALL_USERS=true`
2. **使用容器后端**——在 config.yaml 中设置 `terminal.backend: docker`
3. **限制资源上限**——设置适当的 CPU、内存和磁盘限制
4. **安全存储机密**——将 API 密钥保存在 `~/.hermes/.env` 中，并设置合适的文件权限
5. **启用私聊配对**——尽可能使用配对码而不是硬编码用户 ID
6. **审查命令允许列表**——定期审计 config.yaml 中的 `command_allowlist`
7. **设置 `terminal.cwd`**——不要让代理从敏感目录操作
8. **以非 root 用户运行**——切勿以 root 身份运行网关
9. **监控日志**——检查 `~/.hermes/logs/` 中是否有未经授权的访问尝试
10. **保持更新**——定期运行 `hermes update` 以获取安全补丁

### 保护 API 密钥

```bash
# 为 .env 文件设置适当权限
chmod 600 ~/.hermes/.env

# 为不同服务使用独立的密钥
# 切勿将 .env 文件提交到版本控制
```

### 网络隔离

为了最大安全性，请在独立的机器或虚拟机上运行网关。在 `config.yaml` 中设置 `terminal.backend: ssh`，然后通过 `~/.hermes/.env` 中的环境变量提供主机详细信息：

```yaml
# ~/.hermes/config.yaml
terminal:
  backend: ssh
```

```bash
# ~/.hermes/.env
TERMINAL_SSH_HOST=agent-worker.local
TERMINAL_SSH_USER=hermes
TERMINAL_SSH_KEY=~/.ssh/hermes_agent_key
```

SSH 连接详细信息位于 `.env`（而非 `config.yaml`），因此不会被检查到版本控制中，也不会随配置文件导出而共享。这使得网关的消息连接与代理的命令执行分离。

## 供应链建议检查

Hermes 内置了一个建议扫描器，用于标记活跃 venv 中与已知受损版本目录（如 2026 年 5 月 `mistralai 2.4.6` 投毒等供应链蠕虫）匹配的 Python 包。实现位于 `hermes_cli/security_advisories.py`。

运行方式：

- **CLI 启动横幅。** 如果存在匹配的建议，则打印一行警告，并指向 `hermes doctor` 以获取完整的修复方案。
- **`hermes doctor`。** 显示每条活跃建议的版本详情和 2-4 步修复说明。
- **网关启动。** 记录到 `gateway.log`；第一条交互消息显示一个简短的操作员横幅。

每条建议都有一个稳定的 ID。阅读并处理完后，可以永久忽略它：

```bash
hermes doctor --ack <advisory-id>
```

确认信息持久化到 `config.security.acked_advisories`，并在重启后仍然有效。旧建议有意**不**从目录中移除——保留它们可以使新安装的用户对历史上受损的版本保持警惕，这些版本可能仍缓存在私有镜像中。

该检查仅使用标准库，每条建议运行一次 `importlib.metadata.version()` 查找，因此每次启动时运行是安全的。

### 可选依赖项懒安装

许多功能（Mistral TTS、ElevenLabs、Honcho 记忆、Bedrock、Slack、Matrix……）依赖于并非每位用户都需要的 Python 包。Hermes 在首次使用时**懒加载**安装这些包，而不是在 `hermes-agent[all]` 下主动安装。实现位于 `tools/lazy_deps.py`。

此方案解决的问题：

- **脆弱性。** 当某个额外依赖项传递依赖项在 PyPI 上不可用（因恶意软件被隔离、已撤回、上传损坏）时，整个 `[all]` 解析会失败，新安装会静默回退到一个精简的层级——一次丢失 10 多个不相关的额外项。懒安装隔离每个后端，使得一个受污染的依赖项无法破坏其他功能。
- **臃肿。** 只与一个提供程序对话的用户不再需要拉取数百个永远不会导入的包。

工作原理：

1. 后端模块在其首次导入路径的顶部调用 `ensure("feature.name")`。
2. 如果缺少依赖项，`ensure` 会检查 `config.yaml` 中的 `security.allow_lazy_installs`（默认 `true`），并为允许列表中的规范运行一个 venv 作用域的 `pip install`。
3. 如果安装失败或用户已禁用懒安装，则调用抛出 `FeatureUnavailable`，包含实际的 pip 错误输出并指向 `hermes tools`。

由 `tools/lazy_deps.py` 强制执行的安全保证：

| 保证 | 含义 |
|---|---|
| 仅 venv 作用域 | 安装到活跃 venv 中的 `sys.executable`——绝不使用系统 Python |
| 仅按名称从 PyPI 安装 | 规范接受 `"package>=1.0,<2"` 语法。不支持 `--index-url`、`git+https://` 或 file: 路径——恶意的 `config.yaml` 无法重定向安装 |
| 允许列表 | 只有出现在树内 `LAZY_DEPS` 映射中的规范才能通过此路径安装。功能名称的拼写错误不会获得“安装任意内容”的语义 |
| 可选择退出 | 设置 `security.allow_lazy_installs: false` 可完全禁用运行时安装。适用于受限网络或严格安全策略 |
| 无静默重试 | 失败时显示 `FeatureUnavailable`——不缓存错误状态，不会产生重试风暴 |

禁用运行时安装：

```yaml
# ~/.hermes/config.yaml
security:
  allow_lazy_installs: false
```

禁用后，需要可选依赖项的后端会提示用户手动运行安装（`pip install …`），或通过 `hermes tools` 选择其他后端。