---
title: Skills
---

name: deploy-runbook
description: 我们的部署运行手册 — 服务、回滚、Slack频道
version: 1.0.0
author: My Org Platform Team
metadata:
  hermes:
    tags: [deployment, runbook, internal]
---

--- body ---
# 部署运行手册（Deploy Runbook）

步骤1：...
```

推送到 GitHub 后，任何 Hermes 用户都可以订阅并安装：

```bash
hermes skills tap add my-org/hermes-skills
hermes skills search deploy
hermes skills install my-org/hermes-skills/deploy-runbook
```

#### 非默认路径（Non-default paths）

如果你的技能（skills）不在 `skills/` 目录下（常见情况是在现有项目中添加 `skills/` 子树），请编辑 `~/.hermes/.hub/taps.json` 中的 tap 条目：

```json
{
  "taps": [
    {"repo": "my-org/platform-docs", "path": "internal/skills/"}
  ]
}
```

`hermes skills tap add` 命令行工具默认将新 tap 的路径设置为 `path: "skills/"`；如果需要不同路径，请直接编辑文件。`hermes skills tap list` 会显示每个 tap 的实际有效路径。

#### 直接安装单个技能（不添加 tap）

用户也可以直接从任何公共 GitHub 仓库安装单个技能，而无需将整个仓库添加为 tap：

```bash
hermes skills install owner/repo/skills/my-workflow
```

当你只想分享一个技能而不希望用户订阅你的整个注册库时，这很有用。

#### Tap 的信任级别（Trust levels for taps）

新添加的 tap 默认被分配 `community`（社区）信任级别。从中安装的技能会经过标准安全扫描，并在首次安装时显示第三方警告面板。如果你的组织或广泛信任的来源应获得更高信任级别，请将其仓库地址添加到 `tools/skills_hub.py` 的 `TRUSTED_REPOS` 中（需要 Hermes 核心 PR）。

#### Tap 管理

```bash
hermes skills tap list                                # 显示所有配置的 tap
hermes skills tap add myorg/skills-repo               # 添加（默认路径：skills/）
hermes skills tap remove myorg/skills-repo            # 移除
```

在运行中的会话内部：

```
/skills tap list
/skills tap add myorg/skills-repo
/skills tap remove myorg/skills-repo
```

Tap 存储在 `~/.hermes/.hub/taps.json` 中（按需创建）。

## 捆绑技能更新（Bundled skill updates）—— `hermes skills reset`

Hermes 在仓库的 `skills/` 目录中附带了一组捆绑技能。在安装和每次 `hermes update` 时，同步过程会将这些技能复制到 `~/.hermes/skills/` 中，并在 `~/.hermes/skills/.bundled_manifest` 中记录一个清单，该清单将每个技能名称映射到同步时的内容哈希（**原始哈希 origin hash**）。

每次同步时，Hermes 会重新计算本地副本的哈希值，并与原始哈希值进行比较：

- **未更改** → 可以安全拉取上游更改，复制新的捆绑版本，并记录新的原始哈希。
- **已更改** → 被视为**用户修改**并永久跳过，因此你的编辑永远不会被覆盖。

这种保护机制很好，但有一个尖锐的边缘情况。如果你编辑了一个捆绑技能，之后又想放弃更改，通过从 `~/.hermes/hermes-agent/skills/` 复制粘贴来恢复捆绑版本，清单中仍然保留着上次成功同步时的*旧*原始哈希。你新复制的内容（当前的捆绑哈希）与该旧原始哈希不匹配，因此同步会继续将其标记为用户修改。

`hermes skills reset` 是逃生通道：

```bash
# 安全操作：清除该技能的清单条目。保留你当前的副本，
# 但下次同步会基于它重新建立基线，以便未来的更新正常工作。
hermes skills reset google-workspace

# 完全恢复：同时删除本地副本并重新复制当前捆绑版本。
# 当你想要恢复原始的官方技能时使用。
hermes skills reset google-workspace --restore

# 非交互模式（例如在脚本或 TUI 模式中）——跳过 --restore 确认。
hermes skills reset google-workspace --restore --yes
```

相同的命令在聊天中可作为斜杠命令使用：

```text
/skills reset google-workspace
/skills reset google-workspace --restore
```

:::note 配置文件（Profiles）
每个配置文件在其自己的 `HERMES_HOME` 下拥有自己的 `.bundled_manifest`，因此 `hermes -p coder skills reset <name>` 只会影响该配置文件。
:::

### 斜杠命令（Slash commands）（在聊天内）

所有相同的命令都适用于 `/skills`：

```text
/skills browse
/skills search react --source skills-sh
/skills search https://mintlify.com/docs --source well-known
/skills inspect skills-sh/vercel-labs/json-render/json-render-react
/skills install openai/skills/skill-creator --force
/skills check
/skills update
/skills reset google-workspace
/skills list
```

官方可选技能仍使用 `official/security/1password` 和 `official/migration/openclaw-migration` 等标识符。