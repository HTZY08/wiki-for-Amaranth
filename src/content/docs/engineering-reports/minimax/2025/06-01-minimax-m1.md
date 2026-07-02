---
title: MiniMax-M1 — 世界上首个开源大规模混合注意力推理模型
date: 2025-06-01
source: arXiv 2506.13585
---

# MiniMax-M1

**发布日期：** 2025-06-01  
**来源：** arXiv 2506.13585  
**工程范式：** 硬核系统协同设计——用 Lightning Attention 高效扩展推理时计算。

## 设计哲学

MiniMax-M1 是 **世界上第一个开源、大规模、混合注意力推理模型**。基于 MiniMax-Text-01 的基础架构（456B 总参数/45.9B 激活），通过大规模 RL 训练获得推理能力。其核心价值主张是 **效率**：相比 DeepSeek R1，M1 在生成 100K tokens 时只消耗 25% 的 FLOPs——这使得推理时计算的扩展成本大幅降低。

更惊人的是训练效率：通过混合注意力 + CISPO 算法，M1 的全量 RL 训练在 **512 张 H800 GPU 上仅需 3 周，租用成本仅 $534,700**。这是当时最具成本效益的推理模型训练。

## 关键架构决策

- **基座模型：** MiniMax-Text-01（456B/45.9B, MoE, 混合注意力）
- **推理训练：** 大规模 RL，涵盖数学推理和基于沙箱的真实世界软件工程环境
- **上下文窗口：** 原生 1M tokens（8 倍于 DeepSeek R1 的 128K）
- **RL 算法：** CISPO（Clipped Importance Sampling Policy Optimization）
  - 创新点：clip importance sampling weights 而非 token updates
  - 优势：比 PPO、GRPO 等变体更高效
- **Lightning Attention 的核心优势：**
  - 线性复杂度使推理时计算的 FLOPs 随思考长度线性增长（而非二次增长）
  - 在 100K thinking tokens 时消耗仅 DeepSeek R1 的 25%
- **版本：** 发布 40K 和 80K thinking budgets 两个版本

### 关键结果

| 指标 | MiniMax-M1-80K | DeepSeek R1 | Qwen3-235B |
|------|---------------|-------------|------------|
| 训练成本 | $534,700 (512 H800 × 3 周) | 显著更高 | - |
| 上下文 | 1M | 128K | - |
| 推理效率 (100K tokens FLOPs) | 25% of R1 | 100% | - |
| 软件工程 | 领先 | 强 | - |
| 工具使用 | 领先 | - | - |
| 长上下文 | 领先 | 有限 | - |

### CISPO 核心直觉

| 算法 | Token 更新 | Importance Weight | 训练稳定性 |
|------|-----------|-------------------|-----------|
| PPO | clip token prob | raw | 高 |
| GRPO | group norm | raw | 中 |
| CISPO | 无 clip | clip weight | 更高 |

## 范式对比

| 维度 | MiniMax-M1 | DeepSeek R1 | OpenAI o1 |
|------|-----------|-------------|----------|
| 架构 | MoE + Hybrid Attention | MoE + Dense Attention | 未公开 |
| 开源 | ✅ | ✅ | ❌ |
| 训练成本 | $534,700 | ~$5M+ | 未公开 |
| 推理效率 | 25% FLOPs of R1 | 基线 | 更高成本 |
| 上下文 | 1M | 128K | 128K |

## 可复用的工程经验

1. **CISPO 是比 PPO/GRPO 更高效的 RL 算法选择** —— clip importance weight 而非 token prob 的创新值得推广
2. **Hybrid Attention 对推理时计算的效率优势是指数级的** —— 思考 100K tokens 和 10K tokens 的额外开销在 O(n) 线性下可控
3. **低成本训练（$534,700 = 512 H800 × 3 周）开源的推理模型可以匹配闭源 SOTA** —— 证明了开源-闭源差距在推理领域在缩小
4. **1M 上下文推理模型比 128K 的有本质优势** —— 长文档代码库、长对话历史的推理任务会越来越多
