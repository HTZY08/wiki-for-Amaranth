---
title: Gemini 4 Hydrogen — 一次预训练喂三个档位，用"每任务成本"而不是每 token 价格定位
date: 2026-11-12
source: "https://deepmind.google/models/model-cards/gemini-4-hydrogen"
---

# Gemini 4 Hydrogen：家族分型走到"快执行"这一层

**发布日期：** 2026-11-12（模型卡标注 Published 12 November 2026）
**来源：** https://deepmind.google/models/model-cards/gemini-4-hydrogen
**评测方法页：** https://deepmind.google/models/evals-methodology/gemini-4-hydrogen
**工程范式：** 一个基座（Argon）派生两代适配体（Carbon → Hydrogen/Neon）。Hydrogen 不做新预训练，定位在"快执行"层：牺牲终端/电脑操作的精度，换取单位时间内完成更多 agentic 任务，并在安全评测上按"能力增量"而非"发布次数"分配预算。

## 设计哲学

模型卡里有一句结构性的话：**"Gemini 4 Hydrogen is adapted from Gemini 4 Carbon."** 这句话在架构、训练数据、数据处理、硬件、软件五个小节里各出现一次——五节正文全部指向 Carbon 模型卡。

也就是说，Hydrogen 的成本结构里没有一次新的预训练。约束是明确的：**不打算为"快档"再烧一次前沿预训练，只能用已有 Carbon 权重往下调**。原文没有说明改动发生在哪个阶段（蒸馏、剪枝、继续训练均未披露），这是这套文档体系一贯的透明度代价。

定位原文写得很清楚，且是相对关系而非绝对能力：

- 前沿档（Carbon、Argon）"built for deep, long-horizon reasoning on your hardest problems"；
- Hydrogen "built for rapid execution across diverse agentic workflows"，并明确点名"as sub-agents orchestrated alongside frontier models"。

所以 Hydrogen 的竞争对手不是别家的旗舰，而是**同一套编排里被并行拉起几十次的子 agent 槽位**。这个设定直接决定了后面所有取舍：单任务精度可以让，单任务延迟和 token 支出不能让。

放弃的东西有三样：架构透明度（全部指向 Carbon 卡）、极端精度（终端操作、电脑操作明显落后）、拒答克制（无理由拒答比上一代升了 5.57 个百分点，见安全节）。

## 关键架构决策

- **注意力机制**：未披露。模型卡架构节整节指向 Gemini 4 Carbon，Carbon 卡本身也不给注意力选型。
- **MoE 设计**：未披露。专家数、粒度、路由、gating 全部没有公开。参数规模同样未披露。
- **训练策略**：未披露。唯一可确认的因果是"adapted from Carbon"，即沿用 Carbon 的权重底座，改动在后续阶段。知识截止 2026 年 3 月——比发布时间晚不到一年，但对 11 月发布的模型来说这个 cutoff 偏旧，说明底座不是为"最新知识"重建的。
- **推理优化**：
  - 上下文：输入+输出共享一个 100 万 token 的统一窗口。
  - 输出预算：默认同步输出上限 64K token；"background long decode" 可延伸到接近 1M。这是一个产品化的显式开关——把"要不要等"交给调用方，而不是让模型自己决定吐多长。
  - 思考档位：四级（low / medium / high / xhigh），**默认 high**（据 Gemini API 模型清单，2026-11 快照）。默认不在最低档，说明 Google 判断这个档位的买家愿意用 token 换成功率。
  - 分发渠道一次铺满：Gemini app、Gemini API、Google Sheets、AI Studio、Gemini for business、Antigravity、Google Search。Sheets 和 Search 出现在列表里，说明这个档位承担的其实是"高 QPS 消费级入口"的推理负载。
- **Post-training**：模型卡只说全周期内建安全（预训练数据过滤、SFT + RL 后训练、产品层与系统层过滤、使用监测），没有给 RL 算法、reward 设计或数据配比。

## 关键结果

### 能力（来源：模型卡评测表，2026 年 11 月；DeepMind 自报）

| 类别 | 基准 | Gemini 4 Hydrogen | Claude Sonnet 5.5 | GPT-6.1 Terra |
| --- | --- | --- | --- | --- |
| Agentic coding | SWE-sweep | 13.5% | 3.1% | 5.8% |
| Agentic coding | Terminal-Bench 4.1（去作弊校正） | 57.0% | 63.9% | — |
| Knowledge work | Agents' Last Exam v1.1 | 71.6% | 60.4% | 69.8% |
| Knowledge work | AutomationBench-AA | 76.1% | 71.8% | 60.2% |
| Knowledge work | Vending-Bench 2（银行余额） | $14,549 | $11,165 | $9,107 |
| Computer use | OSWorld-2.1（离线子集） | 77.6% | 83.9% | 74.2% |
| 多模态理解 | MKA（Climb WSR 准确率） | 53.4% | 52.0% | 43.8% |
| 多模态理解 | Chartography | 66.6% | 61.6% | 63.2% |
| 科学与数学 | Terminal-Bench-Science 0.1 | 51.4% | 59.9% | 58.3% |
| 推理 | HLE-Diamond | 58.8% | 53.3% | 47.3% |

这张表读下来有一条清晰的分界线。**凡是"一次交付、结果可自动判定"的基准，Hydrogen 全部领先**：Agents' Last Exam 领先 Sonnet 5.5 11.2 个百分点，Vending-Bench 2 领先 30%，SWE-sweep 是竞品的 2–4 倍。**凡是"多步交互、状态持续演进"的基准，Hydrogen 全部落后**：Terminal-Bench 4.1 落后 6.9 个百分点，OSWorld-2.1 落后 6.3，Terminal-Bench-Science 落后 8.5。

这个组合不是随机的。它符合"高吞吐执行器"的定位：短链路、单轮、可并行、结果好判的任务交给它；需要长时间维护环境状态、每步都要精确操作的任务交回前沿档。也是这条分界线让"每任务成本"这个指标有意义——同样 $1.50/$7.50（Gemini API 清单价，2026-11 快照）的 token 价格下，能不能把一个任务一次做完，才是成本。

一个诚实的自我限制写在模型卡里：**"at times the model may use more tokens to maximize performance, especially at higher thinking levels."** 也就是说默认 high 档下，它可能用更多 token 换成功率——这意味着"每 token 便宜"和"每任务便宜"在这款模型上不完全等价，宣传口径选的是后者。

### 安全（按能力增量分配评测预算）

这部分是这次发布里最有工程价值的细节。Hydrogen 没有做一套完整的关键能力评测，理由写在模型卡里：它相对 Gemini 4 Argon 未出现 Material Capability Change（MCC），因此按 Frontier Safety Framework（2026 年 4 月版）不需要全套 CCL 评测，改为只做 CBRN 与网络安全两个域的定向评估。

结果：两个域都**未达 CCL，但触及了 CCL 的告警阈值**（原文：CCL not reached, CCL alert threshold reached）。CBRN 中的化/放/核 uplift TCL 与"有害操纵"CCL 的处理是"沿用 Argon 的结论 + 继续部署缓解措施"；Loss of Control 的三大项则因为 MCC 不成立而免测——但 DeepMind 写明"nevertheless applying control, monitoring and model security mitigations as if the TCL had been reached, as a conservative assumption"。

相对 Gemini 3.8 Flash 的安全指标变化（百分点，模型卡原表）：

| 评测 | 变化 |
| --- | --- |
| 文→文安全（越高越好） | +0.80pp |
| 多语言安全 | +1.10pp |
| 图→文安全 | +7.00pp |
| 拒答语气（客观、非说教） | −0.65pp |
| 无理由拒答（越低越好） | **+5.57pp（退步）** |

模型卡自己点出了退步的来源："unjustified refusals are higher, particularly for multimodal prompts." 结合图→文安全 +7.00pp 一起看，这是同一个取舍的两面：多模态侧的分类器更保守，安全率上去了，误拒也上去了。

## 范式对比

三条路线在 2026 年下半年收敛到同一个结构：**基座只训一次，往下的档位靠适配**。

- **DeepMind**：Argon（新基座）→ Carbon（前沿适配）→ Hydrogen / Neon（快档与中价档）。产品矩阵按"任务形态"切分，而不是按参数量切分。文档层面把"适配"写死（五节指向 Carbon），把能力差异放在评测表里让人自己读。
- **Anthropic**：同一时间用"评测预算随能力增量缩放"的做法——Haiku 5.5 的系统卡直接说明删节（见 `anthropic/2026/10-07-claude-haiku-5-5`），理由是"把预部署测试集中在前沿模型上"。两家独立得出同一结论：**小档位不值得同等规格的安全文档**。
- **OpenAI**：GPT-6.2 走的是同代双发（Astra + Sol），用 Preparedness Framework 的阈值分级（Critical / High）而不是删节评测来控制成本。

差异在于"档位"用什么维度定义。DeepMind 用**任务形态**（深推理 vs 快执行 vs 高并发入口），Anthropic 用**能力层级 + 风险阈值**，OpenAI 用**能力阈值 + 部署面**。这也是为什么 Hydrogen 的评测表要放 Agents' Last Exam、Vending-Bench 这类"任务完成度"指标——它的档位是任务给的，不是参数给的。

## 社区评价

发布后主流报道集中在家族分型本身：MLQ.ai 指出 Carbon 的模型卡索引仍然只列 Argon，安全报告链接指向 10 月的 Argon 报告而非 Carbon 专项评估——文档一致性上确实存在这类缝隙。Hydrogen 的模型卡里"Safety & Security Report (coming soon)"出现了两处，即发布当日安全报告尚未上线。引用这份卡片时需要注意：能力数据是发布日数据，安全章节的完整版缺失。

## 可复用的工程经验

1. **用"任务形态"切产品线，而不是用参数量切。** 评测表按"一次交付 vs 多步交互"分栏，客户能直接判断该把哪个档塞进编排的哪个槽位。参数量切分对买家没有决策价值。
2. **默认档位不要设在最低。** Hydrogen 默认 high 思考档，等于承认"买家愿意用 token 换一次成功率"。默认值是可以被起诉的产品承诺，别把它当省钱开关。
3. **安全评测预算按"能力增量"分配。** 先做 MCC 判定，MCC 不成立就只测高风险域，但缓解措施按最坏假设上（"as if the TCL had been reached"）。这是可以照抄的工程流程：**判定可以放松，缓解不能放松**。
4. **把"长输出要不要等"产品化为开关**（64K 同步 / 1M 后台长解码）。比让模型自己决定吐多长更可控，也更好做容量规划。
5. **看 benchmark 要看它测的是"交付"还是"过程"。** 同一款模型可以在 Agents' Last Exam 上赢 11 个点、在 Terminal-Bench 上输 7 个点，两者不矛盾——它们测的不是同一件事。选型时先问自己的任务属于哪一类。
6. **无理由拒答要和误伤率一起看。** 多模态安全 +7.00pp 的代价是误拒 +5.57pp，如果你的产品是多模态高频入口，这个代价会直接变成用户体验问题，得自己做一遍良性 prompt 回归。
