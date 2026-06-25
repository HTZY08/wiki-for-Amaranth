---
title: "代码库检查 — 使用 pygount 检查代码库：LOC、语言、比率"
sidebar_label: "代码库检查"
description: "使用 pygount 检查代码库：LOC、语言、比率"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非本页面。 */}

# 代码库检查（Codebase Inspection）

使用 pygount 检查代码库：代码行（LOC）、语言、比率。

## 技能元数据（Skill metadata）

|                    |                                                              |
| ------------------ | ------------------------------------------------------------ |
| 来源（Source）     | 内置（默认安装）                                             |
| 路径（Path）       | `skills/github/codebase-inspection`                          |
| 版本（Version）    | `1.0.0`                                                      |
| 作者（Author）     | Hermes 代理（Agent）                                         |
| 许可证（License）  | MIT                                                          |
| 平台（Platforms）  | linux, macos, windows                                        |
| 标签（Tags）       | `LOC`, `代码分析`, `pygount`, `代码库`, `指标`, `仓库`       |
| 相关技能（Related） | [`github-repo-management`](/docs/user-guide/skills/bundled/github/github-github-repo-management) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发该技能时加载的完整技能定义。这是技能激活时代理所看到的指令。
:::

# 使用 pygount 进行代码库检查（Codebase Inspection with pygount）

使用 `pygount` 分析仓库的代码行数、语言分布、文件数量以及代码与注释比例。

## 何时使用（When to Use）

- 用户询问代码行（LOC）数量
- 用户想要仓库的语言分布
- 用户询问代码库大小或组成
- 用户想要代码与注释的比例
- 一般性的“这个仓库有多大”问题

## 前置条件（Prerequisites）

```bash
pip install --break-system-packages pygount 2>/dev/null || pip install pygount
```

## 1. 基本摘要（最常用）

获取包含文件数量、代码行和注释行的完整语言分布：

```bash
cd /path/to/repo
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,.eggs,*.egg-info" \
  .
```

**重要提示：** 务必使用 `--folders-to-skip` 排除依赖/构建目录，否则 pygount 将遍历它们，耗时极长甚至卡死。

## 2. 常见文件夹排除项

根据项目类型调整：

```bash
# Python 项目
--folders-to-skip=".git,venv,.venv,__pycache__,.cache,dist,build,.tox,.eggs,.mypy_cache"

# JavaScript/TypeScript 项目
--folders-to-skip=".git,node_modules,dist,build,.next,.cache,.turbo,coverage"

# 通用排除项
--folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,vendor,third_party"
```

## 3. 按特定语言过滤（Filter by Specific Language）

```bash
# 仅统计 Python 文件
pygount --suffix=py --format=summary .

# 仅统计 Python 和 YAML
pygount --suffix=py,yaml,yml --format=summary .
```

## 4. 逐文件详细输出

```bash
# 默认格式显示每个文件的分解
pygount --folders-to-skip=".git,node_modules,venv" .

# 按代码行排序（通过 sort 管道）
pygount --folders-to-skip=".git,node_modules,venv" . | sort -t$'\t' -k1 -nr | head -20
```

## 5. 输出格式（Output Formats）

```bash
# 汇总表（默认推荐）
pygount --format=summary .

# 用于编程处理的 JSON 输出
pygount --format=json .

# 管道友好：语言、文件数、代码、文档、空行、字符串
pygount --format=summary . 2>/dev/null
```

## 6. 解读结果（Interpreting Results）

汇总表的列含义：
- **语言（Language）** — 检测到的编程语言
- **文件（Files）** — 该语言的文件数量
- **代码（Code）** — 实际代码行数（可执行/声明性）
- **注释（Comment）** — 注释或文档行数
- **%（%）** — 占总数的百分比

特殊伪语言：
- `__empty__` — 空文件
- `__binary__` — 二进制文件（图片、编译产物等）
- `__generated__` — 自动生成的文件（通过启发式检测）
- `__duplicate__` — 内容完全相同的文件
- `__unknown__` — 无法识别的文件类型

## 常见陷阱（Pitfalls）

1. **务必排除 .git、node_modules、venv** — 不指定 `--folders-to-skip` 时，pygount 会遍历所有内容，可能耗时数分钟或在大型依赖树上卡死。
2. **Markdown 显示 0 代码行** — pygount 将所有 Markdown 内容归类为注释，而非代码。这是预期行为。
3. **JSON 文件代码行数偏低** — pygount 可能保守地统计 JSON 行数。若要精确统计 JSON 行数，请直接使用 `wc -l`。
4. **大型单体仓库** — 对于非常大的仓库，建议使用 `--suffix` 来针对特定语言，而非扫描所有内容。