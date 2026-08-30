---
title: Qwen3.8-Flash-Next — Qwen4 架构的实验预览：QSA 微块稀疏注意力 + N-gram 嵌入 + Muon
date: 2026-08-26
source: https://huggingface.co/Qwen/Qwen3.8-Flash-Next
---

# Qwen3.8-Flash-Next — Qwen4 架构的实验预览：QSA 微块稀疏注意力 + N-gram 嵌入 + Muon

**发布日期：** 2026年8月26日
**来源：** https://huggingface.co/Qwen/Qwen3.8-Flash-Next | https://qwen.ai/blog?id=qwen3.8-flash-next
**工程范式：** 以"极致成本效率"为第一性约束的 Qwen4 架构探路——微块级稀疏注意力（QSA）+ Gated Residual + N-gram 嵌入 + 混合优化器，用 6B 激活对标 27B/旗舰级能力

## 设计哲学

Qwen3.8-Flash-Next 官方定位是 **"experimental preview of the architecture that will underpin Qwen4"**。它回答的问题不是"下一个模型多强"，而是"**当参数规模与上下文长度都在膨胀时，核心组件如何重新设计才能在成本上可持续**"。

四个核心创新全部服务于同一约束——把每 token 的成本压下去、同时不牺牲质量：

1. **QSA（Qwen Sparse Attention）替代 Gated Attention**：不是选单个 token，而是在 **micro-block 级别**操作——长上下文延迟显著下降，直击 agentic 负载
2. **Gated Residual**：加宽残差流（widened residual streams），用逐元素数据依赖读门 + 每分支标量写门调制信息流——在保持训练稳定性的前提下提升跨层表达能力
3. **N-gram Embedding**：用短 n-gram 索引做参数扩展的新轴——比 MoE 计算量更小、更易 offload，内存受限加速器上高效
4. **Tailored Training Recipe**：Muon 与 AdamW 按权重类别分工，基于重新拟合的 scaling laws 去掉 batch-size warmup，直接以目标 batch size 起步——减少优化器步数、支持更大学习率

**放弃了什么：** Flash-Next 是 125B/6B 激活的"小而极致"实验品，不是生产旗舰——生产旗舰是 Qwen3.8-Flash（1M 上下文、内置工具）。它主动放弃了一部分纯能力上限，换取对 Qwen4 架构方向的低成本验证。

## 关键架构决策

### 模型规格
- 总参数 125B，激活 6B，另有 51B N-gram 嵌入 + 4B MTP
- Hidden dim 2560，48 层
- Hidden layout：12 × (3 × (Gated DeltaNet → MoE) → 1 × (QSA → MoE))
- Token embedding 248,320（padded）；N-gram embedding 20,000,000（layer 2 的 bigram/trigram）
- 上下文：262,144 原生，可扩展至 1,000,000

### QSA（Qwen Sparse Attention）
- 24 Q-heads / 2 KV-heads，head dim 256，RoPE dim 64
- Indexer：MQA 结构，4 query heads + 1 shared key head，head dim 128
- **Budget：512 blocks 或 2048 tokens**——以块为粒度选择参与注意力的 token 集合

### Gated DeltaNet（线性注意力）
- 48 V-heads / 16 QK-heads，head dim 128

### MoE
- 512 专家，每 token 激活 10 routed + 1 shared，专家中间维度 640

### Gated Residual
- 4 branches，bottleneck rank 320

### 训练
- Muon + AdamW 按权重类别混合；重新拟合 scaling laws 指导；无 batch-size warmup
- MTP 1 层，多步训练

### 推理
- thinking 默认开启；`enable_thinking` / `preserve_thinking` / `reasoning_effort` 可控
- 长上下文建议静态 YaRN 按需调整 factor（如 524K 场景用 factor 2.0）

## 关键结果

（均为原文 model card 数字）

### 语言能力（vs Qwen3.8-27B / Qwen3.7-Plus / DeepSeek-V4-Flash-0731 / Claude Opus 4.6）
| Benchmark | Flash-Next | Qwen3.8-27B | Qwen3.7-Plus | DS-V4-Flash | Opus 4.6 |
|---|---|---|---|---|---|
| DeepSWE 1.1 | 58.7 | 42.2 | 16.5 | 54.4 | -- |
| SWE-bench Pro | 62.5 | 61.7 | 55.8 | 56.0 | 53.4 |
| SWE-bench Multilingual | 81.0 | 73.8 | 75.8 | -- | 77.5 |
| NL2Repo-Bench | 48.1 | 42.3 | 41.1 | 54.2 | 47.6 |
| CoWorkBench | 73.9 | 70.7 | 65.1 | 45.1 | 68.2 |
| JobBench | 55.7 | 33.4 | 27.6 | 41.3 | 36.6 |
| Agents' Last Exam | 24.3 / 51.2 | 20.4 / 42.9 | 13.2 / 33.6 | 25.2 / -- | -- |
| Toolathlon Verified | 73.5 | 67.1 | 50.6 | 70.3 | -- |
| IFBench | 81.3 | 79.5 | 79.1 | 79.2 | 62.5 |
| GPQA Diamond | 91.7 | 89.2 | 90.3 | 90.8 | 91.3 |
| HLE | 35.9 | 30.8 | 34.7 | 33.8 | 40.0 |
| LiveCodeBench v6 | 91.9 | 90.3 | 89.6 | 90.6 | 88.8 |

### 视觉语言能力
| Benchmark | Flash-Next | Qwen3.8-27B | Qwen3.7-Plus | Opus 4.6 |
|---|---|---|---|---|
| ClawEval-MM | 64.4 / 60.4 | 57.4 / 56.9 | 57.4 / 60.1 | 52.5 / 54.7 |
| RecreationBench | 49.9 | 47.1 | 30.2 | -- |
| AndroidWorld | 84.5 | 81.9 | 81.0 | 62.0 |
| OSWorld 2.0 (binary/partial) | 19.4 / 52.3 | 19.4 / 48.0 | 2.8 / 21.5 | -- |
| ERQA | 72.3 | 65.5 | 69.8 | 40.8 |
| RealWorldQA | 88.5 | 85.9 | 86.9 | 73.9 |
| MathVision (w/ CI) | 95.7 | 94.6 | 88.7 | 65.5 |

核心信号：**6B 激活的 Flash-Next 在绝大多数编码与 agent 基准上超越 27B 密集模型（Qwen3.8-27B）与 17B 激活的 Qwen3.7-Plus**——架构效率的验证成功。

## 范式对比

- **vs Qwen 自家主线（3.8-Max 的 Gated Attention 路线）**：Flash-Next 用 QSA 替换 Gated Attention，是"软注意力 → 稀疏块注意力"的范式切换；Gated DeltaNet 保留、MoE 布局延续——Qwen4 的候选形态是"DeltaNet 为主 + 稀疏块注意力为辅"
- **vs DeepSeek DSA / MiniMax MSA（同为稀疏注意力）**：DeepSeek DSA 走 token 级稀疏（top-k token 选择），MiniMax MSA 走两级 indexer + 块级；Qwen QSA 走 **micro-block 级 + budget 上限**（512 blocks / 2048 tokens）——三家在"稀疏粒度"上形成 token/block/micro-block 的路线分化
- **vs 纯线性注意力路线（如 Mamba/DeltaNet 纯化）**：Qwen 坚持混合——3 层 DeltaNet + 1 层软/稀疏注意力交错，证明纯线性注意力在 agent 场景尚不足以单独支撑

## 社区评价

原文未提供 HN/Reddit 讨论数据，未独立核实，暂不引用。可关注点：① HF 上标注"Upcoming release / waiting for the release"（8/26 当天发布），下载量 5.2 万+/月说明社区热度高；② 51B N-gram 嵌入是否真的比 MoE 更易 offload——这是内存受限部署的关键验证点。

## 可复用的工程经验

1. **用"架构预览"小模型验证下一代架构**：在 125B/6B 规模上验证 QSA/Gated Residual/N-gram 嵌入，再决定 Qwen4 主架构——架构创新的验证成本可以低一个数量级
2. **稀疏注意力的块粒度是关键旋钮**：token 级稀疏（DSA）vs block 级（MSA）vs micro-block 级（QSA）——粒度越小，索引越细但开销越大；budget 上限（512 blocks/2048 tokens）是控制延迟的可调参数
3. **加宽残差流需要门控**：widen residual stream 会破坏训练稳定性，Gated Residual（读门 + 写门）是恢复稳定性的关键配套
4. **混合优化器 + 无 warmup 是省步数利器**：Muon/AdamW 按权重类别分工 + scaling laws 指导直接以目标 batch 起步——大规模训练中省掉的每一步都是实打实的算力
