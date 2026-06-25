---
title: Web Search
---

## 可选技能：`searxng-search`

对于需要通过 `curl` 直接使用 SearXNG 的代理（Agent）（例如在网页工具集不可用时作为备用），请安装 `searxng-search` 可选技能：

```bash
hermes skills install official/research/searxng-search
```

此技能会教导代理（Agent）如何：
- 通过 `curl` 或 Python 调用 SearXNG JSON API
- 按分类（`general`、`news`、`science` 等）过滤
- 处理分页和错误情况
- 在 SearXNG 不可达时优雅地回退