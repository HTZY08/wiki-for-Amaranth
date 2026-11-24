---
title: Gemini 4 Carbon — 底座不动，靠后训练把能力指数从 50 拉到 59
date: 2026-11-10
source: "https://deepmind.google/models/model-cards/gemini-4-carbon"
---

# Gemini 4 Carbon：同一底座的偏置型号

**发布日期：** 2026-11-10（模型卡；评测数据官方标注为 2026 年 10 月口径）
**来源：** https://deepmind.google/models/model-cards/gemini-4-carbon
**工程范式：** 底座共享、后训练分型——Carbon 直接基于 Gemini 4 Argon，架构、数据、硬件、软件全部"见 Argon 模型卡"，只在"多花思考 token、跑更长的验证回路"上做偏置，用配置化的 thinking level 把同一套权重复用成不同档位的产品。

## 设计哲学

这份模型卡的信息量在它**没有**写的东西里。Architecture、Model Data、Implementation、Acceptable Usage、Safety Policies 五节的正文全部是"基于 Gemini 4 Argon，详见 Argon 模型卡"——即 Carbon 没有换架构，也没有重新预训练。

官方给出的能力差异解释只有一句：Carbon 用**比 Argon 更多的 thinking token**去探索假设、深度推理、跑更长的验证回路，并配**可配置的 thinking level** 在质量、延迟、成本之间取舍。

这解释了一个反常的数字：同一底座，AA Index v5.0 从 Argon 的 50 升到 59。如果架构没动，这 9 分就只能来自后训练与推理期计算——这是"后训练 + test-time compute 比换基座更便宜"路线在旗舰级产品上的一个公开样本。

代价同样明确：官方在已知局限里承认"在更高 thinking level 下模型会消耗更多 token 来最大化表现"，并可能出现偶发变慢或超时。也就是说，分数换的是推理成本，不是免费的。另一个被放弃的方向是通用性最优——Carbon 在家族里并非全维度最强（Neon 的 AA Index 为 61）。

## 关键架构决策

- **规模、层数、MoE 配置、注意力选型**：官方未披露，模型卡全部指向 Gemini 4 Argon。
- **上下文**：输入输出合计最长 1M token；文本、图像、音频、视频输入，文本输出。
- **推理期计算**：varying thinking level，是这一型号唯一的"架构级"设计变量。
- **安全能力门控放在渠道层，不在权重层**：高危网络安全能力（漏洞发现、利用验证、修补）只通过 **Fairwind Program** 对已验证的防御方开放；同一份模型卡说明网络安全类评测分数"反映通过 Fairwind Program 访问时的表现"。这是把双重用途能力做成**分发策略**而非模型内拒答的做法。
- **知识截止**：2026 年 3 月。
- **安全对照（相对 Argon 的百分点变化）**：文本安全 +3.50pp、多语种安全 +3.55pp、图到文安全 −1.00pp、语气 +1.10pp、无理由拒答 +1.10pp。官方注明这套评测已改进，**不与此前模型卡的数字直接可比**。

## 关键结果

以下全部出自 Gemini 4 Carbon 模型卡（官方自报，2026 年 10 月口径），同一张表里并列了四家模型：

| 维度 | 基准 | Carbon | Argon | GPT-6 Astra | Opus 5.5 | Fable 5.1 |
| --- | --- | --- | --- | --- | --- | --- |
| 通用 | AA Index v5.0 | 59 | 50 | 57 | 58 | 49 |
| 通用 | Vals Index v2.2 | 70.4% | 69.2% | 65.0% | 70.2% | — |
| Agent 编码 | SWE-sweep | 9.6% | 4.3% | 9.5% | 3.6% | 2.9% |
| Agent 编码 | FrontierSWE 2 | 61.2% | 55.0% | 65.5% | 62.3% | 56.3% |
| Agent 编码 | Terminal-Bench 4.0 (AA) | 65.2% | 57.1% | 59.1% | 59.6% | 52.0% |
| 计算机操作 | Agents' Last Exam v1.1 | 77.4% | 69.0% | 73.1% | 71.6% | — |
| 计算机操作 | OSWorld-2.1（离线子集） | 81.5% | 74.7% | 80.9% | 87.2% | 76.8% |
| 知识工作 | AutomationBench (Zapier) | 53.9% | 51.3% | 41.4% | 42.5% | 31.4% |
| 知识工作 | Vending-Bench 2（期末余额） | $16,484 | $13,718 | $15,515 | $9,235 | $5,422 |
| 多模态 | Chartography | 72.5% | 71.6% | 71.0% | 66.3% | 46.2% |
| 多模态 | Blueprint-Bench 2 | 58.6% | 54.4% | 49.7% | 51.2% | 41.9% |
| 长上下文 | GraphWalks（256k→1M，BFS F1） | 96.2% | 84.2% | 71.8% | 66.8% | 65.0% |
| 科学数学 | RiemannBench | 80.0% | 76.0% | 72.0% | 69.6% | 65.6% |
| 科学数学 | Terminal-Bench-Science 0.1 | 64.8% | 52.9% | 63.3% | 59.0% | 43.3% |
| 网络安全 | CWE-bench | 71.0% | 68.0% | 68.0% | 67.0% | 58.0% |
| 网络安全 | ExploitGym | 54.8% | 42.0% | 42.4% | 34.5% | — |
| 网络安全 | SEC-bench Pro | 88.2% | 83.4% | 85.4% | — | — |

读法上有两点必须注意：

1. **同底座 delta 才是这份卡的核心证据**。GraphWalks 84.2→96.2（+12.0pp）、Terminal-Bench-Science 52.9→64.8、ExploitGym 42.0→54.8，这些都不是换基座能解释的，只能来自后训练与更多推理 token。
2. **口径不可跨表混用**。SWE-sweep 上 Carbon 9.6% 与 FrontierSWE 2 上 61.2% 差了一个量级，模型卡本身就说明"harness 是能力的一部分"；引用任何单点分数时必须带 harness 名。

## 范式对比

- **对 Anthropic**：Opus 5.5 在 OSWorld-2.1 上 87.2% 明显领先 Carbon 的 81.5%，说明 Anthropic 把计算机操作当主战场；而 Carbon 的优势集中在长上下文、编码终端任务、企业工作流自动化（AutomationBench 53.9% vs 42.5%）。
- **对 OpenAI**：GPT-6 Astra 在 FrontierSWE 2 上 65.5% 仍高于 Carbon 61.2%，但 Carbon 在 Terminal-Bench 4.0（65.2% vs 59.1%）与 Terminal-Bench-Science（64.8% vs 63.3%）反超——同样是终端类任务，两家在不同 harness 上的强弱关系是相反的。
- **对自家 Neon**：Neon 的 AA Index 61 更高，Carbon 不去抢这个位置，而是保留网络安全与长程工程两个专门场景。DeepMind 的产品逻辑是**矩阵覆盖**而不是单一冠军。

## 社区评价

本次检索未取得可引用的 HN / Reddit 技术讨论原文，故不转述任何社区观点。第三方独立复测（如 Artificial Analysis 的 v5.0 指数）与官方数字的一致性，需要在下一次独立榜单更新后才能核对。

## 可复用的工程经验

1. **底座共享、后训练分型，是当前最便宜的多产品线策略**。同一套权重，用 thinking level 与 post-training 偏置切出高端/中端两档，比训两个模型省一个数量级的算力。
2. **要把"同底座 delta"当成架构实验的替代品**。GraphWalks +12pp 这种同权重对照，比跨公司比分数更能说明问题出在哪个环节。
3. **双重用途能力门控在渠道层**。Fairwind Program 这种"分数标注按访问通道给出"的做法，比在模型内硬拒答更能同时保住防御方可用性与滥用面控制。
4. **报分数必须同行列对手型号 + harness**。这份卡把 GPT-6 Astra / Opus 5.5 / Fable 5.1 放在同一张表里，可核对性远高于只报"领先 X%"。
5. **安全评测改进后要显式声明不可比**。官方主动写明"评测已改进，不与历史模型卡直接可比"——这是避免自己数据集漂移的最省事做法。
6. **推理期 token 是新的成本变量**。部署前要把 thinking level 与 P99 延迟、每任务成本一起标定，否则高分会在账单上变成惊吓。
