---
sidebar_position: 12
title: "Web搜索提供者插件"
description: "如何为Hermes Agent构建一个web搜索/提取/爬取的后端插件"
---

# 构建Web搜索提供者插件

Web搜索提供者插件注册一个后端，服务于`web_search`、`web_extract`以及（可选）深度爬取工具调用。内置提供者——Firecrawl、SearXNG、Tavily、Exa、Parallel、Brave Search（免费版）、xAI和DDGS——均作为插件位于`plugins/web/<name>/`下。你可以通过在其旁边放置一个目录来添加新插件或覆盖捆绑插件。

:::tip
Web搜索是Hermes支持的几种**后端插件**之一。其他插件（各有自己的ABC）包括[图片生成提供者插件](/developer-guide/image-gen-provider-plugin)、[视频生成提供者插件](/developer-guide/video-gen-provider-plugin)、[记忆提供者插件](/developer-guide/memory-provider-plugin)、[上下文引擎插件](/developer-guide/context-engine-plugin)和[模型提供者插件](/developer-guide/model-provider-plugin)。通用工具/钩子/CLI插件请参阅[构建Hermes插件](/guides/build-a-hermes-plugin)。
:::

## 发现机制原理

Hermes在三个位置扫描Web搜索后端：

1. **捆绑** — `<repo>/plugins/web/<name>/`（自动加载，带有`kind: backend`，始终可用）
2. **用户** — `~/.hermes/plugins/web/<name>/`（通过`plugins.enabled`或`hermes plugins enable <name>`选择启用）
3. **Pip** — 声明了`hermes_agent.plugins`入口点的包

每个插件的`register(ctx)`函数调用`ctx.register_web_search_provider(...)`——这将实例注册到`agent/web_search_registry.py`中。每个能力（capability）的活动提供者通过配置选择：

| 能力 | 配置键 | 回退到 |
|---|---|---|
| `web_search` | `web.search_backend` | `web.backend` |
| `web_extract` | `web.extract_backend` | `web.backend` |
| `web_extract`内的深度爬取模式 | `web.extract_backend` | `web.backend` |

当两个键都未设置时，Hermes根据环境中存在的API密钥/URL自动检测后端。`hermes tools`会引导用户进行选择。

## 目录结构

```
plugins/web/my-backend/
├── __init__.py     # register() 入口点
├── provider.py     # WebSearchProvider 子类
└── plugin.yaml     # 清单，包含 kind: backend 和 provides_web_providers
```

`brave_free/`和`ddgs/`是树中最小的参考实现——`brave_free`是一个需要API密钥的纯搜索提供者，`ddgs`是一个无需密钥、延迟安装其SDK的提供者。

## WebSearchProvider ABC

继承`agent.web_search_provider.WebSearchProvider`。唯一必需的成员是`name`、`is_available()`以及你实现的`search()` / `extract()`中的任意一个。（深度爬取不是独立方法——它是`extract()`的一种模式。）

```python
# plugins/web/my-backend/provider.py
from __future__ import annotations

import os
from typing import Any, Dict, List

from agent.web_search_provider import WebSearchProvider


class MyBackendWebSearchProvider(WebSearchProvider):
    """针对My Backend HTTP API的最小化纯搜索提供者。"""

    @property
    def name(self) -> str:
        # 用于web.search_backend / web.extract_backend / web.backend
        # 配置键的稳定标识符。小写，无空格；允许连字符。
        return "my-backend"

    @property
    def display_name(self) -> str:
        # 在`hermes tools`中显示的人类可读标签。默认为`name`。
        return "My Backend"

    def is_available(self) -> bool:
        # 廉价检查——环境变量是否存在、可选依赖是否可导入等。
        # 绝对不能进行网络调用（每次`hermes tools`渲染时都会运行）。
        return bool(os.getenv("MY_BACKEND_API_KEY", "").strip())

    def supports_search(self) -> bool:
        return True

    def supports_extract(self) -> bool:
        return False

    def search(self, query: str, limit: int = 5) -> Dict[str, Any]:
        import httpx

        api_key = os.environ["MY_BACKEND_API_KEY"]
        try:
            resp = httpx.get(
                "https://api.example.com/search",
                params={"q": query, "count": max(1, min(int(limit), 20))},
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as exc:
            return {"success": False, "error": str(exc)}

        # 响应形状是固定的——参见下文"响应形状"。
        return {
            "success": True,
            "data": {
                "web": [
                    {
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "description": item.get("snippet", ""),
                        "position": idx + 1,
                    }
                    for idx, item in enumerate(data.get("results", []))
                ],
            },
        }
```

```python
# plugins/web/my-backend/__init__.py
from plugins.web.my_backend.provider import MyBackendWebSearchProvider


def register(ctx) -> None:
    """插件入口点——加载时调用一次。"""
    ctx.register_web_search_provider(MyBackendWebSearchProvider())
```

## plugin.yaml

```yaml
name: web-my-backend
version: 1.0.0
description: "My Backend web search — Bearer-auth REST API"
author: Your Name
kind: backend
provides_web_providers:
  - my-backend
requires_env:
  - MY_BACKEND_API_KEY
```

| 键 | 用途 |
|---|---|
| `kind: backend` | 将插件路由到后端加载路径 |
| `provides_web_providers` | 此插件注册的提供者`name`列表——加载器使用它在`hermes tools`中宣传插件，甚至早于`register()`运行 |
| `requires_env` | 在`hermes plugins install`期间的交互式凭据提示（完整格式请参阅[构建Hermes插件](/guides/build-a-hermes-plugin#gate-on-environment-variables)） |

## ABC参考

完整契约在`agent/web_search_provider.py`中。你可以重写的方法：

| 成员 | 必需 | 默认值 | 用途 |
|---|---|---|---|
| `name` | ✅ | — | 在`web.*_backend`配置中使用的稳定标识符 |
| `display_name` | — | `name` | 在`hermes tools`中显示的标签 |
| `is_available()` | ✅ | — | 廉价可用性门控——环境变量、可选依赖 |
| `supports_search()` | — | `True` | 用于`web_search`路由的能力标志 |
| `supports_extract()` | — | `False` | 用于`web_extract`路由的能力标志 |
| `search(query, limit)` | 条件 | 抛出异常 | 当`supports_search()`返回`True`时必需 |
| `extract(urls, **kwargs)` | 条件 | 抛出异常 | 当`supports_extract()`返回`True`时必需 |

提供者可以从单个类中提供多种能力——Firecrawl、Tavily、Exa和Parallel都实现了搜索和提取。Brave Search和DDGS仅提供搜索；SearXNG仅提供搜索，并带有文档化的"配对提取提供者"工作流程。

## 响应形状

工具包装器期望一个固定的信封，因此它不需要在后端之间进行转换。

**搜索成功：**

```python
{
    "success": True,
    "data": {
        "web": [
            {"title": str, "url": str, "description": str, "position": int},
            ...
        ],
    },
}
```

**提取成功：**

```python
{
    "success": True,
    "data": [
        {
            "url": str,
            "title": str,
            "content": str,
            "raw_content": str,
            "metadata": dict,    # 可选
            "error": str,        # 可选，仅在单个URL失败时
        },
        ...
    ],
}
```

**任一能力失败时：**

```python
{"success": False, "error": "人类可读的消息"}
```

`search()`和`extract()`都可以是`async def`——调度器通过`inspect.iscoroutinefunction`检测协程函数并相应地进行等待。对于小型后端，执行阻塞I/O（HTTP、SDK调用）的同步实现是可以的；调度器会处理线程。

## 能力标志

Hermes根据`supports_*`标志将调用路由到正确的提供者。一个常见的多提供者设置：

```yaml
# ~/.hermes/config.yaml
web:
  search_backend: "brave-free"     # 仅搜索，快速，免费每月2000次
  extract_backend: "firecrawl"     # 提取 + 爬取，付费配额
```

当`web.search_backend`或`web.extract_backend`未设置时，两者都回退到`web.backend`。当后者也未设置时，Hermes根据环境变量是否存在，选择第一个支持请求能力的可用提供者。

如果你的提供者仅支持一种能力，请将其他标志保留为默认值（`False`），注册表将跳过该工具——当用户仅使用X进行搜索却要求代理进行提取时，不会出现误导性的"提供者X失败"错误。

## Hermes如何将其接入工具

`web_search`和`web_extract`工具位于`tools/web_tools.py`中。在调用时，它们：

1. 读取相关的配置键（`web.search_backend`用于`web_search`，`web.extract_backend`用于`web_extract`）
2. 向注册表请求具有该`name`的提供者
3. 检查`is_available()`和匹配的`supports_*()`标志
4. 调度到`search()` / `extract()`（深度爬取作为`extract()`内部的一种模式运行），如果方法是协程则等待
5. 对响应信封进行JSON序列化并返回给LLM

错误作为工具结果呈现；LLM决定如何解释它们。如果没有注册提供者（或所有可用提供者都未通过能力门控），则工具返回一个有用的错误，指向`hermes tools`。

## 延迟安装可选依赖

如果你的提供者包装了第三方SDK（如DDGS对`ddgs`包所做的那样），不要在模块顶层`import`它。在`is_available()`或`search()`内部使用`tools.lazy_deps.ensure(...)`——Hermes将在首次使用时安装该包，由`security.allow_lazy_installs`门控。关于安全模型，请参阅[构建Hermes插件 → 延迟安装](/guides/build-a-hermes-plugin#lazy-install-optional-python-dependencies)。

## 参考实现

- **`plugins/web/brave_free/`** — 小型、需要API密钥、纯搜索的HTTP提供者。良好的起始模板。
- **`plugins/web/ddgs/`** — 无需密钥、延迟安装其SDK的提供者。对于包装Python包的后端而言，有用的模式。
- **`plugins/web/firecrawl/`** — 完整的多能力提供者（搜索+提取+爬取），支持多种格式模式。
- **`plugins/web/searxng/`** — 自托管、URL配置、无需认证的后端。
- **`plugins/web/xai/`** — 基于LLM的搜索，通过Grok的服务器端`web_search`工具实现。展示了如何重用已有的OAuth/环境变量凭据表面（`tools/xai_http.py`），而无需添加新的环境变量，以及如何编写一个遵守无网络契约的廉价`is_available()`。

## 通过pip分发

```toml
# pyproject.toml
[project.entry-points."hermes_agent.plugins"]
my-backend-web = "my_backend_web_package"
```

`my_backend_web_package`必须公开一个顶层的`register`函数。完整设置请参阅通用插件指南中的[通过pip分发](/guides/build-a-hermes-plugin#distribute-via-pip)。

## 相关页面

- [Web搜索](/user-guide/features/web-search) — 面向用户的功能文档和每个后端的配置
- [插件概览](/user-guide/features/plugins) — 所有插件类型一览
- [构建Hermes插件](/guides/build-a-hermes-plugin) — 通用工具/钩子/斜杠命令指南