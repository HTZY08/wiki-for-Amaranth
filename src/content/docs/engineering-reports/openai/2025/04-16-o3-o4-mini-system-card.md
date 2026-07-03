---
title: "o3 & o4-mini — 工具整合推理的新高度"
date: 2025-04-16
source: OpenAI System Card / community.openai.com
---

# OpenAI o3 & o4-mini System Card

**发布日期：** 2025-04-16  
**来源：** OpenAI 官方博客 / System Card  
**工程范式：** 统一推理模型路线——推理模型学会在何时用工具，以及如何将工具整合到推理过程中。

## 设计哲学

o3 和 o4-mini 将推理模型推到新高度，核心创新是 **推理与工具使用的深度融合**。此前 o1 仅能思考，o3 则训练模型在思考过程中主动决定何时调用工具（浏览器、代码执行器、文件解析器等）以及如何利用工具结果进一步推理。

关键信号："these models are trained to reason about when and how to use tools to produce detailed and thoughtful answers in the right output formats, typically in under a minute."

o3 是当时 OpenAI 最强大的推理模型；o4-mini 是为开发者打造的更小、更快版本。

## 关键架构决策

- **工具推理：** 模型在 CoT 中主动生成工具调用，并将工具输出纳入后续推理
- **视觉推理：** 显著增强的图像理解和多模态推理能力
- **Sandbagging 评估：** 引入更严格的能力隐藏检测
- **PersonQA 回归：** 在 PersonQA 上 o4-mini 出现幻觉回升（低于 o1 和 o3）
- **定价：** o3 $10/$40 in/out per million tokens；o4-mini $2.50/$10 in/out per million tokens

### 性能概览

| 模型 | 定价（输入/输出 per 1M tokens） | 定位 |
|------|------------------------------|------|
| o3 | $10 / $40 | 最强推理模型 |
| o4-mini | $2.50 / $10 | 开发者优化的快速推理 |
| o3-pro | 更高 | Pro 用户的深度思考版本 |

### PersonQA 幻觉评估

| 模型 | 得分 |
|------|------|
| o1 | 0.16 |
| o3 | 0.33 | 
| o4-mini | 低于 o1 和 o3 |

## 范式对比

| 维度 | o3 | o1 | GPT-4o |
|------|-----|-----|--------|
| 工具整合 | 原生推理中调用 | ❌ | 函数调用（非推理） |
| 推理时缩放 | 更强 | ✅ | ❌ |
| 视觉推理 | 显著提升 | 有限 | 好 |
| 代码能力 | SOTA | 好 | 中等 |
| 定价 | $10/$40 | $15/$60 | $2.50/$10 |

## 可复用的工程经验

1. **推理+工具的整合是下一阶段大模型的标配能力** —— o3 证明纯推理模型已经不够，模型需要能行动
2. **开发者版本（o4-mini）的独立优化至关重要** —— 专业用户需要低成本、快速推理的专用模型
3. **Sandbagging 检测将成为安全报告的标准章节** —— 更强的模型带来更强的隐藏能力动机
4. **推理模型的幻觉问题不可忽视** —— o3 在 PersonQA 上的表现提醒：更多推理不一定意味着更少幻觉
