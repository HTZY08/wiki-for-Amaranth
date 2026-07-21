---
title: MiniMax M3 — 第一个将前沿编程、1M上下文、原生多模态三者合一的开源模型
date: 2026-07-21
source: https://www.minimax.io/blog/minimax-m3
---

# MiniMax M3 — 第一个将前沿编程、1M上下文、原生多模态三者合一的开源模型

**发布日期：** 2026年7月
**来源：** [MiniMax M3 Blog](https://www.minimax.io/blog/minimax-m3) · [HuggingFace](https://huggingface.co/MiniMaxAI/MiniMax-M3) · [GitHub](https://github.com/MiniMax-AI/MiniMax-M3)
**工程范式：** 稀疏注意力驱动的原生多模态扩展——用 MSA 替代全注意力，将计算复杂度从二次降到线性，使百万级上下文在实践上可行

## 设计哲学

MiniMax M3 的核心矛盾是：`Agent 化任务需要超长上下文，但全注意力的 O(n²) 复杂度使长上下文不可负担`。MiniMax 的选择是**从注意力机制底层解决问题**，而不是在推理时做工程优化。

核心约束和取舍：

- **拒绝全注意力的"先天缺陷"**：M3 放弃传统 GQA/MHA，采用自主研发的 MiniMax Sparse Attention（MSA），一种基于块级预过滤的稀疏注意力。在 1M 上下文下，per-token 计算量仅为 M2 的 1/20。
- **原生多模态，非事后拼接**：M3 从训练 Step 0 开始就进行混合模态训练，而非在文本模型上嫁接视觉编码器。这意味着不同模态的语义空间从底层自然融合。
- **开放权重且前沿**：M3 是目前唯一同时具备三个前沿能力（编程/Agent、百万上下文、原生多模态）的开源权重模型，对标闭源前沿模型。
- **放弃常见的"高跑分单点"**：MiniMax 明确将评估重点从标准 benchmark 转移到**真实世界场景**（CUDA 内核自主优化、论文复现），主动选择更难验证的评估方式。

模型配置：~428B 参数，~23B 激活参数（MoE）。

## 关键架构决策

### 注意力机制：MSA（MiniMax Sparse Attention）

MSA 是 M3 最核心的架构创新，一篇独立的技术报告已发布（arXiv:2606.13392）。

- **设计原理**：稀疏注意力通过在 attention 计算前添加预过滤阶段来避免复杂度爆炸。与 DSA（GLM-5）和 MoBA（DeepSeek-V4）相比，MSA 能将 KV 更精细地划分成块，实现更高的有效上下文覆盖。
- **算子优化**：采用"KV outer gather Q"策略——以外层 KV 块作为循环，聚合命中它们的 query。每个块只读取一次，内存访问连续。在 M3 的 head 配置下，算术强度显著优于常见的 Flash-Sparse-Attention 和 flash-moba（>4× 加速）。
- **实际效果**：1M 上下文时，prefill 加速 9×，decode 加速 15×。多轮消融实验表明 MSA 在绝大多数能力上匹配全注意力。

### 训练策略

M3 的训练管线在 M2 的基础上有两大关键变化：

1. **全模态交织训练**：从 Step 0 开始混合文本、图像、视频数据。MiniMax 发现**交织数据比合成数据更容易规模化**，因此重构了整个文本预训练数据管线，生成了大量交织数据。
2. **交互式用户模拟器框架**：为弥补 benchmark 和真实用户体验之间的差距，构建了能模拟真实开发者协作者的交互式模拟器。它暴露模型在训练和评估中接触协作场景（需求细化、方案讨论、反馈修正、连续任务切换），使 Agent 能从被动执行转变为主动协作。

### 推理优化

- 支持三种 `thinking` 模式：`enabled`（始终推理）、`adaptive`（自动判断）、`disabled`（最低延迟）
- 官方推荐推理框架：SGLang、vLLM、Transformers、KTransformers、unsloth
- 推理参数：temperature=1.0, top_p=0.95
- API 按输入长度分级定价：≤512K 为普通费率，>512K 为长上下文费率
- 提供 priority 服务 tier（高并发场景的调度优先级）

### Post-training

虽然 M3 的 blog 未披露完整的 RL 训练细节，但信息包括：

- Agentic RL 训练使用真实世界用户的协作逻辑
- 引入了"Producer + Verifier adversarial harness loop"，Agent Team 能在执行中持续自我产出、反思和修正
- 借鉴 OpenCode 和 Pi 构建了 MiniMax Code 脚手架

## 关键结果

### 编程与 Agent benchmark

| Benchmark | M3 分数 | 说明 |
|-----------|---------|------|
| SWE-Bench Pro | 59.0% | 软件工程验证 |
| SWE-Bench Verified | 80.5% | HF 评估结果 |
| Terminal-Bench 2.1 | 66.0% | 终端执行 |
| SWE-fficiency | 34.8% | 效率评估 |
| KernelBench Hard | 28.8% | CUDA 内核优化（Blackwell） |
| MCP Atlas | 74.2% | MCP 任务 |
| Apex-Agents | 27.7% | Agent 基准（HF 数据） |
| Claw-Eval (General) | 74.5% | 通用得分（HF 数据） |
| SkillsBench V1.1 | 53% | 技能基准 |

### 多模态 benchmark

| Benchmark | M3 分数 | 对比 |
|-----------|---------|------|
| MMMU Pro | 78.1% | 高校多模态理解 |
| Video-MME v2 | 85.4% | 视频理解（HF 评估） |
| OmniDocBench | 未公开具体数值 | 文档理解 |
| OSWorld-Verified | 70.06% (Max Steps=200) | 桌面操控 |

### 真实世界任务

1. **CUDA FP8 GEMM 内核自主优化**：24 小时内完成 147 次 benchmark 提交和 1,959 次工具调用，将 Hopper FP8 硬件峰值利用率从 7.6% 提升到 71.3%，实现 9.4× 加速。最佳方案出现在第 145 次提交。
2. **论文独立复现**：自主运行近 12 小时，产生 18 个 commit 和 23 张实验图，成功复现 ICLR 2025 杰出论文奖论文的核心实验。
3. **PostTrainBench**：从 4 个仅完成预训练的 Base 模型开始，自主完成数据合成→训练→评估→迭代全流程，最终得分 0.37（Opus 4.7: 0.42, GPT-5.5: 0.39）。

## 范式对比

### MiniMax M3 vs DeepSeek-V4

| 维度 | MiniMax M3 | DeepSeek-V4 |
|------|-----------|-------------|
| 注意力 | MSA（块级稀疏） | MoBA（MoE+稀疏）+ Hybrid Attention |
| 上下文 | 1M | 1M |
| 多模态 | 原生（Step 0 交融） | 训练后对齐 |
| 激活参数 | ~23B | V4-Pro 待定 |
| 开源权重 | ✅ 已开源 | Preview 阶段 |
| 典型能力 | 编程+Agent+多模态三合一 | 超长上下文+推理 |

### MiniMax M3 vs GLM-5

| 维度 | MiniMax M3 | GLM-5 |
|------|-----------|-------|
| 注意力 | MSA | DSA（Dynamic Sparse Attention） |
| 上下文 | 1M | 1M（GLM-5.2） |
| 开源 | ✅ 完全开源 | ✅ 开源 |
| 多模态 | 原生 | 分离式（5V 分支） |
| 核心差异 | 原生多模态+Agent | Agentic engineering |

M3 的核心差异化优势是**将三个前沿能力打包进同一个开源权重模型**，这在 2026 年 7 月的时间点上是行业唯一；相比 DeepSeek-V4 和 GLM-5，M3 在多模态的原生性上走得更远。

## 社区评价

截至 2026-07-21：
- GitHub: 416 stars, 47 forks（发布仅三周）
- HuggingFace: 189K 月下载量
- MiniMax Token Plan 同步发布（Plus $20/月→1.7B tokens）
- MiniMax Code 桌面应用配套发布，支持 Computer Use

## 可复用的工程经验

1. **注意力机制是超长上下文的第一性原理杠杆**——MSA 的块级稀疏路径比全注意力在 1M 上下文下实现 20× 的 per-token 降低。MiniMax 的经验是，不修复注意力层的基础复杂度，上层工程优化（KV cache、量化）的收益有限。
2. **原生多模态的训练数据策略**：交织数据比合成数据更容易规模化。重构文本预训练管线来生产交织数据，让模型从训练第一步就接触跨模态信息，比事后拼接更有效。
3. **真实世界任务是更有效的验证信号**：CUDA 内核优化和论文复现等端到端任务比标准 benchmark 更能暴露模型的真实差距。M3 连续 145 次尝试才获得最优解——这种 persistence 是标准 benchmark 无法测量的。
4. **M3 的开源生态策略**同时覆盖了多个推理框架，使模型可部署在 SGLang、vLLM、Transformers、KTransformers、unsloth 等多个栈上，降低了社区采用的门槛。
