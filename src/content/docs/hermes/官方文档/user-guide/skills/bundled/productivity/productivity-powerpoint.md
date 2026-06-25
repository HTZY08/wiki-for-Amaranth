---
title: Powerpoint
---

## 转换为图像（Converting to Images）

将演示文稿转换为单独的幻灯片图像以进行视觉检查：

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
```

这将创建 `slide-01.jpg`、`slide-02.jpg` 等文件。

修复后重新渲染特定幻灯片：

```bash
pdftoppm -jpeg -r 150 -f N -l N output.pdf slide-fixed
```

---

--- body ---
--- body ---
## 依赖项（Dependencies）

- `pip install "markitdown[pptx]"` - 文本提取
- `pip install Pillow` - 缩略图网格
- `npm install -g pptxgenjs` - 从头创建
- LibreOffice（`soffice`）- PDF 转换（通过 `scripts/office/soffice.py` 为沙盒环境自动配置）
- Poppler（`pdftoppm`）- PDF 转图像