---
title: Llama 4 — 原生多模态 MoE 开源模型家族
date: 2025-04-05
source: ai.meta.com/blog
---

# Llama 4

**发布日期：** 2025-04-05（Scout & Maverick）  
**来源：** ai.meta.com/blog (Llama 4 blog post)  
**工程范式：** 开源模型首次全面转向 MoE + 原生多模态。

## 设计哲学

Llama 4 是 Llama 系列的第五代，也是一次根本性的架构变革：

1. **首次 MoE**：从 Dense Transformer 全面转向 Mixture-of-Experts
2. **原生多模态**：文本和图像从训练开始就一起学习（非后期组合）
3. **三级产品线**：Scout（轻量）、Maverick（均衡）、Behemoth（教师模型）

核心理念：**MoE 可以同时实现高性能和高效率**——Scout 和 Maverick 都有 17B 激活参数，但总参数量不同，适应不同部署场景。

## 关键架构决策

### 家族规格
| 模型 | 总参数 | 激活参数 | 专家数 | 上下文 | 标签 |
|------|--------|---------|-------|--------|------|
| **Scout** | 109B | 17B | 16 | 10M | 轻量，单 GPU |
| **Maverick** | 400B | 17B | 128 | 1M | 高性能 |
| **Behemoth** | 2T | 288B | 16 | - | 教师模型（训练中） |

### 关键架构创新

**1. MoE 架构**
- Scout：16 专家，MoE，17B 激活 / 109B 总计
- Maverick：128 专家，MoE，17B 激活 / 400B 总计
- 每个 token 由 router 选择 top-2（或 top-k）专家处理
- **关键设计决策**：两个模型使用相同的激活参数量（17B），但总参数量不同

**2. 原生多模态**
- 从预训练开始就同时处理文本和图像
- 使用专门的视觉编码器（MetaCLIP 或其他）
- Scout 和 Maverick 都是原生多模态

**3. Scout 的 10M 上下文**
- 业界领先的上下文长度（10M tokens）
- 使用 4-bit 量化可在单张 H100 GPU 上运行

**4. Maverick 的 128 专家**
- 128 专家在推理时只激活其中的一小部分
- MoE 带来了更高的模型容量，但推理成本接近 Scout

**5. Behemoth（教师模型）**
- 2T 参数，288B 激活
- 作为教师模型蒸馏 Scout 和 Maverick
- 继续训练中，未发布

### 训练
- Scout 和 Maverick 的训练都受益于 Behemoth 的蒸馏
- 支持 12+ 种语言
- 支持通过模型输出改进其他模型（包括合成数据生成和蒸馏）

## 关键结果

Scout 和 Maverick 在多项基准上展示出竞争力：

### 推理和编码
- **Maverick** 在推理和编码任务上与 GPT-4o、DeepSeek V3 竞争
- 17B 激活参数即达到 400B+ 级别模型的性能

### 多模态
- 原生多模态设计使 Scout/Maverick 在图像理解任务上表现强劲
- 与 GPT-4o 和 Gemini 2.0 Flash 相比有竞争力

### 部署效率
- Scout 在单张 H100 上运行（4-bit 量化）
- NVIDIA TensorRT-LLM 优化：B200 GPU 上 Scout 超过 **40K tokens/sec**，Maverick 超过 **30K tokens/sec**

## 范式对比

| 维度 | Llama 3.1 405B | Llama 4 Scout | Llama 4 Maverick | GPT-4o |
|------|---------------|--------------|-----------------|--------|
| 架构 | Dense | MoE (16x) | MoE (128x) | MoE |
| 激活参数 | 405B | 17B | 17B | - |
| 多模态 | 组合方法 | 原生 | 原生 | 原生 |
| 上下文 | 128K | 10M | 1M | 128K |
| 单 GPU 部署 | ❌ | ✅ | ❌ | ❌ |

## 可复用的工程经验

1. **MoE 是 Llama 系列的最大架构变革**——从 Dense 到 MoE 的转向验证了 MoE 在大规模模型中的效率优势。
2. **"相同激活参数、不同总参数"的产品策略**——Scout 和 Maverick 共享 17B 激活，但通过不同专家数差异化，是巧妙的工程决策。
3. **原生多模态替代组合方法**——Llama 4 从预训练开始就使用多模态数据，比 Llama 3.1 的组合方法更彻底。
4. **10M 上下文是 Scout 的差异化优势**——在需要处理超长文档的场景有独特价值。
5. **Behemoth 作为教师模型的蒸馏策略**——Scout 和 Maverick 在训练中受益于 2T 参数教师模型的知识蒸馏。
6. **产品线分层（Scout/Maverick/Behemoth）**让不同需求层次的用户都有合适选择。
