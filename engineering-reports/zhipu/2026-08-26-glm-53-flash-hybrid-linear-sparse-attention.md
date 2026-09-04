---
title: GLM-5.3-Flash：线性+稀疏混合注意力下的前沿智能平价化 — 320B/18B 原生多模态的成本-性能极值工程
date: 2026-08-26
source: https://z.ai/blog/glm-5.3-flash
---

# GLM-5.3-Flash：前沿智能平价化 — 320B/18B 原生多模态的成本-性能极值工程

**发布日期：** 2026-08-26（z.ai blog；中文发布页 zhipuai.cn/zh/research/163）
**来源：** https://z.ai/blog/glm-5.3-flash
**工程范式：** 智谱在 GLM-5 系列上第一次把「架构效率」而不是「规模堆叠」作为第一约束——用稀疏+线性混合注意力与 mHC 超连接，把 320B/18B 的模型推到逼近 Claude Opus 4.8 的能力区间，定价压到 Opus 4.8 的 1/40，并在国产加速芯片上端到端验证了可服务的推理栈。

## 设计哲学

核心约束：**前沿智能的推理成本必须下降一个数量级以上**。智谱的解法不是缩小模型等比例损失能力，而是用「少参数、多效率」的架构替代「多参数、多计算」的路线。

三个层次同时设计（原文结论自述）：
1. **架构层**：更少计算产出更强能力——激活参数几乎减半（相对 GLM-4.5 系 32B→18B）、层数几乎减半（92→45），却全面超越参数量高出一倍的 GLM-5.2；
2. **数据层**：30T token 多模态预训练语料（新训 base 模型，非 GLM-5.3 的蒸馏裁剪）；
3. **基础设施层**：推理引擎与国产芯片 co-design——"模型优化系统，系统承载模型"的正向循环。

放弃的是：单点绝对性能登顶的叙事（HLE/推理极值不追 Opus 级），换取的是 Pareto 前沿上「57 分智能 @ $0.045/task」的位置——原文明确用 Artificial Analysis Intelligence Index v4.1.1 的 Pareto 前沿语言来描述定位。这不是防守型小模型，是**主动把性价比做成产品形态**。

## 关键架构决策

- **注意力机制：稀疏注意力 + 线性注意力混合（GLM 系列首次）**。线性注意力通过递归状态建模捕获局部依赖（低成本、无随序列增长的缓存），稀疏注意力通过轻量索引器召回全局上下文（保持 1M 长上下文的精准性）。这是开源前沿模型中首个此类混合（原文称 "the first open-source frontier model with a hybrid sparse and linear attention architecture"——中文页表述为"首个采用稀疏注意力与线性注意力混合架构的开源前沿模型"）。
- **IndexPool（索引器压缩）**：稀疏注意力的索引器在 1M 上下文下是时延与内存瓶颈；IndexPool 通过加权池化把索引器的 4 个缓存向量压缩为 1 个，显著降低索引开销。这是针对「索引器自身 KV 放大」问题的专门设计。
- **mHC（Manifold-Constrained Hyper-Connections，流形约束超连接）**：沿用并改进超连接（Hyper-Connections）残差结构，加流形约束以提升 scaling 效率——与 GLM-5.3 同一家族技术（GLM-5.3 分析已覆盖其基础原理）。
- **MoE 未启用**：GLM-5.3-Flash 是 dense MoE 之外的第三条路——320B 总参数中有相当部分来自非激活的索引/状态通路，但激活仅 18B。与同代竞品（DeepSeek-V4-Flash 284B/13B、Kimi-K3、GLM-5.3）相比，其**每 head 每层注意力计算量在所有对比基线中最低**；KV cache（BF16 每层平均）比 GLM-5.3 小 4.4×，但仍略高于 Kimi-K3 与 DeepSeek-V4-Flash——原文明确承认这是后续优化方向（不粉饰短板）。
- **训练策略**：全新训练的 base（GLM-5.3-Flash-Base，非 GLM-5.3 剪枝），30T token 多模态语料。Base 对比（原文表）：18B 激活/320B 总参数下 MMLU 88.1、BBH 86.6、HellaSwag 87.1、LiveCodeBench-Base 37.6、SimpleQA 33.5——LiveCodeBench-Base 37.6 超过 GLM-5-Base（744B/40B，34.4）与 DeepSeek-V4-Flash-Base（284B/13B，29.9），说明数据与架构效率在 code 方向上有真实的代际增益。
- **原生多模态（GLM-5 系列首个）**：视觉不是外挂 encoder 的「看图」，而是进入编码循环——模型自主决定何时"观察"、用渲染结果做视觉自评估与测试时改进。针对视觉编码建了数据合成流水线（要求模型与环境交互、检视自身输出、迭代修正）；前端 coding 探索基于环境反馈的 RL；用真实用户流程做 agent 验证，把校验范围从功能正确性延伸到渲染与交互体验。
- **推理优化/国产芯片服务栈**（中文发布页细节，全部实测声称）：在 SGLang 上自建专用推理引擎（由 GLM-5.3 驱动的 infra agent 辅助开发算子与诊断瓶颈）；技术栈 = 线性注意力和 LM head 的节点内张量并行 + ReplaySSM + W8A8 量化 + INT8/FP8/BF16 混合缓存量化 + Layer Split；以算力换带宽、以通信换显存（针对国产芯片内存容量/带宽短板与 1M 上下文压力）；集群层用生产级 **EPD（Encode–Prefill–Decode）分离式架构**——多模态编码、prompt 预填充、逐 token 解码拆成可独立调度/独立扩缩容的工作池。宣称：同硬件上端到端性能较初始基线提升 3×，硬件效率与单 token 成本达到与主流 NVIDIA GPU 相当水平。
- **Post-training**：RL 重点在环境反馈（前端渲染、GUI 判断、Browser Use/Computer Use Agent 闭环）；匿名模型 ox-alpha（牛来）在 OpenCode/OpenRouter 大规模真实流量测试中验证，**全部请求流量由国产芯片提供算力**——把灰度发布本身变成 RL 反馈与基础设施压力测试。

## 关键结果

（全部来自原文 benchmark 表，未见第二方独立复测；对比模型数字为智谱自测/官方口径）

**Coding / Agentic 主线（强项）：**
| Benchmark | GLM-5.3-Flash | GLM-5.2 | DeepSeek-V4-Vision-Exp | Claude Opus 4.8 | GPT-5.6 Terra | Gemini 3.7 Flash |
|---|---|---|---|---|---|---|
| Terminal Bench 2.1 | 84.3 | 81.0 | 83.9 | 85.0 | 87.4 | 85.8 |
| DeepSWE v1.1 | 63.4 | 46.2 | 59.3 | 58.0 | 69.6 | 65.3 |
| NL2Repo | 56.3 | 48.9 | 57.7 | 69.7 | - | - |
| Toolathlon Verified | 78.4 | 59.9 | 75.9 | 76.2 | 74.9 | - |
| AutomationBench v1.0.6 | 48.8 | 26.2 | 38.8 | 41.0 | 37.2 | 52.3 |
| Agents' Last Exam | 26.3 | 20.4 | 27.3 | 27.0 | 28.0 | - |
| HLE w/ Tools | 55.3 | 54.7 | 55.1 | 57.9 | - | - |
| GDPval-AA v2 | 1773 | 1504 | 1675 | 1582 | 1571 | 1527 |

**Vision / 文档理解：**
| Benchmark | GLM-5.3-Flash | DeepSeek-V4-Vision-Exp | Claude Opus 4.8 | GPT-5.6 Terra | Gemini 3.7 Flash |
|---|---|---|---|---|---|
| OfficeQA Pro | 62.4 | 57.9 | 48.9 | - | - |
| CharXiv Reasoning w/ Tools | 89.4 | 80.4 | 89.9 | 88.0 | 88.7 |
| Chartography w/ Tools | 78.0 | 64.3 | 75.0 | 68.0 | 65.0 |
| BabyVision | 53.4 | 35.1 | 46.8 | 61.6 | 70.9 |
| MVbench | 77.8 | 69.4 | 67.1 | 75.0 | 82.2 |
| MMVU | 80.5 | 72.7 | 67.4 | 75.8 | 82.3 |

**解读要点：**
- Agentic 增量最大：DeepSWE 63.4 vs GLM-5.2 46.2（+17.2）、AutomationBench 48.8 vs 26.2（+22.6）——是 18B 激活模型对 32B 激活前代的碾压式超越，验证「架构效率 > 参数规模」；
- 逼近 Opus 4.8：Terminal Bench 84.3 vs 85.0、Toolathlon 78.4 vs 76.2（反超）、Z.ai Code Bench v1.0 max effort 29.0 vs 29.5；
- 弱于 Gemini 3.7 Flash 的视频/图像理解（BabyVision 53.4 vs 70.9、MMVU 80.5 vs 82.3）——多模态视觉仍是短板；
- 综合智能：AA Intelligence Index v4.1.1 得 57 分，与 Claude Opus 4.8 持平（中文页口径）；对应价格 $0.045/task（折后），约 Opus 4.8 的 1/40、GLM-5.3 的 1/10（限时 1/20）。

**Base 模型横向（原文表）：**
| Benchmark | GLM-4.5-Base 355B/32B | GLM-5-Base 744B/40B | DeepSeek-V4-Flash-Base 284B/13B | GLM-5.3-Flash-Base 320B/18B |
|---|---|---|---|---|
| MMLU | 86.1 | 88.3 | 88.5 | 88.1 |
| BBH | 86.2 | 87.4 | 84.9 | 86.6 |
| LiveCodeBench-Base | 28.1 | 34.4 | 29.9 | 37.6 |
| SimpleQA | 30.0 | 36.0 | 31.2 | 33.5 |

**效率数字：** 相对 GLM-5.3，注意力计算量降低 3.0×、KV cache 降低 4.4×；对比基线中注意力计算量最低。注：GLM-5.3 具体参数原文未披露（本次不引用其绝对参数量）。

## 范式对比

| 维度 | GLM-5.3-Flash | DeepSeek-V4-Flash | Kimi K3 | Gemini 3.7 Flash |
|---|---|---|---|---|
| 规模路线 | 320B/18B 混合注意力 dense+稀疏 | 284B/13B MoE（DSA） | 2.8T 级 MoE 旗舰 | 闭源（参数未披露） |
| 效率核心 | 线性+稀疏混合注意力 + IndexPool + mHC | MLA/稀疏注意力系 + 半自回归投机 | KDA/AttnRes + GPU kernel 深度优化 | 原生推理优化 + effort 控制 |
| 价格策略 | 1/40 Opus 4.8（折后） | 低价 API | 低价大杯 | 引入期折扣（3.7 Flash $1.5/$7.5，2027 到期） |
| 多模态 | 原生，进编码循环（视觉自评） | Vision-Exp 变体（后加） | 原生视觉 | 全模态 |
| 国产芯片 | 首发即大规模国产芯片生产验证 | 未主打 | 未主打 | N/A |

智谱与 DeepSeek 的差异最有意思：DeepSeek 用 MoE + MLA 做极致激活参数性价比，智谱这次完全绕开 MoE 的 router/专家负载问题，用**线性注意力代替大部分专家计算**——两种「稀疏化」哲学（参数稀疏 vs 计算稀疏）。而相对 Kimi K3 的「更大规模 + kernel 优化」，智谱选择「更小规模 + 架构换道」，证明 2026 下半年性价比竞争已经从「同样参数更便宜」进入「不同架构同智能」阶段。

## 社区评价

暂未独立核实 HN/Reddit 深度技术讨论（本次扫描未做社区追踪）。可记录的外部事实：匿名测试阶段 ox-alpha 在 OpenCode/OpenRouter 成为当周最受欢迎模型、创双平台调用量新高（智谱自述，未第三方复核）；该模型 8 月下旬已在 OpenRouter 被社区广泛猜测为智谱新模型。社区口碑信号正面但本文不引用未核实的第三方评价。

## 可复用的工程经验

1. **稀疏注意力的索引器本身会放大 KV——IndexPool 是教科书级修补**：任何「轻量索引器 + 全局稀疏召回」架构在 1M 上下文都会遇到索引器缓存膨胀，加权池化压缩 key 向量（4→1）是低代价高收益的通用技巧，可迁移到任何 retrieval-based attention 设计。
2. **线性 + 稀疏混合比全稀疏更容易落地**：线性注意力负责局部依赖（递归、O(1) 状态），稀疏注意力只负责全局召回（索引器选择性 attend）——分工明确后，长上下文服务成本大头（线性扫描）被消掉，且推理引擎只需对两类算子分别优化。这是「不要用稀疏注意力做所有事」的工程示范。
3. **能力对标要分层报告**：智谱对每个竞品只报自己最强的几个维度（对 Opus 4.8 报 coding/agentic、对 Gemini 报视频时坦承落后）——写作工程范式分析时应同样按维度拆解而非合并一个总分。
4. **把灰度发布变成基础设施测试**：ox-alpha 匿名上 OpenRouter + 全部流量跑国产芯片，一次获得「真实负载压测 + 用户反馈 + 国产芯片生产验证」三重收益。对任何计划换硬件平台的团队，这是比内部 benchmark 强得多的验证方式。
5. **infra agent 反哺 infra（模型优化系统）**：GLM-5.3 驱动的 agent 参与开发推理算子、诊断瓶颈——「用上一代最强模型写下一代模型的 serving 栈」已成为可执行的工程实践，不再只是愿景。
6. **诚实标注短板**：KV cache 仍大于 Kimi-K3/DeepSeek-V4-Flash 被原文主动披露并列为 next step——效率类报告中「已知短板 + 优化方向」比全篇自夸更可信，也直接服务后续迭代路线图。
