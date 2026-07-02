---
title: DeepSeekMath — 数学预训练数据工程与 GRPO 强化学习
date: 2024-02-05
source: arXiv 2402.03300
---

# DeepSeekMath

**发布日期：** 2024-02-05
**来源：** arXiv 2402.03300
**工程范式：** 从 Common Crawl 大规模提取数学数据 + 无 critic 模型的强化学习算法创新。

## 设计哲学

DeepSeekMath 的设计围绕两个核心问题展开：如何从海量网络数据中高效提取数学内容，以及如何用更轻量的 RL 方法提升数学推理能力。前者催生了迭代式数据筛选管线——用 fastText 分类器对 Common Crawl 做多轮 recall，最终得到 120B tokens 的数学语料，7 倍于 Minerva 数据量。后者催生了 GRPO——去掉 RLHF 中的 critic/value 模型，用组内分数归一化替代价值函数估计，大幅降低显存开销。关键洞察是：代码预训练是数学推理的良好起点，DeepSeekMath-Base 继承自 DeepSeek-Coder-Base-v1.5 7B。

## 关键架构决策

- **基座模型：** DeepSeek-Coder-Base-v1.5 7B（而非通用 DeepSeek LLM），利用编程数据强化逻辑推理能力
- **数据配方：** 56% 数学 + 4% AlgebraicStack + 10% arXiv + 20% GitHub 代码 + 10% NL，共 500B tokens 继续训练
- **GRPO：** 组大小 G=32，不使用 critic 模型，advantage 由组内分数归一化得到。对比 PPO，GRPO 节省约 50% 训练显存
- **过程监督：** 在 GRPO 基础上，按步骤计算奖励，advantage 为未来步骤奖励之和的归一化值

## 关键结果

DeepSeekMath-Base 7B 在 MATH 上达 36.2%（few-shot CoT），持平 Minerva 540B（此前需 77 倍参数）。DeepSeekMath-Instruct 7B 经 SFT+GRPO 在 MATH 上达 51.7%（+5pp），GSM8K 达 88.2%（+5pp），CMATH 达 88.8%（+4pp）。GRPO+PS 优于 GRPO+OS，过程监督对数学推理价值显著。

## 范式对比

与 Minerva（540B 参数，RJT 数据）相比，DeepSeekMath 证明数据质量比模型规模更重要——7B 模型在 MATH 上接近 540B。与 Llemma 相比，DeepSeekMath 的数据量（120B vs 51.9B）和迭代筛选策略是关键差异。GRPO 为后续 DeepSeek 全系列 RL 训练奠定了算法基础。

## 可复用工程经验

1. 从代码模型继续训练做数学推理，比从通用语言模型更有效
2. 迭代式数据筛选（而非一次性过滤）能有效提升 recall
3. GRPO 是 PPO 的高性价比替代，适合预算有限的团队
4. 过程监督超越结果监督，但实现成本可控
