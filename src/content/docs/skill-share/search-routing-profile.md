---
title: Search Routing Profile
description: Hermes 搜索路由栈 — 多引擎自动降级、模式路由、Key 轮换
---

# Unified Search Routing

Hermes Agent 的完整搜索路由架构。覆盖 MCP 统一搜索、原生 web_search、公共 API 路由三层，自动按模式选引擎、按失败降级、多 Key 轮换。

## 架构总览

```
用户搜索请求
    ↓
┌─ MCP 统一搜索 (mcp_mcp_search_mcp) ───────────────────┐
│  按 mode 选首引擎 → 失败自动降级 → 返回结果             │
│  modes: auto / fast / zh / news / academic / deep      │
│        full_content / crawl / google / fallback         │
└────────────────────────────────────────────────────────┘
┌─ 原生 web_search ──────────────────────────────────────┐
│  走 config.yaml → web.backend: tavily (1000次/月)      │
│  适合：简单查询、快速问答                                │
└────────────────────────────────────────────────────────┘
┌─ 公共 API 路由 (public-api-brain-router) ──────────────┐
│  意图匹配 → 调用免key公共API → 结构化数据做主干         │
│  覆盖：书籍/词典/论文/古籍/汇率/天气/地震/诗歌           │
└────────────────────────────────────────────────────────┘
```

## 一、MCP 统一搜索（推荐入口）

MCP 搜索服务器 `mcp_search_server.py` 聚合 9 个引擎，按 mode 自动选首引擎，失败自动降级。

### 调用方式

| 场景 | mode | 示例 |
|------|------|------|
| 通用搜索 | `auto` | `mcp_mcp_search_mcp(query="...")` |
| 快速查询 | `fast` | 同上，mode 参数省略时默认 auto |
| 中文内容 | `zh` | 优先走 AnySearch（中文友好） |
| 新闻 | `news` | 优先走 You.com |
| 学术/深度 | `academic` / `deep` | 优先走 Exa |
| 全文抓取 | `full_content` / `crawl` | 优先走 Firecrawl |
| Google 风格 | `google` | 优先走 Serper |
| 兜底 | `fallback` | 直接走 DuckDuckGo |

### 引擎排序与降级链

`auto` 模式引擎顺序（依次尝试，前一个失败自动降级到下一个）：

```
tinyfish → perplexity → anysearch → firecrawl → youcom → exa → tavily → serper → duckduckgo
```

### 各 Mode 首引擎

| mode | 首引擎 | 说明 |
|------|--------|------|
| auto | tinyfish | 免费自由层，5次/分钟 |
| fast | tinyfish | 同上 |
| zh | anysearch | 中文搜索结果好 |
| news | youcom | 新闻类结果 |
| academic | exa | 学术论文搜索 |
| deep | exa | 深度研究 |
| full_content | firecrawl | 全页抓取 |
| crawl | firecrawl | 批量爬取 |
| google | serper | Google 搜索结果 |
| fallback | duckduckgo | 零成本兜底 |

### Key 轮换机制

支持多 Key 轮换，失败自动换下一个：

| 引擎 | Key 列表 |
|------|----------|
| anysearch | `ANYSEARCH_API_KEY_OUTLOOK`, `ANYSEARCH_API_KEY_GMAIL` |
| firecrawl | `FIRECRAWL_API_KEY_GOOGLE`, `FIRECRAWL_API_KEY_GITHUB` |
| youcom | `YOUCOM_API_KEY_GOOGLE`, `YOUCOM_API_KEY_APPLE` |
| tavily | `TAVILY_API_KEY_1`, `TAVILY_API_KEY_2`, `TAVILY_API_KEY_3` |
| exa | `EXA_API_KEY`, `EXA_API_KEY_2` |
| perplexity | `OPENROUTER_API_KEY`（单 Key） |
| serper | `SERPER_API_KEY`（单 Key） |

轮换算法：Round-robin，每个引擎失败后自动尝试下一个 Key，全部 Key 都失败才降级到下一个引擎。

## 二、原生 web_search

Hermes 内置的 `web_search` 工具，走 Tavily API。

```
config.yaml → web.backend: tavily
免费额度：1000 次/月
HTTPS 432 → 触发降级
```

适合快速问答、简单查询。耗尽时降级到 MCP 统一搜索。

## 三、公共 API 路由

免 Key 公共 API 直接查询，不走搜索引擎。适用于精确结构化数据场景。

| 领域 | API | 免 Key |
|------|-----|--------|
| 搜书 | OpenLibrary | ✅ |
| 查词典 | Free Dictionary | ✅ |
| 论文 | arXiv | ✅ |
| 古籍 | Chinese Text Project | ✅ |
| 电子书 | Gutendex | ✅ |
| 汇率 | Exchangerate API | ✅ |
| 地震 | USGS | ✅ |
| 诗歌 | PoetryDB | ✅ |
| IP 定位 | ip-api.com | ✅ |
| 论文元数据 | Crossref | ✅ |
| 天气 | Weatherstack | ❌ 需 Key |
| 新闻 | Mediastack | ❌ 需 Key |

降级链：免Key API → 需Key API → 搜索引擎兜底。

## 四、辅助搜索通道

### TinyFish

免费搜索（5次/分钟）+ 抓取（25 URL/分钟），基于自建 Chromium 集群渲染。

- 被集成到 MCP 搜索服务器的首层引擎
- Key 存储在 `~/.tinyfish-key`
- WSL/容器环境需代理，证书验证失败时 SSL 降级

### Bypass Paywall

绕过付费墙的 6 层递进方案：

```
r.jina.ai → Googlebot UA → Bingbot UA → Referer伪装 → AMP → archive.today → Google Cache
```

覆盖 NYT/WSJ/FT/Economist/Medium 等 50+ 付费站点。

## 五、搜索路由决策表

| 场景 | 推荐入口 | mode | 原因 |
|------|---------|------|------|
| 日常问答 | MCP 搜索 | auto | TinyFish 免费，降级链全 |
| 快速查资料 | MCP 搜索 | fast | 同上 |
| 中文内容 | MCP 搜索 | zh | AnySearch 中文结果好 |
| 找新闻 | MCP 搜索 | news | You.com 新闻优先 |
| 查论文 | MCP 搜索 | academic | Exa 学术搜索 |
| 深度调研 | MCP 搜索 | deep | Exa 多结果 |
| 提取全页 | MCP 搜索 | full_content | Firecrawl |
| 精确数据（书/词/汇率） | 公共 API 路由 | — | 免 Key，100% 准确 |
| web_search 可用 | 原生 web_search | — | Tavily，简单够用 |
| Tavily 额度耗尽 | 自动降级到 MCP 搜索 | auto | — |
| 所有 API 都挂 | DuckDuckGo | fallback | 零成本兜底 |

## 配置文件

| 文件 | 作用 |
|------|------|
| `/opt/data/config.yaml` | web.backend, web.search_backend |
| `/opt/data/scripts/mcp_search_server.py` | MCP 统一搜索服务器（9 引擎降级链 + Key 轮换） |
| `/opt/data/skills/software-development/public-api-brain-router/SKILL.md` | 公共 API 路由技能 |
| `/opt/data/skills/research/tinyfish-search-fetch/SKILL.md` | TinyFish 集成技能 |
| `~/.tinyfish-key` | TinyFish API Key |

## 已知限制

- TinyFish 自由层 5次/分钟 search，批量任务需间隔
- Tavily 1000次/月，超额后返回 432
- Serper 免费层 2500次/月（Google 搜索）
- Firecrawl 需代理访问
- 公共 API 部分有 Rate Limit
- 如需更多免费额度：每个 Tavily/AnySearch/Firecrawl Key 可注册多个免费账号，轮换使用
