---
title: DeepSeek-V4 — 百万 Token 上下文的高效 MoE 架构
date: 2026-07-05
source: https://arxiv.org/abs/2606.19348
---

# DeepSeek-V4 — 百万 Token 上下文的高效 MoE 架构

**发布日期：** 2026年6月（arXiv 2606.19348）
**来源：** https://arxiv.org/abs/2606.19348
**模型权重：** https://huggingface.co/collections/deepseek-ai/deepseek-v4
**工程范式：** 用极致架构创新突破长上下文效率瓶颈

---

## 设计哲学

### 核心约束

DeepSeek-V4 面对的核心矛盾是：**vanilla attention 的二次计算复杂度在超长上下文中成为不可承受的瓶颈**。随着推理模型（如 o1、DeepSeek-R1）确立 test-time scaling 新范式，长上下文处理成为制约进一步 scaling 的关键障碍。具体而言：

- 1M token 上下文中，标准 attention 的 FLOPs 和 KV cache 开销随序列长度平方增长
- 长时域任务（复杂 agentic workflow、跨文档分析、online learning）需要高效支持超长序列
- 同时要在不牺牲短文本能力的前提下实现长上下文效率

### 架构选择的权衡

| 约束 | 应对策略 | 放弃的选项 |
|------|----------|-----------|
| Attention 二次复杂度 | 混合压缩注意力（CSA + HCA），将序列压缩到 1/4 和 1/128 | 纯 dense attention 的简单性 |
| MoE 通信瓶颈 | 细粒度 EP 方案：wave-based 调度实现计算-通信全重叠 | 低带宽下可能的端到端性能 |
| 残差连接不稳定 | mHC：将残差映射约束到双随机矩阵流形 | 标准残差连接的简洁性 |
| 优化器收敛慢 | Muon optimizer + 混合 Newton-Schulz 正交化 | AdamW 的普适性（仅保留部分模块用 AdamW） |
| 训练不稳定 | Anticipatory Routing + SwiGLU Clamping | 简单回滚的权宜方案 |
| 推理显存 | FP4 QAT + 异构 KV cache + 磁盘存储 | FP8/BF16 精度的存储代价 |

### 重要放弃

论文明确承认：**为了极端的长上下文效率，DeepSeek-V4 采用了大胆的架构设计**，因此引入了相当程度的架构复杂性。未来迭代将进行更系统的"蒸馏"，保留最核心的设计，让架构更简洁而不牺牲性能。

---

## 关键架构决策

### 1. 混合注意力架构：CSA + HCA

这是 DeepSeek-V4 最核心的创新，目标是**在 1M 上下文下将 attention FLOPs 和 KV cache 降低到 V3.2 的个位数百分比**。

#### Compressed Sparse Attention (CSA)

- **压缩 KV 条目**：每 `m=4` 个 token 压缩为一个 KV 条目。压缩采用带可学习位置偏置的加权求和，使用来自前后窗口共 `2m` 个 KV 条目（存在重叠，实际压缩率为 1/m）
- **Lightning Indexer 稀疏选择**：为每个 query token 计算压缩 KV 条目上的 index scores，top-k 选择参与 core attention 的 KV 条目
  - Flash (284B)：top-k = 512
  - Pro (1.6T)：top-k = 1024
- **共享 KV MQA**：所有 query head 共用同一组压缩 KV 条目，采用 Multi-Query Attention
- **分组输出投影**：将 `n_h` 个 attention head 输出分成 `g` 组，每组先降维再投影回 hidden size，降低输出投影计算量
- **Sliding Window 辅助分支**：额外保留最近 `n_win=128` 个未压缩 KV 条目，增强局部依赖建模
- **Attention Sink**：可学习 sink logits，允许 attention head 的总注意力权重不等于 1

#### Heavily Compressed Attention (HCA)

- 比 CSA 更激进的压缩：每 `m'=128` 个 token 压缩为一个 KV 条目（不与 CSA 重叠压缩）
- 不做稀疏 attention——所有压缩 KV 条目都参与 dense attention
- 同样使用共享 KV MQA 和分组输出投影

#### 混合配置

- CSA 和 HCA 在 Transformer 层中交错排列
- Flash：43 层（前 2 层纯 SWA，后续层 CSA/HCA 交错）
- Pro：61 层（前 2 层 HCA，后续层 CSA/HCA 交错）
- 各层之间 KV cache 大小不同（因为 CSA/HCA 比例不同）

### 2. MoE 设计

| 规格 | DeepSeek-V4-Flash | DeepSeek-V4-Pro |
|------|-------------------|-----------------|
| 总参数量 | 284B | 1.6T |
| 激活参数量 | 13B | 49B |
| Transformer 层数 | 43 | 61 |
| Hidden size | 4096 | 7168 |
| 每层共享 expert | 1 | 1 |
| 每层 routed experts | 256 | 384 |
| 每 token 激活 experts | 6 | 6 |
| Expert intermediate dim | 2048 | 3072 |
| 前 3 层路由策略 | Hash routing | Hash routing |
| MTP 深度 | 1 | 1 |

继承 DeepSeek-V3 的 DeepSeekMoE 框架：细粒度 routed experts + shared experts。与 V3 的不同：
- 激活函数从 Sigmoid 改为 `Sqrt(Softplus(.))` 计算 affinity scores
- 移除对路由目标节点数量的约束
- 前几个 Transformer block 的 dense FFN 替换为 Hash routing 的 MoE 层

### 3. Manifold-Constrained Hyper-Connections (mHC)

mHC 是 Hyper-Connections (HC) 的改进，核心思想：

- 将残差流宽度从 `d` 扩展到 `n_hc × d`（n_hc=4），通过三个线性映射（输入/残差/输出）控制信息流
- **核心创新**：将残差映射矩阵 `B_l` 约束到**双随机矩阵流形（Birkhoff polytope）** ——确保谱范数 ≤ 1，从而使残差变换非扩张
- 通过 Sinkhorn-Knopp 算法（20 次迭代）将 `B_l` 投影到该流形
- 输入/输出映射也通过 Sigmoid 约束为非负有界
- 参数动态生成：输入相关成分 + 输入无关静态偏置
- 工程优化后，mHC 的 wall-time 开销仅占 overlapped 1F1B pipeline stage 的 **6.7%**

### 4. Muon Optimizer

- 大部分模块使用 Muon，仅 embedding、prediction head、mHC 静态偏置/gating factors、RMSNorm 保留 AdamW
- **混合 Newton-Schulz 迭代**：8 步快速收敛系数 + 2 步稳定系数，共 10 步
- Nesterov trick + update RMS rescaling（因子 0.18）
- 无需 QK-Clip：attention 架构允许直接对 query/KV 做 RMSNorm，防止 logit 爆炸
- MoE 梯度用随机舍入量化到 BF16 同步，通信量减半；使用 all-to-all + FP32 local sum 避免低精度累积误差

### 5. 训练策略

- Flash：32T tokens，max batch size 75.5M
- Pro：33T tokens，max batch size 94.4M
- 序列长度渐进扩展：4K → 16K → 64K → 1M
- 前 1T tokens 用 dense attention 预热，64K 长度时引入 sparse attention
- 引入 sparse attention 后，先用短阶段预热 lightning indexer
- AdamW 参数：β1=0.9, β2=0.95, ε=1e-20, weight_decay=0.1
- Muon：momentum=0.95, weight_decay=0.1, RMS rescale=0.18
- Flash peak LR：2.7e-4，Pro peak LR：2.0e-4，cosine decay 到 1/10

### 6. 训练稳定性

**Anticipatory Routing**：将 backbone 网络和 routing 网络的更新解耦——step t 使用 θ_t 计算特征，但路由索引使用历史参数 θ_{t-Δt}。动态触发：检测到 loss spike 时自动激活，稳定后恢复标准训练，额外开销约 20%。

**SwiGLU Clamping**：线性分量限制在 [-10, 10]，gate 分量上限 10。

### 7. FP4 量化感知训练 (QAT)

Post-training 阶段引入，应用于两个组件：
- **MoE expert weights**：FP32 master weights → FP4 量化 → 反量化回 FP8 计算（FP8→FP8 框架无需修改，因为 FP8 E4M3 动态范围覆盖 FP4 E2M1）
- **Indexer QK path**：QK 激活全部以 FP4 缓存/加载/乘加
- Index scores 从 FP32 量化到 BF16，top-k selector 获得 **2× 加速**，KV 条目 recall 率 **99.7%**

### 8. Post-Training：领域专家 → On-Policy Distillation 两阶段

**第一阶段——培养领域专家**：对数学、编程、agent、指令遵循四个领域分别独立训练专家模型。每个专家先做 domain-specific SFT，再用 GRPO 做 RL。

**第二阶段——On-Policy Distillation (OPD)**：10+ 个教师模型（各领域专家）通过 reverse KL divergence 蒸馏到一个统一学生模型。关键工程：
- 全词汇表 logit distillation（而非 token-level 近似），降低梯度估计方差
- 教师参数 offload 到分布式存储 + ZeRO 分片按需加载
- 只缓存最后一层 hidden states，运行时通过 prediction head 重建 logits
- 按教师索引排序训练样本，每 mini-batch 每个教师 head 只加载一次

### 9. 推理优化

- **异构 KV cache**：CSA/HCA 的 classical KV cache + SWA 和未压缩尾部 token 的 state cache
- **磁盘 KV cache 存储**：消除共享前缀请求的重复 prefilling
  - CSA/HCA：全量存储压缩 KV entries
  - SWA：三种策略（Full Caching / Periodic Checkpointing / Zero Caching），按部署场景选择
- **MegaMoE 融合 kernel**：CUDA kernel 实现 MoE 层计算-通信的全重叠管线，速度提升 1.50~1.73×（推理），最高 1.96×（RL rollout）
- **TileLang DSL**：平衡开发生产力和运行时效率，融合 kernel 开发，Z3 SMT solver 辅助形式化整数分析
- **Batch-invariant 确定性 kernel**：dual-kernel 策略解码、DeepGEMM 替代 cuBLAS、确定性 attention backward

### 10. 推理效率核心数据

以 BF16 GQA8（head dim 128）为 baseline：
- 1M 上下文下，DeepSeek-V4 系列 KV cache 降至 baseline 的 **~2%**

相对 DeepSeek-V3.2（1M 上下文）：

| 指标 | V4-Pro vs V3.2 | V4-Flash vs V3.2 |
|------|----------------|-------------------|
| 单 token FLOPs | **27%** | **10%** |
| KV cache 大小 | **10%** | **7%** |
| 激活参数量 | 49B vs 37B | 13B vs 37B |
| 总参数量 | 1.6T vs 671B | 284B vs 671B |

---

## 关键结果

### Base Model 对比（表 1，与 V3.2-Base 同设置评估）

| 维度 | 基准 | V3.2-Base (37B) | Flash-Base (13B) | Pro-Base (49B) |
|------|------|-----------------|------------------|----------------|
| **世界知识** | MMLU-Pro | 65.5 | 68.3 | **73.5** |
| | MMLU | 87.8 | 88.7 | **90.1** |
| | Simple-QA verified | 28.3 | 30.1 | **55.2** |
| | C-Eval | 90.4 | 92.1 | **93.1** |
| | SuperGPQA | 45.0 | 46.5 | **53.9** |
| **语言&推理** | BBH | 87.6 | 86.9 | 87.5 |
| | DROP (F1) | 88.2 | 88.6 | 88.7 |
| **代码&数学** | HumanEval | 62.8 | 69.5 | **76.8** |
| | MATH | 60.5 | 57.4 | **64.5** |
| | GSM8K | 91.1 | 90.8 | **92.6** |
| **长上下文** | LongBench-V2 | 40.2 | 44.7 | **51.5** |

> 关键发现：Flash-Base 仅 13B 激活参数量（V3.2 为 37B），却在大多数 benchmark 上超越 V3.2-Base，证明了架构创新的效率提升。

### DeepSeek-V4-Pro-Max vs 闭源模型（表 6）

| 基准 | 指标 | Opus 4.6 | GPT-5.4 | Gemini-3.1-Pro | V4-Pro-Max |
|------|------|----------|---------|----------------|------------|
| MMLU-Pro | EM | **89.1** | 87.5 | 91.0 | 87.5 |
| SimpleQA-Verified | Pass@1 | 46.2 | 45.3 | **75.6** | 57.9 |
| Chinese-SimpleQA | Pass@1 | 76.4 | 76.8 | **85.9** | 84.4 |
| GPQA Diamond | Pass@1 | 91.3 | 93.0 | **94.3** | 90.1 |
| HLE | Pass@1 | 40.0 | 39.8 | **44.4** | 37.7 |
| LiveCodeBench | Pass@1 | 88.8 | - | 91.7 | **93.5** |
| Codeforces | Rating | - | 3168 | 3052 | **3206** |
| HMMT 2026 Feb | Pass@1 | 96.2 | **97.7** | 94.7 | 95.2 |
| IMOAnswerBench | Pass@1 | 75.3 | **91.4** | 81.0 | 89.8 |
| Apex Shortlist | Pass@1 | 85.9 | 78.1 | 89.1 | **90.2** |
| MRCR 1M | MMR | **92.9** | - | 76.3 | 83.5 |
| CorpusQA 1M | ACC | **71.7** | - | 53.8 | 62.0 |
| SWE Verified | Resolved | **80.8** | - | 80.6 | 80.6 |
| SWE Pro | Resolved | 57.3 | **57.7** | 54.2 | 55.4 |
| BrowseComp | Pass@1 | 83.7 | 82.7 | **85.9** | 83.4 |

> 论文核心 claim：**DeepSeek-V4-Pro-Max 重新定义了开放模型 SOTA**，在知识基准上大幅超越开源竞品，推理性能接近前沿闭源模型（落后约 3-6 个月），在 Codeforces 上排名第 23（人类选手）。

### 推理 effort 模式（表 7）

三种模式：Non-think（快速直觉）、Think High（逻辑分析）、Think Max（极致推理），通过不同的长度惩罚和上下文窗口控制。

Pro-Max vs Flash-Max 在 HLE 上：37.7% vs 34.8%；LiveCodeBench：93.5% vs 91.6%；Codeforces：3206 vs 3052。

### 中国写作能力

- 功能性写作 vs Gemini-3.1-Pro：整体胜率 **62.65% vs 34.10%**
- 创意写作：指令遵循胜率 **60.03%**，写作质量胜率 **77.48%**
- 在复杂指令/多轮场景中 vs Opus 4.5：胜率 **45.9% vs 52.0%**

### R&D Coding Benchmark

- DeepSeek-V4-Pro-Max：**67%** Pass Rate（vs Opus 4.5 Thinking 73%，Opus 4.6 Thinking 80%）
- 52% 内部开发者认为 V4-Pro 可作为默认编程模型，39% 倾向肯定

---

## 范式对比

### vs Gemini-3.1-Pro（Google）

| 维度 | DeepSeek-V4 | Gemini-3.1-Pro |
|------|-------------|----------------|
| 知识 | 显著落后（SimpleQA：57.9 vs 75.6） | 领先 |
| 推理 | 接近，部分领先 | 全面较强 |
| 长上下文（MRCR/CorpusQA） | **领先**（83.5 vs 76.3, 62.0 vs 53.8） | 相对落后 |
| 中文写作 | **大幅领先**（62.65% 胜率） | 风格固化 |
| 架构效率 | MoE 1.6T/49B + 混合压缩注意力 | 未公开 |

### vs GPT-5.4（OpenAI）

| 维度 | DeepSeek-V4 | GPT-5.4 |
|------|-------------|---------|
| 推理 | Codeforces 略超（3206 vs 3168），HMMT 略低（95.2 vs 97.7） | 全面领先 |
| 知识 | 全面落后 | 领先 |
| 架构 | 开源 MoE，13B/49B 激活 | 闭源 |
| 效率 | 1M 上下文 FLOPs 仅标准 attention 的 ~2% | 未公开 |

### vs Claude Opus 4.5/4.6（Anthropic）

| 维度 | DeepSeek-V4 | Claude Opus |
|------|-------------|-------------|
| 代码（SWE） | 80.6% vs 80.8% (Opus 4.6) | 小幅领先 |
| 长上下文 | 接近（MRCR 83.5 vs 92.9） | 显著领先 |
| 中文写作 | 中等难度更优，复杂场景略低 | 复杂场景略优 |
| 架构 | 开源 | 闭源 |

### vs Kimi K2.6 / GLM-5.1（国内开源）

DeepSeek-V4-Pro-Max 全面超越。在知识基准上优势尤为显著（SimpleQA 20+ 百分点优势）。Agent 能力接近。

### 范式差异总结

DeepSeek-V4 的差异在于**用系统级架构创新替代纯算力 scaling**——不是单纯堆参数或推 Lora/dense attention，而是通过：
1. 混合压缩注意力从根本上改变 attention 计算图
2. 全栈基础设施优化（从融合 kernel 到 KV cache 管理）
3. 领域专家 → OPD 的高效 post-training 范式

这使得它在更少的激活参数（Flash 13B vs V3.2 37B）下实现全面超越，且在 1M 上下文下比 V3.2 高效 3.7~10 倍。

---

## 可复用的工程经验

### 1. MoE 通信-计算全重叠：wave-based 细粒度 EP

核心 insight：通信时间可隐藏在 MoE 层的计算之下。在 V4-Pro 中，每个 token-expert pair 需要 6hd FLOPs，但只需 3h bytes 通信（FP8 Dispatch + BF16 Combine），**每个 GBps 带宽可隐藏 6.1 TFLOP/s 的计算**。

**实践建议**：
- 通信带宽不必无限制增加——一旦 C/B ≤ 2d（V4-Pro 为 6144 FLOPs/Byte），再扩大带宽的收益递减
- 将 experts 分成 wave，当前 wave 计算 / 下一 wave token 传输 / 已完成 expert 结果发送并发进行
- 给 GPU 厂商的建议：wave 式调度使计算、显存、网络同时高负载，需提供充足的功率余量

### 2. 确定性训练和推理全线对齐

DeepSeek-V4 实现了 training → post-training → inference 的全链路 **bitwise 对齐**。具体做法：
- 丢弃 cuBLAS（不保证 batch invariance），端到端替换为 DeepGEMM
- Attention 解码用 dual-kernel 策略：满 SM wave 用单 SM 计算 + 最后部分填充 wave 用多 SM + 分布式共享内存，累积顺序保证一致
- Backward pass 确定性：attention backward 按 SM 分配独立 buffer + 全局确定性和；MoE backward 做 token order pre-processing + rank 间 buffer 隔离
- 给 AI infra 工程师：**batch invariance 不只是 debug 工具，是让 post-training 和推理行为一致的先决条件**

### 3. TileLang + Host Codegen：kernel 开发效率与性能兼得

放弃手写数百个 Torch ATen operator，改用 TileLang DSL：
- Fusion kernel 开发周期从周级降到天级
- **Host Codegen**：将 Python 层的运行时校验移到生成的 host 代码中，CPU 端校验开销从数十~数百微秒降至 **<1 微秒每次调用**
- **Z3 SMT solver** 集成到 TileLang 代数系统，处理可变 shape tensor 的向量化等复杂优化
- 给 kernel 工程师：DSL 不是性能的敌人——在保守精度默认值下，TileLang kernel 保持与手写 CUDA 竞争力

### 4. 异构 KV cache + 磁盘存储：共享前缀复用

解决混合 attention 导致的 KV cache 碎片化：
- **State cache**：SWA 和未压缩尾部 token 按 sequence state 管理，固定大小池动态分配
- **Classical cache**：以 lcm(m, m') 为 block 大小对齐，每 block 产出 k1 个 CSA 压缩 token + k2 个 HCA 压缩 token
- **磁盘存储**：压缩 KV entries 全量存盘；SWA 按场景选策略（全缓存/周期 checkpoint/零缓存）
- 给推理部署工程师：不要假设 PagedAttention 能处理所有 attention 模式——对于混合压缩 attention，需要与 attention kernel 协同设计 cache layout

### 5. Anticipatory Routing：训练不稳定的事前预防

不是事后回滚，而是**提前干预**：
- 将路由计算延迟 Δt 步，使用历史参数 θ_{t-Δt} 做路由，当前参数 θ_t 做特征计算
- 动态触发：正常训练时不激活，检测到 loss spike 自动回滚一小段并激活，稳定后恢复
- 整体开销可忽略（动态场景下额外开销约 20% 且只有 spike 时触发）
- 给大模型训练团队：**路由机制本身是 loss spike 的放大器** —— 解耦路由网络和 backbone 网络的更新频率是一种有效的稳定策略

### 6. 全词汇表 OPD：从 token-level 近似到精确蒸馏

放弃简化的 token-level KL 损失，改用全词汇表 logit distillation：
- 使用 reverse KL 而非 forward KL，学生生成轨迹（on-policy），从教师分布中选择性学习
- 教师 hidden states 而非 logits 缓存，运行时重建，极大降低显存
- 训练样本按教师索引排序，每 mini-batch 每个教师 head 只加载一次
- 给 RLHF/post-training 工程师：**token-level 近似节省资源但引入方差，全词汇表蒸馏在足够工程优化下是可行的**，且训练更稳定

### 7. 可抢占容错 Rollout 服务

在大型 GPU 集群中抢占是常态：
- **Token 粒度 WAL**：每生成一个 token 立即追加到日志
- 被抢占时保存未完成请求的 KV cache
- 恢复时基于 WAL + KV cache 继续解码，而非从头重新生成
- 重要：**从头重新生成会引入长度偏差**——短响应更容易存活，导致模型偏向短输出
- 给 RL 训练团队：batch-invariant + deterministic kernel + WAL 三件套是实现可靠大规模 RL 训练的基础设施前提

### 8. DSec Sandbox Platform（Agent 基础设施）

- 4 种执行模式（Function Call / Container / microVM / fullVM），统一 API
- 3FS + EROFS 分层加载：基镜像只读共享，写时复制
- 轨迹日志支持 preemption-safe 恢复、fine-grained provenance、deterministic replay
- 单集群管理数十万并发 sandbox 实例
- 给 agent 训练团队：**Sandbox 不仅仅是评测环境，它是训练管线的一部分**——需要支持抢占、恢复、确定性 replay

---

## 总结

DeepSeek-V4 展示了**系统级架构创新驱动的效率革命**——不是简单地扩大模型或增加算力，而是通过重构 attention 计算图（CSA+HCA）、优化残差信息流（mHC）、改进优化器（Muon）、量化感知训练（FP4 QAT）、以及全栈基础设施优化，在 1M token 上下文中实现了与 V3.2 相比 3.7~10 倍的效率提升。

其核心启示：**当架构效率提升到一定程度，更小的激活参数（13B）可以超越更大的模型（37B V3.2），而更大的模型（49B Pro）可以在逼近闭源前沿的同时保持长上下文的实用性。** 这为 test-time scaling、long-horizon agent 和 online learning 等下一代范式铺平了道路。
