---
title: Image Generation
---

title: 图像生成
description: 通过 FAL.ai 生成图像 — 11 种模型，包括 FLUX 2、GPT Image (1.5 & 2)、Nano Banana Pro、Ideogram、Recraft V4 Pro、Krea 2 等，可通过 `hermes tools` 选择。
sidebar_label: 图像生成
sidebar_position: 6
---

--- body ---
# 图像生成

Hermes 代理（Agent）通过 FAL.ai 从文本提示（prompt）生成图像。开箱即支持十一种模型，每种模型在速度、质量和成本方面各有取舍。当前使用的模型可通过 `hermes tools` 由用户配置，并持久保存在 `config.yaml` 中。

## 支持的模型

| 模型 | 速度 | 优势 | 价格 |
|---|---|---|---|
| `fal-ai/flux-2/klein/9b` *(默认)* | `<1s` | 快速、文本清晰 | $0.006/MP |
| `fal-ai/flux-2-pro` | ~6s | 工作室级照片真实感 | $0.03/MP |
| `fal-ai/z-image/turbo` | ~2s | 双语 EN/CN，60 亿参数 | $0.005/MP |
| `fal-ai/nano-banana-pro` | ~8s | Gemini 3 Pro，推理深度，文本渲染 | $0.15/图像 (1K) |
| `fal-ai/gpt-image-1.5` | ~15s | 遵循提示（Prompt adherence） | $0.034/图像 |
| `fal-ai/gpt-image-2` | ~20s | 最先进的文本渲染 + 中日韩文（CJK），世界感知的照片真实感 | $0.04–0.06/图像 |
| `fal-ai/ideogram/v3` | ~5s | 最佳排版 | $0.03–0.09/图像 |
| `fal-ai/recraft/v4/pro/text-to-image` | ~8s | 设计、品牌系统、生产就绪 | $0.25/图像 |
| `fal-ai/qwen-image` | ~12s | 基于大语言模型（LLM），复杂文本 | $0.02/MP |
| `fal-ai/krea/v2/medium/text-to-image` | ~15-25s | 插图、动漫、绘画、表现/艺术风格 | $0.030–0.035/图像 |
| `fal-ai/krea/v2/large/text-to-image` | ~25-60s | 照片真实感，原始纹理外观（运动模糊、颗粒感、胶片感） | $0.060–0.065/图像 |

价格为撰写时的 FAL 定价；请查看 [fal.ai](https://fal.ai/) 获取当前价格。

## 设置

:::tip Nous 订阅用户
如果您拥有付费的 [Nous Portal](https://portal.nousresearch.com) 订阅，则无需 FAL API 密钥即可通过 **[工具网关（Tool Gateway）](tool-gateway.md)** 使用图像生成功能。您的模型选择在两个路径中保持一致。新安装可通过 `hermes setup --portal` 登录并一次性开启所有网关工具；现有安装可通过 `hermes tools` 选择 **Nous 订阅（Nous Subscription）** 作为图像生成后端。

如果托管网关返回特定模型的 `HTTP 4xx` 错误，说明该模型尚未在门户端代理 — 代理（Agent）会告知您，并提供修复步骤（设置 `FAL_KEY` 直接访问，或选择其他模型）。
:::

### 获取 FAL API 密钥

1. 在 [fal.ai](https://fal.ai/) 注册
2. 从您的控制面板生成一个 API 密钥

### 配置并选择一个模型

运行工具命令：

```bash
hermes tools
```

导航到 **🎨 图像生成（Image Generation）**，选择您的后端（Nous 订阅或 FAL.ai），然后选择器会以列对齐表格显示所有支持的模型 — 使用方向键导航，按 Enter 选择：

```
  模型                          速度     优势                          价格
  fal-ai/flux-2/klein/9b         <1s     快速、文本清晰               $0.006/MP   ← 当前使用中
  fal-ai/flux-2-pro              ~6s     工作室级照片真实感           $0.03/MP
  fal-ai/z-image/turbo           ~2s     双语 EN/CN，60 亿参数       $0.005/MP
  ...
```

您的选择将保存到 `config.yaml` 中：

```yaml
image_gen:
  model: fal-ai/flux-2/klein/9b
  use_gateway: false            # 如果使用 Nous 订阅则为 true
```

### GPT-Image 质量

`fal-ai/gpt-image-1.5` 和 `fal-ai/gpt-image-2` 请求的质量固定为 `medium`（约 $0.034–$0.06/图像，尺寸 1024×1024）。我们不将 `low` / `high` 档次作为用户可选选项公开，以便 Nous Portal 计费在所有用户间保持可预测 — 各档次之间的成本差异为 3–22 倍。如果您想要更便宜的选项，请选择 Klein 9B 或 Z-Image Turbo；如果需要更高质量，请使用 Nano Banana Pro 或 Recraft V4 Pro。

## 使用

面向代理（Agent）的模式有意保持最小化 — 模型会自动获取您配置的任何内容：

```
生成一张宁静的山景图，伴有樱花
```

```
创建一张睿智老猫头鹰的方形肖像 — 使用排版模型
```

```
给我制作一幅未来城市景观图，横向构图
```

## 图像到图像 / 编辑

当当前模型支持时，同一个 `image_generate` 工具也可以**编辑现有图像** — 传入源图像，后端会自动路由到其编辑端点（与 `video_generate` 处理图像到视频的方式类似）。省略源图像即为纯文本到图像。

```
取这张照片，让它变成雨夜的东京街道 → <image>
```

```
将这两张产品照片融合成一张主图 → <image1> <image2>
```

驱动编辑的两个输入：

- **`image_url`** — 要编辑/转换的主源图像（公共 URL 或本地路径）。
- **`reference_image_urls`** — 额外的风格/构图参考（每个模型有上限）。

### 哪些后端支持编辑

| 后端 | 图像到图像 | 参考上限 | 方式 |
|---|---|---|---|
| **FAL.ai**（以下具备编辑能力的模型） | ✓ | 最多 9 个 | 路由到模型的 `/edit` 端点 |
| **OpenAI**（`gpt-image-2`） | ✓ | 最多 16 个 | `images.edit()` |
| **xAI**（Grok Imagine） | ✓ | 1 个 | `/v1/images/edits`（`grok-imagine-image-quality`） |
| **Krea**（`Krea 2`） | ✓ | 最多 10 个 | 参考引导生成（`image_style_references`） |
| **OpenAI（Codex 认证）** | ✗ | — | 仅文本到图像 |

具有编辑端点的 FAL 模型：`flux-2/klein/9b`、`flux-2-pro`、`nano-banana-pro`、`gpt-image-1.5`、`gpt-image-2`、`ideogram/v3` 和 `qwen-image`。纯文本到图像的 FAL 模型（`z-image/turbo`、`recraft`、`krea/*`）会拒绝图像输入，并附带明确的错误信息，指引您使用具备编辑能力的模型。

当前模型的编辑能力会在运行时体现在工具描述中，因此代理（Agent）在调用工具前就知道 `image_url` 是否会被接受。

## 宽高比

从代理（Agent）的角度看，每个模型都接受相同的三种宽高比。在内部，每个模型的原生尺寸规格会自动填充：

| Agent 输入 | image_size（flux/z-image/qwen/recraft/ideogram） | aspect_ratio（nano-banana-pro） | image_size（gpt-image-1.5） | image_size（gpt-image-2） |
|---|---|---|---|---|
| `landscape` | `landscape_16_9` | `16:9` | `1536x1024` | `landscape_4_3`（1024×768） |
| `square` | `square_hd` | `1:1` | `1024x1024` | `square_hd`（1024×1024） |
| `portrait` | `portrait_16_9` | `9:16` | `1024x1536` | `portrait_4_3`（768×1024） |

GPT Image 2 映射到 4:3 预设而非 16:9，因为其最小像素数为 655,360 — `landscape_16_9` 预设（1024×576 = 589,824）会被拒绝。

此转换在 `_build_fal_payload()` 中完成 — 代理（Agent）代码无需了解各模型 schema 的差异。

## 自动放大

通过 FAL 的 **Clarity Upscaler** 进行放大按模型进行控制：

| 模型 | 放大？ | 原因 |
|---|---|---|
| `fal-ai/flux-2-pro` | ✓ | 向后兼容（曾是选择器前的默认值） |
| 其他所有 | ✗ | 快速模型会失去其亚秒级的价值主张；高分辨率模型则不需要 |

执行放大时，使用以下设置：

| 设置 | 值 |
|---|---|
| 放大倍数 | 2× |
| 创造力（Creativity） | 0.35 |
| 相似度（Resemblance） | 0.6 |
| 引导比例（Guidance scale） | 4 |
| 推理步数（Inference steps） | 18 |

如果放大失败（网络问题、速率限制），会自动返回原始图像。

## 内部工作原理

1. **模型解析** — `_resolve_fal_model()` 从 `config.yaml` 读取 `image_gen.model`，回退到 `FAL_IMAGE_MODEL` 环境变量，最后回退到 `fal-ai/flux-2/klein/9b`。
2. **载荷构建** — `_build_fal_payload()` 将您的 `aspect_ratio` 转换为模型的原生格式（预设枚举、宽高比枚举或 GPT 字面量），合并模型的默认参数，应用调用者的覆盖值，然后过滤到模型支持的 `supports` 白名单，从而避免发送不支持的键。
3. **提交** — `_submit_fal_request()` 通过直接 FAL 凭据或托管 Nous 网关进行路由。
4. **放大** — 仅当模型的元数据中包含 `upscale: True` 时运行。
5. **交付** — 最终图像 URL 返回给代理（Agent），代理发出 `MEDIA:<url>` 标签，平台适配器将其转换为原生媒体。

## 调试

启用调试日志：

```bash
export IMAGE_TOOLS_DEBUG=true
```

调试日志输出到 `./logs/image_tools_debug_<session_id>.json`，包含每个调用的详细信息（模型、参数、时序、错误）。

## 平台交付

| 平台 | 交付方式 |
|---|---|
| **CLI** | 图像 URL 以 markdown 形式打印为 `![](url)` — 点击打开 |
| **Telegram** | 照片消息，提示作为标题 |
| **Discord** | 嵌入在消息中 |
| **Slack** | URL 由 Slack 展开 |
| **WhatsApp** | 媒体消息 |
| **其他** | 纯文本 URL |

## 限制

- **需要凭据** 用于活动后端（FAL `FAL_KEY` / Nous 订阅、`OPENAI_API_KEY`、xAI OAuth、`KREA_API_KEY`）
- **编辑依赖于模型** — 图像到图像仅在具备编辑能力的模型上有效（见上方表格）；仅文本到图像的模型会拒绝图像输入并附带明确错误
- **临时 URL** — 后端返回托管 URL，数小时/天后过期；Hermes 会将它们物化到本地缓存，因此过期后仍可正常交付
- **模型特定约束** — 某些模型不支持 `seed`、`num_inference_steps` 等。`supports` / `edit_supports` 过滤器会静默丢弃不支持的参数；这是预期行为