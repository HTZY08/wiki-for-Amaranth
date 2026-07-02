---
title: DeepSeek V4 Preview — 放弃 MLA，拥抱混合注意力
date: 2026-07-03
source: HuggingFace deepseek-ai/DeepSeek-V4-Pro
---

# DeepSeek V4 Preview

**发布日期：** 2026-04-24
**来源：** HuggingFace deepseek-ai/DeepSeek-V4-Pro
**工程范式：** 极致推理效率路线——自 V2 以来最大的架构变更，放弃定义 V2/V3 的核心发明 MLA。

## 设计哲学

DeepSeek 面对的核心约束是推理成本——KV cache 随序列长度线性增长，1M 上下文下 V3.2 的 KV cache 大到部署成本不可接受。他们选择了一次架构级的彻底重构：放弃自己定义了两代的 MLA（Multi-head Latent Attention），转向 CSA+HCA 混合注意力。这是罕见的「自我革命」——放弃自己创造并验证过的成熟架构。

关键取舍：放弃 MLA 的 KV 压缩路线，选择稀疏化路线。彻底性在于不仅改了 attention，连残差流都换了（mHC 替代标准残差连接），optimizer 也从 AdamW 换成了 Muon。

## 关键架构决策

- **注意力架构：** CSA（Compressed Sparse Attention, ~4x 压缩）+ HCA（Heavily Compressed Attention, ~128x 压缩）的混合注意力。所有层仍然是 attention-based——没有用 linear attention 替换 quadratic attention。
- **稀疏机制：** FP4 lightning indexer 选 top-k 相关 block 做 attention（CSA），HCA 提供 128x 压缩后的 dense attention 作为全局粗粒度视图。
- **Sliding Window：** 128-token sliding window + learnable attention sinks。
- **残差流：** mHC（Manifold-Constrained Hyper-Connections）替代标准残差连接，约束在 Birkhoff 多面体上的混合矩阵，谱范数 ≤ 1，消除深度网络梯度爆炸。
- **模型规格：** V4-Pro（1.6T 总参/49B 激活，61 层），V4-Flash（284B 总参/13B 激活，43 层），均支持 1M 上下文。
- **训练优化：** Muon 优化器（大部分参数）+ FP4 QAT（专家权重和 CSA indexer）。
- **推理效率：** KV cache 仅为 V3.2 的 10%（Pro）和 7%（Flash）。单 token 推理 FLOPs 为 V3.2 的 10%（Flash）和 27%（Pro）。
- **开源：** MIT 协议，HuggingFace 可下载。

## 范式对比

DeepSeek 的路线是「自己造轮子——发现轮子不够好——砸了重造」。V2 定义 MLA 时它是第一个用 latent attention 压缩 KV 的团队，V4 放弃 MLA 时也是第一个承认 MLA 路线在超长上下文下可能不是最优解的团队。这种自我否定的能力在 AI 工程界极其罕见。

与 MiniMax MSA（block-level 稀疏）和 GLM IndexShare（跨层共享 indexer）对比，DeepSeek 的 CSA 走 token-level 细粒度选择路线，理论上 FLOPs 缩减潜力最大，但 GPU 利用率可能不如 block-level 方案。

## 社区评价

HN 2091 points/398 comments。r/LocalLLaMA 深入讨论：
- "CSA+HCA 没有用 linear attention 替换 quadratic attention，所有层仍然是 attention-based"
- "DeepSeek 是目前唯一解决该训练稳定性问题并落地的实验室"
- "这是 preview 版本，正式版可能还有变化"

## 可复用的工程经验

1. 架构层面的自我革命是痛苦但必要的——不要被自己的历史成就绑定
2. mHC 的 Birkhoff 多面体约束是解决深度网络梯度爆炸的优雅方案
3. FP4 QAT + Muon 优化器的组合是训练效率和模型质量平衡的关键
4. 所有层保持 attention-based 而不是替换为 linear——这是与 RWKV/Mamba 等路线的根本区别
