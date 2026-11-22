---
title: Claude Fable 5.2 / Mythos 5.2 — 同一权重，两套护栏，按用途发钥匙
date: 2026-11-09
source: "https://www.anthropic.com/claude-fable-and-mythos-5-2"
---

# Claude Fable 5.2 与 Mythos 5.2：安全分层做成产品结构

**发布日期：** 2026-11-09
**来源：** https://www.anthropic.com/claude-fable-and-mythos-5-2
**工程范式：** 一个底层模型，两种交付形态——能力不再按"型号大小"分层，而按"护栏强度与准入资格"分层；同时把 effort 档位当作成本控制器卖给用户。

## 设计哲学

Anthropic 的做法在结构上很清楚：Fable 与 Mythos 是**同一个底层模型**，Fable 带强网络与生物护栏、对所有人开放；Mythos 护栏更松，只发给通过 Life Sciences / Cyber Verification Program 审核的机构。这不是两个模型，是一个模型的两条准入门。

另一个值得注意的取舍是定位：官方明确说"大多数编码与知识工作请先用 Opus 5.5"，Fable/Mythos 留给最难、最开放的技术工作；并且允许它当 Advisor（小模型来咨询它）或 Orchestrator（它把简单任务派给小模型）。也就是说，最强模型被设计成**稀疏调用的专家**，而不是默认入口——这是成本结构决定的产品形态。

## 关键架构决策

- 参数规模、层数、注意力与 MoE 配置、训练数据：**未披露**。
- **effort 分层**：Low / Medium / High / Xhigh / Max 多档，官方公布的是"每档的准确率 vs 每任务成本"曲线，而不是单一分数。这是把推理期算力当作产品参数来卖。
- **Fast mode**：可选，token 生成速度最高 2.5×，价格 $16 / $80 per MTok（标准价 $8 / $40）。
- **护栏工程**：Fable 5.2 的网络与生物护栏"与 5.1 同样稳健但产生更少的无谓拦截"；官方称实现了"迄今最强的防蒸馏攻击保护"；新增针对沙箱逃逸等具体行为的评估。
- **速度**：输出生成比 5.1 快最多 30%。

## 关键结果

官方对照表（除注明外均为开启护栏、各自最高 effort；Mythos 5.2 用于减少护栏干扰的测试）：

- Agentic coding — FrontierCode 2.0：Fable 5.2 **49.1%**（Xhigh），Fable 5.1 32.4%，Opus 5.5 45.5%，GPT-6 Astra 42.8%，Gemini 4 Carbon 41.1%。
- Agentic coding — FrontierSWE v2：**69.9%**，对比 Opus 5.5 62.3%、GPT-6 Astra 65.5%、Gemini 4 Carbon 61.2%。
- Business workflows — AutomationBench：**51.4%**（Opus 5.5 42.5%、GPT-6 Astra 41.4%、Gemini 4 Carbon 53.9%）。
- Agentic scientific research — Terminal-Bench-Science 0.1：**74.6%**（Mythos 5.2 75.3%），Opus 5.5 58.7%，GPT-6 Astra 68.1%。
- Cybersecurity — CyScenarioBench：Mythos 5.2 **76.3%**（Mythos 5.1 61.7%）；CVE Rediscovery：Mythos 5.2 **89.6%**（5.1 为 78.3%）。
- Protein design — de novo binder design (24 hr)：Mythos 5.2 **85.1**（5.1 为 79.1）。
- Agentic search — WANDR（relaxed）：**82.1%**（5.1 68.7%，Opus 5.5 72.3%）。
- Computer use — OSWorld 2.1（offline 子集）：**89.3%**（Opus 5.5 87.2%，GPT-6 Astra 79.5%）。
- Robotics — RoboDojo Sim：**64.9%**（Fable 5.1 27.6%，Opus 5.5 39.4%）。
- Knowledge work — AA-Briefcase v1.1：66.1% rubric / **1785 Elo**（Opus 5.5 1800 Elo）；Remote Labor Index：**41.3%**（Opus 5.5 21.3%）。
- HLE（with tools）：**74.2%**；Chartography（no tools）：**73.4%**。

成本侧：FrontierCode 2.0 上，High effort 的 Fable 5.2 与 Opus 5.5 的最高分基本持平（45.3% vs 45.5%），每任务成本约为一半；HLE 上 Low effort 的 Fable 5.2 就能追平 Opus 5.5 的最高分，成本不到 1/10。

工程侧自述：Anthropic 核心代码库中超过 90% 已合并改动由 Claude 编写（人工指导）；一组 agent 用早期 Fable 5.2 把一个关键生产服务从 Python 迁到 Rust，启动速度约快 26 倍。

## 范式对比

和 OpenAI 的系统卡路线相比，Anthropic 把"安全"做成了**准入分层**而不是运行时监控；和 z.ai 相比，Anthropic 不公开底座（GLM-5.3 明说只做 post-training），也不比拼单点 cyber 分数（Mythos 5.2 在 ExploitBench 类任务上反而不如部分对手，官方自己列出了 CyScenarioBench 的分差口径）。真正的差异点在**评测方法学**：Anthropic 全篇在讲"准确率 vs 成本"曲线，把 effort 当变量；多数同行仍只给单点最优分。

## 社区评价

第三方媒体对"9 月还写文章呼吁放慢前沿节奏、11 月就发前沿模型"的时间差有不少评论；技术侧讨论多集中在 effort 档位的性价比和 prompt injection 数据（有转述称 Gray Swan 间接攻击成功率 4.09%、高于 5.1 的 1.02%）。该数字出自二手转述，**未在官方发布页核到**，引用前需回查系统卡原文。

## 可复用的工程经验

1. **同一权重两套护栏**是比"训练两个模型"便宜得多的分层方案，前提是护栏足够模块化、能产出可审计的准入流程。
2. **把 effort 做成显式旋钮并公开成本曲线**。用户能自己选"每任务多少钱"，比隐藏推理长度更可控。
3. **最强模型不该是默认入口**。设计成 Advisor/Orchestrator 的稀疏调用点，能在保能力的同时控住账单。
4. **护栏优化的目标函数是"少误杀"**：在保持同等安全的前提下减少无谓拦截，比"更严"更有工程价值。
5. **评测要报成本**。没有成本维度的编码榜单会系统性高估"全力推理"的价值。
