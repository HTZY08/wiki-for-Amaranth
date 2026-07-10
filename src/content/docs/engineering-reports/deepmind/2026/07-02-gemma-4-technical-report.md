---
title: Gemma 4 Technical Report — 密度化路线上的架构创新
date: 2026-07-02
source: arXiv:2607.02770
---

# Gemma 4 Technical Report

**发布日期：** 2026-07-02  
**来源：** [arXiv:2607.02770](https://arxiv.org/abs/2607.02770)  
**工程范式：** 受限参数量下通过架构创新追赶大参数竞品的密度化路线。

---

## 设计哲学

**核心约束：** 开源模型必须在可控参数量内实现前沿级能力。Gemma 4 覆盖从 2.3B（端侧）到 31B（数据中心）的设备生态，最大的 31B 稠密模型也要与 700B+ MoE 开源模型（GLM 5、DeepSeek V4）同台竞技。

**面对约束的架构选择：**

- **不堆参数，堆密度。** Gemma 4 31B（稠密 31B，激活参数 = 总参数）在 Arena Text 达到 Elo 1451，与 DeepSeek V4 Pro（1.6T 总参 / 49B 激活，Elo 1456）仅差 5 分。这意味着每个参数的效率远超对手。
- **用推理时计算弥补模型容量。** 引入 thinking mode（推理时生成长链思考痕迹），在不增加模型参数的前提下提升 STEM 推理能力。
- **多模态原生但无编码器。** 12B 模型完全抛弃专用 vision/audio encoder，用轻量投影层直接把 raw patches 映射到 LLM 嵌入空间——最大程度复用 LLM backbone 的计算能力，减少内存碎片和 I/O 瓶颈。
- **量化优先。** 从训练时就做 QAT（量化感知训练），而不是训练后量化（PTQ）。这意味着推理时可以直接跑 int4/int8，而不损失精度。

**放弃了什么：**

- **放弃了大参数带来的规模直觉。** 31B 是前沿稠密模型中最小的之一，必须用更精细的架构设计来弥补。
- **放弃了纯稠密注意力。** 用 5:1 局部滑动窗口:全局注意力的混合模式，降低长序列的计算复杂度。
- **放弃了专用 encoder 的灵活性。** 12B 的 encoder-free 架构把 vision/audio 处理完全交给 LLM，这对对齐能力要求极高。

---

## 关键架构决策

### 1. 混合注意力机制（Local-Global Attention）

**选型：** 每个模块采用 5:1 的局部滑动窗口与全局自注意力比例（2.3B 为 4:1）。全局层复用 key 作为 value（`values = keys`），配合 p-RoPE（p=0.25）和 KV cache sharing。

**原因：** 长上下文场景中，KV cache 是显存瓶颈。方案组合拳减了 **37.5%** 的全局 KV cache 占用：
- keys 复用为 values → 减少一个完整的 value 投影矩阵
- p-RoPE（p=0.25）→ 降低旋转位置编码的维度开销
- KV cache sharing（E2B: 20/35, E4B: 18/42）

RoPE 频率设为全局层 1M / 局部层 10k，分离了长程语义和局部细粒度建模。

### 2. 无编码器（Encoder-Free）统一架构

**选型：** Gemma 4 12B 完全抛弃了独立的 vision encoder（550M）和 audio encoder（305M），用轻量投影模块替代。

- **Vision 处理：** 48×48×3 RGB 图像块 → 单层大矩阵乘法（35M 参数替代 550M encoder）→ 2D 坐标位置嵌入 → LayerNorm → LLM backbone
- **Audio 处理：** 原始 16kHz 音频切割为 40ms 块 → 640 维向量 → 直接投影到 LLM 嵌入空间

**原因：** 减少内存碎片、降低 I/O 延迟、让 LLM backbone 统一建模所有模态。代价是对齐训练难度大——12B 的某些视觉 benchmark 低于同尺寸加 encoder 的模型（如 MMMU Pro 69.1 vs 31B 的 76.9），但在 audio 表现上达到了与专用 encoder 模型（E4B + 305M encoder）相当的水平（FLEURS ASR en: 0.063 vs 0.065）。

### 3. MoE 设计

**选型：** 26B 总参 / 3.8B 激活的 MoE 变体（26B-A4B），其余模型均为稠密架构。

**原因：** Google DeepMind 对 MoE 的使用非常克制——只在 26B 总参规模上有一个 MoE 变体，而非全系列 MoE。这与 DeepSeek（全系列 MoE）形成鲜明对比。这可能反映了 Google 对稠密模型训练稳定性和推理可预测性的偏好。26B-A4B 在 Arena Text 达到 Elo 1438，与 31B 稠密的 1451 差距不大，说明 MoE 以更少激活参数接近了稠密表现。

### 4. 训练策略

**基础设施：**

| 模型 | TPU | #Chips | 数据并行 | 序列并行 | 副本并行 |
|------|-----|--------|---------|---------|---------|
| E2B | v6e | 4,096 | 16 | 8 | 32 |
| E4B | v6e | 6,144 | 16 | 16 | 24 |
| 12B | v5p | 12,288 | 16 | 16 | 48 |
| 26B-A4B* | v6e | 6,144 | 16 | 16 | 24 |
| 31B | v6e | 10,240 | 16 | 16 | 40 |

- 使用 JAX + Pathways 单控制器编程范式 + GSPMD 自动并行化
- ZeRO-3 优化器状态分片
- **Slice-Granularity Elasticity：** TPU 局部故障时自动用更少的芯片继续训练，中断时间从数分钟降到数秒
- Tokenizer：262K 词汇量的 SentencePiece，拆分数位、保留空白、byte-level

**数据：** 大规模、多领域预训练数据（网页、代码、图像、音频），截止日期 2025 年 1 月。严格去污染——移除 benchmark 污染数据、隐私信息、不安全内容。

### 5. 推理优化

**MTP（Multi-Token Prediction）投机解码草稿头：**
- 4 层 Transformer 模块（3 局部 + 1 全局注意力），交叉注意力到主模型 KV cache
- 维度：E2B/E4B 256，26B-A4B/31B 1024
- **无需 MTP prefill，支持任意草稿长度**
- E2B/E4B 的 drafter 用 top-k 聚类降低投影矩阵从 d×262K 到 d×4K，保持相近接受率

**QAT（量化感知训练）：**
- 移动端量化：per-channel int2/int4 权重 + int8 激活
- Q4_0：blockwise 量化
- 每 block 增加标量 scale 保证 fp16 推理稳定性
- 150M vision encoder：W8A8 减少 2× 内存占用，44% 延迟降低
- Audio encoder：W{2,4,8}A8，磁盘占用从 390MB（Gemma 3n）降到 87MB，减少 **78%**

### 6. Post-Training

- 类似 Gemma 3 的指令微调流水线
- 新增 thinking mode 支持：通过系统 prompt 中的 `<|think|>` token 触发推理痕迹
- 数据筛选：去重、去隐私、不安全输出过滤
- 添加鼓励上下文归因（in-context attribution）和保守拒绝的数据子集，提高幻觉指标
- 控制 token：`<|turn|>` 格式，`<|channel|>thought<|channel|>` 包裹推理内容

---

## 关键结果

### Arena Text 排名（截至 2026-06-19）

| 模型 | Elo | 类型 | 参数量 |
|------|-----|------|--------|
| Gemma 4 31B | **1451** | 稠密 | 31B |
| Gemma 4 26B-A4B | **1438** | MoE | 26B / 4B 激活 |
| DeepSeek V4 Pro | 1456 | MoE | 1.6T / 49B |
| GLM 5 | 1457 | MoE | 744B / 40B |
| Kimi K2.6 | 1460 | MoE | 1T / 32B |

**解读：** 31B 稠密是 Arena 排名最高的稠密开放模型，Elo 1451 vs 1.6T 的 DeepSeek V4 Pro Elo 1456——参数少 50 倍，分数仅差 5 分。

### 关键 Benchmark 对比

| Benchmark | 31B | 26B-A4B | 12B | E4B | E2B | Gemma 3 27B |
|-----------|-----|---------|-----|-----|-----|-------------|
| MMLU Pro | 85.2 | 82.6 | 77.2 | 69.4 | 60.0 | 67.6 |
| AIME 2026 (no tools) | 89.2 | 88.3 | 77.5 | 42.5 | 37.5 | 20.8 |
| LiveCodeBench v6 | 80.0 | 77.1 | 72.0 | 52.0 | 44.0 | 29.1 |
| GPQA Diamond | 84.3 | 82.3 | 78.8 | 58.6 | 43.4 | 42.4 |
| Codeforces Elo | 2150 | 1718 | 1659 | 940 | 633 | 110 |
| HLE | 19.5 | 8.7 | 5.2 | — | — | — |
| IFEval | 98.9 | 98.5 | 97.2 | 96.7 | 94.6 | 90.4 |
| MMMLU (多模态) | 88.4 | 86.3 | 83.4 | 76.6 | 67.4 | 70.7 |
| RULER 128k | 96.4 | 89.8 | 91.2 | 86.6 | 70.4 | 66.0 |

**密度化信号：** E2B（2.3B）在 AIME 2026（37.5）和 LiveCodeBench（44.0）上已经接近甚至超过 Gemma 3 27B（20.8/29.1），参数减少 10 倍。

### 视觉 Benchmark（thinking mode, 最高分辨率）

| Benchmark | 31B | 26B-A4B | 12B | E4B | E2B | Gemma 3 27B |
|-----------|-----|---------|-----|-----|-----|-------------|
| MMMU Pro | 76.9 | 73.8 | 69.1 | 52.6 | 44.2 | 49.7 |
| MATH-Vision | 85.6 | 82.4 | 79.7 | 59.5 | 52.4 | 46.0 |
| InfographicVQA | 92.0 | 89.3 | 88.4 | 70.0 | 63.9 | 70.6 |

### 音频 Benchmark

- 与 Gemma 3n 相比，E2B 翻译提升 12%，转录提升 17%；E4B 翻译提升 10%，转录提升 12%
- 尽管 audio encoder 磁盘占用减少了 78%（390MB → 87MB），性能反而提升
- 12B encoder-free 架构在音频 benchmark（FLEURS ASR 平均 WER 0.063）上持平 E4B（0.065）

---

## 范式对比

### vs Meta Llama 系列

| 维度 | Gemma 4 | Llama 4 |
|------|---------|---------|
| 规模策略 | 小参数量 + 架构创新 | 大参数量 + MoE |
| 多模态 | 原生多模态 + encoder-free | 外挂 vision encoder |
| 推理支持 | thinking mode 原生支持 | 需外部 CoT 框架 |
| 量化 | QAT 从训练开始 | PTQ |
| 许可证 | Apache-2.0 | 自定义（商用限制） |

**关键差异：** Gemma 4 走了「密度优先」，Llama 走「规模优先」。31B 对撞 400B+ 的场景下，Gemma 证明了架构创新可以大幅缩小差距。

### vs DeepSeek V4

| 维度 | Gemma 4 | DeepSeek V4 |
|------|---------|-------------|
| 架构偏好 | 稠密为主，MoE 仅一个变体 | 全线 MoE |
| 参数规模 | 2.3B–31B | 13B–1.6T |
| KV cache 优化 | keys 复用为 values + p-RoPE + sharing | MLA（Multi-head Latent Attention） |
| 推理优化 | MTP 投机解码 | MTP + DPU 加速 |
| 上下文长度 | ~256K 验证 | ~1M |
| 开源策略 | Apache-2.0 全开源 | 部分开源 |

**关键差异：** DeepSeek 在 MoE 和超长上下文上走得更远，但 Gemma 4 证明了稠密路线在 2026 年仍然能打。两者的 KV cache 优化思路不同——DeepSeek 用 MLA 从根本上压缩 KV cache，Gemma 用工程组合拳（keys=values + p-RoPE + sharing）。

### vs Qwen 系列

| 维度 | Gemma 4 | Qwen 3.5 |
|------|---------|----------|
| 规模 | 31B 最大 | 397B-A17B MoE |
| 多模态 | encoder-free 12B, encoder 其他 | 同尺寸变体均有 encoder |
| 端侧 | 2.3B / 4.5B 有专用 per-layer embed | 专门的端侧变体 |
| Arena | 31B 1451 | 397B-A17B 1444 |

**关键差异：** Gemma 4 31B 在略小参数下 Arena 排名超过 Qwen 3.5 397B-A17B（1451 vs 1444），再次验证密度化路线的有效性。

---

## 可复用的工程经验

1. **Keys 复用为 values 是低成本的 KV cache 优化。** 不需要改模型架构，只在全局注意力层设置 `values = keys` 即可省掉一个完整投影矩阵的计算和存储。结合 p-RoPE 可再减维度开销。

2. **MTP drafter 用交叉注意力利用主模型 KV cache 是关键设计。** 传统投机解码需要单独为 drafter 做 prefill，但 Gemma 4 的设计让 drafter 直接 cross-attend 主模型的 KV cache，省掉了 prefill 步骤、支持任意草稿长度。

3. **QAT 远比 PTQ 值得做。** 训练时量化让模型学到「容忍量化噪声」的表征，比训练后用任何校准数据做 PTQ 的效果都好。Gemma 4 的音频 encoder 在 78% 磁盘压缩率下性能反而提升，说明 QAT 甚至可以通过正则化效果提升泛化。

4. **思考模式（Thinking Mode）对小模型的提升比例大于大模型。** E2B（2.3B）在 AIME 2026 上从 Gemma 3 27B 的 20.8 跳到 37.5，提升 80%，而 31B 从 20.8 跳到 89.2。但 12B（77.5）vs 26B-A4B（88.3）的差距远小于参数比例预期。这意味着推理时 CoT 可以部分弥补模型容量的不足——对算力有限但需要强推理的场景是重大利好。

5. **Encoder-free 架构的 ROI 随模型增大而增加。** 12B 的 encoder-free 设计在 audio 上持平带 encoder 的方案，在 vision 上略逊但差距可控。更大的模型可能有更充裕的 backbone 容量来建模 raw patches，随着模型增大 encoder-free 的优势（减少内存碎片、简化部署）会越来越显著。

6. **per-layer embeddings 是小模型的有效参数杠杆。** E2B 和 E4B 使用 per-layer embedder（每层独立的嵌入投影），使 2.3B 有效参数在总参 5B 内实现远高于纯参数密度的表现。这相当于在每个 transformer 层都做了一次「再思考」输入表示。

7. **多模态训练可以联合提升文本能力。** 对比 Gemma 3 27B（文本训练）和 Gemma 4 E4B（多模态训练，4.5B 有效参数），E4B 在纯文本 benchmark（MMLU Pro 69.4 vs 67.6, GPQA 58.6 vs 42.4）上全面超越。多模态数据本身可能是更好的训练信号。
