---
title: Pixel Art
---

title: "像素艺术 — 带有复古时代调色板的像素艺术（NES、Game Boy、PICO-8）"
sidebar_label: "像素艺术"
description: "带有复古时代调色板的像素艺术（NES、Game Boy、PICO-8）"
---

--- body ---
{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 像素艺术

带有复古时代调色板的像素艺术（NES、Game Boy、PICO-8）。

## 技能元数据

| 属性 | 值 |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/creative/pixel-art` 安装 |
| 路径 | `optional-skills/creative/pixel-art` |
| 版本 | `2.0.0` |
| 作者 | dodo-reach |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `creative`, `pixel-art`, `arcade`, `snes`, `nes`, `gameboy`, `retro`, `image`, `video` |

## 参考：完整 SKILL.md

:::info
以下是 Hermes 在此技能被触发时加载的完整技能定义。这是技能激活时智能体（Agent）看到的指令。
:::

# 像素艺术（Pixel Art）

将任何图像转换为复古像素艺术（pixel art），然后可以选择性地将其动画化为带有时代特效（雨、萤火虫、雪、余烬）的短 MP4 或 GIF。

此技能附带两个脚本：

- `scripts/pixel_art.py` — 照片 → 像素艺术 PNG（弗洛伊德-斯坦伯格抖动，Floyd-Steinberg dithering）
- `scripts/pixel_art_video.py` — 像素艺术 PNG → 动画 MP4（+ 可选 GIF）

每个脚本均可直接导入或运行。预设（preset）可在需要时代精准色彩（NES、Game Boy、PICO-8 等）时锁定硬件调色板（palette），或使用自适应 N 色量化（adaptive N-color quantization）实现街机/SNES 风格外观。

## 何时使用

- 用户希望从源图像获得复古像素艺术
- 用户要求 NES / Game Boy / PICO-8 / C64 / 街机 / SNES 风格
- 用户想要一个短循环动画（雨景、夜空、雪景等）
- 海报、专辑封面、社交媒体帖子、精灵图、角色、头像

## 工作流程

生成之前，与用户确认风格。不同的预设会产生截然不同的输出，重新生成成本较高。

### 步骤 1 — 提供风格

使用 4 个代表性预设调用 `clarify`。根据用户的要求选择相应的集合——不要一次性列出全部 14 个。

当用户意图不明确时的默认菜单：

```python
clarify(
    question="你想要哪种像素艺术风格？",
    choices=[
        "街机（arcade）— 大胆、块感十足的 80 年代街机风格（16 色，8 像素）",
        "NES — 任天堂 8 位硬件调色板（54 色，8 像素）",
        "Game Boy — 4 级灰度绿色 Game Boy DMG",
        "SNES — 更清晰的 16 位风格（32 色，4 像素）",
    ],
)
```

当用户已经指定了某个时代（例如“80 年代街机”、“Gameboy”）时，跳过 `clarify`，直接使用匹配的预设。

### 步骤 2 — 提供动画（可选）

如果用户要求生成视频/GIF，或者输出可能因动态效果而更佳，询问选择哪种场景：

```python
clarify(
    question="想要添加动画吗？选择一种场景或跳过。",
    choices=[
        "夜晚（night）— 星星 + 萤火虫 + 落叶",
        "都市（urban）— 雨 + 霓虹闪烁",
        "雪景（snow）— 飘落的雪花",
        "跳过 — 仅图像",
    ],
)
```

**不要**连续调用 `clarify` 超过两次。一次用于风格，一次用于场景（如果需要动画）。如果用户在消息中明确指定了风格和场景，则完全跳过 `clarify`。

### 步骤 3 — 生成

先运行 `pixel_art()`；如果需要动画，则在其结果上链接调用 `pixel_art_video()`。

## 预设目录

| 预设 | 时代 | 调色板 | 像素块大小 | 最佳用途 |
|------|------|--------|-----------|----------|
| `arcade` | 80 年代街机 | 自适应 16 色 | 8 像素 | 大胆海报、英雄艺术 |
| `snes` | 16 位 | 自适应 32 色 | 4 像素 | 角色、细节场景 |
| `nes` | 8 位 | NES（54 色） | 8 像素 | 真正的 NES 外观 |
| `gameboy` | DMG 掌机 | 4 种绿色调 | 8 像素 | 单色 Game Boy |
| `gameboy_pocket` | Pocket 掌机 | 4 种灰色调 | 8 像素 | 单色 GB Pocket |
| `pico8` | PICO-8 | 16 种固定色 | 6 像素 | 幻想主机外观 |
| `c64` | Commodore 64 | 16 种固定色 | 8 像素 | 8 位家用电脑 |
| `apple2` | Apple II 高分辨率 | 6 种固定色 | 10 像素 | 极致复古，6 色 |
| `teletext` | BBC Teletext | 8 种纯色 | 10 像素 | 粗体原色 |
| `mspaint` | Windows MS Paint | 24 种固定色 | 8 像素 | 怀旧桌面 |
| `mono_green` | CRT 荧光粉 | 2 种绿色 | 6 像素 | 终端/CRT 美学 |
| `mono_amber` | CRT 琥珀色 | 2 种琥珀色 | 6 像素 | 琥珀色显示器外观 |
| `neon` | 赛博朋克 | 10 种霓虹色 | 6 像素 | 蒸汽波/赛博 |
| `pastel` | 柔和蜡笔 | 10 种蜡笔色 | 6 像素 | 可爱/温和 |

命名的调色板位于 `scripts/palettes.py` 中（完整列表见 `references/palettes.md`——共 28 种命名调色板）。任何预设均可覆盖：

```python
pixel_art("in.png", "out.png", preset="snes", palette="PICO_8", block=6)
```

## 场景目录（用于视频）

| 场景 | 特效 |
|------|------|
| `night` | 闪烁星星 + 萤火虫 + 飘落的树叶 |
| `dusk` | 萤火虫 + 闪光 |
| `tavern` | 尘埃颗粒 + 温暖闪光 |
| `indoor` | 尘埃颗粒 |
| `urban` | 雨 + 霓虹闪烁 |
| `nature` | 树叶 + 萤火虫 |
| `magic` | 闪光 + 萤火虫 |
| `storm` | 雨 + 闪电 |
| `underwater` | 气泡 + 微光 |
| `fire` | 余烬 + 闪光 |
| `snow` | 雪花 + 闪光 |
| `desert` | 热浪 + 尘土 |

## 调用模式

### Python（导入）

```python
import sys
sys.path.insert(0, "/home/teknium/.hermes/skills/creative/pixel-art/scripts")
from pixel_art import pixel_art
from pixel_art_video import pixel_art_video

# 1. 转换为像素艺术
pixel_art("/path/to/photo.jpg", "/tmp/pixel.png", preset="nes")

# 2. 添加动画（可选）
pixel_art_video(
    "/tmp/pixel.png",
    "/tmp/pixel.mp4",
    scene="night",
    duration=6,
    fps=15,
    seed=42,
    export_gif=True,
)
```

### CLI

```bash
cd /home/teknium/.hermes/skills/creative/pixel-art/scripts

python pixel_art.py in.jpg out.png --preset gameboy
python pixel_art.py in.jpg out.png --preset snes --palette PICO_8 --block 6

python pixel_art_video.py out.png out.mp4 --scene night --duration 6 --gif
```

## 流程原理

**像素转换：**
1. 增强对比度/色彩/锐度（对于较小的调色板增强更强）
2. 色调分离（posterize）以在量化前简化色调区域
3. 使用 `Image.NEAREST` 按 `block` 缩小（硬像素，无插值）
4. 使用弗洛伊德-斯坦伯格抖动（Floyd-Steinberg dithering）进行量化——可选择自适应 N 色调色板或命名的硬件调色板
5. 使用 `Image.NEAREST` 重新放大

**在缩小之后进行量化**，确保抖动与最终像素网格对齐。如果先量化，误差扩散会浪费在后续消失的细节上。

**视频叠加：**
- 每帧复制基础帧（静态背景）
- 叠加无状态每帧粒子绘制（每个特效一个函数）
- 通过 ffmpeg `libx264 -pix_fmt yuv420p -crf 18` 编码
- 可选 GIF 通过 `palettegen` + `paletteuse`

## 依赖

- Python 3.9+
- Pillow（`pip install Pillow`）
- 系统 PATH 中的 ffmpeg（仅视频需要 — Hermes 会安装此包）

## 常见陷阱

- 调色板键名区分大小写（`"NES"`、`"PICO_8"`、`"GAMEBOY_ORIGINAL"`）。
- 非常小的源图像（宽度<100像素）在 8-10 像素块下会崩塌。如果源图像很小，请先放大。
- 分数的 `block` 或 `palette` 会破坏量化 — 请使用正整数。
- 动画粒子数量针对约 640x480 的画布调整。对于非常大的图像，可能需要使用不同种子进行第二遍处理以增加密度。
- `mono_green` / `mono_amber` 强制 `color=0.0`（去饱和）。如果覆盖并保留色度，2 色调色板可能会在平滑区域产生条纹。
- `clarify` 循环：每轮最多调用两次（风格，然后场景）。不要用更多选择让用户感到困扰。

## 验证

- PNG 创建在输出路径
- 在预设的块大小下可见清晰的方形像素块
- 颜色数量匹配预设（目测图像或运行 `Image.open(p).getcolors()`）
- 视频是有效的 MP4（`ffprobe` 可打开）且大小非零

## 署名

命名的硬件调色板和 `pixel_art_video.py` 中的程序化动画循环移植自 [pixel-art-studio](https://github.com/Synero/pixel-art-studio)（MIT）。有关详细信息，请参见此技能目录中的 `ATTRIBUTION.md`。