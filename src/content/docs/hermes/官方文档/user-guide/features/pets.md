---
sidebar_position: 11
title: "宠物（Petdex 吉祥物）"
description: "领养一个动画吉祥物，它会响应代理在 CLI、TUI 和桌面应用中的活动"
---

# 宠物

Hermes 可以显示一个动画**宠物**——一个小的吉祥物精灵，它会根据代理在 **CLI**、**TUI** 和 **桌面应用** 中的活动（空闲、运行工具、思考、完成、失败）做出反应。宠物来自公开的 [petdex](https://github.com/crafter-station/petdex) 画廊。

宠物纯属装饰。它们**不会影响提示缓存、令牌或代理的行为**——精灵仅是显示问题。此功能**默认关闭**，直到你安装并选择宠物后才会激活。

## 工作原理

- 宠物安装到你的配置文件的 `pets/` 目录（`<HERMES_HOME>/pets/<slug>/`），因此每个[配置文件](../profiles.md)保留自己的集合。
- 选择宠物会将 `display.pet.slug` 和 `display.pet.enabled` 写入 `config.yaml`——不存储为密钥或环境变量。
- 每个界面监视其已跟踪的活动，并将其映射到六种动画状态之一。映射集中在一处，因此每个界面行为一致：

| 代理活动 | 宠物状态 |
| --- | --- |
| 工具/回合刚刚失败 | `failed` |
| 计划完成（所有待办事项完成） | `jump`（庆祝） |
| 回合干净地完成 | `wave` |
| 工具正在执行 | `run` |
| 模型正在思考/阅读 | `review` |
| 回合进行中（未指定） | `run` |
| 等待你的响应（消息/批准提示打开） | `waiting`（在旧版8行精灵上回退为 `idle`） |
| 没有任何活动 | `idle` |

## 渲染

在终端（CLI/TUI）中，当你的终端支持图形协议（**kitty**、**Ghostty**、**WezTerm**、**iTerm2** 或 **sixel**）时，Hermes 全保真渲染精灵。否则自动回退到真彩色 Unicode **半块**渲染。在管道或重定向中（无 TTY），终端渲染默认禁用。

桌面应用将宠物绘制为画布上的浮动精灵，并通过**设置 → 外观**切换。

## 快速开始（CLI）

```bash
# 浏览画廊（按子字符串过滤）
hermes pets list
hermes pets list cat

# 安装宠物并一次性激活
hermes pets install boba --select

# 在终端中预览/动画（Ctrl+C 停止）
hermes pets show

# 检查你的设置
hermes pets doctor
```

## `hermes pets` 命令

| 目标 | 命令 |
| --- | --- |
| 浏览画廊 | `hermes pets list [query] [--limit N]` |
| 列出已安装的宠物 | `hermes pets list --installed` |
| 安装宠物 | `hermes pets install <slug> [--select] [--force]` |
| 设置活动宠物 | `hermes pets select [slug]`（不带 slug 将显示选择器） |
| 调整宠物大小（全局） | `hermes pets scale <factor>`（例如 `0.5`，限制在 0.1–3.0） |
| 预览/动画 | `hermes pets show [slug] [--state <s>] [--cycle] [--once] [--mode <m>] [--scale <f>]` |
| 禁用宠物 | `hermes pets off` |
| 移除已安装的宠物 | `hermes pets remove <slug>` |
| 诊断设置 | `hermes pets doctor` |

`hermes pets show` 标志：

- `--state` — 播放单个状态（`idle`、`wave`、`run`、`failed`、`review`、`jump`）。
- `--cycle` — 循环播放所有状态。
- `--once` — 仅播放一次，不循环。
- `--mode` — 覆盖渲染协议（`kitty`、`iterm`、`sixel`、`unicode`、`auto`）。
- `--scale` — 覆盖屏幕缩放比例（`0` = 使用配置）。

## `/pet` 斜杠命令

在 CLI 和 TUI 中，无需离开会话即可管理宠物：

- `/pet` — 切换宠物开启/关闭（如果没有活动宠物，则领养第一个已安装的宠物）。
- `/pet list` — 浏览画廊。
- `/pet scale <factor>` — 全局调整宠物大小（例如 `/pet scale 0.5`）。
- `/pet <slug>` — 领养特定宠物。
- `/pet off` — 禁用宠物。

在 TUI 中，`/pet list` 打开交互式选择器覆盖层；在桌面应用中，它打开 Cmd+K 宠物面板。

## 桌面应用

在桌面应用中，你可以通过两种方式管理宠物：

- **Cmd+K → "宠物…"** — 浏览、搜索、领养和切换宠物，无需离开键盘（与主题选择器类似）。
- **设置 → 外观** — 相同的画廊，外加一个**大小滑块**，拖拽时实时调整浮动吉祥物的大小。

两者都会在原地领养/切换/调整浮动吉祥物——大小更改立即生效；领养新宠物后片刻即可显示。

### 弹出覆盖层

**Shift+点击**浮动宠物，将其弹出到独立的透明、始终置顶的桌面窗口。当 Hermes 最小化时（类似 Codex 风格），宠物仍保持可见，因此一眼就能知道代理正在做什么。

弹出后的操作：

| 操作 | 行为 |
| --- | --- |
| **拖拽** | 将宠物移动到屏幕任意位置，甚至应用之外。其位置和弹出/嵌入状态在重启后保持不变。 |
| **单击** | 打开迷你编辑器，向最近的会话发送提示——无需显示应用。 |
| **双击** | 切换应用窗口：如果应用在前台则最小化，如果隐藏则恢复。 |
| **Shift+点击** | 将宠物弹回窗口。 |
| **邮件图标** | 仅在你离开时回合完成时出现；点击将应用提升到最近的线程（并标记为已读）。 |

只有弹出的宠物会显示**气泡**（`工作中…`、`思考中…`、`轮到你了`……）——在窗口内，应用本身是界面，因此宠物保持静默。

覆盖层是应用内宠物的纯粹傀儡——它没有独立的网关连接，也不会出现在 dock 或应用切换器中。

## 配置

所有设置均位于 `config.yaml` 的 `display.pet` 下：

```yaml
display:
  pet:
    enabled: false        # 主开关（选择宠物后变为 true）
    slug: ""              # 活动宠物；空 = 第一个安装的
    render_mode: auto      # auto | kitty | iterm | sixel | unicode | off
    scale: 0.33           # 主大小旋钮（相对于原生 192x208 帧）
    unicode_cols: 0       # 硬性覆盖终端宽度（0 = 从 scale 推导）
```

- **`scale`** 是唯一的主大小旋钮。一个数字同时缩小所有表面：桌面画布按此比例缩放像素，CLI/TUI 从此推导终端列宽度。半块回退会限制在可读性下限——它无法像真实像素的 kitty/GUI 渲染那样缩小而不变得模糊，因此相同的 `scale` 在 kitty 下清晰，但在半块中受到限制。
- **`render_mode: auto`** 检测 kitty/iTerm2/sixel，并回退到 unicode 半块。显式设置它可强制使用某个协议，或设为 `off` 以禁用终端渲染，同时保持桌面上的宠物。
- **`unicode_cols`** 独立于 `scale` 固定终端列宽度；留为 `0` 则从 `scale` 推导宽度。

## 故障排除

运行 `hermes pets doctor`——它会报告：

- 宠物目录以及安装了哪些宠物，
- `display.pet.enabled`、`display.pet.slug` 以及解析后的活动宠物，
- 配置的 `render_mode`、检测到的终端图形协议以及 TTY 的有效模式，
- 是否可导入 Pillow（用于精灵解码）。

当宠物已安装、已选择、已启用且 Pillow 可用时，它将打印 `✓ ready`。

常见问题：

- 只有当你**安装并选择**了宠物（`enabled: true`）后，宠物才会显示。
- 在管道/重定向中（无 TTY），终端渲染默认禁用。
- petdex npm CLI 安装到 `~/.codex/pets`；Hermes 使用其自身的作用域 `<HERMES_HOME>/pets/`——请通过 `hermes pets` 安装。

## 另请参阅

- [`petdex` 技能](../skills/bundled/productivity/productivity-petdex.md) 允许代理按请求安装和切换宠物。