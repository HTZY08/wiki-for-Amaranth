---
title: DeepSeek-V4.1-Flash — KV Cache 压缩作为第一优化目标
date: 2026-09-17
source: "https://arxiv.org/abs/2609.19969"
---

# DeepSeek-V4.1-Flash：把 KV Cache 当成主战场

**发布日期：** 2026-09-17（arXiv v1）
**来源：** https://arxiv.org/abs/2609.19969
**工程范式：** 长程 agent 负载下，瓶颈从算力转移到存储与带宽——所以把 KV Cache 体积当作一级设计变量，用架构换显存。

## 设计哲学

论文开篇给了一个清晰的成本归因：长程 agent 让输入变得极重（input-heavy），稀疏注意力已经把长序列的**计算**成本压下去了，剩下的瓶颈是 KV cache 的**存储、复用与迁移**——HBM 容量、SSD 容量、I/O 与互联带宽。也就是说，DeepSeek 判断当下的部署成本曲线由缓存决定，不是由 FLOPs 决定。

在这个判断下，V4.1-Flash 的核心约束是"HBM 放不下、SSD 读不快、带宽不够搬"。他们的取舍很明确：放弃一部分注意力表达自由度（从 V4 的 CSA+HCA 混合改为纯 CSA2，跨层复用 KV），换取 KV 体积的 4 倍压缩；再放弃精确重建 SWA 状态（改成有界重放），换取持久化缓存再降一半。两个"放弃"换来的都是显存与磁盘，不是分数。

## 关键架构决策

- **注意力机制**：Causal Encoder-Decoder（CED）。decoder 的 global KV 由 encoder 最后一层隐状态投影得到，因此 prefill 只激活 8B、decode 激活 16B——对输入重的 agent 负载，这是把算力花在"读"而不是"重算"上。
- **KV 压缩三级路径**：CSA2 做跨层复用（global KV 与 indexer K 共享），三种静态模式 Full / Reindex / Reuse；Reuse 层连 Top-K index 一起复用，prefill 只用 15 个 kernel、decode 11 个。叠加 FP4 KV cache 后，全局 KV 降到 **890 bytes/token**，约为 V4-Flash 的 1/4（相对 V1 约 1/437）。
- **部署层**：SWA Bounded Replay——只重放最近 `n_win` 个 token 来近似重建 SWA KV，不再把 SWA cache 持久化到 SSD，持久化 KV 降到约 1/8。
- **其它架构增项**：Single-Pass mHC + Mega-mHC kernel（激活内存流量较原四 kernel 实现减半）、Engram 条件记忆模块、DSpark 投机解码（半自回归草稿 + 置信度调度验证）。
- **训练**：45T token 多模态语料；稀疏注意力从 64K 序列直接从头训，不做 dense 预热；总参 552B（backbone），1M 上下文。
- **Post-training**：论文明确说**没有算法创新**——SFT → RL → on-policy distillation，与 V4 沿用同一套；所有实质变化在数据管线（自动化合成、环境构建、逐步扩 RL 数据与 rollout）。附录 C 给了 reasoning effort 的指数 token 惩罚推导，把 effort 当作部署期的成本-质量旋钮，而不是硬 token 预算。

## 关键结果

- 单 token decode FLOPs 随上下文增长近乎恒定：4K→1M（256 倍）只涨 1/4。
- Base 模型在世界知识、推理、代码上对标 DeepSeek-V4-Pro-Base，在留出评测上高 5%–10%，而只用 1/3 总参数、1/4 激活参数。
- Agent 侧：官方称在 Terminal-Bench 2.1、DeepSWE v1.1、AutomationBench 上与闭源前沿模型同档；在需要专家级领域知识的 Terminal-Bench 4.0 上仍有差距；多模态在视觉推理与专业图表上优于 Kimi-K3，但整体与巨型闭源系统仍有明显差距。
- 具体分数本文摘要页未逐项列出，正文表格为准。

第三方评估报告（arXiv 2610.35671，评测 V4.1 Flash-1017 版本）记录了发布后一周该模型成为 OpenRouter 上使用量最高的模型、处理约 33.6 万亿 token——这属于外部观测，不是 DeepSeek 自报。

## 范式对比

同为长上下文竞赛，路线已经分叉：MiniMax M3 用 MSA 稀疏注意力算子把 1M 上下文的 per-token 计算压到上一代的 1/20；DeepSeek 则承认算力侧已有解，转身去打缓存体积与持久化层。Qwen4-Max 用 GDN+QSA 把历史压成定长状态，本质也是同一目标（降低长序列边际成本），但 Qwen 没有公开 KV 字节数。差别在于：DeepSeek 把"每 token 多少字节"变成了可对外比较的一等指标（890 B/token），这是很少见的透明度。

## 社区评价

本次检索未取得可引用的 HN / Reddit 技术讨论原文，故不转述观点。

## 可复用的工程经验

1. **先量化瓶颈再选架构**。把"每 token KV 字节数"当成与 loss 同级的指标跟踪，能在需求变化（agent 化、长输入）时第一时间发现成本重心转移。
2. **跨层复用比算子优化更容易兑现**。CSA2 的收益不依赖特定硬件特性，属于"改图就能拿"的部分，优先做。
3. **缓存精度是独立旋钮**。FP4 KV 在训练期就引入、只有边际性能损失，说明缓存精度可以和权重精度解耦下调。
4. **允许近似重建**。持久化 SWA 换重算是典型的存储-算力再平衡，只要重算量有界（`n_win`），总成本是降的。
5. **post-training 没新算法也能涨分**。数据管线与环境构建本身就是模型能力的一部分，别把"算法创新"当作唯一叙事。
