---
title: 技能系统（Skill）
description: Skill 是什么、怎么写、怎么管理——给 Agent 的操作手册体系
---

## 什么是 Skill

Skill 是 Hermes 的 procedural memory——不是给人类读的文档，是给 AI 读的操作手册。

```
普通文档：告诉人类"怎么做某事"
Skill：    告诉 AI"怎么做某事，且遇到什么问题该怎么修"
```

每次对话开始时，Hermes 扫描匹配的 skill 注入到系统提示中。skill 写得越清楚，AI 行为越准确。

## 结构

每个 skill 是一个 `.md` 文件，放在 `~/.hermes/skills/<分类>/<技能名>/SKILL.md`。

### 文件头（YAML frontmatter）

```yaml
---
name: skill-name
description: 一句话说明这个技能做什么
category: devops
---
```

### 正文结构

正文是给 AI 读的指令。好 skill 的写法：

```
# 技能名

## 核心模式

这个技能要解决什么问题、用什么方法。

## Quick Reference

最常用的命令/代码片段，放在最前面。

## Step by Step

详细的执行步骤，每一步写清楚做什么。

## Pitfalls

踩过的坑——"如果你遇到了 X，试试 Y"。

## Verification

怎么确认操作成功了。
```

## 怎么写一个好 Skill

### 原则

1. **触发条件明确** — 第一条就写清楚"什么时候用这个 skill"
2. **命令可复制** — 贴实际的命令，不是"你可以这样做"
3. **pitfalls 是精华** — 踩过的坑比步骤更有价值
4. **验证步骤** — 最后一定要写"怎么知道搞定了"
5. **开箱即用** — AI 读完之后应该能直接执行

### 什么时候值得写

- ✅ 需要 5 步以上的重复操作
- ✅ 有特定的参数组合和注意事项
- ✅ 容易忘步骤的操作
- ❌ 一次性任务
- ❌ 过于简单（1-2 步）的操作

## 管理命令

```bash
# 列出所有可用 Skill
hermes skills list

# 查看某个 Skill 的详细内容
hermes skills view skill-name

# 创建一个新 Skill
hermes skill create my-skill --category devops
```

## 当前技能体系

共有 120+ 个技能，按分类存放：

| 分类 | 数量 | 举例 |
|------|------|------|
| devops | ~30 | 微信网关、Docker、代理、GPU、CI/CD |
| software-development | ~15 | TDD、代码审查、调试 |
| mlops | ~15 | 模型部署、生图、量化 |
| research | ~20 | 文献搜索、数据分析、论文写作 |
| productivity | ~10 | PPT 生成、文档处理 |
| creative | ~10 | ASCII 艺术、角色设计 |
| social-media | ~5 | 微信、Twitter |
| meta | ~3 | 写作风格、角色设定 |
