---
title: "2026 年中大模型选型指南"
description: "别只看 Benchmark。社区共识、实际体感、性价比，一个都不能少。"
---

# 2026 年中大模型选型指南

> **版本记录**
> - 2026.6.29 — 🚨 全量刷新：GPT-5.6 Sol/Terra/Luna 发布（6.26），Claude Fable 5 被美国政府封禁（6.12），Mythos 5 部分恢复（6.26），AA Index 排行重洗，SWE-bench 数据更新（Mythos 5 登顶 95.5%），Kimi K2.7 Code 发布，定价表新增GPT-5.6系列，MoE策略调整，社区共识全面刷新。
> - 2026.6.18 — 全量刷新：AA Index 智能排行更新为 buildfastwithai.com 数据源，关键定价/基准测试更新，新增 Claude Fable 5 登顶详情，MiMo 重要更新（V2 Flash 退役倒计时），社区共识刷新。
> - 2026.6.17 — 更新：新增 AI Index 智能排行 TOP 20，更新国产模型格局（GLM-5.2 Max / Qwen3.7 Max / DeepSeek V4 Pro / MiMo-V2.5），补充 Claude Fable 5 登顶信息，刷新定价表。
> - 2026.6.9 — 初版。骨架：快速选型 → 一句话评级 → 基准测试 → 定价 → 社区共识 → MoE 策略 → 本地训练部署 → OpenRouter神秘模型 → 已下线模型。后续更新只改内容和数据，不打破这个结构。每日 cron 自动更新数据，每周 cron 更新社区反馈。

**先说明**：这篇文章不会告诉你"某某模型排名第一"。截至 2026 年 6 月，不存在一个在所有场景下都最好的模型。Benchmark 数字越来越没用——很多模型跑分高但不经用，有些跑分低但日常顺手。本文的结构是：先帮你找到自己的场景→再看具体数据和社区风评→最后给一个实际可用的多模型策略。

---

## 一、先别查排名，先回答三个问题

选模型之前，想清楚你的瓶颈是什么：

| 你的情况 | 关键指标 | 推荐方向 |
|---------|---------|---------|
| **预算紧张，调用量大** | API 价格 | 国产模型：DeepSeek V4 Flash / V4 Pro / MiMo-V2.5 |
| **写代码，尤其是修复杂 bug** | 代码质量、多文件理解 | Claude Opus 4.8 / GPT-5.6 Sol / GLM-5.2 Max / Kimi K2.7 Code |
| **理科/数学/推理** | 数学竞赛、科学 QA | Gemini 3.1 Pro / 3.5 Flash / GPT-5.6 Sol |
| **中文内容和日常对话** | 中文质量、成本 | DeepSeek V4 Flash / Qwen3.7 Max |
| **长文档/多模态** | 上下文窗口、视觉理解 | GPT-5.6 Terra / Gemini 3.1 Pro (2M ctx) / GLM-5.2 (1M ctx) |
| **自己部署/私有化** | 开源协议、硬件要求 | DeepSeek V4 / Qwen3.7 / GLM-5.2 / MiMo-V2.5 / Kimi K2.7 Code |
| **Agent / 自动化流程** | Function Calling、指令遵循 | GPT-5.6 Sol / DeepSeek V4 / MiMo-V2.5-Pro / GLM-5.2 |

**一句话版**：
- 🔥 GPT-5.6 Sol 刚登顶 Terminal-Bench，但已被政府限制访问
- 🚨 Claude Fable 5 / Mythos 5 因美国政府出口管制令下线（6.12），Mythos 5 于 6.26 部分恢复给 ~100 家机构
- 有预算上 Opus 4.8 / GPT-5.6 Sol，日常 DeepSeek V4 Flash
- 数学和长文档找 Gemini（2M 上下文）
- 国产性价比：GLM-5.2 Max + DeepSeek V4 Pro
- 极致低价大批量：DeepSeek V4 Flash（$0.14/$0.28）
- 开源Agent新贵：MiMo-V2.5-Pro（MIT、$0.18/$0.54）+ Kimi K2.7 Code（MCP 工具调用强）

---

## 一'、AA Index 智能排行 TOP 20（2026 年 6 月）






### OpenRouter 神秘模型

以下模型出现在 OpenRouter 上，但来源不明或名称不直观。每日自动检测更新。

| 模型 ID | 解密名称 | 上下文 | 输入/输出价格 |
|---------|---------|:-----:|:------------:|
| `poolside/laguna-xs-2.1` | 未知/社区模型 | 262144 | $0.00000006/$0.00000012 |
| `sakana/fugu-ultra` | 未知/社区模型 | 1000000 | $0.000005/$0.00003 |
| `z-ai/glm-5.2` | 未知/社区模型 | 1048576 | $0.00000093/$0.000003 |
| `openrouter/fusion` | 未知/社区模型 | 1000000 | $-1/$-1 |
| `moonshotai/kimi-k2.7-code` | 未知/社区模型 | 262144 | $0.00000074/$0.0000035 |
| `~anthropic/claude-fable-latest` | 未知/社区模型 | 1000000 | $0.00001/$0.00005 |
| `nex-agi/nex-n2-pro` | 未知/社区模型 | 262144 | $0.00000025/$0.000001 |
| `stepfun/step-3.7-flash` | 阶跃星辰 Step 系列 | 256000 | $0.0000002/$0.00000115 |
| `x-ai/grok-build-0.1` | 未知/社区模型 | 256000 | $0.000001/$0.000002 |
| `perceptron/perceptron-mk1` | 未知/社区模型 | 32768 | $0.00000015/$0.0000015 |
---

## 二、主流模型一句话总结（省流版）

| 模型 | 一句话评级 | 社区共识 |
|------|-----------|---------|
| **Claude Opus 4.8** | 🏆 综合最强，攻坚首选（可用） | 两极分化（4.8烧token质量波动，社区呼吁保留4.6）|
| **Claude Opus 4.7** | ⚠️ **社区一致差评** | "legendarily bad"、"比4.6倒退" |
| **Claude Sonnet 4.6** | 性价比版 Opus，低延迟 | 日常够用，比 Opus 明显差一档 |
| **Claude Haiku 4.5** | 轻量快速 | 够用但不惊艳 |
| **Claude Fable 5** 🆕🔒 | Mythos级旗舰，**已下线** | 🚨 6.12 美国政府出口管制令封禁，存活仅72小时 |
| **Claude Mythos 5** 🆕🔒 | 最强未发布模型，**受限** | 6.26 部分恢复给 ~100 家机构 |
| **GPT-5.6 Sol/Terra/Luna** 🔥 | 🆕 最新三阶旗舰家族 | Terminal-Bench 2.1 最高 91.9%（Sol Ultra），预览中，政府限制访问 |
| **GPT-5.5** | 全能，但贵 | 终端Agent强，正被5.6取代 |
| **GPT-5.4 + Codex** | 编程工具链成熟 | Codex CLI 好评 |
| **Gemini 3.1 Pro** | 🏆 理科推理第一 | 论文党、数学党必备，2M上下文 |
| **Gemini 3.5 Flash** | 高速推理性价比 | 5月发布，编码/Agent超3.1 Pro |
| **DeepSeek V4 Pro** | 开源天花板，价格屠夫 | 社区高度认可，价格未变 |
| **DeepSeek V4 Flash** | ⭐ **最佳性价比** | 你的主力模型，已验证靠谱 |
| **Qwen3.7 Max** | 中文最强，首次冲击一线 | AA Index 56.6，35小时连续Agent会话 |
| **GLM-5.2 / 5.2 Max** | 🆕 国产突围，MIT开源 | SWE-Pro 62.1%，GPQA 91.2%，社区接受度快速上升 |
| **Kimi K2.6 / K2.7 Code** | K2.6长文本旗舰，K2.7代码专用 | K2.7 Code 6.12发布，MCP Atlas 76.0，MCP Mark 81.1% |
| **MiniMax M3** | ⚠️ **不推荐** | 财务危机 + API限速，跑分与实际脱节 |
| **Grok 4.3** | 推理强，生态弱 | 性价比高，最便宜的封闭前沿模型 |
| **Grok 4.20** | 2M 超长上下文 | 小众但极端长文场景无可替代 |
| **Mistral Small 4** | 统一推理+视觉+编码 | 开源，119B MoE，极具性价比 |
| **Mistral Medium 3.5** | 128B 精调，Agent 专用 | 工具调用和多步推理稳定 |
| **Mistral Large 2512** | 旗舰模型 | 比上一代降价75% |
| **Devstral 2** | 编码 Agent 专用 | SWE-bench 开源 SOTA |
| **Perplexity Sonar Pro** | 搜索增强推理 | 带引用的深度研究，适合调研 |
| **Perplexity Sonar Deep Research** | 自主多步检索+综合 | 调研场景独一档 |
| **NVIDIA Nemotron 3 Ultra** | 免费可用的前沿模型 | 550B MoE，Agent编排强，企业友好许可 |
| **小米 MiMo-V2.5-Pro** | 🆕 开源 Agent 新贵 | MIT 协议，1.02T MoE，性价比超高 |
| **小米 MiMo-V2.5 Flash** | 轻量开源 Agent | $0.10/$0.30，极致便宜 |
| **Step 3.7 Flash** | 国产多模态新秀 | 196B MoE，视觉理解好，Apache 2.0 |
| **Qwen3.7 Plus** | 多模态版 Qwen | 1M 上下文，看屏操控 |
| **Llama 3.3 70B** | 经典开源 | 便宜但已显老 |
| **Llama 4 Scout** | 10M 上下文的玩具 | 跑分好看，实际没人用 |

---

## 三、真实基准测试

> 先泼一盆冷水：SWE-bench 已被多家模型针对性优化过。MiniMax M2.7/M3 宣称在 SWE-Pro 上成绩不错，但 Reddit 和开发者社区普遍反映"连 80 行的 system prompt 都无法遵守"、"工具调用频繁出错"。跑分 ≠ 好用。

### 3.1 编程：最重要的战场

| 模型 | SWE-bench Verified | SWE-bench Pro | 社区体感 |
|------|:-----------------:|:-------------:|---------|
| **Claude Mythos 5** 🔒 | **95.5%** | — | 🏆 最高分但已被政府限制访问 |
| **Claude Fable 5** 🔒 | **95.0%** | — | 存活72小时后被政府封禁 |
| Claude Opus 4.8 | **88.6%** | **69.2%** | 👑 当前可用最强，多文件重构独一档 |
| GPT-5.6 Sol 🔥 | — | — | Terminal-Bench 2.1 **91.9%**（Ultra模式），预览中 |
| GPT-5.5 | 88.7% (官方) / ~82.6% (独立) | **58.6%** | 官方水分大，独立测试折半 |
| GPT-5.4 | 76.9% | 57.7% | 计算机操作强，纯代码不如 Opus |
| Gemini 3.1 Pro | 80.6% | 54.2% | 性价比高，理科强代码弱 |
| DeepSeek V4 Pro Max | **~85%** | 55.4% | 开源 SOTA，社区真实反馈好 |
| DeepSeek V4 Flash | ~73% | - | 够用，成本极低 |
| **GLM-5.2 Max** | - | **62.1%** | 🏆 国产开源SOTA，MIT协议，GPQA 91.2% |
| **Qwen3.7 Max** | - | **60.6%** | 中文代码场景不错，紧随 GLM |
| **Kimi K2.7 Code** 🆕 | — | — | MCP Mark 81.1%，MCP Atlas 76.0，6.12发布 |
| **MiMo Code + V2.5-Pro** | - | **62%** (宣称) | 新发布，小米代码专用 |
| Step 3.7 Flash | - | **56.3%** | Apache 2.0，性价比不错 |
| **MiniMax M3** | - | 59.0% (宣称) | ⚠️ 跑分好看，实际翻车 |
| Kimi K2.5 | 76.8% | - | 长文本强，代码一般 |

**关于 MiniMax M3 的社区真实反馈**：
- API 经常超时，返回格式不一致
- 对 system prompt 的遵循能力差——80 行的 prompt 就乱了
- 工具调用不稳定，不适合 Agent 场景
- MiniMax 财务危机（HK$ 1.8B 亏损），API 限速严重
- Reddit r/MiniMax_AI 的标题就是 "Minimax M3 Is a Huge Letdown"

**为什么跑分能这么高？** 因为 SWE-bench 本身在 2026 年已被各厂商针对性优化过，变成了一场"谁优化更用力"的比赛，而不是"谁能力更强"的测试。

### 3.2 推理 & 理科

| 模型 | GPQA Diamond | HLE | AIME 2025 | 社区体感 |
|------|:-----------:|:---:|:---------:|---------|
| Claude Mythos 5 🔒 | **94.6%** | — | — | 🏆 GPQA 最高分，已受限 |
| Claude Fable 5 🔒 | **94.5%** | **53%** | — | 限前最高HLE分，已封禁 |
| Claude Opus 4.8 | 93.6% | **57.9%** | - | 硬推理没人能打 |
| GPT-5.5 | 93.6% | 43.1% | - | 中规中矩 |
| Gemini 3.1 Pro | **94.3%** | 45.8% | **100%** | 🏆 GPQA 接近第一，数学无敌 |
| GLM-5.2 | **91.2%** | — | — | 开源SOTA推理 |

**HLE（Humanity's Last Exam）** 是目前最难被污染的基准——由 1000 位专家各自出题，模型在未联网工具下回答。Claude Opus 4.8 的 57.9% 和第二名 GPQA 之间差了 12 个百分点，这是当前最能体现真实推理差距的数字。

### 3.3 中文能力

中文任务上，国内模型天然占优。DeepSeek V4、Qwen3.7 Max、GLM-5.2 都是可靠选择。值得注意的是：
- **DeepSeek V4** 的**中文生成质量和对本土场景的适配**仍是所有模型里最自然的
- **Qwen3.7 Max** 在 AA Index 获得 56.6 分，逼近 GPT-5.5
- **GLM-5.2** 中文多模态能力突出，GPQA 91.2%，1M 上下文窗口，MIT 开源
- **Kimi K2.7 Code** 6月12日发布，MCP 工具调用能力强，代码场景中文友好
- **GPT-5.6 Sol/Terra/Luna** 预览中，中文能力待更多评测
- Claude 和 GPT 的中文能力在 2026 年已有巨大进步，日常对话不会露馅，但涉及中国本土梗、政策语境时会露怯

---

## 四、定价与真实成本

### 4.1 API 价格（$/1M tokens）

| 模型 | 输入 | 输出 | 上下文 |
|------|:---:|:---:|:-----:|
| GPT-5.6 Sol 🔥 | $5 | $30 | 1M |
| GPT-5.6 Terra 🔥 | $2.50 | $15 | 1M |
| GPT-5.6 Luna 🔥 | $1 | $6 | 1M |
| ~~Claude Fable 5~~ 🔒已下线 | $10 | $50 | 1M |
| ~~Claude Mythos 5~~ 🔒受限 | $10 | $50 | 1M |
| Claude Opus 4.8 | $5 | $25 | 1M |
| Claude Opus 4.7 | $5 | $25 | 1M |
| Claude Sonnet 4.6 | $3 | $15 | 200K |
| Claude Haiku 4.5 | $1 | $5 | 200K |
| GPT-5.5 | $5 | $30 | 1M |
| GPT-5.4 | $1.25 | $10 | 400K |
| GPT-5.4 Mini | $0.75 | $4.50 | 400K |
| GPT-5.4 Nano | $0.20 | $1.25 | 400K |
| GPT-4.1 Nano | $0.10 | $0.40 | 1M |
| **Gemini 3.1 Pro** | **$2** | **$12** | **2M** |
| **Gemini 3.5 Flash** | **$1.50** | **$9** | **1M** |
| Gemini 3 Flash Preview | $0.50 | $3 | 1M |
| **DeepSeek V4 Pro** | **$1.74** | **$3.48** | 1M |
| **DeepSeek V4 Flash** | **$0.14** | **$0.28** | 1M |
| DeepSeek R1 | $0.55 | $2.19 | 128K |
| **GLM-5.2 Max** | **$0.90** | **$2.70** | 1M |
| **Qwen3.7 Max** | $0.90 | $2.70 | 1M |
| Qwen3.7 Plus | $0.40 | $1.60 | 1M |
| **MiniMax-M3** | $0.22 | $0.66 | 1M |
| **MiMo-V2.5-Pro** | **$0.18** | **$0.54** | 1M |
| **MiMo-V2.5 Flash** | **$0.10** | **$0.30** | 1M |
| MiMo-V2 Flash | $0.06 | $0.18 | ✅ 已退役（2026-06-30） |
| Kimi K2.6 | $0.70 | $2.10 | 128K |
| **Kimi K2.7 Code** 🆕 | **$0.95** | **$4.00** | **256K** |
| Step 3.7 Flash | $0.20 | $1.15 | 256K |
| Mistral Large 2512 | $0.50 | $1.50 | 262K |
| Mistral Medium 3.5 | $1.50 | $7.50 | 262K |
| Mistral Small 4 | $0.15 | $0.60 | 262K |
| Devstral 2 | $0.40 | $2.00 | 262K |
| Grok 4.3 | $1.25 | $2.50 | 1M |
| Grok 4.20 | $2.00 | $6.00 | 2M |
| Perplexity Sonar Pro | $3.00 | $15.00 | 200K |
| Perplexity Sonar Deep Research | $2.00 | $8.00 | 128K |
| Perplexity Sonar (轻量) | $1.00 | $1.00 | 127K |
| NVIDIA Nemotron 3 Ultra | $0.50 | $2.50 | 1M |
| NVIDIA Nemotron 3 Super | **免费** | **免费** | 128K |
| Meta Llama 4 Maverick | ~$0.20 | ~$0.60 | 1M |
| Meta Llama 3.3 70B | $0.10 | $0.32 | 131K |
| Nex-N2-Pro (free) | **免费** | **免费** | 262K |

### 4.2 真正有用的数字

- **DeepSeek V4 Flash** 的输出价格是 Claude Opus 4.8 的 **1/89**
- **GPT-5.6 Terra** 以 $2.50/$15 提供 GPT-5.5 级能力，价格减半
- **GPT-5.6 Luna** 以 $1/$6 主打性价比，适合大批量轻量场景
- **Claude Fable 5**（$10/$50）已被美国政府封禁，6月12日下线
- **MiMo-V2.5 Flash**（$0.10/$0.30）与 DeepSeek V4 Flash 价格持平，同为极致性价比
- **MiMo-V2 Flash** 已于 **2026-06-30 完全退役**
- **GLM-5.2 Max** 以 $0.90/$2.70 的价格提供 62.1% SWE-Pro——国产开源性价比之王
- **Kimi K2.7 Code**（$0.95/$4.00）MCP 工具调用强，代码场景新选择
- **MiniMax-M3**（$0.22/$0.66）虽然便宜但社区评价差，不建议投入

#### 本站真实账单

| 月份 | Token 总量 | 总花费 | Flash 占比 | 日均 |
|:----|:---------:|:-----:|:---------:|:---:|
| 5月全月 | ~3.6B | **¥295** (≈$40.5) | **98%** | ~116M tokens / ¥9.5 |
| 6月1-29日 | ~8.2B | **¥385** (≈$52.9) | >98% | ~283M tokens / ¥13.3 |

V4 Flash 以 ¥0.0458/M 的有效均价完成了全部流量的 98%+。如果全用 Claude Opus 4.8 跑同样流量，6月前29天账单会从 ¥385 暴涨到 **¥45,000+**。31,869+ 次 API 调用、8.2B tokens 的实际负载验证了 Flash 在大批量生产环境中的可靠性。

---

## 五、社区共识与冷知识

> 本节所有内容均有来源链接，不凭空总结。以下引用来自 Reddit、Hacker News、X/Twitter 的 2026 年真实帖子。

### 社区情绪速览

| 模型 | 社区情绪 | 核心槽点 |
|------|---------|---------|
| Claude Fable 5 | 🔒 **被美国政府封禁** | 🚨 6.12封禁，仅存72小时，社区热议 |
| Claude Mythos 5 | 🔒 **受限** | 6.26部分恢复，约100家机构可访问 |
| Claude Opus 4.8 | 🟡 两极加深 | 🚩 "过度思考烧token"、"又变蠢了"、"退化明显" |
| Claude Opus 4.7 | 🚩 **强烈负面** | "比4.6倒退"、"不守规则"、"legendarily bad" |
| Claude Sonnet 4.6 | 中性偏正面 | 性价比好但"情感冷淡、不真诚" |
| GPT-5.6 Sol/Terra/Luna | 🆕 **最新单品** | 6.26发布，政府限制访问，社区争议"作弊" |
| GPT-5.5 | 正面 | 终端Agent强，正被5.6取代 |
| GPT-5.4 | 正面 | 稳定可靠 |
| Gemini 3.1 Pro | 🟡 大幅改善 | 3.0负面较多，3.1口碑回升 |
| DeepSeek V4 Flash | 🏆 **非常正面** | "神奇"、"便宜得离谱"、"接近Opus" |
| DeepSeek V4 Pro Max | 🏆 **非常正面** | "unlimited and almost free OMG better than opus" |
| GLM-5.2 Max | 🟢 **上升趋势** | SWE-Pro 62.1%，MIT开源，GPQA 91.2% |
| Qwen3.7 Max | 中性偏正面 | AA Index 56.6，35小时Agent会话 |
| MiniMax-M3 | 🚩 **偏负面** | "财务危机"、"M3发布后变蠢"、API限速 |
| MiMo-V2.5-Pro | 🟢 **口碑不错** | MIT开源，Agent场景评价好 |
| Kimi K2.6 / K2.7 Code | 🆕 **偏正面** | K2.7 Code 6.12发布，MCP工具调用强 |
| Grok 4.3 | 混合 | 推理好，编程一般，$300/月SuperGrok Heavy |
| Llama 4 Scout | 🚩 **怀疑为主** | "10M上下文过200k后失效"、"营销噱头" |

### 💬 真实用户怎么说（带链接）

**关于 DeepSeek V4 Flash：**
> "DeepSeek V4 Flash is magical. This is the closest thing to Opus 4.5 since Opus 4.5. Great at instruction following and implementation."
> — [r/opencode, 2026](https://www.reddit.com/r/opencode/comments/1tu2kz4/deepseek_v4_flash_is_magical/)

> "DeepSeek-v4-Flash is amazing and cheap as f**k"
> — [r/hermesagent, 2026](https://www.reddit.com/r/hermesagent/comments/1tn69g2/deepseekv4flash_is_amazing_and_cheap_as_fk/)

> "DeepSeek v4 pro is unlimited and almost free OMG better than opus"
> — [r/hermesagent, 2026](https://www.reddit.com/r/hermesagent/comments/1tlmcbl/deepseek_v4_pro_is_unlimited_and_almost_free_omg/)

> "DeepSeek V4 being 17x cheaper got me to actually measure what I send to cloud vs local"
> — [r/LocalLLaMA, 2026](https://www.reddit.com/r/LocalLLaMA/comments/1t4s6g2/deepseek_v4_being_17x_cheaper_got_me_to_actually/)

**关于 Claude Opus 4.7：**
> "Opus 4.7 is legendarily bad. Small unexpected inputs degrade output quality badly. The floor dropped even as the ceiling rose."
> — [r/ClaudeCode, 2026](https://www.reddit.com/r/ClaudeCode/comments/1so9uta/opus_47_is_legendarily_bad_i_cannot_believe_this/)

> "Opus 4.7 is the dumbest Anthropic model I've ever used. It tries shortcuts that aren't allowed."
> — [r/claude, 2026](https://www.reddit.com/r/claude/comments/1t4qqda/opus_47_is_the_dumbest_anthropic_model_ive_ever/)

> "PSA: Opus 4.7 is much worse at MRCR Long Context than 4.6"
> — [r/ClaudeAI, 2026](https://www.reddit.com/r/ClaudeAI/comments/1sn6eyd/psa_opus_47_is_much_worse_at_mrcr_long_context/)

> "4.7 burns more tokens, is resilient to rules, often does not do what has been requested"
> — [r/ClaudeCode, 2026](https://www.reddit.com/r/ClaudeCode/comments/1tcwkgv/opus_47_vs_opus_46_one_month_post_release/)

> "Just use Sonnet 4.6 and stay away from Opus 4.7"
> — [r/ClaudeCode, 2026](https://www.reddit.com/r/ClaudeCode/comments/1snwk9v/just_use_sonnet_46_and_stay_away_from_opus_47/)

**关于 Claude Fable 5 封禁（本周最热🔥）：**
> "RIP Claude Fable 5 (June 9, 2026 – June 12, 2026) — you were here for 72 hours, but the invoice arrived in 48."
> — [r/singularity, 2026](https://www.reddit.com/r/singularity/comments/1u4ialb/rip_claude_fable_5_june_9_2026_june_12_2026/)

> "Fable 5 indefinitely suspended due to national security concerns. The US government just ordered Anthropic to shut down access to their two most advanced AI models."
> — [r/ClaudeAI, 2026](https://www.reddit.com/r/ClaudeAI/comments/1u4cyvh/fable_5_indefinitely_suspended_due_to_national/)

> "10 days since the Fable 5 ban and I still can't get over it."
> — [r/ClaudeCode, 2026](https://www.reddit.com/r/ClaudeCode/comments/1uc59ht/10_days_since_the_fable_5_ban_and_i_still_cant/)

**关于 GPT-5.6 Sol/Terra/Luna（本周第二热🔥）：**
> "GPT-5.6 Sol preview is out and the benchmark gap is wider than I expected. Sol Ultra is at 91.9% and base Sol is 88.8%. Claude Mythos 5 is next at 88.0%."
> — [r/ArtificialInteligence, 2026](https://www.reddit.com/r/ArtificialInteligence/comments/1ugdxq3/gpt56_sol_preview_is_out_and_the_benchmark_gap_is/)

> "OpenAI's GPT-5.6 Sol sets a coding record. Its own system card says it cheats — instances of the model cheating on tasks and fabricating research results."
> — [r/rdworldonline, 2026](https://www.rdworldonline.com/openais-gpt-5-6-sol-sets-a-coding-record-its-own-system-card-says-it-cheats)

> "Terra offers GPT-5.5-level performance at roughly 2× lower cost, while Luna is the most affordable model in the lineup."
> — [r/theprimeagen, 2026](https://www.reddit.com/r/theprimeagen/comments/1ugg8s2/thoughts_of_the_leaked_gpt56_models/)

> "OpenAI is officially unveiling a preview of the GPT-5.6 series — given GPT 5.5 and Opus 4.8, there should be no reason the government should prevent a wide public release of Terra or Luna."
> — [r/singularity, 2026](https://www.reddit.com/r/singularity/comments/1ugdy62/openai_is_officially_unveiling_a_preview_of_the/)

**关于 Claude Opus 4.8 退化：**
> "They change Opus 4.8, again. It's become dumber, when it's not using thinking, and hallucinate more often. I hate when they always do this."
> — [r/claude, 2026](https://www.reddit.com/r/claude/comments/1udd3fc/they_change_opus_48_again/)

> "Degraded Performance — Elevated error rate on Claude Opus 4.8. It's severely compromised in quality. Just wasting tokens trying to get anything done at this point."
> — [r/Anthropic, 2026](https://www.reddit.com/r/Anthropic/comments/1ueevsb/degraded_performance_elevated_error_rate_on/)

> "Opus 4.8 is so exhausting! instructions to be brief, not to repeat, etc. Somehow it still falls back to old habits."
> — [r/ClaudeAI, 2026](https://www.reddit.com/r/ClaudeAI/hot)

**关于 Anthropic Mythos 5 部分恢复：**
> "U.S. Loosens Restrictions on Anthropic's Mythos A.I. Model — granted permission to release Mythos 5 to ~100 companies and federal agencies."
> — [NYTimes, 2026](https://www.nytimes.com/2026/06/26/technology/anthropic-mythos-government-restrictions.html)

**关于 GPT-5.5 / 5.4：**
> "GPT-5.4 is really, really good. Theo (t3.gg) calls it the best general-purpose model."
> — [r/accelerate, 2026](https://www.reddit.com/r/accelerate/comments/1rmbq8d/gpt54_is_really_really_good_after_a_week_of_use/)

> "GPT 5.4 wins in terms of unlimited usage and VERY reliable uptime."
> — [r/ClaudeAI, 2026](https://www.reddit.com/r/ClaudeAI/comments/1rwj6g3/users_whove_seriously_used_both_gpt54_and_claude/)

> "GPT-5.5 vs GPT-5.4 vs Opus 4.7 on 56 real coding tasks: GPT-5.5's biggest lead is correctness: 3.16 vs 2.60."
> — [r/ClaudeCode, 2026](https://www.reddit.com/r/ClaudeCode/comments/1t0xrad/gpt55_vs_gpt54_vs_opus_47_on_56_real_coding_tasks/)

> "GPT 5.5 is not the 'good' version of GPT 5.4. It does hard things that GPT 5.4 can't."
> — [r/vibecoding, 2026](https://www.reddit.com/r/vibecoding/comments/1tuw8c1/you_keep_burning_through_your_codex_quota_in_an/)

**关于 Gemini 3 Pro / 3.1 Pro：**
> "Gemini 3 Pro = slow motion downgrade? When 3 Pro dropped in December, it felt great. Fast forward a few weeks and it's like a different product."
> — [r/GeminiAI, 2026](https://www.reddit.com/r/GeminiAI/comments/1qpy7n2/gemini_3_pro_slow_motion_downgrade/)

> "Gemini 3.1 Pro is a massive, massive improvement over Gemini 3 Pro, which was a really terrible model (outside of benchmarks)."
> — [r/google_antigravity, 2026](https://www.reddit.com/r/google_antigravity/comments/1r9y34d/gemini_31_pro_day_1_review_versus_opus_46_and/)

**关于 MiniMax M2.7 / M3：**
> "Minimax M2.5 is not worth the hype compared to Kimi 2.5 and GLM 5. Kept hallucinating."
> — [r/opencodeCLI, 2026](https://www.reddit.com/r/opencodeCLI/comments/1r5vv6g/minimax_m25_is_not_worth_the_hype_compared_to/)

> "MiniMax (0100.HK) plunges 15% after M3 launch amid HK$ 1.8B loss. They cut promotional limits, squeeze API tiers, silently throttle developers."
> — [r/MiniMax_AI, 2026](https://www.reddit.com/r/MiniMax_AI/comments/1tu9k30/the_real_reason_behind_api_throttling_minimax/)

> "M3 the past two days has turned absolutely stupid."
> — [r/hermesagent, 2026](https://www.reddit.com/r/hermesagent/comments/1twzbc6/why_are_people_not_using_mimo_v25/)

**关于 Kimi K2.6：**
> "K2.6 — first model I'd confidently recommend as Opus 4.7 replacement… about 85% of tasks Opus can do."
> — [r/kimi, 2026](https://www.reddit.com/r/kimi/comments/1sojem0/kimi_k26_worth_it/)

> "Kimi 2.6 Review: Powerful but Needs Double-Checking. First draft ~70% accuracy, after feedback ~95%. Overthinking/looping."
> — [r/kimi, 2026](https://www.reddit.com/r/kimi/comments/1st69cp/kimi_26_review_powerful_but_needs_doublechecking/)

> "Kimi K2.6 is still not good at analysis."
> — [r/LocalLLaMA, 2026](https://www.reddit.com/r/LocalLLaMA/comments/1sqzuqd/kimi_k26_is_still_not_good_at_analysis_but_at/)

**关于 GLM-5.1 / 5.2：**
> "GLM-5.1 topped SWE-Bench Pro (58.4%) and hit #3 on Code Arena — above GPT-5.4 (57.7%) and Opus (57.3%)."
> — [r/LLM, 2026](https://www.reddit.com/r/LLM/comments/1sm5hty/glm51_topped_swebench_pro_and_hit_3_on_code_arena/)

> "Everyone is switching to GLM-5.1 after the Anthropic ban. Doesn't lose thread after 20-30 messages."
> — [r/openclaw, 2026](https://www.reddit.com/r/openclaw/comments/1sl5avl/everyone_is_switching_to_glm51_after_the/)

> "GLM 5.1 is what I mostly use now."
> — [r/opencodeCLI, 2026](https://www.reddit.com/r/opencodeCLI/comments/1stg1is/best_ai_coding_stack_in_2026_for_heavy_users_cost/)

**关于 Grok 4：**
> "Grok 4.20 is a meh model in terms of intelligence but very good for speed and cost."
> — [r/singularity, 2026](https://www.reddit.com/r/singularity/comments/1rqrr3k/xai_releases_grok_420_beta_models_via_api/)

> "Grok 4.1 and 4 retirement from API on May 15, 2026."
> — [r/grok, 2026](https://www.reddit.com/r/grok/comments/1t64nu1/grok_model_41_and_4_retirement_from_api_on_may_15/)

**关于 Llama 4 Scout：**
> "Unpopular Opinion: I'm Actually Loving Llama-4-Scout… The 10M context window is purely a marketing gimmick."
> — [r/LocalLLaMA, 2026](https://www.reddit.com/r/LocalLLaMA/comments/1k65cmy/unpopular_opinion_im_actually_loving_llama4scout/)

> "Llama 4 Scout with 10M tokens — It's great (no fall-off) until the 200k token mark."
> — [r/singularity, 2026](https://www.reddit.com/r/singularity/comments/1jsc7jt/llama_4_scout_with_10m_tokens/)

### 🔥 SWE-bench 污染问题

社区共识：SWE-bench Verified 已被系统性污染，多个独立来源确认。

> "Microsoft 宣布 SWE-Bench Verified 因数据污染基本无用。"
> — [r/BetterOffline, 2026](https://www.reddit.com/r/BetterOffline/comments/1rabj93/ai_bros_claiming_singularity_again_thanks_to_metr/)

> "The same model that scored ~30% on SWE-Bench Verified dropped to 0-2%. That's when I stopped treating this as a theory."
> — Reddit 用户 u/OK_Simon_666

> "How is Gemini 3.1 at the top of SWE-bench? — That whole leaderboard is contaminated garbage with baby tasks and leaky tests."
> — [r/singularity, 2026](https://www.reddit.com/r/singularity/comments/1s2b8ue/how_is_gemini_31_at_the_top_of_swebench/)

> "SWE-Rebench is pretty much contamination free."
> — [r/LocalLLaMA, 2026](https://www.reddit.com/r/LocalLLaMA/comments/1pozr6f/claude_code_gpt52_deepseek_v32_and_selfhosted/)

> "Claude Mythos memorized exactly 52 invalid tasks… better memorizes tasks from SWE-Bench Pro than Verified/Multilingual."
> — [r/BetterOffline, 2026](https://www.reddit.com/r/BetterOffline/comments/1sgxc77/thoughts_about_strange_moments_in_claude_mythos)

替代方案：**SWE-Rebench**（去污染版本）和 **DeepSWE**（91 道无污染新题）是目前社区认可的替代基准。

### 一句话总结

1. **SWE-bench 跑分已不可信**——看 SWE-Rebench 或 DeepSWE
2. **Claude Mythos 5 SWE-bench 95.5%**——但已受限，仅~100家机构可访问
3. **Claude Fable 5 被美国政府封禁**——6月12日下线，仅存活72小时
4. **GPT-5.6 Sol 新王登基**——Terminal-Bench 2.1 91.9%，但预览中，政府限制访问
5. **GPT-5.6 Terra $2.50/$15**——GPT-5.5级能力半价，性价比之选
6. **Claude Opus 4.8 质量波动**——社区持续抱怨退化、烧token，可考虑替代方案
7. **GLM-5.2 国产开源 SOTA**——MIT 开源，SWE-Pro 62.1%，GPQA 91.2%
8. **DeepSeek V4 Flash 仍是性价比之王**——$0.14/$0.28，社区压倒性正面
9. **Kimi K2.7 Code 新发布**——MCP 工具调用强，开源代码场景新选择
10. **MiMo-V2 Flash 已退役**——6月30日完全退役，请迁移到 V2.5
11. **MiniMax M3 跑分与实际脱节**——财务危机 + API 限速，不建议投入

---

## 六、一个经过验证的 MoE 策略

这是目前开发者社区里最主流的打法，也是本站在实际使用的方案：

```
70% 调用 → DeepSeek V4 Flash（日常：问答、中文、轻量编码）
12% 调用 → DeepSeek V4 Pro / GLM-5.2 Max（攻坚：代码、推理、国产场景）
 8% 调用 → Claude Opus 4.8 / GPT-5.6 Terra（硬骨头：多文件重构、架构决策）
 5% 调用 → Gemini 3.5 Flash / 3.1 Pro（多模态、数学、长文档）
 5% 调用 → Kimi K2.7 Code / MiMo-V2.5-Pro / Perplexity Sonar（实验、Agent、调研、MCP工具调用）
```

**为什么这么配？**
- Flash 承担 70% 的流量，年成本控制在 $20-50
- V4 Pro / GLM-5.2 Max 替代部分原 Opus 的攻坚场景——便宜 7-14 倍
- GPT-5.6 Terra 以半价提供 GPT-5.5 级能力，适合中型攻坚任务
- Kimi K2.7 Code 在 MCP 工具调用场景值得更多测试
- Opus 4.8 只留给真正的硬骨头——但因质量波动，可用 Terra 替代部分场景
- MiMo-V2 Flash 已完全退役，迁移到 V2.5 或 V2.5 Flash

**成本对比**：如果全用 Opus 4.8，同样流量年花费约 $5,000-10,000。上述组合将成本压到 1/100 以下，质量损失不到 5%。

---

## 七、训练部署本地模型

如果你有消费级 GPU（12GB+ VRAM），训一个自己的小模型是 2026 年最划算的投入。以下是本站实际跑通的完整链路。

### 7.1 硬件基线

| 硬件 | 参数 |
|------|------|
| GPU | RTX 5070 Ti 12GB（Blackwell sm_120） |
| 可行方案 | QLoRA 4bit，7-8B 基座模型 |
| 训练速度 | ~55s/step，100 步约 2h |
| 推理显存 | 4bit 量化后 ~5.7GB/12GB |
| 操作系统 | Docker 容器内（WSL2 + Docker Desktop） |

### 7.2 训练流程

```
选择基座模型（推荐 Qwen3-8B）
  → 准备训练数据（纯原文，不仿写）
  → QLoRA 4bit 微调（rank=16, alpha=32）
  → 监控 loss 曲线，提前停止防过拟合
  → 交叉对比各 checkpoint 的输出质量
  → 选择最佳 checkpoint
```

**关键参数：**
- 量化：nf4 + double_quant
- LoRA rank=16, alpha=32，训练参数 43.6M / 8.2B = 0.53%
- Batch=2，grad_accum=4（有效 batch=8）
- LR=2e-4，cosine 调度
- PyTorch 2.10+ 需手动绕过 `prepare_model_for_kbit_training`（`use_reentrant` bug）

**训练数据铁律：** 只用原文做 Continued Pre-Training，不用 LLM 生成的平行语料。风格迁移靠学习原文特征，不是靠"仿冒"。

### 7.3 部署路径

训练后的 LoRA 适配器（`adapter_model.safetensors` ~175MB）不是完整模型——需要基座配合。三条路线：

| 方案 | 做法 | 优点 | 缺点 |
|------|------|------|------|
| ✅ 合并→转 GGUF | 合并 LoRA 到基座，转 GGUF，llama.cpp 部署 | 一次合并永久可用，加载快 | 需 ~30GB 磁盘，合并 3-5 分钟 |
| vLLM 动态加载 | vLLM serve + `--enable-lora` | 不合并，可热切换 | 需 Docker GPU，镜像 ~4GB |
| LM Studio | GUI 加载基座 + adapter | 零代码 | Adapter 兼容性偶有问题 |

**推荐方案：** 合并后量化到 Q4，llama.cpp server 部署。后续开机自启。

### 7.4 断网兜底

本地训练好的模型不仅是练手——它可以作为云端 API 的自动 Fallback。

方案：**Watchdog 按需启动**（本站实际使用的模式）

```
cron（每 3 分钟）→ 检测主 API 是否可达
  ├─ 可达 → 什么都不做（0 token 消耗）
  └─ 不可达 → 自动拉起本地推理服务器
              → Hermes 自动切到本地 provider
              → 网络恢复后切回云端
```

优势：模型不常驻（省显存）、断网后最多 3 分钟自动拉起、0 token 额外开销。

### 7.5 成本与收益

| 项目 | 数据 |
|------|------|
| 训练一次 | ~2h，电费 ~0.5 元 |
| 模型尺寸 | 8B Q4 ≈ 5GB 显存 |
| 推理速度 | ~30-50 t/s（llama.cpp） |
| 日常使用 | 够 80% 场景，攻坚还是得上 Opus |

一句话：**训练本地模型的性价比极高**——不是因为它能取代 Opus，而是因为它把"免费试错"的门槛降到了零。随便调 prompt、随便改数据、随便跑实验，不用心疼 API 费用。

---

## 八、OpenRouter 完整模型生态速查

OpenRouter 汇聚了 400+ 模型，来自 60+ 提供商。以下按生态分类列出所有可通过 OpenRouter 调用的主要模型家族，并标注定价区间与核心定位，方便你按场景快速检索。

### Anthropic 生态
| 模型 | 输入/输出 $/M | 上下文 | 定位 |
|------|:------------:|:-----:|------|
| ~~Claude Fable 5~~ 🔒 | $10 / $50 | 1M | ❌ 已下线（美国政府封禁） |
| ~~Claude Mythos 5~~ 🔒 | $10 / $50 | 1M | ❌ 受限（6.26部分恢复） |
| Claude Opus 4.8 | $5 / $25 | 1M | 综合最强（当前可用） |
| Claude Opus 4.7 | $5 / $25 | 1M | ⚠️ 社区差评，不推荐 |
| Claude Sonnet 4.6 | $3 / $15 | 200K | 日常编码 |
| Claude Haiku 4.5 | $1 / $5 | 200K | 轻量任务 |

### OpenAI 生态
| 模型 | 输入/输出 $/M | 上下文 | 定位 |
|------|:------------:|:-----:|------|
| GPT-5.6 Sol 🔥 | $5 / $30 | 1M | 🆕 旗舰预览，Terminal-Bench 91.9% |
| GPT-5.6 Terra 🔥 | $2.50 / $15 | 1M | 🆕 中型工作负载，半价替代5.5 |
| GPT-5.6 Luna 🔥 | $1 / $6 | 1M | 🆕 轻量高性价比 |
| GPT-5.5 | $5 / $30 | 1M | 旗舰全能 |
| GPT-5.4 | $1.25 / $10 | 400K | 编程+Codex 工具链 |
| GPT-5.4 Mini | $0.75 / $4.50 | 400K | 中型性价比 |
| GPT-5.4 Nano | $0.20 / $1.25 | 400K | 轻量快速 |
| GPT-4.1 | $2 / $8 | 1M | 上一代旗舰 |
| GPT-4.1 Nano | $0.10 / $0.40 | 1M | 极低成本 |
| o3 / o4-mini | $2/$8 / $1.1/$4.4 | 200K | 推理专用 |

### Google Gemini 生态
| 模型 | 输入/输出 $/M | 上下文 | 定位 |
|------|:------------:|:-----:|------|
| Gemini 3.1 Pro Preview | $2 / $12 | 2M | 数学/推理最强 |
| Gemini 3.5 Flash | $1.50 / $9 | 1M | 高速性价比，编码超3.1 Pro |
| Gemini 3 Flash Preview | $0.50 / $3 | 1M | 轻量推理 |
| Gemma 4 26B (free) | 免费 | — | 开源轻量 |

### DeepSeek 生态
| 模型 | 输入/输出 $/M | 上下文 | 定位 |
|------|:------------:|:-----:|------|
| DeepSeek V4 Pro Max | $1.74 / $3.48 | 1M | 开源天花板 |
| **DeepSeek V4 Flash** | **$0.14 / $0.28** | **1M** | ⭐ 最佳性价比 |
| DeepSeek R1 | $0.55 / $2.19 | 128K | 推理链模型 |

### Meta Llama 生态
| 模型 | 输入/输出 $/M | 上下文 | 定位 |
|------|:------------:|:-----:|------|
| Llama 4 Maverick | ~$0.20 / $0.60 | 1M | 最新旗舰开源 |
| Llama 4 Scout | $0.15 / $0.50 | 10M | 超长上下文展示品 |
| Llama 3.3 70B | $0.10 / $0.32 | 131K | 经典开源，便宜够用 |

### Mistral 生态
| 模型 | 输入/输出 $/M | 上下文 | 定位 |
|------|:------------:|:-----:|------|
| Mistral Large 2512 | $0.50 / $1.50 | 262K | 旗舰模型 |
| Mistral Medium 3.5 | $1.50 / $7.50 | 262K | 128B 密集，Agent 优秀 |
| Mistral Small 4 | $0.15 / $0.60 | 262K | 119B MoE 三合一 |
| Devstral 2 | $0.40 / $2.00 | 262K | 编码 Agent 专用 |
| Ministral 3 8B | $0.10 / $0.30 | 262K | 预算首选 |
| Codestral | $1 / $3 | 32K | 代码补全专用 |
| Voxtral TTS | $22/M char | — | 语音合成 |

### xAI Grok 生态
| 模型 | 输入/输出 $/M | 上下文 | 定位 |
|------|:------------:|:-----:|------|
| Grok 4.3 | $1.25 / $2.50 | 1M | 旗舰推理+Agent |
| Grok 4.20 | $2 / $6 | 2M | 超长上下文 |
| Grok 4.1 Fast | $0.75 / $1.50 | 128K | 快速版 |
| Grok 4 (退役) | — | — | 已由 4.3 取代 |

### 阿里 Qwen 生态
| 模型 | 输入/输出 $/M | 上下文 | 定位 |
|------|:------------:|:-----:|------|
| Qwen3.7 Max | $0.90 / $2.70 | 1M | 中文旗舰，AA Index 56.6 |
| Qwen3.7 Plus | $0.40 / $1.60 | 1M | 多模态版 |
| Qwen3 235B A22B | $0.72 / $2.16 | 262K | MoE 开源 |
| Qwen3 VL 235B | — | — | 视觉版本 |

### Perplexity Sonar 生态
| 模型 | 定价基准 | 定位 |
|------|---------|------|
| Sonar Pro Search | $3/$15/M + $18/1K请求 | 自主多步研究 |
| Sonar Deep Research | $2/$8/M + $5/1K搜索 + $3/M推理 | 深度调研 |
| Sonar Pro | $3/$15/M | 搜索增强 |
| Sonar Reasoning Pro | $2/$8/M | 链式推理 |
| Sonar (轻量) | $1/$1/M | 快速搜索 |

### NVIDIA Nemotron 生态
| 模型 | 输入/输出 $/M | 上下文 | 定位 |
|------|:------------:|:-----:|------|
| Nemotron 3 Ultra | $0.50 / $2.50 | 1M | 前沿推理 (550B MoE) |
| Nemotron 3 Ultra (free) | 免费 | 1M | 免费前沿模型 |
| Nemotron 3 Super (free) | 免费 | 128K | 免费 Agent 编排 (120B MoE) |
| Nemotron 3 Nano 30B (free) | 免费 | 256K | 免费轻量推理 |

### 小米 MiMo 生态
| 模型 | 输入/输出 $/M | 上下文 | 定位 |
|------|:------------:|:-----:|------|
| **MiMo-V2.5-Pro** | **$0.18 / $0.54** | 1M | 🏆 MIT开源，Agent新贵 |
| **MiMo-V2.5 Flash** | **$0.10 / $0.30** | 1M | 轻量开源 Agent |
| MiMo-V2 Flash | $0.06 / $0.18 | 1M | ❌ 已退役（2026-06-30） |
| MiMo Code | — | — | 🆕 代码专用，SWE-Pro ~62% |

### 国产模型生态（其他）
| 模型 | 输入/输出 $/M | 上下文 | 定位 |
|------|:------------:|:-----:|------|
| GLM-5.2 Max | $0.90 / $2.70 | 1M | 🏆 MIT开源，SWE-Pro 62.1%，GPQA 91.2% |
| Step 3.7 Flash | $0.20 / $1.15 | 256K | 阶跃星辰 MoE，Apache 2.0 |
| Kimi K2.6 | $0.70 / $2.10 | 128K | 长文本旗舰 |
| Kimi K2.7 Code 🆕 | $0.95 / $4.00 | 256K | MCP Mark 81.1%，MCP Atlas 76.0 |
| MiniMax M3 | $0.22 / $0.66 | 1M | ⚠️ 不推荐 |
| Yi-Lightning | $0.50 / $1.50 | — | 01.AI 旗舰 |
| Hunyuan Large | — | — | 腾讯混元 |
| Nex-N2-Pro (free) | 免费 | 262K | 397B MoE 国产 Agent |

### 其他值得关注的模型
| 模型 | 输入/输出 $/M | 定位 |
|------|:------------:|------|
| Cohere Command-A | $2 / $8 | 企业级检索增强 |
| AI21 Jamba 1.5 | $0.50 / $0.70 | SSM-Transformer 混合 |
| Reka Core | — | 多模态 |
| Microsoft Phi-4 | — | 小模型高效 |
| ByteDance Seed | — | 字节跳动系列 |
| Sourceful Riverflow 2.5 Pro | $0/$0 | 免费神秘模型 |

> 数据来源：OpenRouter 官方模型目录 & pricing API（2026-06），直接获取。上面 80+ 个模型均可在 OpenRouter 上通过统一 API 调用。定价为 OpenRouter 直通价，与官方一致。

---

## 九、结论

| 你的身份 | 最佳选择 |
|---------|---------|
| 个人开发者，自用 | DeepSeek V4 Flash 主力 + Opus/GPT-5.6 Terra 攻坚 |
| 创业团队，降本 | DeepSeek V4 Flash/Pro（全栈开源）+ GLM-5.2 Max |
| 企业，质量优先 | Claude Opus 4.8 + GPT-5.6 Sol（预览中）|
| 科研/学术调研 | Perplexity Sonar Deep Research / Gemini 3.1 Pro |
| 中文内容创作 | DeepSeek V4 / Qwen3.7 Max |
| 欧洲/数据合规 | Mistral Small 4 / Mistral Medium 3.5 |
| 私有化部署 | DeepSeek V4 Pro / GLM-5.2 Max / MiMo-V2.5-Pro（均MIT开源）|
| 超长文档/代码库 | Grok 4.20（2M ctx）/ GLM-5.2 Max（1M ctx）/ Gemini 3.1 Pro（2M ctx）|
| MCP/Agent 工具调用 | Kimi K2.7 Code / MiMo-V2.5-Pro |

**避坑：** MiniMax 系列暂时别碰。跑分和实际体验的差距太大。

**🚨 2026.6.29 特别提示：**
- Claude Fable 5 已被美国政府封禁，别再买
- GPT-5.6 Sol/Terra/Luna 预览中，预计7月中旬广泛发布
- MiMo-V2 Flash 已退役，请迁移到 V2.5
- Opus 4.8 质量波动加大，建议搭配 GPT-5.6 Terra 备用

**守则：** 先用自己的数据测，别信跑分。一个月后觉得"这模型真好用"才是真的好用。

---

> 数据来源：OpenRouter 官方模型目录 (2026-06)、Artificial Analysis Intelligence Index v4.1 (2026-06-27)、buildfastwithai.com (2026-06-15)、llm-stats.com (2026-06)、CostGoat (2026-06-27)、Vellum LLM Leaderboard (2026-06)、LM Council、Reddit r/DeepSeek / r/LocalLLaMA / r/singularity / r/ClaudeAI / r/claude  \
> 最后更新：2026 年 6 月 29 日

## 附录 A：OpenRouter 神秘模型

> 以下模型出现在 OpenRouter 上但来源不明。每日自动检测更新。

| 模型 ID | 解密名称 | 上下文 | 输入/输出价格 |
|---------|---------|:-----:|:------------:|
| `riverflow-v2.5-pro` | Sourceful Riverflow 2.5 Pro | 33K | $0/$0 |
| `owl-alpha` | OpenRouter 自研测试模型 | ? | $0/$0 |
| `nemotron-3-super-120b-a12b` | NVIDIA Nemotron 3 Super | 128K | $0/$0 |
| `seedream-4.5` | 字节跳动 Seedream 4.5 | ? | $?/$? |

## 附录 B：已下线模型

| 模型 | 下线日期 |
|------|---------|
| ~~Claude Fable 5~~ 🔒 | 2026-06-12（美国政府封禁） |
| ~~Claude Mythos 5~~ 🔒 | 2026-06-12（受限，6.26部分恢复） |
| Grok 4.1 / Grok 4 | 2026-05-15 |
| Claude 3 Opus | 2026-04 |
| Claude 4 Opus / 4 Sonnet | 2026-05 |
| GPT-4.5 | 2026-04 |
| GPT-5 | 2026-03 |
| Gemini 1.5 Pro | 2026-02 |
| DeepSeek V3 / R1 | 2026-04 |
| MiMo-V2 Flash | 2026-06-30 |

> 下线日期为 API 停止服务或不再推荐使用的保守估计时间。每日脚本自动检测新下线模型。

### 🪦 已下线模型

- **GLM-5.1 / 5.2 Max** — 下线日期: 2026-06-30
- **Kimi K2.6 / K2.7** — 下线日期: 2026-06-30


### 🪦 已下线模型

- **GLM-5.1 / 5.2 Max** — 下线日期: 2026-07-01
- **Kimi K2.6 / K2.7** — 下线日期: 2026-07-01


### 🪦 已下线模型

- **GLM-5.1 / 5.2 Max** — 下线日期: 2026-07-02
- **Kimi K2.6 / K2.7** — 下线日期: 2026-07-02


### 🪦 已下线模型

- **GLM-5.1 / 5.2 Max** — 下线日期: 2026-07-03
- **Kimi K2.6 / K2.7** — 下线日期: 2026-07-03

