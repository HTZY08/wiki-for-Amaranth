---
title: MiniMax Sparse Attention — 极简高效的块级稀疏注意力
date: 2026-07-05
source: https://arxiv.org/abs/2606.13392
---

# MiniMax Sparse Attention — 极简高效的块级稀疏注意力

**发布日期：** 2026年6月（arXiv 2606.13392）
**来源：** https://arxiv.org/abs/2606.13392
**工程范式：** Occam's Razor — 保留最简必要组件的块级稀疏注意力

## 设计哲学

MSA 的核心约束是将二次复杂度注意力降为可线性扩展的稀疏注意力。遵循 Occam's Razor 原则，经过大量消融实验后，只保留最简必要组件：

- **在 GQA 上叠加稀疏性**，而非另起炉灶设计新的注意力架构。最大限度地复用已有的软件和硬件基础设施。
- **只做选择器（Selector），不做计算器**。Index Branch 仅负责选出重要块（Top-k），不参与值向量的聚合计算。推理时完全不经过指数运算。
- **尽可能删减**：经过消融证实可移除的组件一律移除——Index Value Head（消融表明 warmup 后不再需要）、Learnable Attention Sink（无稳定收益）、Forced Sink & Local Window（模型可自行习得）。
- **块级（Block-level）粒度**，而非 token 级粒度。这使 KV 读取保持连续，GPU tensor-core 利用率更高。

## 关键架构决策

### 1. 双层架构：Index Branch + Main Branch

在标准 GQA 层之上附加两个分支：

- **Index Branch（轻量级索引分支）**：每个 GQA group 引入一个 index query head（`W_q_idx`），所有 group 共享一个 index key head（`W_k_idx`）。输入 hidden states 经 `stop_gradient` 后送入 Index Branch，确保梯度不回流到 backbone。
  - 对每个因果可见的 key token 计算点积分数 `S = Q_idx · K_idx^T / sqrt(d_idx)`
  - 块级 max-pooling：对每个块 `B_b` 取其 token 得分最大值作为块得分 `M`
  - 每个 GQA group 独立选择 Top-k 个块 → 每个 group 有自己的选择集 `I_i^{(r)}`
  - **始终保留 local block**（包含 query 位置自身的块），无需硬编码 sink 或大局部窗口

- **Main Branch（主分支）**：在 Index Branch 选出的块集合上执行标准 exact softmax attention。每个 query token 只关注最多 `k * B_k` 个 token（固定预算 2048 个 token），与序列长度无关。

### 2. Blockwise Top-k Selection per GQA Group

- **块大小** `B_k = 128`，**选块数** `k = 16`，固定预算 2048 tokens/query
- 每个 GQA group 独立选择自己的 top-k 块，而非所有 query head 共享同一个选择。这保留了 multi-group 的选择多样性——可视化显示不同 group 会选择不同的长程 stripe
- 块级选择使 KV 读取连续，kernel 友好

### 3. Exp-free TopK Kernel

- 由于 softmax 保序，Top-k 直接对原始得分排序，跳过 max/exp/sum 步骤
- 针对 `B_k=128, k=16` 的小 k 场景定制：每个 warp 的 32 条 lane 各处理输入行的 1/32，维护 k 元素 min-heap，最终通过 k 轮 shuffle merge 合并 32 个局部 TopK
- 相比 `torch.topk` 加速 **5.1×**，相比 TileLang radix-select 加速 **3.7×**（128K seq, k=16）

### 4. KV-outer 迭代顺序

- Q-outer 迭代的算术强度 = `G`（GQA ratio），而 KV-outer 迭代的算术强度 = `2/3 * B_k`
- 由于 `2/3 * 128 ≈ 85 >> G = 16`，选择 KV-outer 迭代 + Query Gather
- 对外层循环遍历 `(KV_block, KV_head)` tile，通过反向稀疏索引找到选择该块的所有 query 位置，将 query 加载到 shared memory 通过 TMA copy 批量处理
- Query concatenation：将 `ceil(128/G)` 个查询拼接到一起，填满 `128×128` 的 score MMA

### 5. Pre-scheduled Tile Chunking + Two-phase Combine

- Sink 块（首个块）被几乎所有 query 选中，直接映射为单 CTA 会导致负载极不均匀
- GPU 调度 kernel 将每个 KV tile 沿 query 维度切分为最多 `~2kB_k` 个 query 的 chunk，热门 tile 分给多个 CTA
- 每个 `(query, chunk)` 对预分配 `O_buf` 中的槽位（32-bit handle 打包），无需原子操作
- 两阶段 forward：第一 kernel 写本地归一化的 partial 输出和 logsumexp；第二 kernel 读取所有 partial，计算全局 softmax 归一化并加权合并
- 使用 Programmatic Dependent Launch 隐藏 inter-kernel 启动延迟

### 6. KL Alignment Loss

- Top-k 不可导 → 使用 KL 散度作为 indexer 的训练信号
- Index Branch 分布 `P_idx` 匹配 Main Branch attention 分布 `P`（在选中块的 token 集合上）
- Teacher `P` 通过 GQA group 内所有 query head 的 attention 概率平均得到
- 关键保护措施：**Gradient Detach** — `Q_idx = stop_grad(X) * W_q_idx`，KL loss 的梯度仅更新 `W_q_idx` 和 `W_k_idx`，不进入 backbone，避免 self-distillation 导致 backbone 退化

### 7. Indexer Warmup

- 训练前期 Main Branch attention 熵快速下降 → 若直接从稀疏开始，早期随机选择会路由到无关 token
- 两阶段调度：前若干步使用 full attention（两分支都做），只通过 KL loss 训练 indexer；warmup 后切换到稀疏模式
- 从 dense checkpoint 转换时同样适用：先 40B token warmup，再 400B token sparse CPT

### 8. 始终保留 Local Block

- 每个 query 位置的 local block 始终被选中，不占 top-k 名额
- 防止退化选择（跳过 immediate neighbor），提供稳定的短程建模能力
- 消融表明 forced sink 和 fixed local window 都可以去掉——模型可自行习得 sink 和局部选择模式

## 关键结果

### 质量（109B MoE, 3T tokens 训练）

| 维度 | Full Attention | MSA-PT | MSA-CPT |
|------|:---:|:---:|:---:|
| MMLU | 67.0 | **67.2** | 66.8 |
| GSM8K | 76.2 | **77.7** | 73.7 |
| MMMU | **46.8** | 45.9 | 44.5 |
| RULER-8K | 79.8 | **84.2** | 77.2 |
| RULER-32K | 75.0 | **77.5** | 75.7 |

- MSA-PT（从头稀疏训练）在多数 benchmark 上匹配或略超 dense baseline
- MSA-CPT（从 dense checkpoint 转换）保持与原 checkpoint 接近的能力
- 长上下文扩展（+140B tokens）后 HELMET-128K 差 0.6 分，RULER-128K 反超 0.12 分

### 效率（H800 GPU, 1M context）

| 指标 | 提升倍数 |
|------|:--------:|
| 每 token 注意力计算量减少 | **28.4×** |
| Prefill wall-clock 加速 | **14.2×** |
| Decoding wall-clock 加速 | **7.6×** |

- 理论 FLOPs 减少大于实测加速比，原因是稀疏引入的索引构造、TopK 选择、反向索引物化、query gathering、负载均衡等开销

## 范式对比：MSA vs. DeepSeek Sparse Attention (DSA)

| 维度 | MSA | DSA |
|------|-----|-----|
| **基础架构** | GQA（Grouped Query Attention） | MLA（Multi-head Latent Attention, MQA mode） |
| **选择粒度** | 块级（block-level, 128 tokens/block） | Token 级 |
| **选择共享方式** | 每个 GQA group 独立选择 | 所有 query head 共享同一个 Top-k 索引 |
| **索引器** | 单 head 点积 + max-pooling（无非线性） | 多 head ReLU-based lightning indexer |
| **索引器训练** | KL alignment loss（匹配 Main Branch 分布） | 推测通过 LM loss 反向传播（论文未明确） |
| **Index Value Head** | 训练初期有，warmup 后丢弃 | 不适用（索引器独立于注意力输出） |
| **GPU 内核特色** | KV-outer order, exp-free TopK, pre-scheduled chunking, two-phase combine | 未公开 kernel 细节 |
| **始终保留** | Local block（仅每个 query 的自身块） | 未明确提及 |
| **Warmup** | 两阶段：full attention warmup → sparse | 未明确提及 |
| **从 dense 转换** | 支持（CPT 路线，40B warmup + 400B sparse） | 部分支持（DeepSeek-V4 使用 CSA 替代 DSA） |
| **Kernel 开源** | ✅ github.com/MiniMax-AI/MSA | ❌ 未公开 |
| **生产模型** | ✅ MiniMax-M3 (HuggingFace) | ✅ DeepSeek-V4 |

**核心差异总结**：

MSA 的核心选择是 **per-GQA-group 独立 × 块级粒度**。这位于检索灵活性与硬件效率的最佳平衡点：

- DSA 的 token 级粒度更细，但难以高效映射到 GPU matrix 操作
- DSA 所有 head 共享一个索引，丢失了多头检索多样性
- MSA 的块级连续性使得 KV-outer 迭代具有远高于 Q-outer 的算术强度（`2/3 * B_k >> G`），而 token 级稀疏很难做到
- MSA 的 KL loss + gradient detach 方案让 indexer 训练成为局部的、干净的信号，避免了 DSA 中可能出现的 backbone 扰动

MSA 相比 DSA 的弱项：MLA 的 KV cache 压缩能力比 GQA 更优，MLA + 稀疏注意力理论上能在 long-context decoding 中节省更多显存带宽。

## 消融洞察（消融实验的关键教训）

### 1. Gradient Detach 的必要性

不加 detach 时，KL loss 梯度进入 backbone 产生两种失败模式：
- KL 系数较大时 → 梯度尖峰导致 LM loss 在几百步内发散
- 即使系数稳定 → backbone 通过简化自身 attention 分布来降低 KL loss（self-distillation 效应），短上下文 benchmark 逐步退化

**教训**：辅助 loss 必须严格限制在目标子网络，不可让它影响主网络的学习目标。

### 2. Index Value Head → 可省

- 训练初期需要 Index Branch 输出参与 LM loss 来初始化 indexer
- 引入 warmup 后，indexer 在 warmup 阶段就能获得良好初始化，Index Value Head 不再必要
- 消融实验显示 with-value 和 no-value 在全部 benchmark 上互有胜负，无系统性差异
- **教训**：临时性的训练辅助组件可以用更优雅的调度方案替代。

### 3. Learnable Attention Sink → 不需要

- GPT-OSS 风格的可学习 sink 参数不能完全消除 first-token sink 行为，部分 head 的 first token 仍是主导 sink
- 下游 perplexity 无稳定改善
- **教训**：自然涌现的模式不必用显式参数建模，先尝试让模型自行习得。

### 4. Forced Sink & Local Window → 可省

- 初期为了稳定训练同时强制选择第一个块和一个固定局部窗口
- 消融后移除这些强制约束，模型仍然表现出 sink 和局部选择模式
- RULER-32K 甚至从 65.8 降到 61.5（无强制更好）
- **教训**：硬编码的先验知识会限制模型适应能力，初始稳定后早移除。

### 5. Sliding Window vs. Dynamic Selection

- 在相同 FLOP 预算下，滑动窗口（固定位置模式）perplexity 始终高于 MSA
- **教训**：内容相关的动态稀疏比位置固定的稀疏有本质优势，即使在相等计算量下。

## 可复用的工程经验

### 设计原则

1. **在已有基础设施上叠加**：MSA 构建在 GQA 之上，而非取代它。任何已有的 GQA 模型都可以用 MSA 替换注意力层（通过 CPT 路线），无需从头训练。对比 NSA（需要 MQA/MHA backbone 和三路并行结构），MSA 的迁移成本极低。

2. **选择器与计算器分离**：Index Branch 只做选择，不做注意力计算。推理时 Index Branch 只需计算 block-wise max-pooling，完全不涉及 exp 操作和 value 聚合。这种职责分离使得训练（需要 KL loss）和推理（只需要 dot product + max）的优化路径不同。

3. **Occam's Razor 的实践方法论**：先加所有可能组件，然后逐一消融移除。每个组件的存在必须有可测量的收益，否则移除。论文通过系统性的消融实验（梯度源、value head、sink、local window、block size），只保留必要的核心组件。

### 训练技巧

4. **两阶段 warmup 策略**：从已训练的 dense checkpoint 到稀疏注意力，不是一次切换，而是先跑 full attention warmup（仅训练 indexer），再切换到稀疏模式。这对于稳定性和下游质量至关重要。

5. **Local block 作为安全网**：始终保留 query 自身的 local block 是最小必要的先验知识——它防止了训练早期 indexer 把关键局部信息全选丢。注意只保留 local block，不保留全局 sink 或大局部窗口。

6. **Gradient detach 保护主网络**：辅助 loss 的梯度必须通过 `stop_gradient` 限制在目标子网络内。否则辅助 loss 会将不相关的优化信号注入主网络，导致灾难性遗忘或训练不稳定。

### Kernel 工程

7. **小 k 场景专用 TopK**：通用 TopK kernel 针对大规模候选集优化（radix sort/bitonic sort），小 k 场景（k=16）用 per-thread heap + shuffle merge 反而更快（5.1× over torch.topk）。

8. **KV-outer 迭代 + Query Gather**：稀疏注意力中每个 KV block 被少量 query 选中，Q-outer 迭代会导致算术强度低。切换到 KV-outer + gather 后，算术强度从 `G` 提升到 `2/3 * B_k`（~85 vs 16）。

9. **Pre-scheduled chunking 解决负载不均**：sink block 等热门块被几乎所有 query 选中，单 CTA 处理会严重过载。GPU 调度 kernel 将大 tile 切分为小 chunk，多 CTA 并行处理同一 KV tile。

10. **Two-phase forward 替代 online softmax**：当一条 query 的 k 个 partial 由 k 个不同 CTA 产出时，无法做 inline softmax。分离为 attention kernel + combine kernel，先写局部归一化的 partial 和 logsumexp，再全局合并。

### 部署视角

11. **两条生产路线**：
    - **MSA-PT**（从头训练）：适合新模型，sparse 从头学，质量最优（尤其在多模态和长上下文上）
    - **MSA-CPT**（从 dense checkpoint 转换）：适合已有 GQA 模型的升级，只需 400B token 的继续训练

12. **固定预算推理**：无论上下文多长（128K、1M），每个 query 始终只处理 2048 个 KV token。延迟与上下文长度无关，只与固定预算相关。

13. **与 GQA 的兼容性**：MSA 可以直接插入任何 GQA-based 模型（当前大多数开源前沿模型），无需修改 backbone 结构。这大大降低了采用门槛。
