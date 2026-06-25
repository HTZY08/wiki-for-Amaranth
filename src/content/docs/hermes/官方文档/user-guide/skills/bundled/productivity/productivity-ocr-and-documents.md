---
title: Ocr And Documents
---

## 注意

- `web_extract` 始终是处理 URL 的首选
- pymupdf 是安全默认选项——即时可用，无需模型，随处运行
- marker-pdf 用于 OCR、扫描文档、公式、复杂布局——仅在需要时安装
- 两个辅助脚本均可通过 `--help` 查看完整用法
- marker-pdf 首次使用时会下载约 2.5GB 模型至 `~/.cache/huggingface/`
- 处理 Word 文档：`pip install python-docx`（优于 OCR——可解析实际结构）
- 处理 PowerPoint：请参见 `powerpoint` 技能（使用 python-pptx）