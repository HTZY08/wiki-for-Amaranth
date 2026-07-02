---
title: ChatGLM2-6B — 第二代开源双语对话模型
date: 2023-06-25
source: GitHub (THUDM/ChatGLM2-6B)
---

# ChatGLM2-6B

**发布日期：** 2023-06-25  
**来源：** GitHub THUDM/ChatGLM2-6B  
**工程范式：** 第二代小模型快速迭代——在保持 6B 规模的同时大幅提升性能。

## 设计哲学

ChatGLM2-6B 是 ChatGLM-6B 的第二代，保留了 6B 参数量和消费级部署优势，但在架构和性能上做了大幅改进。核心设计理念是 **"在固定参数量上最大化性能"**：不增加模型规模，而是通过架构优化（Multi-Query Attention、FlashAttention）和训练改进来提升能力。

关键信号：这是一个"小步快跑"的工程策略——每一代都在相同成本约束下追求最大收益。

## 关键架构决策

### Multi-Query Attention (MQA)
- 用 MQA 替代标准多头注意力，大幅减少 KV 缓存大小
- 推理速度提升 **42%**

### FlashAttention
- 引入 FlashAttention 实现 32K 上下文（从第一代 2K 提升 16 倍）
- 在不显著增加显存的情况下支持长序列

### 训练优化
- 继续在高质量双语数据上预训练
- 改进对齐训练流程

## 关键结果

| 基准 | ChatGLM-6B | ChatGLM2-6B | 提升幅度 |
|------|-----------|-------------|---------|
| MMLU | 基线 | 基线 +23% | +23% |
| GSM8K | 基线 | 基线 +571% | +571% |
| BBH | 基线 | 基线 +60% | +60% |
| HumanEval | 基线 | 显著提升 | - |

- 上下文从 2K 扩展到 **32K**
- 推理速度提升 **42%**（MQA 贡献）

### CodeGeeX2-6B（ChatGLM2 的代码版本）
基于 ChatGLM2-6B 额外训练 600B 代码 tokens 得到 CodeGeeX2-6B：
- HumanEval-X Pass@1 改进：
  - Python +57%，C++ +71%，Java +54%，JavaScript +83%，Go +56%

## 范式对比

| 维度 | ChatGLM-6B | ChatGLM2-6B | LLaMA 2 7B |
|------|-----------|-------------|------------|
| 参数 | 6.2B | 6.2B | 7B |
| 上下文 | 2K | 32K | 4K |
| Attention | MHA | MQA + FlashAttention | GQA |
| 推理加速 | - | +42% | 有加速 |
| 消费级 GPU | ✅ | ✅ | ✅ |

## 可复用的工程经验

1. **MQA 是 6B 级别模型推理成本的"杠杆"**——参数量不变，推理速度大幅提升。
2. **FlashAttention 是长上下文的"免费午餐"**——ChatGLM2 证明在 6B 模型上也能支持 32K 上下文。
3. **CodeGeeX2 证明代码能力可以通过"基座 + 代码续训"高效获得**——从通用模型到代码专家的成本远低于从头训练。
4. **"每代在相同成本下翻倍性能"的产品策略**适合快速迭代的工程团队。
