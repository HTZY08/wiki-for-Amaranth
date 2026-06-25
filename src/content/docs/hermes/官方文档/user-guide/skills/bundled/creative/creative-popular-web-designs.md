---
title: Popular Web Designs
---

title: "热门网页设计 —— 54 个真实设计系统（Stripe、Linear、Vercel）的 HTML/CSS 实现"
sidebar_label: "热门网页设计"
description: "54 个真实设计系统（Stripe、Linear、Vercel）的 HTML/CSS 实现"
---

--- body ---
{/* 本页面由 `website/scripts/generate-skill-docs.py` 根据技能（Skill）的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 热门网页设计（Popular Web Designs）

54 个真实设计系统（Stripe、Linear、Vercel）的 HTML/CSS 实现。

## 技能（Skill）元数据

| | |
|---|---|
| 来源（Source） | 捆绑（默认安装） |
| 路径（Path） | `skills/creative/popular-web-designs` |
| 版本（Version） | `1.0.0` |
| 作者（Author） | Hermes 代理（Agent） + Teknium（设计系统源自 VoltAgent/awesome-design-md） |
| 许可协议（License） | MIT |
| 支持平台（Platforms） | linux, macos, windows |

## 参考：完整的 SKILL.md

:::info
以下为 Hermes 在该技能被触发时加载的完整技能定义。当技能激活时，代理（Agent）看到的指令即为此内容。
:::

# 热门网页设计（Popular Web Designs）

54 个可直接用于生成 HTML/CSS 的真实世界设计系统。每个模板（template）都捕捉了某个网站完整的视觉语言：调色板（color palette）、排版层次（typography hierarchy）、组件样式（component styles）、间距系统（spacing system）、阴影（shadows）、响应式行为（responsive behavior），以及包含精确 CSS 值的实用代理提示（agent prompts）。

## 相关设计技能

- **`claude-design`** — 用于掌控设计的 *流程与品味*（界定简报、生成变体、验证本地 HTML 工件、避免 AI 设计敷衍）。当用户希望根据已知品牌风格设计精良的页面时，可将此技能与该技能配对使用：`claude-design` 驱动工作流程，本技能提供视觉词汇。
- **`design-md`** — 当交付物是正式的 DESIGN.md 令牌（token）规范文件而非渲染后的工件时使用。

## 使用方法

1. 从下方目录中选择一个设计
2. 加载它：`skill_view(name="popular-web-designs", file_path="templates/<site>.md")`
3. 在生成 HTML 时使用设计令牌（design tokens）和组件规范
4. 与 `generative-widgets` 技能配合，通过 cloudflared 隧道提供结果

每个模板顶部都包含一个 **Hermes 实现说明（Hermes Implementation Notes）** 区块，内容包括：
- CDN 字体替代方案及 Google Fonts `<link>` 标签（可直接粘贴）
- 主字体和等宽字体的 CSS font-family 堆栈（font-family stack）
- 提醒使用 `write_file` 创建 HTML，并使用 `browser_vision` 进行验证

## HTML 生成模式

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>页面标题</title>
  <!-- 从模板的 Hermes 说明中粘贴 Google Fonts 的 <link> 标签 -->
  <link href="https://fonts.googleapis.com/css2?family=..." rel="stylesheet">
  <style>
    /* 将模板的调色板应用为 CSS 自定义属性 */
    :root {
      --color-bg: #ffffff;
      --color-text: #171717;
      --color-accent: #533afd;
      /* ... 更多来自模板第 2 节的内容 */
    }
    /* 应用模板第 3 节中的排版样式 */
    body {
      font-family: 'Inter', system-ui, sans-serif;
      color: var(--color-text);
      background: var(--color-bg);
    }
    /* 应用模板第 4 节中的组件样式 */
    /* 应用模板第 5 节中的布局 */
    /* 应用模板第 6 节中的阴影 */
  </style>
</head>
<body>
  <!-- 根据模板中的组件规范进行构建 -->
</body>
</html>
```

使用 `write_file` 写入文件，通过 `generative-widgets` 工作流程（cloudflared 隧道）提供服务，并使用 `browser_vision` 验证结果以确保视觉准确性。

## 字体替代参考

大多数网站使用无法通过 CDN 获取的专有字体。每个模板都映射了一个能保留设计特色的 Google Fonts 替代字体。常见映射如下：

| 专有字体（Proprietary Font） | CDN 替代字体（CDN Substitute） | 特征（Character） |
|---|---|---|
| Geist / Geist Sans | Geist（在 Google Fonts 上） | 几何风格，紧凑字间距 |
| Geist Mono | Geist Mono（在 Google Fonts 上） | 整洁等宽，连字 |
| sohne-var（Stripe） | Source Sans 3 | 轻量优雅 |
| Berkeley Mono | JetBrains Mono | 技术等宽 |
| Airbnb Cereal VF | DM Sans | 圆润友好的几何风格 |
| Circular（Spotify） | DM Sans | 几何风格，温暖 |
| figmaSans | Inter | 清晰的人本主义风格 |
| Pin Sans（Pinterest） | DM Sans | 友好，圆润 |
| NVIDIA-EMEA | Inter（或 Arial 系统） | 工业感，清晰 |
| CoinbaseDisplay/Sans | DM Sans | 几何风格，值得信赖 |
| UberMove | DM Sans | 粗体，紧凑 |
| HashiCorp Sans | Inter | 企业级，中性 |
| waldenburgNormal（Sanity） | Space Grotesk | 几何风格，略紧凑 |
| IBM Plex Sans/Mono | IBM Plex Sans/Mono | 可在 Google Fonts 上获取 |
| Rubik（Sentry） | Rubik | 可在 Google Fonts 上获取 |

当模板的 CDN 字体与原始字体一致（Inter、IBM Plex、Rubik、Geist）时，不会产生替代损失。当使用替代字体（如 DM Sans 代替 Circular，Source Sans 3 代替 sohne-var）时，应严格遵循模板的字重（weight）、尺寸（size）和字间距（letter-spacing）值——这些承载的视觉特征比具体字体更重要。

## 设计目录

### AI 与机器学习

| 模板（Template） | 网站（Site） | 风格（Style） |
|---|---|---|
| `claude.md` | Anthropic Claude | 暖赭石色强调色，整洁的编辑式布局 |
| `cohere.md` | Cohere | 鲜艳渐变色，数据丰富的仪表盘美学 |
| `elevenlabs.md` | ElevenLabs | 深色电影感 UI，音频波形美学 |
| `minimax.md` | Minimax | 大胆的深色界面，霓虹色强调 |
| `mistral.ai.md` | Mistral AI | 法式极简主义，紫色调 |
| `ollama.md` | Ollama | 终端优先，单色简洁 |
| `opencode.ai.md` | OpenCode AI | 开发者导向的深色主题，全等宽 |
| `replicate.md` | Replicate | 干净的白色画布，代码优先 |
| `runwayml.md` | RunwayML | 电影感深色 UI，媒体丰富布局 |
| `together.ai.md` | Together AI | 技术感，蓝图风格设计 |
| `voltagent.md` | VoltAgent | 虚空黑色画布，翠绿强调色，终端原生 |
| `x.ai.md` | xAI | 醒目的单色，未来感极简，全等宽 |

### 开发者工具与平台

| 模板（Template） | 网站（Site） | 风格（Style） |
|---|---|---|
| `cursor.md` | Cursor | 时尚深色界面，渐变强调色 |
| `expo.md` | Expo | 深色主题，紧凑字间距，代码中心 |
| `linear.app.md` | Linear | 超极简深色模式，精准，紫色强调 |
| `lovable.md` | Lovable | 俏皮渐变色，友好的开发者美学 |
| `mintlify.md` | Mintlify | 干净，绿色强调，阅读优化 |
| `posthog.md` | PostHog | 俏皮品牌，开发者友好的深色 UI |
| `raycast.md` | Raycast | 时尚深色铬色，鲜艳渐变强调 |
| `resend.md` | Resend | 极简深色主题，等宽强调 |
| `sentry.md` | Sentry | 深色仪表盘，数据密集，粉紫强调 |
| `supabase.md` | Supabase | 深翠绿主题，代码优先的开发者工具 |
| `superhuman.md` | Superhuman | 高级深色 UI，键盘优先，紫色辉光 |
| `vercel.md` | Vercel | 黑白精准，Geist 字体系统 |
| `warp.md` | Warp | 深色类 IDE 界面，基于块的命令 UI |
| `zapier.md` | Zapier | 暖橙色，友好插画驱动 |

### 基础设施与云

| 模板（Template） | 网站（Site） | 风格（Style） |
|---|---|---|
| `clickhouse.md` | ClickHouse | 黄色强调，技术文档风格 |
| `composio.md` | Composio | 现代深色，彩色集成图标 |
| `hashicorp.md` | HashiCorp | 企业级干净，黑白色 |
| `mongodb.md` | MongoDB | 绿色叶子品牌，开发者文档导向 |
| `sanity.md` | Sanity | 红色强调，内容优先的编辑布局 |
| `stripe.md` | Stripe | 标志性紫色渐变，字重300优雅 |

### 设计与生产力

| 模板（Template） | 网站（Site） | 风格（Style） |
|---|---|---|
| `airtable.md` | Airtable | 彩色，友好，结构化数据美学 |
| `cal.md` | Cal.com | 干净中性 UI，开发者导向的简洁 |
| `clay.md` | Clay | 有机形状，柔和渐变，艺术指导布局 |
| `figma.md` | Figma | 生动多彩，俏皮且专业 |
| `framer.md` | Framer | 大胆黑蓝，动效优先，设计前沿 |
| `intercom.md` | Intercom | 友好蓝色调色板，对话式 UI 模式 |
| `miro.md` | Miro | 亮黄色强调，无限画布美学 |
| `notion.md` | Notion | 温暖极简，衬线标题，柔和表面 |
| `pinterest.md` | Pinterest | 红色强调，瀑布流网格，图片优先布局 |
| `webflow.md` | Webflow | 蓝色强调，精美营销网站美学 |

### 金融科技与加密货币

| 模板（Template） | 网站（Site） | 风格（Style） |
|---|---|---|
| `coinbase.md` | Coinbase | 干净蓝色身份，信任导向，机构感 |
| `kraken.md` | Kraken | 紫色强调的深色 UI，数据密集仪表盘 |
| `revolut.md` | Revolut | 时尚深色界面，渐变卡片，金融科技精准 |
| `wise.md` | Wise | 亮绿色强调，友好清晰 |

### 企业与消费

| 模板（Template） | 网站（Site） | 风格（Style） |
|---|---|---|
| `airbnb.md` | Airbnb | 暖珊瑚色强调，摄影驱动，圆润 UI |
| `apple.md` | Apple | 高级留白，SF Pro，电影感图像 |
| `bmw.md` | BMW | 深色高级表面，精准工程美学 |
| `ibm.md` | IBM | Carbon 设计系统，结构化蓝色调色板 |
| `nvidia.md` | NVIDIA | 绿黑能量，技术力量美学 |
| `spacex.md` | SpaceX | 醒目黑白，全出血图像，未来感 |
| `spotify.md` | Spotify | 深色背景上的鲜艳绿色，粗体文字，专辑封面驱动 |
| `uber.md` | Uber | 大胆黑白，紧凑字距，都市能量 |

## 选择设计

根据内容匹配设计：

- **开发者工具 / 仪表盘：** Linear, Vercel, Supabase, Raycast, Sentry
- **文档 / 内容网站：** Mintlify, Notion, Sanity, MongoDB
- **营销 / 落地页：** Stripe, Framer, Apple, SpaceX
- **深色模式 UI：** Linear, Cursor, ElevenLabs, Warp, Superhuman
- **浅色 / 干净 UI：** Vercel, Stripe, Notion, Cal.com, Replicate
- **俏皮 / 友好：** PostHog, Figma, Lovable, Zapier, Miro
- **高级 / 奢华：** Apple, BMW, Stripe, Superhuman, Revolut
- **数据密集 / 仪表盘：** Sentry, Kraken, Cohere, ClickHouse
- **等宽 / 终端美学：** Ollama, OpenCode, x.ai, VoltAgent