# Cross-Image Consistency Techniques for Scientific Illustration

2026 年跨图一致性技术栈速查。适用场景：多张科学图共用同一套视觉语言（色板、描边、标注风格、布局逻辑）。

## 技术对比

| 方法 | 是否需要训练 | 一致性强度 | 适用场景 | 典型工具 |
|:-----|:-----------:|:---------:|:---------|:---------|
| **Prompt 硬约束** | ❌ 不需要 | ⚠️ 60-80% | 色板/描边/字体统一 | MeiGen / GPT Image 2.0 |
| **referenceImages** | ❌ 不需要 | ✅ 80-90% | 整组图风格锚定 | MeiGen / OpenAI API |
| **ConsiStory** | ❌ 不需要 | ✅ 85-95% | 主体/角色跨图一致（SDXL） | ComfyUI + ConsiStory node |
| **IP-Adapter** | ❌ 不需要 | ✅ 80-90% | 风格迁移、参考图注入 | ComfyUI |
| **LoRA 微调** | ✅ 需 10-20 张图 | ✅✅ 95%+ | 角色锁定、品牌风格固化 | ComfyUI / Kohya |
| **AutoFigure** | ❌ 不需要（框架） | ✅ 布局优先 | 科学图自动生成 | ICLR 2026 / Qwen3-VL |

## GPT Image 2.0 原生一致性

OpenAI 于 2026 年 4 月发布的 `gpt-image-2` 模型（通过 MeiGen 可用）已内置跨图一致性支持：

- **8-image coherent batches**：同一 batch 内人物/物体自动保持视觉连续性
- 通过 `referenceImages` 参数传入参考图作为风格锚点
- 文字渲染（中文+英文）质量达到可出版水平

**推荐用法：**
```
首张图 → 出图 → referenceImages 传给下一张 → 出图 → 传递 → ...
```
同时每张 prompt 加入：
```
Match the visual style of the reference image exactly — same line thickness, same color palette, same labeling style.
```

## ConsiStory（NVIDIA, 2024）

论文：Training-Free Consistent Text-to-Image Generation（NVlabs/consistory）

核心原理：在 SDXL 内部通过**共享注意力激活值**实现主体一致性，不需要任何训练。

- 速度：~10 秒/张（H100）
- 比 LoRA 方法快 20 倍
- 支持多主体场景
- 需 ComfyUI + 对应节点

## AutoFigure（ICLR 2026）

论文：AutoFigure: Generating and Refining Publication-Ready Scientific Illustrations

与你正在做的事情高度重合。三阶段流水线：

```
Stage 1: 概念提取       ← 读全文 → 抽取关键实体和关系
Stage 2: 迭代自我修正    ← 生成布局 → 批判 → 修正（平均5轮）
Stage 3: 风格引导渲染    ← 用风格prompt渲染最终图
```

**关键结论：**
- 布局规划先于渲染（"Logic layout first, visual rendering later"）
- GPT-Image 裸 prompt 评分 3.47 vs AutoFigure 7.03（有布局规划比没有强一倍）
- Qwen3-VL-235B 开源模型评分 7.08（超过 Claude Opus）
- 可本地部署（2 张 H100 或 2 台 DGX Spark）
- 迭代轮数与质量：0→6.28, 5 轮→7.14

**对你最有用的设计原则：** 把版面布局规划与视觉渲染分离——先用文字描述清楚每张图放什么、放哪、什么颜色，再出图。这正是 paper-figure-mapper 的 ZONES/LABELS/COLORS 结构做的事。

## LoRA 训练（情感助手类应用的标准方案）

那些情感助手之所以能**每张图都保持同一张脸**，是因为：
1. 用 10-20 张角色图训练一个 LoRA（~10MB）
2. 每次出图的 prompt 里触发该 LoRA
3. 角色锁定率 >95%

对科学综述不需要——你要的不是同一张脸，是同一套视觉语言。

## 参考链接

- ConsiStory: https://research.nvidia.com/labs/par/consistory
- ConsiStory GitHub: https://github.com/NVlabs/consistory
- GPT Image 2: https://spicyadvisory.com/blog/chatgpt-images-2-0-business-guide-2026
- AutoFigure: https://openreview.net/forum?id=5N3z9JQJKq
- Awesome GPT Image 2 Prompts: https://github.com/YouMind-OpenLab/awesome-gpt-image-2
