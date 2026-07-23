---
title: DeepSeek-V3.2 — DSA 稀疏注意力与 10% 后训练算力扩展的工程实践
date: 2025-12-25
source: https://arxiv.org/abs/2512.02556
---

# DeepSeek-V3.2 — DSA 稀疏注意力与 10% 后训练算力扩展的工程实践

**发布日期：** 2025-12-25（arXiv 预印本）；2025-09（V3.2-Exp）；2025-12（V3.2 正式版）
**来源：** https://arxiv.org/abs/2512.02556
**工程范式：** 在 MLA 基础上引入 DeepSeek Sparse Attention (DSA)，通过稀疏注意力降低长序列推理成本；将后训练计算预算推至预训练的 10%+，配合大规模合成 agent 任务 RL 逼近闭源前沿

## 设计哲学

DeepSeek-V3.2 面对的核心矛盾是：开源模型与闭源模型的差距在**三个维度**上同时拉大——架构效率（vanilla attention 的长序列瓶颈）、后训练算力投入（开源普遍不足）、agent 泛化能力（工具使用场景的指令跟随差距）。

三个技术突破对应三个约束：

1. **DSA（DeepSeek Sparse Attention）**：在 MLA 基础上叠加稀疏索引器，将注意力复杂度从 O(L²) 降至 O(Lk)，k=2048 ≪ L。放弃的是"所有 token 间全连接"的假设——实践中大多数注意力权重集中在少量 token 上。
2. **后训练算力扩展**：RL 训练的计算预算超过预训练成本的 10%。放弃的是"预训练决定一切"的假设——后训练阶段的大规模 RL 可以显著提升 reasoning 和 agent 能力。
3. **Agentic Task 合成管线**：放弃"真实数据才是好数据"的假设——用合成管线生成 1,800+ 环境 + 85,000+ 复杂 prompt 来做 RL，泛化到未见过的工具使用场景。

## 关键架构决策

### 注意力机制：DeepSeek Sparse Attention (DSA)

- **核心思路**：在 MLA 的 MQA 模式下，用一个轻量级 Lightning Indexer 为每个 query token 选择 top-k 个 KV 条目（k=2048），只对选中的条目做注意力计算
- **Lightning Indexer**：小规模的 multi-head scorer（FP8 实现），计算出 query 和每个前驱 token 之间的 index score。使用 ReLU 激活（考虑吞吐量），仅用作 token 选择、不做 softmax
- **实例化在 MLA 上**：基于 MQA 模式的 MLA 实现，每个 KV entry 自然被多个 query heads 共享
- **两阶段持续预训练**：
  - Dense Warm-up (1,000 steps, 2.1B tokens)：冻结主模型参数，仅训练 Indexer，用 KL 散度对齐 Indexer 输出与主注意力分布。LR=10⁻³
  - Sparse Training (15,000 steps, 943.7B tokens)：引入 token selection，优化全部参数。Indexer 从计算图 detach 单独优化，仅接收 KL loss 信号。LR=7.3×10⁻⁶，每 query 选 2048 个 KV tokens
- **推理成本**：Prefilling 阶段 O(L²) 降为 O(Lk)，decoding 阶段类似。H800 集群实测显示长序列场景 token 成本显著低于 V3.1-Terminus
- **短序列场景**：特别实现 masked MHA 模式模拟 DSA，保持短上下文下的效率

### MoE 设计

- 沿用 DeepSeek-V3 的 MoE 架构（MLA + MoE），与 V3.1-Terminus 架构完全一致，**唯一的架构改动是 DSA 的引入**
- 基于 V3.1-Terminus 的 128K 上下文长度继续训练
- **Keep Routing** 机制：推理时保存 expert routing path，训练时强制执行相同路径——解决 MoE 模型中推理和训练框架的 routing 不一致导致的优化不稳定问题

### 训练策略：可扩展的 GRPO

- **不偏 KL 估计**：修正 K3 估计器，使用 importance-sampling ratio 得到 unbiased KL 估计。当 π_θ ≪ π_ref 时原始 K3 梯度会赋予超大权重，修正后消除了系统性偏差
- **Off-Policy Sequence Masking**：当序列的 policy divergence 超过阈值 δ 且 advantage 为负时 mask 掉该序列。直觉：模型从自己的错误中学到最多，高度 off-policy 的负样本会破坏稳定性
- **Keep Sampling Mask**：保留 top-p/top-k 采样时的截断 mask，确保 π_old 和 π_θ 共享相同的 action subspace
- **专家蒸馏**：为 6 个领域（数学、编程、逻辑推理、通用 agent、agent coding、agent search）分别训练 specialist，用 RL 训练到高水平，然后蒸馏数据到最终 checkpoint。蒸馏后性能仅略低于 specialist，后续 RL 抹平差距

### Post-training：思考如何在工具调用中保持推理链

- **思考上下文管理**：Discard reasoning content only when new user message arrives；工具调用结果返回时保留 reasoning trace。这避免了 DeepSeek-R1 策略中每轮工具调用都重新推理的 token 浪费
- **Cold-Start**：精心设计 system prompt 让模型产生 reasoning-in-tool-use 的轨迹作为 RL 初始种子
- **Agentic 任务四大类**：
  - Code Agent：从 GitHub 挖掘数百万 issue-PR pair，构建可执行环境（支持 Python/Java/JS/TS/C/C++/Go/PHP）
  - Search Agent：用多 agent 管线生成长尾实体 QA 对，覆盖多语言多领域
  - Code Interpreter：Jupyter Notebook 做复杂推理
  - General Agent：自动合成 1,827 个任务环境和 4,417 个 prompt，每个环境附带 verifier

### 推理优化

- DSA 降低 KV cache footprint，配合 MLA 的 KV 压缩
- Out-of-domain agent 泛化验证：RL 仅在合成数据上训练，但 MCP-Universe/MCP-Mark等未见过的环境上仍有显著提升
- 上下文管理扩展 test-time compute：Summary/Discard-75%/Discard-all 三种策略应对长 agent 轨迹的场景

## 关键结果

### 主模型（DeepSeek-V3.2 Thinking vs 闭源/开源前沿）

| 基准 | GPT-5 High | Gemini-3.0 Pro | Kimi-K2 Thinking | DeepSeek-V3.2 Thinking |
|------|-----------|---------------|-----------------|----------------------|
| MMLU-Pro (EM) | 87.5 | 90.1 | 84.6 | **85.0** |
| GPQA Diamond (Pass@1) | 85.7 | 91.9 | 84.5 | **82.4** |
| HLE (Pass@1) | 26.3 | 37.7 | 23.9 | **25.1** |
| AIME 2025 (Pass@1) | 94.6 | 95.0 | 94.5 | **93.1** |
| LiveCodeBench (Pass@1-COT) | 84.5 | 90.7 | 82.6 | **83.3** |
| Codeforces (Rating) | 2537 | 2708 | - | **2386** |
| SWE Verified (Resolved) | 74.9 | 76.2 | 71.3 | **73.1** |
| SWE Multilingual (Resolved) | 55.3 | - | 61.1 | **70.2** |
| Terminal Bench 2.0 (Acc) | 35.2 | 54.2 | 35.7 | **46.4** |
| BrowseComp (Pass@1) | 54.9 | - | 60.2* | **67.6*** |
| BrowseCompZh (Pass@1) | 63.0 | - | 62.3 | **65.0** |
| MCP-Universe (Success Rate) | 47.9 | 50.7 | 35.6 | **45.9** |

* 带 * 的 BrowseComp 分数启用了上下文管理

### DeepSeek-V3.2-Speciale（高算力变体，IMO/IOI 金牌）

| 基准 | GPT-5 High | Gemini-3.0 Pro | DS-V3.2 Speciale |
|------|-----------|---------------|-----------------|
| AIME 2025 | 94.6 | 95.0 | **96.0** |
| HMMT Feb 2025 | 88.3 | 97.5 | **99.2** |
| IMOAnswerBench | 76.0 | 83.3 | **84.5** |
| LiveCodeBench | 84.5 | 90.7 | **88.7** |
| Codeforces Rating | 2537 | 2708 | **2701** |
| HLE | 26.3 | 37.7 | **30.6** |

竞赛成绩：IMO 2025 金牌（35/42）、CMO 2025 金牌（102/126）、IOI 2025 金牌（492/600，总分第10）、ICPC WF 2025 金牌（10/12 题，总分第2）

### Token 效率对比（DeepSeek-V3.2 vs K2-Thinking）

相同精度水平下，DeepSeek-V3.2 使用显著更少的输出 token：
- AIME 2025: DS 16k → K2 24k（少 33%）
- HMMT Feb: DS 19k → K2 31k（少 39%）
- LiveCodeBench: DS 16k → K2 29k（少 45%）

### 合成 Agent 任务难度验证（Pass@K）

| Pass@K | DS V3.2-Exp | Sonnet-4.5 | Gemini-3.0 Pro | GPT-5 Thinking |
|--------|-----------|-----------|---------------|---------------|
| 1 | 12% | 34% | 51% | 62% |
| 2 | 18% | 47% | 65% | 75% |
| 4 | 26% | 62% | 74% | 82% |

合成任务对 DeepSeek V3.2-Exp 足够难（12%），对闭源模型也有挑战性（最高 62%）。

## 范式对比

**vs DeepSeek-V4：** V3.2 和 V4 走的是不同的优化方向。V3.2 聚焦于 **DSA + 后训练 RL scaling**，V4 聚焦于 **百万 token 上下文 + 超长序列效率**。V3.2 的 DSA（选 k=2048 个 token）和 V4 的 FlashMemory 索引是不同粒度的稀疏化策略。

**vs Kimi K2：** V3.2 在大部分基准上匹配 K2，但 token 效率显著更好（少 33-45% 的推理 token）。这得益于 DSA + MLA 的架构优势和更高效的 RL 训练。

**vs GPT-5/Gemini-3.0 Pro：** 在 reasoning 基准上接近 GPT-5，落后 Gemini-3.0 Pro。Speciale 变体在竞赛上匹敌 Gemini-3.0 Pro，但 token 效率差 2-3 倍。

**关键差异：** DeepSeek 是唯一有系统公开 ">10% 预训练算力用于后训练 RL" 细节的团队。这个数字本身就是一个工程声明——后训练不再只是"微调"，而是与预训练等量级的大规模计算。

## 社区评价

- r/LocalLLaMA 上 V3.2 发布后讨论集中在其 DSA 的 FP8 实现效率和 Keep Routing 机制对 MoE RL 训练稳定性的贡献
- Sebastian Raschka 的技术点评中将 V3.2 的 GRPO 扩展策略（KL 修正 + Off-Policy Masking）列为"2025 年 RL 稳定化训练的最实用产出"
- Speciale 的 IMO/IOI 金牌成绩被认为是"开源模型首次在竞赛推理上达到封闭模型水平"的标志性事件

## 可复用的工程经验

1. **DSA 的 Indexer Alignment 策略**：先用 1000 step 的 dense warm-up 冻结主模型训练 Indexer（LR=10⁻³），再用 15K step 的 sparse training 联合优化。分阶段引入稀疏化显著减少了训练不稳定性
2. **Off-Policy Sequence Masking**：当 advantage 为负且 π_old / π_θ 的 KL 超过阈值时 mask 掉该序列。精确解决了 MoE + RL 中 inference/training framework 不一致导致的 off-policy 问题
3. **Keep Routing + Keep Sampling Mask**：MoE 模型 RL 训练的两个关键工程技巧，前者稳定 expert 参数空间，后者保证 action subspace 一致
4. **合成任务自动生成 + Verifier**：1,800+ 环境的自动合成管线是开源社区最实用的经验——"hard to solve, easy to verify"的任务设计原则适用于任何想用合成数据做 RL 的团队
5. **Thinking Context Management**：只在用户新消息到达时丢弃 reasoning trace，工具调用结果返回时保留。这个策略让 agent 场景的 token 效率比 Re-R1 方案提升数倍，但需要 agent framework 不使用 user message 模拟工具调用（Roo Code/Terminus 等不兼容）
