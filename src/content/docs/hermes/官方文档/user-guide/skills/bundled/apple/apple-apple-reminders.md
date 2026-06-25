--- frontmatter ---
---
title: "Apple 提醒事项 — 通过 remindctl 管理 Apple 提醒事项：添加、列出、完成"
sidebar_label: "Apple 提醒事项"
description: "通过 remindctl 管理 Apple 提醒事项：添加、列出、完成"
---

--- body ---
{/* 此页面由 website/scripts/generate-skill-docs.py 基于技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Apple 提醒事项

通过 remindctl 管理 Apple 提醒事项：添加、列出、完成。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/apple/apple-reminders` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | macos |
| 标签 | `Reminders`, `tasks`, `todo`, `macOS`, `Apple` |

## 参考：完整 SKILL.md

:::info
以下是当此技能被触发时 Hermes 加载的完整技能定义。这是技能激活时代理（Agent）看到的指令。
:::

# Apple 提醒事项

使用 `remindctl` 直接从终端管理 Apple 提醒事项。任务通过 iCloud 在所有 Apple 设备间同步。

## 前提条件

- 已安装 **macOS** 及 Reminders.app
- 安装：`brew install steipete/tap/remindctl`
- 在提示时授予提醒事项权限
- 检查：`remindctl status` / 请求：`remindctl authorize`

## 何时使用

- 用户提及“提醒”或“提醒事项 App”
- 创建带截止日期、可同步到 iOS 的个人待办事项
- 管理 Apple 提醒事项列表
- 用户希望任务显示在其 iPhone/iPad 上

## 何时不使用

- 安排代理（Agent）提醒 → 改用 cronjob 工具
- 日历事件 → 使用 Apple 日历或 Google 日历
- 项目任务管理 → 使用 GitHub Issues、Notion 等
- 如果用户说“提醒我”但指的是代理提醒 → 先澄清

## 快速参考

### 查看提醒事项

```bash
remindctl                    # 今日提醒
remindctl today              # 今天
remindctl tomorrow           # 明天
remindctl week               # 本周
remindctl overdue            # 过期
remindctl all                # 所有
remindctl 2026-01-04         # 指定日期
```

### 管理列表

```bash
remindctl list               # 列出所有列表
remindctl list Work          # 显示指定列表
remindctl list Projects --create    # 创建列表
remindctl list Work --delete        # 删除列表
```

### 创建提醒事项

```bash
remindctl add "Buy milk"
remindctl add --title "Call mom" --list Personal --due tomorrow
remindctl add --title "Meeting prep" --due "2026-02-15 09:00"
```

### 截止时间 vs 提醒/提前通知

`--due` 和 `--alarm` 是不同的字段：

- `--due` 设置提醒的截止日期/时间。
- `--alarm` 设置 EventKit 的提醒/通知触发时间。定时提醒默认会在截止时间触发通知，但当用户要求提前提醒时，请显式传递 `--alarm`。

对于截止时间为下午 2:00、并提前 30 分钟通知的提醒：

```bash
remindctl add --title "Hairdresser" --due "2026-05-15 14:00" --alarm "2026-05-15 13:30"
```

编辑现有提醒：

```bash
remindctl edit 87354 --due "2026-05-15 14:00" --alarm "2026-05-15 13:30"
```

提醒事项 UI 可能会按提醒时间显示或分组项目，因为那是通知触发的时间。请通过 JSON 验证，而非假定截止时间已变更：

```bash
remindctl today --json
```

预期的结构：

- `dueDate`：实际截止时间
- `alarmDate`：通知/提前提醒时间

Apple 公开的 `EKReminder` 文档仅列出提醒特有的属性。提醒支持来自继承的 `EKCalendarItem` 行为，通过 remindctl 的 `--alarm` 标志暴露。

### 完成/删除

```bash
remindctl complete 1 2 3          # 按 ID 完成
remindctl delete 4A83 --force     # 按 ID 删除
```

### 输出格式

```bash
remindctl today --json       # JSON 格式，便于脚本处理
remindctl today --plain      # TSV 格式
remindctl today --quiet      # 仅显示计数
```

## 日期格式

`--due` 和日期过滤器支持：
- `today`, `tomorrow`, `yesterday`
- `YYYY-MM-DD`
- `YYYY-MM-DD HH:mm`
- ISO 8601（`2026-01-04T12:34:56Z`）

## 规则

1. 当用户说“提醒我”时，需澄清：是 Apple 提醒事项（同步到手机）还是代理 cronjob 提醒
2. 创建前始终确认提醒内容和截止日期
3. 使用 `--json` 进行程序化解析