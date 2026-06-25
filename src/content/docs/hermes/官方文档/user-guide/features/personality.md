---
sidebar_position: 9
title: "人格与 SOUL.md"
description: "通过全局 SOUL.md、内置人格（Personality）和自定义角色定义来定制 Hermes Agent 的人格"
---

# 人格（Personality）与 SOUL.md

Hermes Agent 的人格是完全可定制的。`SOUL.md` 是**主要身份（primary identity）**——它是系统提示（system prompt）中的第一个部分，定义了代理是谁。

- `SOUL.md` —— 一个持久的角色文件，位于 `HERMES_HOME` 中，作为代理的身份（系统提示中的 #1 插槽）
- 内置或自定义的 `/personality` 预设 —— 会话级别的系统提示覆盖层

如果你想要改变 Hermes 的身份，或者将其替换为完全不同的代理角色，请编辑 `SOUL.md`。

## SOUL.md 现时如何工作

Hermes 现在会在以下位置自动生成一个默认的 `SOUL.md`：

```text
~/.hermes/SOUL.md
```

更准确地说，它使用当前实例的 `HERMES_HOME`，因此如果你使用自定义主目录运行 Hermes，它将使用：

```text
$HERMES_HOME/SOUL.md
```

### 重要行为

- **SOUL.md 是代理的主要身份。** 它占据系统提示中的 #1 插槽，替换硬编码的默认身份。
- 如果 `SOUL.md` 尚不存在，Hermes 会自动创建一个起始版本
- 现有用户的 `SOUL.md` 文件永远不会被覆盖
- Hermes 仅从 `HERMES_HOME` 加载 `SOUL.md`
- Hermes 不会在当前工作目录中查找 `SOUL.md`
- 如果 `SOUL.md` 存在但为空，或无法加载，Hermes 会回退到内置的默认身份
- 如果 `SOUL.md` 有内容，该内容将在安全扫描和截断后原样注入
- SOUL.md **不会**在上下文文件（context files）部分重复出现——它只出现一次，作为身份

这使得 `SOUL.md` 成为真正的每个用户或每个实例的身份，而不仅仅是一个附加层。

## 为什么这样设计

这保持了人格的可预测性。

如果 Hermes 从你启动它的任意目录加载 `SOUL.md`，你的人格可能会在项目之间意外改变。通过仅从 `HERMES_HOME` 加载，人格属于 Hermes 实例本身。

这也使得教用户更容易：
- “编辑 `~/.hermes/SOUL.md` 来改变 Hermes 的默认人格。”

## 在哪里编辑

对于大多数用户：

```bash
~/.hermes/SOUL.md
```

如果你使用自定义主目录：

```bash
$HERMES_HOME/SOUL.md
```

## SOUL.md 中应该放什么？

用于持久的语气和人格指导，例如：
- 语调
- 沟通风格
- 直接程度
- 默认交互风格
- 风格上应避免什么
- Hermes 应如何处理不确定性、分歧或模糊性

较少用于：
- 一次性项目指令
- 文件路径
- 仓库约定
- 临时工作流细节

那些属于 `AGENTS.md`，而不是 `SOUL.md`。

## 好的 SOUL.md 内容

一个好的 SOUL 文件是：
- 跨上下文的稳定内容
- 足够广泛，可适用于许多对话
- 足够具体，能实际塑造语气
- 专注于沟通和身份，而不是特定任务的指令

### 示例

```markdown
# Personality

You are a pragmatic senior engineer with strong taste.
You optimize for truth, clarity, and usefulness over politeness theater.

## Style
- Be direct without being cold
- Prefer substance over filler
- Push back when something is a bad idea
- Admit uncertainty plainly
- Keep explanations compact unless depth is useful

## What to avoid
- Sycophancy
- Hype language
- Repeating the user's framing if it's wrong
- Overexplaining obvious things

## Technical posture
- Prefer simple systems over clever systems
- Care about operational reality, not idealized architecture
- Treat edge cases as part of the design, not cleanup
```

## Hermes 注入到提示中的内容

`SOUL.md` 的内容直接进入系统提示的 #1 插槽——代理身份位置。不会添加任何包装语言。

内容会经过：
- 提示注入（prompt-injection）扫描
- 如果内容过大则截断

如果文件为空、仅含空白字符或无法读取，Hermes 会回退到内置的默认身份（“You are Hermes Agent, an intelligent AI assistant created by Nous Research...”）。此回退也适用于设置了 `skip_context_files` 的情况（例如在子代理/委托上下文中）。

## 安全扫描

`SOUL.md` 与其它上下文文件一样，在纳入前会进行提示注入模式扫描。

这意味着你应该仍然保持它专注于角色/语气，而不是试图偷偷加入奇怪的元指令。

## SOUL.md 与 AGENTS.md 的对比

这是最重要的区别。

### SOUL.md
用于：
- 身份
- 语调
- 风格
- 沟通默认设置
- 人格层面的行为

### AGENTS.md
用于：
- 项目架构
- 编码约定
- 工具偏好
- 仓库特定工作流
- 命令、端口、路径、部署说明

一个有用的规则：
- 如果它应该跟随你到任何地方，则属于 `SOUL.md`
- 如果它属于一个项目，则属于 `AGENTS.md`

## SOUL.md 与 `/personality` 的对比

`SOUL.md` 是你的持久默认人格。

`/personality` 是一个会话级别的覆盖层，用于更改或补充当前系统提示。

所以：
- `SOUL.md` = 基线语气
- `/personality` = 临时模式切换

示例：
- 保持一个务实的默认 SOUL，然后使用 `/personality teacher` 进行辅导对话
- 保持一个简洁的 SOUL，然后使用 `/personality creative` 进行头脑风暴

## 内置人格（Built-in personalities）

Hermes 自带内置人格，你可以通过 `/personality` 切换。

| 名称 | 描述 |
|------|------|
| **helpful** | 友好、通用的助手 |
| **concise** | 简短、直击要点的回应 |
| **technical** | 详细、准确的技术专家 |
| **creative** | 创新、跳出框框的思维 |
| **teacher** | 耐心的教育者，带有清晰的示例 |
| **kawaii** | 可爱的表达、闪亮和热情 ★ |
| **catgirl** | 猫娘，带有猫的表情，nya~ |
| **pirate** | 赫尔墨斯船长，精通技术的海盗 |
| **shakespeare** | 吟游诗人的散文，富有戏剧性 |
| **surfer** | 超级放松的老兄氛围 |
| **noir** | 硬汉侦探的叙述 |
| **uwu** | 极度可爱，带有 uwu 语 |
| **philosopher** | 对每个查询进行深度沉思 |
| **hype** | 最高能量和热情！！！ |

## 用命令切换人格

### CLI

```text
/personality
/personality concise
/personality technical
```

### 消息平台

```text
/personality teacher
```

这些是方便的覆盖层，但你的全局 `SOUL.md` 仍然为 Hermes 提供其持久的默认人格，除非覆盖层实质性地改变了它。

## 配置文件中的自定义人格

你也可以在 `~/.hermes/config.yaml` 的 `agent.personalities` 下定义命名的自定义人格。

```yaml
agent:
  personalities:
    codereviewer: >
      You are a meticulous code reviewer. Identify bugs, security issues,
      performance concerns, and unclear design choices. Be precise and constructive.
```

然后通过以下命令切换：

```text
/personality codereviewer
```

## 推荐工作流

一个强大的默认设置是：

1. 在 `~/.hermes/SOUL.md` 中保留一个深思熟虑的全局 `SOUL.md`
2. 将项目指令放入 `AGENTS.md`
3. 仅在需要临时模式切换时使用 `/personality`

这将为你提供：
- 稳定的语气
- 项目特定行为放在它该在的地方
- 需要时临时控制

## 人格如何与完整提示交互

从高层次来看，提示堆栈包括：
1. **SOUL.md**（代理身份——如果 SOUL.md 不可用，则使用内置回退）
2. 工具感知的行为指导
3. 记忆/用户上下文
4. 技能指导
5. 上下文文件（`AGENTS.md`、`.cursorrules`）
6. 时间戳
7. 平台特定的格式化提示
8. 可选的系统提示覆盖层，如 `/personality`

`SOUL.md` 是基础——其他所有内容都构建在其之上。

## 相关文档

- [上下文文件](/user-guide/features/context-files)
- [配置](/user-guide/configuration)
- [技巧与最佳实践](/guides/tips)
- [SOUL.md 指南](/guides/use-soul-with-hermes)

## CLI 外观与对话人格

对话人格和 CLI 外观是分开的：

- `SOUL.md`、`agent.system_prompt` 和 `/personality` 影响 Hermes 的说话方式
- `display.skin` 和 `/skin` 影响 Hermes 在终端中的外观

关于终端外观，请参阅 [皮肤与主题](./skins.md)。