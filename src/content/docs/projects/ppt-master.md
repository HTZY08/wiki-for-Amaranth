---
title: PPT-Master
description: AI 驱动的 PPT 美学分析与生成引擎
---

> 从设计第一原理出发——分析 → 设计 → 生成  
> 开源 · MIT 协议 · Python  
> 仓库：`/opt/data/projects/ppt-master/`

---

## 这是什么

PPT-Master 不是又一个 AI PPT 模板工具。它把设计原则变成可执行的代码。

```
你拿到一个 PPT → 分析它好不好、为什么好 → 按设计准则从零生成新的
```

三大功能：

- **📊 分析**：量化评分现有 PPT/PDF 的设计质量
- **🎨 设计系统**：四本经典教材提炼的设计规则 + 8 套调色板
- **🛠️ 生成**：Markdown 大纲 → 原生可编辑 .pptx

---

## 📊 七维美学分析器

输入一个 PDF，输出 7 个维度的量化评分。不是"我觉得"，是逐页扫描后的数据。

```bash
python3 -m ppt_master analyze my_deck.pdf
```

### 七个维度

| 维度 | 满分 | 评估什么 |
|------|------|---------|
| **色彩体系** | 10 | 颜色数量、主色调是否突出、是否克制 |
| **字体层级** | 10 | 字体种类、字号层级是否清晰 |
| **信息密度** | 10 | 每页文字量、段落长度、是否过度拥挤 |
| **版面布局** | 10 | 留白、边距、内容分布是否均衡 |
| **视觉层次** | 10 | 标题/正文/数据是否有清晰的视觉优先级 |
| **图形一致性** | 10 | 图标风格、图片风格是否统一 |
| **数据可视化** | 10 | 图表类型选择是否合理、是否干净 |

### 输出示例

```
📊 PPT-Master Design Analysis
==================================================
  File:   my_deck.pdf
  Pages:  27
  Score:  8.3/10
==================================================

  Color: 10/10 ✅ Color-restrained (3 colors)
  Typography: 7/10 ⚠️ Too many fonts (14 types)
  Information Density: 8/10 ✅
  Layout: 9/10 ✅ Good margins
  Visual Hierarchy: 8/10 ✅
  Graphic Consistency: 6/10 ⚠️ Inconsistent icon styles
  Data Visualization: 7/10 ⚠️ Some charts need decluttering

  🎯 Recommendations:
    → Reduce font count from 14 to ≤3
    → Unify icon style across all slides
```

也支持 JSON 结构化输出：

```bash
python3 -m ppt_master analyze --json my_deck.pdf
```

---

## 🎨 设计系统

### 四本教材提炼的规则

不是 AI 生成的"我觉得"，是从经典教材里一条条提取出来的。

#### Tufte — 《The Visual Display of Quantitative Information》

- **数据墨水比**：去掉不承载信息的装饰元素。页面上每一滴墨水都应该传达信息
- **谎言因子**：图形展示的效果不能扭曲实际数据。比例尺必须真实
- **小多组图**：与其堆在一个复杂图表里，不如拆成多个并排的简单图
- **图表垃圾**：3D 效果、网格线过度、不必要的渐变填充——统统去掉

#### Robin Williams — 《The Non-Designer's Design Book》

- **对比**：如果两个元素不同，就让它们明显不同（不是"稍微不同"）
- **重复**：同样的设计元素在全篇重复出现，形成统一感
- **对齐**：页面上每个元素都与另一个元素有视觉联系
- **邻近**：相关的元素放在一起，不相关的分开

#### Nancy Duarte — 《slide:ology》

- **5 条数据幻灯片规则**：①讲一个故事 ②简化 ③突出关键 ④标注重点 ⑤核对一致性
- **色彩理论**：主色 ≤ 3 种、强调色 < 10% 面积
- **字体层级**：标题 28-36pt、正文 14-18pt、注释 10-12pt

#### Cole Knaflic — 《Storytelling with Data》

- **图表选择**：比较用柱状图、趋势用折线图、构成用条形图、分布用散点图
- **去杂乱**：去掉默认网格线、去掉不必要标签、简化颜色
- **预注意属性**：用颜色/粗细/位置引导视线，先于意识到达需要关注的地方

### 8 套精选调色板

每套 5 色：主色 × 辅助 × 背景 × 强调 × 深色

```python
palettes = {
    "business":  ["#2B2D42", "#8D99AE", "#EDF2F4", "#EF233C", "#D90429"],
    # 深蓝灰 + 冷灰 + 浅灰白 + 亮红 + 深红——商务简洁感

    "tech":      ["#03045E", "#0077B6", "#00B4D8", "#90E0EF", "#CAF0F8"],
    # 深海蓝 + 钴蓝 + 青蓝 + 浅蓝 + 冰蓝——科技清爽

    "academic":  ["#780000", "#C1121F", "#FDF0D5", "#003049", "#669BBC"],
    # 深红 + 亮红 + 米白 + 深藏青 + 钢蓝——学术稳重

    "modern":    ["#006D77", "#83C5BE", "#EDF6F9", "#FFDDD2", "#E29578"],
    # 深青绿 + 浅青绿 + 冰白 + 暖粉 + 陶土——现代柔和

    "nature":    ["#DAD7CD", "#A3B18A", "#588157", "#3A5A40", "#344E41"],
    # 米灰 + 草绿 + 深绿 + 墨绿 + 深墨——自然大地

    "vibrant":   ["#FF9F1C", "#FFBF69", "#FFFFFF", "#CBF3F0", "#2EC4B6"],
    # 亮橙 + 暖黄 + 白 + 浅青 + 青绿——活力明快

    "luxury":    ["#0A0A0A", "#0070F3", "#D4AF37", "#F5F5F5", "#FFFFFF"],
    # 纯黑 + 亮蓝 + 金色 + 浅灰 + 白——奢华简约

    "creative":  ["#CDB4DB", "#FFC8DD", "#FFAFCC", "#BDE0FE", "#A2D2FF"],
    # 淡紫 + 粉红 + 浅粉 + 天蓝 + 淡蓝——创意柔和
}
```

每个调色板的角色：

| 角色 | 用途 | 占比建议 |
|------|------|---------|
| 主色 | 标题、关键强调 | 20% |
| 辅助色 | 次要元素、图表 | 15% |
| 背景色 | 幻灯片背景 | 55% |
| 强调色 | 数据点、关键发现 | 5% |
| 深色 | 正文文字 | 5% |

---

## 🛠️ Markdown 到原生 PPTX

```bash
python3 -m ppt_master generate outline.md -o deck.pptx -p academic
```

输出的 `.pptx` 全部是原生 PowerPoint 形状——文本框、矩形、图表都是真实元素，不是截图，可以在 PowerPoint 里继续编辑。

支持模板参数：

| 参数 | 说明 | 示例 |
|------|------|------|
| `-p / --palette` | 调色板名 | `tech` / `academic` / `luxury` |
| `-o / --output` | 输出路径 | `deck.pptx` |
| `--aspect` | 比例 | `16:9`（默认）或 `4:3` |

### 示例大纲格式

```markdown
# 课题名称

## 研究背景

- 背景介绍第一点
- 背景介绍第二点
- 目前存在的问题

## 研究思路

1. 方法一：简述
2. 方法二：简述
3. 方法三：简述

## 实验结果

| 指标 | 本方法 | 对照 A | 对照 B |
|------|--------|--------|--------|
| 准确率 | 96.3% | 89.1% | 91.7% |
| 速度 | 12ms | 45ms | 23ms |

## 结论

- 主要发现
- 创新点
- 下一步工作
```

---

## 配置设计系统文件

项目目录结构：

```
ppt-master/
├── ppt_master/              # 核心代码
│   ├── analyze/             # 分析器
│   ├── generate/            # 生成器
│   └── design/              # 设计系统
├── design_system/
│   ├── palettes.json        # 8套调色板定义
│   └── ...                  # 未来可扩展
├── references/              # 设计原理原文提取
│   ├── data-ink-ratio.md
│   ├── CRAP-principles.md
│   ├── slide-design-rules.md
│   └── chart-rules.md
├── pyproject.toml
└── README.md
```

---

## 安装

```bash
git clone https://github.com/HTZY08/ppt-master   # 如果公开了
# 或
cd /opt/data/projects/ppt-master

pip install -e .    # 可编辑安装
```

依赖：Python 3.10+、python-pptx、Pillow、lxml

---

## 不做什么

- ❌ 不是模板填充器——不从预制模板库匹配，从零生成
- ❌ 不是在线服务——跑在你本机，数据不外传
- ❌ 不是图片拼贴——每个元素都是可编辑的 PPT 原生形状
- ❌ 不是"一句话生成PPT"——需要你提供大纲，工具负责排版和设计

---

## 为什么做这个

市面上的 AI PPT 工具基本都在做同一件事：从模板库里找一个长得最像的塞内容。输出的 PPTX 要么是扁平图片不能编辑，要么换一张图就崩了排版。

PPT-Master 换了一条路：从设计的第一原理出发定义什么是"好的PPT"，然后用代码实现它。

分析器给出量化依据而不是"我觉得"，生成器从零构建而不是凑模板。颜色来自提取自经典教材的配色系统，排版规则来自四本书的交叉验证。

> 如果昊天没说"做你自己的东西"，这个项目可能永远不会开始。
