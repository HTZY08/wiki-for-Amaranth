--- frontmatter ---
---
sidebar_position: 12
title: "视频生成提供者插件"
description: "如何为 Hermes Agent 构建视频生成后端插件"
---

--- body ---
# 构建视频生成提供者插件 (Building a Video Generation Provider Plugin)

视频生成提供者插件注册一个后端，为每次 `video_generate` 工具调用提供服务。内置提供者（xAI、FAL）作为插件提供。通过将一个目录放入 `plugins/video_gen/<name>/`，可以添加新的提供者，或覆盖已有的打包提供者。

:::tip
视频生成与[图片生成提供者插件](/developer-guide/image-gen-provider-plugin)几乎逐行对应 —— 如果你已经构建过一个图片生成后端，你就会知道它的结构。主要区别在于：一个 `capabilities()` 方法用于声明模态/宽高比/时长，以及一个路由约定（传递 `image_url` 时使用图片转视频，省略时使用文本转视频 —— 提供者内部选择正确的端点）。
:::

## 统一表面（一个工具，两种模态）

`video_generate` 工具通过一个参数暴露出两种模态：

- **文本转视频 (Text-to-video)** —— 仅使用 `prompt` 调用。提供者路由到其文本转视频端点。
- **图片转视频 (Image-to-video)** —— 使用 `prompt` + `image_url` 调用。提供者路由到其图片转视频端点。

编辑和扩展功能有意不在范围内。大多数后端不支持它们，而且不一致性会迫使 Agent 的工具描述中为每个后端编写特定文本。

## 发现机制 (Discovery)

Hermes 在三个位置扫描视频生成后端：

1. **打包提供者** —— `<repo>/plugins/video_gen/<name>/`（自动加载，`kind: backend`）
2. **用户提供者** —— `~/.hermes/plugins/video_gen/<name>/`（通过 `plugins.enabled` 选择加入）
3. **Pip 包** —— 声明 `hermes_agent.plugins` 入口点的包

每个插件的 `register(ctx)` 函数调用 `ctx.register_video_gen_provider(...)`。活跃提供者由 `config.yaml` 中的 `video_gen.provider` 选定；`hermes tools` → Video Generation 引导用户完成选择。与 `image_generate` 不同，没有树内遗留后端 —— 每个提供者都是一个插件。

## 目录结构

```
plugins/video_gen/my-backend/
├── __init__.py      # VideoGenProvider 子类 + register()
└── plugin.yaml      # 清单文件，kind: backend
```

## VideoGenProvider 抽象基类 (ABC)

继承 `agent.video_gen_provider.VideoGenProvider`。必需：`name` 属性和 `generate()` 方法。

```python
# plugins/video_gen/my-backend/__init__.py
from typing import Any, Dict, List, Optional
import os

from agent.video_gen_provider import (
    VideoGenProvider,
    error_response,
    success_response,
)


class MyVideoGenProvider(VideoGenProvider):
    @property
    def name(self) -> str:
        return "my-backend"

    @property
    def display_name(self) -> str:
        return "My Backend"

    def is_available(self) -> bool:
        return bool(os.environ.get("MY_API_KEY"))

    def list_models(self) -> List[Dict[str, Any]]:
        # 每个条目是一个模型家族（model FAMILY）—— 用户选择一次的名称。
        # 你的提供者的 generate() 根据是否传递了 image_url 在家族内路由。
        return [
            {
                "id": "fast",
                "display": "Fast",
                "speed": "~30s",
                "strengths": "Cheapest tier",
                "price": "$0.05/s",
                "modalities": ["text", "image"],  # 仅供参考
            },
        ]

    def default_model(self) -> Optional[str]:
        return "fast"

    def capabilities(self) -> Dict[str, Any]:
        return {
            "modalities": ["text", "image"],
            "aspect_ratios": ["16:9", "9:16"],
            "resolutions": ["720p", "1080p"],
            "min_duration": 1,
            "max_duration": 10,
            "supports_audio": False,
            "supports_negative_prompt": True,
            "max_reference_images": 0,
        }

    def get_setup_schema(self) -> Dict[str, Any]:
        return {
            "name": "My Backend",
            "badge": "paid",
            "tag": "Short description shown in `hermes tools`",
            "env_vars": [
                {
                    "key": "MY_API_KEY",
                    "prompt": "My Backend API key",
                    "url": "https://mybackend.example.com/keys",
                },
            ],
        }

    def generate(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        image_url: Optional[str] = None,
        reference_image_urls: Optional[List[str]] = None,
        duration: Optional[int] = None,
        aspect_ratio: str = "16:9",
        resolution: str = "720p",
        negative_prompt: Optional[str] = None,
        audio: Optional[bool] = None,
        seed: Optional[int] = None,
        **kwargs: Any,  # 始终忽略未知关键字参数以保持向前兼容
    ) -> Dict[str, Any]:
        # 路由（ROUTE）：根据 image_url 是否存在选择端点。
        if image_url:
            endpoint = "my-backend/image-to-video"
            modality_used = "image"
        else:
            endpoint = "my-backend/text-to-video"
            modality_used = "text"

        # ... 调用你的 API ...

        return success_response(
            video="https://your-cdn/output.mp4",
            model=model or "fast",
            prompt=prompt,
            modality=modality_used,
            aspect_ratio=aspect_ratio,
            duration=duration or 5,
            provider=self.name,
        )


def register(ctx) -> None:
    ctx.register_video_gen_provider(MyVideoGenProvider())
```

## 插件清单文件

```yaml
# plugins/video_gen/my-backend/plugin.yaml
name: my-backend
version: 1.0.0
description: "My video generation backend"
author: Your Name
kind: backend
requires_env:
  - MY_API_KEY
```

## `video_generate` 模式

该工具为每个后端暴露一个统一的模式。提供者忽略它们不支持的参数。

| 参数 (Parameter) | 作用 |
|---|---|
| `prompt` | 文本指令（必需） |
| `image_url` | 当设置时 → 图片转视频；省略时 → 文本转视频 |
| `reference_image_urls` | 风格/角色参考（依赖于提供者） |
| `duration` | 秒数 —— 提供者会进行限制 |
| `aspect_ratio` | `"16:9"`、`"9:16"`、`"1:1"` 等 —— 提供者会进行限制 |
| `resolution` | `"480p"` / `"540p"` / `"720p"` / `"1080p"` —— 提供者会进行限制 |
| `negative_prompt` | 要避免的内容（仅限 Pixverse/Kling） |
| `audio` | 原生音频（Veo3 / Pixverse 定价层级） |
| `seed` | 可复现性 |
| `model` | 覆盖当前活跃的模型/家族 |

提供者的 `capabilities()` 方法声明哪些参数会被尊重。Agent 会在工具描述中看到当前后端的 capability，当用户通过 `hermes tools` 更改后端时会动态重建。

## 模型家族与端点路由（FAL 模式）

当你的后端在每个“模型”下有多个端点时 —— 例如 FAL，每个家族（Veo 3.1、Pixverse v6、Kling O3）都有一个 `/text-to-video` 和一个 `/image-to-video` URL —— 将每个**家族**表示为一个目录条目。你的 `generate()` 根据是否传递了 `image_url` 来选择正确的端点：

```python
FAMILIES = {
    "veo3.1": {
        "text_endpoint": "fal-ai/veo3.1",
        "image_endpoint": "fal-ai/veo3.1/image-to-video",
        # ... 家族特定的 capability 标志 ...
    },
}

def generate(self, prompt, *, image_url=None, model=None, **kwargs):
    family_id, family = _resolve_family(model)
    endpoint = family["image_endpoint"] if image_url else family["text_endpoint"]
    # ... 根据家族声明的 capability 标志构建负载，调用端点 ...
```

用户在 `hermes tools` 中一次性选择 `veo3.1`。Agent 从不考虑端点 —— 它只是传递（或不传递）`image_url`。

## 选择优先级

对于每个实例的模型旋钮（参见 `plugins/video_gen/fal/__init__.py`）：

1. 来自工具调用的 `model=` 关键字参数
2. `<PROVIDER>_VIDEO_MODEL` 环境变量
3. `config.yaml` 中的 `video_gen.<provider>.model`
4. `config.yaml` 中的 `video_gen.model`（当它是你的 ID 之一时）
5. 提供者的 `default_model()`

## 响应格式

`success_response()` 和 `error_response()` 产生每个后端返回的字典格式。请使用它们 —— 不要手动构造字典。

成功响应键：`success`、`video`（URL 或绝对路径）、`model`、`prompt`、`modality`（`"text"` 或 `"image"`）、`aspect_ratio`、`duration`、`provider`，以及 `extra`。

错误响应键：`success`、`video`（None）、`error`、`error_type`、`model`、`prompt`、`aspect_ratio`、`provider`。

## 保存生成产物

如果你的后端返回 base64，使用 `save_b64_video()` 将内容写入 `$HERMES_HOME/cache/videos/`。如果是通过后续 HTTP 获取的原始字节，使用 `save_bytes_video()`。否则直接返回上游 URL —— 网关会在交付时解析远程 URL。

## 测试

在 `tests/plugins/video_gen/test_<name>_plugin.py` 中放置一个冒烟测试。xAI 和 FAL 的测试展示了模式 —— 注册，验证目录，练习同时使用和不使用 `image_url` 的路由，断言缺少认证时返回干净的错误响应。