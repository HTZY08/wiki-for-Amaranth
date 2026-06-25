--- frontmatter ---
---
frontmatter:
  title: 故障排除
  description: 针对 SearXNG 集成的常见问题及解决方法。
---

--- body ---
## 故障排除

### `web_search` 返回 `{"success": false}`

- 检查 `SEARXNG_URL` 是否可达：`curl -s "http://localhost:8888/search?q=test&format=json"`
- 如果得到 HTTP 403，说明 JSON 格式被禁用——在 `settings.yml` 的 `formats` 列表中添加 `json`，然后重启
- 如果出现连接错误，容器可能未运行：`docker ps | grep searxng`

### `web_extract` 提示 "search-only backend"

SearXNG 无法提取 URL 内容。将 `web.extract_backend` 设置为支持提取的提供商：

```yaml
web:
  search_backend: "searxng"
  extract_backend: "firecrawl"  # 或 tavily / exa / parallel
```

### SearXNG 返回 0 条结果

某些公共实例禁用了特定的搜索引擎或分类。尝试：
- 换一个查询词
- 从 [searx.space](https://searx.space/) 换一个公共实例
- 自行搭建实例以获得可靠的结果

### 公共实例受到速率限制

切换到自托管实例（参见上方 [选项 A](#option-a--self-host-with-docker-recommended)）。使用 Docker 搭建的实例没有速率限制。

### `web_extract` 返回截断的内容，并附带 "summarization timed out" 提示

辅助模型未能在配置的超时时间内完成摘要。请执行以下任一操作：

- 在 `config.yaml` 中提高 `auxiliary.web_extract.timeout` 的值（全新安装默认 360 秒，若此键缺失则默认为 30 秒）
- 将 `web_extract` 辅助任务切换为更快的模型（如 `google/gemini-3-flash-preview`）——参见 [web_extract 如何处理长页面](#how-web_extract-handles-long-pages)
- 对于不适合使用摘要的页面，改用 `browser_navigate`

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