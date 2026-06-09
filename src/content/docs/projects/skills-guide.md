---
title: Skill 详解
description: 技能系统的结构、写法与使用方式
---

---

## 什么是 Skill

Skill 是 Hermes 的 **procedural memory**——不是给人类读的文档，是给 AI 读的操作手册。

```
普通文档：告诉人类"怎么做某事"
Skill：    告诉 AI"怎么做某事，且遇到什么问题该怎么修"
```

每次对话开始时，Hermes 会扫描所有匹配的 skill，把内容注入到 AI 的系统提示中。所以 skill 写得越清楚，AI 的行为就越准确。

---

## 结构

每个 skill 是一个 `.md` 文件，放在 `/opt/data/skills/<分类>/<技能名>/SKILL.md`。

### 文件头（YAML frontmatter）

```yaml
---
name: skill-name
description: "一句话说明这个技能做什么"
category: devops
---
```

### 正文（Markdown）

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

踩过的坑。这是 skill 最有价值的部分——"如果你遇到了 X，试试 Y"。

## Verification

怎么确认操作成功了。
```

---

## 当前技能体系

共有 **120+** 个技能，按分类存放：

| 分类 | 数量 | 举例 |
|------|------|------|
| `devops` | ~30 | 微信网关、Docker、代理、GPU、CI/CD |
| `software-development` | ~15 | TDD、代码审查、调试 |
| `mlops` | ~15 | 模型部署、生图、量化 |
| `research` | ~20 | 文献搜索、数据分析、论文写作 |
| `productivity` | ~10 | PPT 生成、文档处理 |
| `creative` | ~10 | ASCII 艺术、角色设计 |
| `social-media` | ~5 | 微信、Twitter |
| `meta` | ~3 | 写作风格、角色设定 |

---

## 怎么写一个好 Skill

### 原则

1. **触发条件明确** — 第一条就写清楚"什么时候用这个 skill"
2. **命令可复制** — 贴实际的命令，不是"你可以这样做"
3. **pitfalls 是精华** — 踩过的坑比步骤更有价值
4. **验证步骤** — 最后一定要写"怎么知道搞定了"
5. **开箱即用** — AI 读完之后应该能直接执行

### 模板

````markdown
---
name: my-skill
description: "做什么用的"
---

# My Skill

## 触发条件
用户提到/需要做 XXX 时加载此技能。

## 核心命令

```bash
# 核心操作
命令1
命令2
```

## 详细步骤

1. 第一步
2. 第二步
3. 第三步

## 常见问题

### 问题1：XXX 报错
原因：XXX
解决：YYY

## 验证

执行后如何确认成功。
````

---

## Skill 的维护

- **发现过时了** → 直接改，不要等
- **发现漏了步骤** → 补上，写下这次怎么发现的
- **踩了新坑** → 加到 Pitfalls 节
- **合并重复技能** → 内容合并到 umbrella skill，删掉被合并的

Skill 不维护就是废纸。每次用它发现问题，顺手更新。

---

## 并不神秘

Skill 就是笔记。区别是普通笔记写给人类看，skill 写给 AI 看。内容是一样的——怎么做事、踩过什么坑、怎么确认做对了。
