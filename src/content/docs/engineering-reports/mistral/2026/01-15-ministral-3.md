---
title: Ministral 3 — 级联蒸馏高效小模型：用 1/10 的训练数据匹敌旗舰
date: 2026-01-15
source: https://arxiv.org/abs/2601.08584
---

# Ministral 3 — 级联蒸馏高效小模型

**发布日期：** 2026-01-15
**来源：** https://arxiv.org/abs/2601.08584
**工程范式：** 级联蒸馏（Cascade Distillation）——从大教师模型迭代剪枝+蒸馏，用 1-3T token 训练出匹敌 15-36T token 从头训练模型的性能

## 设计哲学

Mistral 的核心约束：如何在资源和成本受限的 edge/端侧场景下，用最少的训练数据和算力产出有竞争力的模型。

核心选择：**不从头训练小模型**，而是从一个强教师模型（Mistral Small 3.1, 24B）出发，通过迭代剪枝→蒸馏→再剪枝的 Cascade Distillation，逐级缩小到 14B→8B→3B。

放弃了什么：
- 放弃了"同参数量下最高绝对性能"的追求——Ministral 3 的性能目标是"在 1-3T token 训练预算下匹敌 15T+ token 的模型"，而非在所有 benchmark 上第一
- 放弃了在 3B 模型上投入额外的 embedding 参数（3B 使用 tied input-output embeddings）
- 放弃了纯从头训练的架构自由度——架构从教师模型继承，裁剪而非设计

## 关键架构决策

- **注意力机制**：Grouped Query Attention（GQA），32 query heads / 8 key-value heads，RoPE 位置编码
- **激活函数**：SwiGLU
- **归一化**：RMSNorm
- **长上下文扩展**：YaRN + position-based softmax temperature scaling（Nakanishi 2025 / Meta 2025），目标 256K
- **视觉编码器**：410M ViT（来自 Mistral Small 3.1 Base，冻结），训练新的 projection layer
- **词汇表**：131K tokens
- **参数量**：
  - 14B：40层，d=5120，FFN dim=16384
  - 8B：34层，d=4096，FFN dim=14336
  - 3B：26层，d=3072，FFN dim=9216，tied embeddings

### Cascade Distillation 流程

1. **剪枝**：从教师模型按三个维度裁剪（层剪枝→隐藏维度 PCA 投影→FFN 维度重要性排序）
   - 层重要性：输出 norm / 输入 norm 比值（比传统的 perplexity-based 方法更简单有效）
   - 隐藏维度：PCA 对所有层的 attn_norm + ffn_norm 输入做降维
   - FFN 维度：SiLU(W1*x) * W3*x 的激活值绝对值均值
2. **蒸馏**：用 forward KL divergence 对学生模型做 logit-level 蒸馏，蒸馏目标只含 KL loss（不混合 next-token prediction）
3. **重复**：继续对 14B 剪枝得到 8B，对 8B 剪枝得到 3B
4. **数据效率**：单次通过整个数据 mix，不重复使用数据

### Post-Training

**Instruction 版本**：
1. SFT（fp8 quantization + logit distillation，教师为 Mistral Medium 3）
2. Online DPO（ODPO）：在线采样两个候选 + Pairwise Reward Model 评分 + 改进版 DPO loss（binomial 概率加权 + β-rescaling）

**Reasoning 版本**（从预训练 checkpoint 而非 ODPO 版本出发）：
1. SFT w/ CoT（长/短推理轨迹混合）
2. GRPO（两阶段：STEM RL → General RL，max gen len 从 32K 提升到 80K）
3. ODPO（后 RL 对齐，stripped thinking chunks before reward scoring）

### 关键蒸馏发现

1. **更强的教师≠更好的学生**：预训练阶段，从 Mistral Small 3.1（24B）蒸馏优于从 Medium 3（更强但更大）蒸馏
2. **post-trained 教师优于 base 教师**：从 instruct/reasoning 版本教师蒸馏在预训练阶段产生更强学生（尤其是 math/code 能力）
3. **preference-tuned 教师优于 SFT-only 教师**：偏好优化过的 checkpoint 作为 SFT 蒸馏教师始终更强

## 关键结果

### Pre-train Base 模型对比

| 模型 | MMLU | MMLU-Redux | MATH(CoT) | TriviaQA |
|------|------|------------|-----------|----------|
| Ministral 3 14B | 79.4 | 82.0 | **67.6** | **74.9** |
| Qwen 3 14B | 83.7 | - | 62.0 | 70.3 |
| Gemma 3 12B | 76.6 | - | 48.7 | 78.8 |
| Ministral 3 8B | 76.1 | 79.3 | **62.6** | **68.1** |
| Ministral 3 3B | 70.7 | 73.5 | **60.1** | 59.2 |

### Instruct 模型对比

| 模型 | Arena Hard | WildBench | MATH(maj@1) |
|------|-----------|-----------|-------------|
| Ministral 3 14B | **55.1** | **68.5** | 90.40 |
| Qwen3 14B | 42.7 | 65.1 | 87.00 |
| Ministral 3 8B | 50.9 | 66.8 | 87.60 |
| Ministral 3 3B | 30.5 | 56.8 | 83.00 |

### Reasoning 模型对比

| 模型 | AIME 2025 | GPQA Diamond | LiveCodeBench v6 |
|------|-----------|--------------|-----------------|
| Ministral 3 14B | **85.0** | **71.2** | **64.6** |
| Qwen3 14B | 73.7 | 66.3 | 59.3 |
| Ministral 3 8B | 78.7 | 66.8 | 61.6 |
| Ministral 3 3B | 72.1 | 53.4 | 54.8 |

**核心亮点**：Ministral 3 14B Reasoning 在 AIME 2025 上达到 **85.0%**，远超同级 Qwen3 14B 的 73.7%，且训练数据量仅为其约 1/12（~1T vs ~36T tokens）。

## 范式对比

| 维度 | Mistral (Ministral 3) | Qwen 3 | Gemma 3 |
|------|----------------------|--------|---------|
| 训练方式 | Cascade Distillation（剪枝+蒸馏） | 从头训练 | 蒸馏（从 Gemini） |
| 训练数据量 | 1-3T tokens | 36T tokens | - |
| 架构继承 | 从教师继承 | 自主设计 | 从 Gemini 继承 |
| 许可 | Apache 2.0 | Apache 2.0 | Gemma license |
| 定位 | edge/端侧优先 | 通用全尺寸 | 轻量开放 |

## 社区评价

Ministral 3 的关键贡献在于验证了"大模型通过级联剪枝+蒸馏可以高效训练小模型"这一假设，为资源受限场景提供了架构无关的通用方法论。三个反直觉的蒸馏发现（教师不是越大越好、post-trained > base、preference-tuned > SFT）对行业有一定参考价值。

（原文发布于 HN 但讨论热度中等。）

## 可复用的工程经验

1. **Cascade Distillation 可替代从头训练**：用 1/10-1/30 的 token 量产出同级别模型，推理成本显著降低
2. **层重要性评估用激活 norm 比值**：output_norm/input_norm 均值作为剪枝信号，比 perplexity-based 方法计算量低且效果相当
3. **在线 DPO 优于离线 DPO**：在线采样 + 动态评分能处理 infinite generation 等 model-induced artifacts
4. **GRPO 的两阶段设计**：先专注 STEM 推理提升，再泛化到 general chat，可避免推理增强破坏对话质量
5. **3B 模型的特殊处理**：低参数量下需要蒸馏辅助（防止 verbosity/repetition），且 ODPO 在 3B 上增益有限——资源最低的模型可能需要最小化 post-training pipeline
