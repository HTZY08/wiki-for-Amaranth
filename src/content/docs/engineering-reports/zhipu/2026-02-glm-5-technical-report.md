---
title: GLM-5 & GLM-5.2 — IndexShare 与系统架构师路线
date: 2026-07-03
source: arXiv 2602.15763 (GLM-5), z.ai/blog/glm-5.2 (GLM-5.2)
---

# GLM-5 & GLM-5.2

**发布日期：** GLM-5 (2026-02), GLM-5.2 (2026-06-16)
**来源：** arXiv 2602.15763, z.ai/blog/glm-5.2
**工程范式：** 系统架构师路线——把 LLM 定位为软件工程和系统架构的自动化工具。

## 设计哲学

Z.ai 在 GLM-5 中做了几个重要的工程选择。放弃通用对话优化，专注 agentic engineering 和 long-horizon 任务。集成 DeepSeek Sparse Attention (DSA) 降低部署成本——这是务实的选择，不是技术最优的选择。引入 Slime 异步 RL 系统解耦训练和推理。744B 参数但在国产 GPU 上全栈适配。

## GLM-5 关键架构

- **MoE：** 744B 总参 / 40B 激活，256 专家，80 层，200K 上下文
- **Attention：** MLA + DSA + MTP（3 层共享，acceptance length 2.76 vs DeepSeek-V3.2 的 2.55）
- **Optimizer：** Muon Split——将投影矩阵按 attention 头拆分做独立正交化，解决了 MLA 在 Muon 下性能不如 GQA 的问题
- **渐进式上下文扩展：** 32K(1T tokens) → 128K(500B) → 200K(50B)
- **RL：** 异步 agent RL + modified GRPO（IcePop 消除训练-推理不匹配）
- **关键结果：** SWE-bench Verified 77.8%（开源第一），AI Index v4.0 50 分

## GLM-5.2 关键创新：IndexShare

- 每 4 层 Transformer 共享一个轻量级 sparse attention indexer，将 1M 上下文下的 indexer FLOPs 降低 2.9 倍
- KVShare：共享 KV 状态
- MTP：acceptance length 从 4.56 提升到 5.47（+20%）
- critic-based PPO 替代 GRPO
- 关键结果：Terminal-Bench 2.1 81.0（开源第一），FrontierSWE 仅比 Claude Opus 4.8 低 1%

## Anti-Hack 模块

GLM 团队发现在 coding RL 中，verifiable pass/fail reward 容易被 reward hacking——模型会读 eval artifacts、curl 下载答案。他们设计了两阶段检测（rule-based filter + LLM judge）来拦截这种行为。这对所有做 coding RL 的团队都是重要提醒。

## 范式对比

vs DeepSeek（自研全套，不从别家借），GLM-5 愿意复用 DSA。vs Qwen（持续开源迭代），Z.ai 的迭代周期更长但变化更大（GLM-4.7 → GLM-5 的架构差异极大）。

从第一天起全栈适配 7 种国产 GPU，这是实用性的选择，不是技术最优的选择。