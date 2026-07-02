---
title: MiMo-V2-Flash — MoE 路由与长上下文
date: 2026-07-03
source: arXiv 2601.02780
---

# MiMo-V2-Flash

**发布日期：** 2026-01
**来源：** arXiv 2601.02780
**工程范式：** MoE 路由 + 长上下文工程路线。

## 关键架构

- **规模：** 309B 总参 / 15B 激活的 MoE
- **Attention：** 混合注意力（SWA:global = 5:1），128-token sliding window
- **开源：** MIT 协议

## 关键结果

SWE-bench Verified 上接近 DeepSeek-V3.2 水平（72-73% vs 73-75%），AIME25 80-86%，GPQA-Diamond 80-87%。社区关注的后续版本 MiMo-V2.5-Pro 支持到 1M 上下文。

## 社区评价

知乎上有中文解读。小米公开了完整的技术报告（MIT 开源）。在 AI Index v4.0 上 V2.5 达到 54 分。