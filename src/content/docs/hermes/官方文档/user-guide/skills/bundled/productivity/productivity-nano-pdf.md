---
title: Nano Pdf
---

title: "Nano Pdf — 通过 nano-pdf CLI（自然语言提示）编辑 PDF 文本/错别字/标题"
sidebar_label: "Nano Pdf"
description: "通过 nano-pdf CLI（自然语言提示）编辑 PDF 文本/错别字/标题"
---

--- body ---
--- body ---
{/* 此页面由网站/脚本/generate-skill-docs.py 根据技能目录下的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Nano Pdf

通过 nano-pdf CLI（自然语言提示）编辑 PDF 文本/错别字/标题。

## 技能（Skill）元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/productivity/nano-pdf` |
| 版本 | `1.0.0` |
| 作者 | 社区 |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `PDF`, `文档`, `编辑`, `自然语言处理`, `效率` |

## 参考：完整 SKILL.md

:::info
以下为 Hermes 在触发此技能时加载的完整技能定义。即技能激活时代理所看到的指令。
:::

# nano-pdf

使用自然语言指令编辑 PDF。指向某一页，描述需要修改的内容。

## 前置条件

```bash
# 使用 uv 安装（推荐 — 在 Hermes 中已可用）
uv pip install nano-pdf

# 或使用 pip
pip install nano-pdf
```

## 使用方法

```bash
nano-pdf edit <文件.pdf> <页码> "<指令>"
```

## 示例

```bash
# 修改第一页的标题
nano-pdf edit deck.pdf 1 "将标题改为 'Q3 结果' 并修复副标题中的错别字"

# 更新某一页的日期
nano-pdf edit report.pdf 3 "将日期从 1 月更新为 2026 年 2 月"

# 修正内容
nano-pdf edit contract.pdf 2 "将客户名称从 'Acme Corp' 改为 'Acme Industries'"
```

## 注意事项

- 页码基于 0 或 1 取决于版本 — 若编辑到了错误页面，请尝试 ±1 重试
- 编辑后务必验证输出 PDF（使用 `read_file` 检查文件大小，或直接打开查看）
- 该工具底层使用大语言模型 — 需要 API 密钥（查看 `nano-pdf --help` 了解配置）
- 适用于文本修改；复杂的布局调整可能需要其他方法