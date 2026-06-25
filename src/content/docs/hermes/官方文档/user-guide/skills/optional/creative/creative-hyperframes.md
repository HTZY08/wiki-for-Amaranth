---
description: 使用超帧（Hyperframes）创建基于HTML的视频合成、动画标题卡、社交媒体覆盖层、带字幕的谈话头视频、音频反应式视觉和着色器过渡。
sidebar_label: 超帧（Hyperframes）
title: 超帧（Hyperframes）
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# 超帧（Hyperframes）

使用超帧（HyperFrames）创建基于HTML的视频合成、动画标题卡、社交媒体覆盖层、带字幕的谈话头视频、音频反应式视觉和着色器过渡。HTML是视频的真实来源（source of truth）。当用户需要从HTML合成渲染的MP4/WebM、希望在媒体上制作文字/标志/图表动画、需要与音频同步的字幕、需要TTS旁白、或将网站转换为视频时使用。

## 技能元数据（Skill metadata）

| | |
|---|---|
| 来源（Source） | 可选（Optional）——使用 `hermes skills install official/creative/hyperframes` 安装 |
| 路径（Path） | `optional-skills/creative/hyperframes` |
| 版本（Version） | `1.0.0` |
| 作者（Author） | heygen-com |
| 许可证（License） | Apache-2.0 |
| 平台（Platforms） | linux, macos, windows |
| 标签（Tags） | `creative`, `video`, `animation`, `html`, `gsap`, `motion-graphics` |
| 相关技能（Related skills） | [`manim-video`](/docs/user-guide/skills/bundled/creative/creative-manim-video), [`meme-generation`](/docs/user-guide/skills/optional/creative/creative-meme-generation) |

## 参考：完整 SKILL.md

:::info
以下是由 Hermes 在触发此技能时加载的完整技能定义。这是代理（Agent）在技能激活时看到的指令。
:::

# 超帧（HyperFrames）

HTML是视频的真实来源。合成（composition）是一个包含用于定时（timing）的 `data-*` 属性、用于动画的 GSAP 时间线和用于外观的 CSS 的 HTML 文件。超帧引擎逐帧捕获页面，并使用 FFmpeg 编码为 MP4/WebM。

**与 `manim-video` 互补：** 对数学/几何解释器（方程式、3B1B风格）使用 `manim-video`。对运动图形、带字幕的谈话头、产品导览、社交媒体覆盖层、着色器过渡以及任何由真实视频/音频媒体驱动的场景使用 `hyperframes`。

## 何时使用

- 用户要求从文本、脚本或网站生成渲染视频
- 动画标题卡、下方三分之一（lower thirds）或排版介绍
- 带字幕的旁白视频（TTS + 字幕与波形同步）
- 音频反应式视觉（节拍同步、频谱条、脉动辉光）
- 场景到场景过渡（淡入淡出、擦除、着色器扭曲、闪白）
- 社交媒体覆盖层（Instagram/TikTok/YouTube风格）
- 网站到视频流水线（捕获URL，生成推广视频）
- 任何必须以确定性方式渲染为视频文件的 HTML/CSS/JS 动画

**不要**使用此技能的场景：
- 纯数学/方程动画（→ `manim-video`）
- 图像生成或梗图（→ `meme-generation`、图像模型）
- 实时视频会议或流媒体

## 快速参考

```bash
npx hyperframes init my-video               # 生成项目结构
cd my-video
npx hyperframes lint                        # 在预览/渲染前验证
npx hyperframes preview                     # 实时重载浏览器预览（端口 3002）
npx hyperframes render --output final.mp4   # 渲染为 MP4
npx hyperframes doctor                      # 诊断环境问题
```

渲染标志：`--quality draft|standard|high` · `--fps 24|30|60` · `--format mp4|webm` · `--docker`（可复现）· `--strict`。

完整 CLI 参考：[references/cli.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/cli.md)。

## 设置（一次性）

```bash
bash "$(dirname "$(find ~/.hermes/skills -path '*/hyperframes/SKILL.md' 2>/dev/null | head -1)")/scripts/setup.sh"
```

该脚本：
1. 检查是否已安装 Node.js >= 22 和 FFmpeg（如果未安装则打印修复说明）。
2. 全局安装 `hyperframes` CLI（`npm install -g hyperframes@>=0.4.2`）。
3. 通过 Puppeteer 预缓存 `chrome-headless-shell`——**需要**通过 Chrome 的 `HeadlessExperimental.beginFrame` 捕获路径实现最佳品质渲染。
4. 运行 `npx hyperframes doctor` 并报告结果。

如果设置失败，请参见 [references/troubleshooting.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/troubleshooting.md)。

## 流程（Procedure）

### 1. 编写HTML之前先规划

在接触代码之前，先在高层阐述：
- **内容**（What）——叙事弧线、关键时刻、情感节拍
- **结构**（Structure）——合成、轨道（视频/音频/覆盖层）、时长
- **视觉标识**（Visual identity）——颜色、字体、动画风格（爆发式/电影感/流畅/技术感）
- **英雄帧**（Hero frame）——对每个场景，最多元素同时可见的时刻。这是你会先构建的静态布局。

**视觉标识门控（硬性门控）。** 在编写任何合成HTML之前，必须定义视觉标识。禁止使用默认或通用颜色（如 `#333`、`#3b82f6`、`Roboto`——如果出现这些，说明此步骤被跳过）编写合成。按顺序检查：

1. **项目根目录下有 `DESIGN.md`？** → 使用其精确的颜色、字体、动效规则以及“不要做什么”约束。
2. **用户指定了风格**（例如“瑞士脉动”、“暗黑科技”、“奢侈品牌”）？ → 生成一个包含 `## 风格提示（Style Prompt）`、`## 颜色（Colors）`（3-5种十六进制颜色及角色）、`## 字体（Typography）`（1-2个字体族）、`## 不要做什么（What NOT to Do）`（3-5个反模式）的最小 `DESIGN.md`。
3. **以上都不是？** → 在编写任何HTML之前先问3个问题：
   - 情绪（Mood）？（爆发式/电影感/流畅/技术感/混乱/温暖）
   - 浅色还是深色画布？
   - 是否有品牌色、字体或视觉参考？

   然后根据答案生成 `DESIGN.md`。每个合成必须将其调色板和字体溯源到 `DESIGN.md` 或用户的明确指示。

### 2. 搭建项目骨架

```bash
npx hyperframes init my-video --non-interactive
```

模板（Templates）：`blank`、`warm-grain`、`play-mode`、`swiss-grid`、`vignelli`、`decision-tree`、`kinetic-type`、`product-promo`、`nyt-graph`。通过 `--example <name>` 选择一个，通过 `--video clip.mp4` 或 `--audio track.mp3` 注入媒体。

### 3. 先布局，后动画

先编写**英雄帧（hero frame）** 的静态 HTML+CSS——尚无 GSAP。`.scene-content` 容器必须填满场景（`width:100%; height:100%; padding:Npx`），使用 `display:flex` + `gap`。使用内边距将内容向内推——永远不要对内容容器使用 `position: absolute; top: Npx`（当内容高于剩余空间时会溢出）。

只有当英雄帧看起来正确后，才添加 `gsap.from()` 入场（动画**到** CSS位置）和 `gsap.to()` 出场（动画**从**该位置出发）。

有关数据属性模式（data-attribute schema）和合成规则的完整信息，请参见 [references/composition.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/composition.md)。

### 4. 使用 GSAP 制作动画

每个合成必须：
- 注册其时间线：`window.__timelines["<composition-id>"] = tl`
- 以暂停状态开始：`gsap.timeline({ paused: true })`——播放器控制回放
- 使用有限的 `repeat` 值（无 `repeat: -1`——会破坏捕获引擎）。计算：`repeat: Math.ceil(duration / cycleDuration) - 1`。
- 具有确定性——不能有 `Math.random()`、`Date.now()` 或时钟逻辑。如果需要伪随机性，使用种子化 PRNG。
- 同步构建——时间线构建时不能有 `async`/`await`、`setTimeout` 或 Promise。

有关核心 GSAP API（补间、缓动、交错、时间线）的信息，请参见 [references/gsap.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/gsap.md)。

### 5. 场景之间的过渡

多场景合成要求使用过渡。规则：
1. **始终在场景之间使用过渡**——无跳剪（jump cuts）。
2. **始终对每个场景元素使用入场动画**（`gsap.from(...)`）。
3. **永远不要使用出场动画**，除了最后一个场景——过渡本身就是出场。
4. 最后一个场景可以淡出。

使用 `npx hyperframes add <transition-name>` 安装着色器过渡（`flash-through-white`、`liquid-wipe` 等）。完整列表：`npx hyperframes add --list`。

### 6. 音频、字幕、TTS、音频反应、高亮

- **音频：** 始终使用独立的 `<audio>` 元素（视频设为 `muted playsinline`）。
- **TTS：** `npx hyperframes tts "脚本文本" --voice af_nova --output narration.wav`。使用 `--list` 列出所有声音。声音 ID 的第一个字母编码语言（`a`/`b`=英语，`e`=西班牙语，`f`=法语，`j`=日语，`z`=中文普通话等）——CLI 会自动推断 phone-mizer 语言环境；只有需要覆盖时传入 `--lang`。非英语音素化需要系统中安装 `espeak-ng`。
- **字幕：** `npx hyperframes transcribe narration.wav` → 单词级转录。根据转录的语气选择风格（hype / corporate / tutorial / storytelling / social——参见 `references/features.md` 中的表格）。**语言规则：** 除非音频确认是英语，否则永远不要使用 `.en` whisper 模型——`.en` 会对非英语音频进行翻译而不是转录。每个字幕组必须在其出场补间之后有一个硬性的 `tl.set(el, { opacity: 0, visibility: "hidden" }, group.end)` 杀尾——否则组会泄漏到后面的组中。
- **音频反应式视觉：** 预先提取音频频段（低音/中音/高音），并在时间线内使用 `for` 循环的 `tl.call(draw, [], f / fps)` 逐帧采样——单个长补间不会对音频做出反应。将低音映射到 `scale`（脉冲），高音映射到 `textShadow`/`boxShadow`（辉光），整体振幅映射到 `opacity`/`y`/`backgroundColor`。避免均衡器条的陈词滥调——让内容引导视觉，音频驱动其行为。
- **标记式高亮：** 用于文本强调的高亮、圆圈、爆发、涂鸦、草图效果是确定性的 CSS+GSAP——参见 `references/features.md#marker-highlighting`。完全可搜索，无需动画 SVG 滤镜。
- **场景过渡：** 每个多场景合成必须使用过渡（无跳剪）。从 CSS 原语（推拉滑、模糊交叉淡入淡出、缩放穿过、交错块）或着色器过渡（`flash-through-white`、`liquid-wipe`、`cross-warp-morph`、`chromatic-split` 等）中选择，通过 `npx hyperframes add` 安装。情绪和能量表位于 `references/features.md#transitions`。不要在同一合成中混用 CSS 和着色器过渡。

### 7. 校验（Lint）、验证（Validate）、检查（Inspect）、预览（Preview）、渲染（Render）

```bash
npx hyperframes lint              # 捕获缺失的 data-composition-id、重叠轨道、未注册的时间线
npx hyperframes validate          # 在5个时间戳上进行 WCAG 对比度审计
npx hyperframes inspect           # 视觉布局审计——溢出、帧外元素、被遮挡的文字
npx hyperframes preview           # 实时浏览器预览
npx hyperframes render --quality draft --output draft.mp4    # 快速迭代
npx hyperframes render --quality high --output final.mp4     # 最终交付
```

`hyperframes validate` 在每个文本元素后面采样背景像素，并在对比度低于 4.5:1（大文本则为 3:1）时发出警告。`hyperframes inspect` 是布局侧辅助工具——在多个时间戳上运行页面，标记静态校验无法看到的问题（例如字幕在 4.5 秒时才超出安全区域的换行、卡片在其标题为最长变体时溢出、元素最终位于过渡着色器后面）。特别是在包含对话气泡、卡片、字幕或紧密排版的合成上运行 `inspect`。

### 8. 网站到视频（如果用户提供 URL）

使用 [references/website-to-video.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/website-to-video.md) 中的 7 步捕获到视频工作流程：捕获 → DESIGN.md → SCRIPT.md → 故事板 → 合成 → 渲染 → 交付。

## 陷阱（Pitfalls）

- **`HeadlessExperimental.beginFrame' wasn't found`** — Chromium 147+ 移除了此协议。确保使用 `hyperframes@>=0.4.2`（自动检测并回退到截图模式）。逃生舱：`export PRODUCER_FORCE_SCREENSHOT=true`。参见 [hyperframes#294](https://github.com/heygen-com/hyperframes/issues/294) 和 [references/troubleshooting.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/troubleshooting.md)。
- **系统 Chrome（非 `chrome-headless-shell`）** — 渲染挂起 120 秒后超时。运行 `npx puppeteer browsers install chrome-headless-shell`（setup.sh 已执行）。`hyperframes doctor` 会报告将使用哪个二进制文件。
- **任何地方出现 `repeat: -1`** — 破坏捕获引擎。始终计算有限的重复次数。
- **对稍后进入的剪辑元素使用 `gsap.set()`** — 该元素在页面加载时不存在。在时间线内部使用 `tl.set(selector, vars, timePosition)`，在或稍后于剪辑的 `data-start` 位置。
- **内容文本中的 `<br>`** — 强制换行不知道渲染的字宽，因此自然换行 + `<br>` 会导致双倍换行。使用 `max-width` 让文本自动换行。例外情况：简短的显示标题，其中每个单词有意单独占一行。
- **对 `visibility` 或 `display` 进行动画** — GSAP 无法对它们进行补间。使用 `autoAlpha`（同时处理可见性和透明度）。
- **调用 `video.play()` 或 `audio.play()`** — 框架拥有播放控制。永远不要自己调用。
- **异步构建时间线** — 捕获引擎在页面加载后同步读取 `window.__timelines`。永远不要将时间线构建包装在 `async`、`setTimeout` 或 Promise 中。
- **包装在 `<template>` 中的独立 `index.html`** — 隐藏了浏览器的所有内容。只有通过 `data-composition-src` 加载的**子合成**才使用 `<template>`。
- **使用视频作为音频** — 始终使用静音 `<video>` + 独立的 `<audio>`。

## 验证（Verification）

在渲染前后：

1. **Lint + Validate + Inspect 通过：** `npx hyperframes lint --strict && npx hyperframes validate && npx hyperframes inspect`（lint 捕获结构问题，validate 捕获对比度问题，inspect 捕获视觉布局/溢出问题——如果出现警告，请参见 troubleshooting.md）。
2. **动画编排（Animation choreography）** — 对于新合成或重大动画更改，运行动画映射。`npx hyperframes init` 将技能脚本复制到项目，因此路径是项目本地路径：
   ```bash
   node skills/hyperframes/scripts/animation-map.mjs <composition-dir> \
     --out <composition-dir>/.hyperframes/anim-map
   ```
   输出一个 `animation-map.json`，包含每个补间的摘要、ASCII 甘特图时间线、交错检测、死区（>1 秒无动画）、元素生命周期和标志（`offscreen`、`collision`、`invisible`、`paced-fast` <0.2s、`paced-slow` >2s）。扫描摘要和标志——修复或证明每个。对小编辑可跳过。
3. **文件存在且非零：** `ls -lh final.mp4`。
4. **时长匹配 `data-duration`：** `ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 final.mp4`。
5. **视觉检查：** 提取合成中间帧：`ffmpeg -i final.mp4 -ss 00:00:05 -vframes 1 preview.png`。
6. **如果需要音频则存在：** `ffprobe -v error -show_streams -select_streams a -of default=nw=1:nk=1 final.mp4 | head -1`。

如果 `hyperframes render` 失败，运行 `npx hyperframes doctor` 并在报告时附上其输出。

## 参考（References）

- [composition.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/composition.md) — 数据属性、时间线合约、不可协商规则、排版/素材规则
- [cli.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/cli.md) — 每个 CLI 命令（init, capture, lint, validate, inspect, preview, render, transcribe, tts, doctor, browser, info, upgrade, benchmark）
- [gsap.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/gsap.md) — HyperFrames 的 GSAP 核心 API（补间、缓动、交错、时间线、matchMedia）
- [features.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/features.md) — 字幕、TTS、音频反应、标记高亮、过渡（按需加载）
- [website-to-video.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/website-to-video.md) — 7 步捕获到视频工作流程
- [troubleshooting.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/troubleshooting.md) — OpenClaw 修复、环境变量、常见渲染错误
```