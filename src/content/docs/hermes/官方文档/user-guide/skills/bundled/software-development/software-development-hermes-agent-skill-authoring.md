---
title: Hermes Agent Skill Authoring
---

name: my-skill-name               # 小写字母，连字符，≤64 个字符（MAX_NAME_LENGTH）
description: 当 <触发条件> 时使用。 <单行行为描述>。
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [简短, 描述性, 标签]
    related_skills: [other-skill, another-skill]
---

--- body ---
```

`version` / `author` / `license` / `metadata` 并非由验证器（validator）强制要求，但每个对等技能（peer）都包含它们——省略会让你的技能显得格格不入。

## 大小限制

- 描述（Description）：≤ 1024 个字符（强制要求）。
- 完整 SKILL.md 文件：≤ 100,000 个字符（强制要求，对应 `MAX_SKILL_CONTENT_CHARS`，约 36k 个 token）。
- 仓库中 `software-development/` 目录下的对等技能（peer skills）大小约为 **8-14k 个字符**。请尽量靠近该范围。如果超过 20k 字符，请拆分为 `references/*.md` 文件，并在 SKILL.md 中引用它们。

## 对等结构（Peer-Matched Structure）

仓库内所有技能大致遵循以下结构：

```
# <标题>

## 概述（Overview）
一至两段：做什么以及为什么。

## 何时使用（When to Use）
- 触发条件列表（带项目符号）
- “不要用于：”反触发条件

## <技能特有的主题章节>
- 常用快速参考表
- 包含精确命令的代码块
- Hermes 专属配方（通过 scripts/run_tests.sh 运行测试、ui-tui 路径等）

## 常见陷阱（Common Pitfalls）
常见错误及其修复方法的编号列表。

## 验证清单（Verification Checklist）
- [ ] 操作后验证的复选框列表

## 一次性配方（One-Shot Recipes，可选）
命名场景 → 具体命令序列。
```

并非每个章节都是强制性的，但 `概述` + `何时使用` + 可操作主体 + 陷阱是技能看起来像“对等技能”的最低要求。

## 目录放置

```
skills/<类别>/<技能名称>/SKILL.md
```

当前仓库中的类别（可通过 `ls skills/` 确认）：`autonomous-ai-agents`, `creative`, `data-science`, `devops`, `dogfood`, `email`, `gaming`, `github`, `leisure`, `mcp`, `media`, `mlops/*`, `note-taking`, `productivity`, `red-teaming`, `research`, `smart-home`, `social-media`, `software-development`。

选择最接近的现有类别。不要随意创建新的顶层类别。

## 工作流程

1. **调研目标类别中的对等技能（peer skills）：**
   ```
   ls skills/<类别>/
   ```
   阅读 2-3 个对等技能（peer skills）的 SKILL.md 文件，以匹配语气和结构。
2. **如有疑问，请检查验证器（validator）约束：** 查看 `tools/skill_manager_tool.py`。
3. **起草：** 使用 `write_file` 写入 `skills/<类别>/<名称>/SKILL.md`。
4. **本地验证：**
   ```python
   import yaml, re, pathlib
   content = pathlib.Path("skills/<类别>/<名称>/SKILL.md").read_text()
   assert content.startswith("---")
   m = re.search(r'\n---\s*\n', content[3:])
   fm = yaml.safe_load(content[3:m.start()+3])
   assert "name" in fm and "description" in fm
   assert len(fm["description"]) <= 1024
   assert len(content) <= 100_000
   ```
5. **Git add + commit** 到当前活跃分支。
6. **注意：** 当前会话的技能加载器是缓存的——`skill_view` / `skills_list` 在新会话开始之前不会看到新技能。这是预期行为，并非错误。

## 交叉引用其他技能

`metadata.hermes.related_skills` 在加载时会合并两个技能树（`skills/` 仓库内和 `~/.hermes/skills/` 用户本地）。你可以从仓库内技能引用用户本地技能，但其他新克隆仓库的用户将无法解析该引用。建议只从仓库内技能引用同样位于仓库内的技能。如果一个经常被引用的技能仅存在于 `~/.hermes/skills/` 中，考虑将其提升到仓库中。

## 编辑现有的仓库内技能

- **小修复（拼写错误、添加陷阱、调整触发条件）：** `skill_manage(action='patch', name=..., old_string=..., new_string=...)` 适用于仓库内技能。
- **重大重写：** 使用 `write_file` 重写整个 SKILL.md。`skill_manage(action='edit')` 也可以使用，但需要提供完整的更新内容。
- **添加辅助文件：** 使用 `write_file` 写入 `skills/<类别>/<名称>/references/<文件>.md`、`templates/<文件>` 或 `scripts/<文件>`。`skill_manage(action='write_file')` 也可以使用，并且会强制检查 references/templates/scripts/assets 子目录的白名单。
- **始终提交（commit）编辑内容——** 仓库内技能是源代码，而不是运行时状态。

## 常见陷阱

1. **为仓库内技能使用 `skill_manage(action='create')`。** 该操作会写入 `~/.hermes/skills/`，而不是仓库目录。创建仓库内技能请使用 `write_file`。

2. **`---` 前存在前导空白。** 验证器（validator）检查 `content.startswith("---")`；任何前导空行或 BOM 都会导致验证失败。

3. **描述（description）过于泛化。** 对等技能（peer）的描述都以“When ...”（当...时使用）开头，并描述*触发条件类别*，而非单一任务。“当调试 X 时使用”优于“调试 X”。

4. **忘记作者/许可证/metadata 块。** 虽然验证器（validator）不强制要求，但每个对等技能（peer）都包含；省略会让技能显得半成品。

5. **编写了一个与现有对等技能（peer）重复的技能。** 创建之前，先 `ls skills/<类别>/` 并打开 2-3 个对等技能。优先扩展已有技能，而不是创建过于相近的新技能。

6. **期望当前会话能看到新技能。** 不会。技能加载器在会话启动时初始化。请在新会话中验证，或通过 `skill_view` 使用精确路径查看。

7. **链接到仓库中不存在的技能。** `related_skills: [some-user-local-skill]` 对你有效，但其他克隆仓库的用户将无法解析。建议只链接仓库内的技能。

## 验证清单

- [ ] 文件位于 `skills/<类别>/<名称>/SKILL.md`（而非 `~/.hermes/skills/`）
- [ ] Frontmatter 从字节 0 开始，以 `---` 开头，以 `\n---\n` 结束
- [ ] `name`、`description`、`version`、`author`、`license`、`metadata.hermes.{tags, related_skills}` 均已存在
- [ ] 名称 ≤ 64 个字符，小写字母 + 连字符
- [ ] 描述（description）≤ 1024 个字符，并以“当 ... 时使用”开头
- [ ] 文件总字符数 ≤ 100,000（目标 8-15k）
- [ ] 结构：`# 标题` → `## 概述` → `## 何时使用` → 主体 → `## 常见陷阱` → `## 验证清单`
- [ ] `related_skills` 引用了仓库内存在的技能（或明确允许用户本地引用）
- [ ] 已完成 `git add skills/<类别>/<名称>/ && git commit` 到目标分支