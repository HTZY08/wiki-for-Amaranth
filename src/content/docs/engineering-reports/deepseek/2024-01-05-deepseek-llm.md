---
title: DeepSeek LLM — 长期主义 Scaling Law 开源模型
date: 2024-01-05
source: arXiv 2401.02954
---

# DeepSeek LLM

**发布日期：** 2024-01-05（模型 2023-11-29）
**来源：** arXiv 2401.02954
**工程范式：** 长期主义路线——不是追 SOTA，而是系统建立 Scaling Law 的工程框架。

## 设计哲学

DeepSeek 的起点就和其他开源模型不同。LLaMA 追求「小参数出奇迹」，Falcon 追求「纯开源数据」，DeepSeek LLM 的定位是「长期主义」——花大量篇幅研究 Scaling Law 的细节（超参数缩放、最优模型/数据分配、数据质量影响），而不是急着刷榜。

核心约束：有限算力下如何最大化模型能力。DeepSeek 的选择是用理论指导实践——先通过大量小规模实验拟合 Scaling Law 公式，再用公式预测最优配置。

关键放弃：7B/67B 这个规模在当时不算最大（LLaMA 2 有 70B），但 DeepSeek 放弃了「追参数规模」而选择「追效率」。

## 关键架构决策

- **架构：** 标准 LLaMA 架构（Pre-Norm + RMSNorm + SwiGLU + RoPE），67B 用 GQA（8 kv_heads），95 层深而窄的设计（vs 典型的 80 层宽设计）
- **Tokenizer：** BBPE，词表 10 万+15 特殊 token，数字拆分到个位
- **训练数据：** 2T tokens（中英），跨 91 个 Common Crawl 快照做激进去重，去重率 89.8%（vs 单快照的 22.2%）
- **超参数 Scaling：** batch_size ∝ C^0.125，lr ∝ C^(-0.3271)
- **最优分配：** 以 non-embedding FLOPs/token 替代 params 作为模型规模指标，N_opt ∝ C^0.524，D_opt ∝ C^0.476
- **数据质量影响：** 高质量数据越多，新增算力应更多分配给模型扩展而非数据扩展
- **LR 策略：** Multi-step LR scheduler（80%/10%/10% 三段衰减），支持 continual training 复用权重
- **对齐：** 150 万指令（46.6% 数学/22.2% 代码/31.2% 通用）+ DPO。发现 7B 加 system prompt 会降性能，67B 反而提升
- **基础设施：** HAI-LLM 框架 + Flash Attention + ZeRO-1 + bf16 + fp32 梯度累积 + 异步 5 分钟 checkpoint

## 关键结果

- 67B Chat 在开放评测超越 GPT-3.5
- 在代码/数学/推理任务上超越 LLaMA-2 70B
- Scaling Law 预测对 1000 倍算力预算的模型（7B/67B）准确

## 范式对比

vs LLaMA-2（Meta，同期最强开源），DeepSeek LLM 参数相当但做了更系统的 Scaling Law 研究。vs GPT-3.5（闭源，同期基准），67B Chat 在开放评测上已能匹敌。DeepSeek 从一开始就表现出「研究驱动」而非「产品驱动」的风格——这是理解 DeepSeek 后来所有工作的钥匙。

## 可复用的工程经验

1. 跨快照去重（89.8% 去重率）是提升数据效率的关键——单快照去重的 22.2% 完全不够
2. 数字拆分到个位能显著提升数学推理能力
3. 数学数据占比高（46.6%）会导致重复率上升，需要两阶段微调缓解
4. Multi-step LR 比 cosine 更适合实际工程——支持 continual training
