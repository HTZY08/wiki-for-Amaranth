---
title: Gemini 4 Argon / Carbon / Neon — 家族分型替代单点旗舰
date: 2026-10-01
source: "https://deepmind.google/models/gemini"
---

# Gemini 4：一个家族，三种性格

**发布日期：** 2026 年 10 月（Gemini 4 Argon 发布月；官方模型页未标注具体日期）；Gemini 4 Neon 为 2026 年 11 月
**来源：** https://deepmind.google/models/gemini
**工程范式：** 不追单点最强，按工作负载分型出模——长上下文、网络安全、agent 编码各给一个偏置过的型号，用评测矩阵而不是单一分数说话。

## 设计哲学

Gemini 4 的结构信息在评测矩阵里：官方同时列出 Argon、Carbon、Neon、Hydrogen 四条线，并各自对位不同对手（Argon 对 GPT-6 Astra / Claude Opus 5.5；Carbon 对 GPT-6 Astra / Claude Fable 5.1；Neon 对 Claude Opus 5.5 / GPT-6.2 Sol；Hydrogen 对 Claude Sonnet 5.5 / GPT-6.1 Terra）。这说明产品线是按**价位与工作负载**切分的，而不是按"代际大小"切分。

代价也很明显：Argon 在通用能力指数上并不领先（AA Index v5.0 为 50，Carbon 59、Neon 61），但在长上下文与部分企业工作流上被单独调优——官方合作伙伴证言里反复出现"跨文档取证""图表召回""100× 运行时压缩"这类具体场景，而不是通用智能宣称。

## 关键架构决策

- 参数规模、层数、MoE 配置、注意力选型、训练数据：**官方未披露**。
- **安全工程**（官方 Argon 专页要点）：拒答有害请求同时保留双重用途科研空间；官方称 Argon 是"迄今对间接 prompt injection 最有韧性"的型号；对 CoT 与动作做错位监控并在必要时中止执行；在高风险训练/评估前对沙箱做隔离封存。
- **能力分型**（据 Google 官方 10 月更新）：Argon 偏复杂编码与金融工作流；Carbon 偏长程工程与网络安全防御；Neon 为 11 月新增的更高一档；Hydrogen 偏小型高性价比。

## 关键结果

官方评测矩阵中的关键数字（均为 DeepMind 自报，方法页 deepmind.google/models/evals-methodology/gemini-4-*）：

| 维度 | 基准 | Gemini 4 Argon | 对照 |
| --- | --- | --- | --- |
| 通用 | AA Index v5.0 | 50 | GPT-6 Astra 57 / Opus 5.5 58 |
| 长上下文 | GraphWalks（256k→1M，BFS F1） | **84.2%** | GPT-6 Astra 71.8% / Carbon 96.2% |
| Agent 编码 | FrontierSWE 2 | 55.0% | GPT-6 Astra 65.5% / Carbon 61.2% |
| Agent 编码 | Terminal-Bench 4.0 (AA) | 57.1% | Carbon 65.2% / Astra 59.1% |
| 计算机操作 | OSWorld-2.1（offline） | 74.7% | Carbon 81.5% / Opus 5.5 87.2% |
| 知识工作 | AutomationBench (Zapier) | 51.3% | Carbon 53.9% / Astra 41.4% |
| 知识工作 | Vending-Bench 2（期末余额） | $13,718 | Carbon $16,484 |
| 多模态 | Chartography | 71.6% | Astra 71.0% / Fable 5.1 46.2% |
| 科学数学 | RiemannBench | **76.0%**（家族最高） | Carbon 72.0% |
| 网络安全 | ExploitGym | 42.0% | Carbon 54.8% |
| 网络安全 | SEC-bench Pro | 83.4% | Carbon 88.2% |

家族内对比可见设计意图：Carbon 在编码、网络安全、长上下文上全面领先；Argon 在数学（RiemannBench 76.0）与通用知识工作上相对更好；Neon（11 月）把 AA Index 推到 61，并在 SWE-sweep 上给出 39.0%（Mini-SWE harness 下 12.8%），这是很值得注意的 harness 敏感度——同一个模型换 harness 分数掉 26 个点。

## 范式对比

Neon 的 SWE-sweep 双 harness 数据（39.0% provider harness vs 12.8% mini-SWE）和 Argon/Carbon 的"内测 vs AA 复测"混排，说明 DeepMind 在评测透明度上比多数同行更愿意暴露弱点，但也意味着跨公司比较必须看清 harness。相比之下，z.ai 在 GLM-5.3 报告里把评测脚手架（Claude Code 2.1.207）与反作弊白名单写得很细，DeepSeek 则直接报"每 token KV 字节"这种系统指标——三家各自的透明点不同，不能混读。

## 社区评价

本次检索未取得可引用的 HN / Reddit 技术讨论原文，故不转述。

## 可复用的工程经验

1. **按工作负载分型，比堆一个全能模型更容易打准场景**。同一底座体系下给长上下文、网络安全、通用知识各一个偏置型号。
2. **报分数必须带 harness**。同一模型 39.0% / 12.8% 的差距说明脚手架是能力的一部分。
3. **把"抗 prompt injection"当独立工程目标**。对 agent 产品而言，这比多两分通用智能更值钱。
4. **沙箱在执行前封存**。高风险评估与训练前先隔离，能避免评估污染与逃逸。
5. **对外给伙伴场景证据**，不只给排行榜：跨文档取证、图表召回这类具体能力描述更能说明取舍。
