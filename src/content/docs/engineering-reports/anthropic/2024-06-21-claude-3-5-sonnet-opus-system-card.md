---
title: Claude 3.5 Sonnet/Opus System Card — 能力跃迁 + Agentic 转向
date: 2026-07-03
source: anthropic.com/system-cards
---

# Claude 3.5 Sonnet/Opus System Card

**发布日期：** 2024-06-21（Claude 3.5 Sonnet 初版）、2024-10-22（升级版 + Claude 3.5 Haiku）、2025-02（Claude 3.7 Sonnet）  
**来源：** Model Card Addendum: Claude 3.5 Sonnet / Claude 3.5 Haiku and Upgraded Claude 3.5 Sonnet  
**工程范式：** Agentic 能力工程 + 多模态扩展

## 设计哲学

Claude 3.5 系列标志着 Anthropic 从"纯语言助手"向"agentic 系统"的战略转向。核心设计理念是：**能力越强 ≠ 越危险**，只要安全评估能跟上。

关键声明：Claude 3.5 Sonnet 在几乎所有 benchmark 上超越 Claude 3 Opus（当时的最强模型），"while operating faster and at a lower cost"——这意味着能力-成本曲线的 Pareto 改进，而非线性 scaling。

2024 年 10 月的升级版引入了**computer use（计算机使用）**能力——模型可以解读 GUI 截图并生成鼠标点击/键盘输入等操作。这是 Anthropic 在 agentic safety 方向的关键工程决策：与其在受限环境中隔离 agent，不如在真实操作系统中测试并在 System Card 中透明报告失败率。

## 关键架构决策

### 训练与对齐
- **无架构革命**：Claude 3.5 系列是 Claude 3 家族的演进而非全新架构。
- **知识截止**：Sonnet 初版 2024 年 1 月；升级版 2024 年 4 月；Haiku 2024 年 7 月。
- **ASL-2 分类**：所有 Claude 3.5 模型均保持在 AI Safety Level 2（不会造成灾难性伤害风险），未触发 RSP 全面评估所需的 4 倍有效计算阈值。

### Computer Use（计算机使用）
- **系统架构**：模型接收截图 → 生成 GUI 命令（鼠标、点击、按键）→ 导航网站/交互 UI → 完成多步流程。
- **评估框架**：OSWorld（操作系统、办公、日常、专业、工作流五大类真实任务）。
- **结果**：15 步内 14.9%、50 步内 22.0%，远低于人类 72.36%。明确声明"substantial room for future improvement"。

### Agentic Coding
- 模型执行搜索→查看→编辑→测试的 agentic 循环，典型处理 3-4 个文件，最多 20 个文件。
- **内部评估**：Claude 3.5 Sonnet（原版）解决 64% 问题（Claude 3 Opus 38%）；升级版提升至 78%。

## 关键结果

### Claude 3.5 Sonnet（2024-06）核心 Benchmark

| Benchmark | Claude 3.5 Sonnet | Claude 3 Opus | GPT-4o |
|-----------|-------------------|---------------|--------|
| GPQA Diamond | **59.4%** | 50.4% | 53.6% |
| MMLU (5-shot) | **90.4%** | 88.2% | 88.7% |
| HumanEval | **92.0%** | 84.9% | 90.2% |
| Visual MMMU | **68.3%** | 59.4% | 69.1% |
| MathVista | **67.7%** | 50.5% | 63.8% |

### 升级版 Claude 3.5 Sonnet（2024-10）改进

| Benchmark | 升级版 | 原版 | 提升 |
|-----------|--------|------|------|
| SWE-bench Verified | **49.0%** | 33.4% | +15.6pp |
| GPQA Diamond | **65.0%** | 59.4% | +5.6pp |
| MATH | **78.3%** | 71.1% | +7.2pp |
| AIME 2024 (Maj@64) | **27.6%** | 16.7% | +10.9pp |
| TAU-bench Retail | **69.2%** | 62.6% | +6.6pp |

### Claude 3.5 Haiku（2024-10）
- 在同类模型中表现出色，多项 benchmark 匹敌原版 Claude 3.5 Sonnet 和 Claude 3 Opus。
- SWE-bench Verified: 40.6%（对比 Claude 3 Haiku 的 7.2%）。

### 安全评估（Refusals）

| 指标 | 升级版 Sonnet | 原版 Sonnet | Claude 3 Opus |
|------|-------------|-------------|--------------|
| Toxic 正确拒绝 | 89.2% | 96.4% | 92.0% |
| Non-toxic 错误拒绝 | **5.3%** | 11.0% | 11.9% |
| XSTest 错误拒绝 | 4.3% | **1.7%** | 8.3% |

升级版在 non-toxic prompt 上大幅减少了错误拒绝，说明安全校准精度提升。

## 范式对比

| 维度 | Claude 3.5 | GPT-4o | Gemini 1.5 Pro |
|------|-----------|--------|-----------------|
| 多模态 | 视觉理解（非生成） | 原生多模态 | 原生多模态 |
| Computer Use | 首次引入 | 无 | 无 |
| Agentic 评估 | SWE-bench + 内部编码 | 较少公开 | 较少公开 |
| 安全分级 | ASL-2（系统化 RSP） | 未系统化 | 未系统化 |

## 可复用工程经验

1. **渐进式安全分类**：ASL-2 意味着不需要完整 RSP 评估——建立了能力阈值与评估深度的对应关系，而非一刀切。
2. **Computer Use 的工程化测试框架**：OSWorld 提供了真实操作系统环境的标准化测试方法，可复用于后续模型的 agentic safety 评估。
3. **Agentic Coding 的内部评估**：Anthropic 构建了多步骤编码任务 + 工具使用的内部评估集（64%→78% 的提升可追踪），这种内部评估比公开 benchmark 更敏感。
4. **外部测试合作网络**：US AISI、UK AISI、METR 三家外部机构进行独立测试——建立了行业标准的前置测试协作模式。
5. **Human Feedback 的多维赢率分析**：按 Law (82%)、Finance (73%)、Philosophy (73%) 等专业领域细分评估，而非单一 win rate——提供更精细的能力画像。

## 局限性

Computer Use 的 22%（50 步内）远低于人类 72.36%，agentic 能力仍处于早期。ASL-2 分类意味着未触发最深度的安全评估。部分 benchmark 的 SOTA 时间窗口极短（被 GPT-4o 在 MMMU 上反超）。错误拒绝率在 toxic prompt 上从 96.4% 降到 89.2%——安全-能力的 tradeoff 尚未解决。
