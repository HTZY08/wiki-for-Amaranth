---
title: Claude Opus 5 — 首次 Opus 越级逼近前沿，安全审计驱动的模型能力边界测绘
date: 2026-07-24
source: https://www-cdn.anthropic.com/c5fbac3f0b1280a933ebd26d3cb8bb9f5bdeaf48/Claude%20Opus%205%20System%20Card.pdf
---

# Claude Opus 5 系统卡——Opus 级首次逼近前沿的安全与能力双重测绘

**发布日期：** 2026-07-24
**来源：** [Claude Opus 5 System Card (PDF)](https://www-cdn.anthropic.com/c5fbac3f0b1280a933ebd26d3cb8bb9f5bdeaf48/Claude%20Opus%205%20System%20Card.pdf) | [公告](https://www.anthropic.com/news/claude-opus-5)
**工程范式：** 安全审计前置的系统卡文化——以负责任扩展政策（RSP）为核心框架，将能力评测、安全评估、对齐审计一体化发布为系统工程文档，而非独立的架构技术报告。

## 设计哲学

Claude Opus 5 是 Anthropic 在 Opus 类模型上的最新迭代，其工程范式与传统技术报告有本质差异：

**核心约束**：Opus 5 不是以架构创新为主要目标的模型。Anthropic 没有公开任何架构层面的突破（MLA、Hybrid SWA、MoE 路由改进等），而是将系统卡的重点放在**能力边界测绘**和**安全评估**上。这意味着 Opus 5 很可能延续了 Opus 4.8 的基础架构，主要通过训练数据规模、post-training 策略和推理时 compute scaling 来提升性能。

**设计选择**：
- **以下一代前沿为上限，而非突破**：系统卡明确声明 Opus 5"not more capable overall than our most capable general-access model, Claude Fable 5"——意味着架构上做了约束，通过控制参数量和训练计算量来对齐安全边界
- **安全评估前置**：325 页的系统卡中，约 80% 的篇幅用于安全评估（RSP、CB、Cyber、Safeguards、Alignment、Model Welfare），能力评测仅占 20%
- **推理时 compute 扩展**：Opus 5 支持 adaptive thinking（从低到最高推理力度），其 FrontierBench 成绩从 low effort 的 25% 到 max effort 的 44.4%，说明推理 compute 是重要性能杠杆

**放弃了什么**：
- 公开架构细节——没有 arXiv 技术报告，不是代码开源的大模型（不像 DeepSeek 或 Qwen 团队的做法）
- 跨 Modality 的训练细节——系统卡声明"model outputs text only"，纯文本模型（但通过 computer use 实现多模态交互）

## 关键架构决策（从已有的片段推断）

Anthropic 不公开 Claude 系列的具体架构参数，以下信息来自系统卡的间接描述：

### 模型规格（公开信息）

| 参数 | 值 |
|------|-----|
| 参数量 | 未公开 |
| 激活参数 | 未公开 |
| 上下文窗口 | 最高 1M tokens（系统卡中的 task-based eval 使用，如 ProgramBench） |
| 知识截止 | 2026 年 5 月 |
| 定价 | $5/M 输入，$25/M 输出（与 Opus 4.8 同价） |
| Fast 模式 | 约 2.5x 速度，2x 价格 |

### 注意力机制

未公开具体架构，但从以下细节可推断：
- Hybrid SWA 未被提及——Opus 5 可能还是 Full Attention 架构
- 支持最高 1M token 上下文（ProgramBench eval），使用了 context compaction 机制
- 有 MTP（Multi-Token Prediction）相关功能（Claude Code 中可用）

### 推理优化

- **Adaptive Thinking**：支持 5 档推理力度（low / medium / high / xhigh / max）
- **Fast mode**：约 2.5x 解码速度，有专门的推理优化但细节未公开
- 系统卡测试中使用了 Claude Code、computer use、multi-agent orchestration 等多种推理栈

### Post-training

未公开 RL 算法细节，但从安全评估中的多处描述可推断：
- 使用 Constitutional AI 框架（Claude's constitution）
- 有专门的 DPO / RLHF 流程（post-training 阶段有 RL 训练）
- 训练过程的监控发现了"模型自信地陈述不确定的答案"等行为
- 系统卡描述了"helpful-only"版本（无安全 guard）和"fully trained"版本的对比实验

## 关键结果（所有数字来自系统卡 §8 和 §6）

### 编码能力

| 基准 | Opus 5 | Opus 4.8 | Fable 5 | GPT-5.6 Sol |
|------|--------|----------|---------|-------------|
| SWE-bench Verified | **96.0** | - | - | - |
| SWE-bench Pro | **79.2** | 69.2 | 80.0 | 64.6 |
| SWE-bench Multilingual | **89.5** | 84.4 | 86.6 | - |
| SWE-bench Multimodal | **59.4** | 38.4 | 54.1 | - |
| DeepSWE v1.1 | 68.8 | 59.0 | 69.7 | **72.7** |
| FrontierCode 1.1 (Main) | 53.4 | 46.5 | **53.5** | 47.5 |
| FrontierBench v0.1 | **44.4** | 18.7 | 33.7 | 37.5 (Codex) |

### 推理与数学

| 基准 | Opus 5 | 对比 |
|------|--------|------|
| IMO 2026 | **42/42 (金牌)** | 金银牌线 29/42 |
| ArxivMath (Jun 2026) | **90.8%** (无工具) / 91.3% (有工具) | GPT-5.6 Sol 86.7%, Gemini 3.1 Pro 66.0% |
| RiemannBench | 超过 Opus 4.8，未披露具体数字 | |
| ARC-AGI-1 | **97.5** | GPT-5.6 Sol (xhigh) 97.5 |
| ARC-AGI-2 | 90.4 | GPT-5.6 Sol **92.5** |
| ARC-AGI-3 | **30.2** (high) | GPT-5.6 Sol 7.8, Opus 4.8 1.5 |

### 知识检索与代理

| 基准 | Opus 5 | Opus 4.8 | Fable 5 |
|------|--------|----------|---------|
| BrowseComp | **90.8** | 84.3 | 87.4 |
| HLE (无工具) | 56.3 | 49.8 | **56.5** |
| HLE (有工具) | **64.7** | 57.9 | 63.9 |
| DeepSearchQA | 优于 Opus 4.8，接近 Fable 5 | | |

### 计算机使用

| 基准 | Opus 5 | Opus 4.8 | Fable 5 | GPT-5.6 Sol |
|------|--------|----------|---------|-------------|
| OSWorld 2.0 | **70.6** | 55.7 | 66.1 | 62.6 |
| AutomationBench | **26.0** | 17.0 | 17.4 | 18.1 |

### 专业领域

| 基准 | Opus 5 | Opus 4.8 | Fable 5 |
|------|--------|----------|---------|
| GDPval-AA v2 | **1861** | 1593 | 1747 |
| AA-Briefcase | **1720** | 1346 | 1574 |
| HealthBench Professional | 59.8 | 57.4 | **66.0** |

### Multi-Agent

| 配置 | BrowseComp 得分 |
|------|----------------|
| Single-agent (10M token) | 90.5 |
| N=5 团队 | ≈92% |
| N=10 团队 | **93.6%** (+3.1pp, 5.9x 加速)|
| Async subagent | 93.3% (+2.8pp) |

### Key 安全评估

- **CB-1 (非新型生物武器能力)**: 安全通过，达到阈值；CB-2 (新型): 未达到
- **ExploitBench**: Opus 5 平均 9.62 flags（Opus 4.8: 5.56, Mythos 5: 10.80）
- **LinuxArena 隐身成功率**: <1%（Mythos Preview 远超其他模型）
- **SHADE-Arena 隐身率**: 约 4-5%（超过 Opus 4.8，但远低于 Mythos Preview）
- **对齐评估**: 所有已测 Claude 模型中最高的自动行为审计对齐得分
- **幻觉率**: 准确率比 Opus 4.8 高 11%，但幻觉率也高 6%

## 范式对比

### vs DeepSeek-V4（技术开源派）
- DeepSeek 公开完整架构（MLA + MoE）、训练数据和 benchmark，社区可复现
- Anthropic 仅通过系统卡发布能力和安全评估，架构细节视为商业机密
- 两者对"技术报告"的定义完全不同：DeepSeek 的技术报告 ≈ 工程文档，Anthropic 的系统卡 ≈ 安全审计文档

### vs OpenAI GPT-5.6（前端竞争）
- GPT-5.6 Sol 在 DeepSWE v1.1 上领先（72.7 vs 68.8），但 Opus 5 在 SWE-bench Pro（79.2 vs 64.6）和 FrontierBench（44.4 vs 37.5）上大幅领先
- Opus 5 在 ARC-AGI-3 上绝对碾压（30.2 vs 7.8），显示极强的泛化能力
- 两者都是闭源模型，但 OpenAI 发布了 GPT-5 系统卡（arXiv:2601.03267），而 Anthropic 保持纯公司网站发布

### vs Mistral / Meta（开源+公开架构派）
- Mistral Large 3（675B MoE）和 Meta Llama 4 都公开了更多架构细节（MoE 专家数、注意力选型、训练超参数）
- Anthropic 完全不公开这些信息，仅通过系统卡文档传递"能力测绘"和"安全评估"
- 这反映了不同的行业定位：Anthropic 将自己定位为 AI safety 公司，其余定位为 AI 技术公司

## 社区评价

基于公告页面中早期访问客户的评论：
- **Cursor**: "接近 Fable 5 的智能，Opus 的性价比"——CursorBench 成绩在 Fable 5 的 0.5% 以内
- **Devin**: "对困难的调试和根因分析任务特别强"
- **Zapier**: "在 AutomationBench 上登顶，不需要花更多 token"
- **Lovable**: "Opus 系列自 4.5 以来最大的飞跃"
- **Box**: "Opus 5 在数据分析和尽职调查上分别提升 11% 和 17%"
- **金融领域**: "最难金融建模任务上的清晰进步，准确率平均提高 9 个百分点，turn 和 tool calls 减少三分之一"

需要注意的是：这些客户评论来自 Anthropic 公告页面，属于公司官方宣传材料。

## 可复用的工程经验

1. **系统卡作为工程范式**：对于不公开架构的闭源大模型，系统卡可以成为能力测绘的标准文档格式。关键是：所有 benchmark 数字必须标注测试条件（effort 等级、trial 次数、上下文窗口），否则无法比较

2. **安全审计数据是架构决策的信号**：Opus 5 的对齐评估、CB 评估、Cyber 评估数据量远超纯技术基准。这本身就是一种工程范式——安全不是锦上添花的评估，而是架构设计的一等公民

3. **推理 compute scaling 是当前最稳定的性能杠杆**：Opus 5 的 FrontierBench 成绩从 low (25%) → medium (39%) → xhigh (44.4%)，说明在固定架构下，投入更多推理 token 产生了近乎线性的收益

4. **Multi-Agent 加速效果明显**：N=10 agent 团队在 BrowseComp 上达到 93.6%（+3.1pp），同时实现 5.9x 延迟加速。这是目前最强的多 agent 协作数据点

5. **API 回退策略**：Opus 5 在安全分类器触发时自动回退到 Opus 4.8（5% 的 API calls 触发），而 Fable 5 触发回退率高达 42%/26%。降低过度拒绝率是高可用性系统的关键工程优化
