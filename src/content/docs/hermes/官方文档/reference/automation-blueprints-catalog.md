---
title: 自动化蓝图目录
description: Hermes Agent 官方文档汉化版
---

> 本文档基于 [Hermes Agent 官方文档](https://hermes-agent.nousresearch.com/docs/) 汉化
> 原文地址: [`reference/automation-blueprints-catalog.md`](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/reference/automation-blueprints-catalog.md)
> 本版本为自用学习用途，非官方翻译。

---
sidebar_position: 7
title: "Automation Blueprints Catalog"
description: "Ready-to-run automation blueprints — set one up from the dashboard, CLI, TUI, any messenger, or the desktop app."
---

import AutomationBlueprintsCatalog from '@site/src/components/AutomationBlueprintsCatalog';

# Automation Blueprints

Automation Blueprints are ready-to-run automations. Pick one, fill in a couple
of fields, and Hermes schedules it as a cron job — no cron syntax required.

Every blueprint works from **every surface**:

- **Dashboard / desktop app** — open the Cron page, switch to the **Blueprints**
  tab, fill the form, and click *Schedule it*.
- **CLI, TUI, and messengers** — type `/blueprint <name>` (e.g.
  `/blueprint morning-brief`) and Hermes asks you for what it needs, one
  question at a time, then schedules it. The name match is forgiving — a
  prefix or near-spelling resolves. Power users can skip the questions by
  passing values inline: `/blueprint morning-brief time=08:00`.
- **Desktop app** — click **Send to App** on any blueprint and it opens with the
  command pre-loaded in your composer.

Blueprints never schedule anything silently — you always confirm before the job
is created. Manage created jobs anytime with `/cron`.

<AutomationBlueprintsCatalog />

## Writing your own

A blueprint is just a skill with a `metadata.hermes.blueprint` block in its
`SKILL.md` frontmatter. See
[Creating Skills → Automation Blueprints](../developer-guide/creating-skills.md) for the
slot schema and how to publish one.
