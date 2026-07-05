---
title: MiniMax-M2 — 小激活参数撬动最大真实世界智能
date: 2026-07-05
source: https://arxiv.org/abs/2605.26494
tags: [minimax, moe, agent-native, rl, fine-grained-experts, self-evolution]
---

# MiniMax-M2 — 小激活参数撬动最大真实世界智能

**发布日期：** 2026年5月（arXiv 2605.26494）
**来源：** https://arxiv.org/abs/2605.26494
**工程范式：** 极致激活效率 + Agent-native 全栈设计

## 设计哲学

核心约束：229.9B total / 9.8B activated per token。M2 系列坚持 "mini activations unleash max real-world intelligence"，用极小的激活参数换取最大真实世界能力。

这不仅仅是一个效率目标，而是一个**系统级设计约束**——所有架构决策（专家数量、门控机制、注意力类型、后训练管线）都围绕着"如何在 9.8B 激活参数下与 10 倍以上算力的模型竞争"这一核心命题展开。

## 关键架构决策

### 基础配置

| 参数 | 值 |
|------|------|
| 层数 | 62 层 decoder-only Transformer |
| Hidden dim | 3,072 |
| Vocab size | 200,064 |
| Total params | 229.9B |
| Activated params | 9.8B/token |
| 预训练 tokens | 29.2T |
| 原生上下文 | 192K |

### 256 Fine-Grained Experts — 路由组合多样性的杠杆

M2 使用 256 个细粒度专家，每个 token 激活 8 个。对比常见的 32-64 专家设计（如 DeepSeek-V3 的 256 专家但粒度不同），M2 的核心洞察是：

- **组合多样性**：256 选 8 的路由空间（C(256,8) ≈ 10^13）远大于 32 选 2 或 64 选 4，极大增加了模型可以表达的"技能组合"数量。
- **设备利用率**：更多的小专家降低了跨设备 expert utilization variance，减少负载不均衡带来的空闲等待。

Ablation 数据（论文 Table 1）显示，在 500B token 的小规模实验中，从 32 experts/top-2 升级到 128 experts/top-8，在 MATH 上从 19.6 提升到 24.1（+23%），HumanEval 从 29.7 到 32.5（+9.4%）。

### Sigmoid Gating + Expert Bias — 废弃辅助损失

这是对传统 MoE 门控（softmax top-k）的一个重要修正：

- **Sigmoid gating**：每个 expert 获得独立的激活分数，去掉了 softmax 的零和约束。多个 expert 可以同时以高置信度被激活，路由动态更平滑。
- **Learnable expert bias**：每个 expert 带可学习的偏置项，隐式调节 expert 利用率，大幅降低对 auxiliary load-balancing loss 的依赖。

**工程意义**：在 256 expert 的规模下，auxiliary loss 的梯度信号极其稀疏且容易被主任务 loss 淹没。去掉对它的依赖后，路由自然变得更均匀且训练更稳定。

### Full Attention — 对 Hybrid/SWA 的明确否定

M2 在全部 62 层使用 full multi-head attention（GQA: 48 query heads, 8 KV heads），明确放弃了 MiniMax-Text-01 中的 hybrid attention（Lightning Attention + full attention 交错设计）。

论文给出了令人信服的**负向证据链**：

1. **标准 benchmark 无法暴露差异**：在 MMLU、BBH、MATH 上 hybrid SWA 看起来与 full attention 无异。
2. **更大规模下差距显现**：在复杂多跳推理和长上下文检索任务上，hybrid SWA 出现明显退化——RULER 128K CWE 从 90.0 掉到 72.0，MTOB K-e Bleurt 从 60.0 掉到 45.0（Table 2）。
3. **SFT 后长上下文差距加剧**：在 >32K 的 agent 任务上，SWA 表现显著更差；在 <32K 的任务上结果混合（Table 3）。
4. **基础设施不成熟**：线性/稀疏注意力的低精度存储敏感性、缺乏 prefix caching、与 speculative decoding 的集成不清晰——这些都是生产部署的硬伤。

**范式含义**：这是一个"反趋势"决策——当业界纷纷涌向 sliding window、linear attention、hybrid 时，M2 用系统的消融实验证明：对于通用 agent 能力，full attention 仍然是不可妥协的基座。论文也坦诚："随着上下文增长和 GPU 算力放缓，sub-quadratic attention 将变得越来越重要"——这是对未来的前瞻性注脚，而不是对当前选择的辩护。

### Multi-Token Prediction (MTP)

- 预训练时 K=1，loss weight 从 0.3 退火到 0.1。
- 继续预训练衰减阶段通过**权重复制**扩展到 K=3 个 MTP 模块，用于 speculative decoding。
- 关键技巧：权重复制后先冻结主模型单独训练 MTP 模块，loss 稳定后再联合训练。随机初始化的 MTP 模块会暂时退化主模型——这是一个重要的工程陷阱记录。

## Agent-Native 数据管线

这一部分可能是 M2 系列最值得深入研究的工程贡献。整个后训练数据体系围绕一个核心原则：**每个训练轨迹都必须挂载在一个可执行的工作空间上，并配以 artifact-aligned 的验证信号。**

### Agentic Coding 三管线

#### 1. SWE-Scaling Pipeline（从 GitHub PR 到可验证任务）

六阶段流水线：
1. **PR 采集与过滤**：大规模爬取公开 GitHub PR，规则过滤（已合并、带测试用例）。
2. **Agent 合成的多语言 Docker 环境**：非 Python 语言的环境合成不可靠，因此引入 agent-driven execution loop——利用执行反馈迭代生成和修复构建脚本。覆盖编译型语言的 toolchain 协调、异构执行接口、仓库级结构差异。
3. **PR 标注与任务分流**：Bug fix / Feature addition / Performance optimization / Refactoring——不同类型需要不同的 verifiable reward 定义。
4. **测试驱动的可验证奖励**：
   - Bug fix: F2P (Fail-to-Pass) + P2P (Pass-to-Pass) 双重验证
   - Feature addition: 提取新增测试点
   - Performance optimization: P2P + 前后性能对比
5. **模型辅助任务验证**：用 LLM 验证问题描述与测试用例的一致性，补全缺失信息。
6. **任务变换与增强**：
   - Bug injection：注入额外 bug 增加难度
   - Commit merging：合并相邻 commit 构建多步修复
   - SWE-Test conversion：反转任务——让 agent 编写能检测 bug 的测试用例
   - Code review tasks：无运行环境的静态分析

最终产出覆盖 **10+ 编程语言**的大规模训练集。

#### 2. AppDev Pipeline（从零构建完整应用）

与 SWE 不同，AppDev 需要从零构建完整应用。创新在于 **Agent-as-a-Verifier (AaaV)** 三层评价：

1. **Execution Layer**：文件存在性、语法、依赖解析、构建成功、HTTP 状态、JS 错误——硬门槛
2. **Interaction Layer**：Playwright 驱动，检查交互元素、按钮响应、端到端工作流
3. **Visual Aesthetics Layer**：布局专业性、视觉层次、配色和谐、现代 UI 标准

专家元查询（meta queries）编码生产级技术模式，system prompt distillation 让模型将专家最佳实践内化为默认行为。

#### 3. Terminal-Gym（终端任务自动合成）

以完整 Stack Overflow 数据集为种子，经过严格的规则过滤（仅保留已采纳答案、中等难度、可脚本化、可验证的帖子），然后三阶段合成：

1. **环境与测试生成**：Agent 自动生成 Dockerfile + 测试脚本，迭代修复直到通过
2. **查询进化与统一测试**：移除显式 hint，用统一测试套件验证语义一致性而非过拟合提示风格
3. **难度校准**：优先保留零样本通过率低的变体

这正是从 Terminal-Bench 到 **Anything2Docker** 和 **CVE-Factory**（自主安全研究）的基础。

### Agentic Cowork 四领域

四个领域（deep search、office tasks、financial analysis、slide generation）共享同一架构：**真实工作空间 → 强教师模型蒸馏 → artifact-aligned 验证信号**。

值得注意的工程选择：
- Deep search：使用 **guide-and-rewrite** 策略迭代模糊化问题中的实体直到难度合适；每个合成任务配上显式的 evidence specification，拒绝无证据支持的编造。
- Financial analysis：使用 **evidence-driven synthesis**——先执行真实金融工具收集 grounded 轨迹，再反向推导任务，保证可执行性和可验证性。
- Slide generation：增加 **visual scorer**——渲染为图像后评判，不依赖单一渲染工具库。

### Reasoning 数据的三轴缩放

1. **Query-side scaling**：扩大问题覆盖面，特别是 underrepresented 难度区间
2. **Response-side scaling**：每问题多解，OOD generalization 随响应数单调提升
3. **Training-side scaling**：在固定算力预算下优化 query 扩展与 response 扩展的比例，动态分配

质量控制贯穿全部三个阶段。

## Forge — Agent-Native RL 系统

Forge 是 M2 的 RL 基础设施，设计目标是解决"不可能三角"：**System Throughput × Training Stability × Agent Flexibility** 三者间的根本张力。

### MDP 形式化

LLM 作为 policy，context management/memory access/agent state transition 都作为 environment。环境边界画在模型生成接口处——所有处理、转换、响应模型输出的组件都是环境动态的一部分。

**关键设计原则**：policy 不需要显式推理或控制环境与状态转换。训练在 (s_t, a_t) 对上操作——每个 pair 是一个梯度更新的原子单元。而 credit assignment、advantage estimation、reward propagation 仍然在 episode 级别进行。

### CISPO 算法

从 MiniMax-M1 继承的 Clipped Importance Sampling Policy Optimization：

- 非对称裁剪：上界 1+ε_high 防止过大更新，下界 0 允许激进降权
- Stop-gradient on clipped ratio：防止二阶项
- Reward-to-go + trajectory-level baseline 降低方差

### 复合奖励设计

| 奖励分量 | 作用 |
|---------|------|
| Process reward | 密集中间奖励，惩罚语言混合/工具格式错误，奖励结构化推理 |
| Completion time reward | 激励并行执行，相对完成时间单调递减 |
| Task performance | 主任务信号 |

复合奖励 r_t = α·r_t^process + β·r_t^speed + r_t^perf

### Mixed-Domain RL 训练

单一领域 RL 导致灾难性遗忘。M2 在每个训练阶段同时从四个领域采样：**reasoning, coding, agent, general**。三轴调控：domain mixing ratios、context length、difficulty distribution。

早期阶段侧重奠基能力（reasoning + general），后期逐步增加 agent 和 coding 的比例。

### 窗口化 FIFO 调度 (Windowed FIFO)

Agent rollout 完成时间从秒到小时不等：

- 严格 FIFO → 受 straggler 拖累
- 完全贪婪 → 分布偏移，短任务集中在早期 batch

Windowed FIFO 的折中：给定队列 Q，训练调度器只能在滑动窗口 [T_i, T_{i+W-1}] 内获取已完成轨迹（W=0.3N）。窗口内贪婪，跨窗口保持顺序。

**工程洞察**：这是一个简单但极其有效的方案——在 agent RL 场景下"批次分布一致性"与"训练稳定性"之间的关系此前被严重低估。

### Prefix Tree Merging — 最高 40x 加速

多轮 agent 轨迹中，同一 rollout group 内的训练样本共享大量前缀。传统训练独立计算每个样本，冗余计算严重。

Prefix tree merging 将线性样本处理重构为树状计算：共享前缀在前向传播中只算一次，之后分支到各自的 response 段。由于因果注意力在共享前缀上的激活值不变，数学等价于独立样本训练，**零近似误差**。

在实践中达到最高 40x 训练加速和对应的显存节省——这对超长上下文 agent RL 来说是关键使能技术。

### 推理加速三件套

1. **MTP speculative decoding**：MTP 模块通过 top-K KL divergence 与 RL policy 共同训练，保证策略分布变化时 draft acceptance rate 不降
2. **Heterogeneous prefill-decode disaggregation**：分离 prefill 和 decode 实例，消除 MoE 架构中的互相干扰
3. **Global L3 KV Cache Pool**：DFS 驱动的分布式 KV 缓存，cost-aware 路由平衡排队延迟与缓存迁移成本

### 白盒 vs 黑盒 Agent 支持

Forge 通过 Gateway 抽象层统一两种范式：

- **白盒**：context management 逻辑注册到框架内，训练时重建精确状态分布
- **黑盒**：只收集外部可见的 (s_t, a_t, o_t) 元组，支持任意内部架构

已在数百个 agent scaffold 和数千种工具调用格式上验证。

## Interleaved Thinking

M2 将 interleaved thinking 作为一等公民建模原则——推理 token 和动作 token 交替生成，完整推理状态跨轮次持久化。

### Plan-Act-Reflect 循环

每轮：
1. **Plan**：审查累积状态，制定/修正策略
2. **Act**：基于计划选择并执行工具调用
3. **Reflect**：评估观察结果与预期的偏差，更新世界模型

### 推理状态持久性的影响

Ablation 显示（被剥离 thinking blocks 的消融），推理状态持久性在需要多步推理的 agent 任务上（deep search、software engineering）增益最大。这是因为不持久的情况下每轮都需要重新推导上下文、约束和部分结论，导致累积状态漂移。

## Self-Evolution — M2.7

这是论文中最重要的概念性贡献之一——模型开始参与自身训练循环的调试和优化。

### Model Iteration System

人类制定目标 → 通过 chat 引导 agent → agent 在 Agent Harness 中执行。关键在于 Agent Harness 本身由**内部 M2.7 模型零人工代码**生成。

Harness 包含：hierarchical skills for action chaining、persistent memory、safety guardrails、evaluation infrastructure。

### 双循环工作流

- **外循环**：人类主导的实验规划 + 重大迭代决策审查
- **内循环**：M2.7 自主执行——profiling 运行、读取日志、诊断指标异常、自动调试代码和调整配置

这吸收了 **30% 到 50%** 的日常迭代工作负载。

### 递归 Scaffold 升级实例

在一项内部编程 scaffold 优化任务中，M2.7 执行了 100 轮的完全自主迭代循环：分析失败 → 修改代码 → 评估变化。发现了 loop detection 等机制和更好的参数组合，在内部评测上取得 **30% 性能提升**。

**工程意义**：模型正在改进塑造它后续迭代的基础设施——这构成了一个正反馈循环，不再局限于单一 checkpoint 的优化。

## 关键结果

M2.7 与 frontier 模型（Claude Opus 4.6, GPT 5.4, Gemini 3.1 Pro）在 ~10B 激活参数下竞争：

| 基准 | M2.7 | M2.5 | Opus 4.6 | Sonnet 4.6 | GPT 5.4 |
|------|------|------|----------|------------|---------|
| SWE-bench Pro | 56.2 | 55.4 | 57.3 | 57.2 | 57.7 |
| SWE-bench Multilingual | **76.5** | 74.1 | 77.8 | 75.9 | 70.5 |
| Multi-SWE-bench | **52.7** | 51.3 | 50.3 | 51.0 | 49.0 |
| Terminal-Bench 2.0 | 57.0 | 51.7 | 65.4 | 59.1 | 75.1 |
| BrowseComp | 77.8 | 76.3 | 84.0 | 74.7 | 82.7 |
| GDPval-AA | 50.0 | 35.0 | 55.0 | 57.0 | 58.0 |
| AIME 2026 | **94.2** | 87.2 | 92.5 | 92.7 | 97.0 |
| GPQA-Diamond | **89.8** | 85.2 | 89.6 | 87.5 | 92.0 |

系列内进步（M2 → M2.5 → M2.7）在所有 11 个可比较基准上持续提升，最大增益出现在深搜（BrowseComp +33.8）、工具使用（Toolathlon +27.5）和自主 ML 工程（MLE Bench Lite +26.6）领域——这些正是 M2.5/M2.7 数据管线投入最大的方向。

## 范式对比

### vs DeepSeek-V3 系列
- 都采用 MoE + MTP，但 M2 的 fine-grained experts（256 个）比 V3 更极端
- M2 采用 sigmoid gating + expert bias，区别于 V3 的 softmax + auxiliary loss
- M2 的全注意力 vs V3 的 MLA（Multi-head Latent Attention）——两种不同的效率优化路径
- M2 在 agent-native data 和 RL 基础设施上的投入远大于 V3

### vs Claude 系列
- Claude 不使用 MoE，走 dense 路线
- M2 在 ~10B 激活下与 ~100B+ 的 Claude Opus 竞争——这是 MoE 激活优势的最强证明
- M2 的 agent data pipeline 工程比 Anthropic 公开披露的详尽得多

### vs GPT-5
- OpenAI 的 MoE 架构细节不公开，但估计参数量级更大
- M2 在 Multi-SWE-bench 和 SWE-bench Multilingual 上超过 GPT 5.4，在 AIME 2026 和 GPQA 上接近

### vs Gemini 3.1 Pro
- M2 在 BrowseComp、Wide Search、MM Claw 等 agent 任务上超过 Gemini
- 在传统知识基准（MMLU-Pro）上明显落后（81.8 vs 91.2）

## 可复用的工程经验

### 1. 验证信号的质量比数量更重要
M2 整个数据管线的最核心原则：**每个训练轨迹都必须有可执行的、artifact-aligned 的验证信号**。SWE 任务用 F2P/P2P 测试，AppDev 用 AaaV 三层检查，Deep Search 用 evidence specification。不接受 LLM-as-a-Judge 的模糊反馈作为唯一信号。

### 2. 合成数据需要工作空间（workspace）
几乎所有数据管线都围绕"在工作空间中执行"构建——Docker 沙箱、Playwright 浏览器、Excel 工作簿、Slide deck。没有工作空间的合成数据容易教模型"看起来像"而不是"真正会"。

### 3. Full Attention 的代价可能被 hybrids 低估
M2 在 62 层全部使用 full attention 而不是 hybrid，并用大量消融证明 hybrid 在长上下文的 agent 任务上确实不行。这是一个反潮流的实验结论。

### 4. Agent RL 需要一个专门的系统——而不仅仅是套用 RLHF
Forge 的架构教训：agent RL 的"不可能三角"（吞吐量 × 稳定性 × 灵活性）不能靠组合现有的 RLHF/PPO 工具解决。Windowed FIFO、Prefix tree merging、white-box/black-box 统一——这些都是 agent 场景独有的需求。

### 5. 混合领域训练防止遗忘
Mixed-domain RL（reasoning + coding + agent + general 同时训练）有效防止了单领域 RL 导致的灾难性遗忘。这是多阶段训练的最优实践。

### 6. 细粒度专家的组合潜力
256 experts × top-8 的路由组合空间极大。这不是简单的"更多人"，而是"更多组合方式"——每种组合代表一种技能协作模式。

### 7. Self-evolution 不需要完全的自主
M2.7 的 self-evolution 采用双循环设计：人类外循环做重大决策，模型内循环做执行和调试。这种"人类掌舵、模型建造"的分工在可预见的未来可能是最实用的 self-evolution 形态。

### 8. 合成数据质量控制的 "不完美但可验证" 原则
数据质量不是追求完美——而是追求"错了能被发现"。每个任务配可验证奖励信号，意味着训练过程中模型可以学会从失败中恢复，因为奖励信号会指出失败。

## 局限性

- M2 在传统知识基准（MMLU-Pro 81.8 vs Gemini 91.2, HLE 28.0 vs GPT 41.6）上仍有明显差距
- 全注意力架构在吞吐量上的代价在长上下文场景会越来越突出
- Self-evolution 目前仅在一个有限的 MLE bench 场景验证，还没到通用的 autonomous research level
- Windowed FIFO 的 W 参数选择依赖于经验（论文给出 0.3N），缺乏自适应策略
