---
title: Openhue
---

title: "Openhue — 通过 OpenHue CLI 控制 Philips Hue 灯、场景和房间"
sidebar_label: "Openhue"
description: "通过 OpenHue CLI 控制 Philips Hue 灯、场景和房间"
---

--- body ---
{/* 此页面由技能目录中的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Openhue

通过 OpenHue CLI 控制 Philips Hue 灯、场景和房间。

## 技能元数据（Skill metadata）

| | |
|---|---|
| 来源（Source） | 内置（默认安装） |
| 路径（Path） | `skills/smart-home/openhue` |
| 版本（Version） | `1.0.0` |
| 作者（Author） | 社区（community） |
| 许可证（License） | MIT |
| 平台（Platforms） | linux, macos, windows |
| 标签（Tags） | `Smart-Home`, `Hue`, `Lights`, `IoT`, `Automation` |

## 参考：完整 SKILL.md

:::info
以下是此技能触发时 Hermes 加载的完整技能定义。这是技能激活后智能体（Agent）所看到的指令。
:::

# OpenHue CLI

通过终端，经 Hue 桥接器（Hue Bridge）控制 Philips Hue 灯和场景。

## 前置条件（Prerequisites）

```bash
# Linux（预编译二进制文件）
curl -sL https://github.com/openhue/openhue-cli/releases/latest/download/openhue-linux-amd64 -o ~/.local/bin/openhue && chmod +x ~/.local/bin/openhue

# macOS
brew install openhue/cli/openhue-cli
```

首次运行需要按下 Hue 桥接器上的按钮进行配对。桥接器必须与运行环境位于同一本地网络中。

## 使用场景

- "打开/关闭灯"
- "调暗客厅灯"
- "设置场景"或"电影模式"
- 控制特定的 Hue 房间、区域或单个灯泡
- 调节亮度、颜色或色温

## 常用命令（Common Commands）

### 列出资源（List Resources）

```bash
openhue get light       # 列出所有灯
openhue get room        # 列出所有房间
openhue get scene       # 列出所有场景
```

### 控制灯光（Control Lights）

```bash
# 打开/关闭
openhue set light "Bedroom Lamp" --on
openhue set light "Bedroom Lamp" --off

# 亮度（0-100）
openhue set light "Bedroom Lamp" --on --brightness 50

# 色温（暖到冷：153-500 米雷克）
openhue set light "Bedroom Lamp" --on --temperature 300

# 颜色（按名称或十六进制）
openhue set light "Bedroom Lamp" --on --color red
openhue set light "Bedroom Lamp" --on --rgb "#FF5500"
```

### 控制房间（Control Rooms）

```bash
# 关闭整个房间
openhue set room "Bedroom" --off

# 设置房间亮度
openhue set room "Bedroom" --on --brightness 30
```

### 场景（Scenes）

```bash
openhue set scene "Relax" --room "Bedroom"
openhue set scene "Concentrate" --room "Office"
```

## 快速预设（Quick Presets）

```bash
# 就寝模式（暖光调暗）
openhue set room "Bedroom" --on --brightness 20 --temperature 450

# 工作模式（冷光亮）
openhue set room "Office" --on --brightness 100 --temperature 250

# 电影模式（昏暗）
openhue set room "Living Room" --on --brightness 10

# 全部关闭
openhue set room "Bedroom" --off
openhue set room "Office" --off
openhue set room "Living Room" --off
```

## 注意事项（Notes）

- 桥接器必须与运行 Hermes 的设备位于同一本地网络中
- 首次运行需要物理按下 Hue 桥接器上的按钮以授权
- 颜色功能仅对支持彩色的灯泡有效（纯白色型号无效）
- 灯和房间名称区分大小写——请使用 `openhue get light` 检查准确名称
- 可通过 cron 任务实现定时灯光控制（例如：就寝时调暗，起床时调亮）