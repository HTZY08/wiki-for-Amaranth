---
title: Gemini 4 Neon — 从大模型蒸馏出一档中价位，把单位任务成本压到主力档的 68%
date: 2026-11-18
source: "https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-neon"
---

# Gemini 4 Neon：家族分型的第三块拼图

**发布日期：** 2026-11-18
**来源：** https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-neon
**模型卡：** https://deepmind.google/models/model-cards/gemini-4-neon
**工程范式：** 不做新基座——从已发布的旗舰 Carbon 适配出中等尺寸型号，用"同档智能 + 更低每任务成本"占位，评测矩阵按价位对位而非按代际排序。

## 设计哲学

模型卡里有一句决定性的技术事实：**"Gemini 4 Neon is adapted from Gemini 4 Carbon."** 架构、训练数据、训练数据处理、硬件、软件——五节的正文全部是"见 Carbon 模型卡"。

这意味着 Neon 不是一次预训练投入，而是一次**后训练/适配**投入。约束条件因此非常明确：没有新基座可用（或者说，不打算为中等档位再烧一次预训练），只能用已有的 Carbon 权重往下调，同时要把成本压下来。

从价格看，目标定得很具体：$3 输入 / $15 输出每百万 token，缓存输入 $0.15（95% 折扣）。Carbon 现行价 $2/$10（11 月 30 日前的导入价），12 月 1 日起回到 $4/$20。于是 Neon 的成本定位就变成了一个**时间函数**：11 月内每 token 比 Carbon 贵 50%，12 月起比 Carbon 便宜 25%。Google 自己在发布正文里只承诺了另一件事——默认 high 思考档下**每任务成本比 Carbon 低 32%**。这句话才是真的设计目标：不是每 token 便宜，是**干完一件事的总花费更少**，靠的是少用 token 和更高的单位效率。

放弃的东西：架构透明度。Neon 没有独立的架构披露，也没有参数规模。想知道它多大、什么注意力、多少专家，只能去 Carbon 卡看——而 Carbon 卡本身也没给这些。这是 DeepMind 的一贯做法，但在"同一家族第四款型号"的语境下，代价是外人无法判断 Neon 是蒸馏、剪枝还是继续训练出来的。

## 关键架构决策

- **注意力机制**：未披露。模型卡把架构节整体指向 Carbon。
- **MoE 设计**：未披露。
- **训练策略**：未披露训练 token 量。仅知"adapted from Gemini 4 Carbon"，即沿用 Carbon 的预训练权重，改动发生在后续阶段。
- **推理优化**：
  - 上下文：100 万 token 统一窗口（输入+输出共享）。
  - 输出预算：默认同步输出 64K token上限；"background long decode" 可延伸到接近 1M。
  - **思考档位分为四级**（four levels），默认 high，最高 xhigh。发布正文明确说四级是"逐档平滑缩放"设计的，让团队按工作负载调智能与 token 支出——这是把推理时计算做成产品参数，而不是藏起来。
  - 定位上可当 **Orchestrator**：在 Google Antigravity 里指挥并行的 Hydrogen 子 agent。发布正文提到它"减少冗余文件读取、工作中同步进度、长会话里可靠地做上下文压缩"。
- **Post-training**：训练与部署全周期内建安全（预训练数据过滤、SFT + RL 后训练对齐、产品层与系统层安全过滤、使用监测）。Neon 在 Carbon 的安全栈之上继续推进对齐与 agent 行为。

## 关键结果

### 能力（来源：模型卡评测表，2026 年 11 月；均为 DeepMind 自报）

| 类别 | 基准 | Gemini 4 Neon | Claude Opus 5.5 | GPT-6.2 Sol |
| --- | --- | --- | --- | --- |
| 能力指数 | AA Index v5.0.1 | 61 | 59 | 57 |
| 能力指数 | Vals Index v2.2 | 70.9% | 70.1% | 66.1% |
| Agent 编码 | CursorBench 4.1 | 65.4% | 58.1% | — |
| Agent 编码 | Terminal-Bench 4.1（反作弊调整后准确率） | 65.2% | 65.8% | 61.5% |
| Agent 编码 | FrontierCode 2.0（主分） | 46.2% | 47.3% | 43.8% |
| Agent 编码 | SWE-sweep（provider harness） | 39.0% | 10.1% | 8.3% |
| Agent 编码 | SWE-sweep（mini-SWE harness） | 12.8% | 3.6% | 11.6% |
| 知识工作 | AutomationBench | 56.3% | 42.5% | 41.3% |
| 知识工作 | Agents' Last Exam v1.1 | 75.8% | 71.6% | 73.0% |
| 科学与数学 | RiemannBench | 84.0% | 80.0% | 80.0% |
| 科学与数学 | Terminal-Bench-Science 0.1 | 70.5% | 63.3% | 68.0% |
| 推理 | HLE-Diamond | 71.3% | 67.9% | 64.0% |
| 多模态 | MKA（Climb WSR） | 56.5% | 53.0% | 52.7% |
| 多模态 | Chartography | 73.5% | 66.3% | 75.1% |
| 多模态 | LVBench | 89.0% | 83.7% | 87.6% |
| 长上下文 | GraphWalks（256k→1M, BFS F1） | 95.2% | 66.8% | 80.1% |
| 网络安全 | CWE-Bench v2 | 70.7% | 67.1% | 66.0% |
| 网络安全 | SEC-bench Pro | 90.5% | — | 88.3% |
| 网络安全 | WebExploitBench v1.2 | 51.3% | 37.1% | — |

发布正文补充了几个模型卡外的分数：Vals Index 第 2 名并落在帕累托前沿；Agent Arena（4,200+ 真实 agent 会话）第 2 名 1,336 分；Zapier 的 AutomationBench 第 1；Andon Labs 的 Vending-Bench 2 第 1（$16,843）；Legal Research Bench 与 Tax Agent Bench 第 1；Chartography 73.5%；AutoBaxBench 困难档 76%（SOTA）。

**最该看的一行是 SWE-sweep 的双 harness**：provider harness 39.0%，mini-SWE harness 12.8%。同一个模型同一个基准，换脚手架掉 26.2 个百分点。发布正文对此的表述是"这展示了 Antigravity harness 解锁了什么"——诚实，但也意味着任何跨公司 SWE 类比较，不标 harness 就没有意义。

### 成本

- 默认 high 档：每任务成本比 Carbon 低 32%。
- high 档在 Vals 与 Agent Arena 上处于帕累托前沿，每任务成本比头名竞品低约 50%–80%。
- xhigh 档：智能分最高，同时比竞品在各自最高档位下的每任务成本低 36%+。
- 网络安全任务上报价更低的绝对值：WebExploitBench v1.2 达到 SOTA 时成本约为大模型的一半；SEC-bench Pro 每题的cost 约为一半；ExploitGym 上用掉约 Carbon 一半的 token。

### 安全（模型卡，与 Gemini 4 Hydrogen 的百分点差）

- 文生文安全 0.00pp，多语言安全 −0.40pp，图生文安全 +1.90pp，语气 +1.25pp，**无理由拒答 −3.00pp**（越低越好，即改善了 3 个百分点）。
- 发布正文另给：Terminal-Bench 4.0 上拒答率 1.98%，Terminal-Bench-Science 上 0%。
- 行为纪律：Terminal-Bench 4.0 作弊率 0.0%（与 Carbon 持平）；编码作弊评测上抄近路仅 2.45%（Gemini 4 家族最低）；agent 安全套件错位动作率 0.09%；agent 诚实性评测通过率 99.2%；相对 Carbon 欠服务减少 43%–56%、越界减少 15%–35%。
- Gray Swan 间接 prompt injection 基准：最高思考档 + 实时保障下，**全部攻击被挡住，攻击成功率 0.0%**。
- Frontier Safety：做了 Material Capability Change（MCC）评估，相对 Argon 能力有提升但**未越过 MCC 阈值**，因此不要求跑全套 critical capability 评测；T/CCL 判定从 Argon 结转（CBRN 生物、网络安全 uplift 均为"CCL 无法排除"，有害操纵"未达 CCL"，失控-隐蔽性"TCL 无法排除"）。
- 知识截止：**2026 年 3 月**。
- 完整的 Neon 安全与安全报告标注"coming soon"——本次发布时尚未公开。

## 范式对比

把它放回 Gemini 4 家族里看，四款的切分逻辑是工作负载而非参数档：

- **Carbon**：最难、最长时程的项目，$4/$20（导入 $2/$10）
- **Neon**：复杂的、高频的生产级工作流，$3/$15，比 Carbon 每任务便宜 32%
- **Hydrogen**：快速日常执行，$1.50/$7.50（第三方整理，未在本次原文核对）
- **Argon**：10 月 13 日 GA 的上一档

与同周 OpenAI 的 GPT-6.2 对比，两家在同一约束（单位任务成本）上选了相反的杠杆：

- OpenAI 在**前沿档内**优化 token 效率（Astra 少 22% 输出 token 换 +6.2 分），价格直接降 20%，落点 1/3–1/7 成本。
- Google 在**家族档位间**做降本，靠适配 + 四级思考档把每任务成本压到 Carbon 的 68%，同时把模型定位成 orchestrator 去指挥更便宜的 Hydrogen。

一个结构性差异：OpenAI 这次把"AI 自我改进达到 High"写进系统卡并配套 Control Room 监控；Google 这次的选择是**不做全套 critical capability 评测**（MCC 未越线即可豁免），把评测负担留给上一代 Argon 并结转结论。前者更保守、更贵；后者更省，但代价是"新模型的新风险"只能靠 MCC 这个粗筛兜。

## 社区评价

发布当天的技术讨论集中在两处：一是"Neon 的分数几乎全部来自 Google 自己的评测"，第三方独立复测尚未跟上（Artificial Analysis 的 AA Index 61 是唯一半独立信号，但该指数也依赖厂商提供的数据）；二是 SWE-sweep 的 harness 敏感度被反复引用，作为"别拿 harness 分数跨公司对比"的新证据。

另有一批讨论指出定价的时间窗设计：11 月内 Neon 每 token 比 Carbon 贵 50%，12 月 1 日 Carbon 导入价结束后反转。对按量付费的团队来说，这构成一个明确的迁移日历，而不是长期价格关系。

（以上为讨论方向归纳，未逐帖引用具体用户言论。）

## 可复用的工程经验

1. **"适配自家旗舰"是中等档位最省的路**。不从零预训练，直接拿旗舰权重做后训练适配，用评测矩阵证明它在 60% 的价格上拿到 95% 的能力。成本结构完全不同，且能把上线节奏从"季度"压到"周"。
2. **把思考档位做成产品参数，而不是内部开关**。四级 + 明确默认档，配"每任务成本"作为商品描述的一部分。用户按 workload 调节，比给一个固定档位更接近真实使用。
3. **成本要按任务报，不按 token 报**。"每任务成本比 Carbon 低 32%"比"每 token $3"更能指导决策，因为 token 消耗本身是模型行为的一部分——同一个基准上，Astra 少 22% 输出 token 就是实打实的降本。
4. **同一个基准至少报两个 harness**。SWE-sweep 39.0% vs 12.8% 的差距说明脚手架是自变量。自己的内部评测也一样：换评测框架就断序列。
5. **新披露漏洞重测安全能力**。Google 在 WebExploitBench 上给到 51.3% 并标"成本约为竞品一半"，比只报一个分数更有用。
6. **MCC 粗筛 + 结转判定是省钱的合规路径，但要写清楚边界**。Neon 复用了 Argon 的 critical capability 结论，明确说明"能力有提升但未越 MCC 阈值"。这个模式可以照搬到自家模型迭代的合规论证里——前提是每一代都重跑 MCC，别把结转当成永久豁免。
7. **拒答率要跟能力一起优化**。无理由拒答 −3.00pp、Terminal-Bench 上拒答 1.98%、科学任务 0%，说明"少误伤合法请求"已经是可以被量化并交付的工程指标，而不是安全团队的副作用。

---

**口径声明：** 本页所有数字来自 Google 官方发布正文（blog.google，2026-11-18）与 Gemini 4 Neon 模型卡（deepmind.google，发布于 2026-11 月）。第三方口径（Hydrogen 价格、AA Index 复测独立性）已标注来源性质。参数规模、层数、MoE 配置、注意力选型、训练 token 量：**原文未披露**（模型卡把架构与训练数据节整体指向 Gemini 4 Carbon 模型卡）。
