---
title: MiMo-V2.6 — 把 RL 算力当主变量的全模态家族
date: 2026-10-08
source: "https://arxiv.org/abs/2610.11959"
---

# MiMo-V2.6：RL 三条轴一起扩

**发布日期：** 2026-10-08（arXiv v1）
**来源：** https://arxiv.org/abs/2610.11959
**工程范式：** 以"递归自我改进"为目标函数，把 RL 算力拆成 batch/吞吐、环境多样性、grader 算力三条轴同时扩，并用开源配套降低复现门槛。

## 设计哲学

MiMo-V2.6 的立论很直接：要走向 RSI（递归自我改进），就需要 agent 在环境里持续探索并拿到反馈；于是**扩展复杂 agent 任务上的 RL** 是最具体的路径。为此先筑两层地基——预训练打知识底、agent-centric mid-training 扩大探索空间——再谈 RL 规模化。

论文最有价值的部分是它对"扩 RL 到底扩什么"的回答：

1. **扩 batch 与吞吐**：完全异步训练，每步消耗 1,568 个样本、2.7–3.7B token，上下文最长 1M；
2. **扩环境**：代码、通用、视觉、网络安全的混合域，且**同一任务换 harness**；
3. **扩 grader 算力**：不满足于测试用例二值奖励，做 groupwise agentic grading，把组内解的质量差异转成更细的信号。

稳定性代价也被正面处理：冻结 MoE router，并建立多层奖励作弊防御。

## 关键架构决策

- **两档模型**：

| | MiMo-V2.6-Flash | MiMo-V2.6-Pro |
| --- | --- | --- |
| 总参数 | 310B | 1.02T |
| 激活参数 | 15B | 42B |
| 层数（总/SWA/GA） | 48 / 39 / 9 | 70 / 60 / 10 |
| Hidden | 4096 | 6144 |
| 专家（总/激活） | 256 / 8 | 384 / 8 |
| SWA 窗口 | 128 | 128 |

- **文本骨干**：hybrid SWA + Global Attention 交替；每个 hybrid block 为 N 个 SWA block 后接 1 个 GA block；首个 Transformer block 例外（全局注意力 + dense FFN，稳定早期表示）；SWA 与 GA 都用**无共享专家**的稀疏 MoE FFN。MTP 用于预训练。
- **视觉**：MiMo-ViT 用 sink-augmented SWA，局部 SWA 层在行主序/列主序间交替以沿两个空间轴传播信息，周期性插入 GA；<b>4T+ 图像 token</b> 预训练，仅用交叉熵、不加对比学习，且 LLM 保持可训练以给 ViT 提供稳定梯度。
- **音频**：两段式——Audio Tokenizer（因果混合注意力，帧率降到 25Hz，20 层 RVQ、每帧 20 token，2000 万小时音频训练）+ Audio Patch Encoder（4 帧一组，序列率降到 6.25Hz）。
- **投机解码**：独立 5 层 SWA-only 投机解码器（窗口 1024），不依赖 MTP 做草稿。
- **RL 机制**：Groupwise Reward Synthesis（GRS）+ Groupwise Advantage Redistribution（GAR）；采样上做 sample mixing + dynamic sampling + partial rollout 以稳定每任务样本配比；训练与推理引擎在 MoE 路由与 top-p 候选集上对齐。

## 关键结果

- Figure 1 报告：Pro 与 Flash 在 DeepSWE、AutomationBench、MiMo Visual Coding、MiMo Cyber Bench 上的分数随 RL 训练步数**持续上升**，且跨域同时成立。
- 官方给出的编码跨 harness 表（Table 7）显示：同一模型在 7 种 harness 上的均值被单独列出——这与 DeepMind 的 SWE-sweep 双 harness 数据指向同一件事：harness 是能力的一部分。具体分数见原文表格。
- 开源配套：MiMo-V2.6-Distill-Qwen-9B（轻量验证模型）、多域带验证器的任务环境、端到端 RL 框架、可组合 mini-harness；9B 蒸馏模型上验证了跨任务、跨 harness 的稳定 RL 增益。

## 范式对比

与 Kimi K3.1 Pro 相比，两家都在堆 RL 算力，但小米把"环境多样性"和"grader 精度"显式列为主轴，并且**开源数据与环境**；Kimi 侧重 RL 吞吐与跨域联合。与 GLM-5.3 相比，z.ai 走"环境合成 + 二值验证器"，小米走"组内相对评分"——后者更适合没有唯一正确答案的长程任务，前者更适合可判定的编码/漏洞任务。

## 社区评价

本次检索未取得可引用的 HN / Reddit 技术讨论，故不转述。

## 可复用的工程经验

1. **RL 扩展要三条轴一起动**。只扩 batch 不扩环境多样性，模型会在同一批任务上过拟合。
2. **换 harness 训练**：同一任务不同脚手架能提升泛化，这比多造 10% 环境更便宜。
3. **组内相对评分**解决"全过测试用例都一样分"的奖励稀疏问题（GRS/GAR）。
4. **冻结 router** 是大规模 RL 稳定性的低成本手段，代价是路由不再适配新分布。
5. **把训练环境与 RL 框架开源**（含可复现的蒸馏基线），既降复现门槛，也给自己造了一个外部校验器。
