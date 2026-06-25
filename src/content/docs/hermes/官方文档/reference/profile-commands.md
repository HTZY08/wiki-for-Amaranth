# 配置文件（Profile）命令参考

本页面涵盖与 [Hermes 配置文件](../user-guide/profiles.md) 相关的所有命令。通用 CLI 命令请参阅 [CLI 命令参考](./cli-commands.md)。

## `hermes profile`

```bash
hermes profile <subcommand>
```

管理配置文件（profile）的顶层命令。运行 `hermes profile` 而不带子命令时会显示帮助信息。

| 子命令 | 描述 |
|--------|------|
| `list` | 列出所有配置文件。 |
| `use` | 设置活动（默认）配置文件。 |
| `create` | 创建新的配置文件。 |
| `describe` | 读取或设置配置文件的描述信息（看板编排器用于路由）。 |
| `delete` | 删除配置文件。 |
| `show` | 显示配置文件的详细信息。 |
| `alias` | 重新生成配置文件的 shell 别名。 |
| `rename` | 重命名配置文件。 |
| `export` | 将配置文件导出为 tar.gz 存档。 |
| `import` | 从 tar.gz 存档导入配置文件。 |
| `install` | 从 git URL 或本地目录安装配置文件分发版。参见 [配置文件分发版](../user-guide/profile-distributions.md)。 |
| `update` | 重新拉取分发版管理的配置文件并重新应用其捆绑包。 |
| `info` | 显示配置文件的分发版元数据（源 URL、提交、最近更新）。 |

## `hermes profile list`

```bash
hermes profile list
```

列出所有配置文件。当前活动的配置文件以 `*` 标记。

**示例：**

```bash
$ hermes profile list
  default
* work
  dev
  personal
```

无选项。

## `hermes profile use`

```bash
hermes profile use <name>
```

将 `<name>` 设置为活动配置文件。后续所有 `hermes` 命令（不带 `-p`）将使用此配置文件。

| 参数 | 描述 |
|------|------|
| `<name>` | 要激活的配置文件名称。使用 `default` 可返回基础配置文件。 |

**示例：**

```bash
hermes profile use work
hermes profile use default
```

## `hermes profile create`

```bash
hermes profile create <name> [options]
```

创建新的配置文件。

| 参数 / 选项 | 描述 |
|-------------|------|
| `<name>` | 新配置文件的名称。必须是有效的目录名（字母数字、连字符、下划线）。 |
| `--clone` | 从当前配置文件复制 `config.yaml`、`.env`、`SOUL.md` 和技能（skill）。 |
| `--clone-all` | 从当前配置文件复制所有内容（配置、记忆、技能、定时任务、插件）。排除每个配置文件的独立历史：会话、`state.db`、备份、状态快照、检查点。 |
| `--clone-from <profile>` | 从指定配置文件（而非当前配置文件）克隆配置/技能/SOUL。除非与 `--clone-all` 一起使用，否则隐含 `--clone`。 |
| `--no-alias` | 跳过包装脚本的创建。 |
| `--description "<text>"` | 用一两句话描述此配置文件擅长做什么。看板编排器根据此描述来路由任务，而不仅依赖配置文件名称。可跳过，稍后通过 `hermes profile describe` 添加。持久化存储在 `<profile_dir>/profile.yaml` 中。 |
| `--no-skills` | 创建一个**空**配置文件，不启用任何捆绑技能。在配置文件中写入 `.no-bundled-skills` 标记，使后续 `hermes update` 运行不会重新注入捆绑集；并且禁止与 `--clone`、`--clone-from` 或 `--clone-all` 一起使用（这些选项会复制技能）。适用于窄范围编排器配置文件或不应继承完整技能目录的沙盒配置文件。对于已创建的配置文件（包括默认的 `~/.hermes`），可使用 `hermes skills opt-out` / `hermes skills opt-in` 切换此状态。 |

创建配置文件**不会**将该配置文件目录设置为终端命令的默认项目/工作目录。如果希望配置文件在特定项目中启动，请在该配置文件的 `config.yaml` 中设置 `terminal.cwd`。

**示例：**

```bash
# 空白配置文件 —— 需要完整设置
hermes profile create mybot

# 仅从当前配置文件克隆配置
hermes profile create work --clone

# 从当前配置文件克隆所有内容
hermes profile create backup --clone-all

# 从指定配置文件克隆配置
hermes profile create work2 --clone-from work

# 从指定配置文件克隆所有内容
hermes profile create work2-backup --clone-from work --clone-all
```

## `hermes profile describe`

```bash
hermes profile describe [<name>] [options]
```

读取或设置配置文件的描述信息。该描述由看板编排器使用，用于根据每个配置文件擅长什么来路由任务，而不是仅根据名称猜测。持久化存储在 `<profile_dir>/profile.yaml` 中，因此重启后仍然存在，并与网关共享。

不带任何标志时，打印当前描述（如果为空则打印 `(no description set for '<name>')`）。

| 参数 / 选项 | 描述 |
|-------------|------|
| `<name>` | 要描述的配置文件。除非使用了 `--all --auto`，否则为必需。 |
| `--text "<text>"` | 将此确切文本设置为描述（用户编写）。覆盖任何现有描述。 |
| `--auto` | 通过辅助 LLM 根据配置文件的已安装技能、配置的模型和名称自动生成一两句描述。在 `config.yaml` 的 `auxiliary.profile_describer` 下配置模型。自动生成的描述会标记为 `description_auto: true`，以便仪表板可以标记它们以供审查。 |
| `--overwrite` | 与 `--auto` 一起使用时，也会替换用户编写的描述（默认：跳过描述被明确设置的配置文件）。 |
| `--all` | 与 `--auto` 一起使用时，遍历所有缺少描述的配置文件。 |

**示例：**

```bash
# 读取当前描述
hermes profile describe researcher

# 显式设置描述
hermes profile describe researcher --text "读取源代码并撰写发现。"

# 让 LLM 生成描述
hermes profile describe researcher --auto

# 为每个没有描述的配置文件填充描述
hermes profile describe --all --auto
```

## `hermes profile delete`

```bash
hermes profile delete <name> [options]
```

删除配置文件并移除其 shell 别名。

| 参数 / 选项 | 描述 |
|-------------|------|
| `<name>` | 要删除的配置文件。 |
| `--yes`, `-y` | 跳过确认提示。 |

**示例：**

```bash
hermes profile delete mybot
hermes profile delete mybot --yes
```

:::warning
此操作将永久删除配置文件的整个目录，包括所有配置、记忆、会话和技能。不能删除当前活动的配置文件。
:::

## `hermes profile show`

```bash
hermes profile show <name>
```

显示配置文件的详细信息，包括其主目录、配置的模型、网关状态、技能数量以及配置文件状态。

此命令显示配置文件的 Hermes 主目录，而不是终端工作目录。终端命令从 `terminal.cwd` 开始（当 `cwd: "."` 时，在本地后端上为启动目录）。

| 参数 | 描述 |
|------|------|
| `<name>` | 要检查的配置文件。 |

**示例：**

```bash
$ hermes profile show work
配置文件: work
路径:    ~/.hermes/profiles/work
模型:   anthropic/claude-sonnet-4 (anthropic)
网关: 已停止
技能:  12
.env:    存在
SOUL.md: 存在
别名:   ~/.local/bin/work
```

## `hermes profile alias`

```bash
hermes profile alias <name> [options]
```

在 `~/.local/bin/<name>` 重新生成 shell 别名脚本。如果别名被意外删除，或者需要在移动 Hermes 安装后更新它，此命令很有用。

| 参数 / 选项 | 描述 |
|-------------|------|
| `<name>` | 要为其创建/更新别名的配置文件。 |
| `--remove` | 移除包装脚本而不是创建它。 |
| `--name <alias>` | 自定义别名名称（默认：配置文件名称）。 |

**示例：**

```bash
hermes profile alias work
# 创建/更新 ~/.local/bin/work

hermes profile alias work --name mywork
# 创建 ~/.local/bin/mywork

hermes profile alias work --remove
# 移除包装脚本
```

## `hermes profile rename`

```bash
hermes profile rename <old-name> <new-name>
```

重命名配置文件。更新目录和 shell 别名。

| 参数 | 描述 |
|------|------|
| `<old-name>` | 当前配置文件名称。 |
| `<new-name>` | 新配置文件名称。 |

**示例：**

```bash
hermes profile rename mybot assistant
# ~/.hermes/profiles/mybot → ~/.hermes/profiles/assistant
# ~/.local/bin/mybot → ~/.local/bin/assistant
```

## `hermes profile export`

```bash
hermes profile export <name> [options]
```

将配置文件导出为压缩的 tar.gz 存档。

| 参数 / 选项 | 描述 |
|-------------|------|
| `<name>` | 要导出的配置文件。 |
| `-o`, `--output <path>` | 输出文件路径（默认：`<name>.tar.gz`）。 |

**示例：**

```bash
hermes profile export work
# 在当前目录创建 work.tar.gz

hermes profile export work -o ./work-2026-03-29.tar.gz
```

## `hermes profile import`

```bash
hermes profile import <archive> [options]
```

从 tar.gz 存档导入配置文件。

| 参数 / 选项 | 描述 |
|-------------|------|
| `<archive>` | 要导入的 tar.gz 存档路径。 |
| `--name <name>` | 导入的配置文件的名称（默认：从存档推断）。 |

**示例：**

```bash
hermes profile import ./work-2026-03-29.tar.gz
# 从存档推断配置文件名称

hermes profile import ./work-2026-03-29.tar.gz --name work-restored
```

## 分发版命令

:::tip
**初次接触分发版？** 请从 [配置文件分发版用户指南](../user-guide/profile-distributions.md) 开始 —— 它通过完整示例介绍了为什么、何时以及如何。以下部分是一个简洁的 CLI 参考，适用于你已经知道自己想要什么的情况。
:::

分发版将配置文件转变为可共享、可版本化的制品，以 **git 仓库** 的形式发布。接收者通过单个命令安装分发版，以后可以直接在原地更新，而无需触及本地的记忆、会话或凭据。

`auth.json` 和 `.env` 永远不属于分发版的一部分 —— 它们保留在安装用户的机器上。

接收者的用户数据（记忆、会话、认证信息、用户自己对 `.env` 的编辑）在初始安装和后续更新中始终得到保留。

:::info
`hermes profile export` / `import` 仍然是用于在本地机器上进行**本地备份和恢复**的正确命令。分发版（`install` / `update` / `info`）是一个独立的概念：通过 git 发布配置文件，以便其他人可以安装它。
:::

### `hermes profile install`

```bash
hermes profile install <source> [--name <name>] [--alias] [--force] [--yes]
```

从 git URL 或本地目录安装配置文件分发版。

| 选项 | 描述 |
|------|------|
| `<source>` | Git URL（`github.com/user/repo`、`https://...`、`git@...`、`ssh://`、`git://`）或包含根目录下 `distribution.yaml` 的本地目录。 |
| `--name NAME` | 覆盖清单中的配置文件名称。 |
| `--alias` | 同时创建 shell 包装器（例如 `telemetry` → `hermes -p telemetry`）。 |
| `--force` | 覆盖同名的现有配置文件。用户数据仍然保留。 |
| `-y`, `--yes` | 跳过清单预览确认提示。 |

安装程序在要求确认之前会显示清单、列出所需的环境变量，并警告定时任务。所需的环境变量会放入一个 `.env.EXAMPLE` 文件中，你需要将其复制为 `.env` 并填写。

**示例：**

```bash
# 从 GitHub 仓库安装（简写形式）
hermes profile install github.com/kyle/telemetry-distribution --alias

# 从完整的 HTTPS git URL 安装
hermes profile install https://github.com/kyle/telemetry-distribution.git

# 从 SSH 安装
hermes profile install git@github.com:kyle/telemetry-distribution.git

# 开发期间从本地目录安装
hermes profile install ./telemetry/
```

### `hermes profile update`

```bash
hermes profile update <name> [--force-config] [--yes]
```

从其记录的源重新克隆分发版并应用更新。分发版拥有的文件（SOUL.md、skills/、cron/、mcp.json）会被覆盖；用户数据（记忆、会话、认证、.env）永远不会被触及。

默认情况下，`config.yaml` 会被保留，以保持你的本地覆盖设置。传递 `--force-config` 可将其重置为分发版提供的配置。

### `hermes profile info`

```bash
hermes profile info <name>
```

打印配置文件的分发版清单 —— 名称、版本、所需的 Hermes 版本、作者、环境变量要求、源 URL/路径，以及上次 `install` 或 `update` 时记录的 `Installed:` 时间戳。对于检查共享配置文件需要什么，以及发现“此配置文件是 6 个月前安装的，从未更新过”很有用。

`hermes profile list` 还会在 `Distribution` 列中显示分发版名称和版本，而 `hermes profile show <name>` / `delete <name>` 会显示源 URL，让你一眼看出哪些配置文件来自 git 仓库，哪些是本地创建的。

### 私有分发版

私有 git 仓库可以作为分发版源使用，无需额外配置 —— 安装命令会调用你正常的 `git` 二进制文件，因此你的 shell 已配置的任何认证方式（SSH 密钥、`git credential` 帮助程序、GitHub CLI 存储的 HTTPS 凭据）都会透明地生效。

```bash
# 使用你的 SSH 密钥，与任何其他 `git clone` 相同
hermes profile install git@github.com:your-org/internal-assistant.git

# 使用你的 git credential 帮助程序
hermes profile install https://github.com/your-org/internal-assistant.git
```

如果克隆时在终端中交互式地提示输入凭据，该提示会正常显示。请先像平常使用 `git clone` 针对同一仓库一样设置好认证，然后再安装。

### 分发版清单（`distribution.yaml`）

每个分发版在其仓库的根目录下都有一个 `distribution.yaml`：

```yaml
name: telemetry
version: 0.1.0
description: "合规性监控工具"
hermes_requires: ">=0.12.0"
author: "Your Name"
license: "MIT"
env_requires:
  - name: OPENAI_API_KEY
    description: "OpenAI API 密钥"
    required: true
  - name: GRAPHITI_MCP_URL
    description: "记忆图 URL"
    required: false
    default: "http://127.0.0.1:8000/sse"
distribution_owned:   # 可选；默认为 SOUL.md, config.yaml,
                      #   mcp.json, skills/, cron/, distribution.yaml
  - SOUL.md
  - skills/compliance/
  - cron/
```

`hermes_requires` 支持 `>=`、`<=`、`==`、`!=`、`>`、`<` 或裸版本号（视为 `>=`）。如果当前 Hermes 版本不满足规格，安装将失败并显示清晰的错误信息。

`distribution_owned` 是可选的。如果设置了，则更新时只会替换那些路径；配置文件中的其他任何内容仍归用户所有。如果省略，则应用上述默认值。

### 发布分发版

创作分发版只需执行 git push：

1. 在你的配置文件目录中，创建包含至少 `name` 和 `version` 的 `distribution.yaml`。
2. 初始化一个 git 仓库（或使用现有的），然后推送到 GitHub / GitLab / 任何 Hermes 可以克隆的主机。
3. 告诉接收者运行 `hermes profile install <your-repo-url>`。

使用 git 标签进行版本发布 —— 克隆 `HEAD` 的接收者会获得你的最新状态，你可以随时更新清单中的 `version:`。

## `hermes -p` / `hermes --profile`

```bash
hermes -p <name> <command> [options]
hermes --profile <name> <command> [options]
```

全局标志，用于在特定配置文件下运行任何 Hermes 命令，而不改变粘性默认值。此标志会在命令执行期间覆盖活动配置文件。

| 选项 | 描述 |
|------|------|
| `-p <name>`, `--profile <name>` | 此命令要使用的配置文件。 |

**示例：**

```bash
hermes -p work chat -q "检查服务器状态"
hermes --profile dev gateway start
hermes -p personal skills list
hermes -p work config edit
```

## `hermes completion`

```bash
hermes completion <shell>
```

生成 shell 补全脚本。包括配置文件名称和配置文件子命令的补全。

| 参数 | 描述 |
|------|------|
| `<shell>` | 要为其生成补全的 shell：`bash`、`zsh` 或 `fish`。 |

**示例：**

```bash
# 安装补全
hermes completion bash >> ~/.bashrc
hermes completion zsh >> ~/.zshrc
hermes completion fish > ~/.config/fish/completions/hermes.fish

# 重新加载 shell
source ~/.bashrc
```

安装后，Tab 补全可用于：
- `hermes profile <TAB>` —— 子命令（list、use、create 等）
- `hermes profile use <TAB>` —— 配置文件名称
- `hermes -p <TAB>` —— 配置文件名称

## 另请参阅

- [配置文件用户指南](../user-guide/profiles.md)
- [CLI 命令参考](./cli-commands.md)
- [常见问题解答 —— 配置文件章节](./faq.md#profiles)