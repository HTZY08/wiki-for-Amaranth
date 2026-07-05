---
title: Ministral 3 — 级联蒸馏：用 1/10 的 token 训练出竞争级小模型
date: 2026-07-05
source: https://arxiv.org/abs/2601.08584
---

# Ministral 3 — 级联蒸馏：用 1/10 的 token 训练出竞争级小模型

**发布日期：** 2026 年 1 月（arXiv 2601.08584）
**来源：** https://arxiv.org/abs/2601.08584
**工程范式：** Cascade Distillation — 剪枝→蒸馏→再剪枝的迭代高效训练

## 设计哲学

核心约束：**用最少的数据和计算成本训练出竞争级小模型。**

Ministral 3 系列的根本出发点是：当已有强 teacher 模型（Mistral Small 3.1 24B）时，能否不从头训练，而是通过**剪枝 + 蒸馏**的迭代过程，以极低的 token 预算产出参数高效的小模型？这有别于 Qwen 3 / Llama 3 的"从零训"范式——后者需要 15-36T token 来训练 3B-14B 模型，而 Ministral 3 仅用 1-3T token 就达到竞争级表现。

核心 trade-off：接受模型容量上限受限于 teacher（而非数据），换取训练成本降低一个数量级。

## 关键架构决策

### 模型家族：3 种尺寸 × 3 种变体 = 9 个模型

| 尺寸 | 层数 | 隐藏维度 | Q/KV 头数 | FFN 维度 | 绑定嵌入 | 上下文长度 |
|------|------|---------|-----------|---------|---------|-----------|
| 14B  | 40   | 5120    | 32 / 8    | 16384   | ✗       | 256K      |
| 8B   | 34   | 4096    | 32 / 8    | 14336   | ✗       | 256K      |
| 3B   | 26   | 3072    | 32 / 8    | 9216    | ✓       | 256K      |

每个尺寸提供 3 种变体：
- **Base**：预训练基座
- **Instruct**：SFT + ODPO 微调（通用对话）
- **Reasoning**：SFT w/ CoT → GRPO → ODPO（复杂推理）

所有模型共享：GQA（32 query / 8 KV heads）、RoPE 位置编码、SwiGLU 激活、RMSNorm、131K 词表。

视觉能力：所有模型集成一个**冻结的 410M ViT 视觉编码器**（来自 Mistral Small 3.1 / Pixtral），仅训练新的投影层。

### Cascade Distillation 流程

这是本文最核心的工程贡献。算法伪代码：

```
1. 从 teacher (Mistral Small 3.1 24B) 开始
2. 剪枝 24B → 14B init（层剪枝 + 隐藏维度剪枝 + FFN 剪枝）
3. 蒸馏：短上下文 (16K) 训练，logit 蒸馏 from teacher
4. 长上下文扩展：YaRN + position-based softmax temperature → 256K
5. 得到 Ministral 3 14B Base
6. 从 14B Short Ctx. 再次剪枝 → 8B init
7. 重复蒸馏 → 得到 Ministral 3 8B Base
8. 从 8B Short Ctx. 再次剪枝 → 3B init
9. 重复蒸馏 → 得到 Ministral 3 3B Base
```

**关键特性：** 整个流程在一次数据扫描中完成，**避免数据重复**（每个 token 只被看到一次）。

### 剪枝方法（三管齐下）

1. **层剪枝（Layer Pruning）**：基于 `output_norm / input_norm` 比率作为层重要性代理分数，保留 top-k 层。比 Minitron 的 counterfactual perplexity 方法更简单。
2. **隐藏维度剪枝（Hidden Dimension Pruning）**：拼接所有层的 attention norm 和 FFN norm 激活值，执行 PCA 得到统一旋转矩阵，投影到更低维空间。
3. **FFN 剪枝（Feedforward Pruning）**：对于 SwiGLU 结构，计算 `|SiLU(W1·x) * W3·x|` 的逐维度均值作为重要性分数，保留 top-k 维度。

### 训练效率

- **训练 token 总量：仅 1-3T token**（3B 最少，14B 最多）
- 对比：Qwen 3 系列训练了 **36T token**，Llama 3 系列训练了 **15T token**
- 效率提升：~10× token 节约

### 后训练策略

**Instruct 变体：**
1. SFT（fp8 量化，logit 蒸馏 from Mistral Medium 3 — 注意此处 teacher 变强了）
2. Online DPO（ODPO），使用 Pairwise Reward Model (PWRM) 动态评分
   - ODPO 改进：基于 PWRM 概率的软标签替代 hard winner/loser
   - β-rescaling 技术增强训练稳定性
   - 自动检测无限生成循环并标记为 "loser"

**Reasoning 变体：**
1. SFT w/ CoT（含数学、代码、通用对话、工具使用、视觉推理等多领域推理轨迹）
2. GRPO：分两阶段
   - STEM RL：数学、代码、视觉推理（严格多步清洗过滤）
   - General RL：通用指令遵循（LLM-as-Judge + rubric 评分）
3. ODPO（后 RL 对齐，去除思考前缀后再评分）

推理模型将最大生成长度从 32K 增加到 80K 以容纳完整推理链。

### 开源协议

Apache 2.0 — 全部 9 个模型均开源。

## 关键结果

### Base 模型预训练对比（与 Qwen 3 / Gemma 3）

| 模型 | MMLU (5-shot) | MMLU-Redux (5-shot) | TriviaQA (5-shot) | MATH (CoT 2-shot) | AGIEval (5-shot) |
|------|:---:|:---:|:---:|:---:|:---:|
| Qwen 3 14B | 83.7 | 70.3 | 62.0 | 66.1 | 75.4 |
| **Ministral 3 14B** | **82.0** | **74.9** | **67.6** | **64.8** | **74.2** |
| Gemma 3 12B | 76.6 | 78.8 | 48.7 | 58.7 | 69.0 |
| Qwen 3 8B | 79.4 | 63.9 | 57.6 | 59.6 | 70.0 |
| **Ministral 3 8B** | **79.3** | **68.1** | **62.6** | **59.1** | **70.6** |
| Qwen 3 4B | 75.9 | 53.0 | 40.5 | 57.0 | 67.7 |
| **Ministral 3 3B** | **73.5** | **59.2** | **60.1** | **51.1** | **65.2** |

Ministral 3 14B Base 在 TriviaQA (+5.6) 和 MATH (+1.6) 上超过 Qwen 3 14B。**Ministral 3 8B Base 在多数指标上超过更大的 Gemma 12B。**

### Base 模型与 teacher (Mistral Small 3.1 24B) 对比

| 评估项 | MS3.1 24B | M3 14B | M3 8B | M3 3B |
|--------|:---:|:---:|:---:|:---:|
| MMLU (5-shot) | 81.0 | 79.4 | 76.1 | 70.7 |
| MMLU-Redux (5-shot) | 82.7 | 82.0 | 79.3 | 73.5 |
| ARC-Challenge | 91.6 | 89.9 | 88.0 | 85.5 |
| TriviaQA (5-shot) | 79.3 | 74.9 | 68.1 | 59.2 |
| MATH (CoT 2-shot) | 55.8 | **67.6** | **62.6** | **60.1** |
| GPQA Diamond (0-shot) | 36.9 | **39.9** | **39.9** | 33.8 |
| MBPP (3-shot) | 71.6 | 71.6 | 70.0 | 63.0 |
| MMMU (2-shot) | 59.1 | **59.9** | 55.1 | 52.4 |

注意剪枝后的模型在 MATH 和 GPQA Diamond 上**超过 teacher**——这可能是训练数据混合差异或蒸馏过程带来的正则化效应。

### Instruct 模型对比

| 模型 | Arena Hard | WildBench | MATH (maj@1) | MM MTBench |
|------|:---:|:---:|:---:|:---:|
| Qwen3 14B (Non-Thinking) | 42.7 | 65.1 | 87.00 | N/A |
| **Ministral 3 14B Instruct** | **55.1** | **68.5** | **90.40** | **84.90** |
| Gemma3-12B-Instruct | 43.6 | 63.2 | 85.40 | 67.00 |
| Qwen3-VL-8B-Instruct | 52.8 | 66.3 | 94.60 | 80.00 |
| **Ministral 3 8B Instruct** | **50.9** | **66.8** | **87.60** | **80.80** |
| Qwen3-VL-4B-Instruct | 43.8 | 56.8 | 90.00 | 80.08 |
| **Ministral 3 3B Instruct** | **30.5** | **56.8** | **83.00** | **78.30** |
| Qwen3-VL-2B-Instruct | 16.3 | 42.2 | 78.60 | 63.60 |

**Ministral 3 14B Instruct 在 Arena Hard 上以 55.1 大幅领先 Qwen 14B (42.7) 和 Gemma 12B (43.6)**，但注意这里的 Qwen 可能是非视觉版本。

### Reasoning 模型对比

| Benchmark | Qwen3 14B | **M3 14B Reasoning** | Qwen3 8B | **M3 8B Reasoning** | Qwen3 4B | **M3 3B Reasoning** |
|-----------|:---:|:---:|:---:|:---:|:---:|:---:|
| AIME 2024 | 83.7 | **89.8** | 86.0 | **86.0** | 72.9 | **77.5** |
| AIME 2025 | 73.7 | **85.0** | 79.8 | 78.7 | 69.7 | **72.1** |
| HMMT 2025 | 55.8 | **67.5** | 57.5 | 55.8 | 50.8 | **51.7** |
| GPQA Diamond | 66.3 | **71.2** | 67.1 | 66.8 | 60.1 | 53.4 |
| PhyBench | 22.0 | **26.0** | 22.0 | 20.0 | 9.0 | **15.0** |
| LiveCodeBench v6 | 59.3 | **64.6** | 58.0 | **61.6** | 51.3 | **54.8** |

**Ministral 3 14B Reasoning 在所有 benchmark 上全面超越 Qwen 3 14B Reasoning**，尤其在 AIME 2025 上领先 11.3 分（85.0 vs 73.7），HMMT 2025 上领先 11.7 分（67.5 vs 55.8）。

Ministral 3 3B Reasoning 在所有指标上也超过 Qwen 3 4B（更大尺寸），体现了蒸馏范式在极小模型上的超强参数效率。

## 范式对比

| 维度 | Cascade Distillation (Ministral 3) | 从零训练 (Qwen 3 / Llama 3) |
|------|:---:|:---:|
| 训练 token 量 | 1-3T | 15-36T |
| 计算成本 | ~10× 更低 | 基准 |
| 是否需要从头设计架构 | 不需要（继承 teacher） | 需要 |
| 模型上限 | 受限于 teacher 容量 | 理论上无上限 |
| 小模型 (3B) 质量 | 极好（受益于 teacher 知识） | 受限于数据质量和训练技术 |
| 多尺寸一致性 | 高（继承相同 teacher） | 需要独立维护不同尺寸 |
| 新尺寸扩展 | 容易（再剪枝一次即可） | 需重新训练 |
| 数据需求 | 低 | 非常高 |

### 关键发现：Teacher 选择的三条反直觉规律

1. **"Capacity Gap"（容量鸿沟）**：更强的 teacher **不一定**产出更强的 student。预训练阶段，Mistral Small 3.1 (24B) 作为 teacher 比更强的 Mistral Medium 3 更好。但在后训练阶段，更强的 teacher 继续有益。
2. **后训练 teacher > 预训练 teacher**：用 post-trained（instruct/reasoning）teacher 蒸馏 student 预训练，得到更强的模型——尤其在数学和代码能力上有显著提升，知识类任务影响小。
3. **Preference-optimized teacher > SFT-only teacher**：从经过偏好优化的 checkpoint 蒸馏，始终优于仅 SFT 的 teacher，且这些增益在 student 经过自己的偏好优化后仍然保持。

### 序列长度与短期上下文训练

预训练分为两个阶段：
- **阶段 1**：短上下文（16K token）— 主要训练
- **阶段 2**：长上下文扩展（16K → 256K）— 使用 YaRN + position-based softmax temperature scaling

### 与 Qwen 3 的关键差异

Ministral 3 Instruct 不在 SFT 阶段混入长 CoT 数据，这与 Qwen 3 的做法不同。当尝试加入长 CoT 数据时，模型出现过度反思、内部独白和回溯行为，损害通用对话体验。因此 Ministral 3 选择了更清晰的**能力分离**：通用对话用 Instruct，复杂推理用 Reasoning。

## 可复用的工程经验

1. **剪枝 + 蒸馏是训练小模型的"快速通道"**：如果已有强大的 teacher 模型，通过 Cascade Distillation 可以用 1/10 的 token 预算获得竞争级小模型。这特别适合资源受限环境或需要一个模型家族的场景。

2. **Teacher 选择需要分层考虑**：
   - 预训练阶段：用中等强度 teacher（避免 capacity gap）
   - 后训练阶段：用最强 teacher（不受 capacity gap 影响）
   - 始终优先使用 post-trained / preference-optimized teacher

3. **激活范数比是简单的层重要性代理**：`output_norm / input_norm` 比率是比 counterfactual perplexity 更轻量且有效的剪枝指标，值得在类似工作中优先尝试。

4. **ODPO 的工程改进**：
   - 用 PWRM 的连续概率替代 hard 标签，提供更细粒度的优化信号
   - β-rescaling 提升对不同 β 值的鲁棒性
   - 自动检测无限生成循环并作为负样本

5. **推理模型的后训练三阶段法**：SFT w/ CoT → GRPO（STEM → General）→ ODPO，形成一条可复用的推理能力构建流水线。

6. **长上下文扩展的两阶段法**：先训练 short context（16K），再用 YaRN + position-based temperature scaling 扩展到 256K。这种方法比直接训练长上下文更高效。

7. **能力分离，避免 Instruct 和 Reasoning 混淆**：不要在通用对话模型的 SFT 中混入过多长 CoT 数据，否则会破坏对话自然度。应该分别训练两个变体。

8. **3B 模型需要特殊处理**：极小模型容易陷入重复/无限生成，需要蒸馏正则化（如从中等 teacher 做 logit distillation）来稳定训练。
