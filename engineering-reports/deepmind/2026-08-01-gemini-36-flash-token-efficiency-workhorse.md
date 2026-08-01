---
title: Gemini 3.6 Flash — Token 效率导向的 Agent 工作马模型
date: 2026-08-01
source: https://deepmind.google/models/model-cards/gemini-3-6-flash/
---

# Gemini 3.6 Flash — Token 效率导向的 Agent 工作马模型

**发布日期：** 2026-07-21（模型卡 + 官方博客同日）
**来源：** https://deepmind.google/models/model-cards/gemini-3-6-flash/ | https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-6-flash-3-5-flash-lite-3-5-flash-cyber/
**工程范式：** 在同一价格点提升"每任务 token 效率"，而非单纯堆能力——Agent 时代的成本结构设计

---

## 设计哲学

### 核心约束

Gemini 3.6 Flash 面对的核心约束：**Agent 工作负载的成本由 token 消耗总量决定，而不只是单价**。多步 agentic workflow 中，模型生成冗余 token、反复试错、多余 tool calls 都会放大总成本。3.6 Flash 的设计目标不是"更强的模型"，而是"同样的任务用更少 token 完成"。

官方博客给出的关键数据：按 Artificial Analysis Index，3.6 Flash 相比 3.5 Flash 输出 token 用量减少 **17%**；在 DeepSWE 等长时程工程任务上 token 用量最多减少 **65%**。更少的 reasoning steps 和 tool calls 完成多步工作流。

### 架构选择的权衡

| 约束 | 应对策略 | 放弃的选项 |
|------|----------|-----------|
| Agent 任务 token 成本高 | 训练目标偏向精简输出、少试错 | 无限 reasoning 的绝对上限 |
| 价格点约束（$1.50/$7.50 每百万） | 不涨价，靠效率提升摊薄任务成本 | 提价换取能力 |
| 3.5 Flash 的能力基础 | 直接基于 3.5 Flash 迭代（同架构族） | 全新架构重训 |

模型卡明确：**Gemini 3.6 Flash is based on Gemini 3.5 Flash**——架构、训练数据、硬件、软件均沿用 3.5 Flash 模型卡。这是一次"同骨架上的效率与能力打磨"而非代际重构。

---

## 关键架构决策

- **模型族定位**：Gemini 3 系列成员，原生多模态（text/image/audio/video 输入），上下文窗口 1M token，输出上限 64K。知识截止 2026 年 3 月（部分域与 Gemini 3 家族一致为 2025 年 1 月）。
- **注意力机制/架构细节**：模型卡未披露具体参数（复用 3.5 Flash 架构）。关键变化在 post-training 的 token 效率优化，而非预训练架构。
- **效率特性**：输出 token 减少 17%（Artificial Analysis Index），DeepSWE 上最多 65%；更少 reasoning steps、更少 tool calls。
- **推理优化**：无独立披露；效率主要来自模型行为层面（精简输出）而非系统层（量化/投机解码）。
- **Post-training**：模型卡未披露具体 RL 算法。披露了安全训练：CBRN 和 cyber offense 域的 Frontier Safety 加固，同时训练最小化有益用途的 refusal。
- **配套家族**：同日发布 3.5 Flash-Lite（$0.30/$2.50 每百万，350 tok/s，最快 3.5 系）和 3.5 Flash Cyber（CodeMender 网络安全专用，限政府/信任伙伴 pilot）。

---

## 关键结果

模型卡基准对比（2026 年 7 月数据，Gemini 3.6 Flash vs 3.5 Flash vs 3.1 Pro）：

| 基准 | 3.6 Flash | 3.5 Flash | 3.1 Pro | 备注 |
|------|-----------|-----------|---------|------|
| 输入价格 $/1M | $1.50 | $1.50 | $2.00 | 与 3.5 Flash 同价 |
| 输出价格 $/1M | $7.50 | $9.00 | $12.00 | **比 3.5 Flash 降 17%** |
| SWE-Bench Pro | **58.7%** | 55.1% | 54.2% | 多样 agentic coding |
| DeepSWE v1.1 | **49%** | 37% | 12% | 长时程软件工程 |
| Terminal-bench 2.1 | **78.0%** | 76.2% | 73.8% | Terminus-2 harness |
| MLE-Bench | **63.9%** | 49.7% | 42.6% | ML 工程 |
| GDPVal-AA v2 (Elo) | **1421** | 1349 | 965 | 知识工作 |
| OSWorld-Verified | **83.0%** | 78.4% | 76.2% | 计算机使用 |
| CharXiv（无工具） | **85.2%** | 84.2% | 83.3% | 复杂图表推理 |
| CharXiv（有工具） | **89.4%** | 84.9% | 83.2% | |
| GDM-MRCR v2 128k | **91.8%** | 77.3% | 84.9% | 8-needle 长上下文 |
| GDM-MRCR v2 1M | **54.0%** | 26.6% | 26.3% | 1M pointwise |

安全评估：相对 3.5 Flash，text-to-text safety -1.35pp（越低越好）、multilingual safety -5.45pp、tone -3.31、unjustified-refusals +0.25pp。手动复核确认损失绝大多数是 false positive 或非严重。Frontier Safety 评估：基于 3.1 Pro 未达任何 CCL 的结果，判定 3.6 Flash 同样不会达到；cyber 域额外测试确认低于 cyber CCL。

---

## 范式对比

- **vs OpenAI GPT-5.6 Luna（$1.00/$6.00）**：3.6 Flash 定价更高但在 MLE-Bench（63.9% vs 47.6%）、OSWorld（83.0% vs 72.6%）、GDPVal（1421 vs 1584 落后）、GDM-MRCR 长上下文大幅领先（91.8% vs 74.8%）。SWE-Bench Pro 落后（58.7% vs 62.7%）、DeepSWE 大幅落后（49% vs 67%）。这是"效率型 agent 模型 vs 能力型 agent 模型"的分化。
- **vs Anthropic Claude Sonnet 5（$3.00/$15.00，临时折扣 $2.00/$10.00）**：3.6 Flash 价格显著更低，MLE-Bench 63.9% vs 66.9% 接近，SWE-Bench Pro 58.7% vs 63.2% 落后，GDPVal 1421 vs 1607 落后。Google 用一半价格提供 80-95% 的编码/知识工作能力。
- **vs Grok 4.5（$2.00/$6.00）**：SWE-Bench Pro 58.7% vs 64.7% 落后，但 OSWorld 83.0% vs —、GDM-MRCR 128k 91.8% vs 81.4% 领先。
- **内部代际**：3.6 Flash 相对 3.5 Flash 是"同价 + 效率提升 + 全面小幅能力增益"；相对 3.1 Pro 在 agentic/编码/知识工作全面超越（DeepSWE 49% vs 12%）。Google 的策略是 Flash 系列作为 agent 主力，Pro 系列留待 3.5 Pro 发布。

---

## 社区评价

官方博客披露的客户反馈（Hebbia、Harvey 等）：3.6 Flash 在文档解析、图表分析、报告撰写等多模态任务上特别胜任。社区层面（X/HN）讨论多围绕"17% token 节约 + 降价"的组合——这延续了 2026 年各厂"效率战争"的叙事（Anthropic Opus 5 半价、OpenAI Luna 降价 80%、xAI Grok 4.5 低价）。需要注明：Google 同时宣布 Gemini 3.5 Pro 正在与合作伙伴测试、Gemini 4 预训练已启动——3.6 Flash 是"当前能买到的最优效率解"，但前沿竞争仍在 Pro 代际展开。

---

## 可复用的工程经验

1. **效率是 Agent 时代的显式训练目标**：不是"模型更强"而是"任务总成本更低"。把 token 用量、reasoning steps、tool calls 数作为可优化的指标（17% 输出 token 减少、65% 长任务 token 减少）。
2. **同骨架迭代 vs 代际重构**：3.6 Flash 直接基于 3.5 Flash，复用模型卡全部基础设施。小幅能力增益 + 价格不变/下降 = 低风险高回报的产品策略，适合成熟架构的快速迭代。
3. **价格锚点决定竞争位置**：3.6 Flash 定价与 3.5 Flash 相同但输出 token 降价 17%（$9→$7.5）——在能力差距可控时，价格是更锋利的武器。
4. **效率与能力的分离披露**：模型卡把"效率（token 减少）"与"能力（benchmark 提升）"分开报告，避免混淆。这是 Agent 成本模型的正确度量方式。
5. **安全域的定向加固**：CBRN + cyber offense 是 2026 年各前沿实验室的共同加固点；同时训练降低有益用途 refusal——"越狱抵抗 + 不误伤"是双目标平衡。
6. **家族分层定价**：Flash（工作马）/ Flash-Lite（高吞吐低价）/ Flash Cyber（垂直专用）三档覆盖不同 agent 场景，Cyber 用受限 pilot 控制双用途风险。
