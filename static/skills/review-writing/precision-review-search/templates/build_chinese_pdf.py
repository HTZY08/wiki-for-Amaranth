#!/usr/bin/env python3
"""Build an academic-format Chinese PDF from markdown section files.

Usage:
    uv run python3 build_chinese_pdf.py sections/*.md

Requirements:
    pip install weasyprint markdown-it-py  (via uv)

Requires:
    - Chinese font (WenQuanYi Zen Hei) installed on the system
    - markdown-it-py for MD→HTML conversion
    - weasyprint for HTML→PDF

Output: gold-nanomaterials-review.pdf in the current directory.
"""

import os, sys, re
from markdown_it import MarkdownIt
from weasyprint import HTML

def read_sections(file_pattern=None):
    """Read section files from sections/ directory, sorted numerically."""
    sections_dir = "sections"
    file_list = sorted(os.listdir(sections_dir)) if os.path.isdir(sections_dir) else []

    # Allow explicit file list from command line
    if len(sys.argv) > 1:
        file_list = sorted(sys.argv[1:])

    md_parts = []
    for fname in file_list:
        if not fname.endswith(".md"):
            continue
        path = os.path.join(sections_dir, fname) if not fname.startswith("/") else fname
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        md_parts.append(content)

    return "\n\n---\n\n".join(md_parts)


def md_to_html(markdown_text):
    """Convert markdown to HTML."""
    md = MarkdownIt("commonmark", {"maxNesting": 20, "html": True})
    return md.render(markdown_text)


def wrap_html(html_body, title="金纳米材料综述"):
    """Wrap HTML body in full document with Chinese academic CSS."""
    return f"""<!DOCTYPE html>
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
        font-family: "WenQuanYi Zen Hei", "Noto Sans CJK SC", sans-serif;
        color: #666;
    }}
}}
body {{
    font-family: "WenQuanYi Zen Hei", "Noto Sans CJK SC", "SimSun", serif;
    font-size: 11pt;
    line-height: 1.8;
    color: #222;
    text-align: justify;
}}
h1 {{
    font-size: 16pt;
    font-weight: bold;
    color: #1a1a2e;
    margin-top: 1.5em;
    margin-bottom: 0.6em;
    border-bottom: 1px solid #ccc;
    padding-bottom: 0.3em;
    page-break-before: always;
}}
h1:first-of-type {{
    page-break-before: auto;
}}
h2 {{
    font-size: 13pt;
    font-weight: bold;
    color: #333;
    margin-top: 1.2em;
    margin-bottom: 0.4em;
}}
h3 {{
    font-size: 11.5pt;
    font-weight: bold;
    color: #444;
    margin-top: 1em;
    margin-bottom: 0.3em;
}}
p {{
    margin: 0.4em 0;
    text-indent: 2em;
}}
strong {{ color: #000; }}
em {{ color: #555; }}
code {{
    font-family: "DejaVu Sans Mono", monospace;
    font-size: 9pt;
    background: #f4f4f4;
    padding: 1px 3px;
    border-radius: 2px;
}}
a {{ color: #2563eb; text-decoration: none; }}
ul, ol {{ margin: 0.3em 0; padding-left: 2em; }}
li {{ margin: 0.2em 0; }}
blockquote {{
    margin: 0.5em 0;
    padding: 0.3em 1em;
    border-left: 3px solid #ccc;
    color: #555;
    background: #f9f9f9;
}}
table {{ border-collapse: collapse; width: 100%; margin: 0.8em 0; }}
table th, table td {{
    border: 1px solid #ccc;
    padding: 4px 8px;
    font-size: 10pt;
}}
table th {{ background: #e8e8e8; font-weight: bold; }}
hr {{ border: none; border-top: 1px solid #ddd; margin: 1em 0; }}
.title-page {{
    text-align: center;
    padding-top: 6cm;
}}
.title-page h1 {{
    font-size: 22pt;
    border: none;
    margin-bottom: 0.5em;
    page-break-before: auto;
}}
.title-page .subtitle {{
    font-size: 14pt;
    color: #555;
    margin-top: 0.5em;
}}
.title-page .meta {{
    margin-top: 3em;
    font-size: 11pt;
    color: #777;
}}
</style>
</head>
<body>
<div class="title-page">
<h1>{title}</h1>
<div class="subtitle">文献综述</div>
<div class="meta">2026</div>
</div>
{html_body}
</body>
</html>"""


def main():
    markdown_text = read_sections()
    html_body = md_to_html(markdown_text)
    html_full = wrap_html(html_body)

    html_path = "output.html"
    pdf_path = "output.pdf"

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_full)

    print(f"Generating PDF ({len(markdown_text)} chars markdown)...")
    HTML(html_path).write_pdf(pdf_path)
    print(f"Done: {pdf_path} ({os.path.getsize(pdf_path) / 1024:.0f} KB)")

    # Clean up
    os.remove(html_path)


if __name__ == "__main__":
    main()
