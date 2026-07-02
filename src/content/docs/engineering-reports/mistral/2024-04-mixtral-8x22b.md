---
title: Mixtral 8x22B — 超大 MoE 开源模型
date: 2024-04-10
source: mistral.ai/news (blog)
---

# Mixtral 8x22B

**发布日期：** 2024-04-10  
**来源：** mistral.ai/news/mixtral-8x22b  
**工程范式：** MoE 大规模化——141B 总参/39B 激活的稀疏专家模型。

## 设计哲学

Mixtral 8x22B 是 Mixtral 8x7B 的放大版本，将专家 FFN 从 7B 放大到 22B 级别。

核心哲学：**MoE 规模放大是平滑的**——从 8x7B 到 8x22B 不需要改动架构，只需要扩大每个专家的大小。

"Mixtral 8x22B sets a new standard for performance and efficiency within the AI community."

## 关键架构决策

### MoE 规格
- **8 个专家**，每 token 选 top-2
- **39B 活跃参数** / **141B 总参数**
- 架构与 Mixtral 8x7B 一致（GQA + SWA + RoPE）
- 上下文长度：64K

### 多语言
- 英语、法语、德语、西班牙语、意大利语
- 原生函数调用支持
- 约束输出模式支持

### 许可
- Apache 2.0 开源

## 关键结果

### 基准对比
| 基准 | Mixtral 8x22B (39B act) | Llama 2 70B | Command R+ |
|------|------------------------|------------|------------|
| MMLU | 领先 | 68.9 | 落后 |
| HellaSwag | 领先 | - | - |
| GSM8K | 领先 | 63.9 | - |
| HumanEval | 领先 | 29.9 | - |
| MATH | 领先 | 13.5 | - |

- 在所有基准上超越 Llama 2 70B
- 最佳性能-成本比的开源模型之一
- 在代码和数学任务上表现最优

## 范式对比
| 维度 | Mixtral 8x7B | Mixtral 8x22B | Llama 3 70B |
|------|-------------|--------------|------------|
| 活跃参数 | 12.9B | 39B | 70B |
| 总参数 | 46.7B | 141B | 70B |
| 上下文 | 32K | 64K | 8K |
| 多语言 | 4 种 | 5 种 | 英文为主 |
| 函数调用 | 有限 | 原生 | 有限 |

## 可复用的工程经验

1. **MoE 的低成本边际扩展**——从 8x7B 到 8x22B 不需要架构创新，只需放大专家。
2. **39B 活跃参数 vs 70B dense 的性价比优势**——以 ~55% 的活跃参数达到同等或更好性能。
3. **原生函数调用是 Mistral 的差异化能力**——Mixtral 8x22B 即支持函数调用。
4. **Apache 2.0 许可证的一致策略**降低了社区选择成本。
5. **64K 上下文在开源 MoE 上的实现**为长文档场景提供了经济的选择。
