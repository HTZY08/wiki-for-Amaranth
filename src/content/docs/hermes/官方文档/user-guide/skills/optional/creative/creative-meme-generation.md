--- frontmatter ---
---
title: "迷因生成 — 通过选择模板并使用 Pillow 叠加文本来生成真实的迷因图片"
sidebar_label: "迷因生成"
description: "通过选择模板并使用 Pillow 叠加文本来生成真实的迷因图片"
---

--- body ---
{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源 SKILL.md，而非此页面。 */}

# 迷因生成（Meme Generation）

通过选择模板并使用 Pillow 叠加文本来生成真实的迷因图片。生成实际的 .png 迷因文件。

## 技能元数据（Skill metadata）

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/creative/meme-generation` 安装 |
| 路径 | `optional-skills/creative/meme-generation` |
| 版本 | `2.0.0` |
| 作者 | adanaleycio |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `creative`, `memes`, `humor`, `images` |
| 相关技能 | [`ascii-art`](/docs/user-guide/skills/bundled/creative/creative-ascii-art), `generative-widgets` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。当技能激活时，代理（Agent）会看到这些指令。
:::

# 迷因生成

根据主题生成实际的迷因图片。选择模板，编写标题，并渲染带有文本叠加的真实 .png 文件。

## 何时使用

- 用户要求你制作或生成迷因
- 用户想要关于特定主题、情境或挫折的迷因
- 用户说“把这个做成迷因”或类似的话

## 可用模板

脚本支持**约 100 个流行的 imgflip 模板**（按名称或 ID），外加 10 个经过手动调整文本位置的精选模板。

### 精选模板（自定义文本位置）

| ID | 名称 | 字段 | 最佳用途 |
|----|------|--------|----------|
| `this-is-fine` | 没问题 | 顶部, 底部 | 混乱、否认 |
| `drake` | Drake 热线荧光 | 拒绝, 赞同 | 拒绝/偏好 |
| `distracted-boyfriend` | 分心男友 | 分心, 当前, 人物 | 诱惑、优先级转变 |
| `two-buttons` | 两个按钮 | 左, 右, 人物 | 两难选择 |
| `expanding-brain` | 扩大的大脑 | 4 个等级 | 升级的讽刺 |
| `change-my-mind` | 改变我的想法 | 陈述 | 争议性观点 |
| `woman-yelling-at-cat` | 女人对猫大喊 | 女人, 猫 | 争执 |
| `one-does-not-simply` | 不能简单 | 顶部, 底部 | 看似简单实则困难的事 |
| `grus-plan` | 格鲁的计划 | 步骤1-3, 领悟 | 适得其反的计划 |
| `batman-slapping-robin` | 蝙蝠侠扇罗宾 | 罗宾, 蝙蝠侠 | 否决糟糕的想法 |

### 动态模板（来自 imgflip API）

不在精选列表中的任何模板都可以通过名称或 imgflip ID 使用。这些模板会获得智能默认文本位置（两个字段时顶部/底部，三个及以上时均匀分布）。搜索方式：
```bash
python "$SKILL_DIR/scripts/generate_meme.py" --search "disaster"
```

## 步骤

### 模式 1：经典模板（默认）

1. 阅读用户的主题，识别核心动态（混乱、困境、偏好、讽刺等）
2. 选择最匹配的模板。使用“最佳用途”列，或使用 `--search` 搜索。
3. 为每个字段编写简短的标题（每个字段最多 8-12 个词，越短越好）。
4. 查找技能的脚本目录：
   ```
   SKILL_DIR=$(dirname "$(find ~/.hermes/skills -path '*/meme-generation/SKILL.md' 2>/dev/null | head -1)")
   ```
5. 运行生成器：
   ```bash
   python "$SKILL_DIR/scripts/generate_meme.py" <template_id> /tmp/meme.png "caption 1" "caption 2" ...
   ```
6. 通过 `MEDIA:/tmp/meme.png` 返回图片

### 模式 2：自定义 AI 图像（当 `image_generate` 可用时）

当没有经典模板适合，或用户想要原创内容时使用。

1. 先编写标题。
2. 使用 `image_generate` 创建与迷因概念匹配的场景。**不要在图像提示中包含任何文本**——文本将由脚本添加。仅描述视觉场景。
3. 从 `image_generate` 结果 URL 中找到生成的图像路径。如有需要，将其下载到本地路径。
4. 使用 `--image` 运行脚本以叠加文本，选择一种模式：
   - **叠加**（文本直接放在图像上，白色带黑色轮廓）：
     ```bash
     python "$SKILL_DIR/scripts/generate_meme.py" --image /path/to/scene.png /tmp/meme.png "top text" "bottom text"
     ```
   - **横条**（图像上方/下方添加黑色横条，白色文本——更干净，始终可读）：
     ```bash
     python "$SKILL_DIR/scripts/generate_meme.py" --image /path/to/scene.png --bars /tmp/meme.png "top text" "bottom text"
     ```
   当图像繁忙/细节较多，文本不易读时使用 `--bars`。
5. **使用视觉验证**（如果 `vision_analyze` 可用）：检查结果是否良好：
   ```
   vision_analyze(image_url="/tmp/meme.png", question="Is the text legible and well-positioned? Does the meme work visually?")
   ```
   如果视觉模型指出问题（文本难读、位置不佳等），尝试另一种模式（在叠加和横条之间切换）或重新生成场景。
6. 通过 `MEDIA:/tmp/meme.png` 返回图片

## 示例

**“凌晨 2 点调试生产环境”：**
```bash
python generate_meme.py this-is-fine /tmp/meme.png "SERVERS ARE ON FIRE" "This is fine"
```

**“在睡觉和再看一集之间做选择”：**
```bash
python generate_meme.py drake /tmp/meme.png "Getting 8 hours of sleep" "One more episode at 3 AM"
```

**“星期一早晨的阶段”：**
```bash
python generate_meme.py expanding-brain /tmp/meme.png "Setting an alarm" "Setting 5 alarms" "Sleeping through all alarms" "Working from bed"
```

## 列出模板

查看所有可用模板：
```bash
python generate_meme.py --list
```

## 注意事项

- 保持标题简短。文本过长的迷因看起来很糟糕。
- 文本参数的数量要与模板的字段数匹配。
- 选择符合笑话结构的模板，而不仅仅是主题。
- 不要生成仇恨、辱骂或针对个人的内容。
- 脚本在首次下载后将模板图像缓存在 `scripts/.cache/` 中。

## 验证

输出正确当：
- 在输出路径创建了 .png 文件
- 文本在模板上清晰可读（白色带黑色轮廓）
- 笑话成立——标题符合模板的预期结构
- 文件可以通过 MEDIA: 路径传递