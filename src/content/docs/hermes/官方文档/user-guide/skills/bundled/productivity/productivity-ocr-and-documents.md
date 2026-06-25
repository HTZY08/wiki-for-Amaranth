--- frontmatter ---

--- body ---
## Arxiv论文

```
# 仅摘要（快速）
web_extract(urls=["https://arxiv.org/abs/2402.03300"])

# 全文
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])

# 搜索
web_search(query="arxiv GRPO reinforcement learning 2026")
```

## 分割、合并与搜索

pymupdf 原生支持这些操作——使用 `execute_code` 或内联 Python：

```python
# 分割：提取第1-5页生成新PDF
import pymupdf
doc = pymupdf.open("report.pdf")
new = pymupdf.open()
for i in range(5):
    new.insert_pdf(doc, from_page=i, to_page=i)
new.save("pages_1-5.pdf")
```

```python
# 合并多个PDF
import pymupdf
result = pymupdf.open()
for path in ["a.pdf", "b.pdf", "c.pdf"]:
    result.insert_pdf(pymupdf.open(path))
result.save("merged.pdf")
```

```python
# 在所有页面中搜索文本
import pymupdf
doc = pymupdf.open("report.pdf")
for i, page in enumerate(doc):
    results = page.search_for("revenue")
    if results:
        print(f"第{i+1}页：{len(results)}个匹配项")
        print(page.get_text("text"))
```

无需额外依赖——pymupdf 一个包即可覆盖分割、合并、搜索和文本提取。

---

## 注意

- `web_extract` 始终是处理 URL 的首选
- pymupdf 是安全默认选项——即时可用，无需模型，随处运行
- marker-pdf 用于 OCR、扫描文档、公式、复杂布局——仅在需要时安装
- 两个辅助脚本均可通过 `--help` 查看完整用法
- marker-pdf 首次使用时会下载约 2.5GB 模型至 `~/.cache/huggingface/`
- 处理 Word 文档：`pip install python-docx`（优于 OCR——可解析实际结构）
- 处理 PowerPoint：请参见 `powerpoint` 技能（使用 python-pptx）