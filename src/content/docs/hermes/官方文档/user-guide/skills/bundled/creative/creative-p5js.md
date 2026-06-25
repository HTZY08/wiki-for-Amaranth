---
title: P5Js
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# P5Js

p5.js 草图：生成艺术、着色器、交互、3D。

## 技能元数据（Skill metadata）

| | |
|---|---|
| 来源（Source） | 内置（默认安装） |
| 路径（Path） | `skills/creative/p5js` |
| 版本（Version） | `1.0.0` |
| 平台（Platforms） | linux, macos, windows |
| 标签（Tags） | `creative-coding`, `generative-art`, `p5js`, `canvas`, `interactive`, `visualization`, `webgl`, `shaders`, `animation` |
| 相关技能（Related skills） | [`ascii-video`](/docs/user-guide/skills/bundled/creative/creative-ascii-video), [`manim-video`](/docs/user-guide/skills/bundled/creative/creative-manim-video), [`excalidraw`](/docs/user-guide/skills/bundled/creative/creative-excalidraw) |

## 参考：完整 SKILL.md

:::info
以下为 Hermes 在触发该技能时加载的完整技能定义。这是代理在技能激活时看到的指令。
:::

# p5.js 生产管线（Production Pipeline）

## 何时使用

当用户请求如下内容时使用：p5.js 草图、创意编码（creative coding）、生成艺术（generative art）、交互式可视化、画布动画、浏览器视觉艺术、数据可视化、着色器效果，或任何 p5.js 项目。

## 包含内容

使用 p5.js 进行交互式和生成式视觉艺术的生产管线。创建基于浏览器的草图、生成艺术、数据可视化、交互体验、3D 场景、音频响应式视觉和动态图形——导出为 HTML、PNG、GIF、MP4 或 SVG。涵盖：2D/3D 渲染、噪声（noise）与粒子系统、流场、着色器（GLSL）、像素操作、动态字体（kinetic typography）、WebGL 场景、音频分析、鼠标/键盘交互以及无头高分辨率导出。

## 创作标准（Creative Standard）

这是在浏览器中渲染的视觉艺术。画布是媒介；算法是画笔。

**在编写任何代码之前**，先阐述创意概念。这件作品传达了什么意思？是什么让观众停止滚动？它与代码教程中的示例有何不同？用户的提示是起点——用创意雄心去诠释它。

**首次渲染即优秀是不容妥协的。** 输出必须在首次加载时视觉上引人注目。如果它看起来像 p5.js 教程练习、默认配置或“AI 生成的创意编码”，那就是错误的。在交付前重新思考。

**超越参考词汇。** 参考资料中的噪声函数、粒子系统、调色板（color palette）和着色器效果只是起点词汇表。对于每个项目，要进行组合、分层和创造。目录是颜料调色板——你负责绘制画作。

**主动发挥创造力。** 如果用户要求“一个粒子系统”，就交付一个具有涌现的群集行为、拖尾残影、调色深度雾以及呼吸的背景噪声场的粒子系统。至少包含一个用户没有要求但会欣赏的视觉细节。

**密集、分层、深思熟虑。** 每一帧都应值得观看。永远不要用纯白色背景。始终要有构图层次。始终要有有意的颜色选择。始终要有只有在近距离观察时才会显现的微观细节。

**统一美学胜过功能数量。** 所有元素必须服务于统一的视觉语言——共享色温、一致的描边粗细词汇、协调的运动速度。一个拥有十个无关效果的草图，不如一个有三位一体效果的草图。

## 模式（Modes）

| 模式（Mode） | 输入（Input） | 输出（Output） | 参考（Reference） |
|------|-------|--------|-----------|
| **生成艺术** | 种子 / 参数 | 程序化视觉构成（静态或动画） | `references/visual-effects.md` |
| **数据可视化** | 数据集 / API | 交互式图表、图形、自定义数据展示 | `references/interaction.md` |
| **交互体验** | 无（用户驱动） | 鼠标/键盘/触控驱动的草图 | `references/interaction.md` |
| **动画 / 动态图形** | 时间线 / 故事板 | 定时序列、动态字体、过渡 | `references/animation.md` |
| **3D 场景** | 概念描述 | WebGL 几何体、光照、相机、材质 | `references/webgl-and-3d.md` |
| **图像处理** | 图像文件 | 像素操作、滤镜、马赛克、点彩 | `references/visual-effects.md` § 像素操作 |
| **音频响应** | 音频文件 / 麦克风 | 声音驱动的生成式视觉 | `references/interaction.md` § 音频输入 |

## 技术栈（Stack）

每个项目一个独立的 HTML 文件。无需构建步骤。

| 层（Layer） | 工具（Tool） | 目的（Purpose） |
|-------|------|---------|
| 核心（Core） | p5.js 1.11.3 (CDN) | 画布渲染、数学运算、变换、事件处理 |
| 3D | p5.js WebGL 模式 | 3D 几何体、相机、光照、GLSL 着色器 |
| 音频（Audio） | p5.sound.js (CDN) | FFT 分析、振幅、麦克风输入、振荡器 |
| 导出（Export） | 内置 `saveCanvas()` / `saveGif()` / `saveFrames()` | PNG、GIF、帧序列输出 |
| 捕获（Capture） | CCapture.js (可选) | 确定性帧率视频捕获（WebM、GIF） |
| 无头（Headless） | Puppeteer + Node.js (可选) | 自动高分辨率渲染，通过 ffmpeg 输出 MP4 |
| SVG | p5.js-svg 1.6.0 (可选) | 用于印刷的矢量输出——需要 p5.js 1.x |
| 自然媒体（Natural media） | p5.brush (可选) | 水彩、炭笔、钢笔——需要 p5.js 2.x + WEBGL |
| 纹理（Texture） | p5.grain (可选) | 胶片颗粒、纹理叠加 |
| 字体（Fonts） | Google Fonts / `loadFont()` | 通过 OTF/TTF/WOFF2 自定义排版 |

### 版本说明（Version Note）

**p5.js 1.x** (1.11.3) 是默认版本——稳定、文档完善、库兼容性最广。在项目不需要 2.x 特性时使用。

**p5.js 2.x** (2.2+) 新增：`async setup()` 取代 `preload()`、OKLCH/OKLAB 色彩模式、`splineVertex()`、着色器 `.modify()` API、可变字体（variable fonts）、`textToContours()`、指针事件（pointer events）。p5.brush 需要此版本。参见 `references/core-api.md` § p5.js 2.0。

## 管线（Pipeline）

每个项目遵循相同的 6 个阶段路径：

```
CONCEPT → DESIGN → CODE → PREVIEW → EXPORT → VERIFY
```

1. **概念（CONCEPT）** — 阐述创意愿景：氛围、色彩世界、运动词汇、独特之处
2. **设计（DESIGN）** — 选择模式、画布大小、交互模型、色彩系统、导出格式。将概念映射到技术决策
3. **编码（CODE）** — 编写包含内联 p5.js 的单个 HTML 文件。结构：全局变量 → `preload()` → `setup()` → `draw()` → 辅助函数 → 类 → 事件处理器
4. **预览（PREVIEW）** — 在浏览器中打开，验证视觉质量。在目标分辨率下测试。检查性能
5. **导出（EXPORT）** — 捕获输出：使用 `saveCanvas()` 导出 PNG、`saveGif()` 导出 GIF、`saveFrames()` + ffmpeg 导出 MP4、Puppeteer 进行无头批量导出
6. **验证（VERIFY）** — 输出是否与概念相符？在预期的显示尺寸下视觉上是否引人注目？你会装裱它吗？

## 创作方向（Creative Direction）

### 美学维度（Aesthetic Dimensions）

| 维度（Dimension） | 选项（Options） | 参考（Reference） |
|-----------|---------|-----------|
| **色彩系统（Color system）** | HSB/HSL、RGB、命名调色板、程序化和谐、渐变插值 | `references/color-systems.md` |
| **噪声词汇（Noise vocabulary）** | Perlin 噪声、simplex 噪声、分形（八度）、域扭曲（domain warping）、curl 噪声 | `references/visual-effects.md` § 噪声 |
| **粒子系统（Particle systems）** | 基于物理、群集、轨迹绘制、吸引子驱动、流场跟随 | `references/visual-effects.md` § 粒子 |
| **形状语言（Shape language）** | 几何基元、自定义顶点、贝塞尔曲线、SVG 路径 | `references/shapes-and-geometry.md` |
| **运动风格（Motion style）** | 缓动、基于弹簧、噪声驱动、物理模拟、lerp、步进 | `references/animation.md` |
| **排版（Typography）** | 系统字体、加载的 OTF、`textToPoints()` 粒子文本、动态 | `references/typography.md` |
| **着色器效果（Shader effects）** | GLSL 片元/顶点、滤镜着色器、后期处理、反馈循环 | `references/webgl-and-3d.md` § 着色器 |
| **构图（Composition）** | 网格、径向、黄金比例、三分法、有机散布、平铺 | `references/core-api.md` § 构图 |
| **交互模型（Interaction model）** | 鼠标跟随、点击生成、拖拽、键盘状态、滚动驱动、麦克风输入 | `references/interaction.md` |
| **混合模式（Blend modes）** | `BLEND`、`ADD`、`MULTIPLY`、`SCREEN`、`DIFFERENCE`、`EXCLUSION`、`OVERLAY` | `references/color-systems.md` § 混合模式 |
| **分层（Layering）** | `createGraphics()` 屏幕外缓冲区、alpha 合成、遮罩 | `references/core-api.md` § 屏幕外缓冲区 |
| **纹理（Texture）** | Perlin 表面、点画、影线、半色调、像素排序 | `references/visual-effects.md` § 纹理生成 |

### 每个项目的变异规则（Per-Project Variation Rules）

永远不要使用默认配置。对于每个项目：
- **自定义调色板** — 永远不要用原始的 `fill(255, 0, 0)`。始终使用包含 3-7 种颜色设计的调色板
- **自定义描边粗细词汇** — 细强调（0.5）、中等结构（1-2）、粗强调（3-5）
- **背景处理** — 永远不要用纯 `background(0)` 或 `background(255)`。始终是纹理化、渐变或分层的
- **运动多样性** — 不同元素具有不同的速度。主要元素 1 倍速，次要 0.3 倍速，环境 0.1 倍速
- **至少一个发明元素** — 自定义粒子行为、新颖的噪声应用、独特的交互响应

### 项目特定发明（Project-Specific Invention）

对于每个项目，至少发明其中之一：
- 与氛围匹配的自定义调色板（非预设）
- 新颖的噪声场组合（例如 curl 噪声 + 域扭曲 + 反馈）
- 独特的粒子行为（自定义力、自定义轨迹、自定义生成）
- 用户未请求但能提升作品的交互机制
- 创造视觉层次的构图技巧

### 参数设计哲学（Parameter Design Philosophy）

参数应从算法中产生，而非来自通用菜单。问问自己：“这个系统的哪些属性应该是可调的？”

**好的参数** 暴露了算法的特征：
- **数量** — 多少粒子、分支、细胞（控制密度）
- **比例** — 噪声频率、元素大小、间距（控制纹理）
- **速率** — 速度、生长速率、衰减（控制能量）
- **阈值** — 行为何时改变？（控制戏剧性）
- **比率** — 比例、力之间的平衡（控制和谐）

**坏的参数** 是与算法无关的通用控制项：
- “color1”、“color2”、“size” — 脱离上下文毫无意义
- 开关无关效果
- 只改变外观而不改变行为的参数

每个参数都应改变算法的“思考”方式，而不仅仅是“外观”。一个改变噪声八度数的“湍流（turbulence）”参数是好的。一个只改变 `ellipse()` 半径的“粒子大小”滑块是浅薄的。

## 工作流程（Workflow）

### 步骤 1：创意愿景（Creative Vision）

在任何代码之前，阐明：

- **情绪 / 氛围**：观众应该感受什么？沉思？充满活力？不安？好玩？
- **视觉故事**：随时间（或通过交互）会发生什么？构建？衰减？变换？振荡？
- **色彩世界**：暖色/冷色？单色？互补？主色调是什么？强调色是什么？
- **形状语言**：有机曲线？锐利几何？点？线？混合？
- **运动词汇**：缓慢漂移？爆发式喷射？呼吸脉动？机械精度？
- **这个作品的不同之处**：是什么让这个草图独一无二？

将用户的提示映射到美学选择。“放松的生成背景”与“故障数据可视化”所需的一切都不同。

### 步骤 2：技术设计（Technical Design）

- **模式** — 上面表格中的 7 种模式之一
- **画布大小** — 横屏 1920x1080、竖屏 1080x1920、方形 1080x1080 或自适应 `windowWidth/windowHeight`
- **渲染器** — `P2D`（默认）或 `WEBGL`（用于 3D、着色器、高级混合模式）
- **帧率** — 60fps（交互式）、30fps（环境动画）或 `noLoop()`（静态生成）
- **导出目标** — 浏览器显示、PNG 静态图、GIF 循环、MP4 视频、SVG 矢量
- **交互模型** — 被动（无输入）、鼠标驱动、键盘驱动、音频响应、滚动驱动
- **查看器 UI** — 对于交互式生成艺术，从 `templates/viewer.html` 开始，它提供种子导航、参数滑块和下载。对于简单草图或视频导出，使用纯 HTML

### 步骤 3：编码草图（Code the Sketch）

对于**交互式生成艺术**（种子探索、参数调整）：从 `templates/viewer.html` 开始。先阅读模板，保留固定部分（种子导航、操作），替换算法和参数控制。这样就为用户提供了种子上一张/下一张/随机/跳转、带实时更新的参数滑块以及 PNG 下载——全部已连接好。

对于**动画、视频导出或简单草图**：使用纯 HTML：

单 HTML 文件。结构：

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>项目名称</title>
  <script>p5.disableFriendlyErrors = true;</script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.11.3/p5.min.js"></script>
  <!-- <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.11.3/addons/p5.sound.min.js"></script> -->
  <!-- <script src="https://unpkg.com/p5.js-svg@1.6.0"></script> -->  <!-- SVG 导出 -->
  <!-- <script src="https://cdn.jsdelivr.net/npm/ccapture.js-npmfixed/build/CCapture.all.min.js"></script> -->  <!-- 视频捕获 -->
  <style>
    html, body { margin: 0; padding: 0; overflow: hidden; }
    canvas { display: block; }
  </style>
</head>
<body>
<script>
// === 配置（Configuration） ===
const CONFIG = {
  seed: 42,
  // ... 项目特定参数
};

// === 调色板（Color Palette） ===
const PALETTE = {
  bg: '#0a0a0f',
  primary: '#e8d5b7',
  // ...
};

// === 全局状态（Global State） ===
let particles = [];

// === 预加载（Preload，字体、图片、数据） ===
function preload() {
  // font = loadFont('...');
}

// === 设置（Setup） ===
function setup() {
  createCanvas(1920, 1080);
  randomSeed(CONFIG.seed);
  noiseSeed(CONFIG.seed);
  colorMode(HSB, 360, 100, 100, 100);
  // 初始化状态...
}

// === 绘制循环（Draw Loop） ===
function draw() {
  // 渲染帧...
}

// === 辅助函数（Helper Functions） ===
// ...

// === 类（Classes） ===
class Particle {
  // ...
}

// === 事件处理器（Event Handlers） ===
function mousePressed() { /* ... */ }
function keyPressed() { /* ... */ }
function windowResized() { resizeCanvas(windowWidth, windowHeight); }
</script>
</body>
</html>
```

关键实现模式：
- **种子随机性（Seeded randomness）**：始终使用 `randomSeed()` + `noiseSeed()` 以确保可复现性
- **色彩模式（Color mode）**：使用 `colorMode(HSB, 360, 100, 100, 100)` 实现直观的颜色控制
- **状态分离（State separation）**：CONFIG 用于参数，PALETTE 用于颜色，全局变量用于可变状态
- **基于类的实体（Class-based entities）**：粒子、代理、形状作为类，包含 `update()` + `display()` 方法
- **屏幕外缓冲区（Offscreen buffers）**：使用 `createGraphics()` 进行分层合成、轨迹、遮罩

### 步骤 4：预览与迭代（Preview & Iterate）

- 直接在浏览器中打开 HTML 文件——基本草图无需服务器
- 对于本地文件的 `loadImage()`/`loadFont()`：使用 `scripts/serve.sh` 或 `python3 -m http.server`
- 使用 Chrome DevTools 的 Performance 标签验证 60fps
- 在目标导出分辨率下测试，而不仅仅是窗口大小
- 调整参数，直到视觉效果匹配步骤 1 中的概念

### 步骤 5：导出（Export）

| 格式（Format） | 方法（Method） | 命令（Command） |
|--------|--------|---------|
| **PNG** | 在 `keyPressed()` 中调用 `saveCanvas('output', 'png')` | 按 's' 键保存 |
| **高分辨率 PNG** | Puppeteer 无头捕获 | `node scripts/export-frames.js sketch.html --width 3840 --height 2160 --frames 1` |
| **GIF** | `saveGif('output', 5)` — 捕获 N 秒 | 按 'g' 键保存 |
| **帧序列（Frame sequence）** | `saveFrames('frame', 'png', 10, 30)` — 10 秒，30fps | 然后 `ffmpeg -i frame-%04d.png -c:v libx264 output.mp4` |
| **MP4** | Puppeteer 帧捕获 + ffmpeg | `bash scripts/render.sh sketch.html output.mp4 --duration 30 --fps 30` |
| **SVG** | `createCanvas(w, h, SVG)` 配合 p5.js-svg | `save('output.svg')` |

### 步骤 6：质量验证（Quality Verification）

- **是否与愿景相符？** 将输出与创意概念进行比较。如果看起来很普通，请回到步骤 1
- **分辨率检查**：在目标显示尺寸下是否锐利？没有锯齿伪影？
- **性能检查**：在浏览器中是否保持 60fps？（动画至少 30fps）
- **颜色检查**：颜色是否协调？在亮色和暗色显示器上测试
- **边界情况**：在画布边缘会发生什么？调整大小时？运行 10 分钟后？

## 关键实现说明（Critical Implementation Notes）

### 性能——先禁用 FES

友好错误系统（Friendly Error System，FES）会增加高达 10 倍的开销。在每个生产草图中禁用它：

```javascript
p5.disableFriendlyErrors = true;  // 在 setup() 之前

function setup() {
  pixelDensity(1);  // 防止在 retina 上 2x-4x 过度绘制
  createCanvas(1920, 1080);
}
```

在热循环中（粒子、像素操作），使用 `Math.*` 而不是 p5 的包装器——明显更快：

```javascript
// 在 draw() 或 update() 的热路径中：
let a = Math.sin(t);          // 不要用 sin(t)
let r = Math.sqrt(dx*dx+dy*dy); // 不要用 dist() —— 或更好：跳过 sqrt，比较 magSq
let v = Math.random();        // 不要用 random() —— 当不需要种子时
let m = Math.min(a, b);       // 不要用 min(a, b)
```

永远不要在 `draw()` 中 `console.log()`。永远不要在 `draw()` 中操作 DOM。参见 `references/troubleshooting.md` § 性能。

### 种子随机性——始终如此

每个生成式草图必须可复现。相同种子，相同输出。

```javascript
function setup() {
  randomSeed(CONFIG.seed);
  noiseSeed(CONFIG.seed);
  // 所有 random() 和 noise() 调用现在都是确定性的
}
```

切勿将 `Math.random()` 用于生成式内容——仅用于性能关键的非视觉代码。始终使用 `random()` 处理视觉元素。如果需要随机种子：`CONFIG.seed = floor(random(99999))`。

### 生成艺术平台支持（fxhash / Art Blocks）

对于生成艺术平台，将 p5 的 PRNG 替换为平台的确定性随机：

```javascript
// fxhash 约定
const SEED = $fx.hash;              // 每次铸造（mint）唯一
const rng = $fx.rand;               // 确定性 PRNG
$fx.features({ palette: 'warm', complexity: 'high' });

// 在 setup() 中：
randomSeed(SEED);   // 用于 p5 的 noise()
noiseSeed(SEED);

// 用 rng() 替换 random() 以实现平台确定性
let x = rng() * width;  // 而不是 random(width)
```

参见 `references/export-pipeline.md` § 平台导出。

### 色彩模式——使用 HSB

HSB（色调、饱和度、明度）比 RGB 更容易用于生成艺术：

```javascript
colorMode(HSB, 360, 100, 100, 100);
// 现在：fill(hue, sat, bri, alpha)
// 旋转色调：fill((baseHue + offset) % 360, 80, 90)
// 降低饱和度：fill(hue, sat * 0.3, bri)
// 变暗：fill(hue, sat, bri * 0.5)
```

永远不要硬编码原始 RGB 值。定义一个调色板对象，程序化地派生变体。参见 `references/color-systems.md`。

### 噪声——多八度，而非原始

原始的 `noise(x, y)` 看起来像平滑的斑点。叠加八度以获得自然纹理：

```javascript
function fbm(x, y, octaves = 4) {
  let val = 0, amp = 1, freq = 1, sum = 0;
  for (let i = 0; i < octaves; i++) {
    val += noise(x * freq, y * freq) * amp;
    sum += amp;
    amp *= 0.5;
    freq *= 2;
  }
  return val / sum;
}
```

对于流动的有机形态，使用**域扭曲（domain warping）**：将噪声输出作为坐标输入到噪声中。参见 `references/visual-effects.md`。

### createGraphics() 用于分层——非可选

平坦的单遍渲染看起来平淡。使用屏幕外缓冲区进行合成：

```javascript
let bgLayer, fgLayer, trailLayer;
function setup() {
  createCanvas(1920, 1080);
  bgLayer = createGraphics(width, height);
  fgLayer = createGraphics(width, height);
  trailLayer = createGraphics(width, height);
}
function draw() {
  renderBackground(bgLayer);
  renderTrails(trailLayer);   // 持久，渐隐
  renderForeground(fgLayer);  // 每帧清除
  image(bgLayer, 0, 0);
  image(trailLayer, 0, 0);
  image(fgLayer, 0, 0);
}
```

### 性能——尽可能矢量化

p5.js 的 draw 调用开销大。对于数千个粒子：

```javascript
// 慢：单独的形状
for (let p of particles) {
  ellipse(p.x, p.y, p.size);
}

// 快：使用 beginShape() 的单个形状
beginShape(POINTS);
for (let p of particles) {
  vertex(p.x, p.y);
}
endShape();

// 最快：针对大量计数的像素缓冲区
loadPixels();
for (let p of particles) {
  let idx = 4 * (floor(p.y) * width + floor(p.x));
  pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 255;
}
updatePixels();
```

参见 `references/troubleshooting.md` § 性能。

### 多草图的实例模式（Instance Mode）

全局模式会污染 `window`。对于生产环境，使用实例模式：

```javascript
const sketch = (p) => {
  p.setup = function() {
    p.createCanvas(800, 800);
  };
  p.draw = function() {
    p.background(0);
    p.ellipse(p.mouseX, p.mouseY, 50);
  };
};
new p5(sketch, 'canvas-container');
```

当在一页中嵌入多个草图或与框架集成时需要。

### WebGL 模式注意事项（Gotchas）

- `createCanvas(w, h, WEBGL)` — 原点在中心，而非左上角
- Y 轴反转（在 WEBGL 中 Y 正方向向上，P2D 中向下）
- `translate(-width/2, -height/2)` 以获得类似 P2D 的坐标
- 每次变换后使用 `push()`/`pop()` — 矩阵栈会静默溢出
- `texture()` 在 `rect()`/`plane()` 之前——而不是之后
- 自定义着色器：`createShader(vert, frag)` — 在多个浏览器上测试

### 导出——快捷键约定

每个草图应在 `keyPressed()` 中包含以下内容：

```javascript
function keyPressed() {
  if (key === 's' || key === 'S') saveCanvas('output', 'png');
  if (key === 'g' || key === 'G') saveGif('output', 5);
  if (key === 'r' || key === 'R') { randomSeed(millis()); noiseSeed(millis()); }
  if (key === ' ') CONFIG.paused = !CONFIG.paused;
}
```

### 无头视频导出——使用 noLoop()

对于通过 Puppeteer 进行无头渲染，草图**必须**在 setup 中使用 `noLoop()`。如果没有，p5 的绘制循环会在截图缓慢时自由运行——草图会超前，导致帧跳过/重复。

```javascript
function setup() {
  createCanvas(1920, 1080);
  pixelDensity(1);
  noLoop();                    // 捕获脚本控制帧推进
  window._p5Ready = true;      // 通知捕获脚本已就绪
}
```

内置的 `scripts/export-frames.js` 检测 `_p5Ready`，并在每次捕获时调用一次 `redraw()`，实现精确的 1:1 帧对应。参见 `references/export-pipeline.md` § 确定性捕获。

对于多场景视频，使用每片段（per-clip）架构：每个场景一个 HTML，独立渲染，使用 `ffmpeg -f concat` 拼接。参见 `references/export-pipeline.md` § 每片段架构。

### 代理工作流程（Agent Workflow）

在构建 p5.js 草图时：

1. **编写 HTML 文件** — 单个自包含文件，所有代码内联
2. **在浏览器中打开** — `open sketch.html`（macOS）或 `xdg-open sketch.html`（Linux）
3. **本地资产**（字体、图片）需要服务器：在项目目录中运行 `python3 -m http.server 8080`，然后打开 `http://localhost:8080/sketch.html`
4. **导出 PNG/GIF** — 添加上面所示的 `keyPressed()` 快捷键，告诉用户按哪个键
5. **无头导出** — `node scripts/export-frames.js sketch.html --frames 300` 用于自动帧捕获（草图必须使用 `noLoop()` + `_p5Ready`）
6. **MP4 渲染** — `bash scripts/render.sh sketch.html output.mp4 --duration 30`
7. **迭代优化** — 编辑 HTML 文件，用户刷新浏览器以查看更改
8. **按需加载参考** — 在实现过程中需要使用特定参考文件时，使用 `skill_view(name="p5js", file_path="references/...")` 加载

## 性能目标（Performance Targets）

| 指标（Metric） | 目标（Target） |
|--------|--------|
| 帧率（交互式） | 持续 60fps |
| 帧率（动画导出） | 最低 30fps |
| 粒子数（P2D 形状） | 5000-10000 个，60fps |
| 粒子数（像素缓冲区） | 50000-100000 个，60fps |
| 画布分辨率 | 最高 3840x2160（导出），1920x1080（交互式） |
| 文件大小（HTML） | &lt; 100KB（不包括 CDN 库） |
| 加载时间 | &lt; 2 秒到第一帧 |

## 参考文件（References）

| 文件（File） | 内容（Contents） |
|------|----------|
| `references/core-api.md` | 画布设置、坐标系、绘制循环、`push()`/`pop()`、屏幕外缓冲区、构图模式、`pixelDensity()`、响应式设计 |
| `references/shapes-and-geometry.md` | 2D 基元、`beginShape()`/`endShape()`、贝塞尔/Catmull-Rom 曲线、`vertex()` 系统、自定义形状、`p5.Vector`、有符号距离场、SVG 路径转换 |
| `references/visual-effects.md` | 噪声（Perlin、分形、域扭曲、curl）、流场、粒子系统（物理、群集、轨迹）、像素操作、纹理生成（点画、影线、半色调）、反馈循环、反应-扩散 |
| `references/animation.md` | 基于帧的动画、缓动函数、`lerp()`/`map()`、弹簧物理、状态机、时间线序列、`millis()` 计时、过渡模式 |
| `references/typography.md` | `text()`、`loadFont()`、`textToPoints()`、动态字体、文字遮罩、字体度量、响应式文字大小 |
| `references/color-systems.md` | `colorMode()`、HSB/HSL/RGB、`lerpColor()`、`paletteLerp()`、程序化调色板、色彩和谐、`blendMode()`、渐变渲染、精选调色板库 |
| `references/webgl-and-3d.md` | WEBGL 渲染器、3D 基元、相机、光照、材质、自定义几何体、GLSL 着色器（`createShader()`、`createFilterShader()`）、帧缓冲、后期处理 |
| `references/interaction.md` | 鼠标事件、键盘状态、触摸输入、DOM 元素、`createSlider()`/`createButton()`、音频输入（p5.sound FFT/振幅）、滚动驱动动画、响应式事件 |
| `references/export-pipeline.md` | `saveCanvas()`、`saveGif()`、`saveFrames()`、确定性无头捕获、ffmpeg 帧转视频、CCapture.js、SVG 导出、每片段架构、平台导出（fxhash）、视频注意事项 |
| `references/troubleshooting.md` | 性能分析、每像素预算、常见错误、浏览器兼容性、WebGL 调试、字体加载问题、像素密度陷阱、内存泄漏、CORS |
| `templates/viewer.html` | 交互式查看器模板：种子导航（上一张/下一张/随机/跳转）、参数滑块、下载 PNG、响应式画布。从此开始创建可探索的生成艺术 |

---

--- body ---
## 创意发散（Creative Divergence，仅在用户请求实验性/创造性/独特输出时使用）

如果用户要求创造性、实验性、出人意料或非常规的输出，请选择最合适的策略，并在生成代码之前推理其步骤。

- **概念融合（Conceptual Blending）** — 当用户提及要组合的两个事物或想要混合美学时
- **SCAMPER** — 当用户希望在已知生成艺术模式上添加变化时
- **距离联想（Distance Association）** — 当用户给出单个概念并希望进行探索时（“制作一个关于时间的东西”）

### 概念融合（Conceptual Blending）
1. 命名两个不同的视觉系统（例如，粒子物理学 + 手写体）
2. 映射对应关系（粒子 = 墨滴，力 = 笔压，场 = 字形）
3. 选择性融合——保留能产生有趣涌现视觉的映射
4. 将融合编码为一个统一的系统，而不是两个并排的系统

### SCAMPER 变换（SCAMPER Transformation）
取一个已知的生成模式（流场、粒子系统、L-system、元胞自动机）并系统性地变换它：
- **替换（Substitute）**：将圆替换为文字字符，将线替换为渐变
- **组合（Combine）**：合并两个模式（流场 + voronoi）
- **调整（Adapt）**：将 2D 模式应用于 3D 投影
- **修改（Modify）**：夸大比例，扭曲坐标空间
- **改变用途（Purpose）**：将物理模拟用于排版，将排序算法用于颜色
- **消除（Eliminate）**：移除网格，移除颜色，移除对称性
- **反转（Reverse）**：反向运行模拟，反转参数空间

### 距离联想（Distance Association）
1. 锚定在用户的概念上（例如，“孤独”）
2. 在三个距离上生成联想：
   - 近（明显的）：空房间、单独人物、沉默
   - 中（有趣的）：鱼群中一条游错方向的鱼、没有通知的手机、地铁车厢之间的缝隙
   - 远（抽象的）：质数、渐近曲线、凌晨3点的颜色
3. 发展中等距离的联想——它们足够具体以便可视化，但又足够出人意料以引起兴趣