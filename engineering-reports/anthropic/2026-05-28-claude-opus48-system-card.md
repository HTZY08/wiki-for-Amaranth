---
title: Claude Opus 4.8 — 诚实性与协作可靠性的渐进式迭代
date: 2026-05-28
source: https://www-cdn.anthropic.com/0b4915911bb0d19eca5b5ee635c80fef830a37ea.pdf
---

# Claude Opus 4.8 System Card — 诚实性与协作可靠性的渐进式迭代

**发布日期：** 2026年5月28日
**来源：** [Claude Opus 4.8 System Card (PDF)](https://www-cdn.anthropic.com/0b4915911bb0d19eca5b5ee635c80fef830a37ea.pdf) · [官宣博客](https://www.anthropic.com/news/claude-opus-4-8)
**工程范式：** 渐进式可靠性迭代——不追求架构突破，而是在 Agent 能力、诚实性和对齐评估上做系统性打磨

## 设计哲学

Claude Opus 4.8 是 Anthropic 目前最强的通用访问模型，但它的升级幅度刻意保持在"渐进式"范围内。核心约束是：**在 Mythos 级模型（Glasswing 项目）的安全评估尚未完成前，通过工程迭代最大化现有架构的可靠性和诚实性**。

面对这一约束，Anthropic 选择了三线发力：
- **Agent 任务可靠性**——在 Claude Code 中引入 Dynamic Workflows（数百个并行子 agent + 自动验证），大幅提升代码库级迁移的端到端成功率
- **诚实性**——训练模型更频繁地报告不确定性，减少对不可靠结论的过度自信
- **对齐评估深度**——首次在系统卡中引入基于真实内部对话的审计会话，提升对齐评估的现实相关性

**放弃了什么？** 放弃了推出一款"更聪明但更不透明"的模型，转向将 Mythos 级能力保留在受限访问层，Opus 线则专注于可靠性和可监控性。

## 关键架构决策

### 训练数据与过程

- 预训练：来自互联网的公开信息、公开/私有数据集、以及合成数据
- 后训练：大量微调和对齐训练，基于 Claude 的宪法原则
- Crowd workers：通过数据工作平台合作，遵循公平薪酬标准
- 对外发布前进行了广泛的安全评估和外部测试

Anthropic 未披露 Opus 4.8 的具体架构参数（层数、参数量、MoE 配置等），仅描述为"对 Opus 4.7 的升级"。

### Effort Control 机制

Opus 4.8 引入了可调节的"思考努力度"（effort control）：
- **默认（High）**：思维链长度与 Opus 4.7 默认值相近，但性能更好
- **Extra / Max**：更长的推理链以获得更好结果
- **Low**：更快响应，降低速率限制消耗

这一机制直接影响 benchmark 结果——以下所有数字均基于 Max effort 配置。

### Dynamic Workflows（Claude Code）

- 模型可规划任务并将工作分解给数百个并行子 agent
- 自动验证输出后才向用户报告
- 实测可完成从启动到合并的代码库级大规模迁移（数十万行代码）

## 关键结果

所有结果来自系统卡中标准配置（adaptive thinking at max effort, 默认采样参数, 5 trials 平均）：

| 评估 | 子项 | Opus 4.8 | Opus 4.7 | GPT-5.5 | Gemini 3.1 Pro |
|------|------|----------|----------|---------|-----------------|
| SWE-bench | Verified | **88.6** | 87.6 | - | 80.6 |
| SWE-bench | Pro | **69.2** | 64.3 | 58.6 | 54.2 |
| SWE-bench | Multilingual | **84.4** | 80.5 | - | - |
| SWE-bench | Multimodal | **38.4** | 34.5 | - | - |
| Terminal-Bench | 2.1 | 74.6 | 66.1 | **78.2** | 70.3 |
| BrowseComp | single-agent | 84.3 | 79.8 | 84.4 | **85.9** |
| BrowseComp | multi-agent | **88.5** | - | - | - |
| Humanity's Last Exam | No tools | **49.8** | 46.9 | 41.4 | 44.4 |
| Humanity's Last Exam | With tools | **57.9** | 54.7 | 52.2 | 51.4 |
| OSWorld-Verified | - | **83.4** | 82.8 | 78.7 | 76.2 |
| GPQA Diamond | - | 93.6 | **94.2** | - | 94.3 |
| ChartQAPro | No tools | **69.4** | 67.6 | - | - |
| ChartQAPro | With tools | **72.3** | 69.8 | - | - |
| ScreenSpot-Pro | No tools | **82.3** | 79.5 | - | - |
| Finance Agent v2 | - | **53.9** | 51.5 | 51.8 | 43.0 |
| Automation Bench | - | **15.5** | 9.9 | 12.9 | 9.6 |
| GraphWalks BFS | 256K | **85.9** | 76.9 | 73.7 | - |
| GraphWalks Parents | 256K | **99.3** | 93.6 | 90.1 | - |

**其他重要结果：**
- **FrontierSWE**：Opus 4.8 在 mean@5（平均排名 2.74）和 best@5（2.26）均排 #1，超过 Opus 4.7（#3, 4.15/3.68）和 Opus 4.6（#4, 4.94/4.09）
- **Online-Mind2Web**：84%，超过 Opus 4.7 和 GPT-5.5（来自博客原文）
- **Legal Agent Benchmark**：首个突破 10% all-pass 标准的模型
- **Super-Agent Benchmark**：唯一完成每个 case 端到端的模型
- **CursorBench**：在每个 effort 级别上都超过前代

### 诚实性提升

- Opus 4.8 约是 Opus 4.7 的**1/4**概率在代码审查中对缺陷保持沉默
- 在虚假前提测试中（false premise questions），诚实率显著高于前代
- 在身份诚实性测试中，97%的情况下会承认自己是 AI（Mythos Preview 为 100%）

## 范式对比

与 Anthropic 自己的产品线对比：

| 维度 | Opus 4.7 → 4.8 | Mythos Preview | Fable 5 |
|------|----------------|----------------|---------|
| 定位 | 通用最强可访问模型 | 受限前沿模型（Project Glasswing） | 创意/娱乐场景专用 |
| 安全评估深度 | 全量系统卡 + 真实会话审计 | 更严格的安全测试 | 标准安全测试 |
| 对齐 | 🔺 改善（低于 Mythos） | 🔝 最佳对齐 | 标准对齐 |
| Agent 能力 | 🔺 显著提升 | 🔝 最强 | 中等 |

与业界的对比关键差异：
- **vs GPT-5.5**：Opus 4.8 在 SWE-bench Pro(+10.6pp)、OSWorld(+4.7pp) 等编码/Agent 任务上显著领先，但 Terminal-Bench(-3.6pp) 有所不及
- **vs Gemini 3.1 Pro**：在几乎所有编码和 Agent 任务上全面领先，差距显著
- **vs Gemini 3.5 Flash**：Gemini 3.5 Flash 在 Finance Agent v2(57.9%) 和 MCP Atlas(83.6%) 上略领先 Opus 4.8

## 社区评价

Zvi（知名 AI 安全评论员）在系统卡分析中指出：
- Opus 4.8 "更愿意报告不确定性，极不可能自信地给出错误答案"
- 发布节奏为 41 天（Opus 4.7 到 4.8），为 Anthropic 最快迭代速度
- 主要强调"诚实性"而非"能力跃升"

## 可复用的工程经验

1. **安全评估可作为差异化竞争力**：Anthropic 将系统卡中的对齐评估从静态 benchmark 扩展到基于真实内部会话的审计，为模型的诚实性和可监控性提供了更可靠证据
2. **渐进式迭代的节奏管理**：41 天迭代周期表明，前代模型（Opus 4.7）的推理优化和 Agent 能力已有充分工程基础，新一轮迭代可以专注于打磨可靠性和诚实性而不动架构
3. **Effort Control 工程化**：可调节思考努力度让同一模型在不同场景下灵活选择速度/质量权衡，这对 API 产品化和用户体验有明显价值
4. **Agent 框架的放大效应**：Dynamic Workflows（并行子 agent + 自动验证）让模型在代码库级任务上的表现远超单 agent 配置，表明 Agent 框架本身也是一种能力杠杆
