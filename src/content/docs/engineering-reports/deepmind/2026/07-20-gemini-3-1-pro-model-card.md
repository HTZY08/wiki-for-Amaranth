---
title: Gemini 3.1 Pro — 深度推理驱动的 Agentic 能力密度提升
date: 2026-07-20
source: https://deepmind.google/models/model-cards/gemini-3-1-pro/
---

# Gemini 3.1 Pro Model Card——深度推理驱动的 Agentic 能力密度提升

**发布日期：** 2026-02-19（页面发布）  
**来源：** https://deepmind.google/models/model-cards/gemini-3-1-pro/  
**工程范式：** Deep Think 深度推理 + Agentic 能力密度路线——在同代架构上通过推理时计算扩展提升复杂任务表现。

## 设计哲学

Gemini 3.1 Pro 是 Gemini 3 Pro 的增量改进版本，核心思路是：**在保持架构不变的前提下，通过训练数据优化和 Deep Think 推理时扩展（test-time compute scaling）来提升 Agentic 和推理能力。**

架构继承自 Gemini 3 Pro——Sparse MoE Transformer，原生多模态（文本/图像/音频/视频），1M 上下文窗口，64K token 输出。Gemini 3.1 Pro 显著改善了 ARC-AGI-2（31.1% → 77.1%）、Terminal-Bench（56.9% → 68.5%）、BrowseComp（59.2% → 85.9%）等极具挑战性的 benchmark。

关键信号：DeepMind 选择了**在模型家族内部快速迭代（3.0 → 3 Pro → 3.1 Pro → 3.5 Flash → ...）** 而非等待大的架构跳变，体现了"架构稳定、数据和训练策略迭代"的工程路线。

## 关键架构决策

- **架构**：Sparse MoE Transformer（基于 Gemini 3 Pro，未披露具体专家数/激活参数量）
- **多模态**：原生支持文本、图像、音频、视频输入
- **上下文窗口**：1M token
- **输出长度**：64K token
- **Deep Think mode**：推理时扩展（test-time compute），选择性地增加推理计算量以提升复杂推理任务表现
- **训练**：JAX + ML Pathways，TPU 训练

### 与 Gemini 3 Pro 的关系

Gemini 3.1 Pro 基于 Gemini 3 Pro，核心改进来自：
- 训练数据的优化
- 推理时扩展策略（Deep Think）
- 模型卡页面明确说"更多架构信息请参阅 Gemini 3 Pro 模型卡"——意味着架构本身未变

## 关键结果

### Benchmark 对比（Deep Think 模式，High 设置）

| Benchmark | 领域 | Gemini 3.1 Pro | Gemini 3 Pro | 对比说明 |
|-----------|------|---------------|-------------|---------|
| **Humanity's Last Exam** (No tools) | 学术推理 | 44.4% | 37.5% | +6.9pp |
| **Humanity's Last Exam** (Search+Code) | 学术推理 | 51.4% | 45.8% | +5.6pp |
| **ARC-AGI-2** | 抽象推理 | **77.1%** | 31.1% | **+46pp！最大跳跃** |
| **GPQA Diamond** | 科学知识 | 94.3% | 91.9% | +2.4pp |
| **Terminal-Bench 2.0** | Agentic 编码 | 68.5% | 56.9% | +11.6pp |
| **SWE-Bench Verified** | Agentic 编码 | 80.6% | 76.2% | +4.4pp |
| **SWE-Bench Pro (Public)** | 多样化编码 | 54.2% | 43.3% | +10.9pp |
| **LiveCodeBench Pro** | 竞赛编程 | **ElO 2887** | 2439 | +448 ELO |
| **SciCode** | 科学编码 | 59% | 56% | +3pp |
| **APEX-Agents** | 长时专业任务 | **33.5%** | 18.4% | **+15.1pp！** |
| **BrowseComp** | Agentic 搜索 | **85.9%** | 59.2% | **+26.7pp** |
| **MMMU-Pro** | 多模态理解 | 80.5% | 81.0% | -0.5pp（持平） |
| **MMMLU** | 多语言 QA | 92.6% | 91.8% | +0.8pp |
| **MRCR v2 (128k)** | 长上下文 | 84.9% | 77.0% | +7.9pp |
| **MRCR v2 (1M)** | 长上下文（极限） | 26.3% | 26.3% | 持平 |
| **τ2-bench Retail** | Agentic 工具使用 | 90.8% | 85.3% | +5.5pp |
| **τ2-bench Telecom** | Agentic 工具使用 | 99.3% | 98.0% | +1.3pp |
| **MCP Atlas** | MCP 多步工作流 | **69.2%** | 54.1% | **+15.1pp** |
| **GDPval-AA** | 专家任务 | ElO 1317 | 1195 | +122 ELO |

### 安全评测

| 领域 | Gemini 3.1 Pro vs Gemini 3 Pro |
|------|-------------------------------|
| Text Safety | +0.10%（非严重） |
| Multilingual Safety | +0.11%（非严重） |
| Image→Text Safety | -0.33% |
| Unjustified Refusals | -0.08%（更少不合理的拒绝） |

### Frontier Safety 状态

所有 5 个风险域（CBRN、Cyber、Manipulation、ML R&D、Misalignment）均未达到 CCL（Critical Capability Level）警报线。

## 范式对比

与 Anthropic Sonnet 4.6/Opus 4.6/OpenAI GPT-5.3 对比：
- **ARC-AGI-2** 77.1% 显著领先所有竞品（Sonnet 4.6: 58.3%, Opus 4.6: 68.8%, GPT-5.2: 52.9%）
- **HLE** 44.4% 也高于 Sonnet 4.6 (33.2%) 和 GPT-5.2 (34.5%)，略低于 Opus 4.6 (40.0%)
- **APEX-Agents** 33.5% 是 Google 的强力领域——远超 Opus 4.6 (29.8%) 和 GPT-5.2 (23.0%)
- **BrowseComp** 85.9% 领先 Opus 4.6 (84.0%) 和 GPT-5.2 (65.8%)——Agentic 搜索能力突出
- **GPQA Diamond** 94.3% 是全场最高
- 但在 **GDPval-AA**（专家任务 ELO）上，Sonnet 4.6 (1633) 和 Opus 4.6 (1606) 明显领先 Gemini 3.1 Pro (1317)

总体来看，Gemini 3.1 Pro 在**抽象推理（ARC-AGI-2）、Agentic 搜索（BrowseComp）、长时程任务（APEX-Agents）** 三个维度上具有明显优势。

## 社区评价

模型卡于 2026 年 2 月发布。Reddit r/Bard 和 r/LocalLLaMA 社区注意到 ARC-AGI-2 77.1% 的突出表现——这一成绩在同代模型中最高。

DPO 说明：由于模型卡而非完整技术报告，社区讨论集中在 benchmark 对比上；LLM 架构细节（MoE 规格、数据配比等）未公开。

## 可复用的工程经验

1. **同代架构内迭代**：Gemini 3.1 Pro 证明，在架构不变的情况下，通过深度推理扩展（Deep Think）和数据优化，可以在 ARC-AGI-2 这类高难度 benchmark 上取得 46pp 的提升——这几乎相当于"代际升级"的幅度
2. **推理时计算扩展策略**：Deep Think 模式表明，**推理计算量（test-time compute）是架构之外最有效的质量杠杆之一**——特别是在高难度推理任务上
3. **模型卡作为技术报告**：Google 延续"模型卡替代独立技术报告"策略，核心 benchmark 数据在模型卡中公开，但训练细节（数据规模、MoE 配置）仍然不透明——这可以作为其他公司技术文档的参考格式
4. **特定领域优势**：Gemini 3.1 Pro 在 Agentic 搜索（BrowseComp 85.9%）、长时程任务（APEX-Agents 33.5%）、抽象推理（ARC-AGI-2 77.1%）上的显著优势是 Google 在该轮竞争中的差异化定位
