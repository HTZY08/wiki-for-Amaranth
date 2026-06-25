---
title: "Pretext 文本布局"
sidebar_label: "Pretext 文本布局"
description: "用于使用 @chenglou/pretext 构建创意浏览器演示——无DOM文本布局，适用于ASCII艺术、文字绕障碍物排版、文本即几何游戏、动态字样排版以及文本驱动的生成艺术。默认生成单文件HTML演示。"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Pretext 文本布局

用于使用 @chenglou/pretext 构建创意浏览器演示——无DOM文本布局，适用于ASCII艺术、文字绕障碍物排版、文本即几何游戏、动态字样排版以及文本驱动的生成艺术。默认生成单文件 HTML 演示。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/pretext` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `creative-coding`, `typography`, `pretext`, `ascii-art`, `canvas`, `generative`, `text-layout`, `kinetic-typography` |
| 相关技能 | [`p5js`](/docs/user-guide/skills/bundled/creative/creative-p5js), [`claude-design`](/docs/user-guide/skills/bundled/creative/creative-claude-design), [`excalidraw`](/docs/user-guide/skills/bundled/creative/creative-excalidraw), [`architecture-diagram`](/docs/user-guide/skills/bundled/creative/creative-architecture-diagram) |

## 参考：完整的 SKILL.md

:::info
以下为触发该技能时 Hermes 加载的完整技能定义。这是技能激活时代理看到的指令。
:::

# Pretext 创意演示

## 概述

[`@chenglou/pretext`](https://github.com/chenglou/pretext) 是一个 15KB 零依赖 TypeScript 库，由 Cheng Lou（React 核心成员、ReasonML、Midjourney）开发，用于**无需 DOM 的多行文本测量与布局**。它只做一件事：给定 `(text, font, width)`，返回换行、每行宽度、每个字素（grapheme）的位置以及总高度——全部通过 canvas 测量实现，无需重排（reflow）。

这听起来像管道工作。其实不然。由于它快速且几何化，它是一个**创意基石（creative primitive）**：你可以在 60fps 下让段落绕一个移动的精灵（sprite）重排，构建关卡几何由真实词语构成的游戏，通过散文驱动 ASCII 标志，将文本打散为具有精确字素初始位置的粒子，或者实现收缩包装（shrink-wrap）的多行 UI 而无需任何 `getBoundingClientRect` 的性能抖动。

这个技能的存在是为了让 Hermes 能用它制作**酷炫的演示**——就是人们常发布到 X 上的那种。参见 `pretext.cool` 和 `chenglou.me/pretext` 查看社区演示集。

## 何时使用

当用户提出以下需求时使用：
- 一个“pretext 演示”/“酷炫的 pretext 玩意儿”/“文本即 X”
- 文字绕移动形状流动（英雄板块、编辑布局、动画长页面）
- 使用**真实单词或散文**而非等宽栅格的 ASCII 艺术效果
- 游戏场地/障碍物/砖块由文本构成的游戏（字母版俄罗斯方块、散文版打砖块）
- 带有逐字形物理效果的动态排版（碎裂、散射、群集、流动）
- 排版生成艺术，尤其是非拉丁脚本或混合脚本
- 多行“收缩包装”UI（恰好能容纳文本的最小容器宽度）
- 任何需要在**渲染之前**知道换行的场景

不要用于：
- 静态 SVG/HTML 页面，CSS 已能解决布局——直接用 CSS
- 富文本编辑器、通用内联格式化引擎（pretext 有意保持狭窄）
- 图像转文本（使用 `ascii-art` / `ascii-video` 技能）
- 纯 canvas 生成艺术且与文本无关——请用 `p5js`

## 创意标准

这是在浏览器中渲染的视觉艺术。Pretext 返回数字；**你**负责绘制。

- **不要交付“hello world”演示。** `hello-orb-flow.html` 模板只是*起点*。每个交付的演示必须加入有意的色彩、动效、构图，以及一个用户没要求但会欣赏的视觉细节。
- **深色背景、暖色调核心、考究的调色板。** 经典琥珀色配黑色（CRT/终端）可行，但冷白配炭黑（编辑风格）以及低饱和度粉彩（Risograph 风格）也不错。选定一种并坚持使用。
- **比例字体是关键。** Pretext 的整体氛围是“非等宽”——要充分利用这一点。使用 Iowan Old Style、Inter、JetBrains Mono、Helvetica Neue 或可变字体。切勿默认使用无衬线体。
- **真实的来源/文本，而非 lorem ipsum。** 语料应有意义。短篇宣言、诗歌、真实源代码、找到的文本、库本身的 README——永远不要用 `lorem ipsum`。
- **首帧即完美。** 没有加载状态，没有空白帧。演示必须在打开瞬间就看起来可交付。

## 技术栈

每个演示是一个独立的 HTML 文件。无需构建步骤。

| 层 | 工具 | 用途 |
|-------|------|------|
| 核心 | 通过 `esm.sh` CDN 加载的 `@chenglou/pretext` | 文本测量 + 行布局 |
| 渲染 | HTML5 Canvas 2D | 字形渲染、每帧合成 |
| 分词 | `Intl.Segmenter`（内置） | 用于 emoji / CJK / 组合标记的字素分割 |
| 交互 | 原始 DOM 事件 | 鼠标 / 触摸 / 滚轮——无框架 |

```html
<script type="module">
import {
  prepare, layout,                   // 用例1：简单高度
  prepareWithSegments, layoutWithLines,  // 用例2a：固定宽度行
  layoutNextLineRange, materializeLineRange, // 用例2b：流式/可变宽度
  measureLineStats, walkLineRanges,  // 不分配字符串的统计
} from "https://esm.sh/@chenglou/pretext@0.0.6";
</script>
```

固定版本。撰写时为 `@0.0.6`——如果演示行为异常，请查看 [npm](https://www.npmjs.com/package/@chenglou/pretext) 获取最新版本。

## 两种用例

几乎一切都归结为以下两种形态之一。请掌握两者。

### 用例1——测量，然后用 CSS/DOM 渲染

```js
const prepared = prepare(text, "16px Inter");
const { height, lineCount } = layout(prepared, 320, 20);
```

你仍然让浏览器绘制文本。Pretext 仅告诉你给定宽度下盒子会有多高，**无需**读取 DOM。用于：
- 行内包含换行文本的虚拟列表
- 需要精确卡片高度的瀑布流（Masonry）
- “这个标签能放下吗？”的开发时检查
- 远程文本加载时防止布局偏移

**确保 `font` 和 `letterSpacing` 与你的 CSS 完全同步。** Canvas 的 `ctx.font` 格式（例如 `"16px Inter"`、`"500 17px 'JetBrains Mono'"`）必须与渲染的 CSS 匹配，否则测量会偏移。

### 用例2——自己测量*并*渲染

```js
const prepared = prepareWithSegments(text, FONT);
const { lines } = layoutWithLines(prepared, 320, 26);
for (let i = 0; i < lines.length; i++) {
  ctx.fillText(lines[i].text, 0, i * 26);
}
```

这是创意工作的所在。你拥有绘制权，因此可以：
- 渲染到 canvas、SVG、WebGL 或任何坐标系
- 替换逐字形变换（旋转、抖动、缩放、透明度）
- 将行元数据（宽度、字素位置）用作几何

对于**每行宽度可变**的流动（文字绕形状、文字在环带中、文字在非矩形列中）：

```js
let cursor = { segmentIndex: 0, graphemeIndex: 0 };
let y = 0;
while (true) {
  const lineWidth = widthAtY(y);  // 你的函数：在 y 处走廊有多宽？
  const range = layoutNextLineRange(prepared, cursor, lineWidth);
  if (!range) break;
  const line = materializeLineRange(prepared, range);
  ctx.fillText(line.text, leftEdgeAtY(y), y);
  cursor = range.end;
  y += lineHeight;
}
```

这是整个库中最重要的模式。它解锁了“文字绕拖拽精灵流动”——那个在 X 上爆红的演示。

### 值得了解的辅助方法

- `measureLineStats(prepared, maxWidth)` → `{ lineCount, maxLineWidth }`——最宽的行，即多行收缩包装宽度。
- `walkLineRanges(prepared, maxWidth, callback)`——遍历行而不分配字符串。用于当你不需要字符时对字素进行统计/物理计算。
- `@chenglou/pretext/rich-inline`——相同系统，但用于混合字体/标签/提及的段落。从子路径导入。

## 演示配方模式

社区语料库（参见 `references/patterns.md`）聚集为几种强模式。选择一种并发挥——除非被要求，否则不要发明新类别。

| 模式 | 关键 API | 示例思路 |
|---|---|---|
| **绕障碍物重排** | `layoutNextLineRange` + 每行宽度函数 | 编辑段落围绕一个拖动的光标精灵分开 |
| **文本即几何游戏** | `layoutWithLines` + 每行碰撞矩形 | 打砖块，每个砖块是一个测量过的单词 |
| **碎裂/粒子** | `walkLineRanges` → 逐字素 (x,y) → 物理 | 点击后句子爆炸成字母 |
| **ASCII 障碍排版** | `layoutNextLineRange` + 按行测量障碍跨度 | 位图 ASCII 标志、形状变形、可拖动的线框物体使文本围绕其实际几何形状打开 |
| **编辑多栏** | 每栏 `layoutNextLineRange` + 共享游标 | 带有拉引语的动画杂志跨页 |
| **动态类型** | `layoutWithLines` + 每行随时间变换 | 星战片头、波浪、弹跳、故障效果 |
| **多行收缩包装** | `measureLineStats` | 自动调整到最紧凑容器的引用卡片 |

参见 `templates/donut-orbit.html` 和 `templates/hello-orb-flow.html` 作为可运行的单文件入门。

## 工作流程

1. **根据用户要求从上面的表格中选择一个模式。**
2. **从模板开始**：
   - `templates/hello-orb-flow.html`——文本绕移动球体重排（绕障碍物重排模式）
   - `templates/donut-orbit.html`——进阶示例：测量过的 ASCII 标志障碍、可拖动的线框球体/立方体、变形形状场、可选的 DOM 文本以及仅开发用控件
   - 使用 `write_file` 写入 `/tmp/` 或用户工作区的新 `.html` 文件。
3. **将语料替换为与需求相关的用心内容。** 真实散文，10-100 句，无 lorem。
4. **调整审美**——字体、调色板、构图、交互。这是核心工作，不要跳过。
5. **本地验证**：
   ```sh
   cd <dir-with-html> && python3 -m http.server 8765
   # 然后打开 http://localhost:8765/<file>.html
   ```
6. **检查控制台**——如果用错误的字体字符串调用 `prepareWithSegments`，pretext 会抛出错误；所有现代浏览器都支持 `Intl.Segmenter`。
7. **向用户展示文件路径**，而不仅仅是代码——他们想打开它。

## 性能注意事项

- `prepare()` / `prepareWithSegments()` 是昂贵的调用。对每个文本+字体对**只调用一次**。缓存句柄。
- 调整大小时，只重新运行 `layout()` / `layoutWithLines()`——绝不重新 prepare。
- 对于文本不变但几何变化的逐帧动画，在紧密循环中使用 `layoutNextLineRange` 对于正常长度的段落而言，在 60fps 下足够轻量。
- 每帧渲染 ASCII 遮罩时，保留一个单元格缓冲区（`Uint8Array`/类型数组），从单元格或投影几何推导出按行测量的障碍跨度，合并跨度，然后将这些跨度提供给 `layoutNextLineRange` 再绘制文本。
- 保持视觉动画和布局动画耦合。如果一个球体变形为立方体，使用相同的值对渲染的单元格缓冲区和障碍跨度进行补间；否则演示看起来像是画上去的，而非物理重排。
- 淡入淡出时，优先使用图层透明度，而非改变字形强度或障碍物缩放。将临时 ASCII 精灵放在独立的 canvas 上，并通过 CSS/GSAP 透明度淡入淡出，这样几何图形不会看起来缩小。
- Canvas 的 `ctx.font` 设置出人意料地慢；如果字体不变，**每帧只设置一次**，而不是每次调用 `fillText` 都设置。

## 常见陷阱

1. **CSS/Canvas 字体字符串不一致。** 用 `ctx.font = "16px Inter"` 测量，但 CSS 写的是 `font-family: Inter, sans-serif; font-size: 16px`。如果 Inter 加载成功则没事。如果 Inter 404，CSS 回退到 sans-serif，测量会偏移 5-20%。始终 `preload` 字体或使用网络安全家族。

2. **在动画循环中重新 prepare。** 只有 `layout*` 是廉价的。每帧重新调用 `prepare` 会严重拖慢性能。将 prepare 的句柄保持在模块作用域。

3. **忘记使用 `Intl.Segmenter` 进行字素分割。** Emoji、组合标记、CJK——`"é".split("")` 会得到两个字符。在采样单个可见字形时使用 `new Intl.Segmenter(undefined, { granularity: "grapheme" })`。

4. **没有 `extraWidth` 的 `break: 'never'` 块。** 在 `rich-inline` 中，如果对原子标签/提及使用 `break: 'never'`，还必须提供 `extraWidth` 用于药丸状填充——否则标签饰边会溢出容器。

5. **从 `unpkg` 使用 `@chenglou/pretext` 但入口是 TypeScript 专用。** 使用 `esm.sh`——它会自动将 TS 导出编译为浏览器可用的 ESM。`unpkg` 会返回 404 或提供原始 TS。

6. **等宽回退在静默中抹去了全部意义。** 用户看到等宽输出时，往往是 CSS 的 `font-family` 回退到了 `monospace`。通过 DevTools 验证实际渲染的字体。

7. **绕形状流动时跳过行与调整宽度的混淆。** 如果当前行的走廊太窄无法容纳一行，**跳过该行**（`y += lineHeight; continue;`），而不是向 `layoutNextLineRange` 传递一个极小的 maxWidth——pretext 会返回单字素的行，看起来是断裂的。

8. **交付一个“冷”演示。** 默认的首屏看起来像教程水平。添加：暗角、微妙的扫描线、空闲自动动画、一个精心选择的交互响应（拖拽、悬停、滚动、点击）。没有这些，“酷炫 pretext 演示”就会变成“README 的实习复制品”。

## 验证清单

- [ ] 演示是一个独立的 `.html` 文件——可以通过双击或 `python3 -m http.server` 打开
- [ ] `@chenglou/pretext` 通过 `esm.sh` 导入并固定版本
- [ ] 语料是真实散文，不是 lorem ipsum，并与演示概念相符
- [ ] 传给 `prepare` 的字体字符串与 CSS 字体完全一致
- [ ] `prepare()` / `prepareWithSegments()` 只调用一次，而非每帧
- [ ] 深色背景 + 考究的调色板——而非默认的白色画布
- [ ] 至少一个交互响应（拖拽 / 悬停 / 滚动 / 点击）或空闲自动动画
- [ ] 在本地使用 `python3 -m http.server` 测试，并确认控制台无错误
- [ ] 在中档笔记本电脑上达到 60fps（或记录了优雅降级）
- [ ] 包含一个用户没要求的“额外”细节

## 参考：社区演示

克隆这些以获取灵感/模式（全部为 MIT 许可证，链接自 [pretext.cool](https://www.pretext.cool/)）：

- **Pretext Breaker** —— 用单词砖块打砖块 —— `github.com/rinesh/pretext-breaker`
- **Tetris × Pretext** —— `github.com/shinichimochizuki/tetris-pretext`
- **龙动画** —— `github.com/qtakmalay/PreTextExperiments`
- **Somnai 编辑引擎** —— `github.com/somnai-dreams/pretext-demos`
- **Bad Apple!! ASCII** —— `github.com/frmlinn/bad-apple-pretext`
- **拖拽精灵重排** —— `github.com/dokobot/pretext-demo`
- **Alarmy 编辑时钟** —— `github.com/SmisLee/alarmy-pretext-demo`

官方游乐场：[chenglou.me/pretext](https://chenglou.me/pretext/) —— 手风琴、气泡、动态布局、编辑引擎、对齐比较、瀑布流、Markdown 聊天、富笔记。