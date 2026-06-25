--- frontmatter ---
---
name: my-skill
description: 简短描述（在技能搜索结果中显示）
version: 1.0.0
author: 你的名字
license: MIT
platforms: [macos, linux]          # 可选 — 限制特定操作系统平台
                                   #   有效值：macos, linux, windows
                                   #   省略则加载到所有平台（默认）
metadata:
  hermes:
    tags: [Category, Subcategory, Keywords]
    related_skills: [other-skill-name]
    requires_toolsets: [web]            # 可选 — 仅当这些工具集激活时显示
    requires_tools: [web_search]        # 可选 — 仅当这些工具可用时显示
    fallback_for_toolsets: [browser]    # 可选 — 当这些工具集激活时隐藏
    fallback_for_tools: [browser_navigate]  # 可选 — 当这些工具存在时隐藏
    config:                              # 可选 — 技能所需的 config.yaml 设置
      - key: my.setting
        description: "此设置控制的内容"
        default: "sensible-default"
        prompt: "设置提示信息"
    blueprint:                              # 可选 — 将技能标记为可运行的自动化
      schedule: "0 9 * * *"              #   cron 表达式 / "every 2h" / ISO 时间戳
      deliver: origin                    #   可选（默认 origin）
      prompt: "每次运行的指令"  # 可选
      no_agent: false                    # 可选
required_environment_variables:          # 可选 — 技能所需的环境变量
  - name: MY_API_KEY
    prompt: "输入你的 API 密钥"
    help: "在 https://example.com 获取"
    required_for: "API 访问"
---

--- body ---
# 技能标题

简短介绍。

## 使用时机
触发条件 — 代理（Agent）何时应加载此技能？

## 快速参考
常用命令或 API 调用的表格。

## 操作步骤
代理（Agent）遵循的分步说明。

## 常见陷阱
已知的失败模式及如何处理。

## 验证
代理（Agent）如何确认操作成功。

### 平台特定技能

技能可以使用 `platforms` 字段限制自身仅在特定操作系统上运行：

```yaml
platforms: [macos]            # 仅 macOS（例如 iMessage、Apple 提醒事项）
platforms: [macos, linux]     # macOS 和 Linux
platforms: [windows]          # 仅 Windows
```

设置后，在不兼容的平台上，该技能会自动从系统提示（system prompt）、`skills_list()` 和斜杠命令中隐藏。如果省略或为空，则技能会在所有平台上加载（向后兼容）。

### 条件技能激活

技能可以声明对特定工具或工具集的依赖。这控制该技能在给定会话中是否出现在系统提示中。

```yaml
metadata:
  hermes:
    requires_toolsets: [web]           # 如果 web 工具集未激活则隐藏
    requires_tools: [web_search]       # 如果 web_search 工具不可用则隐藏
    fallback_for_toolsets: [browser]   # 如果 browser 工具集已激活则隐藏
    fallback_for_tools: [browser_navigate]  # 如果 browser_navigate 可用则隐藏
```

| 字段 | 行为 |
|-------|----------|
| `requires_toolsets` | 当**任一**列出的工具集**不可用**时，技能被**隐藏** |
| `requires_tools` | 当**任一**列出的工具**不可用**时，技能被**隐藏** |
| `fallback_for_toolsets` | 当**任一**列出的工具集**可用**时，技能被**隐藏** |
| `fallback_for_tools` | 当**任一**列出的工具**可用**时，技能被**隐藏** |

**`fallback_for_*` 的使用场景：** 创建一个在主要工具不可用时作为替代方案的技能。例如，一个 `duckduckgo-search` 技能带有 `fallback_for_tools: [web_search]`，仅当需要 API 密钥的 web 搜索工具未配置时才显示。

**`requires_*` 的使用场景：** 创建一个仅在特定工具存在时才有意义的技能。例如，一个带有 `requires_toolsets: [web]` 的网页抓取工作流技能，在 web 工具被禁用时不会使提示混乱。

### 环境变量要求

技能可以声明它们需要的环境变量。当通过 `skill_view` 加载技能时，其所需变量会自动注册以传递到沙盒执行环境（终端、execute_code）。

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: "Tenor API 密钥"               # 提示用户时显示
    help: "在 https://tenor.com 获取你的密钥"  # 帮助文本或 URL
    required_for: "GIF 搜索功能"   # 什么需要此变量
```

每个条目支持：
- `name`（必需）— 环境变量名称
- `prompt`（可选）— 询问用户时的提示文本
- `help`（可选）— 获取该值的帮助文本或 URL
- `required_for`（可选）— 描述需要此变量的功能

用户也可以手动在 `config.yaml` 中配置传递变量：

```yaml
terminal:
  env_passthrough:
    - MY_CUSTOM_VAR
    - ANOTHER_VAR
```

参见 `skills/apple/` 了解仅 macOS 技能的示例。

## 加载时的安全设置

当技能需要 API 密钥或令牌时，使用 `required_environment_variables`。缺失值**不会**隐藏技能不被发现。相反，当在本地 CLI 中加载技能时，Hermes 会安全地提示用户输入这些值。

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API 密钥
    help: 从 https://developers.google.com/tenor 获取密钥
    required_for: 完整功能
```

用户可以跳过设置并继续加载技能。Hermes 永远不会向模型暴露原始秘密值。网关（Gateway）和消息传递（Messaging）会话会显示本地设置指南，而不是在带内收集机密。

:::tip 沙盒传递
当你的技能被加载时，任何已声明的 `required_environment_variables` 中已设置的值会自动传递到 `execute_code` 和 `terminal` 沙盒中——包括远程后端，如 Docker 和 Modal。你技能的脚本可以访问 `$TENOR_API_KEY`（或在 Python 中为 `os.environ["TENOR_API_KEY"]`），而无需用户额外配置。详情请参见[环境变量传递](/user-guide/security#environment-variable-passthrough)。
:::

旧版 `prerequisites.env_vars` 仍作为向后兼容的别名受支持。

### 配置设置（config.yaml）

技能可以声明非秘密的设置，这些设置存储在 `config.yaml` 的 `skills.config` 命名空间下。与环境变量（存储在 `.env` 中的秘密）不同，配置设置用于路径、偏好和其他非敏感值。

```yaml
metadata:
  hermes:
    config:
      - key: myplugin.path
        description: 插件数据目录的路径
        default: "~/myplugin-data"
        prompt: 插件数据目录路径
      - key: myplugin.domain
        description: 插件操作的领域
        default: ""
        prompt: 插件领域（例如，AI/ML 研究）
```

每个条目支持：
- `key`（必需）— 设置的点路径（例如 `myplugin.path`）
- `description`（必需）— 解释设置控制的内容
- `default`（可选）— 如果用户未配置则使用的默认值
- `prompt`（可选）— 在 `hermes config migrate` 期间显示的提示文本；如果没有则回退到 `description`

**工作原理：**

1. **存储：** 值被写入 `config.yaml` 的 `skills.config.<key>` 下：
   ```yaml
   skills:
     config:
       myplugin:
         path: ~/my-data
   ```

2. **发现：** `hermes config migrate` 扫描所有启用的技能，找到未配置的设置，并提示用户。设置也会出现在 `hermes config show` 的“技能设置”下。

3. **运行时注入：** 当技能加载时，其配置值会被解析并附加到技能消息中：
   ```
   [技能配置（来自 ~/.hermes/config.yaml）：
     myplugin.path = /home/user/my-data
   ]
   ```
   代理（Agent）可以看到配置后的值，而无需自行读取 `config.yaml`。

4. **手动设置：** 用户也可以直接设置值：
   ```bash
   hermes config set skills.config.myplugin.path ~/my-data
   ```

:::tip 何时使用哪种方式
使用 `required_environment_variables` 存储 API 密钥、令牌和其他**秘密**（存储在 `~/.hermes/.env` 中，绝不向模型显示）。使用 `config` 存储**路径、偏好和非敏感设置**（存储在 `config.yaml` 中，在 config show 中可见）。
:::

### 凭证文件要求（OAuth 令牌等）

使用 OAuth 或基于文件凭证的技能可以声明需要挂载到远程沙盒中的文件。这适用于作为**文件**（而非环境变量）存储的凭证——通常是设置脚本生成的 OAuth 令牌文件。

```yaml
required_credential_files:
  - path: google_token.json
    description: Google OAuth2 令牌（由设置脚本创建）
  - path: google_client_secret.json
    description: Google OAuth2 客户端凭证
```

每个条目支持：
- `path`（必需）— 相对于 `~/.hermes/` 的文件路径
- `description`（可选）— 解释文件的内容及其创建方式

加载时，Hermes 会检查这些文件是否存在。缺失的文件会触发 `setup_needed`。现有的文件会自动：
- **挂载到 Docker** 容器中作为只读绑定挂载
- **同步到 Modal** 沙盒中（创建时 + 每个命令之前，以便会话中的 OAuth 正常工作）
- 在**本地**后端可直接使用，无需特殊处理

:::tip 何时使用哪种方式
使用 `required_environment_variables` 存储简单的 API 密钥和令牌（字符串存储在 `~/.hermes/.env` 中）。使用 `required_credential_files` 存储 OAuth 令牌文件、客户端密钥、服务账号 JSON、证书，或任何磁盘上的凭证文件。
:::

参见 `skills/productivity/google-workspace/SKILL.md` 获取同时使用两者的完整示例。

## 技能指南

### 无外部依赖

优先使用标准库 Python、curl 和现有的 Hermes 工具（`web_extract`、`terminal`、`read_file`）。如果需要依赖，请在技能中记录安装步骤。

### 逐步披露

将最常见的工作流程放在最前面。边缘情况和高级用法放在底部。这有助于在常见任务中减少令牌使用。

### 包含辅助脚本

对于 XML/JSON 解析或复杂逻辑，请将辅助脚本放在 `scripts/` 中——不要期望 LLM 每次都内联编写解析器。

### 以文档形式交付媒体（`[[as_document]]`）

如果你的技能生成高分辨率截图、图表或任何有损预览压缩会损害质量的图像——在响应中的某处（通常是最后一行）发出字面指令 `[[as_document]]`。网关（Gateway）会去除该指令，并将该响应中提取的每个媒体路径作为可下载的文件附件提供，而不是作为内联图像气泡。完整语义请参见[技能输出和媒体交付](../user-guide/features/skills.md#skill-output-and-media-delivery)。

#### 从 SKILL.md 引用捆绑脚本

当技能被加载时，激活消息会以 `[技能目录：/abs/path]` 的形式暴露绝对技能目录，并且还会在 SKILL.md 主体中的任何位置替换两个模板令牌：

| 令牌 | 替换为 |
|---|---|
| `${HERMES_SKILL_DIR}` | 技能目录的绝对路径 |
| `${HERMES_SESSION_ID}` | 当前会话 ID（如果没有会话则保留原样） |

因此，SKILL.md 可以告诉代理（Agent）直接运行捆绑脚本：

```markdown
要分析输入，请运行：

    node ${HERMES_SKILL_DIR}/scripts/analyse.js <input>
```

代理（Agent）会看到替换后的绝对路径，并使用 `terminal` 工具执行可立即运行的命令——无需路径运算，无需额外的 `skill_view` 往返。可以通过在 `config.yaml` 中设置 `skills.template_vars: false` 全局禁用替换。

#### 内联 Shell 代码片段（可选加入）

技能也可以在 SKILL.md 主体中嵌入内联 shell 代码片段，格式为 `` !`cmd` ``。启用后，每个代码片段的 stdout 会在代理（Agent）读取消息前内联到消息中，从而使技能能够注入动态上下文：

```markdown
当前日期：!`date -u +%Y-%m-%d`
Git 分支：!`git -C ${HERMES_SKILL_DIR} rev-parse --abbrev-ref HEAD`
```

此功能**默认关闭**——SKILL.md 中的任何代码片段都会未经批准在主机上运行，因此仅为你信任的技能源启用：

```yaml
# config.yaml
skills:
  inline_shell: true
  inline_shell_timeout: 10   # 每个代码片段的超时时间（秒）
```

代码片段以技能目录作为工作目录运行，输出限制为 4000 个字符。失败（超时、非零退出）会以简短的 `[inline-shell error: ...]` 标记显示，而不是破坏整个技能。

### 测试它

运行技能并验证代理（Agent）是否正确遵循指令：

```bash
hermes chat --toolsets skills -q "使用 X 技能执行 Y 操作"
```

## 技能应该存放在哪里？

捆绑技能（在 `skills/` 中）随每次 Hermes 安装一起提供。它们应该**对大多数用户广泛有用**：

- 文档处理、网络研究、常见开发工作流程、系统管理
- 被广泛用户定期使用

如果你的技能是官方的且有用，但并非普遍需要（例如，付费服务集成、重量级依赖），请将其放入 **`optional-skills/`** 中——它会随仓库一起提供，可通过 `hermes skills browse` 发现（标记为“官方”），并以内置信任安装。

如果你的技能是专业化的、社区贡献的或小众的，它更适合放在 **Skills Hub** 中——上传到注册表并通过 `hermes skills install` 分享。

## 蓝图（Blueprints）：既是技能又是自动化

**蓝图**是一个普通技能，但在其 frontmatter 中额外声明了一个调度。添加 `metadata.hermes.blueprint` 块后，该技能就变成了一个可共享、可运行的自动化：

```yaml
metadata:
  hermes:
    tags: [blueprint, email]
    blueprint:
      schedule: "0 8 * * *"     # 存在 `blueprint:` 标记其为可运行
      deliver: telegram          # 可选（默认：origin）
      prompt: "总结我的未读邮件和今天的日历。"  # 可选
      no_agent: false            # 可选
```

因为蓝图**是**一个技能，所以它可以在整个技能管道中无变化地流动——搜索、检查、安装、安全扫描、来源、接入点、集中索引以及用于共享的 `hermes skills publish`。无需学习新内容。

**安装蓝图。** 当你安装一个带有 `blueprint:` 块的技能时，Hermes 会将其注册为**建议的 cron 任务**，而不是直接调度。调度是**选择性加入的**——安装永远不会默默创建重复任务。你可以通过 `/suggestions` 查看并接受它：

```bash
hermes skills install owner/morning-brief
# → 蓝图：'morning-brief' 是一个自动化（调度 0 8 * * *）。
#   已添加到你的建议中——运行 /suggestions 进行调度或拒绝。

# 然后，在会话中：
/suggestions             # 列出待处理的建议，编号
/suggestions accept 1    # 创建 cron 任务
/suggestions dismiss 1   # 不再提供该建议
```

蓝图是统一建议 Cron 任务界面的一个**来源**——同一个位置会出现精选的入门自动化以及（稍后）使用模式和集成建议。参见下面的[建议 Cron 任务](#suggested-cron-jobs)。

**分享你构建的自动化。** 由 cron 任务加载的蓝图（`hermes cron create --skill <name> ...`）可以导出回 SKILL.md 并像任何其他技能一样发布，因此你为自己调优的自动化可以成为其他人一键安装的命令。

蓝图层没有添加新的对象类型、存储或传输——蓝图就是技能，调度就是 cron 任务，共享就是现有的发布/接入点/索引路径。

## 建议 Cron 任务

Hermes 可以*提议*自动化，让你一键接受，而不是让你手动组装 cron 任务。每个提议都通过一个界面——`/suggestions` 命令——流动，无论其来源如何：

| 来源 | 触发方式 |
|--------|---------|
| `catalog` | 精选的入门自动化（`/suggestions catalog`）——每日简报、重要邮件监控、周报、工作日开始提醒 |
| `blueprint` | 你安装了一个带有 `blueprint:` 块的技能 |
| `usage` | 后台审查注意到一个重复请求，适合用调度来处理 |
| `integration` | 你连接了一个账户（Gmail、GitHub 等），并提供了明显的自动化 |

```bash
/suggestions             # 列出待处理的建议
/suggestions accept N    # 调度建议 N（创建 cron 任务）
/suggestions dismiss N   # 拒绝它——永久记录，不再提供
/suggestions catalog     # 添加精选的入门自动化
```

接受建议会调用与 `cronjob` 工具相同的 `cron.jobs.create_job`——没有第二个任务引擎。建议**从不**自动创建任务；接受始终是明确的。被拒绝的建议会通过一个稳定键记录，因此同一提议不会再次提供。待处理列表有上限，因此永远不会成为烦人的通知墙。

**重要邮件监控**目录条目遵循轮询→分类→呈现模式：它使用一个便宜的分类模型（`config.yaml` 中的 `auxiliary.monitor`）对收件箱项目评分，并只提供高于紧急阈值的项目，其他情况下保持静默。

## 发布技能

### 发布到 Skills Hub

```bash
hermes skills publish skills/my-skill --to github --repo owner/repo
```

### 发布到自定义仓库

将你的仓库添加为接入点：

```bash
hermes skills tap add owner/repo
```

用户随后可以从你的仓库搜索和安装。

## 安全扫描

所有从中心安装的技能都会经过安全扫描器，检查以下内容：

- 数据泄露模式
- 提示注入尝试
- 破坏性命令
- Shell 注入

信任级别：
- `builtin` — 随 Hermes 提供（始终受信任）
- `official` — 来自仓库中的 `optional-skills/`（内置信任，无第三方警告）
- `trusted` — 来自 openai/skills、anthropics/skills、huggingface/skills
- `community` — 非危险的发现可以通过 `--force` 覆盖；`dangerous` 判定仍被阻止

Hermes 现在可以从多个外部发现模型消费第三方技能：
- 直接的 GitHub 标识符（例如 `openai/skills/k8s`）
- `skills.sh` 标识符（例如 `skills-sh/vercel-labs/json-render/json-render-react`）
- 从 `/.well-known/skills/index.json` 服务的知名端点

如果你希望你的技能无需特定 GitHub 安装器即可被发现，请考虑除了在仓库或市场中发布外，还通过知名端点提供服务。