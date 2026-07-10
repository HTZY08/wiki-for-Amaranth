---
title: Gemma 4 技术报告 — 开放权重多模态模型系列，从小型边缘部署到高效推理
date: 2026-07-10
source: https://arxiv.org/abs/2607.02770
---

# Gemma 4 技术报告

**发布日期：** 2026-07-02
**来源：** [arXiv:2607.02770](https://arxiv.org/abs/2607.02770)
**工程范式：** Google DeepMind 的开放权重策略——在受限参数量下通过架构创新实现与小规模 MoE 模型竞争的密度化路线

## 设计哲学

Gemma 4 的核心约束是**计算效率 vs 能力覆盖**。Google DeepMind 不做超大规模 MoE（不像 DeepSeek V4 的 1.6T / GLM-5.2 的 744B），而是聚焦于 2.3B–31B 参数范围内的开放权重模型，目标覆盖从手机端到服务器的全场景。

关键权衡：
- **放弃"更大就是更好"**：31B 是最大稠密模型，MoE 版本仅 26B total / 4B active。对比之下，同期的开放权重竞品（GLM-5.2 / Kimi K2.6 / DeepSeek V4）活跃参数都在 30–50B 范围。
- **把资源投入到架构创新而非参数扩容中**：思考模式（thinking mode）、无编码器架构（encoder-free）、多 token 预测草稿头（MTP drafter）——这些都不是 scale 驱动的改进，而是 compute efficiency 驱动的改进。
- **原生多模态而非后期拼接**：所有模型（包括最小的 2.3B）都原生支持文本+图像+音频，12B 版本采用统一无编码器设计，直接处理 raw audio patches 和 image patches。

## 关键架构决策

### 注意力机制
- **混合注意力架构**：本地滑动窗口与全局注意力的 5:1 比例（E2B 为 4:1）
- **pp-RoPE 位置编码**：全局层使用 p=0.25 的 p-RoPE，本地层使用标准 RoPE；全局 RoPE 频率设为 1M，本地层为 10k
- **KV cache 共享与重用**：全局层重用 keys 作为 values（keys = values），结合 KV cache 共享，全局 KV cache 占用减少 37.5%
- QKNorm 和 RMSNorm 前后归一化

### MoE 设计
- 仅一个 MoE 变体：26B-A4B（26B 总参数，3.8B 活跃参数）
- 其余模型（E2B、E4B、12B、31B）均为稠密架构
- E2B 和 E4B 使用逐层嵌入（per-layer embeddings），使有效参数量分别为 2.3B 和 4.5B（总参数分别为 5B 和 8B）

### 训练策略
- 词表大小：262k（SentencePiece tokenizer，split digits，preserved whitespace，byte-level encoding）
- 预训练数据截止日期：2025 年 1 月
- 训练基础设施：
  - E2B: TPUv6e × 4,096 chips
  - E4B: TPUv6e × 6,144 chips
  - 12B: TPUv5p × 12,288 chips
  - 26B-A4B: TPUv6e × 6,144 chips
  - 31B: TPUv6e × 10,240 chips
- 优化器状态使用 ZeRO-3 分片
- 多 Pod 训练使用 Pathways 方法
- 使用 Slice-Granularity Elasticity 实现局部故障时连续训练

### 推理优化
- **MTP Drafter**：训练了 4 层 Transformer 的小型草稿头，用于投机解码。草稿头通过 cross-attention 利用主模型的 KV cache，无需单独的 MTP prefill
- **QAT 量化**：提供量化感知训练的量化版本，E2B/E4B 为 mobile quantization（int2/int4 混合 + int8 激活），较大模型为 Q4_0
- 量化后 E2B 仅 0.8GB，12B 仅 7.65GB

### Post-training
- 增加思考模式（thinking mode）——模型在回答前生成推理轨迹
- 数据过滤：移除个人信息、不安全输出、幻觉倾向数据
- 使用 `<|think|>` 控制 token 切换思考模式
- `<|channel>thought...<channel|>` 格式输出推理轨迹

### 无编码器架构（12B 模型）
- 图像：48×48×3 RGB patches → 单层大 matmul（35M 参数）→ 2D 坐标位置编码 → LayerNorm
- 音频：16kHz raw audio → 40ms chunks（640 维向量）→ 直接投影到 LLM 嵌入空间
- 完全摒弃了独立的视觉编码器（550M）和音频编码器（305M USM），代之以轻量投影模块
- 优势：减少内存碎片，简化部署

### 视觉编码器
- 较大模型（≥12B, MoE, 31B）使用 550M ViT，patch size 16
- E2B/E4B 使用 150M ViT
- 支持可变宽高比，轴向 2D-RoPE + 非因果注意力 + 2D 绝对位置嵌入
- 最大视觉 token 数：70 / 140 / 280 / 560 / 1120

### 音频编码器
- E2B/E4B 使用 305M 编码器（基于 USM），40ms chunks with Mel filterbank
- 相比 Gemma 3n 参数减少 55%（从 680M 降至 305M），不采用 vector quantization
- 量化后编码器从 390MB 降至 87MB（78% 缩小）

## 关键结果

### 文本推理基准（思考模式）

| Benchmark | 31B | 26B-A4B | 12B | E4B | E2B | Gemma 3 27B (非思考) |
|-----------|-----|---------|-----|-----|-----|---------------------|
| MMLU Pro | 85.2 | 82.6 | 77.2 | 69.4 | 60.0 | 67.6 |
| AIME 2026 no tools | 89.2 | 88.3 | 77.5 | 42.5 | 37.5 | 20.8 |
| LiveCodeBench v6 | 80.0 | 77.1 | 72.0 | 52.0 | 44.0 | 29.1 |
| Codeforces Elo | 2150 | 1718 | 1659 | 940 | 633 | 110 |
| GPQA Diamond | 84.3 | 82.3 | 78.8 | 58.6 | 43.4 | 42.4 |
| HLE | 19.5 | 8.7 | 5.2 | - | - | - |
| IFEval | 98.9 | 98.5 | 97.2 | 96.7 | 94.6 | 90.4 |

### 视觉基准（高分辨率，思考模式）

| Benchmark | 31B | 26B-A4B | 12B | E4B | E2B |
|-----------|-----|---------|-----|-----|-----|
| MMMU Pro | 76.9 | 73.8 | 69.1 | 52.6 | 44.2 |
| MATH-Vision | 85.6 | 82.4 | 79.7 | 59.5 | 52.4 |
| InfographicVQA | 92.0 | 89.3 | 88.4 | 70.0 | 63.9 |

### 长期上下文（无思考模式）

| Benchmark | Metric | Length | 31B | 26B-A4B | 12B | E4B | E2B | Gemma 3 27B |
|-----------|--------|--------|-----|---------|-----|-----|-----|-------------|
| RULER | Accuracy | 128k | 96.4 | 89.8 | 91.2 | 86.6 | 70.4 | 66.0 |
| GraphWalks | F1 | <128k | 82.3 | 72.6 | 71.0 | 50.9 | 4.1 | 32.8 |

### 人类评估（Arena Text，截至 2026-06-19）
- Gemma 4 31B Elo 1451 —— 稠密模型类别排名第一的开放模型
- Gemma 4 26B-A4B Elo 1438

## 范式对比

与同赛道的开放权重模型对比：

| 维度 | Gemma 4 | DeepSeek V4 | GLM-5.2 | Qwen3.5 |
|------|---------|-------------|---------|---------|
| 最大活跃参数 | 31B (稠密) / 4B (MoE) | 49B (MoE) | 40B (MoE) | 17B (MoE) |
| 总参数 | 31B / 26B | 1.6T | 744B | 397B |
| 思考模式 | ✅ | ✅ | ✅ | ✅ |
| 原生多模态 | ✅ (text+image+audio) | ❌ (text only) | ❌ (text only) | ✅ |
| 无编码器音频 | ✅ (12B) | - | - | ❌ |
| 开源协议 | Apache 2.0 | MIT | MIT | Apache 2.0 |

**关键差异：** Gemma 4 是唯一同时覆盖 2.3B–31B 全范围、且在小参数下通过架构创新追赶大参数竞品的模型系列。12B 无编码器设计在业界具有独创性。

## 社区评价

- Digital Trends："Gemma 4 31B is the best dense open model money can't buy. It punches well above its 31B weight class."
- HuggingFace 上 Gemma 4 发布后 5 小时内获得 200+ ❤️，社区对无编码器 12B 模型关注度最高
- X 上关于 Gemma 4 训练数据量的讨论引发争议——有评论推测训练 token 数大幅超过 Gemma 3

## 可复用的工程经验

1. **KV cache 共享 + p-RoPE 的组合**：全局层重用 keys 作为 values，减少 37.5% KV cache 占用，且不影响长上下文检索精度。这是一个几乎无代价的推理优化，任何 Transformer 模型都可以采用。
2. **分离式草稿头设计**：MTP drafter 通过 cross-attention 使用主模型的 KV cache，免除单独的 prefill 阶段，支持任意草稿长度。对边缘部署场景的投机解码特别有价值。
3. **完全摒弃编码器**：12B 模型的 encoder-free 设计证明，对于中小规模模型，用 35M 参数的 matmul 替代 550M 参数的 ViT 是可行的。这对边缘部署模型的视觉模态接入有参考价值。
4. **思考模式的工程实现**：用 `<|think|>` 控制 token 切换思考模式，用 `<channel>thought` 标记输出推理轨迹——简单、可预测、与现有训练框架兼容。
5. **逐层嵌入压缩**：E2B/E4B 的 per-layer embeddings 使"有效参数"远小于"总参数"，在没有性能损失的前提下降低显存占用。
