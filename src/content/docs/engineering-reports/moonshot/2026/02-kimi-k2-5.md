---
title: Kimi K2.5 — Visual Agentic Intelligence
date: 2026-07-03
source: arXiv 2602.02276
---

# Kimi K2.5: Visual Agentic Intelligence

**发布日期：** 2026-02 (arXiv 2602.02276)
**来源：** arXiv 2602.02276
**工程范式：** 超大 MoE + 视觉 Agent Swarm——1.04T 总参 / 32B 激活，联合文本-视觉训练，Agent Swarm 分布式编排。

## 设计哲学

K2.5 的核心创新在于**文本与视觉的联合优化**——通过 joint text-vision pre-training、zero-vision SFT、joint text-vision RL 让两种模态相互增强。同时引入 **Agent Swarm** 框架，将复杂任务分解为异构子问题并行执行。Moonshot 相信：下一代 AI 系统需要同时具备视觉理解、长程推理和并行协调能力。

## 关键架构决策

### 模型规模
- **总参数：** 1.04T（较 K2 的 1T 略有增加）
- **激活参数：** 32B 每 token
- **MoE 架构：** 与 K2 相同，384 专家 / 8 active
- **视觉编码器：** MoonViT，原生分辨率视觉编码

### 联合视觉-文本训练
- **Joint text-vision pre-training**：在 15T 混合视觉和文本 tokens 上继续训练（从 K2 checkpoint 开始）
- **Zero-vision SFT**：视觉模态的 SFT 从零开始
- **Joint text-vision RL**：文本和视觉 RL 联合训练
- 额外 ~1T 用于 ViT 训练
- ~700B 用于长上下文中训练
- K2.5 总训练 tokens 约 **28.5T**

### Agent Swarm
- 自导向并行 agent 编排框架
- 动态分解复杂任务为异构子问题
- 子 agent 并行执行
- **延迟降低：** 比单 agent 基线**降低 4.5 倍**
- 支持 100+ 领域专业子 agent

### 上下文
- 上下文窗口：**128K tokens**
- 长上下文缩放技术使能

## 关键结果

### Agentic 和编码能力
- **Agent Swarm** 将延迟降低 4.5 倍
- 在编码、视觉、推理和 agentic 任务上达到 SOTA
- **HLE（带工具）：** 50.2%
- **SWE-Bench：** 开源最高水平（76.8%+）
- K2.5 是当时开源模型中 **Artificial Analysis Intelligence Index 最高**的模型（后被 GLM-5 超越）

### 视觉推理
- **LongVideoBench：** 64.5
- **MMLongBench-Doc：** 35.1
- **InfoVQA：** 83.2
- **ScreenSpot-Pro：** 34.5
- **MMMU：** 61.7
- **MathVision：** 36.8
- **MathVista：** 71.3

## 范式对比

vs K2（纯文本 agentic），K2.5 加入视觉模态后成为完整的视觉 agentic 系统。vs GLM-5（1T/32B，类似规模），K2.5 的 Agent Swarm 框架是独特优势。vs Qwen2.5-VL-7B（7B 密集），K2.5 以更大规模换取更高上限。Agent Swarm vs 标准单 agent 范式——4.5 倍延迟降低提供了规模化 agent 系统的工程路径。

## 可复用的工程经验

1. **Agent Swarm（动态分解 + 并行执行）是克服单 agent 延迟瓶颈的有效方法**
2. **联合文本-视觉 RL 训练可以利用视觉数据增强文本推理能力，反之亦然**
3. **Zero-vision SFT 是训练多模态模型的有效策略**——避免预训练阶段的视觉表征偏差
4. **超大规模 MoE 的训练稳定性在 K2→K2.5 的延续训练中已经验证**
