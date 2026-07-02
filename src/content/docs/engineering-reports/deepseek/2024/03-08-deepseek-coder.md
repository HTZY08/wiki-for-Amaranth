---
title: DeepSeek-Coder — 仓库级代码预训练的工程范式
date: 2024-03-08
source: arXiv 2401.14196
---

# DeepSeek-Coder

**发布日期：** 2024-03-08
**来源：** arXiv 2401.14196
**工程范式：** 以仓库级数据构建和 FIM 训练策略为核心的代码预训练工程。

## 设计哲学

DeepSeek-Coder 的核心洞察是：代码预训练的质量取决于数据组织的粒度。此前 CodeGen、StarCoder 等模型以文件为单位处理代码，丢失了跨文件依赖关系。DeepSeek-Coder 首次在预训练阶段引入仓库级数据构造：用解析器提取 import/include 依赖，按拓扑排序组织文件顺序，每个文件前加路径注释。这种设计让模型天然理解跨文件调用，而非靠上下文窗口硬撑。另一个关键决策是放弃了"代码模型只需代码数据"的假设，保留 10% 英文代码相关自然语言和 3% 中文高质量语料，确保模型的自然语言理解能力不被遗忘。

## 关键架构决策

- **规模：** 1.3B/6.7B/33B 三档（33B 用 GQA 8 kv_heads），从头训练 2T tokens
- **FIM 策略：** 经过系统消融，选择 50% PSM（Prefix-Suffix-Middle）比例，平衡 FIM 性能和标准生成功效。MSP（Masked Span Prediction）全面劣于 PSM
- **长上下文扩展：** RoPE base frequency 从 10000 扩展到 100000，额外 1000 步训练 16K 序列，理论支持 64K
- **训练优化：** FlashAttention v2 + 三阶段 LR（每阶段减少 √10），AdamW（β1=0.9, β2=0.95）

## 关键结果

HumanEval 上 DeepSeek-Coder-Instruct 33B 达 79.3%（Pass@1），超越 Codex（72.2%）和 GPT-3.5 Turbo（76.2%）。多语言编程（MBPP、Multiple-APPS、DS-1000）上保持开源最佳。FIM 消融实验表明 50% PSM 是 Pareto 最优点。

## 范式对比

与 StarCoder（仅文件级数据）相比，仓库级数据使跨文件完井准确率提升显著。与 CodeLLaMA 相比，DeepSeek-Coder 的 FIM 策略更系统化——不是简单加减 FIM 比例，而是通过完整消融找到最优解。

## 可复用工程经验

1. 仓库级数据是代码预训练的"应有基线"，拓扑排序加路径注释实现简单效果大
2. FIM 策略必须消融，50% PSM 是最优起点
3. 代码模型需要保留自然语言数据来维持通用能力
4. 从代码基座开始做数学推理是个好起点
