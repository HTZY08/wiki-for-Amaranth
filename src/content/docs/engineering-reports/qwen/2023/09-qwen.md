---
title: Qwen Technical Report — 阿里通用大模型系列
date: 2026-07-03
source: arXiv 2309.16609
---

# Qwen Technical Report

**发布日期：** 2023-09 (arXiv 2309.16609)
**来源：** arXiv 2309.16609
**工程范式：** 密集架构 + 多领域专业化——统一基座 + 编码/数学/视觉专业模型的「一基多专」路线。

## 设计哲学

Qwen 团队的核心策略是**统一基座 + 专业化扩展**——先打造一个强大的基础语言模型（Qwen），然后在其上构建领域特化模型（Code-Qwen、Math-Qwen、Qwen-VL）。团队相信好的基座模型可以泛化支持多种下游任务。关键设计选择包括大词汇表（152K）、未绑定嵌入权重、QKV 偏置。

## 关键架构决策

### 基础架构
- **Decoder-only Transformer**，参数量 1.8B / 7B / 14B
- **词表：** 152K tokens（基于 tiktoken BPE，专门加入中文字符和数字单 token 化）
- **关键设计：**
  - **未绑定嵌入权重**（Untied embeddings）
  - **RoPE** + FP32 逆频率矩阵
  - **QKV 层偏置**（更好的外推能力）
  - **Pre-RMSNorm** + **SwiGLU** 激活
  - FFN 维度 = hidden size 的 8/3

### 上下文长度扩展
- 预训练长度 2048 tokens
- **NTK-aware interpolation** + **dynamic NTK**（推理时调整 RoPE base）
- **LogN-Scaling**（按上下文长度缩放点积）
- **Window attention**（不同层不同窗口大小）
- 结果：Qwen-7B 在 8K tokens 下保持低困惑度（PPL 4.32）

### 专业化模型
- **Code-Qwen**：在代码数据上继续训练
- **Math-Qwen-Chat**：数学专用 SFT
- **Qwen-VL**：视觉语言版本

### 对齐
- **SFT**：聊天格式数据，约 4000 步训练
- **RLHF**：PMP 预训练 + 人类反馈微调 + PPO
- **Pretrained gradient** 缓解对齐税

## 关键结果

### 基座模型（Table 2）
| Model | MMLU | C-Eval | GSM8K | MATH | HumanEval | BBH |
|-------|------|--------|-------|------|-----------|-----|
| Qwen-1.8B | 44.6 | 54.7 | 21.2 | 5.6 | 17.1 | 28.2 |
| Qwen-7B | 58.2 | 63.5 | 51.7 | 11.6 | 29.9 | 45.0 |
| Qwen-14B | 66.3 | 72.1 | 61.3 | 24.8 | 32.3 | 53.4 |
| LLaMA2-70B | 69.8 | 50.1 | 63.3 | 13.5 | 29.9 | 64.9 |

Qwen-14B 在 C-Eval、MATH、HumanEval 上超越 LLaMA2-70B。

### 对齐模型
- Qwen-14B-Chat 在中文人工评估中接近 GPT-4，超越 GPT-3.5
- **工具选择准确率：** 98%（vs GPT-4 95%, GPT-3.5 85%）
- **代码解释器可执行率：** 81.7%（接近 GPT-4 86.8%）
- **Code-Qwen-14B-Chat HumanEval pass@1：** 66.4%

## 范式对比

vs LLaMA 系列（Meta，类似密集架构），Qwen 的中文能力显著更强（C-Eval 72.1 vs LLaMA2-70B 50.1）。vs GPT-3.5（闭源），Qwen-14B-Chat 在中文场景中可竞争。关键差异：152K 大词表 + QKV 偏置 + 动态 NTK 等工程选择让 Qwen 在密集模型中具有竞争力。

## 可复用的工程经验

1. **大词表（152K）对中文任务的编码效率很重要**——中文字符和数字的单 token 化减少推理延迟
2. **NTK-aware + dynamic NTK + LogN-Scaling 组合「无痛」扩展上下文长度**
3. **未绑定嵌入权重 + QKV 偏置等小设计对模型质量有正向贡献**
4. **Pretrained gradient（在 RLHF 中保留预训练梯度）可以有效缓解对齐税**
5. **「一基多专」策略比独立训练多个模型更高效**
