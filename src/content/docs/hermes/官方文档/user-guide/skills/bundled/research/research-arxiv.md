--- frontmatter ---
---

## Semantic Scholar（引文、相关论文、作者简介）

arXiv 不提供引文数据或推荐。使用 **Semantic Scholar API** 来获取这些信息——免费、基础使用无需密钥（1 次请求/秒），返回 JSON 格式。

### 获取论文详情 + 引文

```bash
# 按 arXiv ID 查询
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2402.03300?fields=title,authors,citationCount,referenceCount,influentialCitationCount,year,abstract" | python3 -m json.tool

# 按 Semantic Scholar 论文 ID 或 DOI 查询
curl -s "https://api.semanticscholar.org/graph/v1/paper/DOI:10.1234/example?fields=title,citationCount"
```

### 获取某篇论文的被引情况（哪些论文引用了它）

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2402.03300/citations?fields=title,authors,year,citationCount&limit=10" | python3 -m json.tool
```

### 获取某篇论文的参考文献（它引用了哪些论文）

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2402.03300/references?fields=title,authors,year,citationCount&limit=10" | python3 -m json.tool
```

### 搜索论文（作为 arXiv 搜索的替代，返回 JSON）

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=GRPO+reinforcement+learning&limit=5&fields=title,authors,year,citationCount,externalIds" | python3 -m json.tool
```

### 获取论文推荐

```bash
curl -s -X POST "https://api.semanticscholar.org/recommendations/v1/papers/" \
  -H "Content-Type: application/json" \
  -d '{"positivePaperIds": ["arXiv:2402.03300"], "negativePaperIds": []}' | python3 -m json.tool
```

### 作者简介

```bash
curl -s "https://api.semanticscholar.org/graph/v1/author/search?query=Yann+LeCun&fields=name,hIndex,citationCount,paperCount" | python3 -m json.tool
```

### 有用的 Semantic Scholar 字段

`title`（标题）、`authors`（作者）、`year`（年份）、`abstract`（摘要）、`citationCount`（引文数）、`referenceCount`（参考文献数）、`influentialCitationCount`（有影响力的引文数）、`isOpenAccess`（是否开放获取）、`openAccessPdf`（开放获取 PDF 链接）、`fieldsOfStudy`（研究领域）、`publicationVenue`（发表场所）、`externalIds`（外部 ID，包含 arXiv ID、DOI 等）

---

--- body ---
## 完整研究流程

1. **发现**：`python scripts/search_arxiv.py "你的主题" --sort date --max 10`
2. **评估影响力**：`curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:ID?fields=citationCount,influentialCitationCount"`
3. **阅读摘要**：`web_extract(urls=["https://arxiv.org/abs/ID"])`
4. **阅读全文**：`web_extract(urls=["https://arxiv.org/pdf/ID"])`
5. **查找相关工作**：`curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:ID/references?fields=title,citationCount&limit=20"`
6. **获取推荐**：POST 到 Semantic Scholar 推荐端点
7. **追踪作者**：`curl -s "https://api.semanticscholar.org/graph/v1/author/search?query=姓名"`

## 速率限制

| API | 速率 | 认证 |
|-----|------|------|
| arXiv | ~1 次请求 / 3 秒 | 无需 |
| Semantic Scholar | 1 次请求 / 秒 | 无需（使用 API 密钥可达 100 次/秒） |

## 注意事项

- arXiv 返回 Atom XML——使用辅助脚本或解析片段以获得干净输出
- Semantic Scholar 返回 JSON——通过 `python3 -m json.tool` 管道输出以增强可读性
- arXiv ID：旧格式（`hep-th/0601001`）与新格式（`2402.03300`）
- PDF：`https://arxiv.org/pdf/{id}`——摘要：`https://arxiv.org/abs/{id}`
- HTML（如果可用）：`https://arxiv.org/html/{id}`
- 如需本地 PDF 处理，请参见技能（skill）`ocr-and-documents`

## ID 版本管理

- `arxiv.org/abs/1706.03762` 始终解析为**最新**版本
- `arxiv.org/abs/1706.03762v1` 指向**特定**不可变版本
- 生成引文时，保留你实际阅读的版本后缀，以防止引文漂移（后续版本可能大幅更改内容）
- API `<id>` 字段返回带版本号的 URL（例如 `http://arxiv.org/abs/1706.03762v7`）

## 撤稿论文

论文在提交后可能被撤稿。此时：
- `<summary>` 字段包含撤稿通知（查找 "withdrawn" 或 "retracted"）
- 元数据字段可能不完整
- 在将结果视为有效论文前，务必检查摘要