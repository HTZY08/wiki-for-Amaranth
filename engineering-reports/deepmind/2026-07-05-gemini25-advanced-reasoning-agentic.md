---
title: Gemini 2.5 — 推理、多模态、长上下文与 Agentic 前沿
date: 2026-07-05
source: https://arxiv.org/abs/2507.06261
---

# Gemini 2.5 — 推理、多模态、长上下文与 Agentic 前沿

**发布日期：** 2025-2026年
**来源：** https://arxiv.org/abs/2507.06261
**工程范式：** 全栈推理 + 多模态 + 长上下文的统一 Agent 平台

## 设计哲学

Gemini 2.5 的设计围绕一个核心理念展开：**将推理、多模态理解、长上下文和工具使用整合进单一模型，使其成为 Agentic 系统的原生平台**。与此前将推理作为独立后处理步骤的范式不同，Gemini 2.5 将"思考"能力直接构建为基础模型的一部分。

### 核心约束

1. **Pareto 最优前沿覆盖**：Gemini 2.X 家族（Pro / Flash / Flash-Lite）覆盖从超强推理到高性价比的全部能力-成本曲线，允许用户在同一个模型系列中按需选择权衡点。
2. **全栈原生整合**：不采用"拼装式"多模态（将独立模型缝合在一起），而是所有模态（文本、图像、音频、视频）在统一的 Transformer 骨架中处理。
3. **1M+ token 长上下文**作为第一性原理能力，而非事后扩展——这要求重写内部评估流程和位置编码策略。
4. **推理成本可控**：通过 Thinking Budgets（思考预算）机制，允许开发者在延迟与质量之间动态权衡。
5. **安全优先**：Frontier Safety Framework (FSF) 定义 Critical Capability Levels (CCLs)，Gemini 2.5 虽未触发任何 CCLs，但网络安全领域已发出早期预警。

### 架构选择

- **放弃**纯 Dense Transformer（Gemini 1.5 的路线），全面转向 **Sparse Mixture-of-Experts (MoE)**。
- **放弃**将推理作为独立系统（如外部 Chain-of-Thought 管线），改为模型原生内置 Thinking 模式。
- **放弃**分别处理不同模态的独立编码器架构，采用 Unified Transformer Backbone。
- **放弃**短期上下文优化，选择从零构建 1M+ token 级别的端到端处理能力。

### 目标用户场景

- 开发者需要一次性处理完整代码库（1M token ≈ 15本小说的文本量）。
- 需要从长达 3 小时的视频中提取特定时刻信息。
- 需要模型自主规划、执行多步骤工具调用（搜索、代码执行、子代理生成）。
- 需要模型具备"思考"能力，但不希望为简单查询付出推理延迟代价。

## 关键架构决策

### 1. Gemini 2.5 Pro (旗舰) & Flash (高性价比)

| 型号 | 定位 | 上下文窗口 | 推理模式 | 已知改进 |
|------|------|-----------|---------|---------|
| **Gemini 2.5 Pro** | 最强推理与多模态 | 1M tokens（2M 即将推出） | 默认全量思考 | 5× Aider Polyglot 提升（1年） |
| **Gemini 2.5 Flash** | 高性价比推理 | 1M tokens | 可调思考预算 | 20-30% 更少 token 消耗 |
| **Gemini 2.0 Flash** | 低延迟 | 标准窗口 | 无原生思考 | 适合高吞吐场景 |
| **Gemini 2.0 Flash-Lite** | 最低成本 | 标准窗口 | 无 | 纯性价比导向 |

Pro 与 Flash 共享同一基础架构（MoE Transformer），差异主要体现在模型规模、专家数量和后训练策略。Flash 的"混合推理"能力使其在需要时仍可进行深度推理，但默认以高效模式运行。

### 2. 思考模型 + 推理 effort scaling

这是 Gemini 2.5 最关键的创新之一：

- **原生思考 (Thinking)**：模型在最终响应前，内部进行成百上千步推理（Chain-of-Thought on steroids），通过专门的 Reinforcement Learning 训练使模型学会"何时思考多久"。
- **自适应计算**：模型根据查询复杂度动态决定思考深度——简单问题浅思考，困难问题深思考。
- **Deep Think 模式**（实验性，2025 I/O 发布）：让模型在回答前考虑多个假设路径。在 2025 USAMO（当年最难数学基准）和 LiveCodeBench 上取得领先。
- **Thinking Budgets**：开发者可以设置思考 token 预算上限，或完全关闭思考能力——在延迟和准确性之间精确控制。

这一架构使 Gemini 2.5 在竞争性编码数学问题上有显著优势，但代价是推理延迟和计算成本显著增加。

### 3. 多模态深度融合（3 小时视频处理）

- **统一 Transformer 骨架**：所有模态（文本、图像、音频、视频）被编码为统一表示空间中的 token 序列。
- **视频帧效率优化**：每帧仅用 **66 tokens** 表示（较前代大幅压缩），使得 1M token 窗口可以容纳约 3 小时视频内容。
- **原生视频理解**：支持从长视频中检索特定时刻（如"在 3 小时讲座视频中找到讲解梯度下降的特定 1 秒钟片段"）。
- **多模态代码生成**：将视频/图像理解与编码能力结合——例如从 3 小时讲座视频生成交互式学习 Web 应用，或从剧本 PDF 生成戏剧练习工具。

### 4. 长上下文架构

- **1M token 上下文窗口**（Gemini 2.5 Pro/Flash 标配），支持 2M token 实验性扩展。
- **超越检索增强**：论文明确挑战了"长上下文模型是否可替代 RAG、SQL 等"——Gemini 2.5 在 LOFT 和 MRCR-V2 基准上验证了在 128K token 长度的领先表现。
- **1M token 级别仍有有效性能**：虽然亿级 token 上的精度有下降，但仍是唯一在该规模公开测试的模型。
- **长上下文使用场景**：整本书分析、完整代码库理解、多轮长对话、跨文档推理。

### 5. Agentic workflow native support

- **原生工具使用**：从 Gemini 2.0 开始训练模型识别函数调用标记，在 Gemini 2.5 中这一能力成为原生特性——模型可在推理过程中决定何时调用工具（搜索、代码执行等）。
- **Gemini Deep Research**：基于 2.5 的自主网页浏览研究代理。升级到 2.5 后，HLE 表现从 7.95% 提升至 26.9%（更多计算时间下可达 32.4%）。
- **Gemini Plays Pokémon**：全自主运行 Pokémon Blue 游戏（~406.5 小时），展示长周期规划、子代理组合和工具编排能力。主代理可动态调用 Pathfinder（导航）和 Boulder_Puzzle_Strategist（谜题）两个子代理——且这两个子代理的 prompt 大部分由 Gemini 2.5 自身编写。
- **MCP 支持**（Model Context Protocol）：Gemini API 和 SDK 原生支持 MCP 工具定义，使开源工具集成更便捷。
- **Computer Use 能力**：Project Mariner 的计算机使用能力已进入 Gemini API。

## 关键结果

以下数据来自 arXiv:2507.06261 技术报告、Google 官方博客（2025 年 3 月 / 5 月 / I/O）以及交叉来源验证。

### 核心推理与编码

| Benchmark | Gemini 2.5 Pro | 对比说明 |
|-----------|---------------|---------|
| LMArena | **#1**（大幅领先） | 衡量人类偏好的综合榜单 |
| WebDev Arena | **#1**（ELO 1415） | Web 应用开发能力冠军 |
| SWE-Bench Verified | **63.8%**（自定义 Agent） | 2× 提升（1 年内） |
| Aider Polyglot | **82.2%** | 5× 提升（1 年内） |
| LiveCodeBench v5 | **74.2-75.6%** | 竞赛级编码 |
| GPQA Diamond | **83.0-86.4%**（单次） | 科学推理 SOTA |
| AIME 2025 | **83.0-88.0%**（单次） | 数学竞赛 |
| MMMU | **79.6-82.0%** | 多模态推理 |
| VideoMME | **84.8%** | 视频理解 SOTA |
| Humanity's Last Exam | **18.8-21.6%**（无工具） | 最难的专家级知识测试 |

### 事实性与长上下文

| Benchmark | Gemini 2.5 Pro | 对比说明 |
|-----------|---------------|---------|
| SimpleQA | **54.0%** | 事实准确性（对比 GPT-4.1 的 19.3%） |
| FACTS Grounding | **87.8%** | 知识 grounding |
| LOFT (128K) | **SOTA** | 长上下文推理 |
| MRCR-V2 (128K) | **SOTA** | 长上下文核心消解 |

### Deep Think 模式（实验性）

| Benchmark | 分数 |
|-----------|------|
| 2025 USAMO | **SOTA**（全球最难数学竞赛） |
| MMMU | **84.0%** |
| LiveCodeBench | **领先** |

### 关键趋势

- Gemini Pro 的 Aider Polyglot 性能在 1 年内提升了 **5 倍**。
- Gemini Pro 的 SWE-bench 性能在 1 年内提升了 **2 倍**。
- HLE 基准从推出（2025 年初）到论文撰写时（2025 年 6 月），最好的模型从个位数精度提升至 20% 以上。

**原文未公开具体数字的项**：模型参数量、MoE 专家数量、训练数据集规模、训练计算量（FLOPs）、推理延迟的具体数值。

## 范式对比

### 与 OpenAI GPT-5 系列的差异

| 维度 | Gemini 2.5 Pro | GPT-5 |
|------|---------------|-------|
| **架构** | Sparse MoE Transformer | 架构未公开（推测 Dense+MoE 混合） |
| **上下文窗口** | **1M tokens**（2M 实验） | 400K tokens |
| **输出长度** | 64K tokens | **128K tokens** |
| **推理模式** | 原生 Thinking + Deep Think | 原生推理（o-series 继承） |
| **多模态** | 原生文本/图像/音频/视频 | 多模态支持 |
| **AIME 2025** | 83-88% | **94.6%** |
| **定价（输入）** | **$1.25-2.50/1M tokens** | $10-15/1M tokens（o3 级别） |
| **Agent 支持** | MCP + Computer Use + Sub-agent | 工具调用 + Codex |
| **设计哲学** | 全能统一平台 | 分层产品线（GPT/o-series 分离） |

GPT-5 在纯数学推理（AIME）上明显领先，但在上下文窗口长度和定价效率上 Gemini 2.5 Pro 更有优势。GPT-5 采用分层产品线策略（GPT-5 通用 vs o-series 推理），而 Gemini 2.5 将所有能力整合进同一模型。

### 与 Anthropic Claude 系列的差异

| 维度 | Gemini 2.5 Pro | Claude Opus 4.1 |
|------|---------------|-----------------|
| **上下文窗口** | **1M tokens** | 200K tokens |
| **多模态** | 原生视频/音频/图像 | 图像 + 文本 |
| **推理模式** | 隐式思考（不可见） | **可见扩展思考**（Extended Thinking，中间步骤可读） |
| **SWE-bench** | 63.8% | ~70%+（Claude 3.7 Sonnet） |
| **GPQA Diamond** | **83-86%** | 78-85% |
| **AIME 2025** | 83-88% | **93.2%** |
| **可审查性** | Thought Summaries（结构化摘要） | 完整思考链可见 |
| **企业特性** | Vertex AI 生态 | Amazon Bedrock / GCP |

Claude 在 SWE-bench 等 Agentic 编码任务上传统领先，且 Extended Thinking 的中间步骤可见性对调试更友好。Gemini 2.5 用 5 倍更长的上下文窗口和更低的定价策略形成差异化竞争。

### 与 DeepSeek R1 的差异

DeepSeek R1 作为开源推理模型，在 AIME 上达到 70-79.8%（取决于配置），但在多模态理解和长上下文方面远不及 Gemini 2.5 Pro。Gemini 2.5 的差异化在于**统一能力集**——推理只是整体的一部分，而非全部。

## 可复用的工程经验

### 1. MoE 训练的稳定性突破

论文明确指出通过改进优化器和信号传播技术克服了 MoE 训练不稳定性。这表明：
- **预训练质量直接影响后训练效果**——更大的 MoE 模型通过稳定训练获得更高的基础能力，而非仅靠 RLHF 补救。
- 需要特定的初始化策略和损失函数设计来防止专家坍缩（expert collapse）。

### 2. 长上下文不是"可有可无"的特性，而是重构评估体系

> "Handling million-token contexts required a complete rework of their internal evaluation processes."

如果你的团队要构建长上下文模型，评估流程也必须重新设计——传统"大海捞针"测试远不足以衡量真实能力。LOFT、MRCR-V2、Michelangelo 等新型基准提供了更好的评估框架。

### 3. 推理成本控制的工程价值

**Thinking Budgets** 机制是工程实用性的典范：
- 开发者在 API 调用中设置 `thinking_budget: {max_thinking_tokens: N}`。
- 简单查询（如"什么是 Transformer"）无需深度思考。
- 复杂查询（如"解决这个 USAMO 问题"）自动分配更多计算。
- 可以在不加推理时完全关闭思考能力，获得更快的响应。

这一设计让同一个模型同时覆盖了"快速问答"和"深度推理"两个场景，无需在模型级别做取舍。

### 4. 在 Agent 中内省能力自我增强

**Gemini Plays Pokémon** 实验揭示了关键的涌现能力：
- **子代理自生成**：Gemini 2.5 自动编写了 Pathfinder 和 Boulder_Puzzle_Strategist 子代理的 prompt——这是一种元认知层面上的自我增强。
- **多工具编排**：主代理根据当前游戏状态动态选择调用哪个子代理。
- **长周期目标保持**：能够在 400+ 小时的自主运行中维持核心目标。

这表明：随着基础模型能力的提升，自我改进和子代理编排将成为 Agentic 系统的重要设计模式。

### 5. 安全性需与能力同步演进

- FSF（Frontier Safety Framework）定义了可量化的 Critical Capability Levels。
- Gemini 2.5 虽然在网络安全和 ML R&D 方面有显著提升，但在所有 CCL 上均未突破阈值。
- 对抗训练极大降低了间接提示注入的攻击成功率。
- **每轮能力提升都伴随安全评估的扩展**——Deep Think 模式延迟发布正是因为需要额外的安全评估。

### 6. 基准测试正在快速饱和，需要新型评估方法

论文明确指出了当前的评估危机：
- 1 年内 Aider Polyglot 提升 5×、SWE-bench 提升 2×。
- HLE 每个问题的专家制作成本高达 $5000，但模型在几个月内从个位数提升到了 20%+。
- Agentic 系统的评估复杂度远超传统静态基准。

这一趋势意味着：**如果你的产品仅依赖公开 benchmark 做区分度，你将很快无法区分前沿模型。** 需要构建任务特定、经济价值导向的评估体系。

### 7. 产品化深度：原生整合而非外部管道

Gemini 2.5 的独特优势在于其能力已经深度嵌入 Google 产品生态：
- **Google Search (SGE)**：为 15 亿用户提供 AI Overviews。
- **Project Astra**：音视频对话代理。
- **NotebookLM**：利用长上下文的海量文档处理。
- **Jules**：代码助手。
- **Gemini App**：直接面向用户的对话界面。

这与纯粹 API-first 的路线形成对比，展示了"模型→产品→用户反馈"的闭环加速能力。
