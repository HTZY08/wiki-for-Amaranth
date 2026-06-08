---
title: 技能系统
description: Hermes Skill 体系——自定义、加载与管理
---

Skill 是 Hermes Agent 的"肌肉记忆"——把解决特定问题的流程、命令、参数和注意事项打包成一个可复用的知识包。

## 什么是 Skill

每个 Skill 是一份 `SKILL.md` 文件，包含：

```
---
name: skill-name
description: 一句话描述
category: devops / research / creative / ...
---

## 触发条件
什么场景下加载这个 Skill

## 步骤
按顺序的执行步骤

## 陷阱
常踩的坑
```

## 目录结构

```
~/.hermes/profiles/default/skills/
├── devops/
│   ├── docker-deploy.md
│   └── proxy-setup.md
├── research/
│   ├── arxiv-search.md
│   └── paper-analysis.md
└── creative/
    ├── excalidraw.md
    └── ppt-master.md
```

## 加载与使用

在对话中，Agent 会自动扫描技能列表并加载匹配的 Skill。也可以手动指定：

```bash
skill_view(name='docker-deploy')
```

## 编写自己的 Skill

当遇到以下情况时值得写成 Skill：

- 需要 5 步以上的重复操作
- 有特定的陷阱和注意事项
- 工具调用链有固定模式

编写命令：

```bash
hermes skill create my-skill --category devops
```

## 常用 Skill 举例

| Skill | 用途 |
|-------|------|
| `github-pr-workflow` | PR 生命周期管理 |
| `systematic-debugging` | 4 阶段根因调试法 |
| `siliconflow-image-gen` | 硅基流动 AI 生图 |
| `obsidian` | Obsidian 笔记库操作 |
| `daily-briefing` | 每日三合一简报 |

更新 Skill 直接用 `skill_manage(action='patch')`——发现遗漏就补，不等到下次。
