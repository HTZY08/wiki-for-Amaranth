---
title: Gemini 3.5 Flash — Agentic 能力密度路线
date: 2026-07-03
source: blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-5
---

# Gemini 3.5 Flash

**发布日期：** 2026-06-24
**来源：** Google AI Blog
**工程范式：** Agentic 能力密度路线——把前沿智能压缩到最快的推理速度上。

## 设计哲学

Google 的核心约束不是能力不够，而是让能力被实际使用。Gemini 3.5 Flash 选择在中低推理成本上提供接近前沿的能力，核心新增是 Computer Use——让模型能直接操作屏幕、点击、输入。

这个选择的信号意义：Google 认为 2026 下半年的竞争焦点已经从「谁能做最聪明的模型」转向「谁能让模型做最多的事」。

## 关键架构决策

- 架构细节未公开，Gemini 3.x 家族基于 MoE Transformer
- Computer Use：模型原生能力，非 RAG/外挂
- Agentic 能力：支持工具调用、屏幕操作、多步推理
- 多模态：延续 Gemini 家族的原生多模态设计

## 范式对比

vs Anthropic（专注安全降级），Google 专注 agentic 扩展。vs OpenAI（GPT-5.5 做统一模型），Google 做能力分层——Flash 做速度，Pro 做深度，Ultra 做极限。

## 可复用的经验

1. Computer Use 是下一个标配能力
2. 推理速度 vs 能力深度是 2026 年最重要的 trade-off，没有之一