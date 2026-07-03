---
title: "Claude Fable 5 & Mythos 5 System Card — 安全分层工程"
date: 2026-07-03
source: anthropic.com/system-cards
---

# Claude Fable 5 & Mythos 5 System Card

**发布日期：** 2026-06-09
**来源：** anthropic.com/system-cards
**工程范式：** 能力分层 + 安全防御工程路线——同一模型两种配置，用安全系统决定谁用什么能力。

## 设计哲学

Anthropic 面对的核心约束是能力快速增长与安全部署的矛盾。他们的答案：不降能力，降访问权限。Fable 5 和 Mythos 5 是同一个底层模型，但 Fable 5 的安全分类器会在检测到高风险请求时自动降级到 Opus 4.8。

关键放弃：Fable 5 在某些任务上用户得到的不是 Fable 5 的能力，而是 Opus 4.8 的。这建立在用户不会注意到降级、或者即使注意到也不会离开的假设上。

## 关键架构决策

- **安全架构：** 双层分类器（probe + LLM classifier），覆盖 cyber/bio/chem/distillation 四个域。触发率 < 5% 的用户会话。
- **底层模型：** 具体细节未公开，已知支持 1M token 上下文、128K max output。
- **定价：** $10/$50 per M token（vs Opus 4.8 的 $4.8/$24）。
- **自适应思考（adaptive thinking）：** 推理时动态调整思考深度。
- 同一底层模型做出两种配置——Fable 5（含安全分类器，公开可用）和 Mythos 5（解除防护，限可信伙伴）。

## 关键结果

由 Epoch AI 编录。风险：美国政府引用 Anthropic 自身的安全警告，对 Fable 5 实施了出口管制——发布 72 小时后暂停全球服务。

## 范式对比

vs OpenAI GPT-5.5（统一模型，不做安全降级），Anthropic 的安全工程更激进。vs Google Gemini 3.5（走全面 agent 化路线），Anthropic 更聚焦纯安全工程。

## 社区争议

Reddit 上 "RIP Claude Fable 5 (June 9, 2026 – June 12, 2026)" 帖子生动记录了从发布到被美国政府叫停的全过程。Forbes 报道美国政府引用 Anthropic 自身的安全报告来认证其风险等级。核心争议：这是单一冲突，还是前沿 AI 监管方式的预演？社区对 Anthropic 的安全策略两极分化——有人认为它是真正的安全工程，有人认为是恐惧营销。