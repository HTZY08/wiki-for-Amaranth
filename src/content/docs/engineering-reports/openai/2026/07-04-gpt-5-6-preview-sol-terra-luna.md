---
title: GPT-5.6 Preview System Card — Sol/Terra/Luna 三级架构与美国政府审查下的受限发布
date: 2026-07-04
source: https://deploymentsafety.openai.com/gpt-5-6-preview
---

# GPT-5.6 Preview System Card：Sol / Terra / Luna

**发布日期：** 2026-06-26
**来源：** [OpenAI 部署安全中心](https://deploymentsafety.openai.com/gpt-5-6-preview) / [OpenAI 官方博客](https://openai.com/index/previewing-gpt-5-6-sol/)
**工程范式：** 能力分层（Sol/Terra/Luna）、subagent 加速的 ultra 推理模式、分层安全栈、美国政府参与的受限发布流程

## 设计哲学

GPT-5.6 的核心约束不再是纯粹的能力提升，而是 **安全分级 × 政府审查 × 能力分发的三角平衡**。

三个关键选择定义了这一代：

1. **能力分层而非模型变体**——告别 "nano/mini" 式的规模缩放任命名，改为 Sol（旗舰）/ Terra（均衡）/ Luna（快速低价）的**用例导向分层**。每层有自己的能力剖面、定价和安全配置。
2. **subagent 的 ultra 模式**——不是让单一模型思考更久，而是让模型学会委派子任务给 subagent 并行执行。这是 OpenAI 首次在产品层推出自主任务分发能力。
3. **以安全性为代价换取政府许可**——在美国商务部对 Anthropic 下架 Claude Fable 5 后的监管环境下，OpenAI 主动将 GPT-5.6 置于政府审查流程，以有限预览（约 20 家组织）换取未来广泛可用。

放弃的是：即时全面可用性。这是 OpenAI 第一次在模型发布时出于政府要求而非技术原因限制发布范围。

## 关键架构决策

### 模型家族

| 模型 | 定位 | 输入价格（per 1M tokens） | 输出价格（per 1M tokens） |
|------|------|--------------------------|--------------------------|
| **Sol** | 旗舰：复杂推理、安全研究、长时间编码 | $5.00 | $30.00 |
| **Terra** | 均衡：大规模生产环境的可靠性能 | $2.50 | $15.00 |
| **Luna** | 快速低价：摘要、草稿、日常自动化 | $1.00 | $6.00 |

- Terra 性能与 GPT-5.5 相当但成本为一半
- Luna 在多项测试中接近 GPT-5.5 水平

### 推理策略

- **`max` reasoning effort**：给 Sol 最长的内部思考时间（延续 GPT-5.4/5.5 的 thinking 范式）
- **`ultra` mode（新引入）**：超越单 agent 能力边界，通过 subagent 分解复杂任务并行执行
  - Sol 在 ultra 模式下达到 Terminal-Bench 2.1 的 91.91%（vs max 模式的 88.76%）
- **Effort scaling curves**：系统卡中首次全面呈现性能随 reasoning effort 变化的曲线，而非仅报告单点分数

### 安全架构：分层安全栈

GPT-5.6 引入 OpenAI 至今最复杂的安全栈：

1. **模型级拒绝**：训练中的安全微调，禁止被禁的网络安全协助（包括伪装意图的 jailbreak 尝试）
2. **实时激活分类器**（新增）：Sol 和 Terra 配有领域敏感激活分类器，监控生成过程，检测潜在违规时暂停生成
3. **二级推理模型审查**：触发时由更大的推理模型审查对话上下文，评估是否应阻止输出
4. **账户级跨对话分析**：识别跨对话的恶意行为模式，区分防御性安全工作和恶意利用
5. **自动红队**：投入超过 700,000 A100e GPU 小时进行通用 jailbreak 搜索

安全分类覆盖三个能力域：
- **网络安全**：High 风险（未达 Critical 阈值，无法自主完成端到端攻击）
- **生物/化学**：High 风险
- **AI 自我改进**：未达 High 阈值

即使 Luna 和 Terra 也被归类为网络安全和生物/化学能力的 High 风险。

### 推理缓存

- 引入显式 cache breakpoints
- 30 分钟最低缓存生存期
- cache writes：1.25× uncached input rate
- cache reads：90% cached-input discount
- 比 GPT-5.5 更可预测的缓存计费

### Cerebras 硬件部署

- GPT-5.6 Sol 将登陆 Cerebras 硬件（2026 年 7 月）
- 目标速度：高达 750 tokens/sec

## 关键结果

### Terminal-Bench 2.1（命令行编码）

| 模型/模式 | 得分 |
|-----------|------|
| GPT-5.6 Sol (ultra) | **91.91%** |
| GPT-5.6 Sol (max) | **88.76%** |
| Claude Mythos 5 | **88%** |
| GPT-5.5 | **83.4%** |

### Agent's Last Exam

| 模型 | Code mode |
|------|-----------|
| GPT-5.6 Sol | **50.9%**（唯一超过 50% 的模型）|
| GPT-5.6 Luna | 略超 GPT-5.5 |

### ExploitBench（网络安全）

- GPT-5.6 Sol 使用约 1/3 的 Mythos Preview 输出 token 即达到竞争性性能
- 在 ExploitGym 上，Sol/Terra/Luna 随 reasoning 增加均显示显著改善

### 生物学 / 基因学

- Sol 和 Terra 在 GeneBench v1（长程基因组学和定量生物学分析）上优于 GPT-5.5 和 GPT-5.4
- Sol 使用更少 token 达到更强结果

### 安全评估（Production Benchmarks）

- GPT-5.6 Sol 与 GPT-5.5 的整体违规率大致相当
- 性相关内容违规率：从 0.05% 增加到 0.07%（相对增加 40%，但绝对率仍然很低）
- 心理健康违规率：从 0.03% 降低到 0.02%（降低约 40%）
- 所有 Safeguard 评估中，模型行为满足 OpenAI 的安全标准

## 范式对比

### vs Anthropic Claude (Fable 5 / Mythos 5)

- 两者都经历政府审查——Anthropic 被直接下架，OpenAI 主动受限预览
- Sol 在 ExploitBench 上接近 Mythos Preview 但使用少得多 token
- Pricing：Sol $35/M tokens vs Fable 5 $60/M tokens，OpenAI 定价显著更低
- Anthropic 的 RSP 3.0 框架更强调自主性风险评估；OpenAI 的 Preparedness Framework 更关注能力分级

### vs GPT-5.5

- 定价不变（Sol = GPT-5.5 价格），但 Terminal-Bench 从 83.4% 升至 91.91%
- 安全栈复杂度大幅增加（激活分类器、二级审查）
- 引入子代理能力（ultra mode）是架构性的增量

### vs 其他厂商

- 对比 Z.ai GLM-5.2（$5.80/M tokens）：GPT-5.6 定价从 $7（Luna）到 $35（Sol）
- 对比 DeepSeek-V4（$0.42-$1.305/M tokens）：GPT-5.6 价格是 5-30 倍
- 在长程编码上失去绝对统治力——GLM-5.2 在 PostTrainBench 上已超过 GPT-5.5

## 社区评价

- HN/Reddit 焦点主要在于政府介入审查流程的先例，而非技术内容本身
- 行业评论指出：当 frontier 模型发布变成"Negotiated deployment"时，意味着安全监管已成为实际的市场准入壁垒
- 开发者关注 Cache breakpoints 和 30 分钟缓存策略对 agentic loop 成本控制的实际影响
- VentureBeat：OpenAI 的定价策略被解读为从"追求最大用户量"转向"价值定价+政府合约"
- Cerebras 合作：部分开发者认为这是对 NVIDIA 垄断的分散策略

## 可复用的工程经验

1. **能力分层比参数缩放任命更有利于商业化**：Sol/Terra/Luna 分别对应不同的用例剖面和成本结构，而不是简单的"大中小"。
2. **推理 effort 曲线基准测试**：报告单点得分隐藏了大量信息。展示 performance-effort 的 scaling curve 能让使用者做出更好的性价比决策。
3. **Subagent 加速模式**：当任务可分解时，subagent 并行执行比单一模型更长的 chain-of-thought 效率更高。Terminal-Bench 上 ultra 模式比 max 模式提升 3%+。
4. **Prompt caching 的成本可预测性设计**：显式 cache breakpoints + 30 分钟最小存活期，让 agentic loop 的成本从"不可预测波动"变为"可建模的固定模式"。
5. **安全设计的分层冗余**：训练级 + 推理级 + 账户级 + 持续测试级——任一单层可被攻破时仍有其他层兜底。对需要处理敏感数据的企业应用同样适用。
