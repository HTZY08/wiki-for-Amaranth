---
title: Seed1.8 — 面向通用化真实世界 Agent 能力的统一感知-推理-行动模型
date: 2026-07-06
source: https://arxiv.org/abs/2603.20633
---

# Seed1.8 Model Card：Towards Generalized Real-World Agency

**发布日期：** 2026-03-21（v1），2026-03-28（v2）
**来源：** [arXiv:2603.20633](https://arxiv.org/abs/2603.20633)
**工程范式：** 单一模型内集成感知-推理-行动的 Agent 化路线，四档 Thinking Mode 可配置推理深度，以经济价值导向的定制评测驱动优化

## 设计哲学

Seed1.8 的核心约束是：**模型不能只在标准 benchmark 上好看，必须能在真实世界的多轮交互中可靠行动。**

面对这一约束，团队的架构选择是放弃"任务特化 agent 管线"的思路，转而将感知（perception）、推理（reasoning）和行动（action）整合在单一模型内——搜索、代码执行、GUI 交互都通过统一 Agent 接口实现，而非外挂编排框架。

放弃了什么：放弃了 benchmark 榜单上的极致单点分数。Seed1.8 在大部分 benchmark 上不是最高分（通常是第二或第三），但在经济价值导向的内部评测（Education、Customer Support、Information Processing、Complex Workflow 等）上展现了一致性更好的表现。

## 关键架构决策

### 4 档 Thinking Mode

Seed1.8 支持四种可配置的推理深度：

| Mode | 定位 |
|------|------|
| `no_think` | 极低延迟，简单问答 |
| `think-low` | 轻量推理 |
| `think-medium` | 中等深度，平衡延迟与质量 |
| `think-high` | 完整链式推理，复杂任务 |

这在当时是中国模型中少见的显式 inference-time compute scaling 设计，使模型能根据任务复杂度自适应分配推理算力。

### 统一 Agent 接口

不依赖外部的 agent framework 或编排层，模型原生支持：
- **搜索**：从外部来源收集信息并综合证据
- **代码生成和执行**：结构化计算、程序修改、工具编排
- **GUI 交互**：通过截屏、文档、图表、视频进行视觉感知，在无 API 的环境中直接操作

### 视觉编码优化

对图片和视频输入优化 token 消费，在多模态和长上下文场景中降低延迟和算力成本 — 具体 token 压缩比率未公开。

### 经济价值导向的内部评测

团队建立了 6 个高价值场景的内部 benchmark：
- **Education**：K-12 核心科目的解题、评分、讲解、出题
- **Customer Support Q&A**：基于企业知识库的客服问答
- **Information Processing**：从海量 UGC 中提炼观点和情绪
- **Intention Recognition**：从对话/会议记录/社媒中推断意图
- **Information Extraction**：从异构文档中结构化提取
- **Complex Workflow**：端到端多步流程执行

## 关键结果

### Reasoning

| Benchmark | Seed1.8 | GPT-5 High | Claude-Sonnet-4.5 | Gemini-2.5-pro | Gemini-3-pro |
|-----------|---------|------------|-------------------|----------------|--------------|
| AIME-25 | **94.6*** | 87.0* | 88.0* | 95.0* | 94.3 |
| HMMT-25(Feb) | **88.3*** | 66.7 | 86.7 | 97.5* | 89.7 |
| BeyondAIME | 74.0 | 62.0 | 62.0 | 83.0 | **77.0** |
| GPQA-Diamond | 85.7* | 83.4* | **86.4*** | 91.9* | 83.8 |
| ARC-AGI-1 | 65.7* | 63.7* | 37.0* | 75.0* | **67.9** |
| LiveCodeBench(v6) | **87.0*** | 64.0* | 73.6* | 90.7 | 79.5 |

*注：标 * 的数据来自该模型的官方技术报告。

### Instruction Following

| Benchmark | Seed1.8 | GPT-5 High | Claude-Sonnet-4.5 | Gemini-2.5-pro | Gemini-3-pro |
|-----------|---------|------------|-------------------|----------------|--------------|
| Inverse IFEval | 78.9 | 70.2 | 75.3 | 80.6 | **80.3** |
| MultiChallenge | **69.6** | 57.2 | 55.4 | 67.4 | 66.7 |

### 经济价值场景（内部评测）

| 场景 | Seed1.8 | GPT-5 High | Claude-Sonnet-4.5 | Gemini-2.5-pro | Gemini-3-pro |
|------|---------|------------|-------------------|----------------|--------------|
| Education | 55.0 | 53.0 | 52.4 | **57.0** | **60.8** |
| Customer Support | 63.4 | 59.4 | **64.6** | 65.5 | **69.0** |
| Complex Workflow | 53.0 | **55.4** | 54.4 | 58.2 | 54.6 |

Seed1.8 在经济价值场景上表现稳定，但最高分往往属于 Gemini-3-pro。

### Agentic 能力

Agentic 搜索、编码和 GUI 具体数字：原文以表格形式呈现但未在可读部分清晰展示所有数值。详见原文 §2.3 Agentic Capabilities。

## 范式对比

### vs GPT-5 High & Claude-Sonnet-4.5

Seed1.8 在数学和代码推理上表现出色（AIME-25 **94.6*** 超过所有对比模型），但在 STEM 深度推理（GPQA-Diamond 85.7 vs Gemini-3-pro 83.8）上略逊于 Claude-Sonnet-4.5（86.4）。

关键差异在于：Seed1.8 的 Thinking Mode 设计让推理深度可配置，而 GPT-5 High 和 Claude-Sonnet-4.5 的推理模式是固定的或二元的（开/关）。

### vs Gemini 系列

Gemini-3-pro 在绝大多数 benchmark 上表现最强，但 Seed1.8 在推理和指令跟随上与 Gemini-2.5-pro 相当甚至更优。Seed1.8 在 ARC-AGI-1 上的 65.7 vs Gemini-2.5-pro 的 37.0，显示出明显的推理优势。

### vs 国内同行

相比 DeepSeek、Qwen 的独立 Agent/Code 模型路线，Seed1.8 选择将 Agent 能力直接集成到基础模型中，而不是通过外挂适配层。统一感知-推理-行动的思路后来被 Seed2.0/2.1 继承并强化。

## 社区评价

暂无显著 HN/Reddit 讨论帖。Seed1.8 作为 2026 年 Q1 的过渡版本（介于 Seed1.6 和 Seed2.0 之间），在社区中的讨论热度不及 Seed2.0 及之后的版本。

## 可复用的工程经验

1. **内部经济价值评测比公开 benchmark 更有产品指导意义**：Seed1.8 在公开 benchmark 上不一定最优，但在定制的高价值场景评测上表现稳定。对生产系统而言，定义自己的"价值场景"并建立评测体系比追求公共榜单更有意义。
2. **Thinking Mode 分级是实用的延迟-质量权衡设计**：让用户/应用根据任务复杂度选择合适的推理深度，比固定推理模式更灵活。no_think→think-high 四档为 API 用户提供了明确的性价比选择空间。
3. **Agent 能力原生集成 vs 外挂框架的选择**：Seed1.8 证明，对于追求可靠性的生产系统，将搜索/代码/GUI 能力原生集成到模型中可以减少系统复杂性和故障点。代价是模型训练和评估的复杂度增加。
4. **统一 Agent 接口**：搜索、代码执行、GUI 交互共享同一个接口规范，降低了部署和维护成本。这与依赖多个独立工具链的架构形成对比。
