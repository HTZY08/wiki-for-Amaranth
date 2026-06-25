---
title: Training Unsloth
---

title: "Unsloth — Unsloth: 将 LoRA/QLoRA 微调速度提升 2-5 倍，降低显存消耗"
sidebar_label: "Unsloth"
description: "Unsloth: 将 LoRA/QLoRA 微调（fine-tuning）速度提升 2-5 倍，降低显存消耗"
---

--- body ---
{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Unsloth

Unsloth：将 LoRA/QLoRA 微调（fine-tuning）速度提升 2-5 倍，降低显存消耗。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/mlops/unsloth` 安装 |
| 路径 | `optional-skills/mlops/training/unsloth` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可 | MIT |
| 依赖 | `unsloth`, `torch`, `transformers`, `trl`, `datasets`, `peft` |
| 平台 | linux, macos |
| 标签 | `微调`, `Unsloth`, `快速训练`, `LoRA`, `QLoRA`, `内存高效`, `优化`, `Llama`, `Mistral`, `Gemma`, `Qwen` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时代理所看到的指令。
:::

# Unsloth 技能

基于官方文档，提供有关 unsloth 开发的全面协助。

## 何时使用此技能

此技能应在以下场景触发：
- 使用 unsloth 时
- 询问 unsloth 特性或 API 时
- 实现 unsloth 解决方案时
- 调试 unsloth 代码时
- 学习 unsloth 最佳实践时

## 快速参考

### 常见模式

*快速参考模式将在您使用此技能时逐步添加。*

## 参考文件

此技能包含 `references/` 目录下的完整文档：

- **llms-txt.md** — Llms-Txt 文档

当需要详细信息时，使用 `view` 读取具体的参考文件。

## 使用此技能

### 对于初学者
从getting_started或tutorials参考文件开始，了解基础概念。

### 对于特定功能
使用相应类别的参考文件（如api、guides等）获取详细信息。

### 对于代码示例
上面的快速参考部分包含了从官方文档中提取的常见模式。

## 资源

### references/
从官方来源提取的结构化文档。这些文件包含：
- 详细说明
- 带有语言注释的代码示例
- 原始文档的链接
- 快速导航的目录

### scripts/
在此处添加辅助脚本以执行常见自动化任务。

### assets/
在此处添加模板、样板代码或示例项目。

## 备注

- 此技能从官方文档自动生成
- 参考文件保留了源文档的结构和示例
- 代码示例包含语言检测以便更好地进行语法高亮
- 快速参考模式从文档中的常见用法示例中提取

## 更新

要使用更新后的文档刷新此技能：
1. 使用相同配置重新运行爬虫
2. 技能将使用最新信息重建

<!-- 触发重新上传 1763621536 -->