---
title: Seed1.5-VL — 紧凑型多模态 MoE，Agent 任务超越 CUA 和 Claude 3.7
date: 2026-07-03
source: https://arxiv.org/abs/2505.07062
---

# Seed1.5-VL Technical Report

**发布日期：** 2026-05-13
**来源：** arXiv 2505.07062, https://seed.bytedance.com/en/public_papers/seed1-5-vl-technical-report
**工程范式：** 参数效率 × 多模态 Agent 路线——用 20B 激活的 MoE 在 60 项基准上拿到 38 项 SOTA，在 GUI/游戏 agent 任务上超越业界领先的全模态系统。

## 设计哲学

ByteDance Seed 团队在 Seed1.5-VL 上延续了 Seed 系列一贯的参数效率路线。核心约束是推理成本与模型能力的平衡——豆包/抖音用户量级下，不能跑激活参数过百亿的模型。Seed1.5-VL 选择了 532M 视觉编码器 + 20B 激活 MoE 的紧凑架构，但在多模态理解和 agent 任务上达到 SOTA。

关键 trade-off：总参数量未公开（MOE 架构，多个专家），但仅 20B 激活参数。这意味着训练成本较高（需要训练完整的 MoE），但推理成本很低。对面向亿级消费者的 ByteDance，这是正确的经济选择。

## 关键架构决策

- **视觉编码器：** 532M 参数，与 MoE LLM 解耦。未公开具体架构细节（是否采用 ViT、SigLIP 或其他方案）。
- **LLM 主干：** MoE 架构，20B 激活参数。延续 Seed-Thinking 的技术栈。
- **支持模式：** 非思考（标准）模式和思考（深度推理）模式，覆盖图像理解、视频理解、文档理解、GUI 任务等。
- **训练数据：** 预训练超过 3T 多模态数据 token。

## 关键结果

来自原文的 benchmark 结果摘要：

**整体表现：** 60 项公开 benchmark 中 38 项达到 SOTA，涵盖多模态推理、图像 QA、图表理解、视觉定位/计数、视频理解、GUI Agent 等任务。

**Agent 任务对比：**
- GUI 控制和 gameplay 任务上：Seed1.5-VL **超越 OpenAI CUA 和 Claude 3.7**
- 在视觉推理任务（如 visual puzzles）中表现突出

**推理能力：** 不仅在多模态理解上表现出色，在纯推理任务（如数学推理）上也展示了竞争力。

**API 可用性：** 已通过火山引擎（Volcano Engine）提供服务，模型 ID: `doubao-1-5-thinking-vision-pro-250428`。

> 注：原文未公开具体的 benchmark 数值表（如 MMLU、MathVista 等分数），仅提及 "38 out of 60 SOTA" 和 "outperforms OpenAI CUA and Claude 3.7"。

## 范式对比

| 维度 | Seed1.5-VL | Gemini 3.5 Flash | Qwen3.5-Omni | GLM-5V-Turbo |
|------|-----------|-------------------|---------------|---------------|
| 激活参数 | 20B MoE | 未公开 | 数百亿 MoE | 未公开 |
| 视觉编码器 | 532M | 原生多模态 | SigLIP2 | CogViT |
| Agent 能力 | GUI + Gameplay | Computer Use | WebSearch + FunctionCall | 工具链 + Claw |
| SOTA 覆盖 | 38/60 public | 未公开此项 | 215 subtasks | 多项 agentic SOTA |

## 社区评价

截至 2026-07-03，该论文在 arXiv 上尚无公开引用。社区讨论主要集中在知乎和中文技术社区，正面评价集中于参数效率比（20B 激活 vs 领先 Agent 效果）。

## 可复用的工程经验

1. **参数效率是多模态 Agent 的可行路径**：20B 激活参数足以在 Agent 任务上超越参数规模大得多的系统，关键在于训练数据的质量和覆盖度。
2. **紧凑视觉编码器的可行性**：532M 视觉编码器搭配 MoE LLM，证明了视觉理解和推理能力并不单纯依赖巨大的视觉编码器。
3. **视频 + GUI + Gameplay 的统一训练受益**：跨任务数据混合训练，使单一模型在不同类型的视觉-动作任务上都表现良好。
