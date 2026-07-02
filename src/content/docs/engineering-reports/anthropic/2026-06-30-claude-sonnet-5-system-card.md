---
title: Claude Sonnet 5 — 最有 Agent 能力的 Sonnet
date: 2026-07-03
source: anthropic.com/news/claude-sonnet-5
---

# Claude Sonnet 5 System Card

**发布日期：** 2026-06-30  
**来源：** anthropic.com/news/claude-sonnet-5, anthropic.com/claude-sonnet-5-system-card  
**工程范式：** Agentic Sonnet — 能力接近 Opus 4.8 但成本更低

## 设计哲学

Claude Sonnet 5 标志着 Anthropic "能力分层"战略的又一次深化。核心定位：**"For many developers, the agentic AI era began with Sonnet-class models"**——Sonnet 系列是 Agentic AI 的普及层。

Anthropic 的工程决策是让 Sonnet 5 "narrows the gap: its performance is close to that of Opus 4.8, but at lower prices"。这使得 Sonnet 5 替换 Sonnet 4.6 成为 Claude.ai Free/Pro 的默认模型。

**关键放弃**：Sonnet 5 选择了降低价格门槛来换取市场覆盖——$2/MTok 的 introductory pricing（标准 $3/MTok），相比 Opus 4.8 的 $4.8/$24。代价是新 tokenizer 导致相同输入增加 1.0-1.35× token 消耗。

### 定价策略分析

| 阶段 | Input | Output | 备注 |
|------|-------|--------|------|
| Introductory (至 2026-08-31) | $2/MTok | $10/MTok | 约成本中性（新 tokenizer） |
| Standard | $3/MTok | $15/MTok | 对比 Opus 4.8: $4.8/$24 |

## 关键架构决策

### Agentic 架构升级
Sonnet 5 在 agentic 能力上有系统性提升：

- **Planning & Tool Use**：增强的推理-行动循环，模型能更好地规划多步任务并调用工具。
- **Brownfield Coding**：针对复杂存量代码库的改进——通过早期访问合作伙伴验证。
- **Effort Level 可调**：继承自 Opus 4.5+ 的 effort parameter，用户可在成本与能力之间权衡。在高 effort 下，部分任务可匹配 Opus 4.8。

### Tokenizer 变更
Sonnet 5 引入了新 tokenizer，导致相同文本消耗 1.0-1.35× 更多 token。这在 pricing 层面被 introductory pricing 抵消，但对已做 token 预算规划的开发者构成迁移成本。

### Cypber Safeguards
默认启用与 Opus 4.7/4.8 相同的 cyber safeguards，但比 Fable 5 的分类器较宽松。Sonnet 5 在 Firefox exploit 开发评估中 full working exploits 为 0.0%（与 Sonnet 4.6 相同），partial success 率略有提升。

## 关键结果

### Benchmark 表现

| Benchmark | Sonnet 5 | Sonnet 4.6 | Opus 4.8 | 趋势 |
|-----------|---------|-----------|---------|------|
| OSWorld-Verified | **81.2%** | — | — | Agentic 能力核心指标 |
| BrowseComp (single agent) | **84.7%** | — | 79.3% | Agentic 搜索 |
| SWE-bench Pro | **63.2%** | — | 69.2% | 编码接近 Opus 4.8 |
| Terminal-Bench 2.1 | **69.2%** | — | — | 终端操作 |
| Humanity's Last Exam w/ tools | **57.4%** | — | ~50% | 超越 Opus 4.8 |

**关键信号**：Sonnet 5 在多个 benchmark 上接近甚至超越 Opus 4.8，尤其是在 Humanity's Last Exam (w/ tools) 上达到 57.4%（vs Opus 4.8 约 50%）。

### Safety 评估

| 维度 | Sonnet 5 | 对比 |
|------|---------|------|
| Misaligned behavior | 低于 Sonnet 4.6 | 略高于 Opus 4.8 和 Mythos Preview |
| Agentic safety | 改进的恶意请求拒绝 + prompt injection 抵抗 | 优于 Sonnet 4.6 |
| Hallucination | 低于 Sonnet 4.6 | — |
| Sycophancy | 低于 Sonnet 4.6 | — |
| Firefox exploit (full) | 0.0% | 与 Sonnet 4.6 相同 |

### 早期访问合作伙伴反馈（10 家）
合作伙伴反馈揭示 Sonnet 5 的实际工程表现：

- **Brownfield 编码**：多个合作伙伴强调其在复杂存量代码库中的表现（"traces a failure to its actual root cause and ships a durable fix instead of patching the symptom"）。
- **Agentic 工作流**：端到端多步任务完成（"update Salesforce account tiers, send a launch announcement... it finished end to end. That used to stall halfway."）。
- **成本效率**："Same output quality, fewer steps to get there"——成本降低了但输出质量未降。
- **安全一致性**："It refuses unsafe requests cleanly and consistently... A model that knows when to say no is just as important as one that knows how to build."（Lovable）

### 能力-成本曲线
Anthropic 发布的能力-成本曲线（effort 参数可调）显示：
- Sonnet 5（橙色曲线）是 Sonnet 4.6（灰色曲线）的 strict improvement。
- 覆盖比 Opus 4.8（黄色曲线）更广泛的成本-能力选项范围。
- 在高 effort 水平下，部分任务匹配 Opus 4.8。

## 范式对比

| 维度 | Sonnet 5 | Opus 4.8 | Fable 5 |
|------|---------|---------|---------|
| 定位 | 普及层 Agentic AI | 旗舰公开模型 | 安全强化版 |
| 定价 | $3/$15 | $4.8/$24 | $10/$50 |
| Cyber Safeguards | 默认启用（较宽松） | 默认启用 | 严格双层分类器 |
| Tokenizer | 新（1.0-1.35×膨胀） | 旧 | 旧 |
| SWE-bench Pro | 63.2% | 69.2% | 80.3% |

与 GPT-5.5 对比：Anthropic 延续了"安全分层"路径——Sonnet 5 缺失 Fable 5 的严格分类器，依靠系统提示级别的安全措施。OpenAI 的统一模型策略不做安全降级，但也没有能力分层。

## 社区评价

Simon Willison 记录了新 tokenizer 的使用体验——对已有 token 优化的工作流需要重新校准。HN 讨论（487 点）中有用户指出定价策略可能掩盖 tokenizer 变更的真实成本——$2/MTok 的 introductory price 乘以 1.35× token 膨胀，实际成本接近 $2.7/MTok。

另有用户质疑 Agentic 能力提升是否以可靠性为代价——"有重大问题尚未公开讨论"。

## 可复用工程经验

1. **Sonnet 作为能力分层的关键层**：Anthropic 确立了 Sonnet = "agentic AI 普及层"的产品定位，将前沿能力以更低价格下放。
2. **Early Access Program 作为评估手段**：10 家合作伙伴的定性反馈提供了 benchmark 无法捕获的真实工程表现。
3. **Introductory pricing 平滑迁移成本**：新 tokenizer 的迁移成本被 introductory pricing 吸收，6 周后过渡到标准价格——有计划的定价迁移策略。
4. **Cost-Performance Pareto Frontier**：Effort parameter 使一个模型覆盖从低成本到高能力的连续 spectrum，而非离散模型选择。
5. **Agentic safety 的差异化策略**：Sonnet 5 使用比 Fable 5 更宽松的安全措施——安全投入与风险暴露成正比，而非一刀切。

## 局限性

新 tokenizer 的向后兼容性问题尚未完全解决。部分 benchmark（Terminal-Bench 2.1）缺少 Opus 4.8 的直接对比数据。Misaligned behavior 略高于 Opus 4.8——在追求成本效率时安全校准是否做了 tradeoff 尚不明确。Cyber safety 评估中 partial success rate 的提升提示通用能力增长可能间接提升 cyber 能力（即使未专门训练）。
