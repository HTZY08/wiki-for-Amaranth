---
title: MiniMax M3.1 Flash — 参数一个没加，全押在推理栈和量化感知训练上
date: 2026-10-19
source: "https://huggingface.co/MiniMaxAI/MiniMax-M3.1-Flash"
---

# MiniMax M3.1 Flash：同骨干换更便宜的推理栈

**发布日期：** 2026-10-19（API / M Plan / MiniMax Code 上线；权重 2026-10-23 发布于 Hugging Face）
**来源：** https://huggingface.co/MiniMaxAI/MiniMax-M3.1-Flash
**架构论文（MSA）：** https://arxiv.org/abs/2606.13392
**工程范式：** 骨干不动——依旧是 M3 的 428B/23B 原生多模态 MoE——三处改动全部落在"推理怎么更便宜"上：注意力全替换成稀疏、训练时就把量化算进去、投机解码换成自研 draft head。定位不是"更强"，是"同一档智能下每 token 更便宜"。

## 设计哲学

模型卡把改动列成三条，没有第四条：

1. **Sparse attention throughout**：把 M3 里保留的三个全注意力层也换成稀疏注意力——M3 只是部分层稀疏，M3.1-Flash 是全体。
2. **Quantization-aware training**：routed MoE 专家和注意力路径在训练阶段就做量化，不是后训练再压。
3. **DSpark speculative decoding**：用 DSpark 替换掉此前 EAGLE 式的 MTP 方案，草稿头随权重一起发布。

参数一个没加：约 428B 总参 / 23B 激活，和 M3 完全同规格；上下文仍是 100 万 token；输入文本/图像/视频，输出文本。

这个选择背后的约束很清楚——**M3 的架构（含 MiniMax Sparse Attention）已经吃完了架构红利的空间**。MSA 论文（arXiv 2606.13392）已经把 1M 上下文下单 token 注意力计算量降到 GQA 基线的 1/28.4，H800 上 prefill 14.2×、解码 7.6× 的墙钟加速。再往上做架构创新的边际收益不高，于是这一代把力气花在两处更"脏"的地方：**训练期的量化**（省显存、省带宽）和**解码期的投机**（省延迟）。

放弃的东西同样明确：**不公布骨干细节**（MoE 层数、专家数、路由方式未披露）。也从产品侧放弃了"可关闭思考"这个选项——M3.1-Flash 是"always thinks"的模型，只能通过 `reasoning_effort`（low / medium / high / xhigh / max）调深度，最低档不是"不想"，是"想得少"。这对成本敏感的高并发场景是一个真实的约束：**它无法退化成一个纯快模型**。

## 关键架构决策

- **注意力机制**：MiniMax Sparse Attention（MSA）覆盖全模型，包括此前 M3 保留为全注意力的前三个层。MSA 的设计是用一个轻量的、无 exp 运算的 Index Branch 对 KV 分块打分、按 GQA group 各自选 Top-k，Main Branch 只对被选中的块做精确 block-sparse 注意力；算子层用"KV 外层、gather Q"的顺序，使每个 KV block 只读一次且访存连续。稀疏注意力全线铺开是这代最激进的改动——它把"质量风险"从成本问题变成了训练问题。
- **MoE 设计**：约 428B 总参、每 token 激活 23B。专家数、粒度、路由与 gating 策略**未在模型卡披露**（M3 的公开资料为 256 个细粒度专家，M3.1 是否沿用未确认）。
- **训练策略**：预训练数据规模未披露。可确认的是量化感知训练覆盖 **routed MoE 专家 + 注意力路径**，即把"部署时要压的那部分"提前放进训练目标里。这是一个工程顺序上的选择：先决定怎么服务，再决定怎么训。
- **推理优化**：
  - 上下文 1M，推理档位 `reasoning_effort` 五级，采样推荐 temperature=1.0、top_p=0.95。
  - **DSpark 投机解码**带草稿头随权重发布，官方点名配套 SGLang / vLLM / TokenSpeed 三套 serving 方案，另有 FlagOS 多芯部署。
  - 配套生态明确列出仍在接入的：Transformers、KTransformers、unsloth、ATOM。
- **Post-training**：模型卡只说"building on MiniMax-M3, improves task performance and inference efficiency"，未披露 RL 算法、reward 设计或数据配比。从评测方向看，后训练明显向 agentic 任务、编码与网络安全倾斜（见下）。

## 关键结果

### 能力（来源：HF 模型卡，厂商自报；每项注明了 harness 与上下文长度）

| 基准 | M3.1 Flash | DeepSeek V4.1 Flash-1017 | DeepSeek V4.1 Flash | Kimi K3 | GLM-5.3 | GPT-5.6 Sol | Opus 5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Automation-Bench v1.0.6 | **62.8** | 60.5 | 54.8 | 46.7 | 48.8 | 45.8 | 50.3 |
| BankerToolBench | **76.2** | — | 73.7 | 69.1 | 74.5 | 74.6 | 76.2 |
| GDP.pdf AA | 20.8 | — | 12.8 | 22.0 | 11.2 | 27.2 | 21.6 |
| Terminal Bench 4.0 | 38.1 | **42.3** | 31.2 | 12.6 | 37.9 | 39.9 | 51.8 |
| LOCA-Bench 256K | **60.3** | — | — | 49.7 | 50.3 | 60.0 | 53.7 |
| Agents' Last Exam | 29.6 | — | — | 28.3 | — | 30.6 | 32.2 |
| OSWorld 2.0 | 61.7 | — | 54.3 | 58.3 | — | 65.7 | 70.6 |
| PostTrain Bench v1.1 | 39.3 | — | 30.5 | 36.6 | 37.5 | 36.2 | 40.4 |
| DeepSWE v1.1 | 73.7 | **77.0** | 74.2 | 67.5 | 66.9 | 73.0 | 74.0 |
| NL2Repo-Bench | 61.2 | **68.2** | 65.4 | 58.0 | 58.0 | 56.8 | 75.3 |
| SWE Refactor Bench | 23.0 | — | 11.8 | 19.5 | 10.4 | 28.5 | 31.0 |
| CyberGym | 82.2 | — | — | 80.0 | **84.5** | 83.6 | — |
| BabyVision（有工具） | 91.0 | **92.5** | 89.6 | 85.7 | — | 88.9 | 94.1 |
| HLE（无工具） | 43.4 | 42.6 | 39.2 | 43.5 | 42.3 | 49.5 | 55.6 |
| CharXiv RQ | 82.5 | — | 69.0 | **84.8** | — | 85.2 | 83.7 |

读法上有两条要点，都写在模型卡的评测注释里：

- **不是同一套 harness 跑出来的横向比较。** Terminal Bench 4.0 用 Codex 0.149.1；DeepSWE v1.1 用 mini-SWE-agent 2.4.5、512K 上下文；NL2Repo 与 PostTrain Bench 用 Claude Code（2.1.233 / 2.1.251）；CyberGym 用 Claude Code 1M 上下文；BankerToolBench 用 OpenCode 1.17.18。评测脚本、上下文预算、允许的思考预算各不相同，所以这张表反映的是"各家自己最有利配置下的成绩"，不是纯净对照。
- **空格不等于零。** 模型卡明确写 blank = no official result（例如 CLI-only 的结果被排除），不是 0 分。

这张表给出的画像相当具体：**M3.1 Flash 赢在"工具调用密集、流程可判"的任务（Automation-Bench、BankerToolBench、LOCA-Bench 256K、CyberGym），输在"仓库级代码工程"上（Terminal Bench 4.0 输给 DeepSeek 4.2 分，NL2Repo 输 7 分，DeepSWE 输 3.3 分）**。和 Opus 5 的正面对比更清楚：BankerToolBench 打平（76.2），SWE Refactor 只有 23.0 vs 31.0，OSWorld 61.7 vs 70.6。

### 成本（厂商定价页，2026-10-19/20 快照）

每百万 token：输入 $0.15、输出 $0.60、缓存读取 $0.015。**100 万上下文不加价**——没有长上下文阶梯。这个定价把"1M 上下文"从奢侈品变成默认项。

但第三方实测给了一个必要的修正：AI/ML API 的 51 次编码任务测试里，M3.1 Flash 通过 49 次（DeepSeek V4.1 Flash 51 次、GLM-5.3 Flash 50 次），**并且每个任务平均写出约 5,900 个输出 token，比 DeepSeek V4.1 Flash 多 62%**——因为它 always thinks，最低档也仍在思考。单价便宜 2.6 倍，但 token 消耗多 62%，最终每任务成本的优势会被削掉一大块。这正是"每 token 便宜 ≠ 每任务便宜"的教科书案例。

## 范式对比

三家中国厂商在 2026 年下半年的效率路线，切口完全不同：

| | 改什么 | 代表动作 | 代价 |
| --- | --- | --- | --- |
| **MiniMax** | 推理栈 | MSA 全铺 + QAT + DSpark 投机 | 骨干不变，能力上限被 M3 锁死；always-think 无法退化成快模型 |
| **DeepSeek**（V4 系） | 注意力结构 + KV | CSA/HCA 混合注意力、跨层 KV 复用、CED 架构（decode 激活 16B / prefill 激活 8B） | 结构复杂，训练与推理的耦合更深 |
| **Moonshot**（K3 系） | 专家规模 | 2.8T 总参 / 896 专家选 16、KDA + Gated MLA 3:1 混合 | 权重体积与部署门槛（252GB 级 8-bit 权重） |

MiniMax 这条路的独特性在于**它把"降本"做成了训练期承诺而不是部署期技巧**：量化进训练目标、稀疏进全部层、草稿头随权重发。好处是服务侧几乎不需要额外工程就能吃到收益（SGLang/vLLM 提供 recipe）；代价是模型能力被同一个骨干封顶——这也解释了为什么 M3.1 是"Flash"而不是新的旗舰命名。

与 Anthropic 的对照更有意思：Haiku 5.5 是**削减能力换安全边界清晰**，M3.1 Flash 是**保持能力换每 token 成本**。两家都在做"小档位"，但对"小"的定义相反。

## 社区评价

第三方评测的分歧集中在两处。第一是**架构透明度**：多家测评指出 M3.1 的参数规模、激活量在发布初期没有官方口径（模型卡后补为 428B/23B），主张"等模型卡再下结论"。第二是**基准数字的来源一致性**：Automation-Bench 在不同转引里出现过 62.2 与 62.8 两个值，模型卡最终写的是 62.8。此外，Artificial Analysis 的独立测得智能指数约 42–43（M3 为 29），但同期测出"知识题答错时倾向于猜而不是承认不确定"，且输出 token 量偏大——与上面"每任务成本"的观察一致。

平台侧的事实倒是没有分歧：它上线时以匿名代号在 OpenRouter 上跑过，正式发布后权重 10 月 23 日开放，采用 MiniMax Community License。

## 可复用的工程经验

1. **降本的三件套有先后顺序：先决定怎么服务，再决定怎么训。** M3.1 把量化写进训练目标，等于承认"部署形态是设计输入而不是事后优化"。做自研模型或微调时，量化/稀疏/投机解码应该进训练计划，而不是上线前一周的调优项。
2. **"always think" 是一个成本陷阱。** 单价降 2.6 倍、token 涨 62%，净收益远小于账面。评估任何推理模型，先测**每完成一个任务的总 token 与总成本**，别用单价排序。
3. **稀疏注意力铺到 100% 要用训练去补，不是靠推理配置。** 把最后三个全注意力层也换掉之后，质量靠训练期对齐而不是采样参数。
4. **看横向 benchmark 先看 harness 表。** 这张表里 Terminal Bench 用 Codex、DeepSWE 用 mini-SWE-agent、NL2Repo 用 Claude Code、BankerToolBench 用 OpenCode——四套脚手架、四种上下文预算。跨模型对比时，脚手架差异经常大于模型差异。
5. **同骨干做版本迭代时，把改动控制在一个维度。** M3 → M3.1 只动推理栈与后训练，参数不动，好处是"变便宜了"这件事可以被干净地归因；坏处是上限也一起被锁住。要不要这么切，取决于你这一代的目标是抢份额还是抢能力。
