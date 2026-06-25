--- frontmatter ---
---
title: "架构图（Architecture Diagram）—— 深色主题SVG架构/云/基础设施图表，以HTML呈现"
sidebar_label: "架构图（Architecture Diagram）"
description: "深色主题SVG架构/云/基础设施图表，以HTML呈现"
---

--- body ---
{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 架构图（Architecture Diagram）

深色主题的SVG架构/云/基础设施图表，以HTML呈现。

## 技能元数据（Skill metadata）

| | |
|---|---|
| 来源（Source） | 内置（默认安装） |
| 路径（Path） | `skills/creative/architecture-diagram` |
| 版本（Version） | `1.0.0` |
| 作者（Author） | Cocoon AI (hello@cocoon-ai.com)，由 Hermes Agent 移植 |
| 许可证（License） | MIT |
| 平台（Platforms） | linux, macos, windows |
| 标签（Tags） | `architecture`, `diagrams`, `SVG`, `HTML`, `visualization`, `infrastructure`, `cloud` |
| 相关技能（Related skills） | [`concept-diagrams`](/docs/user-guide/skills/optional/creative/creative-concept-diagrams)，[`excalidraw`](/docs/user-guide/skills/bundled/creative/creative-excalidraw) |

## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是代理（Agent）在技能激活时看到的指令。
:::

# 架构图技能（Architecture Diagram Skill）

生成专业的、深色主题的技术架构图，作为独立的HTML文件，内联SVG图形。无需外部工具、无需API密钥、无需渲染库——只需编写HTML文件并在浏览器中打开即可。

## 适用范围（Scope）

**最适合用于：**
- 软件系统架构（前端/后端/数据库层）
- 云基础设施（VPC、区域、子网、托管服务）
- 微服务/服务网格拓扑
- 数据库 + API 映射、部署图
- 任何技术基础设施主题，适合深色网格背景美学

**首先考虑其他工具的情形：**
- 物理、化学、数学、生物学或其他科学主题
- 物理对象（车辆、硬件、解剖图、横截面）
- 平面图、叙事流程、教育/教科书风格的视觉内容
- 手绘白板草图（考虑使用 `excalidraw`）
- 动画讲解（考虑使用动画技能）

如果该主题有更专业的技能可用，则优先使用。如果没有合适的技能，此技能也可作为通用SVG图表的备选方案——输出将带有下述深色技术美学。

基于 [Cocoon AI 的 architecture-diagram-generator](https://github.com/Cocoon-AI/architecture-diagram-generator) (MIT)。

## 工作流程（Workflow）

1. 用户描述其系统架构（组件、连接、技术）
2. 按照以下设计系统生成HTML文件
3. 使用 `write_file` 保存为 `.html` 文件（例如 `~/architecture-diagram.html`）
4. 用户在任意浏览器中打开——离线工作，无依赖项

### 输出位置（Output Location）

将图表保存到用户指定的路径，或默认保存到当前工作目录：
```
./[项目名称]-architecture.html
```

### 预览（Preview）

保存后，建议用户打开它：
```bash
# macOS
open ./my-architecture.html
# Linux
xdg-open ./my-architecture.html
```

## 设计系统与视觉语言（Design System & Visual Language）

### 颜色调色板（语义映射）（Color Palette (Semantic Mapping)）

使用特定的 `rgba` 填充和十六进制描边来分类组件：

| 组件类型（Component Type） | 填充（Fill）(rgba) | 描边（Stroke）(Hex) |
| :--- | :--- | :--- |
| **前端（Frontend）** | `rgba(8, 51, 68, 0.4)` | `#22d3ee` (青色-400) |
| **后端（Backend）** | `rgba(6, 78, 59, 0.4)` | `#34d399` (翠绿色-400) |
| **数据库（Database）** | `rgba(76, 29, 149, 0.4)` | `#a78bfa` (紫罗兰色-400) |
| **AWS/云（AWS/Cloud）** | `rgba(120, 53, 15, 0.3)` | `#fbbf24` (琥珀色-400) |
| **安全（Security）** | `rgba(136, 19, 55, 0.4)` | `#fb7185` (玫瑰色-400) |
| **消息总线（Message Bus）** | `rgba(251, 146, 60, 0.3)` | `#fb923c` (橙色-400) |
| **外部（External）** | `rgba(30, 41, 59, 0.5)` | `#94a3b8` (石板色-400) |

### 排版与背景（Typography & Background）
- **字体（Font）：** JetBrains Mono（等宽字体），从 Google Fonts 加载
- **字号（Sizes）：** 12px（名称），9px（子标签），8px（注释），7px（极小标签）
- **背景（Background）：** Slate-950 (`#020617`)，带有微妙的40px网格图案

```svg
<!-- 背景网格图案（Background Grid Pattern） -->
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.5"/>
</pattern>
```

## 技术实现细节（Technical Implementation Details）

### 组件渲染（Component Rendering）
组件为圆角矩形（`rx="6"`），描边宽度1.5px。为防止箭头透过半透明填充显示，使用**双重矩形遮罩技术**：
1. 绘制不透明背景矩形（`#0f172a`）
2. 在其上绘制半透明样式矩形

### 连接规则（Connection Rules）
- **Z轴顺序（Z-Order）：** 在SVG中*尽早*绘制箭头（在网格之后），使其渲染在组件框后面
- **箭头（Arrowheads）：** 通过SVG标记定义
- **安全流（Security Flows）：** 使用玫瑰色虚线（`#fb7185`）
- **边界（Boundaries）：**
  - *安全组（Security Groups）：* 虚线（`4,4`），玫瑰色
  - *区域（Regions）：* 大虚线（`8,4`），琥珀色，`rx="12"`

### 间距与布局逻辑（Spacing & Layout Logic）
- **标准高度（Standard Height）：** 60px（服务）；80-120px（大型组件）
- **垂直间距（Vertical Gap）：** 组件之间至少40px
- **消息总线（Message Buses）：** 必须放置在服务之间的*间隙*中，不得重叠
- **图例放置（Legend Placement）：** **关键。** 必须放置在所有边界框之外。计算所有边界的最低Y坐标，并将图例放置在其下方至少20px处。

## 文档结构（Document Structure）

生成的HTML文件遵循四部分布局：
1. **标题（Header）：** 带有脉冲点指示器和副标题的标题
2. **主SVG（Main SVG）：** 包含在圆角边框卡片内的图表
3. **摘要卡片（Summary Cards）：** 图表下方的三卡片网格，用于高层次细节
4. **页脚（Footer）：** 最小化元数据

### 信息卡片模式（Info Card Pattern）
```html
<div class="card">
  <div class="card-header">
    <div class="card-dot cyan"></div>
    <h3>标题（Title）</h3>
  </div>
  <ul>
    <li>• 项目一</li>
    <li>• 项目二</li>
  </ul>
</div>
```

## 输出要求（Output Requirements）
- **单个文件（Single File）：** 一个自包含的 `.html` 文件
- **无外部依赖（No External Dependencies）：** 所有CSS和SVG必须内联（Google Fonts除外）
- **无JavaScript（No JavaScript）：** 使用纯CSS实现任何动画（如脉冲点）
- **兼容性（Compatibility）：** 必须在任何现代网络浏览器中正确渲染

## 模板参考（Template Reference）

加载完整的HTML模板，以获取精确的结构、CSS和SVG组件示例：

```
skill_view(name="architecture-diagram", file_path="templates/template.html")
```

该模板包含每种组件类型（前端、后端、数据库、云、安全）、箭头样式（标准、虚线、曲线）、安全组、区域边界和图例的工作示例——在生成图表时，将其作为结构参考。