---
title: Ministral 3 — Cascade Distillation 高效小模型家族
date: 2025-12-01
source: arXiv 2601.08584
---

# Ministral 3 Series

**发布日期：** 2025-12-01  
**来源：** arXiv 2601.08584  
**工程范式：** Cascade Distillation——通过逐级剪枝与蒸馏从大模型高效导出小模型。

## 设计哲学

Ministral 3 系列是 Mistral AI 的小模型产品线，覆盖 3B、8B、14B 三个尺寸。其核心理念是 **Cascade Distillation（级联蒸馏）**——不从头训练小模型，而是从强父模型（Mistral Small 3.1，24B）通过迭代剪枝和蒸馏高效导出。

关键洞察：**小模型不需要从头训练**。通过从 24B 父模型剪枝和蒸馏，Ministral 3 仅用 1-3T 训练 tokens 就达到其他模型 15-36T tokens 训练的效果。

"Unlike popular pretrained models such as Qwen3 or Llama3 that are trained on 36 trillion and 15 trillion tokens respectively, we are able to produce competitive models trained for between 1 and 3 trillion tokens."

## 关键架构决策

### Cascade Distillation 方法
1. 从 **Mistral Small 3.1**（24B 参数）父模型开始
2. 通过**迭代剪枝**减少层数和宽度
3. **知识蒸馏**从父模型传递知识到子模型
4. **继续训练**在小量 tokens 上微调

### 模型规格
| 尺寸 | 参数 | 类型 | 训练 tokens |
|------|------|------|-----------|
| Ministral 3B | 3B | Dense | ~1T |
| Ministral 8B | 8B | Dense | ~2T |
| Ministral 14B | 14B | Dense | ~3T |

每个尺寸有三个变体：
- **Base**：预训练基础模型
- **Instruct**：指令微调
- **Reasoning**：复杂问题推理

### 架构
- 标准 Decoder-only Transformer
- Dense（非 MoE）
- 继承 Mistral Small 3.1 的架构设计（GQA、RoPE 等）

### 效率
- 相比从零训练 Qwen3（36T tokens）或 Llama 3（15T tokens），Ministral 3 仅需 1-3T tokens
- 训练成本降低 5-10 倍
- 推理成本按参数量比例减少

## 关键结果

### 性能对比
| 基准 | Ministral 3B | Ministral 8B | Ministral 14B | Qwen2.5-7B | Llama 3.2-3B |
|------|-------------|-------------|--------------|------------|-------------|
| MMLU | 竞争性 | 竞争性 | 强 | 基线 | 基线 |
| 推理 | 良好 | 强 | 最强 | - | - |
| 代码 | 良好 | 强 | 强 | - | - |

Ministral 3 系列在各自参数量级上具有竞争力：
- 3B：与 Llama 3.2-3B 竞争
- 8B：与 Qwen2.5-7B、Llama 3.1-8B 竞争
- 14B：在 14B 级别具有最强性能之一

### 推理变体
- 专门的推理版本（Reasoning variant）针对复杂问题优化
- 可能使用了 Chain-of-Thought 或 RL 训练

## 范式对比
| 维度 | Ministral 3 | Qwen 3 | Llama 3.2 |
|------|------------|-------|-----------|
| 训练策略 | Cascade Distillation | 从头训练 | 从头训练 |
| 训练 tokens | 1-3T | 36T | 9T+ |
| 核心优势 | 极致效率 | 全面覆盖 | 社区生态 |
| 小模型 | 3B/8B/14B | 0.5B-72B | 1B/3B/8B |
| 推理变体 | ✅ | 部分 | ❌ |

## 可复用的工程经验

1. **Cascade Distillation 是训练小模型的高效替代方案**——用 1/10 的训练成本达到相近性能。
2. **"父模型 → 剪枝 → 蒸馏"管线**可以系统化地导出不同尺寸的子模型。
3. **训练 tokens 从 15T+ 降到 1-3T 是巨大的成本节省**——对预算有限的团队是可行路径。
4. **小模型的推理版本（Reasoning variant）**增加了产品差异化。
5. **Dense 小模型 + 蒸馏**的组合在边缘部署场景特别有吸引力——不需要 MoE 的路由开销。
