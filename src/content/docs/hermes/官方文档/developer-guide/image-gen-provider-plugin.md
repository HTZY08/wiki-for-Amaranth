---
sidebar_position: 11
title: "图像生成提供者插件"
description: "如何为 Hermes Agent 构建一个图像生成后端插件"
---

---
# 构建图像生成提供者插件

图像生成（Image-gen）提供者插件注册一个后端，用于服务每一个 `image_generate` 工具调用——DALL·E、gpt-image、Grok、Flux、Imagen、Stable Diffusion、fal、Replicate、本地 ComfyUI 配置等。内置的提供者（OpenAI、OpenAI-Codex、xAI）都以插件形式提供。你可以通过将目录放入 `plugins/image_gen/<name>/` 来添加一个新的，或覆盖一个已有的。

:::tip
图像生成是 Hermes 支持的几种**后端插件**之一。其他（具有更专门化抽象基类 ABC）有[内存提供者插件](/developer-guide/memory-provider-plugin)、[上下文引擎插件](/developer-guide/context-engine-plugin)和[模型提供者插件](/developer-guide/model-provider-plugin)。通用工具/钩子/CLI 插件请参见[构建一个 Hermes 插件](/guides/build-a-hermes-plugin)。
:::

## 发现机制

Hermes 在三个位置扫描图像生成后端：

1. **内置（Bundled）** — `<repo>/plugins/image_gen/<name>/`（自动加载，带有 `kind: backend`，始终可用）
2. **用户（User）** — `~/.hermes/plugins/image_gen/<name>/`（通过 `plugins.enabled` 选择加入）
3. **Pip** — 声明了 `hermes_agent.plugins` 入口点的包

每个插件的 `register(ctx)` 函数调用 `ctx.register_image_gen_provider(...)`——将其注册到 `agent/image_gen_registry.py` 中的注册表中。活跃的提供者由 `config.yaml` 中的 `image_gen.provider` 选定；`hermes tools` 会引导用户完成选择。

`image_generate` 工具包装器查询注册表以获取活跃提供者，并分派到那里。如果没有注册提供者，工具会显示一个有用的错误信息，指向 `hermes tools`。

## 目录结构

```
plugins/image_gen/my-backend/
├── __init__.py      # ImageGenProvider 子类 + register()
└── plugin.yaml      # 清单，包含 kind: backend
```

一个内置插件到此就完整了。位于 `~/.hermes/plugins/image_gen/<name>/` 的用户插件需要添加到 `config.yaml` 的 `plugins.enabled` 列表中（或运行 `hermes plugins enable <name>`）。

## ImageGenProvider 抽象基类（ABC）

子类化 `agent.image_gen_provider.ImageGenProvider`。唯一必需的成员是 `name` 属性和 `generate()` 方法——其他部分都有合理的默认值：

```python
# plugins/image_gen/my-backend/__init__.py
from typing import Any, Dict, List, Optional
import os

from agent.image_gen_provider import (
    DEFAULT_ASPECT_RATIO,
    ImageGenProvider,
    error_response,
    normalize_reference_images,
    resolve_aspect_ratio,
    save_b64_image,
    success_response,
)


class MyBackendImageGenProvider(ImageGenProvider):
    @property
    def name(self) -> str:
        # 用于 image_gen.provider 配置的稳定标识符。小写，无空格。
        return "my-backend"

    @property
    def display_name(self) -> str:
        # 在 `hermes tools` 中显示的人类可读标签。如果省略，默认为 name.title()。
        return "My Backend"

    def is_available(self) -> bool:
        # 如果缺少凭据或依赖，返回 False。
        # 工具的可访问性检查会在分派前调用此方法。
        if not os.environ.get("MY_BACKEND_API_KEY"):
            return False
        try:
            import my_backend_sdk  # noqa: F401
        except ImportError:
            return False
        return True

    def list_models(self) -> List[Dict[str, Any]]:
        # 在 `hermes tools` 模型选择器中显示的目录。
        return [
            {
                "id": "my-model-fast",
                "display": "My Model (Fast)",
                "speed": "~5s",
                "strengths": "快速迭代",
                "price": "$0.01/图像",
            },
            {
                "id": "my-model-hq",
                "display": "My Model (HQ)",
                "speed": "~30s",
                "strengths": "最高保真度",
                "price": "$0.04/图像",
            },
        ]

    def default_model(self) -> Optional[str]:
        return "my-model-fast"

    def get_setup_schema(self) -> Dict[str, Any]:
        # 用于 `hermes tools` 选择器的元数据——设置时提示的键。
        return {
            "name": "My Backend",
            "badge": "paid",        # 可选；在选择器中作为短标签显示
            "tag": "名称下方显示的一行描述",
            "env_vars": [
                {
                    "key": "MY_BACKEND_API_KEY",
                    "prompt": "My Backend API 密钥",
                    "url": "https://my-backend.example.com/api-keys",
                },
            ],
        }

    def capabilities(self) -> Dict[str, Any]:
        # 声明此后端是否支持图像到图像 / 编辑。
        # 工具层在动态模式中暴露这些信息，以便模型知道何时启用 `image_url`。默认（如果省略）是仅文本：{"modalities": ["text"], "max_reference_images": 0}。
        return {"modalities": ["text", "image"], "max_reference_images": 4}

    def generate(
        self,
        prompt: str,
        aspect_ratio: str = DEFAULT_ASPECT_RATIO,
        *,
        image_url: Optional[str] = None,
        reference_image_urls: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        prompt = (prompt or "").strip()
        aspect_ratio = resolve_aspect_ratio(aspect_ratio)

        if not prompt:
            return error_response(
                error="提示词是必需的",
                error_type="invalid_input",
                provider=self.name,
                prompt="",
                aspect_ratio=aspect_ratio,
            )

        # 路由：如果设置了 image_url（或 reference_image_urls），则调用是图像到图像 / 编辑请求；否则是文本到图像。在 success_response 的 `modality` 字段中报告所采用的路径。
        sources = []
        if image_url:
            sources.append(image_url)
        sources.extend(normalize_reference_images(reference_image_urls) or [])
        modality = "image" if sources else "text"

        # 模型选择优先级：环境变量 → 配置 → 默认值。内置 openai 插件中的 _resolve_model() 辅助函数是一个好的参考。
        model_id = kwargs.get("model") or self.default_model() or "my-model-fast"

        try:
            import my_backend_sdk
            client = my_backend_sdk.Client(api_key=os.environ["MY_BACKEND_API_KEY"])
            if modality == "image":
                result = client.edit(
                    prompt=prompt,
                    model=model_id,
                    image_urls=sources,
                )
            else:
                result = client.generate(
                    prompt=prompt,
                    model=model_id,
                    aspect_ratio=aspect_ratio,
                )

            # 支持两种格式：
            #   - URL 字符串：直接以 `image` 返回
            #   - base64 数据：通过 save_b64_image() 保存到 $HERMES_HOME/cache/images/
            if result.get("image_b64"):
                path = save_b64_image(
                    result["image_b64"],
                    prefix=self.name,
                    extension="png",
                )
                image = str(path)
            else:
                image = result["image_url"]

            return success_response(
                image=image,
                model=model_id,
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                provider=self.name,
                modality=modality,
            )
        except Exception as exc:
            return error_response(
                error=str(exc),
                error_type=type(exc).__name__,
                provider=self.name,
                model=model_id,
                prompt=prompt,
                aspect_ratio=aspect_ratio,
            )


def register(ctx) -> None:
    """插件入口点——加载时调用一次。"""
    ctx.register_image_gen_provider(MyBackendImageGenProvider())
```

## plugin.yaml

```yaml
name: my-backend
version: 1.0.0
description: 我的图像后端——通过 My Backend SDK 进行文本到图像生成
author: Your Name
kind: backend
requires_env:
  - MY_BACKEND_API_KEY
```

`kind: backend` 将插件路由到图像生成注册路径。`requires_env` 在 `hermes plugins install` 期间会被提示。

## 抽象基类（ABC）参考

完整合约在 `agent/image_gen_provider.py` 中。你通常会覆盖的方法：

| 成员 | 是否必需 | 默认值 | 用途 |
|---|---|---|---|
| `name` | ✅ | — | 用于 `image_gen.provider` 配置的稳定标识符 |
| `display_name` | — | `name.title()` | 在 `hermes tools` 中显示的标签 |
| `is_available()` | — | `True` | 检查缺失凭据/依赖的门控 |
| `list_models()` | — | `[]` | `hermes tools` 模型选择器的目录 |
| `default_model()` | — | 来自 `list_models()` 的第一个 | 当没有配置模型时的回退 |
| `get_setup_schema()` | — | 最小化 | 选择器元数据 + 环境变量提示 |
| `generate(prompt, aspect_ratio, **kwargs)` | ✅ | — | 实际的调用 |

## 响应格式

`generate()` 必须返回通过 `success_response()` 或 `error_response()` 构建的字典。两者都位于 `agent/image_gen_provider.py` 中。

**成功：**
```python
success_response(
    image=<url-或-绝对路径>,
    model=<模型-id>,
    prompt=<回显的提示词>,
    aspect_ratio="landscape" | "square" | "portrait",
    provider=<你的提供者名称>,
    extra={...},  # 可选，后端特定字段
)
```

**错误：**
```python
error_response(
    error="人类可读的消息",
    error_type="provider_error" | "invalid_input" | "<异常类名>",
    provider=<你的提供者名称>,
    model=<模型-id>,
    prompt=<提示词>,
    aspect_ratio=<解析后的宽高比>,
)
```

工具包装器将字典 JSON 序列化后交给 LLM。错误会作为工具结果呈现；LLM 决定如何向用户解释。

## 处理 base64 与 URL 输出

某些后端返回图像 URL（fal、Replicate）；其他返回 base64 负载（OpenAI gpt-image-2）。对于 base64 的情况，使用 `save_b64_image()`——它会写入 `$HERMES_HOME/cache/images/<prefix>_<timestamp>_<uuid>.<ext>` 并返回绝对 `Path`。将该路径（作为 `str`）作为 `image=` 参数传递给 `success_response()`。网关传递（Telegram 图片气泡、Discord 附件）可以识别 URL 和绝对路径。

## 用户覆盖

将用户插件放到 `~/.hermes/plugins/image_gen/<name>/` 目录下，使用与内置插件相同的 `name` 属性，并通过 `hermes plugins enable <name>` 启用——注册表是最后写入者获胜，因此你的版本会替换内置版本。这对于将 `openai` 插件指向私有代理，或替换自定义模型目录非常有用。

## 测试

```bash
export HERMES_HOME=/tmp/hermes-imggen-test
mkdir -p $HERMES_HOME/plugins/image_gen/my-backend
# …将 __init__.py + plugin.yaml 复制到该目录…

export MY_BACKEND_API_KEY=your-test-key
hermes plugins enable my-backend

# 将其选为活跃提供者
echo "image_gen:" >> $HERMES_HOME/config.yaml
echo "  provider: my-backend" >> $HERMES_HOME/config.yaml

# 练习它
hermes -z "生成一张穿太空服的柯基犬图像"
```

或交互式：`hermes tools` → "Image Generation" → 选择 `my-backend` → 如果提示，输入 API 密钥。

## 参考实现

- **`plugins/image_gen/openai/__init__.py`** — 将 gpt-image-2 的低/中/高等级别作为三个虚拟模型 ID 共享一个 API 模型，但使用不同的 `quality` 参数。这是一个很好的例子，展示在同一后端下的层级模型以及 config.yaml 优先级链。
- **`plugins/image_gen/xai/__init__.py`** — 通过 xAI 的 Grok Imagine。不同形状（URL 输出，更简单的目录）。
- **`plugins/image_gen/openai-codex/__init__.py`** — Codex 风格的 Responses API 变体，重用 OpenAI SDK 但使用不同的路由基础 URL。

## 通过 pip 分发

```toml
# pyproject.toml
[project.entry-points."hermes_agent.plugins"]
my-backend-imggen = "my_backend_imggen_package"
```

`my_backend_imggen_package` 必须暴露一个顶层的 `register` 函数。请参阅通用插件指南中的[通过 pip 分发](/guides/build-a-hermes-plugin#distribute-via-pip)以获得完整设置。

## 相关页面

- [图像生成](/user-guide/features/image-generation) — 面向用户的特性文档
- [插件概述](/user-guide/features/plugins) — 所有插件类型一览
- [构建一个 Hermes 插件](/guides/build-a-hermes-plugin) — 通用工具/钩子/斜杠命令指南