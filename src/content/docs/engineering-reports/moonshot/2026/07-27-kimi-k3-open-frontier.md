---
title: Kimi K3 — 开放前沿的 2.8T MoE 架构突破
date: 2026-07-27
source: https://www.kimi.com/blog/kimi-k3
---

# Kimi K3 — 开放前沿的 2.8T MoE 架构突破

**发布日期：** 2026-07-27
**来源：** https://www.kimi.com/blog/kimi-k3
**工程范式：** 以全新注意力机制（Kimi Delta Attention + Attention Residuals）为架构主干、极致稀疏 MoE（16/896）为规模杠杆，首个开源逼近 3T 参数级别的模型系列，走先发博客+后发技术报告的开放路线。

> **说明：** 本文基于 Kimi 官方技术博客撰写。完整技术报告将后续发布。博客中未披露的架构细节、训练超参数、数据组成等已在文中标注为"未披露"。

## 设计哲学

Kimi K3 的核心约束是：**在开源模型参数量级上突破 3T 天花板，同时维持可部署的推理效率。** 开源模型的前沿在过去 12 个月中一直被 Kimi 系模型定义——Kimi 连续 9 个月刷新开源模型参数量上限。K3 需要继续这一轨迹。

面对这一约束，K3 没有走单一架构增量改进的路线，而是引入了**两套全新注意力机制 + 一套 MoE 框架升级**：

- **Kimi Delta Attention (KDA)：** 一个高效的注意力缩放基础架构
- **Attention Residuals (AttnRes)：** 跨深度层选择性检索表示，而非均匀累积
- **Stable LatentMoE + Quantile Balancing：** 在 16/896 极端稀疏下保持路由稳定

放弃的是什么？K3 没有在 blog 中提及放弃了哪些设计，但结合 K2 系的已知架构，可以推断 K3 放弃了传统 MoE 的均匀专家分配假设，转而采用更激进的稀疏性 + 量化感知训练。

## 关键架构决策

### 注意力机制：Kimi Delta Attention (KDA) + Attention Residuals (AttnRes)

KDA 是 K3 的注意力基础设施，设计目标是支持超过万亿参数规模的注意力高效计算。AttnRes 则在深度维度上提供跨层表示的选择性检索——不是每一层都均匀累积前层信息，而是选择性检索有贡献的信息。两者共同构成"纵向稀疏+横向高效"的注意力框架。

### MoE 设计：16/896 专家 + Stable LatentMoE

- **总参数：** 2.8T
- **激活参数：** 未披露（由 16/896 路由密度可估算约 50B 级别）
- **专家数：** 896 个，每次激活 16 个
- **路由机制：** Stable LatentMoE 框架
- **专家均衡策略：** Quantile Balancing——直接从 router score 的分位数推导专家分配，消除启发式更新和敏感的均衡超参数
- **优化器：** Per-Head Muon——将 Muon 优化器推广到按注意力头独立优化，在 2.8T 规模下实现更自适应的学习

### 激活函数与门控

- **Sigmoid Tanh Unit (SiTU)：** 改进激活函数控制
- **Gated MLA：** 改进注意力选择性（Multi-head Latent Attention 的变体）

### 训练策略

- **量化感知训练：** 从 SFT 阶段起即使用 MXFP4 权重 + MXFP8 激活，确保广泛的硬件兼容性
- **专家并行训练：** 全平衡设计——静态形状 + 关键路径无主机同步，防止专家失衡降低吞吐
- **推荐的部署配置：** 64 加速器以上的 supernode 配置

### 推理优化

- **KDA Prefill Cache：** 在 vLLM 社区贡献了对应实现（将与模型一起发布）
- 官方 Kimi API 基于 Mooncake 解耦推理架构，编码类负载缓存命中率 >90%
- **定价：** \$0.30/MTok（缓存命中输入），\$3.00/MTok（缓存未命中输入），\$15.00/MTok（输出）

### 上下文窗口

- **1M token** 上下文窗口
- **原生多模态：** 文本、图像、视频在同一模型内理解

### Post-training

未在 blog 中详细披露。仅提及在"max thinking effort"模式下运行。

## 关键结果

以下数据均来自 Kimi K3 官方博客。注意：不同模型可能使用不同的 harness，直接数字对比需谨慎。

### 编码能力

| 基准 | Kimi K3 | Claude Fable 5 | GPT 5.6 Sol | GLM-5.2 |
|------|---------|----------------|-------------|---------|
| DeepSWE v1.1 | 67.3 (KimiCode) | — | — | — |
| Terminal-Bench 2.1 | 62.9 (KimiCode) | 未披露 | 未披露 | 55.8 |
| Program Bench | 66.6 (KimiCode) | 未披露 | 未披露 | 48.3 |
| SWE Marathon | 44.9 (Claude Code) | 35.1 (Claude Code, 35% fallback) | — | 40.5 |
| FrontierSWE (Dominance) | 54.1 (KimiCode) | 未披露 | 未披露 | 未披露 |
| PostTrain Bench | 74.5 (Claude Code) | 77.2 | 78.3 | 73.0 |
| MLS Bench Lite | 65.2 (KimiCode) | 未披露 | 未披露 | 60.0 |
| KCB 2.0 | 75.0 (KimiCode) | 未披露 | 未披露 | 未披露 |

### 生产力和 Agent 能力

| 基准 | Kimi K3 | Claude Fable 5 | GPT 5.6 Sol | GLM-5.2 |
|------|---------|----------------|-------------|---------|
| BrowseComp (1M ctx, 有上下文管理) | 90.7 | 69.0 | 73.0 | — |
| BrowseComp (无上下文管理) | 90.4 | — | — | — |
| OfficeQA Pro | 80.3 | 81.1 | 77.7 | 57.2 |
| SpreadsheetBench 2 | 66.4 | 64.2 | 57.1 | 41.6 |
| MCP Atlas | 70.9 | 未披露 | 未披露 | 未披露 |
| AutomationBench | 71.0 | 未披露 | 未披露 | 未披露 |
| GDPval-AA | 1736 | — | — | — |
| AA-Briefcase | 3,900 | — | — | — |
| APEX-Agents | 672 | — | — | — |

### 多模态能力

| 基准 | Kimi K3 |
|------|---------|
| MMMU-Pro | 79.4 |
| PerceptionBench | 84.0 |
| ZeroBench | 6.0 (5次运行) |

### 扩展效率

相比 Kimi K2，K3 在整体扩展效率上提升约 **2.5×**——结构变化使模型能更有效地将计算转化为智能。

## 范式对比

### vs Claude Fable 5 / GPT 5.6 Sol

博客明确承认 K3 的整体性能仍落后于这两种最强大的专有模型。但在特定方向（BrowseComp、编码马拉松类 benchmark）K3 展现了竞争力。

### vs GLM-5.2

K3 在几乎所有可比基准上显著领先 GLM-5.2——这反映了 2.8T 对比 200B+ 参数量级带来的结构化优势。

### vs MiniMax M3

两者都走开源路线，但路线差异明显：
- **参数量级：** K3 是 2.8T / 16 激活；M3 未公开总参数，但激活参数估计小得多
- **注意力机制：** K3 用 KDA + AttnRes；M3 用 MSA（MiniMax Sparse Attention）
- **开源战略：** M3 已开源权重；K3 承诺今日（2026-07-27）发布权重
- **上下文：** 两者都有 1M token 窗口

## 社区评价

截至撰写时未有广泛的 HN/Reddit 技术讨论（模型权重今日刚发布）。

## 已知限制（来自官方）

1. **对 thinking history 敏感：** K3 在 preserving thinking history 模式下训练。如果 agent harness 未能回传全部历史思考内容，或从其他模型切换到 K3，生成质量会高度不稳定。
2. **过度主动性：** 训练强调长周期、高难度任务，导致在遇到模糊用户意图时可能做出意外决策。需要在 system prompt 中明确行为边界。
3. **与顶级专有模型的体验差距：** 整体用户体验相比 Claude Fable 5 和 GPT 5.6 Sol 仍有可见差距。

## 可复用的工程经验

1. **Quantile Balancing 替代启发式均衡：** 在极端稀疏 MoE（16/896）下，从 router score 分位数推导专家分配比传统辅助均衡更简单、更稳定。消除了一个敏感的均衡超参数。
2. **Per-Head Muon：** 将优化器策略下放到每个注意力头维度——在超大参数规模下可能比全局优化更有效。
3. **量化感知训练前置化：** 从 SFT 阶段开始做 MXFP4/MXFP8 量化训练，减少了后期量化的适应损失。
4. **KDA + AttnRes 的组合：** 横向（KDA）和纵向（AttnRes）两个维度的稀疏化可以叠加，产生超线性的效率收益——相比 K2 的 2.5× 效率提升证明了这一点。
5. **训练→推理协同设计：** KDA 需要新的 prefill cache 策略（在 vLLM 中实现），说明架构创新必须配套推理基础设施的协同升级。
