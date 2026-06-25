---
title: Obsidian
---

title: "Obsidian — 在 Obsidian 仓库中阅读、搜索、创建和编辑笔记"
sidebar_label: "Obsidian"
description: "在 Obsidian 仓库中阅读、搜索、创建和编辑笔记"
---

--- body ---
{/* 此页面由网站/脚本/生成技能文档.py 根据技能的 SKILL.md 自动生成。请编辑源 SKILL.md 而非此页面。 */}

# Obsidian

在 Obsidian 仓库中阅读、搜索、创建和编辑笔记。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/note-taking/obsidian` |
| 平台 | linux, macos, windows |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。即技能激活时代理所看到的指令。
:::

# Obsidian 仓库

使用此技能进行基于文件系统的 Obsidian 仓库操作：阅读笔记、列出笔记、搜索笔记文件、创建笔记、追加内容以及添加维基链接（wikilinks）。

## 仓库路径

在调用文件工具之前，请使用已知或已解析的仓库路径。

记录的仓库路径约定是 `OBSIDIAN_VAULT_PATH` 环境变量，例如来自 `${HERMES_HOME:-~/.hermes}/.env`。如果未设置，则使用 `~/Documents/Obsidian Vault`。

文件工具不会展开 shell 变量。不要将包含 `$OBSIDIAN_VAULT_PATH` 的路径传递给 `read_file`、`write_file`、`patch` 或 `search_files`；请先解析仓库路径，然后传递具体的绝对路径。仓库路径可能包含空格，这也是优先使用文件工具而非 shell 命令的另一个原因。

如果仓库路径未知，可以使用 `terminal` 来解析 `OBSIDIAN_VAULT_PATH` 或检查回退路径是否存在。一旦路径已知，切换回文件工具。

## 阅读笔记

使用 `read_file` 并传入已解析的笔记绝对路径。优先使用此方法而非 `cat`，因为它提供行号和分页功能。

## 列出笔记

使用 `search_files` 并设置 `target: "files"` 和已解析的仓库路径。优先使用此方法而非 `find` 或 `ls`。

- 要列出所有 Markdown 笔记，请在仓库路径下使用 `pattern: "*.md"`。
- 要列出子文件夹，请在该子文件夹的绝对路径下搜索。

## 搜索

使用 `search_files` 进行文件名和内容搜索。优先使用此方法而非 `grep`、`find` 或 `ls`。

- 对于文件名搜索，使用 `search_files` 并设置 `target: "files"` 和文件名 `pattern`。
- 对于笔记内容搜索，使用 `search_files` 并设置 `target: "content"`，内容正则表达式作为 `pattern`，并在需要限制匹配 Markdown 笔记时设置 `file_glob: "*.md"`。

## 创建笔记

使用 `write_file` 并传入已解析的绝对路径和完整的 Markdown 内容。优先使用此方法而非 shell 的 heredoc 或 `echo`，因为它可以避免 shell 引用问题并返回结构化结果。

## 追加到笔记

当操作不复杂时，优先使用原生的文件工具工作流：

- 使用 `read_file` 读取目标笔记。
- 当有稳定上下文时（例如在现有标题后添加章节或在已知尾部块前追加），使用 `patch` 进行锚定追加。
- 当重写整个笔记比构建脆弱的 patch 更清晰时，使用 `write_file`。

对于使用 `patch` 的锚定追加，将锚点替换为锚点加上新内容。

对于无稳定上下文的简单追加，如果这是最清晰且安全的选择，则可以使用 `terminal`。

## 定向编辑

当当前内容提供稳定上下文时，使用 `patch` 进行有针对性的笔记更改。优先使用此方法而非 shell 文本重写。

## 维基链接

Obsidian 使用 `[[笔记名称]]` 语法链接笔记。在创建笔记时，使用此语法链接相关内容。