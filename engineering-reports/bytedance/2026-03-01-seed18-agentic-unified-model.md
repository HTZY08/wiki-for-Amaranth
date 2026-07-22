---
title: Seed1.8 Model Card — 感知-推理-行动统一模型，迈向通用真实世界智能体
date: 2026-03-01
source: https://arxiv.org/abs/2603.20633
---

# Seed1.8 Model Card

**发布日期：** 2026-03-01（arXiv 论文）
**来源：** [Seed1.8 Model Card (arXiv)](https://arxiv.org/abs/2603.20633) | [Seed1.8 官方页面](https://seed.bytedance.com/en/seed1_8)
**工程范式：** 在单一模型中统一感知、推理和行动能力，而非构建专用的 agent pipeline；通过可配置 thinking mode + 高效视觉编码平衡推理深度与延迟

## 设计哲学

Seed1.8 是字节跳动 Seed 团队对"通用智能体"的技术路线选择——不依赖外部 agent framework，而是在单一模型中原生整合所有智能体能力。

核心约束：真实世界的交互式场景要求模型具备多步推理、工具调用、环境反馈处理能力，同时受到延迟和计算成本的硬约束。

**四个核心设计原则：**
1. **强基础能力：** 在标准 LLM 和 VLM 基准上保持竞争力（推理、指令遵循、知识覆盖、多模态理解）——这是智能体行为的基础
2. **统一智能体交互：** 在单一模型内支持搜索、代码生成与执行、GUI 交互、视觉感知——不是外部编排
3. **延迟/成本感知推理：** 可配置 thinking modes + 优化视觉编码，平衡推理深度与响应时间
4. **与真实场景对齐的评估：** 基于高价值应用领域的内部分布式评估，而非仅依赖学术基准

**放弃的路线：**
- 放弃了任务特定的 agent pipeline（不采用 ReAct/Plan-and-Solve 等框架化 agent 实现）
- 放弃了事后拼接视觉能力——视觉在训练初始即与语言统一处理
- 放弃了固定推理模式——提供 NoThink / Low / Medium / High 多种 thinking 配置

## 关键架构决策

### 模型架构

| 特性 | Seed1.8 |
|------|---------|
| 基础能力 | LLM + VLM（统一多模态）|
| 智能体能力 | 搜索、代码执行、GUI 操作、视频工具调用 |
| 推理模式 | NoThink / Low / Medium / High（可配置 thinking 深度）|
| 视觉处理 | 高效视觉编码，显著的 token 效率优势 |
| 视频理解 | 支持高帧率回放 + VideoCut 工具 |
| 上下文 | 128K+（多模态长上下文 SOTA 在 MMLB-NIAH 上）|
| 前代对比 | Seed1.5-VL → Seed1.6（首次引入 thinking modes）→ Seed1.8 |

**视觉 Token 效率：**

Seed1.8 使用优化的视觉编码器，在相同视频理解精度下消耗显著更少的 token：
- 32K token 预算下：Seed1.8 的精度超过 Seed1.5-VL 在 80K token 下的表现
- 这种效率使长视频理解在实际部署中更可行

### 推理配置

Seed1.8 支持四种 thinking 模式，在推理计算与性能之间提供连续权衡：

| 模式 | 应用场景 | 性能特征 |
|------|---------|---------|
| NoThink | 简单查询 | 最低延迟，依赖内化知识 |
| Low | 日常任务 | 适度推理 |
| Medium | 复杂问题 | 平衡 |
| High | 前沿推理 | 最大 test-time compute |

**关键发现：** 相比 Seed1.6，Seed1.8 在相同推理 token 消耗下持续改善性能，且在挑战性基准上呈现更陡峭的缩放曲线——Seed1.6 容易在高计算量下趋于平台期，而 Seed1.8 随着 test-time compute 增加仍持续改善。

### 视觉能力

**多模态推理（ZeroBench SOTA）：**
Seed1.8 在 ZeroBench（最具挑战性的视觉推理基准）上以 Pass@1 11.0 超越 Gemini 3 Pro 的 10.0。在 9 个多模态推理基准中的 7 个上排名第二，仅次于 Gemini 3 Pro。

| 基准 | Seed1.8 | Gemini 3 Pro | GPT-5.1 High |
|-----|:-------:|:-----------:|:------------:|
| ZeroBench (Pass@1) | **11.0** | 10.0 | - |
| MMMU | 第二 | 第一 | 第三 |
| MathVista | 第二 | 第一 | 第三 |
| MathVision | 第二 | 第一 | - |

**GUI Grounding（SOTA）：**
- ScreenSpot-Pro：64.3（基本能力），使用 crop-box 工具时达到 **73.1**（新 SOTA）
- 在 OSWorld、Realbench、Online-Mind2web、AndroidWorld 四个关键 GUI 基准上实现最佳性能

**2D & 3D 空间理解（新 SOTA）：**
- DA-2K：90.7 Pass@1（Gemini 3 Pro：82.1）
- MMSIBench (circular)：25.8 Pass@1（Gemini 3 Pro：25.4）

### 智能体能力

**搜索能力（GAIA SOTA）：**
Seed1.8 在 GAIA 上达到 **93.2**，显著超越 GPT-5-high（76.7）。

| 基准 | Seed1.8 | GPT-5 High | Gemini 3 Pro |
|-----|:-------:|:----------:|:-----------:|
| GAIA | **93.2** | 76.7 | 未披露 |
| BrowseComp-en | **67.6** | - | - |
| BrowseComp-zh | **78.5** | - | - |
| HLE (text-only) | 40.9 | - | - |

**编码与工具使用：**
- AInstein-SWE-Bench：第二
- Terminal Bench 2.0：第二
- SWE-bench Verified、Multi-SWE-Bench、BFCL-v4、τ²-Bench 上与前沿模型持平

**经济价值转化（特定场景量化）：**
- 金融 (FinSearchComp)：56.2
- 专家工作流 (XpertBench)：金融 62.0、法律 55.2
- 生活规划 (WorldTravel)：多模态设置下最佳

### 视频理解

Seed1.8 支持 VideoCut 工具：在长视频中指定起止时间戳和高帧率（1-5 FPS）进行局部细节回放。

| 场景 | Seed1.8 | Seed1.8 + VideoCut | 对比模型 |
|------|:-------:|:------------------:|:--------:|
| CGBench | 基线 | **显著提升** | - |
| LVBench | 基线 | **显著提升** | - |
| ZeroVideo（内部高难度）| 基线 | **超越** Gemini 2.5/3 Pro | Gemini 2.5/3 Pro |

## 关键结果

### 视觉 Token 效率对比

Seed1.8 的视频理解效率远超同期模型：
- 在 32K token 下即达到 Seed1.5-VL 在 80K token 下的表现
- 在 CGBench、LVBench、VideoMME 三个基准上均验证了此差异

### Thinking 效率（BeyondAIME, KORBench, MMMU-Pro, MathVision）

| 基准 | NoThink (Seed1.8) | NoThink (Seed1.6) | High (Seed1.8) | High (GPT-5.1) |
|-----|:-----------------:|:-----------------:|:--------------:|:--------------:|
| MMMU-Pro | **65.4** | 61.0 | - | 43.5 |
| MathVision | - | - | **81.3** | 77.2 |
| EMMA NoThink | **50.1** | - | 前代 High 仅 48.1 | - |

## 范式对比

**vs Seed2.0（2607.00248，2026-07-05 已覆盖）：** Seed1.8 和 Seed2.0 代表了 Seed 系列的两条路线——Seed1.8 是"通用智能体统一模型"，强调感知/推理/行动一体化；Seed2.0 是"通用智能"（Towards Intelligence Frontier），更关注长链推理和 agent 生产力。两者互补而非替代，Seed1.8 在视觉/SOTA 搜索能力上更突出。

**vs GPT-5.1/GPT-5.5：** Seed1.8 在 GAIA（93.2 vs 76.7）和 MMMU-Pro NoThink（65.4 vs 43.5）上显著领先 GPT-5.1 和 GPT-5.5。这表明字节在"小型思考 + 强内化知识"路线上的效率优势——无需大量 test-time compute 即可在中等难度查询上取得优势。

**vs Gemini 3 Pro：** Seed1.8 在多个视觉基准上匹敌甚至超越 Gemini 3 Pro（ZeroBench、VLMsAreBiased、DA-2K、MMSIBench），但在其他大多数基准上仍落后。Gemini 3 Pro 的整体能力广度更广，但 Seed1.8 在特定维度（GUI 操作、搜索效率）上展现了独特优势。

## 可复用的工程经验

1. **模式化 Thinking（NoThink→Low→Medium→High）的价值：** Seed1.8 将思考深度作为可配置参数而非模型能力。NoThink 模式在简单查询上足够用且延迟最低，High 模式只在需要时启动。这种"思考预算管理"比"要么全开要么全关"更实用。

2. **视觉 Token 效率是实际部署的关键：** Seed1.8 在 32K token 下的视频理解精度超过前代 80K——2.5 倍效率提升。对于视频类应用，优化视觉编码器减少 token 消耗的重要性不亚于优化模型架构本身。

3. **统一智能体 > 外部编排：** Seed1.8 在单一模型中整合感知/推理/行动，而非写 agent pipeline（ReAct/MCP 等）。这在简单到中等复杂的 agent 场景中减少了框架开销和推理延迟。但高度复杂的工作流可能仍然需要外部编排。

4. **经济价值量化评估框架：** Seed1.8 引入了 FinSearchComp（金融搜索）、XpertBench（专家工作流）、WorldTravel（生活规划）三个业务导向的评估基准。将学术基准与业务 ROI 挂钩的评估方法更能反映模型的实际部署价值。

5. **高帧率视频回放工具（VideoCut）思路：** 不需要将整个视频以高 FPS 编码到上下文——通过工具接口允许模型"回看"关键片段，兼顾了上下文的 token 预算和细节需求。这是一种"工具辅助上下文管理"的通用思路。
