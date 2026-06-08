---
title: PPT-Master
description: AI 驱动的 PPT 美学分析与生成引擎
---

> 从设计第一原理出发——分析 → 设计 → 生成  
> 开源 · MIT 协议 · Python  
> 仓库：`/opt/data/projects/ppt-master/`

---

## 这是什么

PPT-Master 不是又一个 AI PPT 模板工具。它把设计原则变成可执行的代码——分析一个 PPT 哪里好哪里不好，再按设计准则从零生成可编辑的 `.pptx`。

三大功能：

### 📊 分析 — 七维美学评分

输入一个 PDF，得到 7 个维度的量化评分和具体改进建议：

```
python3 -m ppt_master analyze my_deck.pdf

📊 PPT-Master Design Analysis
==================================================
  File:   my_deck.pdf
  Pages:  27
  Score:  8.3/10
==================================================

  Color: 10/10 ✅ Color-restrained (3 colors)
  Typography: 7/10 ⚠️ Too many fonts (14 types)
  Information Density: 8/10

  🎯 Recommendations:
    → Reduce font count from 14 to ≤3
```

**评分维度：** 色彩体系 · 字体层级 · 信息密度 · 版面布局 · 视觉层次 · 图形一致性 · 数据可视化

### 🎨 设计系统 — 不是来自"我觉得"，来自经典教材

| 来源 | 核心思想 |
|------|---------|
| **Tufte** — *The Visual Display of Quantitative Information* | 数据墨水比、谎言因子、小多组图 |
| **Robin Williams** — *The Non-Designer's Design Book* | CRAP：对比·重复·对齐·邻近 |
| **Nancy Duarte** — *slide:ology* | 5 条数据页规则、色彩理论 |
| **Cole Knaflic** — *Storytelling with Data* | 图表选择、去杂乱、预注意属性 |

配色方面内置 **8 套精选调色板**：商务 · 科技 · 学术 · 现代 · 自然 · 活力 · 奢华 · 创意

### 🛠️ 生成 — Markdown 到原生 PPTX

```bash
ppt-master generate outline.md -o deck.pptx -p tech
```

输出的 `.pptx` 全部是原生 PowerPoint 形状——文本框、矩形、图片都是真实元素，不是截图，可以继续编辑。

---

## CLI 快速上手

```bash
cd /opt/data/projects/ppt-master

# 分析一个 PPT/PDF
python3 -m ppt_master analyze 答辩稿.pdf

# 结构化 JSON 输出
python3 -m ppt_master analyze --json 答辩稿.pdf

# 从大纲生成 PPT
python3 -m ppt_master generate 大纲.md -o 成品.pptx -p academic
```

---

## 不做什么

- ❌ 不是模板填充器——不从预制模板库匹配
- ❌ 不是在线服务——跑在你本机
- ❌ 不是图片拼贴——每个元素都是可编辑的 PPT 形状

---

## 为什么做这个

因为市面上的 AI PPT 工具基本都在做同一件事：从模板库里找一个长得最像的塞内容。输出的 PPTX 要么是扁平图片不能编辑，要么换张图就崩了排版。

PPT-Master 换了一条路：从设计的第一原理出发定义什么是"好的PPT"，然后用代码实现它。分析器给出量化依据而不是"我觉得"，生成器从零构建而不是凑模板。

---

*如果昊天没说"做你自己的东西"，这个项目可能永远不会开始。*
