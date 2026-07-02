---
title: Kimi K2.7 Code — 开放权重模型进入 Copilot
date: 2026-07-03
source: marktechpost.com/2026/06/12/moonshot-ai-releases-kimi-k2-7-code, github.com/moonshotai/kimi-k2
---

# Kimi K2.7 Code

**发布日期：** 2026-06-12
**来源：** marktechpost.com, github.com/moonshotai/kimi-k2
**工程范式：** 超大 MoE + Agent Swarm 路线——1T 参数模型配 300 个子 agent 的大规模协调架构。

## 设计哲学

Moonshot 的核心约束是长程编码任务的可靠性——单次对话需要数千步 agent 操作，任何一步出错都导致失败。他们相信用更多参数 + 更多子 agent 来解决：K2.7-Code 的 384 专家提供高质量的生成能力，Agent Swarm 系统的 300 个子 agent 提供执行广度。

## 关键架构决策

- **MoE：** 1T 总参，384 专家，8 active per token + 1 shared expert
- **Agent Swarm：** 300 domain-specialized sub-agents，最高 4000 步连续执行
- **上下文：** 原生长上下文设计，优化 agent 轨迹的持续跟踪
- **发布：** 开放权重（Modified MIT），上线 GitHub Copilot（首个开放权重模型）
- K2.6（1.04T 总参的稀疏 MoE 视觉语言模型）on Lambda 支持 EAGLE-3 speculative decoding

## 关键结果

Code Bench v2: K2.6 从 50.9 跃升至 K2.7 的 62.0（+21.8%），缩小了与 GPT-5.5（69.0）和 Opus 4.8（67.4）的差距。SWE-bench 上 K2.5 曾达到开源最高水平（76.8%+）。

## 范式对比

vs DeepSeek V3.2（671B/37B，精简 MoE），Kimi 走超大 MoE 路线，参数量大但推理质量更高。vs Qwen3-Coder-Next（80B/3B，极致精简），Kimi 走另一极端——用大参数换可靠性。

## 社区评价

Devansh 的 Medium 文章称 Kimi K2 是「更好的 DeepSeek」。Reddit 上聚焦 Agent 编码 benchmark，K2.7 vs GPT-5.5 vs Opus 4.8 横向对比。K2.7 Code 上架 Cursor。