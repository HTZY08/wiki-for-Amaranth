---
title: MiniMax-Text-01 — 4M 上下文与 Lightning Attention
date: 2025-01-14
source: arXiv / filecdn.minimax.chat
---

# MiniMax-Text-01

**发布日期：** 2025-01-14  
**来源：** arXiv / MiniMax 官方  
**工程范式：** 硬核系统协同设计——通过 Lightning Attention 实现 4M 上下文窗口的线性复杂度。

## 设计哲学

MiniMax-Text-01 是 MiniMax-01 系列的基础语言模型，核心设计目标是 **在极致长上下文（4M tokens）下保持计算可负担**。这对几乎所有 Transformer 架构都是巨大挑战——标准 full attention 在 4M 上下文长的计算量和显存需求是天文数字。

MiniMax 的解决方案是 **混合注意力机制（Hybrid Attention）**：将 Lightning Attention（线性复杂度）与 Softmax Attention（标准二次复杂度）结合，使长上下文场景的计算开销从 O(n²) 降低到 O(n)。

同时采用 **Mixture-of-Experts (MoE)** 架构：456B 总参数量，45.9B 每 token 激活。

## 关键架构决策

- **混合注意力：** Lightning Attention + Softmax Attention 的组合
  - Lightning Attention 处理大部分长程依赖
  - Softmax Attention 在局部窗口保持表达能力
- **MoE 架构：** 456B 总参数，45.9B 每激活（约 10:1 稀疏比）
- **上下文窗口：** 原生支持 4M tokens
- **长上下文性能：**
  - 4M token Needle-in-a-Haystack 检索：**100% 准确率**
  - RULER 基准 1M 上下文：性能仅微量退化
- **多模态：** MiniMax-Text-01 + MiniMax-VL-01（视觉语言模型）组成 MiniMax-01 系列

### 核心基准

| 基准 | MiniMax-Text-01 | 对比模型 |
|------|----------------|---------|
| LongBench (1M 上下文) | 领先 | GPT-4 128K |
| RULER (1M) | 微量退化 | 多数模型显著退化 |
| NiH (4M) | 100% | 无直接对比 |
| 标准文本基准 | 可比顶级模型 | GPT-4, Claude 3 |

## 范式对比

| 维度 | MiniMax-Text-01 | DeepSeek V2 | Llama 3 70B |
|------|----------------|-------------|-------------|
| 架构 | Hybrid Attn + MoE | MLA + MoE | Dense |
| 总参数 | 456B | 236B | 70B |
| 激活参数 | 45.9B | 21B | 70B |
| 上下文 | 4M | 128K | 8K |
| 注意力复杂度 | O(n) hybrid | O(n) MLA | O(n²) |
| 开源 | ✅ | ✅ | ✅ |

## 可复用的工程经验

1. **混合注意力（线性 + Softmax）是长上下文场景的实际工程方案** —— 纯线性注意力在标准基准上有质量损失，混合注意力弥补了这个 gap
2. **MoE 在长上下文场景有独特优势** —— 同样的 FLOPs 预算下，MoE 可以用更多参数处理更长上下文
3. **4M 上下文的 Needle-in-Haystack 100% 证明线性注意力在检索任务上不弱于 full attention**
4. **开源 456B 模型的意义：** MiniMax 证明了中型团队也可以训练超大 MoE 模型并开源
