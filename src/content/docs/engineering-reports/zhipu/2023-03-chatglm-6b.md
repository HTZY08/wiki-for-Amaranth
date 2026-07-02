---
title: ChatGLM — GLM-130B to ChatGLM-6B 双语对话模型
date: 2023-03-14
source: arXiv 2210.02414 (GLM-130B), GitHub (ChatGLM-6B)
---

# ChatGLM

**发布日期：** 2023-03 (ChatGLM-6B), 2022-08 (GLM-130B)  
**来源：** arXiv 2210.02414 (GLM-130B ICLR 2023), GitHub  
**工程范式：** GLM 架构——基于自回归空白填充的双语预训练路线。

## 设计哲学

ChatGLM 系列源自 GLM（General Language Model）架构，由清华大学与智谱 AI 联合开发。核心设计理念是 **自回归空白填充（Autoregressive Blank Infilling）**——一种结合自编码和自回归优势的预训练目标，统一了 NLU 和 NLG 任务。

GLM-130B（2022 年 8 月）是千亿级双语模型，训练了 4000 亿 tokens，在 HELM 评测中与 GPT-3 (davinci) 持平。ChatGLM-6B（2023 年 3 月）是对齐后的对话版，6.2B 参数，INT4 量化可在消费级 GPU 上运行（2K 上下文）。

核心哲学：**使用较小模型配合更多训练数据，降低部署门槛**，这在 LLaMA 之前就已提出。

## 关键架构决策

### GLM 架构
- **Autoregressive Blank Infilling**：随机遮盖输入中的连续 token spans，按自回归方式生成被遮盖的内容，兼顾理解与生成。
- **2D Positional Encoding**：编码被遮盖 span 内部和跨 span 的位置关系。
- **LayerNorm + ReLU**（早期版本），后续被 RMSNorm + SwiGLU 取代。

### GLM-130B 关键参数
- 130B 参数，深度 70 层，隐藏维度 12288
- 训练 tokens：400B
- 双语（中文+英文）预训练

### ChatGLM-6B 关键参数
- 6.2B 参数，对话对齐（SFT + RLHF）
- 上下文长度：2K（可通过 FlashAttention 扩展）
- INT4 量化后可在单张消费级 GPU 运行
- 2023 年在 Hugging Face 上获得超 1000 万次下载

## 关键结果

### GLM-130B 结果
- HELM 评测中与 GPT-3 (davinci) 持平
- 在 7 个 NLU 任务上超越 GPT-3 175B
- ICLR 2023 接收

### ChatGLM-6B 社区影响
- 开源后吸引超 1000 万次下载（2023 年）
- 被广泛用于中文对话场景
- 为后续 ChatGLM2/3 和 GLM-4 系列奠定基础

## 范式对比

| 维度 | GLM-130B | GPT-3 175B | LLaMA-65B |
|------|----------|------------|-----------|
| 架构 | Autoregressive Blank Infilling | 标准 Decoder-only | 标准 Decoder-only |
| 语言 | 中英双语 | 英语 | 英语 |
| 开源 | 开源 | 不开源 | 开源 |
| 消费级部署 | 不支持 | 不支持 | 65B 需多 GPU |

## 可复用的工程经验

1. **空白填充预训练**是统一 NLU/NLG 的有效方法，在 GLM 系列中持续使用。
2. **双语预训练的成功**证明单一模型掌握两种语言不损失单语性能。
3. **小模型 + 量化 + 对话对齐**的组合是 LLM 产品化的有效路径——ChatGLM-6B 证明了 6B 模型也能产生实用价值。
4. **开源生态的正反馈**：1000 万次下载带来了社区贡献和改进，加速了后续迭代。
