---
title: Qwen3-Coder-Next — 极致参数效率 MoE
date: 2026-07-03
source: arXiv 2603.00729
---

# Qwen3-Coder-Next

**发布日期：** 2026-03
**来源：** arXiv 2603.00729
**工程范式：** 极致参数效率 + agentic training 路线——80B 仅 3B 激活，业界最低的 active parameter ratio。

## 设计哲学

Qwen 团队的最重要约束是本地开发和低延迟场景。80B 总参但只激活 3B 的 MoE 设计是极致的效率优先选择。为实现 agentic 能力，构建了 MegaFlow 编排系统、合成了约 165 万可验证代码任务实例（约 800K 来自真实 PR，约 851K 来自合成 bug）。

## 关键架构决策

- **MoE：** 80B 总参 / 3B 激活（业界最低的 active parameter ratio）
- **Attention：** hybrid attention（与 Qwen3-Next 保持一致）
- **训练 pipeline：** continued pretraining → SFT → specialized experts → distillation
- **合成数据：** 165 万+ 个可验证代码任务，跨 9+ 编程语言

## 范式对比

vs Kimi K2.7（1T/32B，超大 MoE），Qwen3-Coder-Next 是另一个极端——用最少的激活参数做编码。3B 激活参数的效率极高，但极限能力不如大模型。

## 可复用的工程经验

1. agentic training 需要可验证的执行环境反馈
2. 不同 scaffold 间的能力不迁移，需要 scaffold-specific 数据
3. 最佳拟合打包（BFP）优于简单拼接