--- frontmatter ---
---
sidebar_position: 7
title: "使用 SOUL.md 与 Hermes"
description: "如何使用 SOUL.md 塑造 Hermes Agent 的默认语气，其中应包含的内容，以及它与 AGENTS.md 和 /personality 的区别"
---

--- body ---
# 使用 SOUL.md 与 Hermes

`SOUL.md` 是 Hermes 实例的**主要身份（primary identity）**。它是系统提示（system prompt）中的第一项——定义了代理（Agent）是谁、如何说话、以及避免什么。

如果你希望每次与 Hermes 交谈时都感觉是同一个助手——或者想用你自己的个性完全替换 Hermes 的默认角色——这就是你应该使用的文件。

## SOUL.md 的用途

使用 `SOUL.md` 来定义：
- 语气（tone）
- 个性（personality）
- 沟通风格（communication style）
- Hermes 应该有多直接或多温暖
- Hermes 在风格上应避免什么
- Hermes 应如何对待不确定性、分歧和模糊性

简而言之：
- `SOUL.md` 是关于 Hermes 是谁以及 Hermes 如何说话

## SOUL.md 不适用于什么

不要用它来存放：
- 仓库特定的编码规范（coding conventions）
- 文件路径
- 命令
- 服务端口
- 架构说明
- 项目工作流指令

这些属于 `AGENTS.md`。

一个好的原则：
- 如果它应该适用于所有地方，就放在 `SOUL.md` 中
- 如果它只属于一个项目，就放在 `AGENTS.md` 中

## 文件位置

Hermes 现在仅使用当前实例的全局 SOUL 文件：

```text
~/.hermes/SOUL.md
```

如果你使用自定义主目录运行 Hermes，则变为：

```text
$HERMES_HOME/SOUL.md
```

## 首次运行行为

如果 `SOUL.md` 尚不存在，Hermes 会自动为你生成一个初始版本。

这意味着大多数用户现在从一开始就有一个真实文件，可以立即阅读和编辑。

重要说明：
- 如果你已有 `SOUL.md`，Hermes 不会覆盖它
- 如果文件存在但为空，Hermes 不会添加任何内容到提示中

## Hermes 如何使用它

当 Hermes 启动会话时，它会从 `HERMES_HOME` 读取 `SOUL.md`，扫描其中是否包含提示注入（prompt-injection）模式，必要时截断，并将其作为**代理身份（agent identity）**——系统提示中的第一个槽位。这意味着 SOUL.md 完全替换了内置的默认身份文本。

如果 `SOUL.md` 缺失、为空或无法加载，Hermes 会回退到内置的默认身份。

文件周围不会添加任何包装语言。内容本身至关重要——用你希望代理思考和说话的方式书写。

## 一个好的首次编辑

如果你不做其他事，至少打开文件并更改几行，让它感觉像你。

例如：

```markdown
You are direct, calm, and technically precise.
Prefer substance over politeness theater.
Push back clearly when an idea is weak.
Keep answers compact unless deeper detail is useful.
```

仅此一项就能显著改变 Hermes 的感觉。

## 示例风格

### 1. 务实工程师

```markdown
You are a pragmatic senior engineer.
You care more about correctness and operational reality than sounding impressive.

## Style
- Be direct
- Be concise unless complexity requires depth
- Say when something is a bad idea
- Prefer practical tradeoffs over idealized abstractions

## Avoid
- Sycophancy
- Hype language
- Overexplaining obvious things
```

### 2. 研究伙伴

```markdown
You are a thoughtful research collaborator.
You are curious, honest about uncertainty, and excited by unusual ideas.

## Style
- Explore possibilities without pretending certainty
- Distinguish speculation from evidence
- Ask clarifying questions when the idea space is underspecified
- Prefer conceptual depth over shallow completeness
```

### 3. 教师/解释者

```markdown
You are a patient technical teacher.
You care about understanding, not performance.

## Style
- Explain clearly
- Use examples when they help
- Do not assume prior knowledge unless the user signals it
- Build from intuition to details
```

### 4. 严格评审者

```markdown
You are a rigorous reviewer.
You are fair, but you do not soften important criticism.

## Style
- Point out weak assumptions directly
- Prioritize correctness over harmony
- Be explicit about risks and tradeoffs
- Prefer blunt clarity to vague diplomacy
```

## 什么构成一份有力的 SOUL.md？

一份有力的 `SOUL.md` 应该是：
- 稳定的（stable）
- 广泛适用的（broadly applicable）
- 语气具体（specific in voice）
- 不包含过多临时指令（not overloaded with temporary instructions）

一份薄弱的 `SOUL.md` 则是：
- 充满项目细节
- 自相矛盾
- 试图微观管理每一个回答形态
- 大多数是通用套话，比如“要乐于助人”和“要清晰”

Hermes 已经努力做到乐于助人和清晰。`SOUL.md` 应该添加真实的个性和风格，而不是重申显而易见的默认设置。

## 建议的结构

不一定需要标题，但有帮助。

一个效果不错的简单结构：

```markdown
# Identity
Who Hermes is.

# Style
How Hermes should sound.

# Avoid
What Hermes should not do.

# Defaults
How Hermes should behave when ambiguity appears.
```

## SOUL.md vs /personality

它们是互补的。

用 `SOUL.md` 设定你的持久基线（durable baseline）。
用 `/personality` 进行临时模式切换（temporary mode switches）。

示例：
- 你的默认 SOUL 是务实且直接的
- 然后在一个会话中使用 `/personality teacher`
- 之后切换回来而不更改你的基础声音文件

## SOUL.md vs AGENTS.md

这是最常见的错误。

### 把以下内容放在 SOUL.md 中
- “要直接。”
- “避免夸张的语言。”
- “除非需要深度，否则优先简洁回答。”
- “当用户错误时，要反驳。”

### 把以下内容放在 AGENTS.md 中
- “使用 pytest，不要使用 unittest。”
- “前端位于 `frontend/` 目录。”
- “永远不要直接编辑迁移文件。”
- “API 运行在 8000 端口。”

## 如何编辑它

```bash
nano ~/.hermes/SOUL.md
```

或

```bash
vim ~/.hermes/SOUL.md
```

然后重启 Hermes 或开始一个新的会话。

## 实用工作流程

1. 从自动生成的默认文件开始
2. 修剪任何不符合你期望语气的内容
3. 添加 4–8 行明确定义语气和默认行为
4. 与 Hermes 交谈一段时间
5. 根据仍然感觉不对的地方进行调整

这种迭代方法比试图一次性设计完美个性更有效。

## 故障排除

### 我编辑了 SOUL.md 但 Hermes 听起来仍然一样

检查：
- 你编辑的是 `~/.hermes/SOUL.md` 或 `$HERMES_HOME/SOUL.md`
- 而不是某个仓库本地的 `SOUL.md`
- 文件不为空
- 编辑后会话已重启
- 没有 `/personality` 覆盖层主导结果

### Hermes 忽略了 SOUL.md 的部分内容

可能的原因：
- 更高优先级的指令覆盖了它
- 文件包含冲突的指导
- 文件太长被截断
- 某些文本类似于提示注入内容，可能被扫描器阻止或修改

### 我的 SOUL.md 变得过于项目特定

将项目指令移到 `AGENTS.md` 中，并保持 `SOUL.md` 聚焦于身份和风格。

## 相关文档

- [个性与 SOUL.md](/user-guide/features/personality)
- [上下文文件](/user-guide/features/context-files)
- [配置](/user-guide/configuration)
- [技巧与最佳实践](/guides/tips)