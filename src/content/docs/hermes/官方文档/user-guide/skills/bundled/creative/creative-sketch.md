---
title: Sketch
---

title: "草图（Sketch）——可丢弃的HTML原型：2-3个设计变体以供比较"
sidebar_label: "Sketch"
description: "可丢弃的HTML原型：2-3个设计变体以供比较"
---

--- body ---
{/* 本页面由技能目录中的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非本页面。 */}

# 草图（Sketch）

可丢弃的HTML原型：2-3个设计变体以供比较。

## 技能元数据（Skill metadata）

| | |
|---|---|
| 来源（Source） | 内置（默认安装） |
| 路径（Path） | `skills/creative/sketch` |
| 版本（Version） | `1.0.0` |
| 作者（Author） | Hermes Agent（改编自 gsd-build/get-shit-done） |
| 许可证（License） | MIT |
| 平台（Platforms） | linux, macos, windows |
| 标签（Tags） | `sketch`, `mockup`, `design`, `ui`, `prototype`, `html`, `variants`, `exploration`, `wireframe`, `comparison` |
| 相关技能（Related skills） | [`spike`](/docs/user-guide/skills/bundled/software-development/software-development-spike), [`claude-design`](/docs/user-guide/skills/bundled/creative/creative-claude-design), [`popular-web-designs`](/docs/user-guide/skills/bundled/creative/creative-popular-web-designs), [`excalidraw`](/docs/user-guide/skills/bundled/creative/creative-excalidraw) |

## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时代理（agent）所看到的指令。
:::

# 草图（Sketch）

当用户希望在**做出承诺前先看看设计方向**时使用此技能——以可丢弃的HTML原型形式探索UI/UX想法。关键在于生成2-3个交互式变体，以便用户并排比较视觉方向，而不是生成可交付的代码。

当用户说出诸如“画一下这个屏幕”、“让我看看X可能是什么样子”、“比较布局A和布局B”、“给我2-3个UI方案”、“让我看看一些变体”、“在开始构建之前先做个原型”时，加载此技能。

## 何时不使用

- 用户想要一个生产级组件——使用`claude-design`或正常构建它
- 用户想要一个精美的单次HTML制品（落地页、演示文稿）——`claude-design`
- 用户想要一个图表——`excalidraw`、`architecture-diagram`
- 设计已经确定——直接构建即可

## 如果用户已安装完整的GSD系统

如果`gsd-sketch`显示为同级技能（通过`npx get-shit-done-cc --hermes`安装），优先使用**`gsd-sketch`**以获得完整的工作流程：持久化的`.planning/sketches/`目录及MANIFEST、前沿模式分析、跨历史草图的一致性审计、以及与GSD其他部分的集成。本技能是轻量级的独立版本——一次性的草图，无需状态机制。

## 核心方法

```
输入  →  变体  →  正面交锋  →  选出优胜（或迭代）
```

### 1. 输入（如果用户已提供足够信息，可跳过）

在生成变体之前，获取三件事——一次只问一个问题，不要一次性全问：

1. **感觉。**“应该是什么感觉？形容词、情感、一种氛围。”——*“平静、编辑感、像 Linear”*比*“简洁”*更能说明问题。
2. **参考。**“哪些应用、网站或产品体现了你想象中的感觉？”——实际参考胜过抽象描述。
3. **核心操作。**“用户在此屏幕上做的最重要的一件事是什么？”——所有变体都应很好地服务于这一操作；否则它们就只是装饰。

在每个问题之前简短地回应一下。如果用户已经一次性提供了全部三点，直接跳到变体部分。

### 2. 变体（2-3个，从不1个，很少4个以上）

一次性生成**2-3个变体**。每个变体是一个完整的、独立的HTML文件。不要描述变体——直接构建它们。关键在于比较。

每个变体应持**不同的设计立场**，而非不同的像素值。三个很好的变体维度：

- **密度：**紧凑 / 通透 / 超密集（选择两个对比极）
- **重点：**内容优先 / 动作优先 / 工具优先
- **美学：**编辑感 / 实用主义 / 趣味性
- **布局：**单栏 / 侧边栏 / 分屏
- **基准：**卡片式 / 裸内容 / 文档风格

选择一个维度并从中分化。只有强调色不同的两个变体是浪费精力——用户无法区分它们。

**变体命名：**描述立场，而非编号。

<!-- ascii-guard-ignore -->
```
sketches/
├── 001-calm-editorial/
│   ├── index.html
│   └── README.md
├── 001-utilitarian-dense/
│   ├── index.html
│   └── README.md
└── 001-playful-split/
    ├── index.html
    └── README.md
```
<!-- ascii-guard-ignore-end -->

### 3. 使其成为真正的HTML

每个变体是一个**独立的HTML文件**：

- 内联`<style>`——无需构建步骤，无需外部CSS
- 系统字体或通过`<link>`引入的一个Google Font
- 可通过CDN使用Tailwind（`<script src="https://cdn.tailwindcss.com"></script>`）
- 真实的虚假内容——实际句子、实际姓名，而非“Lorem ipsum”
- **交互式**：链接可点击，悬停有反馈，至少有一个状态转换（打开/关闭、过滤、切换）。冻结的静态图像比粗糙的动画原型更差。

在浏览器中打开。如果看起来有问题，先修复再展示给用户。

**视觉验证变体——使用Hermes的浏览器工具。**不要只写HTML然后指望它能渲染好；加载每个变体并查看它：

```
browser_navigate(url="file:///absolute/path/to/sketches/001-calm-editorial/index.html")
browser_vision(question="这个布局看起来干净可读吗？是否有任何可见的bug（文字重叠、未样式化元素、图片损坏）？")
```

`browser_vision`返回页面实际内容的AI描述以及截图路径——能够捕获纯源码检查遗漏的布局bug（例如，字体导入静默失败、flex容器折叠）。修复并重新导航，直到每个变体看起来正确。

**默认CSS重置 + 系统字体栈**用于快速启动：

```html
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "Helvetica Neue", Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    color: #1a1a1a;
    background: #fafafa;
    line-height: 1.5;
  }
</style>
```

### 4. 变体说明（Variant README）

每个变体的`README.md`应回答：

```markdown
## 变体：{立场名称}

### 设计立场
一句话描述驱动该变体的原则。

### 关键选择
- 布局：...
- 排版：...
- 色彩：...
- 交互：...

### 权衡
- 强项：...
- 弱项：...

### 最适合
- 该变体实际服务的用户或用例类型
```

### 5. 正面交锋（Head-to-head）

所有变体构建完成后，以比较形式呈现。不要只列出——**给出意见**：

```markdown
## 关于首页的三个方案

| 维度 | 平静编辑感 | 实用密集 | 趣味分屏 |
|-----------|----------------|-------------------|---------------|
| 密度   | 低            | 高              | 中        |
| 主要动作可见性 | 低 | 高 | 中 |
| 可扫描性 | 高 | 中 | 低 |
| 感觉 | 平静、可信 | 锐利、工具感 | 邀请感、充满活力 |

**我的看法：** 实用密集适合高级用户，平静编辑感适合内容优先的受众。趣味分屏最弱——试图两者兼顾但都未做好。
```

让用户选出一个优胜者，或组合两个形成一个混合体，或要求再迭代一轮。

## 主题化（当项目具有视觉标识时）

如果用户已有现有主题（颜色、字体、令牌），将共享令牌放在`sketches/themes/tokens.css`中，并在每个变体中通过`@import`引用。保持令牌精简：

```css
/* sketches/themes/tokens.css */
:root {
  --color-bg: #fafafa;
  --color-fg: #1a1a1a;
  --color-accent: #0066ff;
  --color-muted: #666;
  --radius: 8px;
  --font-display: "Inter", sans-serif;
  --font-body: -apple-system, BlinkMacSystemFont, sans-serif;
}
```

不要过度令牌化一个可丢弃的草图——三种颜色和一种字体通常就足够了。

## 交互性指标

当用户能够完成以下操作时，草图才算有足够的交互性：

1. **点击一个主要动作**，然后发生可见的变化（状态变化、模态框、提示消息、导航模拟）
2. **看到一个有意义的状态转换**（过滤列表、切换模式、打开/关闭面板）
3. **悬停在可识别的交互元素上**（按钮、行、标签页）

超过这些就是过度工程化一个可丢弃的原型。少于这些就是一张截图。

## 前沿模式（决定下一步草图的内容）

如果已经存在草图，且用户问“下一步该画什么？”：

- **一致性差距**——来自不同草图的两个优胜变体做出了独立的决定，但尚未组合在一起
- **未草图的屏幕**——被引用但从未探索过
- **状态覆盖**——快乐路径已画，但未涉及空状态/加载状态/错误状态/1000项
- **响应式差距**——仅在一种视口下验证；在移动端/超宽屏下是否成立？
- **交互模式**——静态布局存在；过渡、拖拽、滚动行为缺失

提出2-4个候选名称，让用户选择。

## 输出

- 在仓库根目录下创建`sketches/`（如果用户使用GSD约定，则创建`.planning/sketches/`）
- 每个变体一个子目录：`NNN-立场名称/index.html` + `README.md`
- 告知用户如何打开：macOS上`open sketches/001-calm-editorial/index.html`，Linux上`xdg-open`，Windows上`start`
- 保持变体可丢弃——如果你觉得需要保存一个草图，应该将其提升为实际项目代码，而不是当作资产进行策划

**一个变体的典型工具序列：**

```
terminal("mkdir -p sketches/001-calm-editorial")
write_file("sketches/001-calm-editorial/index.html", "<!doctype html>...")
write_file("sketches/001-calm-editorial/README.md", "## Variant: Calm editorial\n...")
browser_navigate(url="file://$(pwd)/sketches/001-calm-editorial/index.html")
browser_vision(question="这个看起来如何？是否有明显的布局问题？")
```

对每个变体重复，然后呈现比较表格。

## 归属

改编自GSD（Get Shit Done）项目的`/gsd-sketch`工作流程——MIT © 2025 Lex Christopherson ([gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done))。完整的GSD系统包含持久化的草图状态、主题/变体模式参考以及一致性审计工作流程；使用`npx get-shit-done-cc --hermes --global`安装。