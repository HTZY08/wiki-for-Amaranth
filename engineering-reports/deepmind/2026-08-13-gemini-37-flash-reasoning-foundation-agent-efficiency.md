---
title: Gemini 3.7 Flash — 推理基座算法改进的 Flash 代际更新
date: 2026-08-13
source: https://deepmind.google/models/model-cards/gemini-3-7-flash
---

# Gemini 3.7 Flash — 推理基座算法改进的 Flash 代际更新

**发布日期：** 2026年8月13日（model card 发布）
**来源：** https://deepmind.google/models/model-cards/gemini-3-7-flash
**工程范式：** 在同架构基座上做"核心推理基座的算法改进"——以价格不变换取全面的 agent/coding/长上下文能力跃升，靠模型卡量化验证而非架构换血

## 设计哲学

Gemini 3.7 Flash 是 Gemini 3 家族的最新迭代，model card 对架构部分的表述只有一句话：**"Gemini 3.7 Flash is based on Gemini 3.6 Flash"**，并明确"featuring algorithmic improvements to its core reasoning foundation"。

这揭示了一个清晰的工程策略：**Flash 系列的代际更新不做架构革命，而是对推理基座（reasoning foundation）做算法级改进**——训练数据、硬件、软件全部沿用 3.6 Flash，能力提升完全来自推理算法/训练方法的变化。配合"customizable thinking configurations"（可配置思考模式，控制质量/成本/延迟的配比），把推理预算的旋钮交到用户手里。

**放弃了什么：** 没有新架构、没有新上下文窗口（1M 沿用）、没有新价格（intro 价 $0.75/$3.75 不变）。所有投入集中在推理核心与 agent 能力上——这是"同一张牌桌，换打法"而非"换桌子"。

## 关键架构决策

### 模型规格（沿自 Gemini 3.6 Flash）
- 输入：文本、图像、音频、视频；上下文窗口最高 1M tokens
- 输出：文本，64K tokens
- 架构：基于 Gemini 3.6 Flash（细节见 3.6 Flash model card，未在本卡重复披露）
- 知识截止：2026年3月（部分域可更新至 2026年1月）

### 推理控制
- Customizable thinking configurations：可配置思考强度，在质量/成本/延迟之间做权衡
- 这是 Flash 系列"workhorse"定位的核心——同一次推理按需切换深度

### 定价策略
- 输入 $0.75 / 输出 $3.75 每百万 token（intro 价，2026-12-31 到期；之后 $1.50 / $7.50）
- 对比：Claude Sonnet 5 $2/$10、GPT-5.6 Terra $2/$12、Muse Spark 1.2 $1.25/$4.25——Flash 维持显著价格优势

### 安全框架
- Frontier Safety Framework（2026年4月版）评估：CBRN、Cybersecurity、Harmful Manipulation、ML R&D 四个域均未达到 TCL/CCL 门槛
- Cybersecurity 域达到 CCL alert threshold（未到 CCL）；ML R&D 的情境感知（situational awareness）强于 Gemini 3.1 Pro
- 随 3.7 Flash 发布更新了 CBRN 与 cyber offense 的滥用防护

## 关键结果

（均为 model card 原文数字，对比 Gemini 3.6 Flash / Claude Sonnet 5 / GPT-5.6 Terra / Muse Spark 1.2）

| Benchmark | 3.7 Flash | 3.6 Flash | Sonnet 5 | GPT-5.6 Terra | Muse Spark 1.2 |
|---|---|---|---|---|---|
| AA Intelligence Index | 56 | 52 | 55 | 57 | 57 |
| FrontierCode 1.1 | 43.6% | 34.4% | 42.7% | 41.3% | -- |
| DeepSWE v1.1 | 65.3% | 48.6% | 53.8% | 69.6% | 54.9% |
| Code Arena (Elo) | 1588 | 1538 | 1541 | 1523 | 1535 |
| Terminal-bench 2.1 | 85.8% | 78.0% | 80.4% | 87.4% | 82.9% |
| Terminal-bench 3.0 | 14.9% | 5.4% | 14.6% | 20.8% | -- |
| AutomationBench | 30.4% | 17.0% | 10.7% | 23.6% | -- |
| GDPVal-AA v2 (Elo) | 1525 | 1422 | 1598 | 1578 | 1628 |
| Harvey LAB-AA | 90.7% | 85.1% | 90.1% | 85.2% | -- |
| GDP.pdf | 34.0% | 22.0% | 28.0% | 24.7% | 16.0% |
| CharXiv Reasoning (no tools) | 84.5% | 85.2% | 77.0% | 85.9% | -- |
| LVBench | 85.4% | 84.2% | 68.5% | 78.9% | -- |
| GDM-MRCR v2 128K (8-needle) | 97.0% | 91.8% | 81.5% | 93.5% | -- |
| OSWorld-2.0 | 47.9% | 33.8% | -- | 50.2% | -- |
| Agent's Last Exam | 26.3% | 24.2% | 33.3% | 28.0% | -- |
| HLE-Verified | 53.6% | 51.2% | 31.0% | 51.1% | -- |
| BioMysteryBench (human solvable) | 87.1% | 80.6% | 87.5% | 83.8% | -- |

关键观察：
- 对 3.6 Flash 全面碾压（FrontierCode +9.2、DeepSWE +16.7、Terminal-bench 2.1 +7.8、AutomationBench +13.4、MRCR +5.2、OSWorld +14.1）
- 对 Claude Sonnet 5 大幅领先（DeepSWE +11.5、HLE-Verified +22.6、LVBench +16.9），但 GDPVal、Agent's Last Exam 落后
- 对 GPT-5.6 Terra：TB2.1、Agent's Last Exam、DeepSWE 落后，FrontierCode 领先
- 安全：与 3.6 Flash 整体相当（Text to Text Safety +1.17pp 变差，Multilingual Safety -0.48pp 变好，Unjustified-refusals +0.84pp 变差，均绝对值很小）

## 范式对比

- **vs 同价位竞品（Sonnet 5 / GPT-5.6 Terra / Muse Spark 1.2）**：3.7 Flash 的差异化在于"推理基座算法改进"换来的性价比——1/2 到 1/3 的价格、1M 上下文、接近旗舰的 agent 分数。Google 的策略是把 Flash 做成"agent 工作马"，Pro 留给旗舰需求
- **vs 自家 3.6 Flash**：完全同架构、同价格，纯算法迭代——证明 Flash 系列的改进可以不依赖模型规模/架构变化，推理算法本身是有效的 scaling 轴
- **vs 开源（GLM-5.3 / Qwen3.8-Max）**：3.7 Flash 以 1M 上下文 + 65.3 DeepSWE 形成中端壁垒，但 Terminal-bench 3.0 只有 14.9%，说明通用长程 agent 能力仍是全行业的共同短板

## 社区评价

原文未提供 HN/Reddit 讨论数据，未独立核实，暂不引用。值得注意的外部讨论点：① "based on 3.6 Flash" 的表述是否意味着这是 checkpoint 级升级而非独立训练（model card 未披露训练细节）；② intro 价格 12/31 到期的涨价预期对采用决策的影响。

## 可复用的工程经验

1. **推理基座是可独立优化的轴**：同架构、同数据、同硬件的前提下，推理算法改进（thinking 配置、推理路径优化）能带来 DeepSWE +16.7 级别的跃升——不必每次迭代都换架构
2. **模型卡是产品文档也是营销武器**：3.7 Flash 用一张与竞品对齐的 benchmark 表（含价格行）完成定位——"性能/价格比"用一张表说清
3. **intro pricing 是 Flash 系的节奏工具**：$0.75/$3.75 的 intro 价 + 明确到期日，既抢采用又给涨价预期——API 定价可以做成时间敏感的采用激励
4. **安全评估与能力评估分开发布**：Frontier Safety Framework 的 TCL/CCL 表格（含"alert threshold reached 但未到门槛"的精细分级）是开源模型可以借鉴的透明度模板
