---
title: "Openclaw 迁移 — 将用户的 OpenClaw 自定义足迹迁移到 Hermes Agent"
sidebar_label: "Openclaw 迁移"
description: "将用户的 OpenClaw 自定义足迹迁移到 Hermes Agent"
---

--- body ---
{/* 此页面由 website/scripts/generate-skill-docs.py 从技能对应的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Openclaw 迁移

将用户的 OpenClaw 自定义足迹迁移到 Hermes Agent。从 ~/.openclaw 导入 Hermes 兼容的记忆（memory）、SOUL.md、命令允许列表（command allowlist）、用户技能（user skills）以及选定的工作区资产（workspace assets），然后精确报告哪些内容无法迁移及原因。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/migration/openclaw-migration` 安装 |
| 路径 | `optional-skills/migration/openclaw-migration` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent (Nous Research) |
| 许可 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Migration`, `OpenClaw`, `Hermes`, `Memory`, `Persona`, `Import` |
| 相关技能 | [`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) |

## 参考：完整 SKILL.md

:::info
以下是此技能被触发时 Hermes 加载的完整技能定义。这是技能激活时代理（agent）看到的指令。
:::

# OpenClaw -> Hermes 迁移

当用户希望以最少的手动清理将 OpenClaw 设置迁移到 Hermes Agent 时使用此技能。

## CLI 命令

快速、非交互式迁移，使用内置 CLI 命令：

```bash
hermes claw migrate              # 全交互式迁移
hermes claw migrate --dry-run    # 预览将要迁移的内容
hermes claw migrate --preset user-data   # 迁移时不包含机密（secrets）
hermes claw migrate --overwrite  # 覆盖现有冲突
hermes claw migrate --source /custom/path/.openclaw  # 自定义源路径
```

CLI 命令运行的是下面描述的同一迁移脚本。当你想要一个带有 dry-run 预览和逐项冲突解决（conflict resolution）的交互式引导迁移时，使用此技能（通过代理）。

**首次设置：** `hermes setup` 向导会自动检测 `~/.openclaw` 并在配置开始前提供迁移选项。

## 此技能的功能

它使用 `scripts/openclaw_to_hermes.py` 来：

- 将 `SOUL.md` 导入 Hermes 主目录，作为 `SOUL.md`
- 将 OpenClaw 的 `MEMORY.md` 和 `USER.md` 转换为 Hermes 记忆条目
- 将 OpenClaw 命令审批模式合并到 Hermes 的 `command_allowlist`
- 迁移 Hermes 兼容的消息设置，例如 `TELEGRAM_ALLOWED_USERS`，并将 OpenClaw 工作区设置映射到 Hermes 工作目录配置
- 将 OpenClaw 技能复制到 `~/.hermes/skills/openclaw-imports/`
- 可选地将 OpenClaw 工作区指令文件复制到选定的 Hermes 工作区
- 将兼容的工作区资产（如 `workspace/tts/`）镜像到 `~/.hermes/tts/`
- 将没有直接 Hermes 目的地的非机密文档归档
- 生成结构化报告，列出已迁移项、冲突、已跳过项及原因

## 路径解析

辅助脚本位于此技能目录中：

- `scripts/openclaw_to_hermes.py`

当此技能从技能中心（Skills Hub）安装时，通常位置是：

- `~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py`

不要猜测较短路径如 `~/.hermes/skills/openclaw-migration/...`。

在运行辅助脚本之前：

1. 优先使用 `~/.hermes/skills/migration/openclaw-migration/` 下的已安装路径。
2. 如果该路径失败，检查已安装的技能目录，并根据已安装的 `SKILL.md` 解析脚本的相对路径。
3. 仅当已安装位置缺失或技能被手动移动时才使用 `find` 作为后备。
4. 调用终端工具时，不要传递 `workdir: "~"`。使用绝对目录（如用户主目录），或完全省略 `workdir`。

使用 `--migrate-secrets` 时，它还会导入一小部分允许列表中的 Hermes 兼容机密，目前包括：

- `TELEGRAM_BOT_TOKEN`

## 默认工作流程

1. 首先通过 dry run 检查。
2. 提供简明摘要，说明哪些可以迁移、哪些不能迁移、哪些将被归档。
3. 如果 `clarify` 工具可用，则将其用于用户决策，而不是要求自由格式的文本回复。
4. 如果 dry run 发现导入的技能目录存在冲突，在执行之前询问应如何处理。
5. 在执行前询问用户选择两种受支持的迁移模式中的哪一种。
6. 仅当用户希望导入工作区指令文件时，才询问目标工作区路径。
7. 使用匹配的预设和标志执行迁移。
8. 总结结果，特别强调：
   - 已迁移的内容
   - 已归档以供手动审查的内容
   - 已跳过及原因

## 用户交互协议

Hermes CLI 支持 `clarify` 工具用于交互式提示，但它的限制是：

- 一次只能做一个选择
- 最多 4 个预定义选项
- 一个自动的“其他”自由文本选项

它**不支持**单次提示中的真正多选复选框。

对于每次 `clarify` 调用：

- 始终包含非空的 `question`
- 仅针对真正的可选项提供 `choices`
- 将 `choices` 保持在 2-4 个纯字符串选项
- 永远不要发出占位符或截断的选项，例如 `...`
- 永远不要用额外的空格填充或修饰选项
- 永远不要在问题中包含虚假的表单字段，例如 `在此处输入目录`、需要填写的空行或 `_____` 等下划线
- 对于开放式路径问题，仅询问普通句子；用户会在面板下方的正常 CLI 提示符中键入内容

如果 `clarify` 调用返回错误，检查错误文本，修正载荷，并使用有效的 `question` 和干净的选项重试一次。

当 `clarify` 可用且 dry run 揭示任何需要用户决策的事项时，你的**下一步操作必须是一个 `clarify` 工具调用**。
不要以普通的助手消息结束回合，例如：

- “让我展示选择”
- “你想怎么做？”
- “以下是选项”

如果需要用户决策，请先通过 `clarify` 收集，然后再生成更多文本。
如果存在多个未解决的决策，不要在它们之间插入解释性的助手消息。收到一个 `clarify` 响应后，你的下一步操作通常应该是下一个必需的 `clarify` 调用。

每当 dry run 报告以下内容时，将 `workspace-agents` 视为未解决的决策：

- `kind="workspace-agents"`
- `status="skipped"`
- 原因包含 `No workspace target was provided`

在这种情况下，你必须在执行前询问工作区指令。不要默默将其视为跳过决策。

由于该限制，使用以下简化的决策流程：

1. 对于 `SOUL.md` 冲突，使用 `clarify`，选项如：
   - `keep existing`（保留现有）
   - `overwrite with backup`（覆盖并备份）
   - `review first`（先审查）
2. 如果 dry run 显示一个或多个 `kind="skill"` 项且 `status="conflict"`，使用 `clarify`，选项如：
   - `keep existing skills`（保留现有技能）
   - `overwrite conflicting skills with backup`（覆盖冲突技能并备份）
   - `import conflicting skills under renamed folders`（将冲突技能导入到重命名的文件夹下）
3. 对于工作区指令，使用 `clarify`，选项如：
   - `skip workspace instructions`（跳过工作区指令）
   - `copy to a workspace path`（复制到工作区路径）
   - `decide later`（稍后决定）
4. 如果用户选择复制工作区指令，则提出后续开放式 `clarify` 问题，要求提供**绝对路径**。
5. 如果用户选择“跳过工作区指令”或“稍后决定”，则不带 `--workspace-target` 继续。
5. 对于迁移模式，使用 `clarify`，提供以下 3 个选项：
   - `user-data only`（仅用户数据）
   - `full compatible migration`（完全兼容迁移）
   - `cancel`（取消）
6. `user-data only` 意味着：迁移用户数据和兼容配置，但**不**导入允许列表中的机密。
7. `full compatible migration` 意味着：迁移相同的兼容用户数据以及允许列表中的机密（如果存在）。
8. 如果 `clarify` 不可用，则用正常文本询问相同的问题，但仍将答案限制为 `user-data only`、`full compatible migration` 或 `cancel`。

执行门控：

- 如果由 `No workspace target was provided` 引起的 `workspace-agents` 跳过仍未解决，不要执行。
- 解决它的唯一有效方法是：
  - 用户明确选择“跳过工作区指令”
  - 用户明确选择“稍后决定”
  - 用户选择“复制到工作区路径”后提供工作区路径
- dry run 中缺少工作区目标本身并不构成执行许可。
- 在任何必需的 `clarify` 决策未解决之前不要执行。

使用以下确切的 `clarify` 载荷形状作为默认模式：

- `{"question":"Your existing SOUL.md conflicts with the imported one. What should I do?","choices":["keep existing","overwrite with backup","review first"]}`
- `{"question":"One or more imported OpenClaw skills already exist in Hermes. How should I handle those skill conflicts?","choices":["keep existing skills","overwrite conflicting skills with backup","import conflicting skills under renamed folders"]}`
- `{"question":"Choose migration mode: migrate only user data, or run the full compatible migration including allowlisted secrets?","choices":["user-data only","full compatible migration","cancel"]}`
- `{"question":"Do you want to copy the OpenClaw workspace instructions file into a Hermes workspace?","choices":["skip workspace instructions","copy to a workspace path","decide later"]}`
- `{"question":"Please provide an absolute path where the workspace instructions should be copied."}`

## 决策到命令的映射

将用户决策精确映射到命令标志：

- 如果用户为 `SOUL.md` 选择 `keep existing`，则**不**添加 `--overwrite`。
- 如果用户选择 `overwrite with backup`，则添加 `--overwrite`。
- 如果用户选择 `review first`，则先停止执行并审查相关文件。
- 如果用户选择 `keep existing skills`，则添加 `--skill-conflict skip`。
- 如果用户选择 `overwrite conflicting skills with backup`，则添加 `--skill-conflict overwrite`。
- 如果用户选择 `import conflicting skills under renamed folders`，则添加 `--skill-conflict rename`。
- 如果用户选择 `user-data only`，则使用 `--preset user-data` 执行，并且**不**添加 `--migrate-secrets`。
- 如果用户选择 `full compatible migration`，则使用 `--preset full --migrate-secrets` 执行。
- 仅当用户明确提供了绝对工作区路径时才添加 `--workspace-target`。
- 如果用户选择 `skip workspace instructions` 或 `decide later`，则不添加 `--workspace-target`。

在执行之前，用简单的语言重申确切的命令计划，并确保它与用户的选择匹配。

## 运行后报告规则

执行后，将脚本的 JSON 输出视为真理来源。

1. 所有计数基于 `report.summary`。
2. 仅当项的 `status` 恰好为 `migrated` 时，才将其列在“已成功迁移”下。
3. 除非报告显示该项为 `migrated`，否则不要声称冲突已解决。
4. 除非报告项 `kind="soul"` 的状态为 `migrated`，否则不要说明 `SOUL.md` 已被覆盖。
5. 如果 `report.summary.conflict > 0`，则包含冲突部分，而不是默默暗示成功。
6. 如果计数与列出的项不一致，则在响应前修正列表以匹配报告。
7. 如果报告中有 `output_dir` 路径，请包含该路径，以便用户可以检查 `report.json`、`summary.md`、备份和归档文件。
8. 对于记忆或用户配置文件溢出，除非报告明确显示归档路径，否则不要说条目已被归档。如果 `details.overflow_file` 存在，则说明完整溢出列表已导出到那里。
9. 如果技能是在重命名的文件夹下导入的，报告最终目标并提及 `details.renamed_from`。
10. 如果存在 `report.skill_conflict_mode`，将其作为所选导入技能冲突策略的真实来源。
11. 如果项的状态为 `skipped`，则不要将其描述为已覆盖、已备份、已迁移或已解决。
12. 如果 `kind="soul"` 状态为 `skipped` 且原因 `Target already matches source`，则说明它保持不变，并且不要提及备份。
13. 如果重命名的导入技能具有空的 `details.backup`，不要暗示现有的 Hermes 技能已被重命名或备份。仅说明导入的副本已放置在新目标中，并引用 `details.renamed_from` 作为保持原位的既有文件夹。

## 迁移预设

正常使用中优先使用这两个预设：

- `user-data`
- `full`

`user-data` 包括：

- `soul`
- `workspace-agents`
- `memory`
- `user-profile`
- `messaging-settings`
- `command-allowlist`
- `skills`
- `tts-assets`
- `archive`

`full` 包括 `user-data` 中的所有内容以及：

- `secret-settings`

辅助脚本仍支持类别级别的 `--include` / `--exclude`，但将其视为高级后备方案，而非默认用户体验。

## 命令

完整发现的 Dry run：

```bash
python3 ~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py
```

使用终端工具时，首选绝对调用模式，例如：

```json
{"command":"python3 /home/USER/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py","workdir":"/home/USER"}
```

使用 user-data 预设的 Dry run：

```bash
python3 ~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py --preset user-data
```

执行 user-data 迁移：

```bash
python3 ~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py --execute --preset user-data --skill-conflict skip
```

执行完全兼容迁移：

```bash
python3 ~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py --execute --preset full --migrate-secrets --skill-conflict skip
```

执行时包含工作区指令：

```bash
python3 ~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py --execute --preset user-data --skill-conflict rename --workspace-target "/absolute/workspace/path"
```

默认不要使用 `$PWD` 或主目录作为工作区目标。先询问明确的工作区路径。

## 重要规则

1. 除非用户明确要求立即执行，否则在写入前先运行 dry run。
2. 默认不迁移机密（secrets）。令牌、认证 blob、设备凭据和原始网关配置应保留在 Hermes 之外，除非用户明确要求机密迁移。
3. 不要默默覆盖非空的 Hermes 目标，除非用户明确希望如此。启用覆盖时，辅助脚本会保留备份。
4. 始终向用户提供跳过项报告。该报告是迁移的一部分，而非可选的额外内容。
5. 优先使用主 OpenClaw 工作区（`~/.openclaw/workspace/`）而非 `workspace.default/`。仅当主文件缺失时才将默认工作区作为后备。
6. 即使在机密迁移模式下，也只迁移具有干净 Hermes 目的地的机密。不支持的认证 blob 仍必须报告为跳过。
7. 如果 dry run 显示大量资产复制、冲突的 `SOUL.md` 或溢出的记忆条目，在执行前单独指出这些情况。
8. 如果用户不确定，默认选择 `user-data only`。
9. 仅当用户明确提供了目标工作区路径时才包含 `workspace-agents`。
10. 将类别级别的 `--include` / `--exclude` 视为高级逃生出口，而非正常流程。
11. 如果 `clarify` 可用，不要在 dry-run 摘要末尾使用模糊的“你想怎么做？”。改用结构化后续提示。
12. 如果真实的选择提示可用，不要使用开放式的 `clarify` 提示。优先使用可选选项，然后仅对绝对路径或文件审查请求使用自由文本。
13. 在 dry run 后，如果仍有未解决的决策，绝不要在总结后停止。立即使用 `clarify` 获取最高优先级的阻塞决策。
14. 后续问题的优先级顺序：
    - `SOUL.md` 冲突
    - 导入技能冲突
    - 迁移模式
    - 工作区指令目标
15. 不要在同一消息中承诺稍后展示选择。通过实际调用 `clarify` 来展示它们。
16. 在 migration-mode 答案之后，明确检查 `workspace-agents` 是否仍未解决。如果是，则你的下一步操作必须是 workspace-instructions 的 `clarify` 调用。
17. 在任何 `clarify` 答案之后，如果另一个必需的决策仍然存在，不要叙述刚刚决定的内容。立即询问下一个必需的问题。

## 预期结果

成功运行后，用户应拥有：

- 已导入的 Hermes 角色状态（persona）
- 已填充 Hermes 记忆文件，包含转换后的 OpenClaw 知识
- OpenClaw 技能位于 `~/.hermes/skills/openclaw-imports/` 下
- 一份迁移报告，显示任何冲突、遗漏或不支持的数据