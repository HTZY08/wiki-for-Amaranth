---
title: Llama 4 Herd — iRoPE + Early Fusion + MoE：Meta 的开源多模态路线
date: 2025-04-05
source: https://huggingface.co/blog/llama4-release
---

# Llama 4 Herd

**发布日期：** 2025-04-05（模型发布）；公开技术汇总 2026-01
**来源：** [Hugging Face 发布博客](https://huggingface.co/blog/llama4-release) | [arXiv 技术汇总](https://arxiv.org/abs/2601.11659)
**工程范式：** 用 iRoPE（交错 RoPE/NoPE）解决超长上下文的位置编码瓶颈，用早融合（Early Fusion）实现原生多模态，用 1/20 的激活参数做 400B 规模

## 设计哲学

Llama 4 是 Meta 首次在旗舰开源系列中全面转向 MoE 架构，标志着一个明确的范式转换：**不再追求纯 Dense 模型的规模扩展，而是在总参数和激活参数之间做全面权衡。**

核心约束与选择：
- **参数效率优先：** Scout（109B/17B）和 Maverick（402B/17B）激活参数相同，总参数相差 4 倍——同一套推理基础设施运行不同容量
- **原生多模态而非事后嫁接：** 早融合（Early Fusion）——文字 Token 和视觉 Token 在输入阶段直接拼接，而非分阶段处理后再融合
- **MoE 不是全层均匀分布：** Maverick（128 专家）只在半数层使用 MoE，其余层保持 Dense——这种"交错 MoE"设计在总参数和推理速度之间找到平衡
- **Behemoth 作为 Co-distillation 教师：** Llama Maverick 从更大的 Behemoth 模型中蒸馏，使用了动态加权学生-教师 logits 的损失函数

**放弃的路线：**
- 放弃了纯 Dense 架构（Llama 3 的路线）
- 放弃了事后多模态（late fusion）——Llama 3 系列不支持多模态
- 放弃了标准 RoPE 在全层统一使用——换用 iRoPE 模式

## 关键架构决策

### Scout（109B/16E）与 Maverick（402B/128E）

| 特性 | Scout | Maverick |
|------|-------|----------|
| 总参数 | ~109B | ~402B |
| 激活参数 | 17B | 17B |
| 专家数 | 16 | 128 |
| MoE 分布 | 全层 MoE | 半数层 MoE，半数层 Dense |
| 上下文（预训练）| 256K | 256K |
| 上下文（Instruct）| **10M** | **1M** |
| 量化支持 | BF16 + 4-bit on-the-fly | BF16 + FP8 |

### iRoPE 架构——长上下文的关键

Llama 4 的核心创新：**在每个 Transformer Block 内，3 个 RoPE 层 + 1 个 NoPE（无位置编码）层的交替模式。**

```
每个 Transformer Block 内部：
  RoPE Layer 1（chunked attention, 8192 block）
  RoPE Layer 2（chunked attention, 8192 block）
  RoPE Layer 3（chunked attention, 8192 block）
  NoPE Layer（full causal mask，无位置偏差）
```

**为什么 NoPE 层对超长上下文至关重要？**

标准 RoPE 在超长序列（10M）上会遇到注意力概率值随序列长度增加而衰减为零的问题——这是 softmax 函数在极长序列上的已知局限性。具体而言，当序列长度超过训练时见过的长度，RoPE 的相对角度编码不再有效，导致注意力分布趋于均匀，模型失去区分遥远位置的能力。

NoPE 层通过两个机制解决这个问题：
1. **无位置偏差：** 不依赖任何位置编码，对所有 token 一视同仁，避免"见过的最长长度"这个硬约束
2. **full causal mask：** 使用完整因果掩码而非分块注意力，确保跨整个序列的信息流动

**温度缩放（Attention Temperature Tuning）：** 在 NoPE 层中，缩放 softmax 的温度参数来补偿长序列下的注意力分散问题。RoPE 层不需要此修正——它们只关注 8192 以内的局部块。

**QK Normalization（仅 Scout）：** Scout 在 RoPE 层中，对 Q 和 K 状态在 RoPE 嵌入后增加了一层无学习参数的 RMS 归一化。

### 早融合多模态

以别于 DeepSeek-VL2 的三阶段渐进式融合（冻结 LLM → 训练 MLP 适配器 → 联合预训练 → 指令微调），Llama 4 将文本 Token 和视觉 Token 在输入端直接拼接成一整序列：

```
输入：[文本Token_1, 文本Token_2, ..., 图像Token_1, 图像Token_2, ...]
                                ↓
                   统一的 Transformer Stack
                                ↓
                         输出：[完整序列]
```

这种设计的优势在于：
- 跨模态注意力双向流动（文本→图像 和 图像→文本 同时发生）
- 无需专用的模态桥接层（MLP adapter 等）
- 多模态理解从预训练第一阶段就开始

### MoE 设计

**Scout（16 专家）：** 标准 top-2 routing，全 48 层均为 MoE。

**Maverick（128 专家）：** 
- 只有半数层（24 层）使用 MoE，其余 24 层保持 Dense FFN
- 128 专家 × top-2 routing，激活参数保持 17B
- **设计权衡：** 更多专家 → 更细粒度的知识专业化 → 但路由开销和通信成本更高。Meta 选择只在半数层应用 MoE 来平衡

**Co-distillation（Maverick）：**
- 从 Behemoth（更大的教师模型，未开源）蒸馏
- 使用了**动态加权学生-教师 logits** 的损失函数——不是固定的 KL 散度，而是根据 token 的难度动态调整蒸馏权重
- 这意味着模型在简单 token 上更依赖教师，在困难 token 上自行探索

**MetaP 超参数优化：**
- 基于 μP（Maximal Update Parameterization）的方法
- 允许跨不同维度（训练预算、模型大小）最优调整超参数
- 具体细节未公开

## 关键结果

### 基础模型（Pre-trained）

| 基准 | Llama 3.1 70B | Llama 3.1 405B | Scout | Maverick |
|-----|:---:|:---:|:---:|:---:|
| MMLU (5-shot) | 79.3 | 85.2 | 79.6 | **85.5** |
| MMLU-Pro (5-shot) | 53.8 | 61.6 | 58.2 | **62.9** |
| MATH (4-shot) | 41.6 | 53.5 | 50.3 | **61.2** |
| MBPP (3-shot) | 66.4 | 74.4 | 67.8 | **77.6** |
| ChartQA (0-shot) | - | - | 83.4 | **85.3** |
| DocVQA (0-shot) | - | - | 89.4 | **91.6** |

### 指令微调模型（Instruct）

| 基准 | Llama 3.3 70B | Llama 3.1 405B | Scout | Maverick |
|-----|:---:|:---:|:---:|:---:|
| MMLU-Pro (0-shot) | 68.9 | 73.4 | 74.3 | **80.5** |
| GPQA Diamond | - | - | 57.2 | **69.8** |
| MMMU (0-shot) | - | - | 69.4 | **73.4** |
| MMMU-Pro (0-shot) | - | - | 52.2 | **59.6** |
| MathVista (0-shot) | - | - | 70.7 | **73.7** |
| ChartQA (0-shot) | - | - | 88.8 | **90.0** |
| DocVQA (0-shot) | - | - | 94.4 | **94.4** |
| LiveCodeBench (pass@1) | 33.3 | 27.7 | 32.8 | **43.4** |

**关键数据点：**
- Scout（17B active）在 MMLU-Pro 上超过 Llama 3.1 405B（74.3 vs 73.4）——10M 上下文的小模型超过 405B 大模型
- Maverick（17B active / 402B total）在 MMLU-Pro 上达到 80.5——接近当时前沿闭源模型的水平
- Scout 的 10M 上下文在 MTOB（半本书翻译）上达到 chrF 42.2/36.6（英→kgv/kgv→英），Maverick 更达到 54.0/46.4

### 上下文长度与微调

| 模型 | 预训练上下文 | Instruct 上下文 | 扩展方法 |
|------|:---:|:---:|----------|
| Scout (16E) | 256K | **10M** | Mid-training + iRoPE |
| Maverick (128E) | 256K | **1M** | Mid-training + iRoPE |

Instruct 模型通过 mid-training（长上下文扩展训练）将上下文窗口从 256K 扩展到 10M/1M。

## 范式对比

**vs Gemma 4（Dense/RoPE）：** Gemma 4 31B 是纯 Dense 模型，使用 5:1 滑动窗口比和 p-RoPE。Llama 4 在类似激活参数（17B vs 31B）下选择了完全不同的路线——MoE + iRoPE。关键差异在于 Llama 4 的多模态是原生的（早融合），而 Gemma 4 的多模态是通过编码器+投影层（12B 除外）实现的。

**vs DeepSeek-V4（MoE/MLA）：** DeepSeek-V4 使用 Multi-Head Latent Attention（MLA）和更粗粒度的 MoE（1.6T/49B 激活），Llama 4 使用更细粒度的 MoE（128 专家，17B 激活）。DeepSeek 的 MLA 在 KV cache 效率上优于 Llama 4 的标准注意力+chunked attention。但 Llama 4 的 iRoPE 在上下文扩展上更灵活——Scout 的 10M 远超 DeepSeek-V4 的 1M。

**vs 自己的前辈（Llama 3）：** 最大的范式转变：从 Dense → MoE，从纯文本 → 原生多模态，从 128K → 10M 上下文。每个都是数量级的跃升。

## 可复用的工程经验

1. **iRoPE 的可移植性：** 3:1 的 RoPE/NoPE 比例是可移植的设计模式。NoPE 层作为"长上下文锚点"，Chunked attention 的 RoPE 层作为"局部精度层"。这种组合的设计思路可以移植到任何需要超长上下文的 Transformer 中。

2. **MoE 不必全层应用：** Maverick 只在半数层使用 MoE。这给出一个设计自由度——在总参数预算固定的情况下，可以通过调整 MoE 层比例来平衡容量和推理速度。

3. **早融合 > 晚融合：** 对于多模态模型，将不同模态的数据在输入端直接混合，比通过适配器在深层融合更有效。早融合的关键前提是预训练数据中多模态数据的质量和数量——Meta 使用了 40T token（含大量图像/视频数据）。

4. **Co-distillation 的动态权重：** 动态加权学生-教师 logits 而非固定 KL 散度——简单 token 多依赖教师，困难 token 自行探索——比均匀蒸馏更高效。

5. **NoPE + Temperature Tuning 的协同：** 单用 NoPE 在超长上下文中会遇到 softmax 衰减问题。同时进行温度缩放才能发挥 NoPE 的长上下文能力。这两个设计是配套的，缺一不可。
