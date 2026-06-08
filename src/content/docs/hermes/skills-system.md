---
title: 技能系统
description: Skill 是什么、怎么用、怎么写
---

Skill（技能包）是 Hermes 的"操作说明书"——告诉 Agent 如何完成特定任务的标准化流程。

---

## 什么是 Skill

简单说，Skill 就是一份 Markdown 文件，里面写了：

- **这个技能是干什么的**（描述）
- **遇到什么情况应该用**（触发条件）
- **具体怎么做**（步骤）
- **容易踩什么坑**（注意事项）

比如有一个"查 arXiv 论文"的 Skill，当你问"帮我找一下最近关于 XXX 的论文"时，Agent 会加载这个 Skill，按照里面写的步骤去搜索、筛选、返回结果。

## Skill 存在哪

```
~/.hermes/profiles/default/skills/
├── devops/           ← 运维相关
│   ├── docker.md
│   └── proxy.md
├── research/         ← 研究相关
│   ├── arxiv.md
│   └── paper.md
└── creative/         ← 创意相关
    ├── image-gen.md
    └── ppt.md
```

按类别存放在不同文件夹里。

## 查看已有 Skill

```bash
# 列出所有可用 Skill
hermes skills list

# 查看某个 Skill 的详细内容
hermes skills view skill-name
```

## 编写自己的 Skill

当一个操作你做了 3 次以上，就值得写成 Skill。

### 基本格式

```markdown
---
name: my-skill
description: 一句话说明这个技能做什么
category: devops
---

## 触发条件

什么情况下加载这个 Skill（例如：用户问"怎么部署 XXX"）

## 步骤

1. 第一步做什么
2. 第二步做什么
3. ...

## 陷阱

- 容易出错的地方
- 需要特别注意的参数
```

### 创建命令

```bash
# 创建一个新 Skill
hermes skill create my-skill --category devops

# 编辑内容
nano ~/.hermes/profiles/default/skills/devops/my-skill.md
```

### 什么时候值得写 Skill

- ✅ 需要 5 步以上的重复操作
- ✅ 有特定的参数组合和注意事项
- ✅ 容易忘步骤的操作
- ❌ 一次性任务
- ❌ 过于简单（1-2 步）的操作

## Skill 实际案例

| Skill 名称 | 用途 | 包含内容 |
|-----------|------|---------|
| `github-pr-workflow` | 提 PR 的完整流程 | 分支、提交、推送、创建 PR、检查 CI |
| `daily-briefing` | 每日新闻简报 | 抓取 RSS、调用 AI 摘要、格式化输出 |
| `obsidian` | 操作 Obsidian 笔记 | 搜索、读写、创建双向链接 |
| `architectural-diagram` | 画架构图 | 选择合适的图表类型、生成 SVG |

## 更新和删除

```bash
# 更新 Skill 内容
hermes skill patch skill-name

# 删除
hermes skill delete skill-name
```

## 注意事项

- Skill 名称用小写字母和短横线（`my-skill` 而非 `My Skill`）
- 描述要准确，方便 Agent 自动匹配
- 发现 Skill 有遗漏就及时更新，不要等下次
