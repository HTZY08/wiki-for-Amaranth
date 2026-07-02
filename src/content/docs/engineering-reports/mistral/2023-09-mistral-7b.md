---
title: Mistral 7B — 高效 7B 模型，超越 Llama 2 13B
date: 2023-09-27
source: arXiv 2310.06825
---

# Mistral 7B

**发布日期：** 2023-09-27  
**来源：** arXiv 2310.06825  
**工程范式：** 小模型性能密度革命——7B 超越 13B，接近 34B。

## 设计哲学

Mistral 7B 是 Mistral AI 的首个模型，也是 7B 级别最具冲击力的模型之一。核心理念：**在相同的推理成本下，让模型性能尽可能高**。

Mistral 7B 的核心成就是：超越 Llama 2 13B（所有基准）、超越 Llama 1 34B（推理、数学、代码）。其性能密度（performance per parameter）是当时的标杆。

工程哲学：**不堆参数量，靠架构创新和数据质量**。

## 关键架构决策

### 架构
标准 Decoder-only Transformer + 两项关键注意力改进：

**1. Grouped-Query Attention (GQA)**
- 32 个 query head，8 个 KV head（4:1 分组）
- 加速推理、减少解码内存
- 支持更高 batch size

**2. Sliding Window Attention (SWA)**
- 每个 token 最多关注前 W=4096 个 token
- 32 层下有效感受野约 131K tokens（~32 × 4096）
- 推理成本与窗口大小成线性关系，而非序列长度

**3. Rolling Buffer Cache**
- 固定大小的 KV 缓存（窗口大小 W）
- 缓存满后覆盖旧值
- **32K 序列缓存减少 8 倍内存**（无质量损失）

**4. 预填充与分块**
- 长 prompt 按窗口大小分块预填充
- 在缓存和分块之间计算注意力

### 模型参数
| 参数 | 值 |
|------|-----|
| dim | 4096 |
| n_layers | 32 |
| head_dim | 128 |
| hidden_dim | 14336 |
| n_heads | 32 |
| n_kv_heads | 8 |
| window_size | 4096 |
| context_len | 8192 |
| vocab_size | 32000 |

### 指令微调版本
- Mistral 7B-Instruct：在公开指令数据集上微调（无专有数据）
- MT-Bench：6.84 ± 0.07（vs Llama 2 13B Chat 的 6.65）

### 安全防护
- 系统 prompt 可实现 100% 拒绝不安全 prompt（175 个测试 prompt）
- 自反式内容审核：精度 99.4%，召回 95.6%

## 关键结果

### 学术基准
| 模型 | MMLU | HellaSwag | WinoGrande | HumanEval | GSM8K | MATH |
|------|------|-----------|------------|-----------|-------|------|
| Llama 2 7B | 44.4 | 77.1 | 69.5 | 11.6 | 16.0 | 3.9 |
| Llama 2 13B | 55.6 | 80.7 | 72.9 | 18.9 | 34.3 | 6.0 |
| **Mistral 7B** | **60.1** | **81.3** | **75.3** | **30.5** | **52.2** | **13.1** |
| Llama 1 34B | - | - | - | 22.0 | 44.0 | 7.6 |

- Mistral 7B 在 MMLU 上达到类似 Llama 2 **3 倍**参数量的性能
- 在 HumanEval 上接近 Code-Llama 7B（30.5 vs 31.1），同时保留非代码能力

### 人类评估
- llmboxing.com 上 Mistral 7B-Instruct 的输出被偏好 5020 次 vs Llama 2 13B Chat 的 4143 次

## 范式对比
| 维度 | Mistral 7B | Llama 2 13B | Llama 1 34B |
|------|-----------|------------|------------|
| 参数 | 7B | 13B | 34B |
| SWA | ✅ | ❌ | ❌ |
| GQA | ✅ | ❌ | ❌ |
| Apache 2.0 | ✅ | ❌ | ✅ |
| 性能密度 | 最高 | 中 | 低 |

## 可复用的工程经验

1. **SWA + GQA 的组合**是 7B 模型超越 13B 的架构基础。
2. **性能密度（performance per parameter）是比绝对性能更重要的指标**——对于生产部署至关重要。
3. **Rolling Buffer Cache** 是 SWA 工程实现的精妙设计，大幅降低长序列推理内存。
4. **自反式内容审核**（模型自己判断输出安全性）是一个实用的安全方案。
5. **Apache 2.0 许可**的商业友好性对社区采用至关重要。
