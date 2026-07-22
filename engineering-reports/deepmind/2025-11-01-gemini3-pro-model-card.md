---
title: Gemini 3 Pro Model Card — 稀疏 MoE 混合专家 + 原生多模态 + Deep Think 推理
date: 2025-11-01
source: https://deepmind.google/models/model-cards/gemini-3-pro/
---

# Gemini 3 Pro

**发布日期：** 2025 年 11 月（模型发布）；Model Card 最后更新 2026 年 5 月
**来源：** [Model Card (PDF)](https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Model-Card.pdf) | [Model Cards 汇总](https://deepmind.google/models/model-cards/)
**工程范式：** 稀疏 MoE + 原生多模态 + 可选 Deep Think 推理模式，Google 通过 TPU/JAX/Pathways 全栈自研实现模型系列化部署

## 设计哲学

Gemini 3 Pro 是 Google 旗舰推理模型系列的核心骨干。与 Gemini 2.5 Pro 相比，核心约束是：**在不显著增加推理成本的条件下，同时提升推理深度和多模态覆盖度。**

关键设计选择：
- **稀疏 MoE 而非 Dense：** 每个输入 token 只激活参数子集，将模型容量与推理计算解耦
- **原生多模态输入：** 文本、图像、音频、视频四种模态从训练初始即统一处理——不是事后拼接的多模态适配
- **Deep Think 模式作为可选配置：** 不是单独的模型，而是在推理时增强复杂问题求解性能的可选设置
- **模型家族化：** Gemini 3 Pro 是系列核心，衍生出 Pro Image、Flash、3.1 Pro、3.1 Flash、3.1 Flash-Lite、3.1 Flash Live、3.5 Flash 等多个变体——每个变体都是基于 Gemini 3 Pro 的微调/优化，而非从头训练

**放弃的路线：**
- 不追求公开详细的架构参数（Google 不披露专家数、激活参数等具体数字）
- 不追求无限制的上下文窗口——1M 输入/64K 输出是实际部署的稳定配置

## 关键架构决策

### 模型规格

| 特性 | Gemini 3 Pro |
|------|-------------|
| 架构 | 稀疏 MoE Transformer（具体专家数未披露） |
| 模态 | 文本 + 图像 + 音频 + 视频（原生）|
| 上下文 | 1M tokens 输入，64K tokens 输出 |
| Deep Think | 可选推理增强模式 |
| 训练硬件 | Google TPU（TPUv5p/v6e Pod 集群）|
| 训练框架 | JAX + ML Pathways |

### 训练数据
- **来源：** 公开网页文档、文本、代码、图像、音频（含语音和其他音频类型）、视频
- **后训练数据：** 指令微调数据、强化学习数据、人类偏好数据
- **额外来源：** 许可数据、用户数据（在适用服务条款和隐私政策下）、AI 生成合成数据
- **数据处理：** 去重、robots.txt、安全过滤、质量过滤、过滤色情/暴力/CSAM 内容

### Deep Think 模式

Deep Think 是 Gemini 3 Pro 的可选推理增强模式，设计用于：
- 需要增强推理和智能的复杂问题
- 算法开发和科学发现场景
- 战略性规划和逐步改进

在 Deep Think 模式下，Frontier Safety Framework 评估结果与标准模式一致，说明该模式不引入额外的安全风险。

### Frontier Safety Framework 评估

Google DeepMind 的 Frontier Safety Framework（FSF）评估了四个关键领域：

| 领域 | 评估结果 | CCL（关键能力水平） | 是否触发 |
|------|---------|:-----------------:|:-------:|
| CBRN（化学/生物/放射/核） | 提供准确但偶尔可操作的信息，未能显著增强威胁行为者能力 | Uplift Level 1 | ❌ 未触发 |
| 网络安全 | 基准 v1 hard 挑战：11/12 解决；v2 挑战：0/13 端到端解决 | Uplift Level 1 | ❌ 未触发（但 v1 超过警戒线） |
| 有害操纵 | 操纵效能略优于非生成式 AI 基线，未显著优于前代模型 | Level 1（探索性）| ❌ 未触发 |
| ML R&D | 优于 Gemini 2.5，但在 Scaling Law Experiment 和 Optimize LLM Foundry 任务上远低于警戒线 | Acceleration Level 1, Automation Level 1 | ❌ 未触发 |
| Misalignment（探索性）| Agent 解决 3/11 情境意识挑战和 1/4 隐蔽挑战 | Instrumental Reasoning Level 1+2 | ❌ 未触发 |

**关键发现：** Gemini 3 Pro 在所有 CCL 评估中均未触发警戒线。使用 Deep Think 模式时安全评估结果一致。

## 关键结果

### 能力评估

Gemini 3 Pro 在推理、多模态、agentic tool use、多语言、长上下文等多个维度上显著优于 Gemini 2.5 Pro。

具体 benchmark 数字，Model Card 未逐项列出，指引到 [deepmind.com/models/evals-methodology/gemini-3-pro](https://deepmind.com/models/evals-methodology/gemini-3-pro) 查看。

### 安全评估

| 评估维度 | Gemini 3 Pro vs Gemini 2.5 Pro |
|---------|:-----------------------------:|
| 文本到文本安全策略 | -10.4%（回撤） |
| 多语言安全策略 | +0.2% |
| 图像到文本安全策略 | +3.1% |
| Tone（客观语气）| **+7.9%**（显著改善）|
| 边界提示下的指令遵循 | +3.7% |

**安全评估关键发现：**
- 整体上 Gemini 3 Pro 在安全和语气上均优于 Gemini 2.5 Pro
- 无根据拒绝（unjustified refusal）保持在低水平
- Deep Think 模式的安全评估结果与标准模式一致
- 红队测试范围相比 2.5 Pro 有所扩展，未发现严重问题

## 范式对比

**vs OpenAI GPT-5.5：** GPT-5.5 的评估核心是 Preparedness Framework + 外部独立评估（AISI/CAISI），强调"同一模型双轨评估"。Gemini 3 Pro 的评估核心是 Frontier Safety Framework，强调能力水平分级（CCL）和加速/自动化分级。两者的安全评估路径完全不同。

**vs Anthropic Claude Opus 4.8：** Anthropic 的 ASL（AI Safety Levels）与 Google 的 FSF 是可比的框架，但 Anthropic 更强调宪法 AI（Constitutional AI）和红队测试。Gemini 3 Pro 在 FSF 评估中所有维度均未触发警戒线，与其声称的"最智能模型"定位形成对比。

**vs Llama 4：** Google 闭源 + API 分发 vs Meta 开源 + Apache 许可的双轨竞争。技术层面，Gemini 3 Pro 的 Deep Think 模式（可选推理增强）与 Llama 4 的 iRoPE 超长上下文（10M）代表了不同的技术优先级。

## 可复用的工程经验

1. **可选推理模式的安全评估一致性：** Deep Think 模式的安全结果与标准模式一致——这表明增加推理深度（通过 test-time compute）不一定引入额外安全风险。这对其他实现"推理时计算增强"的团队有参考价值。

2. **FSF 的 CCL 分级体系：** 五个风险维度（CBRN/Cyber/Manipulation/ML R&D/Misalignment）+ 三个级别（Acceleration/Automation/Uplift）的评估结构，比单一的"是否危险"更细致。每个维度都有具体的定量阈值。

3. **模型系列化策略：** 从 Gemini 3 Pro 一个骨干衍生 8+ 个变体（Flash、Flash-Lite、Live、Pro Image 等），每个变体针对不同的部署场景微调。这种"一个核心 + N 个适配"的模式在推理成本优化上比单独训练每个变体更高效。

4. **安全能力的绝对评估 vs 相对评估：** Model Card 不仅报告"模型是否安全"的绝对数据，还报告"比 2.5 Pro 好/差 X%"的相对数据。相对评估帮助使用者理解代际变化方向。
