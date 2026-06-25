---
title: Automation Blueprints Catalog
---

sidebar_position: 7
title: "自动化蓝图目录（Automation Blueprints Catalog）"
description: "即开即用的自动化蓝图（Blueprint）——通过仪表板、CLI、TUI、任意即时通讯软件或桌面应用即可设置。"
---

--- body ---
import AutomationBlueprintsCatalog from '@site/src/components/AutomationBlueprintsCatalog';

# 自动化蓝图（Automation Blueprints）

自动化蓝图（Automation Blueprints）是即开即用的自动化流程。选择一个蓝图，填写几个字段，Hermes 就会将其作为 cron 任务调度——无需编写 cron 语法。

每个蓝图均可在**所有界面**中使用：

- **仪表板 / 桌面应用**——打开 Cron 页面，切换到 **Blueprints** 标签页，填写表单，然后点击 *Schedule it*。
- **CLI、TUI 和即时通讯软件**——输入 `/blueprint <name>`（例如 `/blueprint morning-brief`），Hermes 会逐一提问所需信息，然后调度任务。名称匹配是宽松的——支持前缀或近似拼写。高级用户可以通过内联传递值来跳过提问：`/blueprint morning-brief time=08:00`。
- **桌面应用**——在任何蓝图上点击 **Send to App**，即可在编辑器（composer）中预加载该命令打开。

蓝图绝不会静默调度任务——在任务创建前你始终需要确认。随时通过 `/cron` 管理已创建的任务。

<AutomationBlueprintsCatalog />

## 编写你自己的蓝图

蓝图只是一个技能，在其 `SKILL.md` 的 frontmatter 中包含 `metadata.hermes.blueprint` 块。插槽模式（slot schema）及如何发布蓝图，请参阅[创建技能 → 自动化蓝图](../developer-guide/creating-skills.md)。