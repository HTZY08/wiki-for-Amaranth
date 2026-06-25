---
title: Learning Path
---

sidebar_position: 3
title: '学习路径'
description: '根据您的经验水平和目标，选择通过 Hermes Agent 文档的学习路径。'
---

--- body ---

# 学习路径

Hermes Agent 功能强大——可用作 CLI 助手、Telegram/Discord 机器人、任务自动化、强化学习（RL）训练等等。本页帮助您根据经验水平和目标确定从何处开始以及阅读哪些内容。

:::tip 从这里开始
如果您尚未安装 Hermes Agent，请先阅读[安装指南](/getting-started/installation)，然后运行[快速入门](/getting-started/quickstart)。以下内容假设您已成功安装。
:::

:::tip 首次设置提供商
首次用户几乎总是需要运行 `hermes setup --portal` ——一个 OAuth 涵盖了模型加上四个工具网关工具（搜索/图片/TTS/浏览器）。详见 [Nous Portal](/integrations/nous-portal)。
:::

## 如何使用本页

- **了解自己的水平？** 跳转到[按经验水平](#by-experience-level)表格，按照您所在级别的阅读顺序进行。
- **有特定目标？** 直接跳到[按用例](#by-use-case)找到匹配的场景。
- **随便看看？** 查看[关键功能概览](#key-features-at-a-glance)表格，快速了解 Hermes Agent 的所有功能。

## 按经验水平

| 经验水平 | 目标 | 推荐阅读 | 预计时间 |
|---|---|---|---|
| **新手** | 启动并运行，进行基本对话，使用内置工具 | [安装](/getting-started/installation) → [快速入门](/getting-started/quickstart) → [CLI 使用](/user-guide/cli) → [配置](/user-guide/configuration) | 约1小时 |
| **中级** | 设置消息机器人，使用高级功能如记忆（Memory）、定时任务（Cron）和技能（Skill） | [会话](/user-guide/sessions) → [消息](/user-guide/messaging) → [工具](/user-guide/features/tools) → [技能](/user-guide/features/skills) → [记忆](/user-guide/features/memory) → [Cron](/user-guide/features/cron) | 约2–3小时 |
| **高级** | 构建自定义工具、创建技能、使用强化学习（RL）训练模型、为项目做贡献 | [架构](/developer-guide/architecture) → [添加工具](/developer-guide/adding-tools) → [创建技能](/developer-guide/creating-skills) → [贡献](/developer-guide/contributing) | 约4–6小时 |

## 按用例

选择与您想要做的事情相匹配的场景。每个场景都按您应阅读的顺序链接到相关文档。

### "我希望有一个 CLI 编码助手"

使用 Hermes Agent 作为交互式终端助手，用于编写、审查和运行代码。

1. [安装](/getting-started/installation)
2. [快速入门](/getting-started/quickstart)
3. [CLI 使用](/user-guide/cli)
4. [代码执行](/user-guide/features/code-execution)
5. [上下文文件](/user-guide/features/context-files)
6. [技巧与窍门](/guides/tips)

:::tip
使用上下文文件（Context Files）直接将文件传入对话。Hermes Agent 可以读取、编辑和运行您项目中的代码。
:::

### "我希望有一个 Telegram/Discord 机器人"

将 Hermes Agent 部署为您喜欢的消息平台上的机器人。

1. [安装](/getting-started/installation)
2. [配置](/user-guide/configuration)
3. [消息概述](/user-guide/messaging)
4. [Telegram 设置](/user-guide/messaging/telegram)
5. [Discord 设置](/user-guide/messaging/discord)
6. [语音模式](/user-guide/features/voice-mode)
7. [将语音模式与 Hermes 结合使用](/guides/use-voice-mode-with-hermes)
8. [安全](/user-guide/security)

完整项目示例请参阅：
- [每日简报机器人](/guides/daily-briefing-bot)
- [团队 Telegram 助手](/guides/team-telegram-assistant)

### "我希望自动化任务"

安排定期重复的任务、运行批量作业或串连代理（Agent）操作。

1. [快速入门](/getting-started/quickstart)
2. [Cron 定时任务](/user-guide/features/cron)
3. [批量处理](/user-guide/features/batch-processing)
4. [委托](/user-guide/features/delegation)
5. [钩子](/user-guide/features/hooks)

:::tip
Cron 任务让 Hermes Agent 按计划运行任务——每日摘要、定期检查、自动报告——无需您在场。
:::

### "我希望构建自定义工具/技能"

使用您自己的工具和可复用的技能包扩展 Hermes Agent。

1. [插件](/user-guide/features/plugins)
2. [构建 Hermes 插件](/guides/build-a-hermes-plugin)
3. [工具概述](/user-guide/features/tools)
4. [技能概述](/user-guide/features/skills)
5. [MCP（Model Context Protocol）](/user-guide/features/mcp)
6. [架构](/developer-guide/architecture)
7. [添加工具](/developer-guide/adding-tools)
8. [创建技能](/developer-guide/creating-skills)

:::tip
对于大多数自定义工具创建，从插件开始。[添加工具](/developer-guide/adding-tools)页面适用于内置 Hermes 核心开发，而非通常的用户/自定义工具路径。
:::

### "我希望训练模型"

使用强化学习（RL）通过 Hermes Agent 的 RL 训练管线（由 [Atropos](https://github.com/NousResearch/atropos) 驱动）来微调模型行为。

1. [快速入门](/getting-started/quickstart)
2. [配置](/user-guide/configuration)
3. [Atropos RL 环境](https://github.com/NousResearch/atropos) (外部)
4. [提供商路由](/user-guide/features/provider-routing)
5. [架构](/developer-guide/architecture)

:::tip
当您已经了解 Hermes Agent 处理对话和工具调用的基础知识时，RL 训练效果最佳。如果您是新手，请先完成新手路径。
:::

### "我希望将其作为 Python 库使用"

以编程方式将 Hermes Agent 集成到您自己的 Python 应用程序中。

1. [安装](/getting-started/installation)
2. [快速入门](/getting-started/quickstart)
3. [Python 库指南](/guides/python-library)
4. [架构](/developer-guide/architecture)
5. [工具](/user-guide/features/tools)
6. [会话](/user-guide/sessions)

## 关键功能概览

不确定有哪些可用功能？以下是主要功能的快速目录：

| 功能 | 作用 | 链接 |
|---|---|---|
| **工具（Tool）** | 代理（Agent）可调用的内置工具（文件 I/O、搜索、Shell 等） | [工具](/user-guide/features/tools) |
| **技能（Skill）** | 可安装的插件包，添加新功能 | [技能](/user-guide/features/skills) |
| **记忆（Memory）** | 跨会话的持久记忆 | [记忆](/user-guide/features/memory) |
| **上下文文件（Context File）** | 将文件和目录输入对话 | [上下文文件](/user-guide/features/context-files) |
| **MCP（Model Context Protocol）** | 通过 Model Context Protocol 连接到外部工具服务器 | [MCP](/user-guide/features/mcp) |
| **Cron（定时任务）** | 安排定期代理任务 | [Cron](/user-guide/features/cron) |
| **委托（Delegation）** | 生成子代理进行并行工作 | [委托](/user-guide/features/delegation) |
| **代码执行（Code Execution）** | 运行通过编程调用 Hermes 工具的 Python 脚本 | [代码执行](/user-guide/features/code-execution) |
| **浏览器（Browser）** | 网页浏览和抓取 | [浏览器](/user-guide/features/browser) |
| **钩子（Hook）** | 事件驱动的回调和中间件 | [钩子](/user-guide/features/hooks) |
| **批量处理（Batch Processing）** | 批量处理多个输入 | [批量处理](/user-guide/features/batch-processing) |
| **提供商路由（Provider Routing）** | 跨多个 LLM 提供商路由请求 | [提供商路由](/user-guide/features/provider-routing) |

## 接下来阅读什么

根据您当前的位置：

- **刚刚完成安装？** → 前往[快速入门](/getting-started/quickstart)运行您的第一次对话。
- **完成了快速入门？** → 阅读 [CLI 使用](/user-guide/cli)和[配置](/user-guide/configuration)以自定义您的设置。
- **熟悉基础知识？** → 探索[工具](/user-guide/features/tools)、[技能](/user-guide/features/skills)和[记忆](/user-guide/features/memory)以解锁代理的全部功能。
- **为团队设置？** → 阅读[安全](/user-guide/security)和[会话](/user-guide/sessions)以了解访问控制和对话管理。
- **准备好构建？** → 跳转到[开发者指南](/developer-guide/architecture)了解内部结构并开始贡献。
- **想要实际示例？** → 查看[指南](/guides/tips)部分，了解实际项目和技巧。

:::tip
您无需阅读所有内容。选择与您目标匹配的路径，按顺序跟随链接，您将迅速提高效率。您可以随时回到此页面找到您的下一步。
:::