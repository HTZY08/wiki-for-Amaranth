---
title: DeepSeek V4 完整技术报告 — 放弃 MLA，CSA+HCA 混合注意力开创百万级长上下文效率新范式
date: 2026-07-17
source: https://arxiv.org/abs/2606.19348
---

# DeepSeek V4 完整技术报告

**发布日期：** 2026-06-29（arXiv 提交）
**来源：** https://arxiv.org/abs/2606.19348
**工程范式：** 极致推理效率路线——自 V2 以来最大的架构变更，放弃定义 V2/V3 的核心发明 MLA，转向 CSA+HCA 混合注意力 + mHC 残差 + Muon 优化器。

> 本文分析基于 2026 年 6 月发布的完整技术报告（arXiv:2606.19348，~150K 字符，319 位作者）。此为 2026 年 4 月 HuggingFace 模型卡预览版分析（`04-24-deepseek-v4-preview.md`）的补充——现在有了完整的架构细节、benchmark 数据和内部评测。

## 设计哲学

DeepSeek 面对的核心约束是推理成本——KV cache 随序列长度线性增长，1M 上下文下 V3.2 的 KV cache 大到部署成本不可接受。他们选择了一次架构级的彻底重构：放弃自己定义了两代的 MLA（Multi-head Latent Attention），转向 CSA+HCA 混合注意力。这是罕见的「自我革命」——放弃自己创造并验证过的成熟架构。

核心取舍：放弃 MLA 的 KV 压缩路线，选择稀疏化 + 重压缩的混合路线。彻底性在于不仅改了 attention，连残差流都换了（mHC 替代标准残差连接），optimizer 也从 AdamW 换成了 Muon。

关键发现：**DeepSeek 意识到 scaling 的下一个瓶颈不是模型容量，而是长上下文推理效率。** 因此 V4 的架构设计以"在 1M 上下文下的推理 FLOPs 和 KV cache 规模"为核心度量。

## 关键架构决策

### 混合注意力：CSA + HCA

V4 放弃了 V3 的 MLA（KV 低秩压缩），设计了双通道压缩注意力：

- **CSA（Compressed Sparse Attention）：** 每 4 个 token 压缩为 1 个 KV entry（4x 压缩），再用 Lightning Indexer（FP4 精度）做 top-k 稀疏选择。索引器独立训练的 dual-encoder 架构，不加载 backbone。每 query 选 512（Flash）或 1024（Pro）个压缩 KV entry。额外加 128 token 的 sliding window 保局部依赖。

- **HCA（Heavily Compressed Attention）：** 每 128 个 token 压缩为 1 个 KV entry（128x 压缩），不做稀疏选择，保持 dense attention 作为粗粒度全局视图。

- **混合策略：** 前 2 层用纯 SWA（Flash）或纯 HCA（Pro），之后层交错排列 CSA 和 HCA。

- **Positional Encoding：** Partial RoPE——只对最后 64 维加位置编码，输出端用 -i 实现相对位置。

- **Attention Sink：** 可学习的 sink logits，允许 query head 将总注意力权重调整为小于 1 甚至接近 0。

### mHC（Manifold-Constrained Hyper-Connections）

替代标准残差连接，将残差流宽度从 d 扩展到 n_hc × d（n_hc=4）：

- 残差映射矩阵 B_l 约束到 Birkhoff 多面体（双随机矩阵流形），谱范数 ≤ 1，保证非扩张性
- 通过 20 次 Sinkhorn-Knopp 迭代实现投影
- 输入/输出映射用 Sigmoid 约束非负有界
- 参数是动态（输入相关）和静态分量的组合
- 训练开销仅占 1F1B pipeline 阶段的 6.7%（通过融合 kernel + 重计算策略优化）

### MoE 设计

- **Flash：** 1 shared + 256 routed experts，每 token 激活 6 个
- **Pro：** 1 shared + 384 routed experts，每 token 激活 6 个
- 激活函数从 Sigmoid 改为 Sqrt(Softplus)
- 前 3 层 MoE 层使用 Hash routing（基于 token ID 的确定性路由）
- 取消路由目标节点数约束，重设计并行策略
- 沿用 auxiliary-loss-free + 极轻的 sequence-wise balance loss

### Muon 优化器

V3 的 AdamW 换成 Muon，核心是 Newton-Schulz 迭代来做参数更新的正交化：

- 混合 Newton-Schulz：前 8 步用快速收敛系数 (3.4445, -4.7750, 2.0315)，后 2 步用稳定系数 (2, -1.5, 0.5)
- Nesterov momentum（0.95）
- 权重衰减 0.1
- Embedding/prediction head/RMSNorm 仍用 AdamW
- MoE 梯度用 BF16 随机舍入通信，两阶段 all-to-all 避免精度累积误差

### 训练稳定性

遇到了典型的万亿参数 MoE 训练不稳定性问题：

- **Anticipatory Routing：** 路由网络用历史参数（延迟 Δt 步）计算路由索引，断开路网和主网络之间的正反馈循环。实践中预取数据 + 缓存路由索引，仅引入约 20% 额外开销。触发 loss spike 时动态启用。
- **SwiGLU Clamping：** 线性分量钳制到 [-10, 10]，门控分量上界钳制到 10。

### 模型规格

| | V4-Flash | V4-Pro |
|---|---|---|
| 总参数量 | 284B | 1.6T |
| 激活参数量 | 13B | 49B |
| Transformer 层数 | 43 | 61 |
| 隐藏维度 | 4096 | 7168 |
| Routed experts | 256 | 384 |
| 每 token 激活 experts | 6 | 6 |
| 预训练 tokens | 32T | 33T |
| 峰值学习率 | 2.7e-4 | 2.0e-4 |

### 基础设施创新

- **MegaMoE：** 细粒度 EP 融合 kernel（Dispatch-Compress-Combine 全 pipeline 重叠），1.50-1.73x 推理加速，RL rollout 场景达 1.96x。开源在 DeepGEMM。
- **TileLang：** DSL 代替手写 CUDA kernel，支持 Host Codegen（Python 调用开销从数十微秒降至 <1μs）+ Z3 SMT 求解器做形式化整数分析。
- **批量不变性：** dual-kernel 策略实现 batch-invariant attention decoding，替换 cuBLAS 为 DeepGEMM 支持 bitwise 可复现训练和推理。
- **异构 KV Cache：** 为 CSA/HCA 压缩 KV + SWA 设计了双区 KV cache + on-disk 存储策略（Full/Periodic/Zero 三种 SWA 缓存模式）。

### Post-Training 管线

两阶段范式：

1. **独立培养领域专家：** 对数学、编码、agent、指令跟随等各自训练 expert model（SFT + GRPO RL）
2. **On-policy 蒸馏统一：** 统一模型作为学生，通过 reverse KL loss 从多个 teacher 学习

### 推理效率

1M 上下文下 vs V3.2：
- V4-Pro：单 token 推理 FLOPs 仅 27%，KV cache 仅 10%
- V4-Flash：单 token 推理 FLOPs 仅 10%，KV cache 仅 7%

## 关键结果

### Benchmark 评测

报告中未提供完整的 benchmark 数字表格（但提供了 vs Gemini-3.1-Pro 和 Claude-Opus-4.5 的内部评测表格）。以下是报告中披露的关键结论：

**知识：**
- SimpleQA / Chinese-SimpleQA 显著领先开源模型
- MMLU-Pro / HLE / GPQA 略微领先其他开源模型
- 仍落后 Gemini-3.1-Pro（但差距已大幅缩小）

**推理（更多推理 token 扩展后）：**
- V4-Pro-Max 超越 GPT-5.2 和 Gemini-3.0-Pro
- 落后 GPT-5.4 和 Gemini-3.1-Pro（约 3-6 个月差距）
- V4-Flash-Max 与 GPT-5.2 和 Gemini-3.0-Pro 相当 → 极高的成本效益

**Agent：**
- 公开评测上与 Kimi-K2.6、GLM-5.1 相当
- 内部评测超越 Claude Sonnet 4.5，接近 Opus 4.5

**长上下文：** V4-Pro-Max 在 1M token 评测中超越 Gemini-3.1-Pro

### 中文写作与指令遵循（内部评测 vs Gemini-3.1-Pro）

- 办公文本 3170 样本：DS 赢 62.65%，Gem 赢 34.10%，平 3.25%
- 创意写作 2837 样本：指令遵循 DS 赢 60.03%，写作质量 DS 赢 77.48%
- 中文创意写作所有子类中，DS 在绝大多数类别领先

### vs Claude-Opus-4.5

- 复杂指令遵循 49 样本：DS 46.9%，Opus 53.1%
- 多轮写作 147 样本：DS 45.6%，Opus 51.7%

## 范式对比

| 维度 | DeepSeek V4 | DeepSeek V3.2 | Qwen 3.5 | MiniMax M2.7 |
|------|-------------|---------------|----------|--------------|
| 注意力 | CSA+HCA 混合 | MLA | Hybrid SWA+Full | Full Attention |
| 激活参数 | 49B/13B | 37B | 3B-35B | 9.8B |
| 优化器 | Muon | AdamW | AdamW | 未披露 |
| 残差 | mHC | 标准 | 标准 | 标准 |
| 长上下文效率 | **极致**（87-93% FLOPs 减少） | 基线 | 中等 | 中等 |
| 开源 | MIT | MIT | Apache 2.0 | 未开源 |

DeepSeek V4 是**当前唯一在架构层面同时做 KV 压缩 + 稀疏选择 + 重压缩 + 残差重构 + 优化器替换的模型**。Qwen 3.5 和 MiniMax M2.7 选择更保守的注意力设计（SWA hybrid / full attention），DeepSeek 选择了变革最激进的路。

## 社区评价

截至分析日，该论文 arXiv 引用为 0（刚提交不久）。HN 和 Reddit 上的讨论尚未形成。HuggingFace 上模型已提供下载（MIT 协议），社区反响正面——特别是 MegaMoE kernel 开源在 DeepGEMM 获得关注。

## 可复用的工程经验

1. **长上下文是下一个 scaling 瓶颈**——V4 证明了架构级创新可以在 1M 上下文中将推理成本降低 90% 以上
2. **Anticipatory Routing 是训练稳定性强的低成本方案**——断开路网和主干网的正反馈循环比单纯 clamp 更根本
3. **DSL kernel 开发比手写 CUDA 更适合研究型团队**——TileLang 的例子：平衡生产力和性能
4. **位级可复现训练是值得投资的基础设施**——batch invariance + determinism 让 debug 效率大幅提升
5. **两阶段 post-training（专家培养→统一蒸馏）比单一 RL 更有效**——先各自深耕，再统一精华
6. **Muon 可能成为 AdamW 的继任者**——Newton-Schulz 正交化 + BF16 通信压缩，V4 是目前最大的 Muon 验证案例
