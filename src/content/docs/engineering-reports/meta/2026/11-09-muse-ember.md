---
title: Muse Ember — 用旗舰蒸馏出一个"每任务一角四分"的执行层
date: 2026-11-09
source: "https://research.meta.ai/blog/muse-ember"
---

# Muse Ember：Meta 最小的模型，做的是最贵的那部分活

**发布日期：** 2026-11-09
**来源：** https://research.meta.ai/blog/muse-ember
**工程范式：** 把旗舰（Muse Wonder Full）当作教师与数据源，蒸馏出一个只负责"agent 重复动作"的小模型；优化目标不是分数而是每任务成本，用 1M 上下文 + 512K 输出去吃掉原本需要切块的流水线。

## 设计哲学

Meta 对 Ember 的任务定义非常窄：tool calls、coding subtasks、routing、extraction、long document parsing——"agents repeat all day"的那些步骤。这句话背后是一个明确的成本判断：agent 的 token 大头不在规划，而在大量小而结构化的步骤上。把规划交给 Wonder，把体量交给 Ember。

官方给出的推理链条是"personal superintelligence 需要 frontier capability at a price that scales"，而 scaling 的具体形态是**分层**：Wonder 处理最难的问题、Spark 处理编码与 agentic 工作流、Ember 处理可重复的大批量任务。Ember 是第一个用 Muse Wonder Full 训出来的模型——即"旗舰不止是产品，还是数据与教师"。

放弃的部分：它明确不是最强模型（Intelligence Index 36，低于自家 Spark 1.3 的 37，也低于 Fable 5.2 一类的 60+ 档位）；上下文虽 1M，但**超过 200K 的 prompt 会跳到另一档价格**（输入 $0.30、输出 $1.50 每百万 token），也就是说长上下文能力不等于长上下文便宜。多模态只做理解侧，不生成。

## 关键架构决策

**原文未披露架构细节**——没有公开层数、注意力选型、MoE 专家配置、训练数据规模或蒸馏的具体损失函数。可核实的是训练路径与工程约束：

- **训练路径**：Muse Ember 是第一个用 Muse Wonder Full 训练的模型（Muse Wonder Full 于 10 月发布）。官方表述为"we said we would use them to develop specialized models"，即从旗舰派生专用小模型，而非独立从零训练。具体的蒸馏/采样比例、教师信号形式未公开。
- **注意力**：未披露。
- **MoE**：未披露。
- **上下文工程**：1,048,576 token 输入、最高 524,288 token 输出。这两个数字是产品设计而非架构声明——512K 输出意味着"整份文档一次性抽取回来"，不必分段拼接。
- **模态**：原生理解 text / image / audio / video，一个 1M 窗口共用；不接单独的语音或 OCR 模型，直接省掉流水线里的预处理环节。
- **推理分层**：reasoning effort 可从 minimal 调到 max，按任务设定——把"要不要多想"变成调用侧参数，而不是换模型。
- **服务面**：Meta Model API、Muse Code，支持 Responses API；同期上 Google Cloud 与 Oracle Cloud 托管端点。
- **安全**：按 Meta Superintelligence Scaling Framework 评估化学/生物、网络安全、失控三类风险，结论是各类别均低于该框架的高风险阈值；并额外评估了"代表用户行动"的行为（尊重用户意图、处理敏感信息、抵抗网页/文档/工具输出中的隐藏指令、高影响动作前请求人类确认）。因为是小模型，官方强调**核心安全训练与测试与旗舰同规格**。

## 关键结果

全部为官方公布数据（Artificial Analysis Intelligence Index v5，2026-11-09 版；均为 max reasoning effort）：

| 基准 | Muse Ember (max) | Claude Haiku 5.5 (max) | GPT-6 Luna (max) |
| --- | --- | --- | --- |
| AutomationBench-AA（端到端业务流程） | **37.8** | 13.9 | 20.2 |
| Agents' Last Exam | **61.6** | 57.0 | 57.1 |
| Personal Superintelligence Index（Meta 内部八项合成） | **46.8** | 36.1 | 37.0 |
| Terminal-Bench 4.0 | **40.9** | 39.2 | 16.4 |
| Coding Agent Index-AA | **46** | 37 | 31 |
| FrontierCode 2.0-AA | 27.2 | **34.9** | 25.2 |
| GDP.pdf-AA | **22.8** | 20.8 | **22.8** |
| OSWorld 2.1（partial / binary） | **69.5 / 33.8** | 68.9 / 27.8 | 50.5 / 17.0 |
| PerceptionBench（w/ tools） | **80.6** | 78.6 | 62.8 |
| AA Intelligence Index | 36 | 36 | 28 |

**成本侧**（这是发布的核心论点，同样是官方口径）：

- 定价：$0.10 / 1M 输入、$0.004 / 1M 缓存输入、$0.50 / 1M 输出（≤200K prompt）；>200K prompt 为 $0.30 / $0.012 / $1.50
- 每任务成本（AA，max）：Ember **$0.136 @ 35.8 分**；对照 Spark 1.3 为 **$2.39 @ 37 分**——分数差 1.2 分，成本差约 17 倍
- 与 Haiku 5.5 的比较：Ember 在约 $0.136 处拿到 35.8，Haiku 需要约 $0.411 才到 36.2（"matches Haiku's best score at about a third of the cost"）
- 官方称其位于 AA 全榜的效率前沿："no model scores higher for less per task"

**唯一明显落后的项**是 FrontierCode 2.0-AA（27.2 vs Haiku 34.9）——按"可合并性"评判的真实工程任务，说明"低成本的步骤执行"与"能做完整工程判断"仍是两件事。

## 范式对比

- **vs Claude Haiku 5.5（Anthropic）**：同一价位段的直接对手。Ember 在 agent 类（AutomationBench 37.8 vs 13.9）与计算机操作上大幅领先，在真实工程任务上落后。两家对"小模型该擅长什么"的判断不同：Anthropic 把 Haiku 做成便宜的通用模型，Meta 把它做成专职的 agent 执行器。
- **vs 自家 Muse Spark 1.3 / Muse Wonder**：这是同门内的分层实验，而不是替代。37 分涨到 36 分的代价从 $2.39 掉到 $0.14——Meta 用这条曲线论证"旗舰应该是升级档，不该是默认档"。
- **vs 中国开源侧的同类（Qwen3.8-Flash / GLM-5.3-Flash / MiMo-V2.6-Flash）**：那些是开放权重 + 相近激活量，Meta 这条路是闭源蒸馏；差别在于可部署性与可审计性——Ember 只能走 API 或云托管。
- **vs 蒸馏文献的常规做法**：多数蒸馏追求"小模型逼近教师能力"；Ember 追求"小模型占据成本前沿"，接受在硬任务上明显掉队。这是目标函数的替换，不是同一目标下的效率优化。

## 社区评价

发布当天的主要讨论集中在三处：

1. **成本曲线的斜率**：$0.14/任务对 $2.39/任务被普遍当作"分层架构终于算得过来"的证据；Aragon Research 的分析直接把结论写成"frontier 模型应成为升级档，而不是默认档，合理架构是路由器"。
2. **首发伙伴的实测**：Cloudflare 称测试中尾延迟（tail）比对照模型快约 30%；You.com 报 p95 2.2 秒、比领先开源权重模型快 4–13 倍、输出 token 少 36–48%；Cline 强调它适合当 harness 里的 **subagent**。这些是合作方自述，非独立复现。
3. **验证完备性**：OSWorld 2.1 用 partial-credit（69.5）与 binary（33.8）两个口径，PSI 是 Meta 内部八项合成指数——榜单里混着第三方（AA）与内部评测，社区对"内部 composite" 的可比性持保留态度。

## 可复用的工程经验

1. **用旗舰做教师，做"专用执行层"而不是"缩小版旗舰"**。目标函数写成"每任务成本最低且够用"，就能接受在硬任务上掉队——这比追求逼近教师更符合实际部署。
2. **先量 token 分布，再决定模型分层**。如果 agent 的 token 大头在 tool call / 抽取，那优化那部分的小模型的投资回报远高于换更强的规划模型。
3. **长上下文要配成本悬崖**。1M 上下文搭配 >200K 的加价档，是让"能力"和"账单"解耦的标准做法；免费 1M 上下文的产品设计通常不可持续。
4. **把"能不能多想"做成参数**，而不是多挂一个模型。effort 档位让同一 checkpoint 覆盖从路由到复杂抽取的整段需求。
5. **安全评估要覆盖"代用户行动"的行为面**：是否尊重意图、是否处理敏感信息、是否抵抗藏在网页/文档/工具输出里的指令、高影响动作前是否找人确认。小模型不能因为小就省掉这套测试。
6. **报 partial-credit 与 binary 两个口径**。计算机操作类基准的分数对评分口径极度敏感，只报高的那个等于自欺。
