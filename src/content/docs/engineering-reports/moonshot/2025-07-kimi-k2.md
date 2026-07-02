---
title: Kimi K2 — Open Agentic Intelligence
date: 2026-07-03
source: arXiv 2507.20534
---

# Kimi K2: Open Agentic Intelligence

**发布日期：** 2025-07 (arXiv 2507.20534)
**来源：** arXiv 2507.20534
**工程范式：** 超大 MoE + Agentic 训练——1T 总参 / 32B 激活，384 专家，MuonClip 优化器。

## 设计哲学

Kimi K2 的核心约束是 agentic 任务的可靠性——软件工程任务（SWE-Bench）、工具使用、多步推理需要模型在每一步都保持高精度。Moonshot 选择用**超大 MoE（1T 总参/32B 激活）**来提供充足的模型容量，同时用 **MuonClip 优化器** 解决超大 MoE 训练不稳定性。K2 是首个以 agentic intelligence 为核心设计目标的开源模型。

## 关键架构决策

### MoE 架构
- **总参数：** 1T（1,000B 参数）
- **激活参数：** 32B 每 token
- **专家数：** 384 个专家，每 token 激活 8 个
- **上下文窗口：** 128K tokens

### MuonClip 优化器
- 基于 Muon（第二类优化器）改进
- 提出 **QK-clip** 技术解决训练不稳定问题
- 在 15.5T tokens 的预训练中实现**零 loss spike**
- 比传统 AdamW 更高效的 token 利用率

### 多阶段后训练
1. **大规模 Agentic 数据合成管线**：自动生成 agent 交互数据
2. **联合 RL 阶段**：模型通过真实和合成环境的交互提升能力
3. 无需 extended thinking（与 k1.5 不同，K2 在 non-thinking 设置下评测）

### 训练数据
- 预训练数据量：**15.5 万亿 tokens**
- 后训练包括 agentic 数据合成 + RL 联合优化

## 关键结果

### Agentic 能力
| Benchmark | K2 (非思考模式) | 对比 |
|-----------|----------------|------|
| Tau2-Bench | **66.1** | 超 GPT-4.1 |
| ACEBench (En) | **76.5** | – |
| SWE-Bench Verified | **65.8** | 开源 SOTA |
| SWE-Bench Multilingual | **47.3** | 超多数开源/闭源基线 |

### 编码/推理/数学
| Benchmark | K2 (非思考模式) |
|-----------|----------------|
| LiveCodeBench v6 | **53.7** |
| AIME 2025 | **49.5** |
| GPQA-Diamond | **75.1** |
| OJBench | **27.1** |
| MATH-500 | **97.4** |

### Humanity's Last Exam（带工具）
- K2: **44.9%**（超越 GPT-5 的 41.7%）

## 范式对比

vs DeepSeek-V3（671B/37B，256 专家），K2 的专家更多（384 vs 256）但激活参数类似（32B vs 37B）。vs Llama 3.1-405B（密集 405B），K2 用 MoE 在更少激活参数下实现更强 agentic 能力。关键创新在 MuonClip 优化器——这是首次在 1T 级 MoE 上成功应用第二类优化器。

## 可复用的工程经验

1. **Muon 类优化器在大规模 MoE 训练中可行**——QK-clip 解决了之前的不稳定问题
2. **Agentic 能力可以通过合成数据 + RL 联合训练有效获得**——不依赖人工标注
3. **超大 MoE（384 专家）比传统 MoE（64-256 专家）提供更精细的专家分工**
4. **无 extended thinking 设置下的 agentic 性能对推理成本控制至关重要**
