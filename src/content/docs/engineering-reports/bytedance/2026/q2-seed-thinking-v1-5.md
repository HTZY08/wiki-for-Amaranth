---
title: ByteDance Seed-Thinking-v1.5 — 双轨奖励系统
date: 2026-07-03
source: seed.bytedance.com, github.com/ByteDance-Seed/Seed-Thinking-v1.5
---

# ByteDance Seed-Thinking-v1.5

**发布日期：** 2026-Q2
**来源：** seed.bytedance.com
**工程范式：** 参数效率路线——用 1/10 的总参数量匹配更大模型的推理能力。

## 设计哲学

ByteDance 的核心约束是推理成本的商业可行性——亿级用户产品（豆包、抖音）不能跑成本巨大的模型。他们选择 MoE（200B/20B）而不是密集架构，因为激活参数少意味推理成本低。关键 trade-off：总参数量大但激活少，训练成本高但推理成本低，对面向消费者的公司是正确选择。

核心架构：200B 总参 / 20B 激活的 MoE，延续 Seed 系列的参数效率路线。训练分为 SFT + RL 两阶段。

## 关键工程决策：双轨奖励系统

这是 Seed-Thinking-v1.5 最具工程智慧的创新。核心矛盾：RL 的 reward 信号越精确，覆盖的 task 类型越窄；覆盖越广，reward 信号越模糊。

解决方案：把奖励系统拆成双轨并行——

- **可验证任务（数学、代码）：** 走智能逻辑验证器（intelligent logic verification），不是简单检查答案对错，而是验证推理路径的每一步逻辑一致性。
- **不可验证任务（创意写作、开放问答）：** 走成对比较优化（pairwise comparison optimization），用对比排序代替绝对打分。

代价：训练流程更复杂、需要两套 reward pipeline。收益：数学推理和创意生成两类任务不再互相拖累。

## 关键结果

- AIME 2024: 86.7
- GPQA: 77.3
- Codeforces pass@8: 55.0
- 与 DeepSeek R1（671B/37B）和 OpenAI o3-mini 相比，以约 1/10 的总参数量达到可竞争水平

## 范式对比

vs DeepSeek R1（671B/37B，统一 GRPO），Seed 的双轨奖励更定制化但更复杂。vs OpenAI o3（未公开架构但推测为密集），Seed 以 MoE 的低激活参数量打性价比。

## 可复用的工程经验

1. 当 task 类型差异大时，别用统一 reward——拆成多轨
2. 逻辑验证器应该验证推理路径而非仅验证最终答案
3. SFT 数据的构建质量比 RL 算法本身更重要