---
sidebar_position: 1
title: "CLI 命令参考"
description: "Hermes 终端命令及命令族的权威参考"
---

# CLI 命令参考

本页面涵盖您在终端中运行的**终端命令**。

关于聊天中的斜杠命令，请参见 [斜杠命令参考](./slash-commands.md)。

## 全局入口点

```bash
hermes [global-options] <command> [subcommand/options]
```

### 全局选项

| 选项 | 描述 |
|--------|-------------|
| `--version`, `-V` | 显示版本并退出。 |
| `--profile <name>`, `-p <name>` | 选择本次调用使用的 Hermes 配置（profile）。覆盖由 `hermes profile use` 设置的默认配置。 |
| `--resume <session>`, `-r <session>` | 按 ID 或标题恢复之前的会话。 |
| `--continue [name]`, `-c [name]` | 恢复最近的一个会话，或恢复标题匹配的最近一个会话。 |
| `--worktree`, `-w` | 在隔离的 git worktree 中启动，用于并行代理工作流。 |
| `--yolo` | 绕过危险命令的批准提示。 |
| `--pass-session-id` | 将会话 ID 包含在代理的系统提示中。 |
| `--ignore-user-config` | 忽略 `~/.hermes/config.yaml` 并回退到内置默认值。`.env` 中的凭据仍然加载。 |
| `--ignore-rules` | 跳过自动注入 `AGENTS.md`、`SOUL.md`、`.cursorrules`、记忆和预加载技能。 |
| `--tui` | 启动 [TUI](../user-guide/tui.md) 而不是经典 CLI。等同于 `HERMES_TUI=1`。始终覆盖 `display.interface`。 |
| `--cli` | 强制使用经典 prompt_toolkit REPL。用于在单次调用中覆盖 `display.interface: tui`。 |
| `--dev` | 与 `--tui` 一起使用时：通过 `tsx` 直接运行 TypeScript 源码，而不是使用预构建的 bundle（适用于 TUI 贡献者）。 |

## 顶级命令

| 命令 | 用途 |
|---------|---------|
| `hermes chat` | 与代理进行交互式或单次聊天。 |
| `hermes model` | 交互式选择默认提供商和模型。 |
| `hermes fallback` | 管理主模型出错时尝试的回退提供商。 |
| `hermes gateway` | 运行或管理消息网关服务。 |
| `hermes proxy` | 本地 OpenAI 兼容代理，附加 OAuth 提供商凭据。参见 [订阅代理](../user-guide/features/subscription-proxy.md)。 |
| `hermes lsp` | 管理语言服务器协议集成（用于 write_file/patch 的语义诊断）。 |
| `hermes setup` | 全部或部分配置的交互式设置向导。 |
| `hermes whatsapp` | 配置并配对 WhatsApp 桥接。 |
| `hermes slack` | Slack 辅助工具（目前：生成应用清单，使每个命令成为原生斜杠命令）。 |
| `hermes auth` | 管理凭据 — 添加、列出、删除、重置、状态、登出。处理 Codex/Nous/Anthropic 的 OAuth 流程。 |
| `hermes login` / `logout` | **已弃用** — 请改用 `hermes auth`。 |
| `hermes send` | 向已配置的消息平台（Telegram、Discord、Slack、Signal、SMS 等）发送一次性消息。适用于 shell 脚本、cron 任务、CI 钩子和监控守护进程 — 无需代理循环，无需 LLM。 |
| `hermes secrets` | 管理外部密钥源（当前为 Bitwarden Secrets Manager），用于在进程启动时拉取 API 密钥，而不是从 `~/.hermes/.env` 读取。 |
| `hermes migrate` | 诊断并（可选）重写 `config.yaml`，替换对已退役模型或已弃用设置的引用（例如 `migrate xai`）。 |
| `hermes status` | 显示代理、认证和平台状态。 |
| `hermes cron` | 检查并触发 cron 调度器。 |
| `hermes kanban` | 多配置协作看板（任务、链接、调度器）。 |
| `hermes webhook` | 管理动态 webhook 订阅，用于事件驱动激活。 |
| `hermes hooks` | 检查、批准或移除 `config.yaml` 中声明的 shell 脚本钩子。 |
| `hermes doctor` | 诊断配置和依赖问题。 |
| `hermes security audit` | 按需供应链审计（基于 OSV.dev），检查 venv、插件依赖和固定的 MCP 服务器。 |
| `hermes dump` | 可复制粘贴的设置摘要，用于支持/调试。 |
| `hermes prompt-size` | 显示系统提示 + 工具模式（技能索引、记忆、配置）的字节分解。离线运行。 |
| `hermes debug` | 调试工具 — 上传日志和系统信息以获取支持。 |
| `hermes backup` | 将 Hermes 主目录备份为 zip 文件。 |
| `hermes checkpoints` | 检查/清理/清空 `~/.hermes/checkpoints/`（`/rollback` 使用的影子存储）。无参数运行显示状态概览。 |
| `hermes import` | 从 zip 文件恢复 Hermes 备份。 |
| `hermes logs` | 查看、跟踪和过滤代理/网关/错误日志文件。 |
| `hermes config` | 显示、编辑、迁移和查询配置文件。 |
| `hermes pairing` | 批准或撤销消息配对码。 |
| `hermes skills` | 浏览、安装、发布、审计和配置技能。 |
| `hermes bundles` | 将多个技能分组在一个 `/<name>` 斜杠命令下。参见 [技能捆绑包](../user-guide/features/skills.md#skill-bundles)。 |
| `hermes curator` | 后台技能维护 — 状态、运行、暂停、固定。参见 [维护者](../user-guide/features/curator.md)。 |
| `hermes memory` | 配置外部记忆提供者。插件特定的子命令（例如 `hermes honcho`）在其提供者激活时自动注册。 |
| `hermes acp` | 以 ACP 服务器模式运行 Hermes，用于编辑器集成。 |
| `hermes mcp` | 管理 MCP 服务器配置，并以 MCP 服务器模式运行 Hermes。 |
| `hermes plugins` | 管理 Hermes 代理插件（安装、启用、禁用、移除）。 |
| `hermes portal` | Nous Portal 状态、订阅链接和工具网关路由。参见 [工具网关](../user-guide/features/tool-gateway.md)。 |
| `hermes tools` | 按平台配置启用的工具。 |
| `hermes computer-use` | 安装或检查 cua-driver 后端（macOS 计算机使用）。 |
| `hermes sessions` | 浏览、导出、清理、重命名和删除会话。 |
| `hermes insights` | 显示 token/成本/活动分析。 |
| `hermes claw` | OpenClaw 迁移辅助工具。 |
| `hermes dashboard` | 启动 Web 仪表盘，用于管理配置、API 密钥和会话。 |
| `hermes profile` | 管理配置（profile）——多个隔离的 Hermes 实例。 |
| `hermes completion` | 打印 shell 补全脚本（bash/zsh/fish）。 |
| `hermes version` | 显示版本信息。 |
| `hermes update` | 拉取最新代码并重新安装依赖。`--check` 预览但不安装；`--backup` 在拉取前获取 `HERMES_HOME` 快照。 |
| `hermes uninstall` | 从系统移除 Hermes。 |

## `hermes chat`

```bash
hermes chat [options]
```

常用选项：

| 选项 | 描述 |
|--------|-------------|
| `-q`, `--query "..."` | 一次性非交互式提示。 |
| `-m`, `--model <model>` | 覆盖本次运行的模型。 |
| `-t`, `--toolsets <csv>` | 启用逗号分隔的工具集集合。 |
| `--provider <provider>` | 强制指定提供商：`auto`、`openrouter`、`nous`、`openai-codex`、`copilot-acp`、`copilot`、`anthropic`、`gemini`、`huggingface`、`novita`（别名 `novita-ai`、`novitaai`）、`openai-api`、`zai`、`kimi-coding`、`kimi-coding-cn`、`minimax`、`minimax-cn`、`minimax-oauth`、`kilocode`、`xiaomi`、`arcee`、`gmi`、`alibaba`、`alibaba-coding-plan`（别名 `alibaba_coding`）、`deepseek`、`nvidia`、`ollama-cloud`、`xai`（别名 `grok`）、`xai-oauth`（别名 `grok-oauth`）、`qwen-oauth`、`bedrock`、`opencode-zen`、`opencode-go`、`azure-foundry`、`lmstudio`、`stepfun`、`tencent-tokenhub`（别名 `tencent`、`tokenhub`）。 |
| `-s`, `--skills <name>` | 为会话预加载一个或多个技能（可重复或逗号分隔）。 |
| `-v`, `--verbose` | 详细输出。 |
| `-Q`, `--quiet` | 程序模式：隐藏标题/旋转器/工具预览。 |
| `--image <path>` | 将本地图像附加到单个查询。 |
| `--resume <session>` / `--continue [name]` | 直接从 `chat` 恢复会话。 |
| `--worktree` | 为此运行创建隔离的 git worktree。 |
| `--checkpoints` | 在破坏性文件更改前启用文件系统检查点。 |
| `--yolo` | 跳过批准提示。 |
| `--pass-session-id` | 将会话 ID 传入系统提示。 |
| `--ignore-user-config` | 忽略 `~/.hermes/config.yaml` 并使用内置默认值。`.env` 中的凭据仍然加载。适用于隔离的 CI 运行、可复现的 bug 报告和第三方集成。 |
| `--ignore-rules` | 跳过自动注入 `AGENTS.md`、`SOUL.md`、`.cursorrules`、持久记忆和预加载技能。与 `--ignore-user-config` 结合使用可实现完全隔离运行。 |
| `--safe-mode` | 故障排除模式：禁用所有自定义项 — 用户配置、规则/记忆注入、插件和 MCP 服务器（隐式包含 `--ignore-user-config` 和 `--ignore-rules`）。用于隔离问题是来自您的设置还是 Hermes 本身。 |
| `--source <tag>` | 会话源标签，用于过滤（默认：`cli`）。对于不应出现在用户会话列表中的第三方集成，使用 `tool`。 |
| `--max-turns <N>` | 每个对话轮次的最大工具调用迭代次数（默认：90，或配置中的 `agent.max_turns`）。 |

示例：

```bash
hermes
hermes chat -q "Summarize the latest PRs"
hermes chat --provider openrouter --model anthropic/claude-sonnet-4.6
hermes chat --toolsets web,terminal,skills
hermes chat --quiet -q "Return only JSON"
hermes chat --worktree -q "Review this repo and open a PR"
hermes chat --ignore-user-config --ignore-rules -q "Repro without my personal setup"
hermes chat --safe-mode -q "Is this bug mine or Hermes'?"
```

### `hermes -z <prompt>` — 脚本化一次性调用

对于程序化调用方（shell 脚本、CI、cron、通过管道传入提示的父进程），`hermes -z` 是最纯粹的一次性入口点：**单个提示输入，最终响应文本输出，stdout 或 stderr 上无其他内容。** 无标题、无旋转器、无工具预览、无 `Session:` 行 — 只有代理的最终回复作为纯文本。

```bash
hermes -z "What's the capital of France?"
# → Paris.

# 父脚本可以干净地捕获响应：
answer=$(hermes -z "summarize this" < /path/to/file.txt)
```

每次运行的覆盖项（不修改 `~/.hermes/config.yaml`）：

| 标志 | 等效环境变量 | 用途 |
|---|---|---|
| `-m` / `--model <model>` | `HERMES_INFERENCE_MODEL` | 覆盖本次运行的模型 |
| `--provider <provider>` | _(无)_ | 覆盖本次运行的提供商 |

```bash
hermes -z "…" --provider openrouter --model openai/gpt-5.5
# 或：
HERMES_INFERENCE_MODEL=anthropic/claude-sonnet-4.6 hermes -z "…"
```

相同的代理、相同的工具、相同的技能 — 只是去掉了所有交互/装饰层。如果您也需要在记录中包含工具输出，请改用 `hermes chat -q`；`-z` 明确用于“我只想要最终答案”。

## `hermes model`

交互式提供商 + 模型选择器。**这是用于添加新提供商、设置 API 密钥和运行 OAuth 流程的命令。** 请在终端中运行它 — 而不是在活动的 Hermes 聊天会话内部。

```bash
hermes model
```

在以下情况下使用此命令：
- **添加新提供商**（OpenRouter、Anthropic、Copilot、DeepSeek、自定义等）
- 登录基于 OAuth 的提供商（Anthropic、Copilot、Codex、Nous Portal）
- 输入或更新 API 密钥
- 从提供商特定的模型列表中选择
- 配置自定义/自托管端点
- 将新默认值保存到配置中

:::warning hermes model 与 /model 的区别
**`hermes model`**（在终端中运行，不在任何 Hermes 会话内部）是**完整的提供商设置向导**。它可以添加新提供商、运行 OAuth 流程、提示输入 API 密钥和配置端点。

**`/model`**（在活动的 Hermes 聊天会话内部输入）只能**在您已设置的提供商和模型之间切换**。它不能添加新提供商、运行 OAuth 或提示输入 API 密钥。

**如果您需要添加新提供商：** 首先退出您的 Hermes 会话（`Ctrl+C` 或 `/quit`），然后在终端提示符下运行 `hermes model`。
:::

### `/model` 斜杠命令（会话中）

在不离开会话的情况下在已配置的模型之间切换：

```
/model                              # 显示当前模型和可用选项
/model claude-sonnet-4              # 切换模型（自动检测提供商）
/model zai:glm-5                    # 切换提供商和模型
/model custom:qwen-2.5              # 在自定义端点上使用模型
/model custom                       # 从自定义端点自动检测模型
/model custom:local:qwen-2.5        # 使用命名的自定义提供商
/model openrouter:anthropic/claude-sonnet-4  # 切换回云提供商
```

默认情况下，`/model` 的更改**仅适用于当前会话**。添加 `--global` 可将更改持久化到 `config.yaml`：

```
/model claude-sonnet-4 --global     # 切换并保存为新默认值
```

:::info 为什么我只看到 OpenRouter 模型？
如果您只配置了 OpenRouter，`/model` 只会显示 OpenRouter 模型。要添加其他提供商（Anthropic、DeepSeek、Copilot 等），请退出会话并在终端中运行 `hermes model`。
:::

提供商和基本 URL 的更改会自动持久化到 `config.yaml`。当从自定义端点切换出来时，过时的基本 URL 会被清除，以防止泄露到其他提供商。

## `hermes gateway`

```bash
hermes gateway <subcommand>
```

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `run` | 在前台运行网关。推荐用于 WSL、Docker 和 Termux。 |
| `start` | 启动已安装的 systemd/launchd 后台服务。 |
| `stop` | 停止服务（或前台进程）。 |
| `restart` | 重启服务。 |
| `status` | 显示服务状态。 |
| `list` | 列出**所有配置**以及每个配置的网关是否正在运行（如有 PID 则显示）。当您并行运行多个配置并希望获得单一概览时非常方便。 |
| `install` | 安装为 systemd（Linux）或 launchd（macOS）后台服务。 |
| `uninstall` | 移除已安装的服务。 |
| `setup` | 交互式消息平台设置。 |
| `enroll` | 实验性：将此网关注册到中继连接器，并保存用于连接器支持平台的中继凭据。 |

选项：

| 选项 | 描述 |
|--------|-------------|
| `--all` | 对于 `start` / `restart` / `stop`：作用于**每个配置**的网关，而不仅仅是活动的 `HERMES_HOME`。如果您并行运行多个配置并希望在 `hermes update` 后全部重启，则很有用。 |
| `--no-supervise` | 对于 `run`：在 s6-overlay Docker 镜像内部，选择退出自动监管并使用前 s6 前台语义 — 网关作为容器的 main 进程运行，无自动重启。在 s6 镜像外部无效果。等同于设置 `HERMES_GATEWAY_NO_SUPERVISE=1`。 |

`hermes gateway enroll` 接受 `--token`、`--connector-url` 和 `--gateway-id`。它用连接器交换注册令牌，并将生成的 `GATEWAY_RELAY_ID`、`GATEWAY_RELAY_SECRET`、`GATEWAY_RELAY_DELIVERY_KEY` 和可选的 `GATEWAY_RELAY_URL` 值写入活动配置的 `.env`。

:::tip WSL 用户
请使用 `hermes gateway run` 而不是 `hermes gateway start` — WSL 的 systemd 支持不可靠。将其包装在 tmux 中以实现持久性：`tmux new -s hermes 'hermes gateway run'`。详见 [WSL 常见问题](/reference/faq#wsl-gateway-keeps-disconnecting-or-hermes-gateway-start-fails)。
:::

## `hermes lsp`

```bash
hermes lsp <subcommand>
```

管理语言服务器协议集成。LSP 在后台运行真实语言服务器（pyright、gopls、rust-analyzer 等），并将其诊断结果输入到 `write_file` 和 `patch` 使用的写入后检查中。基于 git 工作区检测 — LSP 仅在当前工作目录或编辑的文件位于 git worktree 内时运行。

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `status` | 显示服务状态、已配置的服务器、安装状态。 |
| `list` | 打印支持的服务器注册表。传递 `--installed-only` 以跳过缺失的服务器。 |
| `install <id>` | 主动安装一个服务器的二进制文件。 |
| `install-all` | 安装每个已知自动安装配方的服务器。 |
| `restart` | 拆除正在运行的客户端，以便下次编辑重新启动。 |
| `which <id>` | 打印一个服务器的解析二进制路径。 |

有关完整指南、支持的语言和配置选项，请参见 [LSP — 语义诊断](/user-guide/features/lsp)。

## `hermes setup`

```bash
hermes setup [model|tts|terminal|gateway|tools|agent] [--non-interactive] [--reset] [--quick] [--reconfigure] [--portal]
```

**最简单的路径：** `hermes setup --portal` — 通过 OAuth 登录 Nous Portal 并一次性选择加入 [工具网关](../user-guide/features/tool-gateway.md)。

**首次运行：** 启动首次向导。

**返回用户（已配置）：** 直接进入完整重新配置向导 — 每个提示显示当前值作为默认值，按 Enter 保留或输入新值。无菜单。

跳转到特定部分而不是完整向导：

| 部分 | 描述 |
|---------|-------------|
| `model` | 提供商和模型设置。 |
| `terminal` | 终端后端和沙箱设置。 |
| `gateway` | 消息平台设置。 |
| `tools` | 按平台启用/禁用工具。 |
| `agent` | 代理行为设置。 |

选项：

| 选项 | 描述 |
|--------|-------------|
| `--quick` | 对于返回用户运行：仅提示缺失或未设置的项目。跳过您已配置的项目。 |
| `--non-interactive` | 使用默认值/环境值，无需提示。 |
| `--reset` | 在设置前将配置重置为默认值。 |
| `--reconfigure` | 向后兼容别名 — 现有安装上的裸 `hermes setup` 现在默认执行此操作。 |
| `--portal` | 一次性 Nous Portal 设置：通过 OAuth 登录，将 Nous 设置为推理提供商，并选择加入 [工具网关](../user-guide/features/tool-gateway.md)。跳过向导的其余部分。 |

## `hermes portal`

```bash
hermes portal [status|open|tools]
```

检查 Nous Portal 认证、工具网关路由和访问订阅页面。无子命令调用运行 `status`。

| 子命令 | 描述 |
|------------|-------------|
| `status`（默认） | Portal 认证状态 + 每个工具的工具网关路由摘要。未提供子命令时也显示。 |
| `open` | 在默认浏览器中打开 `portal.nousresearch.com/manage-subscription`。 |
| `tools` | 列出每个工具网关合作伙伴（Firecrawl、FAL、OpenAI TTS、Browser Use、Modal）以及哪些通过 Nous 路由。 |

有关网关本身的配置，请参见 [工具网关](../user-guide/features/tool-gateway.md)。有关一次性设置路径，请参见上面的 `hermes setup --portal`。

## `hermes whatsapp`

```bash
hermes whatsapp
```

运行 WhatsApp 配对/设置流程，包括模式选择和二维码配对。

## `hermes slack`

```bash
hermes slack manifest              # 将清单打印到 stdout
hermes slack manifest --write      # 写入 ~/.hermes/slack-manifest.json
hermes slack manifest --slashes-only  # 仅输出 features.slash_commands 数组
```

生成一个 Slack 应用清单，将 `COMMAND_REGISTRY` 中的每个网关命令（`/btw`、`/stop`、`/model` 等）注册为一级 Slack 斜杠命令 — 实现与 Discord 和 Telegram 的同等功能。将输出粘贴到您的 Slack 应用配置中，位于 [https://api.slack.com/apps](https://api.slack.com/apps) → 您的应用 → **Features → App Manifest → Edit**，然后 **Save**。如果作用域或斜杠命令发生更改，Slack 会提示重新安装。

| 标志 | 默认值 | 用途 |
|------|---------|---------|
| `--write [PATH]` | stdout | 写入文件而不是 stdout。裸 `--write` 写入 `$HERMES_HOME/slack-manifest.json`。 |
| `--name NAME` | `Hermes` | Slack 中的机器人显示名称。 |
| `--description DESC` | 默认描述 | 在 Slack 应用目录中显示的机器人描述。 |
| `--slashes-only` | 关闭 | 仅输出 `features.slash_commands`，用于合并到手动维护的清单中。 |

在 `hermes update` 后再次运行 `hermes slack manifest --write` 以获取任何新命令。

## `hermes send`

```bash
hermes send --to <target> "message text"
hermes send --to <target> --file <path>
echo "message" | hermes send --to <target>
hermes send --list [platform]
```

向已配置的消息平台发送一次性消息，无需启动代理或网关循环。重用网关已配置的凭据（`~/.hermes/.env` + `~/.hermes/config.yaml`），因此运维脚本、cron 任务、CI 钩子和监控守护进程可以发布状态更新，而无需重新实现每个平台的 REST 客户端。

对于机器人令牌平台（Telegram、Discord、Slack、Signal、SMS、WhatsApp-CloudAPI），无需运行网关 — `hermes send` 直接与平台的 REST 端点通信。需要持久适配器的插件平台仍需要活动的网关。

| 选项 | 描述 |
|--------|-------------|
| `-t`, `--to <TARGET>` | 投递目标。格式：`platform`（使用主频道）、`platform:chat_id`、`platform:chat_id:thread_id` 或 `platform:#channel-name`。示例：`telegram`、`telegram:-1001234567890`、`discord:#ops`、`slack:C0123ABCD`、`signal:+15551234567`。 |
| `-f`, `--file <PATH>` | 从 `PATH` 读取消息正文（仅文本文件 — 日志、报告、Markdown）。传递 `-` 强制从 stdin 读取。要发送图像或其他二进制文件，请使用 `MEDIA:<path>`（见下文）。 |
| `-s`, `--subject <LINE>` | 在消息正文前添加主题/标题行。 |
| `-l`, `--list [platform]` | 列出所有平台（或仅指定平台）的已配置目标。 |
| `-q`, `--quiet` | 成功时抑制 stdout — 在脚本中很有用（仅依赖退出代码）。 |
| `--json` | 输出原始 JSON 结果而不是人类可读输出。 |

如果既没有提供位置参数 `message` 也没有提供 `--file`，且 stdin 不是 TTY，则 `hermes send` 从 stdin 读取。退出代码：`0` 成功，`1` 投递/后端失败，`2` 用法错误。

### 发送图像和其他媒体

`--file` 仅用于**文本**正文。要投递图像、文档、视频或音频文件作为原生平台附件，请在消息文本中使用 `MEDIA:<local_path>` 指令引用它：

```bash
hermes send --to telegram "MEDIA:/tmp/screenshot.png"
hermes send --to telegram "Build chart for today MEDIA:/tmp/chart.png"   # 带标题
hermes send --to discord:#ops "MEDIA:/tmp/report.pdf"
```

默认情况下，图像文件作为照片发送（像 Telegram 这样的平台会重新压缩这些照片）。在消息中添加 `[[as_document]]` 以将其作为未压缩的文件附件投递：

```bash
hermes send --to telegram "[[as_document]] MEDIA:/tmp/screenshot.png"
```

示例：

```bash
hermes send --to telegram "deploy finished"
echo "RAM 92%" | hermes send --to telegram:-1001234567890
hermes send --to discord:#ops --file /tmp/report.md
hermes send --to slack:#eng --subject "[CI]" --file build.log
hermes send --list                  # 所有平台
hermes send --list telegram         # 按平台过滤
```

## `hermes secrets`

```bash
hermes secrets bitwarden <subcommand>
hermes secrets bw <subcommand>          # 短别名
```

在进程启动时从外部密钥管理器拉取 API 密钥，而不是将它们存储在 `~/.hermes/.env` 中。当前支持 **Bitwarden Secrets Manager**。请参见完整指南：[Bitwarden 集成](../user-guide/secrets/bitwarden.md)。

`bitwarden`（别名 `bw`）子命令：

| 子命令 | 描述 |
|------------|-------------|
| `setup` | 交互式向导：安装固定的 `bws` 二进制文件，存储访问令牌，并选择一个项目。接受 `--project-id`、`--access-token` 和 `--server-url` 用于非交互使用。 |
| `status` | 显示当前配置、二进制路径/版本和上次获取信息。 |
| `sync` | 立即获取密钥并报告更改的内容。添加 `--apply` 以实际将密钥导出到当前 shell 环境（默认为试运行）。 |
| `install` | 下载并验证固定的 `bws` 二进制文件。`--force` 即使已存在托管副本也重新下载。 |
| `disable` | 关闭 Bitwarden 集成。 |

## `hermes migrate`

```bash
hermes migrate <type>
```

诊断并（可选）重写活动的 `config.yaml`，替换对已退役模型或已弃用设置的引用。在重写之前会创建原始 `config.yaml` 的时间戳备份（使用 `--no-backup` 跳过）。

| 子命令 | 描述 |
|------------|-------------|
| `xai` | 扫描 `config.yaml` 中计划于 2026 年 5 月 15 日退役的 xAI 模型引用，并使用（带 `--apply`）根据 xAI 迁移指南就地将其重写为官方替代品。默认为试运行。 |

迁移子命令的常用标志：

| 标志 | 描述 |
|------|-------------|
| `--apply` | 就地重写 `config.yaml`（默认：试运行，不写入）。 |
| `--no-backup` | 应用时跳过创建 `config.yaml` 的时间戳备份。 |

> 不要与 `hermes claw migrate`（将 OpenClaw 配置一次性导入 Hermes）混淆 — `hermes migrate` 是顶级的配置重写命令。

## `hermes proxy`

```bash
hermes proxy <subcommand>
```

运行一个本地 OpenAI 兼容的 HTTP 服务器，将请求转发到 OAuth 认证的上游提供商（例如 Nous Portal、xAI）。外部应用可以使用任意 bearer token 指向代理；代理会在出口时附加您的真实 OAuth 凭据。请参见 [订阅代理](../user-guide/features/subscription-proxy.md) 获取完整指南。

| 子命令 | 描述 |
|------------|-------------|
| `start` | 在前台运行代理。标志：`--provider <nous\|xai>`（默认 `nous`）、`--host <addr>`（默认 `127.0.0.1`；使用 `0.0.0.0` 暴露于局域网）、`--port <int>`（默认 `8645`）。 |
| `status` | 显示哪些代理上游已就绪（凭据存在、OAuth 有效）。 |
| `providers` | 列出可用的代理上游提供商。 |

## `hermes security`

```bash
hermes security <subcommand>
```

按需针对 [OSV.dev](https://osv.dev) 进行漏洞扫描。覆盖 Hermes venv（已安装的 PyPI 发行版）、`~/.hermes/plugins/` 下插件声明的 Python 依赖以及 `config.yaml` 中固定的 `npx`/`uvx` MCP 服务器。不扫描全局安装的包或编辑器/浏览器扩展。

| 子命令 | 描述 |
|------------|-------------|
| `audit` | 运行一次性供应链审计。 |

`audit` 标志：

| 标志 | 默认值 | 描述 |
|------|---------|-------------|
| `--json` | 关闭 | 输出机器可读的 JSON 而不是人类可读文本。 |
| `--fail-on <level>` | `critical` | 当任何发现达到此严重级别（`low`、`moderate`、`high`、`critical`）时以非零退出。 |
| `--skip-venv` | 关闭 | 跳过扫描 Hermes Python venv。 |
| `--skip-plugins` | 关闭 | 跳过扫描插件依赖文件。 |
| `--skip-mcp` | 关闭 | 跳过扫描 `config.yaml` 中固定的 MCP 服务器。 |

## `hermes login` / `hermes logout` *(已弃用)*

:::caution
`hermes login` 已被移除。请使用 `hermes auth` 管理 OAuth 凭据，使用 `hermes model` 选择提供商，或使用 `hermes setup` 进行完整交互式设置。
:::

## `hermes auth`

管理同提供商密钥轮换的凭据池。请参见 [凭据池](/user-guide/features/credential-pools) 获取完整文档。

```bash
hermes auth                                              # 交互式向导
hermes auth list                                         # 显示所有池
hermes auth list openrouter                              # 显示特定提供商
hermes auth add openrouter --api-key sk-or-v1-xxx        # 添加 API 密钥
hermes auth add anthropic --type oauth                   # 添加 OAuth 凭据
hermes auth remove openrouter 2                          # 按索引移除
hermes auth reset openrouter                             # 清除冷却
hermes auth status anthropic                             # 显示提供商的认证状态
hermes auth logout anthropic                             # 登出并清除存储的认证状态
hermes auth spotify                                      # 通过 PKCE 使用 Spotify 认证 Hermes
```

子命令：`add`、`list`、`remove`、`reset`、`status`、`logout`、`spotify`。无子命令调用时启动交互式管理向导。

## `hermes status`

```bash
hermes status [--all] [--deep]
```

| 选项 | 描述 |
|--------|-------------|
| `--all` | 以可共享的编辑格式显示所有详细信息。 |
| `--deep` | 运行可能需要更长时间的更深入检查。 |

## `hermes cron`

```bash
hermes cron <list|create|edit|pause|resume|run|remove|status|tick>
```

| 子命令 | 描述 |
|------------|-------------|
| `list` | 显示计划任务。 |
| `create` / `add` | 从提示创建计划任务，可选地通过重复 `--skill` 附加一个或多个技能。 |
| `edit` | 更新任务的计划、提示、名称、投递、重复次数或附加的技能。支持 `--clear-skills`、`--add-skill` 和 `--remove-skill`。 |
| `pause` | 暂停任务而不删除它。 |
| `resume` | 恢复暂停的任务并计算其下一次运行时间。 |
| `run` | 在下一个调度器滴答时触发任务。 |
| `remove` | 删除计划任务。 |
| `status` | 检查 cron 调度器是否正在运行。 |
| `tick` | 运行到期的任务并退出。 |

cron **触发器**可通过 `cron.provider` 配置键插拔。空（默认）使用内置进程内计时器。设置为 `chronos`（由 NAS 管理的提供商，用于零缩放托管网关）— 通过 `cron.chronos.*` 键（`portal_url`、`callback_url`、`expected_audience`、`nas_jwks_url`）配置 — 或命名一个自定义提供商，位于 `plugins/cron/<name>/` 或 `$HERMES_HOME/plugins/<name>/`。未知或不可用的提供商回退到内置提供者，因此 cron 永远不会缺少触发器。请参见 [cron 内部](../developer-guide/cron-internals.md#gateway-integration) 文档。

## `hermes kanban`

```bash
hermes kanban [--board <slug>] <action> [options]
```

多配置、多项目协作看板。每个安装可以托管多个看板（每个项目、仓库或域一个）；每个看板是一个独立的队列，拥有自己的 SQLite 数据库和调度器范围。新安装以一个名为 `default` 的看板开始，其数据库为 `~/.hermes/kanban.db`（用于向后兼容）；其他看板存放在 `~/.hermes/kanban/boards/<slug>/kanban.db`。网关嵌入的调度器每个滴答扫描每个看板。

**全局标志（应用于下面的每个操作）：**

| 标志 | 用途 |
|------|---------|
| `--board <slug>` | 操作特定看板。默认为当前看板（通过 `hermes kanban boards switch`、`HERMES_KANBAN_BOARD` 环境变量或 `default` 设置）。 |

**这是人类/脚本界面。** 调度器派生的 agent 工作进程通过专用的 `kanban_*` [工具集](/user-guide/features/kanban#how-workers-interact-with-the-board)（`kanban_show`、`kanban_complete`、`kanban_block`、`kanban_create`、`kanban_link`、`kanban_comment`、`kanban_heartbeat`；编排器配置还可获得 `kanban_list` 和 `kanban_unblock`）驱动看板，而不是 shell 调用 `hermes kanban`。工作进程的 env 中固定了 `HERMES_KANBAN_BOARD`，因此它们物理上无法看到其他看板。

| 操作 | 用途 |
|--------|---------|
| `init` | 如果 `kanban.db` 丢失则创建。幂等。 |
| `boards list` / `boards ls` | 列出所有看板以及任务计数。`--json`、`--all`（包括已归档的）。 |
| `boards create <slug>` | 创建新看板。标志：`--name`、`--description`、`--icon`、`--color`、`--switch`（设为活动）。Slug 为短横线命名法，自动小写。 |
| `boards switch <slug>` / `boards use` | 将 `<slug>` 持久化为活动看板（写入 `~/.hermes/kanban/current`）。 |
| `boards show` / `boards current` | 打印当前活动看板的名称、数据库路径和任务计数。 |
| `boards rename <slug> "<name>"` | 更改看板的显示名称。Slug 不可变。 |
| `boards rm <slug>` | 归档（默认）或硬删除看板。`--delete` 跳过归档步骤。归档的看板移动到 `boards/_archived/<slug>-<ts>/`。对 `default` 拒绝。 |
| `create "<title>"` | 在活动看板上创建新任务。标志：`--body`、`--assignee`、`--parent`（可重复）、`--workspace scratch\|worktree\|dir:<path>`、`--tenant`、`--priority`、`--triage`、`--idempotency-key`、`--max-runtime`、`--max-retries`、`--skill`（可重复）。 |
| `list` / `ls` | 列出活动看板上的任务。使用 `--mine`、`--assignee`、`--status`、`--tenant`、`--archived`、`--json` 过滤。 |
| `show <id>` | 显示任务及其评论和事件。`--json` 用于机器输出。 |
| `assign <id> <profile>` | 分配或重新分配。使用 `none` 取消分配。任务运行时拒绝。 |
| `link <parent> <child>` | 添加依赖。循环检测。两个任务必须在同一看板上。 |
| `unlink <parent> <child>` | 移除依赖。 |
| `claim <id>` | 原子性地声明一个就绪任务。打印解析的工作区路径。 |
| `comment <id> "<text>"` | 添加评论。下一个声明该任务的工作进程在 `kanban_show()` 响应中读取它。 |
| `complete <id>` | 标记任务完成。标志：`--result`、`--summary`、`--metadata`。 |
| `block <id> "<reason>"` | 标记任务因人类输入而阻塞。同时将原因附加为评论。 |
| `schedule <id> "<reason>"` | 将时间延迟/后续工作停放在 `scheduled` 状态，因此不会显示为人类阻塞。 |
| `unblock <id>` | 将阻塞或计划任务返回到就绪状态（如果依赖仍然打开则返回 `todo`）。 |
| `archive <id>` | 从默认列表中隐藏。`gc` 将移除 scratch 工作区。 |
| `tail <id>` | 跟踪任务的事件流。 |
| `dispatch` | 在活动看板上执行一次调度器传递。标志：`--dry-run`、`--max N`、`--failure-limit N`、`--json`。 |
| `context <id>` | 打印工作进程会看到的完整上下文（标题 + 正文 + 父任务结果 + 评论）。 |
| `specify <id>` / `specify --all` | 通过辅助 LLM 将分诊列任务充实为具体规范（标题 + 正文，包含目标、方法和验收标准），然后将其提升为 `todo`。标志：`--tenant`（将 `--all` 限定到一个租户）、`--author`、`--json`。在 `config.yaml` 的 `auxiliary.triage_specifier` 下配置模型。 |
| `decompose <id>` / `decompose --all` | 将分诊列任务分叉成一个子任务图，根据描述路由到专业配置。当 LLM 决定任务不适合分叉时，回退到指定风格的单任务提升。与 `specify` 相同的标志。在 `config.yaml` 的 `auxiliary.kanban_decomposer` 下配置分解器模型；`kanban.orchestrator_profile` 仅控制分叉后谁拥有根/编排任务。当 `kanban.auto_decompose: true`（默认）时，也会在每个调度器滴答时自动运行。请参见 [自动与手动编排](/user-guide/features/kanban#auto-vs-manual-orchestration)。 |
| `gc` | 移除归档任务的 scratch 工作区。 |

示例：

```bash
# 创建第二个看板并在其上放置一个任务，无需切换当前看板。
hermes kanban boards create atm10-server --name "ATM10 Server" --icon 🎮
hermes kanban --board atm10-server create "Restart server" --assignee ops

# 为后续调用切换活动看板。
hermes kanban boards switch atm10-server
hermes kanban list                  # 显示 atm10-server 任务

# 归档看板（可恢复）或硬删除。
hermes kanban boards rm atm10-server
hermes kanban boards rm atm10-server --delete
```

看板解析顺序（最高优先级优先）：`--board <slug>` 标志 → `HERMES_KANBAN_BOARD` 环境变量 → `~/.hermes/kanban/current` 文件 → `default`。

所有操作也可作为网关中的斜杠命令使用（`/kanban …`），具有相同的参数界面 — 包括 `boards` 子命令和 `--board` 标志。

有关完整设计 — 与 Cline Kanban / Paperclip / NanoClaw / Gemini Enterprise 的比较、八种协作模式、四个用户故事、并发正确性证明 — 请参见仓库中的 `docs/hermes-kanban-v1-spec.pdf` 或 [Kanban 用户指南](/user-guide/features/kanban)。

## `hermes webhook`

```bash
hermes webhook <subscribe|list|remove|test>
```

管理用于事件驱动代理激活的动态 webhook 订阅。需要在 config 中启用 webhook 平台 — 如果未配置，则打印设置说明。

| 子命令 | 描述 |
|------------|-------------|
| `subscribe` / `add` | 创建 webhook 路由。返回在您的服务上配置的 URL 和 HMAC 密钥。 |
| `list` / `ls` | 显示所有代理创建的订阅。 |
| `remove` / `rm` | 删除动态订阅。config.yaml 中的静态路由不受影响。 |
| `test` | 发送测试 POST 以验证订阅是否正常工作。 |

### `hermes webhook subscribe`

```bash
hermes webhook subscribe <name> [options]
```

| 选项 | 描述 |
|--------|-------------|
| `--prompt` | 包含 `{dot.notation}` 有效负载引用的提示模板。 |
| `--events` | 逗号分隔的要接受的事件类型（例如 `issues,pull_request`）。空 = 所有。 |
| `--description` | 人类可读的描述。 |
| `--skills` | 逗号分隔的要为代理运行加载的技能名称。 |
| `--deliver` | 投递目标：`log`（默认）、`telegram`、`discord`、`slack`、`github_comment`。 |
| `--deliver-chat-id` | 跨平台投递的目标聊天/频道 ID。 |
| `--secret` | 自定义 HMAC 密钥。如果省略则自动生成。 |
| `--deliver-only` | 跳过代理 — 将渲染后的 `--prompt` 作为文字消息投递。零 LLM 成本，亚秒级投递。要求 `--deliver` 是真实目标（非 `log`）。 |

订阅持久化到 `~/.hermes/webhook_subscriptions.json`，并由 webhook 适配器热加载，无需重启网关。

## `hermes doctor`

```bash
hermes doctor [--fix]
```

| 选项 | 描述 |
|--------|-------------|
| `--fix` | 尽可能尝试自动修复。 |

## `hermes dump`

```bash
hermes dump [--show-keys]
```

输出整个 Hermes 设置的紧凑纯文本摘要。设计用于在寻求支持时复制粘贴到 Discord、GitHub Issues 或 Telegram — 无 ANSI 颜色，无特殊格式，只有数据。

| 选项 | 描述 |
|--------|-------------|
| `--show-keys` | 显示编辑后的 API 密钥前缀（前 4 个和后 4 个字符），而不是仅显示 `set`/`not set`。 |

### 包含内容

| 部分 | 详细信息 |
|---------|---------|
| **头部** | Hermes 版本、发布日期、git 提交哈希 |
| **环境** | 操作系统、Python 版本、OpenAI SDK 版本 |
| **身份** | 活动配置名称、HERMES_HOME 路径 |
| **模型** | 已配置的默认模型和提供商 |
| **终端** | 后端类型（local、docker、ssh 等） |
| **API 密钥** | 所有 22 个提供商/工具 API 密钥的存在检查 |
| **功能** | 启用的工具集、MCP 服务器数量、记忆提供者 |
| **服务** | 网关状态、已配置的消息平台 |
| **工作负载** | Cron 任务计数、已安装技能计数 |
| **配置覆盖** | 与默认值不同的任何配置值 |

### 示例输出

```
--- hermes dump ---
version:          0.8.0 (2026.4.8) [af4abd2f]
os:               Linux 6.14.0-37-generic x86_64
python:           3.11.14
openai_sdk:       2.24.0
profile:          default
hermes_home:      ~/.hermes
model:            anthropic/claude-opus-4.6
provider:         openrouter
terminal:         local

api_keys:
  openrouter           set
  openai               not set
  anthropic            set
  nous                 not set
  firecrawl            set
  ...

features:
  toolsets:           all
  mcp_servers:        0
  memory_provider:    built-in
  gateway:            running (systemd)
  platforms:          telegram, discord
  cron_jobs:          3 active / 5 total
  skills:             42

config_overrides:
  agent.max_turns: 250
  compression.threshold: 0.85
  display.streaming: True
--- end dump ---
```

### 何时使用

- 在 GitHub 上报告 bug — 将 dump 粘贴到您的 issue 中
- 在 Discord 中寻求帮助 — 在代码块中分享
- 将您的设置与其他人比较
- 当某些东西不工作时快速进行健全性检查

:::tip
`hermes dump` 专门设计用于分享。对于交互式诊断，请使用 `hermes doctor`。对于可视化概览，请使用 `hermes status`。
:::

## `hermes debug`

```bash
hermes debug share [options]
```

将调试报告（系统信息 + 最近日志）上传到粘贴服务并获取可分享的 URL。对于快速支持请求很有用 — 包含帮助者诊断问题所需的所有信息。

| 选项 | 描述 |
|--------|-------------|
| `--lines <N>` | 每个日志文件包含的日志行数（默认：200）。 |
| `--expire <days>` | 粘贴过期天数（默认：7）。 |
| `--local` | 在本地打印报告而不是上传。 |

报告包括系统信息（操作系统、Python 版本、Hermes 版本）、最近的代理、网关、GUI/仪表盘和桌面日志（每个文件 512 KB 限制）以及编辑后的 API 密钥状态。密钥始终被编辑 — 不上传任何密钥。

尝试的粘贴服务按顺序：paste.rs、dpaste.com。

### 示例

```bash
hermes debug share              # 上传调试报告，打印 URL
hermes debug share --lines 500  # 包含更多日志行
hermes debug share --expire 30  # 将粘贴保留 30 天
hermes debug share --local      # 打印报告到终端（不上传）
```

## `hermes backup`

```bash
hermes backup [options]
```

创建 Hermes 配置、技能、会话和数据的 zip 归档。备份不包括 hermes-agent 代码本身。

| 选项 | 描述 |
|--------|-------------|
| `-o`, `--output <path>` | zip 文件的输出路径（默认：`~/hermes-backup-<timestamp>.zip`）。 |
| `-q`, `--quick` | 快速快照：仅关键状态文件（config.yaml、state.db、.env、auth、cron 任务）。比完整备份快得多。 |
| `-l`, `--label <name>` | 快照的标签（仅与 `--quick` 一起使用）。 |

备份使用 SQLite 的 `backup()` API 进行安全复制，因此即使 Hermes 正在运行也能正常工作（WAL 模式安全）。

**从 zip 中排除的内容：**

- `*.db-wal`、`*.db-shm`、`*.db-journal` — SQLite 的 WAL/共享内存/日记侧车文件。`*.db` 文件已通过 `sqlite3.backup()` 获取一致快照；同时附带活的侧车文件会导致恢复看到半提交状态。
- `checkpoints/` — 每个会话的轨迹缓存。哈希键控并为每个会话重新生成；无论如何都无法干净地移植到另一个安装。
- `hermes-agent` 代码本身（这是用户数据备份，不是仓库快照）。

### 示例

```bash
hermes backup                           # 完整备份到 ~/hermes-backup-*.zip
hermes backup -o /tmp/hermes.zip        # 完整备份到特定路径
hermes backup --quick                   # 快速仅状态快照
hermes backup --quick --label "pre-upgrade"  # 带标签的快速快照
```

## `hermes checkpoints`

```bash
hermes checkpoints [COMMAND]
```

检查和管理位于 `~/.hermes/checkpoints/` 的影子 git 存储 — 会话内 `/rollback` 命令的后端存储层。可随时安全运行；不需要代理在运行。

| 子命令 | 描述 |
|------------|-------------|
| `status`（默认） | 显示总大小、项目计数和每个项目的分解。裸 `hermes checkpoints` 等效。 |
| `list` | `status` 的别名。 |
| `prune` | 强制清理 — 删除孤立和过时的项目，GC 存储，强制执行大小上限。忽略 24 小时幂等标记。 |
| `clear` | 删除整个检查点基础。不可逆；除非有 `-f`，否则要求确认。 |
| `clear-legacy` | 仅删除由 v1→v2 迁移产生的 `legacy-<timestamp>/` 归档。 |

### 选项

| 选项 | 子命令 | 描述 |
|--------|------------|-------------|
| `--limit N` | `status`、`list` | 要列出的最大项目数（默认 20）。 |
| `--retention-days N` | `prune` | 删除 `last_touch` 超过 N 天的项目（默认 7）。 |
| `--max-size-mb N` | `prune` | 在孤立/过时传递之后，删除每个项目最旧的提交，直到总存储大小 ≤ N MB（默认 500）。 |
| `--keep-orphans` | `prune` | 跳过删除工作目录不再存在的项目。 |
| `-f`, `--force` | `clear`、`clear-legacy` | 跳过确认提示。 |

### 示例

```bash
hermes checkpoints                                  # 状态概览
hermes checkpoints prune --retention-days 3         # 激进清理
hermes checkpoints prune --max-size-mb 200          # 收紧一次大小上限
hermes checkpoints clear-legacy -f                  # 删除 v1 归档目录
hermes checkpoints clear -f                         # 清除所有
```

请参见 [检查点和 `/rollback`](../user-guide/checkpoints-and-rollback.md) 获取完整架构和会话内命令。

## `hermes import`

```bash
hermes import <zipfile> [options]
```

将先前创建的 Hermes 备份恢复到 Hermes 主目录。归档中的所有文件覆盖 Hermes 主目录中的现有文件；`--force` 仅跳过当目标已有 Hermes 安装时触发的确认提示。

| 选项 | 描述 |
|--------|-------------|
| `-f`, `--force` | 跳过已安装的确认提示。 |

:::warning
在导入前停止网关，以避免与正在运行的进程冲突。
:::

### 示例
```bash
hermes import ~/hermes-backup-20260423.zip           # 覆盖前提示
hermes import ~/hermes-backup-20260423.zip --force   # 不提示覆盖
```

## `hermes logs`

```bash
hermes logs [log_name] [options]
```

查看、跟踪和过滤 Hermes 日志文件。所有日志存储在 `~/.hermes/logs/`（或非默认配置的 `<profile>/logs/`）。

### 日志文件

| 名称 | 文件 | 捕获内容 |
|------|------|-----------------|
| `agent`（默认） | `agent.log` | 所有代理活动 — API 调用、工具调度、会话生命周期（INFO 及以上） |
| `errors` | `errors.log` | 仅警告和错误 — agent.log 的过滤子集 |
| `gateway` | `gateway.log` | 消息网关活动 — 平台连接、消息调度、webhook 事件 |
| `gui` | `gui.log` | 仪表盘 / TUI-网关 / PTY-桥接 / websocket 事件 |
| `desktop` | `desktop.log` | Electron 桌面应用 — 启动、后端生成输出和最近的 Python 回溯 |

### 选项

| 选项 | 描述 |
|--------|-------------|
| `log_name` | 要查看的日志：`agent`（默认）、`errors`、`gateway` 或 `list` 显示可用文件及其大小。 |
| `-n`, `--lines <N>` | 显示的行数（默认：50）。 |
| `-f`, `--follow` | 实时跟踪日志，类似于 `tail -f`。按 Ctrl+C 停止。 |
| `--level <LEVEL>` | 显示的最低日志级别：`DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL`。 |
| `--session <ID>` | 过滤包含会话 ID 子字符串的行。 |
| `--since <TIME>` | 显示从相对时间前开始的行：`30m`、`1h`、`2d` 等。支持 `s`（秒）、`m`（分钟）、`h`（小时）、`d`（天）。 |
| `--component <NAME>` | 按组件过滤：`gateway`、`agent`、`tools`、`cli`、`cron`。 |

### 示例

```bash
# 查看 agent.log 的最后 50 行（默认）
hermes logs

# 实时跟踪 agent.log
hermes logs -f

# 查看 gateway.log 的最后 100 行
hermes logs gateway -n 100

# 仅显示过去 1 小时的警告和错误
hermes logs --level WARNING --since 1h

# 根据特定会话过滤
hermes logs --session abc123

# 跟踪 errors.log，从 30 分钟前开始
hermes logs errors --since 30m -f

# 列出所有日志文件及其大小
hermes logs list
```

### 过滤

过滤器可以组合。当多个过滤器激活时，日志行必须通过**所有**过滤器才会显示：

```bash
# 过去 2 小时内包含会话 "tg-12345" 的 WARNING+ 行
hermes logs --level WARNING --since 2h --session tg-12345
```

当 `--since` 激活时，没有可解析时间戳的行包括在内（它们可能是多行日志条目的延续行）。当 `--level` 激活时，没有可检测级别的行包括在内。

### 日志轮转

Hermes 使用 Python 的 `RotatingFileHandler`。旧日志会自动轮转 — 查找 `agent.log.1`、`agent.log.2` 等。`hermes logs list` 子命令显示所有日志文件，包括轮转的日志文件。

## `hermes prompt-size`

```bash
hermes prompt-size [--platform <name>] [--json]
```

报告新会话的固定提示预算 — 在*任何对话内容*之前每次 API 调用发送的内容。当下游适配器或代理的提示预算比模型的上下文窗口更紧时，或者当您想查看哪个块（技能索引、记忆、配置）占主导时很有用。

它构建与代理将使用的相同的系统提示，然后分解：

- **系统提示总计** — 完整组装的提示（身份、指导、技能索引、上下文文件、记忆、配置、时间戳）。
- **技能索引** — `<available_skills>` 块。当安装了许多技能时，这通常是最大的单个块。
- **记忆**和**用户配置** — 您的 `MEMORY.md` / `USER.md` 快照。
- **提示层级** — 稳定 / 上下文 / 易失，与 Hermes 为缓存友好性分层的提示方式匹配。
- **工具模式** — 所有启用工具的 JSON（固定每次调用有效负载的另一半）。

完全离线运行 — 无需 API 调用，无需配置凭据即可工作。

```bash
# CLI 平台的人类可读分解（默认）
hermes prompt-size

# 模拟消息平台的提示（不同平台提示）
hermes prompt-size --platform telegram

# 脚本的机器可读输出
hermes prompt-size --json
```

:::tip
技能索引和工具模式随启用技能和工具的数量而缩放。要缩小提示，禁用未使用的工具集（`hermes tools`）或卸载不需要的技能（`hermes skills`）。当前目录中的上下文文件（AGENTS.md、.cursorrules）也计入总计。
:::

## `hermes config`

```bash
hermes config <subcommand>
```

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `show` | 显示当前配置值。 |
| `edit` | 在您的编辑器中打开 `config.yaml`。 |
| `set <key> <value>` | 设置配置值。 |
| `path` | 打印配置文件路径。 |
| `env-path` | 打印 `.env` 文件路径。 |
| `check` | 检查缺失或过时的配置。 |
| `migrate` | 交互式添加新引入的选项。 |

## `hermes pairing`

```bash
hermes pairing <list|approve|revoke|clear-pending>
```

| 子命令 | 描述 |
|------------|-------------|
| `list` | 显示待处理和已批准的用户。 |
| `approve <platform> <code>` | 批准配对码。 |
| `revoke <platform> <user-id>` | 撤销用户的访问权限。 |
| `clear-pending` | 清除待处理的配对码。 |

## `hermes skills`

```bash
hermes skills <subcommand>
```

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `browse` | 技能注册表的分页浏览器。 |
| `search` | 搜索技能注册表。 |
| `install` | 安装技能。 |
| `inspect` | 预览技能但不安装。 |
| `list` | 列出已安装的技能。 |
| `check` | 检查已安装的 hub 技能是否有上游更新。 |
| `update` | 有上游更改时重新安装 hub 技能。 |
| `audit` | 重新扫描已安装的 hub 技能。 |
| `uninstall` | 移除 hub 安装的技能。 |
| `reset` | 通过清除其清单条目，取消标记为 `user_modified` 的捆绑技能的卡住状态。使用 `--restore` 还会将用户副本替换为捆绑版本。 |
| `opt-out` | 阻止捆绑技能被植入活动配置。写入一个 `.no-bundled-skills` 标记，以便安装程序、`hermes update` 和任何同步跳过捆绑技能植入。默认安全 — 不会接触磁盘上的任何内容。使用 `--remove` 还会删除已存在的**未修改**的捆绑技能（用户编辑的、hub 安装的和手写的技能永远不会被删除；会先预览并确认，`--yes` 跳过）。 |
| `opt-in` | 通过移除 `.no-bundled-skills` 标记撤销 `opt-out`，以便下次 `hermes update` 时再次植入捆绑技能。使用 `--sync` 立即重新植入。 |
| `publish` | 将技能发布到注册表。 |
| `snapshot` | 导出/导入技能配置。 |
| `tap` | 管理自定义技能源。 |
| `config` | 按平台交互式启用/禁用技能配置。 |

常见示例：

```bash
hermes skills browse
hermes skills browse --source official
hermes skills search react --source skills-sh
hermes skills search https://mintlify.com/docs --source well-known
hermes skills inspect official/security/1password
hermes skills inspect skills-sh/vercel-labs/json-render/json-render-react
hermes skills install official/migration/openclaw-migration
hermes skills install skills-sh/anthropics/skills/pdf --force
hermes skills install https://sharethis.chat/SKILL.md                     # 直接 URL（单文件 SKILL.md）
hermes skills install https://example.com/SKILL.md --name my-skill        # 当前言部没有名称时覆盖名称
hermes skills check
hermes skills update
hermes skills config
hermes skills reset google-workspace
hermes skills reset google-workspace --restore --yes
hermes skills opt-out                  # 停止未来的捆绑技能植入（不删除任何内容）
hermes skills opt-out --remove --yes   # 同时删除 UNMODIFIED 的捆绑技能
hermes skills opt-in --sync            # 撤销：移除标记并立即重新植入
```

注意：
- `--force` 可以覆盖第三方/社区技能的非危险策略块。
- `--force` 不能覆盖 `dangerous` 扫描判定。
- `--source skills-sh` 搜索公共 `skills.sh` 目录。
- `--source well-known` 允许您将 Hermes 指向公开 `/.well-known/skills/index.json` 的站点。
- `--source browse-sh` 搜索 [browse.sh](https://browse.sh) 的 200+ 站点特定浏览器自动化技能目录。标识符看起来像 `browse-sh/airbnb.com/search-listings-ddgioa`。
- 传递 `http(s)://…/*.md` URL 可直接安装单文件 SKILL.md。当前言部没有 `name:` 且 URL slug 不是有效标识符时，交互式终端会提示输入名称；非交互式界面（TUI 内的 `/skills install`、网关平台）需要 `--name <x>`。

## `hermes bundles`

```bash
hermes bundles <subcommand>
```

技能捆绑包将多个技能组合在一个 `/<bundle-name>` 斜杠命令下。调用捆绑包会将每个引用的技能加载到单个组合用户消息中。存储：`~/.hermes/skill-bundles/<slug>.yaml`。参见 [技能捆绑包](../user-guide/features/skills.md#skill-bundles) 了解 YAML 模式和行为。

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `list` | 列出已安装的捆绑包（未提供子命令时的默认行为） |
| `show <name>` | 显示一个捆绑包的名称、描述、技能和文件路径 |
| `create <name>` | 创建新捆绑包。传递 `--skill <id>`（可重复）或省略以交互式输入。提供 `--description`、`--instruction`、`--force`。 |
| `delete <name>` | 删除捆绑包文件 |
| `reload` | 重新扫描 `~/.hermes/skill-bundles/` 并报告添加/删除的捆绑包 |

示例：

```bash
hermes bundles create backend-dev \
  --skill github-code-review \
  --skill test-driven-development \
  --skill github-pr-workflow \
  -d "Backend feature work"

hermes bundles list
hermes bundles show backend-dev
hermes bundles delete backend-dev
```

在聊天会话中，`/bundles` 列出已安装的捆绑包，`/<bundle-name>` 加载一个。

## `hermes curator`

```bash
hermes curator <subcommand>
```

维护者是一个辅助模型后台任务，定期审查代理创建的技能，修剪过时的技能，合并重叠的技能，并归档过时的技能。捆绑的和 hub 安装的技能永远不会被触及。归档可恢复；自动删除永远不会发生。

| 子命令 | 描述 |
|------------|-------------|
| `status` | 显示维护者状态和技能统计 |
| `run` | 立即触发维护者审查（阻塞直到 LLM 传递完成） |
| `run --background` | 在后台线程中启动 LLM 传递并立即返回 |
| `run --dry-run` | 仅预览 — 生成审查报告而不进行任何更改 |
| `backup` | 手动创建 `~/.hermes/skills/` 的 tar.gz 快照（维护者也会在每次实际运行前自动快照） |
| `rollback` | 从快照恢复 `~/.hermes/skills/`（默认为最新的） |
| `rollback --list` | 列出可用快照 |
| `rollback --id <ts>` | 按 ID 恢复特定快照 |
| `rollback -y` | 跳过确认提示 |
| `pause` | 暂停维护者直到恢复 |
| `resume` | 恢复暂停的维护者 |
| `pin <skill>` | 固定一个技能，使维护者永远不会自动转换它 |
| `unpin <skill>` | 取消固定一个技能 |
| `restore <skill>` | 恢复已归档的技能 |
| `archive <skill>` | 手动归档一个技能 |
| `prune` | 手动修剪维护者通常会清理的技能 |
| `list-archived` | 列出已归档的技能（可通过 `restore` 恢复） |

在新安装上，第一次计划的传递会延迟一个完整的 `interval_hours`（默认为 7 天）— 网关不会在 `hermes update` 后的第一个滴答上立即进行维护。使用 `hermes curator run --dry-run` 在发生之前预览。

请参见 [维护者](../user-guide/features/curator.md) 了解行为和配置。

## `hermes fallback`

```bash
hermes fallback <subcommand>
```

管理回退提供商链。当主模型因速率限制、过载或连接错误失败时，依次尝试回退提供商。

| 子命令 | 描述 |
|------------|-------------|
| `list`（别名：`ls`） | 显示当前回退链（未提供子命令时的默认行为） |
| `add` | 选择提供商 + 模型（与 `hermes model` 相同的选择器）并追加到链中 |
| `remove`（别名：`rm`） | 选择要从链中删除的条目 |
| `clear` | 移除所有回退条目 |

请参见 [回退提供商](../user-guide/features/fallback-providers.md)。

## `hermes hooks`

```bash
hermes hooks <subcommand>
```

检查在 `~/.hermes/config.yaml` 中声明的 shell 脚本钩子，对合成有效负载进行测试，并管理 `~/.hermes/shell-hooks-allowlist.json` 中的首次使用同意白名单。

| 子命令 | 描述 |
|------------|-------------|
| `list`（别名：`ls`） | 列出已配置的钩子，带有匹配器、超时和同意状态 |
| `test <event>` | 针对合成有效负载触发所有匹配 `<event>` 的钩子 |
| `revoke`（别名：`remove`、`rm`） | 移除命令的白名单条目（下次重启生效） |
| `doctor` | 检查每个已配置的钩子：可执行位、白名单、mtime 漂移、JSON 有效性和合成运行时间 |

请参见 [钩子](../user-guide/features/hooks.md) 了解事件签名和有效负载形状。

## `hermes memory`

```bash
hermes memory <subcommand>
```

设置和管理外部记忆提供者插件。可用提供商：honcho、openviking、mem0、hindsight、holographic、retaindb、byterover、supermemory。一次只能激活一个外部提供商。内置记忆（MEMORY.md/USER.md）始终激活。

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `setup` | 交互式提供商选择和配置。 |
| `status` | 显示当前记忆提供者配置。 |
| `off` | 禁用外部提供商（仅内置）。 |

:::info 提供者特定子命令
当外部记忆提供者激活时，它可能注册自己的顶级 `hermes <provider>` 命令，用于提供者特定管理（例如，当 Honcho 激活时，`hermes honcho`）。未激活的提供者不公开其子命令。运行 `hermes --help` 查看当前已连接的内容。
:::

## `hermes acp`

```bash
hermes acp
```

以 ACP（代理客户端协议）stdio 服务器模式启动 Hermes，用于编辑器集成。

相关入口点：

```bash
hermes-acp
python -m acp_adapter
```

首先安装支持：

```bash
cd ~/.hermes/hermes-agent && uv pip install -e '.[acp]'
```

请参见 [ACP 编辑器集成](../user-guide/features/acp.md)