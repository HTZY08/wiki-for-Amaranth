---
title: Kimi k1.5 — Scaling Reinforcement Learning with LLMs
date: 2026-07-03
source: arXiv 2501.12599
---

# Kimi k1.5: Scaling Reinforcement Learning with LLMs

**发布日期：** 2025-01 (arXiv 2501.12599)
**来源：** arXiv 2501.12599
**工程范式：** 极简 RL 路线——无需 MCTS/价值函数/过程奖励模型，仅靠长上下文 + 在线策略优化实现 SOTA 推理。

## 设计哲学

Kimi k1.5 的核心洞察是：复杂推理可以通过「在长上下文中进行自回归试错」隐式学习，无需显式的树搜索（MCTS）或过程奖励模型（PRM）。关键假设是——当模型被提供足够长的上下文（128K tokens），它可以通过在生成的文本中规划、反思、纠正来隐式模拟搜索过程。这使得 RL 训练大幅简化。

## 关键架构决策

### 1. 极简 RL 框架
- **无需 MCTS**、无需价值函数、无需过程奖励模型
- 使用**在线镜像下降**（online mirror descent）的变体进行策略优化
- 核心公式：对 k 个采样做平均，使用 `∇log πθ(y_j,z_j|x) [r(x,y_j,y*) - r̄] - τ/2 ∇log (πθ/πθ_i)`

### 2. 长上下文缩放（Long Context Scaling）
- RL 训练中将上下文窗口**扩展到 128K tokens**
- **Partial Rollouts**：跨迭代复用之前的轨迹段，避免完整重新生成，使长 CoT 训练变得高效
- 论文结论：「上下文长度是 LLM RL 持续缩放的关键维度」

### 3. 混合部署架构
- **Megatron + vLLM 混合部署**：训练和推理共享同一批 GPU，通过 Kubernetes Sidecar 容器管理
- **Checkpoint Engine**：通过 Mooncake（RDMA）在训练和推理之间快速转换权重
- 训练到推理切换 < 1 分钟，反向切换 ~10 秒

### 4. 代码沙箱优化
- 使用 `crun`、cgroup 复用、tmpfs overlay
- 容器启动时间 0.04 秒（vs Docker 0.12 秒）
- 每秒 120 个容器（vs 27）

### 5. Long2Short 方法
- 将长 CoT 的知识迁移到短 CoT 模型
- 四种策略：模型合并、最短拒绝采样、DPO、Long2short RL
- 「Long2short RL 在 token 效率上最优」

## 关键结果

| Benchmark | Long-CoT (k1.5) | OpenAI o1 | Short-CoT (k1.5) | GPT-4o |
|-----------|----------------|-----------|------------------|--------|
| AIME 2024 (Pass@1) | **77.5** | 74.4 | **60.8** | 9.3 |
| MATH 500 (EM) | **96.2** | 94.8 | **94.6** | 74.6 |
| Codeforces (Percentile) | **94** | 94 | – | – |
| LiveCodeBench (Pass@1) | 62.5 | 67.2 | **47.3** | 33.4 |
| MathVista (Pass@1) | **74.9** | 71.0 | 70.1 | 63.8 |
| MMMU-Val (Pass@1) | 70.0 | 77.3 | **68.0** | 69.1 |

Short-CoT 模式在 AIME 上以 60.8 分超越 GPT-4o（9.3）**+550%**。

## 范式对比

vs DeepSeek R1（671B/37B MoE，使用 GRPO 和冷启动），k1.5 用更小的模型规模和极简框架实现了可比或更好的效果。vs OpenAI o1（推测为密集模型 + MCTS），k1.5 证明了长上下文 RL 可以替代树搜索。

## 可复用的工程经验

1. **长上下文是 RL 缩放的关键维度**——提供更长的上下文窗口，模型可以隐式学习搜索和纠错
2. **Partial Rollouts 是长 CoT RL 训练的使能技术**——没有它就无法高效训练长序列
3. **代码沙箱的微优化（crun/cgroup/tmpfs）在规模化时带来数量级收益**
4. **Reward 质量比 RL 算法更重要**——CoT-RM（98.5% 准确率）远超经典 RM（84.4%）
5. **Long2Short 蒸馏是实用化的关键**——短 CoT 模式在推理时节省大量 token
