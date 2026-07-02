---
title: MiniMax Sparse Attention (MSA) — 注意力机制第三次范式转移
date: 2026-07-03
source: arXiv 2606.13392
---

# MiniMax Sparse Attention (MSA)

**发布日期：** 2026-06-30
**来源：** arXiv 2606.13392
**工程范式：** 硬核系统协同设计路线——不追求理论最优算法，追求在 H800 上能实际跑出 wall-clock 加速。

## 设计哲学

MiniMax 面对的核心约束是 ultra-long-context 推理的成本墙——1M token 的 full attention 在 109B 模型上根本不可部署。他们放弃了 token-level 细粒度稀疏（DeepSeek DSA 路线）而选择 block-level 粗粒度稀疏，因为 block 粒度能在 GPU tensor core 上跑满。

关键决策：block-wise + GQA group-wise selection + 全量 KV cache 保留（不做压缩）。

## 关键架构决策

- **注意力架构：** 双分支结构（Index Branch + Main Branch）。Index Branch 只有两个投影矩阵，对 KV block 打分，每 GQA group 独立选择 top-k block；Main Branch 只对被选中的 block 做精确注意力计算。
- **Block 设计：** block size = 128，k = 16（每个 query 只看 2048 个 token 的 block），强制包含当前 query 所在 block 保证稳定性。
- **Index Branch 训练：** 通过 KL 散度对齐实现，前 40B tokens 做 warmup 后再启用稀疏。stop-gradient 设计防止 indexer 退化。
- **GPU Kernel：** 为 H800 写了三个定制 kernel：
  - Exp-Free TopK：用 per-thread register min-heap 代替 softmax 排序阶段
  - KV-Outer Sparse Attention：把迭代顺序从 query-outer 翻转为 KV-outer，算术强度从 G（query head 数）提升到 (2/3)*Bk（约 85 倍）
  - Sparse KL Loss Backward：用 persistent grid + global atomic counter 实现动态负载均衡
- **推理加速：** 1M 上下文下 Prefill 14.2x 加速，decode 7.6x 加速，总体注意力计算缩减 28.4x，质量零损失

## 范式对比

| 维度 | MiniMax MSA | DeepSeek DSA | GLM IndexShare |
|------|-------------|--------------|----------------|
| 稀疏粒度 | block-level | token-level | block-level |
| Indexer 共享 | 每层独立 | 每层独立 | 4 层共享 |
| KV cache | 全量保留 | 压缩 | MLA 压缩 |
| 硬件优化 | 3 个定制 GPU kernel | 通用实现 | 通用实现 |
| Wall-clock 加速 | 实测 3.7-14.2x | 理论 FLOPs 缩减 | FLOPs ↓2.9x |

三条路线各有取舍——MSA 最简洁，DSA 最精细，IndexShare 最节省 indexer 开销。共同趋势：2026 下半年的注意力标准将从「谁做 sparse attention」变成「谁做的 sparse attention 能真正跑出 wall-clock 加速」。

## 可复用的工程经验

1. 不要追求理论 FLOPs 缩减，要追求 wall-clock 加速
2. block-level 优于 token-level，除非不 care GPU 利用率
3. indexer 的 warmup 是必须的，不 warmup 直接上 sparse 质量下降显著
4. stop-gradient 防止 KL 蒸馏 collapse 是关键但隐式的 trick
5. KV-Outer 迭代顺序翻转是经典的系统优化思路——换个角度看问题，算术强度翻 30 倍

## 社区评价

r/LocalLLaMA：MSA 的 GPU kernel 设计值得每个做 attention 优化的团队学习。r/MachineLearning 指出 MSA 是 M3 的基础，市场反应正面。

## 战略意义

MSA 是 MiniMax M3 的基础架构。据社区推测，M3 将结合 MSA + Forge RL 体系 + M2 的细粒度 MoE，形成完整的「注意力稀疏化 + 训练系统化 + 架构精细化」三线组合。如果推测成立，M3 可能成为第一家同时做好这三条线的公司。
