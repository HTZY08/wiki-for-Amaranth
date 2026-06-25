---
title: Searxng Search
---

title: "Searxng 搜索 — 通过 SearXNG 免费元搜索 — 聚合 70 多个搜索引擎的结果"
sidebar_label: "Searxng 搜索"
description: "通过 SearXNG 免费元搜索 — 聚合 70 多个搜索引擎的结果"
---

--- body ---
{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Searxng 搜索

通过 SearXNG 免费元搜索 — 聚合 70 多个搜索引擎的结果。可自行托管或使用公共实例。无需 API 密钥。当 Web 搜索工具集不可用时自动回退。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/research/searxng-search` 安装 |
| 路径 | `optional-skills/research/searxng-search` |
| 版本 | `1.0.0` |
| 作者 | hermes-agent |
| 许可协议 | MIT |
| 平台 | linux, macos |
| 标签 | `search`, `searxng`, `meta-search`, `self-hosted`, `free`, `fallback` |
| 相关技能 | [`duckduckgo-search`](/docs/user-guide/skills/optional/research/research-duckduckgo-search), [`domain-intel`](/docs/user-guide/skills/optional/research/research-domain-intel) |

## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。当技能激活时，智能体（Agent）会看到这些指令。
:::

# SearXNG 搜索

使用 [SearXNG](https://searxng.org/) 的免费元搜索 —— 一个尊重隐私、自行托管的搜索聚合器，可同时查询 70 多个搜索引擎。

**使用公共实例时无需 API 密钥**。也可以自行托管以完全控制。当主 Web 搜索工具集（`FIRECRAWL_API_KEY`）未配置时，会自动作为回退方案出现。

## 配置

SearXNG 需要一个 `SEARXNG_URL` 环境变量指向你的 SearXNG 实例：

```bash
# 公共实例（无需设置）
SEARXNG_URL=https://searxng.example.com

# 自行托管的 SearXNG
SEARXNG_URL=http://localhost:8888
```

如果未配置实例，此技能将不可用，智能体将回退到其他搜索选项。

## 检测流程

在选择方法前检查实际可用性：

```bash
# 检查是否设置了 SEARXNG_URL 并且实例可访问
curl -s --max-time 5 "${SEARXNG_URL}/search?q=test&format=json" | head -c 200
```

决策树：
1. 如果设置了 `SEARXNG_URL` 且实例响应，则使用 SearXNG
2. 如果 `SEARXNG_URL` 未设置或不可达，则回退到其他可用搜索工具
3. 如果用户明确要求 SearXNG，则帮助他们设置实例或寻找公共实例

## 方法一：通过 curl 的 CLI（推荐）

使用 `terminal` 中的 `curl` 调用 SearXNG JSON API。这避免假设安装了特定的 Python 包。

```bash
# 文本搜索（JSON 输出）
curl -s --max-time 10 \
  "${SEARXNG_URL}/search?q=python+async+programming&format=json&engines=google,bing&limit=10"

# 关闭安全搜索
curl -s --max-time 10 \
  "${SEARXNG_URL}/search?q=example&format=json&safesearch=0"

# 特定类别（general, news, science 等）
curl -s --max-time 10 \
  "${SEARXNG_URL}/search?q=AI+news&format=json&categories=news"
```

### 常见 CLI 标志

| 标志 | 描述 | 示例 |
|------|------|------|
| `q` | 查询字符串（URL 编码） | `q=python+async` |
| `format` | 输出格式：`json`, `csv`, `rss` | `format=json` |
| `engines` | 逗号分隔的引擎名称 | `engines=google,bing,ddg` |
| `limit` | 每个引擎的最大结果数（默认 10） | `limit=5` |
| `categories` | 按类别筛选 | `categories=news,science` |
| `safesearch` | 0=关闭, 1=中等, 2=严格 | `safesearch=0` |
| `time_range` | 时间筛选：`day`, `week`, `month`, `year` | `time_range=week` |

### 解析 JSON 结果

```bash
# 从 JSON 提取标题和 URL
curl -s --max-time 10 "${SEARXNG_URL}/search?q=fastapi&format=json&limit=5" \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
for r in data.get('results', []):
    print(r.get('title',''))
    print(r.get('url',''))
    print(r.get('content','')[:200])
    print()
"
```

每个结果返回：`title`, `url`, `content`（摘要）, `engine`, `parsed_url`, `img_src`, `thumbnail`, `author`, `published_date`

## 方法二：通过 `requests` 的 Python API

直接使用 Python 的 `requests` 库调用 SearXNG REST API：

```python
import os, requests, urllib.parse

base_url = os.environ.get("SEARXNG_URL", "")
if not base_url:
    raise RuntimeError("SEARXNG_URL is not set")

query = "fastapi deployment guide"
params = {
    "q": query,
    "format": "json",
    "limit": 5,
    "engines": "google,bing",
}

resp = requests.get(f"{base_url}/search", params=params, timeout=10)
resp.raise_for_status()
data = resp.json()

for r in data.get("results", []):
    print(r["title"])
    print(r["url"])
    print(r.get("content", "")[:200])
    print()
```

## 方法三：searxng-data Python 包

如需更结构化的访问方式，可安装 `searxng-data` 包：

```bash
pip install searxng-data
```

```python
from searxng_data import engines

# 列出可用的引擎
print(engines.list_engines())
```

注意：此包只提供引擎元数据，不提供搜索 API 本身。

## 自行托管 SearXNG

运行你自己的 SearXNG 实例：

```bash
# 使用 Docker
docker run -d -p 8888:8080 \
  -v $(pwd)/searxng:/etc/searxng \
  searxng/searxng:latest

# 然后设置
SEARXNG_URL=http://localhost:8888
```

或通过 pip 安装：
```bash
pip install searxng
# 编辑 /etc/searxng/settings.yml
searxng-run
```

公共 SearXNG 实例可访问：
- `https://searxng.example.com`（替换为任意公共实例）

## 工作流程：搜索并提取

SearXNG 返回标题、URL 和摘要 —— 而非完整页面内容。要获取完整页面内容，需先搜索，然后使用 `web_extract`、浏览器工具或 `curl` 提取最相关的 URL。

```bash
# 搜索相关页面
curl -s "${SEARXNG_URL}/search?q=fastapi+deployment&format=json&limit=3"
# 输出：包含标题和 URL 的结果列表

# 然后使用 web_extract 提取最佳 URL
```

## 限制

- **实例可用性**：如果 SearXNG 实例宕机或不可达，搜索将失败。始终检查 `SEARXNG_URL` 是否设置且实例可访问。
- **无内容提取**：SearXNG 返回摘要而非完整页面内容。使用 `web_extract`、浏览器工具或 `curl` 获取完整文章。
- **速率限制**：某些公共实例会限制请求。自行托管可避免此问题。
- **引擎覆盖范围**：可用引擎取决于 SearXNG 实例配置。某些引擎可能被禁用。
- **结果时效性**：元搜索聚合外部引擎 —— 结果时效性取决于这些引擎。

## 故障排除

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| `SEARXNG_URL` 未设置 | 未配置实例 | 使用公共 SearXNG 实例或自行设置 |
| 连接被拒绝 | 实例未运行或 URL 错误 | 检查 URL 是否正确且实例正在运行 |
| 结果为空 | 实例阻止了该查询 | 尝试其他实例或自行托管 |
| 响应缓慢 | 公共实例负载过高 | 自行托管或使用负载较低的公共实例 |
| 不支持 `json` 格式 | SearXNG 版本过旧 | 尝试 `format=rss` 或升级 SearXNG |

## 易错点

- **始终设置 `SEARXNG_URL`**：否则技能无法运行。
- **对查询进行 URL 编码**：在 curl 中，空格和特殊字符必须进行 URL 编码；或在 Python 中使用 `urllib.parse.quote()`。
- **使用 `format=json`**：默认格式可能不可读。始终明确请求 JSON。
- **设置超时**：始终使用 `--max-time` 或 `timeout=` 以避免在不可达实例上挂起。
- **自行托管最佳**：公共实例可能宕机、限速或屏蔽。自行托管的实例更可靠。

## 实例发现

如果 `SEARXNG_URL` 未设置且用户询问 SearXNG，帮助他们：
1. 寻找公共 SearXNG 实例（搜索“public searxng instance”）
2. 使用 Docker 或 pip 自行设置

公共实例列表在：https://searxng.org/