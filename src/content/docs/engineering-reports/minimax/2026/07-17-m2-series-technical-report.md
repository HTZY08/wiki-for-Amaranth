---
title: MiniMax-M2 系列技术报告 — 小激活量 + Agent 原生强化学习 + 自我进化萌芽
date: 2026-07-17
source: https://arxiv.org/abs/2605.26494
---

# MiniMax-M2 系列技术报告

**发布日期：** 2026-05-28（arXiv 提交）
**来源：** https://arxiv.org/abs/2605.26494
**工程范式：** 小激活量 + 硬核系统协同设计——"mini activations, max real-world intelligence"。M2 系列涵盖 M2 → M2.5 → M2.7，核心创新在 agent 数据管线、Forge RL 系统和 M2.7 的自我进化启动。

> 本文分析覆盖完整的 M2 系列技术报告（arXiv:2605.26494，207 位作者，~100K 字符）。此前已有 M2.7 专篇分析（`01-15-minimax-m2-7.md`），本文补充完整的架构决策数据、Forge 系统设计和三阶段演进过程。

## 设计哲学

MiniMax 的核心约束是**激活参数量的预算**——M2 只有 9.8B 激活参数（DeepSeek-V4-Pro 的 1/5，GPT-5 级别的 ~1/10）。这个约束倒逼出三个设计选择：

1. **数据质量和奖赏信号比数量更重要**——agent 数据管线强调每条轨迹的可执行验证和 artifact-aligned reward
2. **RL 系统必须 agent-native**——传统 RL 框架无法处理数万步的 agent 轨迹，需要从零搭建
3. **最终目标是自我进化**——模型能自主改进自身训练和 scaffold

M2 系列最重要的选择是**放弃混合注意力**。这与 DeepSeek V4（CSA+HCA）、Qwen 3.5（Hybrid SWA）等主流方向截然相反。

## 关键架构决策

### 注意力：Full Multi-Head Attention（全注意力）

MiniMax 做了异常详尽的 ablation 来证明为什么要全注意力：

**混合 SWA 的实验耗尽多种配置：**
- 不同 SWA/full attention 比例
- 不同 RoPE 设置
- Intra-layer 和 inter-layer 混合方案
- 分析 attention pattern（induction heads, retrieval heads）
- 添加 sink tokens

**预训练阶段结果：** 所有 SWA 变体在 retrieval、multi-hop reasoning、in-context learning 上退化（见下表）：

| 指标 | Full Attention | Hybrid SWA |
|-----|---------------|------------|
| HELMET ICL | 75.8 | 72.7 |
| RULER 128K CWE | 90.0 | 72.0 |
| RULER 128K MQ | 99.0 | 93.0 |
| MTOB K-e Bleurt | 60.0 | 45.0 |

**SFT 后差距扩大：** 在 >32K 上下文的长任务上 SWA 显著更差。在 <32K 的短任务上两者接近，甚至 SWA 在 IFBench/XBench 上略好。

**结论：** MiniMax 认为 full attention 仍然是当前生产环境的更稳妥选择，但承认 sub-quadratic attention 是未来方向。

### MoE：256 Fine-Grained Experts + Sigmoid Gating

- **256 个细粒度专家**（vs 常规 32-64），每 token 激活 8 个
- **Sigmoid gating** 替代 softmax top-k——每个专家独立激活分数，消除 zero-sum 约束
- **Expert bias**：可学习的偏置项，减少 auxiliary loss 依赖
- Ablation 证实 fine-grained experts + MTP 一致提升性能（MATH +4.5%, HumanEval +2.8%）

### MTP（Multi-Token Prediction）

- K=1（预测下一 token），遵循 DeepSeek-V3 设计
- MTP loss weight：初始 0.3，decay 阶段降为 0.1
- 推理时通过 weight copy 扩展为 speculative decoding draft path
- Ablation：MTP 一致提升性能，推理类任务提升最大

### 模型规格

| 属性 | M2 |
|------|----|
| 总参数量 | 229.9B |
| 激活参数量 | 9.8B |
| Transformer 层数 | 62 |
| 隐藏维度 | 3,072 |
| 词表大小 | 200,064 |
| Q head / KV head | 48 / 8（GQA） |
| 细粒度专家数 | 256 |
| 每 token 激活专家 | 8 |
| 预训练 tokens | 29.2T |
| 原生上下文长度 | 192K |

### Forge：Agent-Native RL 系统

这是 M2 系列最大的工程创新——专门为 agent 长轨迹训练的 RL 系统：

**核心设计：**
- **Training-Inference-Agent 解耦：** 支持 white-box（可反向传播）和 black-box（API only）agent 在统一训练循环中
- **Windowed-FIFO Scheduling：** 吸收轨迹长度方差——长轨迹和短轨迹不会互相阻塞
- **Prefix-Tree Merging：** 共享前缀的轨迹合并计算，避免重复 inference
- **推理 kernel 与部署栈协同设计：** 训练时的 inference 直接用生产级推理栈
- **奖赏系统：** 每条 agent 轨迹绑定可执行 workspace + artifact-aligned reward

### Agent 数据管线

M2 系列的能力提升主要来自数据，而非架构变更：

- **Agentic coding 数据：** 大规模可验证的编码轨迹，在可执行 sandbox 中运行并验证
- **Agentic cowork 数据：** 协同工作场景（浏览、搜索、办公工具操作）
- **推理/知识数据：** 标准 SFT + RL 数据
- 核心原则：**奖赏信号的质量和可信度 > 轨迹数量**

### Self-Evolution（M2.7 创新）

M2.7 首次实现了 self-evolution 的"操作化形式"：
- 自主调试训练运行（在自己基础设施上排查失败原因）
- 自主修改自身 agent scaffold（跨任务和实验）
- 在 MLE Bench Lite 上做多轮 self-improvement
- 最佳运行 22 个竞赛中获得 9 金 5 银 1 铜，平均奖牌率 66.6%
- 与 Gemini 3.1 Pro 打平

关键定性观察：M2.7 愿意调试自己的训练 scaffold、修改配置文件、迭代数百轮——形成了"小激活量→最大真实世界智能"的闭环。

## 关键结果

### M2.7 Benchmark 核心数字

**Agentic Coding：**
- SWE-bench Pro: 56.2
- SWE-bench Multilingual: 76.5
- Multi-SWE-bench: 52.7
- Terminal-Bench 2.0: 57.0

**Agentic Cowork：**
- MM Claw: 62.7
- BrowseComp: 77.8
- GDPval-AA: 50.0
- Toolathlon: 46.3

**推理与知识：**
- AIME 2026: 94.2
- GPQA-Diamond: 89.8

### 成本效率

M2.7 在 Kilo Code 测试中交付了约 Claude Opus 4.6 的 90% 质量，成本仅为 7%。这是 "mini activations" 路线的核心价值主张。

## 范式对比

| 维度 | MiniMax M2.7 | DeepSeek V4 Pro | Qwen3.5-Coder-Next | Claude Opus 4.5 |
|------|-------------|-----------------|-------------------|-----------------|
| 激活参数 | **9.8B** | 49B | ~35B | 未披露（估计 >100B） |
| 注意力 | Full Attention | CSA+HCA | Hybrid SWA | 未披露 |
| 专家数 | 256 | 384 | 未披露 | 未披露 |
| 预训练 tokens | 29.2T | 33T | 未披露 | 未披露 |
| RL 系统 | **Forge（Agent-Native）** | 标准 GRPO | 标准 RL | Constitutional AI |
| 自我进化 | ✅ **M2.7 首次实现** | ❌ | ❌ | ❌ |
| 注意力选择依据 | **详尽 ablation 决定不换** | 主动性架构革命 | 中间路线 | 未披露 |
| 开源 | ❌ | ✅ MIT | ✅ Apache 2.0 | ❌ |

MiniMax 的选择与其他公司形成鲜明对比：不是架构激进，而是**数据和 RL 系统激进**。

## 社区评价

截至分析日该论文引用为 0。M2.7 在开发者社区中获得关注主要因为其极高的成本效率（90% 质量 @ 7% 成本）。

## 可复用的工程经验

1. **做详尽 ablation 再放弃全注意力——不是所有场景都需要 "更高效" 注意力**——MiniMax 的 ablation 值得所有团队参考
2. **Agent-Native RL 系统是当前被低估的关键基础设施——Forge 的 Training-Inference-Agent 解耦 + 窗口调度 + 前缀树合并在长轨迹训练中是必须的**
3. **Self-evolution 是后训练的下一个重要前沿**——微调训练环境和 scaffold 的能力比模型参数本身更具杠杆效应
4. **小激活量 + 高质量数据 + 精细 RL = 可竞争前沿性能**——不需要最大模型也能做出有用的 Agent 系统
5. **Sigmoid gating + fine-grained experts + expert bias 组合有效：** 256 专家 + 每 token 8 专家 + sigmoid gating 在 9.8B 激活下做到了 229.9B 总参数的有效利用
