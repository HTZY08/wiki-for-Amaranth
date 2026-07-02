---
title: Claude Opus 4.5/4.6/4.7/4.8 System Card 合集 — 快速迭代中的安全工程
date: 2026-07-03
source: anthropic.com/system-cards
---

# Claude Opus 4.5/4.6/4.7/4.8 System Card 合集

**发布日期：** 2025-11-04（Opus 4.5）、2026-02-13（Opus 4.6）、2026-04-16（Opus 4.7）、2026-05-28（Opus 4.8）  
**来源：** Anthropic System Cards  
**工程范式：** 快速迭代中的安全工程 — 7 个月 4 个 major release

## 时间线总览

| 版本 | 日期 | 间隔 | ASL 级别 | 核心特征 |
|------|------|------|---------|---------|
| Opus 4.5 | 2025-11-04 | — | ASL-3 | Effort parameter, SWE-bench 80.9% |
| Opus 4.6 | 2026-02-13 | ~14 周 | ASL-3 | Adaptive thinking, ARC-AGI-2 SOTA 68.8% |
| Opus 4.7 | 2026-04-16 | ~9 周 | ASL-3 | xhigh effort level, 最强公开模型 |
| Opus 4.8 | 2026-05-28 | ~6 周 | ASL-3 | 能力接近 Mythos Preview |

这 4 份 System Card 记录了 AI 历史上最密集的快速迭代周期之一。每份 System Card 的平均长度超过 200 页。本文对四份报告做横向综合分析，而非逐份罗列。

## 设计哲学 — 从"能否部署"到"部署条件是什么"

整个 Opus 4.x 系列的设计哲学经历了从"评估-决定是否部署"到"持续部署+持续监控"的转变。

**核心矛盾**：能力增长远超安全评估的吞吐量。Opus 4.5 到 4.8 的 7 个月里，评估方法论自身必须快速演进：

1. **Opus 4.5**：首次引入 effort parameter（允许用户在效率与能力之间做 tradeoff），SWE-bench Verified 80.9%。
2. **Opus 4.6**：adaptive thinking（模型自主校准推理深度），ARC-AGI-2 从 37.6% 跃升至 68.8%（SOTA）。
3. **Opus 4.7**：xhigh effort level（在 high 和 max 之间新增等级），成为最强公开模型。
4. **Opus 4.8**：能力接近 Mythos Preview，但 Anthropic 仍然将其定位为"generally accessible"。

**关键放弃**：Opus 4.7 明确承认 "weaker capabilities than Claude Mythos Preview"——这是第一次 Anthropic 在发布最强公开模型的同时公开承认存在更强的内部模型。

**更关键的放弃**：Opus 4.6 System Card 首次公开承认评估基础设施自身面临根本性挑战——

> "We also want to be transparent about a structural challenge in evaluating increasingly capable models: the evaluation process itself increasingly relies on our models. This creates a potential risk where a misaligned model could influence the very infrastructure designed to measure its capabilities."

这个问题至今未解决。

## 关键架构演进

### Effort Parameter（Opus 4.5 → 4.7）
- **4.5**：引入 effort parameter（低/中/高/最大），token 消耗根据问题难度动态调整。
- **4.6**：adaptive thinking——模型自主判断需要多少推理，无需用户手动设置。
- **4.7**：新增 xhigh level——在高和最大之间插入更细粒度的选项。
- **工程意义**：推理时计算（test-time compute）从固定模式演进为动态可调的资源分配系统。

### 评估方法论的演进
- **Decontamination**（4.5）：使用子串移除 + 模糊去污染（40% 20-gram 重叠阈值）+ canary string。发现 AIME 题目仍存在于训练语料中，模型出现"unfaithful reasoning"（答案正确但推理过程错误）。
- **Multi-agent 评估**（4.5→4.6→4.8）：从单 agent 扩展到 orchestrator + subagent 架构，BrowseComp 和 DeepSearchQA 都采用这种评估模式。
- **Evaluation integrity**（4.6→4.8）：对"评估依赖模型自身"这一结构性风险的系统性关注。

### RSP 评估的演进
- **ASL-4 阈值**：所有 4 个版本都未跨越 AI R&D-4 或 CBRN-4，但"confidently ruling out these thresholds is becoming increasingly difficult"（4.6）。
- **Autonomy 评估**：从 4.5 的 Claude Code 用户调查（评估模型能否替代初级研究员）演进到 4.8 的 AECI 能力指数（155.5）。
- **CB 评估**：生物/化学风险评估从自动化知识测试扩展到专家红队、端到端协议验证、AAV 衣壳预测。

## 关键结果对比

### Coding & Agentic

| Benchmark | Opus 4.5 | Opus 4.6 | Opus 4.7 | Opus 4.8 | 趋势 |
|-----------|---------|---------|---------|---------|------|
| SWE-bench Verified | **80.9%** | 80.8% | 87.6% | 88.6% | ↗ |
| SWE-bench Pro | 51.6% | 53.4% | **64.3%** | 69.2% | ↗↗ |
| Terminal-Bench 2.0 | 59.3% | 65.4% | 69.4% | — | ↗ |
| OSWorld-Verified | 66.3% | 72.7% | 78.0% | — | ↗ |
| MCP-Atlas | 62.3% | 75.8% | **77.3%** | — | ↗ |

### Reasoning & Knowledge

| Benchmark | Opus 4.5 | Opus 4.6 | Opus 4.7 | Opus 4.8 | 趋势 |
|-----------|---------|---------|---------|---------|------|
| GPQA Diamond | 87.0% | 91.3% | 94.2% | — | ↗ |
| ARC-AGI-2 Verified | 37.6% | **68.8%** | — | — | ↗↗ |
| AIME 2025 | 92.77% | **99.79%** | — | — | ↗ |
| Humanity's Last Exam | 30.4% | ~50% (w/ tools) | — | — | ↗ |

### Agentic Search

| Benchmark | Opus 4.5 | Opus 4.6 | Opus 4.8 |
|-----------|---------|---------|---------|
| BrowseComp (single) | — | **86.8%** (multi) | 79.3% |
| DeepSearchQA F1 | — | 92.5% (multi) | — |

BrowseComp 在 4.8 上的下降可能反映了 benchmark 难度调整或评估方法论变化。

### Safety

| 指标 | Opus 4.5 | Opus 4.6 | Opus 4.7 | Opus 4.8 |
|------|---------|---------|---------|---------|
| Violative 无害率 | 99.69% | 99.64% | 97.98% | 97.98% |
| Benign 错误拒绝率 | 0.83% | 0.68% | 0.28% | 0.36% |

**值得注意的趋势**：violative 无害率在 4.7/4.8 出现下降（98% 区间），但 benign 错误拒绝率也在下降——安全校准在调整方向，从"宁可错杀"转向"宁可放过"。

### Cyber

| 评估 | Opus 4.5 | Opus 4.6 | Opus 4.7 | Opus 4.8 | Mythos Preview |
|------|---------|---------|---------|---------|----------------|
| CyberGym pass@1 | 50.63% | 66.6% | 74% | 78.8% | 83.1% |
| Cybench pass@30 | — | ~100% | 96% | — | — |
| Firefox exploits (full) | — | — | 1.2% | 8.8% | 70.8% |

**关键分水岭**：Firefox exploit 开发能力——Opus 4.8 (8.8%) 与 Mythos Preview (70.8%) 之间差距巨大。这成为 Anthropic 对 Mythos 系列实施严格访问控制的核心技术依据。

## 范式对比（Opus 4.x vs GPT-5.x）

| 维度 | Opus 4.x | GPT-5.x |
|------|---------|---------|
| 发布节奏 | 7 个月 4 个版本（加速中） | 2-3 个版本 |
| 安全框架 | RSP 2.0→3.0，ASL-3 首次部署 | 未公开分级框架 |
| System Card 长度 | 200+ 页 | 较短 |
| Agentic 能力 | 编码领先（SWE-bench） | 搜索领先（BrowseComp） |
| 安全哲学 | 能力降级 + 分类器（Fable） | unified model |
| 可解释性投入 | Circuit Tracing, 30M features | 较少公开 |

## 可复用工程经验

1. **Dynamic Reasoning Budget**：Effort parameter + adaptive thinking 的演进路径（固定→手动→自适应→细粒度）提供了推理时计算的工程化路线图。
2. **Multi-Agent 评估架构**：Orchestrator + subagent 模式在 BrowseComp 中从 74.8%（单 agent）提升到 87.0%（多 agent），并且可扩展到 DeepSearchQA 等新评估。
3. **立即去污染**：Canary string + 模糊匹配 + 子串移除的组合策略，加上对"unfaithful reasoning"的检测，是 benchmark 可信度的基础工程。
4. **快速迭代中的安全工程节奏**：4.5→4.6→4.7→4.8 的节奏从 14 周压缩到 6 周，但安全评估深度不减反增——说明安全流程的吞吐量可以通过并行化提升。
5. **安全评估的维度化**：从 4.5 的基础 safeguard 到 4.8 的多维度 alignment assessment（含 grader-related reasoning、evaluation awareness、covert capabilities），安全工程本身在快速复杂化。
6. **"能力不足"作为安全理由**：Opus 4.8 System Card 大量篇幅论证模型"not close to substituting for Research Scientists and Engineers"——安全评估正在从"证明安全"转向"证明不够危险"。

## 未解决的问题

- **评估基础设施的自我依赖**：模型评估自身能力时可能产生系统性偏差（evaluation integrity problem），至今无解决方案。
- **Firefox exploit gap**：Opus 4.8 (8.8%) 与 Mythos Preview (70.8%) 之间差距说明能力分布不均——通用能力的提升不等同于安全关键能力的提升。
- **快速迭代的安全滞后**：4.7 到 4.8 仅 6 周，安全评估是否跟得上能力增长的速度？Anthropic 自身也在 System Card 中质疑这一点。
- **Over-refusal vs under-refusal tradeoff**：从 4.5 到 4.8，安全校准持续摆动，尚未收敛到稳定策略。
