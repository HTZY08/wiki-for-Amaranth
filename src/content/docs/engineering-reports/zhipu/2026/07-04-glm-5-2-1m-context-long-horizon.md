---
title: GLM-5.2 — 1M上下文开放权重的长程任务旗舰
date: 2026-07-04
source: https://z.ai/blog/glm-5.2
---

# GLM-5.2：开放式长程任务旗舰模型

**发布日期：** 2026-06-13（模型发布）/ 2026-06-16（技术博客+完整分数卡）
**来源：** [Z.ai 官方博客](https://z.ai/blog/glm-5.2)
**工程范式：** 用 DSA + IndexShare 稀疏注意力实现 1M 工程可用上下文，用 slime 框架做大规模 Agentic RL，用 MTP + 拒绝采样做投机解码加速

## 设计哲学

GLM-5.2 的核心约束是：**长程任务（long-horizon task）的工程可用性**。不是"能接受 1M token"，而是"在 1M token 的真实 coding-agent 轨迹中保持质量"。为此 Z.ai 做了三个关键选择：

1. **优先 long-context 训练覆盖真实工程场景**——大规模实现、自动化研究、性能优化、复杂调试，而非仅理论长上下文评估。
2. **用 IndexShare 降低 DSA（Dynamic Sparse Attention）的计算代价**——每 4 层共享一个 lightweight indexer，而不是每层独立。
3. **放弃美团/字节式的封闭生态，坚持 MIT 开源**——无区域限制、完全开放权重的纯开放策略。

放弃的是：在标准短上下文 benchmark 上堆极致数字。GLM-5.2 在这些 benchmark 上并未领先封闭源旗舰，但在长程编码任务上追平或接近了 Opus 4.8。

## 关键架构决策

### 注意力机制：DSA + IndexShare

- 基础注意力沿用 DSA（Dynamic Sparse Attention），每 4 层 Transformer 共享一个 lightweight indexer
- indexer 放在第 1 层，topk indices 供后续 3 层复用
- 减少了 3/4 层的 indexer dot product 和 topk 计算
- 从 128K 序列长度的 mid-training 阶段开始训练 IndexShare，优于 GLM-5.1 的长上下文 benchmark 且计算更少
- 1M 上下文时 per-token FLOPs 减少 2.9×

### MoE 设计

具体专家数/粒度/路由细节未在博客中完全披露。GLM-5 系列已知为 745B 总参数、256 专家、8 激活（5.9% sparsity）、44B 活跃参数。GLM-5.2 延续此架构但具体参数未更新。

### 训练策略：slime 框架 + OPD（On-Policy Distillation）

- slime 框架支持从训练到大规模推理 rollout 的统一基础设施
- 支持 white-box rollout、black-box rollout、compact trajectory、sub-agent workflow 多种模式
- GLM-5.2 的 post-training 使用 slime 进行并行 OPD 训练，合并了十多个 expert 模型
- 整个 OPD 训练约耗时 2 天
- 支持 KV-cache FP8

### 推理优化

- **MTP 投机解码改进**：
  - IndexShare + KV Share：将 IndexShare 应用到 MTP layer，不同 MTP step 间复用 topk indices
  - 拒绝采样（Rejection Sampling）：消除训练-推理不一致
  - End-to-end TV loss 训练
  - 最终 MTP layer acceptance length 从 4.56 提升至 5.47（+20%）
- **推理引擎三层优化**：
  1. 基于 LayerSplit 的细粒度内存管理和并行化策略，增加 KV-cache 容量
  2. 优化随 context 长度增长而成本增长的 kernel，与 cache transfer pipeline 协调
  3. CPU 端 cache 管理、请求调度、运行时执行路径优化

### Post-training：Critic-based PPO + Anti-hacking

- 从 group-wise 优化转向 critic-based PPO，从单个 rollout 学习
- critic 估计 token-level advantage，而非 group-relative 比较
- 引入 compaction 机制——超长轨迹拆分为多个 sub-traces 后，全部作为可训练轨迹纳入
- 使用 token-level loss 处理长度不平衡
- Anti-hacking：对 NL2Repo 等 benchmark 使用规则 + LLM 判断防止恶意行为（如 unauthorized pip 或 curl 操作）

### 推理 Effort 控制

- 引入 effort level 控制，用户可在 Max 模式下分配更多计算以提升困难任务性能
- Max 模式进一步扩展模型的编码能力，在同 token 预算下表现介于 Claude Opus 4.7 和 Opus 4.8 之间

## 关键结果

### 长程编码 benchmark

| Benchmark | GLM-5.2 | Opus 4.8 | GPT-5.5 | Opus 4.7 |
|-----------|---------|----------|---------|----------|
| FrontierSWE（1M context） | — | +1%（领先 GLM-5.2 1%） | -1%（落后 GLM-5.2 1%） | +11%（领先 GLM-5.2 11%） |
| PostTrainBench | — | 第一 | 被 GLM-5.2 超越 | 被 GLM-5.2 超越 |
| SWE-Marathon | — | +13% | — | — |
| Terminal-Bench 2.1 | **81.0** | **85.0** | — | — |
| SWE-bench Pro | **62.1** | — | — | — |

注：GLM-5.1 对应 Terminal-Bench 2.1 得分 63.5、SWE-bench Pro 得分 58.4。

### 其他指标

- FrontierSWE 使用 1M context length、max effort level、128K max output tokens
- SWE-Marathon 覆盖构建编译器、优化 kernel、开发生产级服务
- 在所有三个长程 benchmark（FrontierSWE、PostTrainBench、SWE-Marathon）上，GLM-5.2 是排名最高的开源模型

## 范式对比

### vs DeepSeek-V4

- DeepSeek-V4 使用 Heavily Compressed Attention（HCA），128:1 压缩比
- GLM-5.2 使用 DSA + IndexShare 做 blockwise sparse，而非压缩
- 两者都追求长上下文效率，但路线不同：DeepSeek 压缩 KV，Z.ai 稀疏化注意力

### vs OpenAI GPT-5.5/5.6

- GLM-5.2 在 PostTrainBench 上超过 GPT-5.5
- 在 FrontierSWE 上领先 GPT-5.5 1%
- 但 Terminal-Bench 2.1 上 81.0 vs Sol 的 91.91%，仍有差距

### vs 其他开源

- MIT 许可证，完全开源——与 Qwen、DeepSeek 的开源策略一致
- 在长程编码任务上，GLM-5.2 是所有开源模型中排名最高的

## 社区评价

- 发布时正值美国商务部下架 Claude Fable 5 / Mythos 5，GLM-5.2 借此窗口成为非美国开发者可用的最强开源编码模型
- 开源社区对 1M 上下文 + MIT 许可反应积极
- 第三方评测（LMArena）中，GLM-5.2 在 frontend coding 类别中排名第一（排除已下架的 Fable 模型）
- 有开发者指出尽管 1M 上下文理论上可用，实际推理中 token 开销仍然显著

## 可复用的工程经验

1. **IndexShare 模式**：当稀疏注意力的 indexer 开销成为瓶颈时，跨层共享 indexer 是低成本的优化手段——减少 3/4 的 indexer 计算而无精度损失。
2. **MTP + 拒绝采样**：通过解决训练-推理分布不一致（KV cache 混合问题），可大幅提升 speculative decoding 的 acceptance length。
3. **Critic-based PPO 替代 Group RL**：对于超长轨迹场景（单个 rollout 可产生数千 tokens），group-wise 优化不如 token-level critic 的 PPO 稳定。
4. **训练-推理闭环**：slime 框架的设计理念——RL rollout 中积累的配置经验、调度策略和优化路径可直接复用到生产 serving 阶段。
5. **Effort level 控制**：对不同难度任务使用不同的推理计算量分配，比单一模型更高效——用户自行在延迟和质量之间做 trade-off。
