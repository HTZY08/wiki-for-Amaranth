#!/usr/bin/env python3
"""
Build Chinese academic PDF from markdown sections.
Usage: uv run python3 build_chinese_pdf.py

Requires: weasyprint, markdown-it-py
Edit the variables below for each new review project.
"""

import os
import re
from markdown_it import MarkdownIt
from weasyprint import HTML

# ===== EDIT THESE FOR EACH PROJECT =====
BASE = "/opt/data/reviews/<project-name>"
SECTIONS = [
    # Ordered list of .md files in sections/
    "01-introduction.md",
    "02-01-topic.md",
    "02-02-topic.md",
    "03-01-topic.md",
    "04-01-topic.md",
]
TITLE = "综述标题"
SUBTITLE = "——副标题"
# =======================================

# Read and combine all markdown
full_md_parts = []
for sec in SECTIONS:
    path = os.path.join(BASE, "sections", sec)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        full_md_parts.append(content)

full_md = "\n\n---\n\n".join(full_md_parts)

# Convert to HTML
md = MarkdownIt("commonmark", {"maxNesting": 20, "html": True})
html_body = md.render(full_md)

# CSS
html_full = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<style>
@page {{
    size: A4;
    margin: 2.5cm 2.5cm 2.5cm 2.5cm;
    @bottom-center {{
        content: counter(page);
        font-size: 10pt;
        font-family: "WenQuanYi Zen Hei", sans-serif;
        color: #666;
    }}
}}
body {{
    font-family: "WenQuanYi Zen Hei", "Noto Sans CJK SC", serif;
    font-size: 11pt;
    line-height: 1.8;
    color: #222;
    text-align: justify;
}}
h1 {{
    font-size: 16pt; font-weight: bold; color: #1a1a2e;
    margin-top: 1.5em; margin-bottom: 0.6em;
    border-bottom: 1px solid #ccc; padding-bottom: 0.3em;
    page-break-before: always;
}}
h1:first-of-type {{ page-break-before: auto; }}
h2 {{ font-size: 13pt; font-weight: bold; color: #333; margin-top: 1.2em; margin-bottom: 0.4em; }}
h3 {{ font-size: 11.5pt; font-weight: bold; color: #444; margin-top: 1em; margin-bottom: 0.3em; }}
p {{ margin: 0.4em 0; text-indent: 2em; }}
a {{ color: #2563eb; text-decoration: none; }}
ul, ol {{ margin: 0.3em 0; padding-left: 2em; }}
li {{ margin: 0.2em 0; }}
table {{ border-collapse: collapse; width: 100%; margin: 0.8em 0; }}
table th, table td {{ border: 1px solid #ccc; padding: 4px 8px; font-size: 10pt; }}
table th {{ background: #e8e8e8; font-weight: bold; }}
hr {{ border: none; border-top: 1px solid #ddd; margin: 1em 0; }}
.title-page {{
    text-align: center; padding-top: 6cm;
}}
.title-page h1 {{
    font-size: 22pt; border: none; margin-bottom: 0.5em; page-break-before: auto;
}}
.title-page .subtitle {{
    font-size: 14pt; color: #555; margin-top: 0.5em;
}}
.title-page .meta {{
    margin-top: 3em; font-size: 11pt; color: #777;
}}
</style>
</head>
<body>

<div class="title-page">
<h1>{TITLE}</h1>
<div class="subtitle">{SUBTITLE}</div>
<div class="meta">文献综述 · 2026</div>
</div>

{html_body}

</body>
</html>"""

html_path = os.path.join(BASE, "review.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_full)

pdf_path = os.path.join(BASE, "review.pdf")
print(f"Generating PDF ({len(full_md)} chars)...")
HTML(html_path).write_pdf(pdf_path)
print(f"Done: {pdf_path} ({os.path.getsize(pdf_path) / 1024:.0f} KB)")
