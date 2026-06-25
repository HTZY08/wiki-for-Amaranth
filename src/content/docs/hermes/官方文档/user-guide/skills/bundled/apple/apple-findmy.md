---
title: Findmy
---

title: "Findmy — 通过 FindMy 追踪苹果设备/AirTags"
sidebar_label: "Findmy"
description: "通过 FindMy 追踪苹果设备/AirTags"
---

--- body ---
{/* 此页面由网站脚本 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Findmy

通过 macOS 上的 FindMy.app 追踪苹果设备/AirTags。

## 技能（Skill）元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/apple/findmy` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | macos |
| 标签 | `FindMy`, `AirTag`, `location`, `tracking`, `macOS`, `Apple` |

## 参考：完整的 SKILL.md

:::info
以下是当该技能被触发时 Hermes 加载的完整技能定义。这是技能激活后代理（agent）看到的指令。
:::

# 查找我的（Find My）（苹果）

通过 macOS 上的 FindMy.app 追踪苹果设备和 AirTags。由于苹果未提供 FindMy 的命令行接口（CLI），本技能使用 AppleScript 打开应用并通过屏幕截图读取设备位置。

## 前置条件

- **macOS**，已安装“查找我的”应用并登录 iCloud
- 设备/AirTags 已在“查找我的”中注册
- 终端已获得屏幕录制权限（系统设置 → 隐私 → 屏幕录制）
- **可选但推荐**：安装 `peekaboo` 以获得更好的 UI 自动化：
  `brew install steipete/tap/peekaboo`

## 何时使用

- 用户询问“我的[设备/猫/钥匙/包]在哪里？”
- 追踪 AirTag 位置
- 检查设备位置（iPhone、iPad、Mac、AirPods）
- 随时间监控宠物或物品的移动（AirTag 巡逻路线）

## 方法 1：AppleScript + 截图（基础）

### 打开“查找我的”并导航

```bash
# 打开“查找我的”应用
osascript -e 'tell application "FindMy" to activate'

# 等待加载完成
sleep 3

# 截取“查找我的”窗口截图
screencapture -w -o /tmp/findmy.png
```

然后使用 `vision_analyze` 读取截图：
```
vision_analyze(image_url="/tmp/findmy.png", question="显示了哪些设备/物品，它们的位置在哪里？")
```

### 切换标签页

```bash
# 切换到设备标签页
osascript -e '
tell application "System Events"
    tell process "FindMy"
        click button "Devices" of toolbar 1 of window 1
    end tell
end tell'

# 切换到物品标签页（AirTags）
osascript -e '
tell application "System Events"
    tell process "FindMy"
        click button "Items" of toolbar 1 of window 1
    end tell
end tell'
```

## 方法 2：Peekaboo UI 自动化（推荐）

如果安装了 `peekaboo`，请使用它进行更可靠的 UI 交互：

```bash
# 打开“查找我的”
osascript -e 'tell application "FindMy" to activate'
sleep 3

# 捕获并标注 UI
peekaboo see --app "FindMy" --annotate --path /tmp/findmy-ui.png

# 按元素 ID 点击特定设备/物品
peekaboo click --on B3 --app "FindMy"

# 捕获详情视图
peekaboo image --app "FindMy" --path /tmp/findmy-detail.png
```

然后通过视觉分析：
```
vision_analyze(image_url="/tmp/findmy-detail.png", question="此设备/物品显示的位置是什么？如果可见，请包含地址和坐标。")
```

## 工作流：随时间追踪 AirTag 位置

用于监控 AirTag（例如追踪猫的巡逻路线）：

```bash
# 1. 打开“查找我的”并切换到物品标签页
osascript -e 'tell application "FindMy" to activate'
sleep 3

# 2. 点击 AirTag 物品（保持页面打开——AirTag 仅在页面打开时更新位置）

# 3. 定期捕获位置
while true; do
    screencapture -w -o /tmp/findmy-$(date +%H%M%S).png
    sleep 300  # 每 5 分钟
done
```

用视觉分析每张截图以提取坐标，然后汇总路线。

## 限制

- FindMy **没有 CLI 或 API**——必须使用 UI 自动化
- AirTag 仅在“查找我的”页面主动显示时更新位置
- 位置精度取决于 FindMy 网络中附近苹果设备的数量
- 屏幕截图需要屏幕录制权限
- AppleScript UI 自动化可能随 macOS 版本变化而失效

## 规则

1. 追踪 AirTag 时保持“查找我的”应用在前台（最小化后会停止更新）
2. 使用 `vision_analyze` 读取截图内容——不要尝试解析像素
3. 对于持续追踪，使用 cronjob 定期捕获并记录位置
4. 尊重隐私——仅追踪用户拥有的设备/物品