---
title: Gemini 3.6 Flash / 3.5 Flash-Lite / 3.5 Flash Cyber — Agent 效率层的三档分层
date: 2026-07-21
source: https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-6-flash-3-5-flash-lite-3-5-flash-cyber/
---

# Gemini 3.6 Flash / 3.5 Flash-Lite / 3.5 Flash Cyber — Agent 效率层的三档分层

**发布日期：** 2026-07-21
**来源：** https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-6-flash-3-5-flash-lite-3-5-flash-cyber/ | [Model Card (PDF)](https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-6-Flash-Model-Card.pdf)
**工程范式：** 在 Gemini 3 系列中通过 token 效率优化（不是架构革命）和第二层模型分化（Flash-Lite / Cyber 专用模型）实现 agentic 工作负载的生产级加速——先发博客+model card，无独立技术报告。

## 设计哲学

Gemini 3.6 Flash 不是一次架构突破——它明确声明"基于 Gemini 3.5 Flash"，没有公开任何架构层面的变更。核心约束是：**在不改变基础架构的前提下，让现有模型系列在 agent 场景下做更多、花更少。**

这意味着 Google 的选择是**系统级效率优化**而非架构创新：
1. **Token 效率提升：** 减少完成任务所需的输出 token 数量和推理步数
2. **价格下调：** 3.6 Flash 的输入/输出定价均低于 3.5 Flash
3. **分层深化：** 在 Flash 系列内部再做分化——Flash-Lite（极致低延迟/高吞吐）和 Flash Cyber（专用安全模型）

放弃的是什么？3.6 Flash 没有追求 benchmark 排名的大幅提升——它的性能增益是渐进式的（几个百分点），核心卖点是性价比。

## 关键架构决策

### 注意力机制
未公开。Model Card 声明"基于 Gemini 3.5 Flash"——意味着沿用了 Gemini 3.5 Flash 的注意力架构。

### 模型规模
未公开具体参数。Gemini 3.5 Flash 本身在前代的基础上做了架构简化；3.6 Flash 延续这一路线。

### 上下文窗口
- **输入：** 最多 1M token（多模态：文本、图像、音频、视频）
- **输出：** 最多 64K token
- **知识截止：** 2026年3月（部分领域有限制到2025年1月）

### 训练策略
未公开。Model Card 全部引用"see the Gemini 3.5 Flash model card"。

### 部署/推理优化
- **推理速度（Flash-Lite）：** 350 输出 token/s（Artificial Analysis Index）
- **推理速度（Flash 3.6）：** 标称 100+ token/s
- **计算机使用：** 3.6 Flash 和 3.5 Flash-Lite 都内置了 computer use 作为客户端工具
- **多模态能力：** 原生支持文本+图像+音频+视频

### 后训练与对齐
- Frontier Safety 防护增强（CBRN 和 cyber offense）
- 减少对有益用途的不必要拒绝
- 3.6 Flash 在安全评估中总体优于 3.5 Flash（详见表）

## 关键结果

以下数据均来自 Google 官方博客和 Model Card。

### 编码与 Agent 能力

| 基准 | 3.6 Flash | 3.5 Flash | 变化 |
|------|-----------|-----------|------|
| DeepSWE | 49% | 37% | +12pp |
| MLE Bench | 63.9% | 49.7% | +14.2pp |
| OSWorld-Verified | 83.0% | 78.4% | +4.6pp |
| GDPval-AA v2 | 1421 | 1349 | +72 |
| Token 效率 (AA Index) | — | — | 输出 token 减少 17% |
| DeepSWE 效率 | — | — | 输出 token 减少高达 65% |

### 3.5 Flash-Lite

- **速度：** 350 输出 token/s
- **定价：** \$0.30/1M 输入, \$2.50/1M 输出
- **质量：** 显著优于 3.1 Flash-Lite
- **内置 computer use**

### 3.5 Flash Cyber (CodeMender)

- 专为网络安全的代码安全设计的专用模型
- 配合 CodeMender 代码安全 agent 使用
- 仅限政府和可信合作伙伴通过有限访问试点计划获取

### 安全评估

| 评估维度 | 3.6 Flash vs 3.5 Flash (pp变化) |
|---------|--------------------------------|
| Text-to-Text 安全 | -1.35% (更好) |
| 多语言安全 | -5.45% (更好) |
| Image-to-Text 安全 | 0% |
| 语气 (Tone) | -3.31% (回退) |
| 无理由拒绝率 | +0.25% (更好) |

### 定价

| 模型 | 输入价格 | 输出价格 |
|------|---------|---------|
| 3.6 Flash | \$1.50/1M tok | \$7.50/1M tok |
| 3.5 Flash-Lite | \$0.30/1M tok | \$2.50/1M tok |
| 3.5 Flash (对比) | 未公开 | — |

## 范式对比

### vs Claude Opus 5 / Sonnet 5

Anthropic 走的是安全审计前置的系统卡路线，每发布一个模型都附带详尽的安全评估。Google 的 model card 与之类似但不完全一致——Google 更强调 Frontier Safety Framework 的 CCL 等级评估，而 Anthropic 更侧重 RSP 框架下的能力测绘。

### vs GPT 5.6 系列

OpenAI 的 GPT-5.6 Sol/Terra/Luna 三档分层与 Google 的三档（3.6 Flash / Flash-Lite / Flash Cyber）思路相似——都是针对不同使用场景做模型分化。不同的是 Google 做了专用安全模型（Cyber），OpenAI 则按推理能力（Sol 最强、Terra 平衡、Luna 最轻）分层。

### vs 自身 3.5 Flash

3.6 Flash 延续了相同的架构，核心变化在数据、训练过程和系统优化——不是架构革命，是效能调优。这与其他公司每代推新架构的策略形成对比。

## 社区评价

截至撰写时尚未看到广泛的技术社区讨论（3.6 Flash 为 product launch 而非技术报告发布）。

## Google 后续路线

博客透露了两个重要信息：
1. **Gemini 3.5 Pro** 正在与合作伙伴测试中，即将广泛发布
2. **Gemini 4** 的预训练已经启动——"我们最雄心勃勃的预训练工作"

## 可复用的工程经验

1. **Token 效率是可持续的竞争优势：** 在不改变架构的前提下只优化 token 使用量（减少 17-65%的输出量），已经能带来显著的成本和延迟改善。这对任何模型的 API 产品化都有启示——减少废话本身就是一次"架构升级"。
2. **分层细化的边际收益：** 在 Flash 系列内部做 Flash-Lite 和 Cyber 两个新子类，比重新训练一个全新模型成本低得多。如果基础架构足够灵活，用同一架构做模型分化是性价比最高的产品扩展方式。
3. **专用安全模型的定位：** Cyber 作为专门针对网络安全场景的模型，仅限政府和合作伙伴使用——这是"能力隔离"的一种实践，不把最高危的能力放入通用模型。
4. **Model Card 的引用链模式：** Gemini 3.6 Flash 的 model card 大量引用"see the Gemini 3.5 Flash model card"——这种链式引用在迭代发布时可以减少重复文档成本，但代价是读者需要跨多份文档才能获得完整信息。
