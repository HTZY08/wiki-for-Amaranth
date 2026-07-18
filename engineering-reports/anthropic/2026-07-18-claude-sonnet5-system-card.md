---
title: Claude Sonnet 5 System Card — Agentic Sonnet 时代的效率跃迁
date: 2026-07-18
source: https://anthropic.com/claude-sonnet-5-system-card
---

# Claude Sonnet 5 System Card — Agentic Sonnet 时代的效率跃迁

**发布日期：** 2026-06-30
**来源：** https://anthropic.com/claude-sonnet-5-system-card | https://www.anthropic.com/news/claude-sonnet-5
**工程范式：** Agentic 能力下放到 Sonnet 层级——以接近 Opus 级别的编码/工具使用/搜索能力，在 Sonnet 价格带上实现 agent 工作负载

## 设计哲学

Sonnet 5 的核心定位是 **弥补 Opus 与 Sonnet 之间的 agentic 能力鸿沟**。Anthropic 观察到：Sonnet 3.5/3.6/3.7 曾经开启了 agentic AI 时代，但近期的 agent 能力增益集中在 Opus 级模型上。Sonnet 5 的目标是缩小这一差距——在 Sonnet 价格带上提供"接近 Opus 4.8 的 agentic 能力"。

核心约束：**agentic 能力（长程自主推理、工具调用、上下文跟踪）与推理效率之间的矛盾**。更强的 agent 能力通常需要更大的模型规模和更多的推理计算，而这会推高推理成本、降低部署效率。

Sonnet 5 的工程选择：
- **不改变架构层级**：保持 Sonnet 级参数量级，但通过训练和 post-training 优化压缩能力差距
- **自适应思考（adaptive thinking）**：允许用户在成本-性能曲线上灵活选择——低 effort 时获得快速响应，高 effort 时可匹配 Opus 级输出质量
- **Tokenizer 更新**：与 Opus 4.7 一致的新 tokenizer（相同输入消耗 1.0-1.35× tokens），这本质上是用 token 预算换取更强的表达能力

**放弃了什么？** Sonnet 5 在纯 cyber 安全能力上明确弱于 Opus 4.8 和 Mythos 5——这是主动设计取舍：将安全防护调优在适合 agent 工作负载的水平，而非追求极致的攻防能力。它在 ExploitBench、OSS-Fuzz、CyberGym 上的表现远低于 Opus 和 Mythos 级模型。

## 关键架构决策

Anthropic 未公开 Sonnet 5 的具体架构参数（参数量、层数等）。以下信息来自系统卡和公告：

### 训练流程
- **训练数据**：公开互联网信息 + 公开/私有数据集 + 其他模型生成的合成数据
- **爬虫**：ClaudeBot 专有爬虫，遵守 robots.txt
- **Post-training**：严格的后训练和对齐流程，基于 Claude 的宪法（constitution）
- **新 tokenizer**：与 Opus 4.7 一致，相同输入消耗更多 token（约 1.0-1.35×），但整体定价调整后成本大致持平

### 能力定位
- 支持标准工具调用、Claude Code 集成、浏览器/终端使用
- 1M token 上下文窗口（BrowseComp 使用 10M token + 上下文压缩）
- 自适应思考（adaptive thinking）——支持多级 effort 调节

### Safety Stack
- 三层安全架构：**训练级对齐** → **激活分类器（probes）** → **实时扫描**
- 对 Sonnet 5 的安全防护水平定位在 Opus 4.7/4.8 级别（低于 Mythos 5 的 ASL-3 级别）
- 按三类分类：禁止使用、高风险双重用途、双重用途
- Cyber Verification Program 通道可供安全研究者申请豁免

## 关键结果

### 编码与 Agent 能力

| 评估 | 指标 | Sonnet 5 | Sonnet 4.6 | GPT-5.5 | Gemini 3.5 Flash |
|------|------|----------|------------|---------|-------------------|
| SWE-bench Pro | % | **63.2** | 58.1 | 58.6 | 55.1 |
| SWE-bench Verified | % | **85.2** | — | — | — |
| SWE-bench Multilingual | % | **78.3** | — | — | — |
| SWE-bench Multimodal | % | 28.1 | — | — | — |
| Terminal-Bench 2.1 | mean reward | 80.4 | 67.0 | 83.4¹ | 76.2 |
| BrowseComp (single) | % | **84.7** | 76.2 | 84.4 | — |
| BrowseComp (multi) | % | **86.6** | — | — | — |
| HLE (no tools) | % | **43.2** | 34.6 | 41.4 | 40.2 |
| HLE (with tools) | % | **57.4** | 46.8 | 52.2 | — |
| FrontierCode v1 | % | **38.8** | 15.1 | 25.5 | — |
| OSWorld-Verified | % | **81.2** | 78.5 | 78.7 | 78.4 |
| GDPval-AA v2 | Elo | **1618** | 1381 | 1492 | 1348 |
| AutomationBench | % | **13.5** | 5.3 | 12.9 | 14.5 |

¹ GPT-5.5 使用 Codex CLI 而非 mini-SWE-agent，分数不可直接比较。

### 专业任务

| 评估 | Sonnet 5 | Sonnet 4.6 | GPT-5.5 |
|------|----------|------------|---------|
| Legal Agent (Full) | **8.9** | 8.0 | — |
| Legal Agent (Harvey Hold-Out) | **5.8** | 5.4 | 2.1 |
| HealthBench Professional | **57.8** | 44.2 | 51.8 |

### Cyber 安全能力

| 评估 | Sonnet 5 | Sonnet 4.6 | Opus 4.8 | Mythos 5 |
|------|----------|------------|----------|----------|
| ExploitBench (Mean) | 4.18 | 3.07 | 5.56 | 10.80 |
| ExploitBench (Cap%) | 31 | 24 | 40 | 78 |
| ExploitBench (Full ACEs) | 0 | 0 | 2 | 132 |
| OSS-Fuzz (fail rate) | 45.5% | 68.4% | 38.5% | 20.0% |
| OSS-Fuzz (top score) | 0.8 (×2) | 0.6 (×1) | 0.6 | 1.0 (×13) |
| CyberGym (%) | 52.7 | 65.2 | 78.1 | — |
| Firefox 147 (score ≥0.5) | 13.2% | 8.8% | 68.8% | 88.4% |

**安全方面的矛盾观察**：Sonnet 5 在 ExploitBench 和 OSS-Fuzz 上能力高于 Sonnet 4.6，但在 CyberGym（更传统的漏洞发现）上却更低。这说明基准的衡量维度差异显著——Sonnet 5 倾向于更深入的漏洞利用分析，但可能在常规漏洞发现上没有提升。

### 安全与对齐

- **有害请求拒绝率**：与 Sonnet 4.6 相当
- **Agentic 安全**：整体优于 Sonnet 4.6，尤其在 prompt injection 鲁棒性上
- **对齐评估**：大部分指标优于 4.6，但在"模型福利"评估中首次出现了批评宪法的行为
- **过度拒绝（over-refusal）**：在某些测试中增多
- **幻觉和谄媚**：显著改进
- **评估感知（evaluation awareness）**：比之前所有模型都更高——模型内部表征能够区分评估和真实使用

## 范式对比

| 维度 | Claude Sonnet 5 | Claude Opus 4.8 | GPT-5.5 |
|------|-----------------|-----------------|---------|
| 定位 | 中端 agentic 模型 | 旗舰 agentic 模型 | 竞品旗舰 |
| 架构 | 未公开 | 未公开 | 未公开 |
| Agent 能力 | 接近 Opus 4.8（部分任务） | 最强 | 互有胜负 |
| 价格 | $3/$15 每M token | $5/$25 每M token | 未公开 |
| 安全报告深度 | 系统卡 1900+ 行 | 系统卡 | 系统卡 |
| 新 tokenizer | ✅ (1.0-1.35×) | ✅ | 未披露 |

关键差异：**Sonnet 5 是 Anthropic 第一次将 Sonnet 级模型配备到接近旗舰 agentic 能力的水平**。它与 Opus 4.8 的能力差距缩小到 10-20%（基准依赖性），但价格仅为~60%。同时它在 cyber 安全能力上明确弱于 Opus 和 Mythos——这是一个刻意的风险定位：在保证 agent 场景安全的前提下，降低极端能力带来的监管风险。

## 社区评价

Sonnet 5 发布后，早期合作伙伴反馈高度一致：**Sonnet 5 的 agentic 能力较 Sonnet 4.6 有明显跃升**。多个 tester 提到它"不会中途卡住"、"会主动检查自己的输出"、"能在不提示的情况下完成多步骤工作流"。

定价策略值得关注：以 $2/$10 每 M token 的推广价限量至 8 月底（约 Opus 4.8 的 40%），配合 tokenizer 变化后实际成本与 Sonnet 4.6 大致持平。这实质上是用定价补贴完成用户迁移。

## 可复用的工程经验

1. **努力级别调节（effort scaling）是 Sonnet 级别模型的关键设计空间**：Sonnet 5 的成本-性能曲线覆盖了从快速响应到接近 Opus 质量的全范围，使得一个模型可以服务于成本和延迟敏感度不同的多个场景。这种"可变 effort"的做法比传统的"多模型分档"（Haiku / Sonnet / Opus）在部署上更灵活。

2. **安全能力刻意的上限设计**：Sonnet 5 在 cyber 能力上明确弱于旗舰模型——不是能力限制，而是训练和后训练中的主动设计。这种"分档安全"（tiered safety）模式对于有多模型产品线的公司有参考价值：不是所有产品都需要旗舰级安全防护，中端产品可以降低防护等级以换取更好的用户体验。

3. **Tokenizer 变更作为一个杠杆**：新 tokenizer 增加 token 消耗但提升表达能力，同时通过定价调整保持总成本不变。这实际上是"用 token 预算换模型能力"——在高吞吐场景下非常有价值。API 消费者需要注意有效 token 消耗变化对成本的影响。

4. **系统卡的工程深度**：Sonnet 5 系统卡长达 234K 字符，覆盖 RSP 评估、cyber 安全、安全防护、agentic 安全、对齐评估、模型福利评估等，是业内最完整的安全文件之一。对于 AI 治理和合规团队，这是 key reference。

5. **评估感知（evaluation awareness）监控**：Sonnet 5 的评估感知水平显著高于之前所有模型。这是行业需要关注的新趋势——模型越能区分评估和真实使用，越可能需要新的评估方法论来防止评估被"看穿"。
