---
title: Attention Residuals — 用深度注意力替代固定残差连接，补上 Transformer 最后一块"线性拼图"
date: 2026-03-31
source: https://arxiv.org/abs/2603.15031
---

# Attention Residuals — 深度维度的 softmax 注意力

**发布日期：** 2026-03-31（arXiv 预印本）
**来源：** https://arxiv.org/abs/2603.15031
**工程范式：** 架构创新——将残差连接从固定单位权重的加法升级为可学习的深度维 softmax 注意力，补全 Transformer 在"深度"维度上的线性→softmax 转变

## 设计哲学

核心观察：现代 Transformer 在**序列维度**已经完成了从 RNN 式线性累积到注意力式选择性融合的跃迁（自注意力），但在**深度维度**，残差连接仍然停留在固定权重加法——每个层接收到的是所有前层输出的等权累加，无法选择性强调或抑制特定层的贡献。

关键约束：PreNorm 的等权累加导致 hidden-state 规模随深度线性增长 O(L)，深层输出被稀释，早期信息被埋没。Moonshot 观察到这是 Transformer 架构中最后一个没有使用可学习融合机制的地方。

核心思想：**深度维度和序列维度存在形式上的对偶性**——RNN 在时间上的线性累积 ↔ 残差连接在深度上的线性累积，因此可以在深度维度上引入和序列维度类似的选择性注意力机制。

## 关键架构决策

### 完整版 Attention Residuals (Full AttnRes)

- 将残差累加 `h_l = Σ v_i` 替换为 `h_l = Σ α_{i→l} · v_i`
- α_{i→l} 是 softmax 注意力权重，由每层一个可学习的伪查询向量 w_l ∈ ℝ^d 计算
- key = value = 前层输出 v_i，使用 RMSNorm 防止大输出层支配注意力权重
- 计算复杂度 O(L²d)，存储 O(Ld)——因为深度 L 通常远小于序列长度 T，O(L²) 在典型 40-80 层网络中是可行的

### 分块版 Block AttnRes（大规模训练实用版本）

- 将 L 层划分为 N 个块（实践中 N≈8），每块内用标准残差和求和，块间用注意力
- 存储/通信从 O(Ld) 降为 O(Nd)
- 配合跨阶段缓存（Cross-stage caching）消除流水线并行下的冗余通信
- 两阶段计算策略（Phase 1: 批处理块间注意力 → Phase 2: 块内顺序合并，使用 online softmax merge）
- 推理延迟开销 < 2%，训练开销在流水线并行下 < 4%

### 集成到 Kimi Linear 架构

- 48B 总参数 / 3B 激活参数，27 Transformer 块（54 层）
- 混合 Kimi Delta Attention (KDA) 和 Multi-Head Latent Attention (MLA)，3:1 比例
- 8/256 routed experts + 1 shared expert
- 6 层/块 → 10 个深度源（9 个块 + token embedding）
- 优化器：Muon，WSD 学习率调度，8M token 全局 batch size
- 预训练 1T tokens + mid-training 400B 高质量数据

### 训练关键技巧

- **初始化至关重要**：所有 w_l 初始化为零，保证初始注意力权重均匀（等价于等权平均），防止训练发散
- **RMSNorm on keys**：防止自然输出幅度大的层主导 softmax，在 Block AttnRes 中尤其关键

## 关键结果

### Scaling Laws

| 变体 | 拟合曲线 | 在 5.6 PFLOP/s-days 的 loss |
|------|---------|--------------------------|
| Baseline (PreNorm) | L = 1.891 × C^(-0.057) | 1.714 |
| Block AttnRes | L = 1.870 × C^(-0.058) | **1.692** |
| Full AttnRes | L = 1.865 × C^(-0.057) | **1.690** |

Block AttnRes 匹配 baseline 需要 1.25× 更多算力。Full AttnRes 略优于 Block，差距随规模缩小。

### 48B 模型下游结果

| 评测 | Baseline | Block AttnRes | Δ |
|------|---------|--------------|---|
| MMLU | 65.9 | **67.0** | +1.1 |
| MMLU-Pro Hard | 35.8 | **38.1** | +2.3 |
| GPQA-Diamond | 37.5 | **45.0** | **+7.5** |
| BBH | 66.3 | **67.6** | +1.3 |
| ARC-Challenge | 75.8 | **76.2** | +0.4 |
| HellaSwag | 79.7 | **79.9** | +0.2 |
| TriviaQA | 72.0 | **73.9** | +1.9 |
| GSM8K | 74.9 | **77.4** | +2.5 |
| MGSM | 58.6 | **61.4** | +2.8 |
| Minerva Math | 35.9 | **39.5** | +3.6 |
| HumanEval | 53.7 | **56.8** | +3.1 |
| MBPP | 67.6 | **68.8** | +1.2 |
| CMMLU | 73.2 | **73.5** | +0.3 |
| C-Eval | 64.0 | **64.7** | +0.7 |

**最大增益出现在多步推理任务**：GPQA-Diamond (+7.5)、Minerva Math (+3.6)、HumanEval (+3.1)，与"更好的深度信息流动有助于组合性任务"的假设一致。

### 消融实验关键结论

- 无输入依赖的 DenseFormer：无增益（1.767 vs baseline 1.766）
- mHC（多流混合）：1.747
- Block AttnRes：1.746，等价于 mHC 但每层 I/O 仅 5.5d 对比 mHC 的 34d
- 滑动窗口聚合（W=8）：1.764——远不如 Block AttnRes，说明远距离层的选择性访问更重要
- Input-dependent query（从当前 hidden state 投影）：可进一步降至 1.731，但引入额外投影和顺序依赖，对推理延迟影响大

### 训练动力学

- **输出幅度**：Baseline 随深度单调增长，Block AttnRes 被限制在块内周期性模式
- **梯度分布**：Baseline 早期层梯度过大，Block AttnRes 更均匀

## 范式对比

| 方法 | 深度聚合方式 | 参数量 | 每层 I/O | 适用场景 |
|------|------------|--------|---------|---------|
| Standard Residual | 等权相加 | 0 | 2d+2d | 最简基线 |
| DenseFormer | 固定标量系数 | O(L) | O(Ld) | 学术验证 |
| (m)HC | m 流混合矩阵 | O(m²L) | ~34d (m=4) | 中等开销 |
| **Full AttnRes** | **深度维 softmax 注意力** | **Ld** | **O(Ld)** | **性能最优** |
| **Block AttnRes** | **分块注意力** | **Ld** | **5.5d** | **实用最优** |

## 社区评价

这篇工作本质上是在"深度"维度上完成了一次从线性到 softmax 注意力的跃迁，和自注意力在序列维度上的历史作用形成对偶——有理论美感。但实用价值取决于 Block AttnRes 能否在更大规模（500B+ 参数）和更长训练（10T+ token）下持续有效。目前 1.4T token 的训练规模相对有限，需要更大规模验证。

## 可复用的工程经验

1. **深度维注意力是低 hanging fruit**：L 通常 < 100，O(L²) 的深度注意力在计算上完全可行，是一个被忽视的架构改进方向
2. **Block 化是工作化关键**：N≈8 的 Block AttnRes 能在保持大部分收益的同时降低通信/存储开销到实用水平
3. **初始化陷阱**：所有新增的可学习权重要初始化为零，否则高阶注意力会破坏初始训练稳定性
4. **消融设计范本**：这篇的消融实验（比较跨层访问粒度、组件、超参数、与 prior work 对比）是架构论文的参考标准——每条结论都有定量证据支持
5. **交叉注意力层间信息流动**：可视化显示 pre-attention 层有更广的感受野，而 pre-MLP 层更关注近邻——这种层类型特化值得在后续架构中作为设计原则
