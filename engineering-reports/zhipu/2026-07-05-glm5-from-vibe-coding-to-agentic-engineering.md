---
title: GLM-5 — 从 Vibe Coding 到 Agentic Engineering
date: 2026-07-05
source: https://arxiv.org/abs/2602.15763
---

# GLM-5 — 从 Vibe Coding 到 Agentic Engineering

**发布日期：** 2026年2月（arXiv 2602.15763）
**来源：** https://arxiv.org/abs/2602.15763
**代码：** https://github.com/zai-org/GLM-5
**工程范式：** 开源 Agent 旗舰 + 异步 RL + 国产芯片全栈适配

> GLM-5（亦称 Zhipu AI / z.ai 第五代）是智谱 AI 于 2026 年 2 月发布的旗舰级开源大模型，74.4B 总参数量（40B 激活），采用 MoE 架构，在 Artificial Analysis Intelligence Index v4.0 以 50 分成为首个达到该分数的开源模型。后续迭代 GLM-5.1（2026年4月）和 GLM-5.2（2026年6月，1M 上下文）进一步巩固了其在长程 Agent 任务中的领先地位。

---

## 设计哲学

### 核心约束

GLM-5 的设计围绕一个核心矛盾展开：**大模型正在从被动知识仓库转向主动问题解决者，但计算成本与真实世界（特别是复杂软件工程）的适应性成为主要瓶颈。** 论文引言明确指出："As LLMs transition from passive knowledge repositories to active problem solvers, the dual challenges of computational cost and real-world adaptability — particularly in complex software engineering — have become the primary bottlenecks."

Zhipu 的应对策略可概括为三条主线：

1. **用架构创新降低长上下文推理成本** — DSA（DeepSeek Sparse Attention）将长序列注意力计算降低约 1.5-2×，且**不损失质量**（lossless by construction），这是与线性注意力（如 Gated DeltaNet、Sliding Window Attention）方案的本质区别。
2. **用异步基础设施解锁 RL 后训练的可扩展性** — 传统同步 RL 在长程 Agent 交互中产生大量 GPU 空闲时间，异步解耦方案是唯一能支撑千级并发长轨迹 RL 训练的工程路径。
3. **从第一天起适配国产芯片全栈** — 这是 Zhipu 作为中国企业的独特战略约束：必须在华为昇腾、摩尔线程等 7 个国产芯片平台上实现完整的推理栈优化，确保在出口管制场景下的可用性。

### 放弃什么

- **放弃"更大"的朴素 scaling** — 从 GLM-4.5 的 355B→744B 只是翻倍，而非像 Kimi K2.5（1043B）那样激进。Zhipu 选择在减少层数（至 80 层）以最小化专家并行通信用开销的同时，用更高质量的数据和后训练来获得收益。
- **放弃一次性端到端训练** — 采用分阶段训练策略：Pre-training → Mid-training（4K→200K 渐进扩展）→ Post-training（Reasoning RL → Agentic RL → General RL → On-Policy Distillation），每个阶段锁定不同能力。
- **放弃完全同步的 RL 范式** — 同步 RL 的数学简洁性被放弃，换取工程上的训练吞吐量。
- **放弃 MLA 的原生实现** — 虽然在架构上选择了 MLA（Multi-latent Attention），但发现其在 Muon 优化器下不如 GQA-8，通过 Muon Split 对投影矩阵进行头部独立正交化来弥补性能差距。

---

## 关键架构决策

### 744B MoE + DSA 架构

```
GLM-5: 744B total / 40B active
├── 256 experts (top-2 routed)
├── 80 layers （从 GLM-4.5 减少）
├── DSA (DeepSeek Sparse Attention) via lightning indexer
├── MLA (Multi-Latent Attention) + Muon Split
└── MTP (Multi-Token Prediction, 3 层共享参数)
```

**架构演进关键点：**

| 对比项 | GLM-4.5 | GLM-5 |
|--------|---------|-------|
| 总参数 | 355B | 744B |
| 激活参数 | 32B | 40B |
| 专家数 | — | 256 |
| 层数 | — | 80 |
| 注意力机制 | 标准 MoE | DSA + MLA |
| 训练 tokens | 23T | 28.5T |

### DSA（DeepSeek Sparse Attention）深度解析

DSA 的核心思想是：**长上下文中约 90% 的注意力条目是冗余的。** DSA 通过一个轻量级 indexer（lightning indexer）为每个查询 token 检索 top-k 最相关的 key-value 条目，然后只在这些稀疏子集上计算注意力。

**为什么 DSA 比线性注意力（SWA、GDN 等）更好？**

论文做了一个详细的消融实验（Table 5）展示了一个清晰的精度-效率权衡层级：

- **Naive SWA Interleave**：在长上下文任务上灾难性退化（RULER@128K 下降 30.35 分）
- **Search-based SWA Pattern**：大大缩小差距，但在细粒度检索任务上仍有 5.69 分损失
- **GDN / SimpleGDN**：进一步改善，但引入了额外参数，且不可避免地丢失信息
- **DSA**：By construction 无精度损失，因为其 indexer 实现了 token 级别的稀疏化而不丢弃任何长程依赖

从工程角度看，DSA 的训练代价远低于 DeepSeek-V3.2（Zhipu 仅用了 20B tokens 的 sparse adaptation + 150B tokens 的 joint training，对比 DeepSeek 的 943.7B tokens），表明 DSA warmup 已经能保留大部分基线质量。

### Muon Split：让 MLA 追上 GQA

在 Muon 优化器下，标准 MLA（576 维 KV-cache latent）的 pre-training 性能无法匹配 GQA-8（2048 维 KV-cache）。Zhipu 的关键创新是将 MLA 的 up-projection 矩阵（W_UQ, W_UK, W_UV）按注意力头拆分为独立子矩阵，分别应用矩阵正交化，使得不同注意力头的投影权重能以不同尺度更新。这既恢复了性能，又保持了 attention logits 在 pre-training 中的稳定性，无需额外的 clipping 策略。

### 内存与并行效率的工程极值

GLM-5 报告在训练基础设施上做了大量系统级优化：

- **Flexible MTP placement**：将 MTP 输出层与主输出层共置于最后 stage 实现参数共享，减少内存压力
- **Pipeline ZeRO2 gradient sharding**：梯度分片 + 双缓冲机制，将持久性梯度内存降至每 stage 分片缓冲 + 2 个完整缓冲
- **Muon 分布式优化器的零冗余通信**：限制 all-gather 到每个 rank 拥有的参数分片，重叠本地计算与分片通信
- **Pipeline activation offloading**：在前向传播后将激活值卸载到主机内存，反向时重新加载，与 computation 重叠调度
- **Sequence-chunked output projection**：将输入序列分块计算投影和 loss，大幅降低峰值内存

### Mid-Training 的渐进式上下文扩展

```
从 4K → 32K（1T tokens）→ 128K（500B tokens）→ 200K（50B tokens）
```

GLM-5 超出 GLM-4.5 的 128K 最大长度，增加 200K 阶段。关键是，在 128K 阶段训练后的数据多样性提升本身就能改善 128K 窗口内的性能，而后续的 200K 阶段在此基础上进一步巩固。

### 量化感知训练（QAT）

在 SFT 阶段引入 INT4 量化感知训练，开发了同时适用于训练和离线量化的 kernel，确保 bitwise-identical 行为。对 MoE expert 采用 W4A8，attention 和 MLP 采用 W8A8。

### On-Policy Cross-Stage Distillation

多阶段 RL 的固有问题：后续阶段的优化可能破坏前一阶段已获得的能力。Zhipu 的方案是在最终阶段执行 on-policy distillation — 前序阶段（Reasoning RL、General RL）的最终 checkpoint 作为 teacher，GRPO group size 设为 1（因为 advantage 直接来自与 teacher 的差距），batch size 1024。

---

## 后训练管线：异步 RL 的基础设施革命

这是 GLM-5 最核心的工程贡献，也是其真正与 vibe coding 分道扬镳的地方。

### 三阶段 RL 管线

```
Base Model
    ↓
SFT (Interleaved Thinking + Preserved Thinking)
    ↓
Reasoning RL (GRPO + IcePop + 4 domain mixed: math/science/code/TIR)
    ↓
Agentic RL (异步、解耦、多任务)
    ↓
General RL (三大维度 + 混合奖励 + 人类风格锚点)
    ↓
On-Policy Cross-Stage Distillation
```

### 异步 RL 基础设施（slime 框架）

**为什么异步是必要的？**

在长程 Agent 任务中，一个 rollout 可能持续数分钟到数十分钟。传统同步 RL 中，所有 GPU 需要等待最慢的轨迹完成才能进入下一轮训练，导致大量 GPU 空闲时间（论文描述为 "severe GPU idle time during long-horizon agent rollouts"）。

**异步 RL 的核心设计：**

```
                        ┌─────────────────┐
                        │  Multi-Task      │
                        │  Rollout         │
                        │  Orchestrator    │
                        └────────┬────────┘
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
              ┌──────────┐ ┌──────────┐ ┌──────────┐
              │ SWE Task │ │ Terminal│ │ Search   │
              │ Service  │ │ Service │ │ Service  │
              └──────────┘ └──────────┘ └──────────┘
                    │            │            │
                    └────────────┼────────────┘
                                 ▼
                         ┌──────────────┐
                         │   slime      │
                         │  Train Engine│
                         └──────────────┘
```

1. **解耦训练引擎和推理引擎**：放在不同 GPU 设备上。推理引擎持续生成轨迹，达到预定义阈值后发送给训练引擎。
2. **周期性权重同步**：训练引擎每 K 次梯度更新后推送新权重回推理引擎。
3. **优化器重置**：每次推理引擎权重更新后重置优化器 — 因为异步意味着 weight update 考虑的是变化后的优化问题。
4. **跨任务统一消息格式**：所有 agentic 任务（SWE、Terminal、Search）的轨迹统一转为 message-list 表示，支持联合训练。

**稳定异步训练的三个关键技术：**

1. **Token-in-Token-out (TITO) Gateway**：消除 re-tokenization 导致的边界不匹配。Rollout 产生的 token IDs 直接传给训练引擎，避免 text-in-text-out 的损失性 round-trip。
2. **Direct Double-sided Importance Sampling**：由于异步环境下精确跟踪 πθold 的 log-probability 不可能（需维护大量 checkpoint 历史），直接复用 rollout log-probabilities 作为 behavior proxy，用双面 token-level 裁剪 [1-ϵ_l, 1+ϵ_h] 控制 off-policy bias。
3. **Staleness-based 丢弃 + 环境失败过滤**：丢弃与当前策略版本差距超过 τ 的轨迹；排除环境崩溃导致的失败样本。

**规模数据：**
- 超 10,000 个真实 SWE 验证环境（9 种编程语言）
- 上千个 Terminal 任务（Docker + Harbor 格式）
- 多跳搜索任务（200 万+ 网页的知识图谱）

### Agentic RL 的 DP-aware Routing

针对 MoE 模型的长上下文多轮 Agent 推理，设计了一种保持 KV-cache 局部性的路由机制：同一 agent 实例的所有请求被一致哈希路由到同一个 DP rank，避免跨 rank 的缓存丢失。结合轻量级动态负载均衡，使得 prefill 成本与增量 token 成正比而非总上下文长度。

### General RL 的混合奖励系统

三个奖励信号类型的组合：

| 类型 | 优势 | 劣势 |
|------|------|------|
| Rule-based | 精确、可解释 | 仅适用于确定性规则 |
| Outcome Reward Model | 低方差、训练高效 | 易受 reward hacking |
| Generative Reward Model | 鲁棒、难以被 exploit | 高方差 |

三个优化维度：**基础正确性**（指令遵循、逻辑一致、事实准确）→ **情商**（共情、自然）→ **任务特定质量**（写作、翻译、角色扮演等）。

### Pony Alpha 匿名发布实验

论文最有趣的部分：Zhipu 将 GLM-5 匿名以 "Pony Alpha" 之名发布在 OpenRouter 上。社区猜测分布为 25% Claude Sonnet 5、20% DeepSeek、10% Grok。这"有效消除了对中国 LLM 能否在 frontier 水平竞争的所有质疑"。

---

## 关键结果

### 综合排名

- **Artificial Analysis Intelligence Index v4.0**: 50（开源权重新纪录，从 GLM-4.7 的 42 跃升 8 分，首次开源模型达到 50）
- **LMArena Text Arena**: #1 开源模型
- **LMArena Code Arena**: #1 开源模型
- 与 Claude Opus 4.5 和 GPT-5.2 (xhigh) 可比

### 与开源竞品的对比

| Benchmark | GLM-5 | DeepSeek-V3.2 | Kimi K2.5 | GLM-4.7 |
|-----------|-------|---------------|-----------|---------|
| HLE (w/ Tools) | 50.4 | 40.8 | 51.8 | 42.8 |
| SWE-bench Verified | 77.8 | 73.1 | 76.8 | 73.8 |
| SWE-bench Multilingual | **73.3** | 70.2 | 73.0 | 66.7 |
| Terminal-Bench 2.0† | **60.7** | 39.3 | 50.8 | 41.0 |
| BrowseComp (w/ CM) | **75.9** | 67.6 | 74.9 | 67.5 |
| BrowseComp-ZH | **72.7** | 65.0 | 62.3 | 66.6 |
| MCP-Atlas | **67.8** | 62.2 | 63.8 | 52.0 |
| Vending Bench 2 | **$4,432** | $1,034 | $1,198 | $2,377 |

GLM-5 在所有 agentic 和 coding 基准上均全面领先于 DeepSeek-V3.2，尤其在 BrowseComp（+8.3）和 MCP-Atlas（+5.6）拉开显著差距。与 Kimi K2.5 相比，在工具使用和长程任务上更具优势。

### CC-Bench-V2 上的真实工程能力

这是 Zhipu 自建的评价套件，反映真实端到端工程能力：

| 类别 | 指标 | GLM-5 | GLM-4.7 | Claude Opus 4.5 |
|------|------|-------|---------|----------------|
| Frontend (HTML ISR) | ISR | 38.9 | 35.4 | **52.2** |
| Frontend (React ISR) | ISR | 34.6 | 17.2 | **39.7** |
| Frontend (Vue ISR) | ISR | 32.7 | 24.5 | **46.9** |
| Backend | Pass@1 | **25.8** | 19.6 | 26.9* |
| Repo Exploration | Pass@1 | **65.6** | 47.8 | 64.5 |
| Chained Tasks | Pass@1 | 52.3 | 43.0 | **61.6** |

*Claude Opus 4.5's backend score of 26.9 is marginally higher

### SWE-rebench 上的泛化能力

在持续采集最新 GitHub issue 的 SWE-rebench 上，GLM-5 以 42.1% 的 Resolved Rate 稳居开源模型前列（对比 Claude Opus 4.5 的 43.8% 和 GPT-5.2 xhigh 的 51.7%），证明其在静态 benchmark 上的表现不是过拟合。

---

## 范式对比

### 与 DeepSeek 的差异

| 维度 | GLM-5 | DeepSeek-V3.2 |
|------|-------|---------------|
| 架构创新 | 采用 DSA（DeepSeek 的发明，但首次在后训练中大规模验证） | DSA 的原创者 |
| 后训练重点 | Agentic RL 是第一优先级，异步实现 | 更传统的同步 RL |
| 上下文扩展 | 4K→32K→128K→200K 三阶段 | 类似方案但规模不同 |
| 国产芯片适配 | **7 个平台全栈适配** | 主要在英伟达生态 |
| 开源许可 | MIT（完全开放） | MIT |
| 对比优势 | 编码 agent 和长程任务 | 推理和数学任务 |

GLM-5 最关键的差异是**将 Agent 能力放在后训练管线的最中心**。DeepSeek 的 RL 管线也包含 agentic 组件，但 Zhipu 是第一个将异步 Agentic RL 作为基础设施一级工程设计、并在 1 万+ 真实 SWE 环境上大规模验证的。

### 与 Kimi K2.5 的差异

Kimi K2.5 以 1043B 总参数（32B 激活）更大，但 GLM-5 在 Vending Bench 2（$4,432 vs $1,198）、Terminal-Bench 2.0（60.7 vs 50.8）、MCP-Atlas（67.8 vs 63.8）上全面胜出，表明 **主动参数效率与后训练策略比原始总参数量更重要**。

### 与 Qwen 的差异

Qwen 系列更强调通用能力和小模型效率（高压缩比的蒸馏产品线），而 GLM-5 的定位非常明确：**旗舰开源 Agent 模型**。在 "Chatbot Arena" 之外，GLM-5 追求的是 Agent Arena 的全面领先。

### "Agentic Engineering" vs "Vibe Coding" 的范式解读

```
Vibe Coding（GLM-4.5 时代）        →    Agentic Engineering（GLM-5 时代）
─────────────────────────               ─────────────────────────────
Human prompt + AI write code           AI plans, implements, iterates autonomously
单次、短上下文交互                          长程、多轮、文件间依赖
静态 benchmark（SWE-bench）                动态基准（CC-Bench-V2、long-horizon chained tasks）
同步 RL（训练/推理耦合）                     异步 RL（解耦、无同步瓶颈）
SFT + 少量 RL                           多阶段 RL（Reasoning→Agentic→General→Distillation）
单平台推理（NV GPU）                       全栈国产芯片适配（7 平台）
```

---

## 可复用的工程经验

### 1. 异步 RL 是 Agent 训练的可扩展性前提

任何想要训练长程 Agent 模型的团队，都必须从同步 RL 中走出来。GLM-5 的经验表明，异步设计不仅仅是工程优化，而是**训练信号质量本身**的提升机制：只有当 rollout 持续不断地产生轨迹且训练引擎永不等待时，才能在合理时间内完成百万级轨迹的探索。

**可复用的组件：**
- TITO Gateway（token 级精确轨迹传递）
- Direct Double-sided Importance Sampling（简化 off-policy correction）
- DP-aware routing for KV-cache locality（长上下文推理的关键加速）

### 2. DSA 比线性注意力更适合 Agent 模型

长上下文场景下，线性注意力（SWA、GDN 等）会引入不可逆的信息损失。DSA 的 lossless-by-construction 特性意味着它可以应用于所有层而不损失质量。对于需要保持细粒度检索能力（如代码查找、长文档定位）的 Agent 模型，这是决定性优势。

### 3. 分阶段后训练是抗遗忘的关键

Reasoning → Agentic → General → Distillation 的顺序不是偶然的。先锁定推理能力（最脆弱、最容易被后续训练破坏），再特化 Agent 能力，最后用 General RL 和 Distillation 恢复广度。On-Policy Cross-Stage Distillation 是多阶段训练防遗忘的最佳实践。

### 4. Interleaved Thinking + Preserved Thinking 的设计模式

GLM-5 在 SFT 中引入了三种思考模式：
- **Interleaved Thinking**：每次响应和工具调用前思考，提升指令遵循和质量
- **Preserved Thinking**：在多轮编码 agent 场景中自动保留所有思考块，避免信息丢失
- **Turn-level Thinking**：每一轮控制是否启用思考

这种设计使得同一个模型既能以低延迟执行简单任务（关闭思考），又能以高精度处理复杂任务（深度链式思考）。

### 5. 消融实验的设计哲学

论文在注意力变体的消融实验（Table 5）上做出了业界标杆级的严谨性：不只是报告 DSA 的结果，而是系统性地对比了 SWA Interleave、SWA Search-based、GDN、SimpleGDN 四种替代方案，在 RULER、MRCR、HELMET-ICL、RepoQA 四个基准上做完整比较，清晰展示效率-精度权衡的全景图。

### 6. 环境构建的规模化工程

超过 1 万个可验证 SWE 环境的构建不是一个副产物，而是核心基础设施：
- 基于真实 Issue-PR 对的自动环境构建（RepoLaunch + Docker）
- Terminal 任务的迭代式合成管线（seed data → draft → 构建 → 验证）
- Search 任务的 Web Knowledge Graph 构建（200 万+ 网页 → 多跳 QA）

### 7. "Pony Alpha" 验证方法

匿名发布不仅是营销策略，更是一种有效的**模型验证方法论**。在社区不知道模型来源的情况下获得真实、无偏见的反馈，特别是在编码和 agentic 工作流中的实际表现。

### 8. 国产芯片全栈适配的模式

从底层 kernel（Lightning Indexer、Sparse Flash Attention、MLAPO）到上层推理引擎（vLLM-Ascend、SGLang）的自底向上优化，使得单台国产芯片节点达到接近双卡国际集群的性能。对于面临出口管制约束的团队，这是完整的参考路线。

---

## 后续迭代：GLM-5.1 / GLM-5.2

- **GLM-5.1**（2026年4月）：改进长程编码任务，在 VectorDBBench、CyberGym 等开放式优化任务上表现提升
- **GLM-5.2**（2026年6月）：1M token 稳定上下文。架构上引入 **IndexShare**（每 4 层共享一个 indexer，1M 上下文下 per-token FLOPs 降低 2.9×），改进 MTP 层的 KVShare。在 FrontierSWE 上仅次于 Claude Opus 4.8，在 PostTrainBench 上超过 GPT-5.5。支持灵活 effort level 控制

---

## 参考文献

- GLM-5 Technical Report: https://arxiv.org/abs/2602.15763
- GLM-5 blog: https://z.ai/blog/glm-5
- GLM-5.1 blog: https://z.ai/blog/glm-5.1
- GLM-5.2 blog: https://z.ai/blog/glm-5.2
- Code/Models: https://github.com/zai-org/GLM-5
- HuggingFace: https://huggingface.co/zai-org/GLM-5
