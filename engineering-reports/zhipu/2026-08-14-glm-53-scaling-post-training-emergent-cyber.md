---
title: GLM-5.3 — 纯 Post-training 扩展与涌现的网络攻防能力
date: 2026-08-14
source: https://z.ai/blog/glm-5.3
---

# GLM-5.3 — 纯 Post-training 扩展与涌现的网络攻防能力

**发布日期：** 2026年8月14日
**来源：** https://z.ai/blog/glm-5.3
**工程范式：** 同一基座模型只做 post-training 扩展——环境合成管线 + 大规模长程 RL（SAO/slime）驱动一切能力增长，包括超出预期的网络攻防涌现

## 设计哲学

GLM-5.3 的核心声明非常明确：**"Scaling post-training is all we did for GLM-5.3."** 它使用与 GLM-5.2 完全相同的基座模型，所有增益全部来自 post-training 阶段的扩展。

这背后是一个被反复验证的工程判断：当 agent 能力提升后，**post-training 的瓶颈从模型本身转移到任务环境**。一个有用的任务环境必须同时满足三个条件——可执行（executable）、可验证（verifiable）、接近真实专业工作（close to real professional work），并且需要大量环境而非少量手工搭建的样本。

智谱为此建立了端到端的环境合成管线：

- **研究 agent 采集**：从真实工作场景收集任务模式，转化为可运行的长程环境（多步依赖、隐藏状态）
- **judge agent 验证**：逐一尝试任务，确认其确实可解
- **合成 verifier**：在看不到参考解的情况下合成验证器；用 oracle / no-op / unsolved-state 三种检查过滤 reward shortcut，产出可直接训练的二元 reward

**放弃了什么：** GLM-5.3 没有改架构、没有换基座、没有做预训练扩展。它把全部筹码押在"环境规模 × RL 算力"这条轴上。另外，权重发布刻意延后两周（等安全评估和加固完成），是少见的"能力发布与权重发布分离"的做法。

## 关键架构决策

### Post-training 基础设施（沿自 GLM-5.2，持续扩展）
- **SAO with compaction**：长程任务 RL 算法，compaction 让增益在长 horizon 任务上保持而非只体现在短任务
- **slime 框架**：开源 post-training 框架，Megatron 训练 + SGLang rollout，训练/rollout/数据缓冲在同一 dataflow 上；数学、代码、沙箱、verifier、长程 agentic 环境都以"数据生成"方式接入，不需要改训练循环
- **训练-rollout 一致性**：新增 top-p mask、top-k 与全词表 OPD、R3 风格配置，训练与 rollout 路径全数值对齐——logprob 平均差异控制在 1e-7 量级（较此前设置减少 99.99%+）

### 环境扩展
- 任务从"编码练习"转向"真实专家工作单元"：部分任务相当于资深工程师数天的工作量
- 示例：ML 基础设施任务中，模型获得与工程师相同的工作环境（计算集群、存储系统、内部文档、代码库、实验结果），需要跨训练栈诊断瓶颈、实现优化、跑实验、交付可测量的端到端加速
- 环境合成仍需要相当量的人工介入（human-in-the-loop），全自动化是下一步

### 安全与披露基础设施
- **Z.ai Security Disclosure Ledger**：公开漏洞披露台账，记录受影响项目、严重性、CVE、漏洞存在时长

## 关键结果

### 编码（对 GLM-5.2 的增益）
| Benchmark | GLM-5.3 | GLM-5.2 |
|---|---|---|
| Terminal Bench 2.1 | 88.2 | 81.0 |
| Terminal Bench 3.0 | 28.3 | 4.6 |
| DeepSWE v1.1 | 66.9 | 46.2 |
| NL2Repo | 58.0 | 48.9 |
| ProgramBench Almost Solved | 19.0 | 9.5 |
| FrontierSWE | 78.1 | 67.5 |
| SWE-Marathon v1.1 | 42.5 | 19.4 |
| PostTrainBench | 39.8 | 31.7 |

- 内部 Z.ai Code Bench 较 GLM-5.2 提升约 50%
- 效率同样提升：Max effort 下 GLM-5.3 达 34.5%（约 75K 输出 token/任务），GLM-5.2 为 23.4%（96K）；High effort 下 GLM-5.3 31.4%（50K token）超越 Claude Opus 4.8 的 29.5%（120K token）

### 网络攻防（涌现能力）
| Benchmark | GLM-5.3 | GLM-5.2 |
|---|---|---|
| CyberGym | 84.5 | 77.2 |
| ExploitGym 2h / 6h | 105 / 130 | 29 / 39 |
| ExploitBench | 54.4 | 24.4 |

- CyberGym 84.5% 为当前该基准最优（领先 Mythos 5 的 83.8% 与 GPT-5.6 Sol 的 83.6%）
- **越往利用链（exploitation chain）深处，增益越大**：ExploitBench 较 GLM-5.2 翻倍以上
- 与安全团队合作实测：在 269 个真实项目中发现 2,436 个漏洞（1,097 个中高危），覆盖系统内核、操作系统、浏览器引擎、开源基础设施、Web 应用、网络协议；最老漏洞引入于 1981 年（45 年），平均漏洞潜伏 26.6 年

### 其他
- HLE w/ Tools 62.5（GLM-5.2 为 54.7）；Agents' Last Exam ALE-CLI 28.5（23.8）；GDPval-AA v2 1769（1508）
- Agentic：Toolathlon Verified 73.0（59.9）；AutomationBench 48.2（26.2）

## 范式对比

- **vs Qwen3.8-Max / DeepSeek-V4-Pro**：同属"8 月开源编码旗舰"竞争。GLM-5.3 的策略是*单轴极致*——不换架构，把 post-training 基础设施（环境合成 + RL 框架）当作核心竞争力。DeepSeek 的路线是架构侧持续推新（DSA 稀疏注意力、DSpark），Qwen 是家族化覆盖（2.4T 旗舰 + 27B 密集 + Flash-Next 架构预览）
- **vs 闭源前沿（Fable 5 / GPT-5.6 Sol）**：GLM-5.3 在 ExploitBench 等利用链深处仍落后闭源（54.4 vs 78.0/76.5），但差距在快速收窄——官方明言"能力增长最快的地方正是我们落后最多的地方"
- **安全范式差异**：把网络攻防能力作为*训练目标*引入（而非仅作为红队评估），并配套公开披露台账——这在开源模型中是罕见的主动姿态

## 社区评价

原文未提供 HN/Reddit 讨论数据，本分析未独立核实社区反应，暂不引用。可关注点：① Terminal Bench 3.0 从 4.6 → 28.3 的跃升是否真实反映通用 agent 能力（该基准偏难，分数普遍低）；② 权重延迟两周发布，需等第三方复测确认 benchmark 无泄漏。

## 可复用的工程经验

1. **瓶颈转移判断**：当模型 agent 能力进入某一水平后，post-training 的瓶颈从模型转向环境——优先投资"环境合成 + 自动验证"管线，而不是反复堆 SFT 数据
2. **Verifier 的防 reward hacking 三检查**：oracle 检查、no-op 检查、unsolved-state 检查——合成 verifier 通过这三关后才能作为可靠二元 reward
3. **训练-rollout 一致性是 RL 稳定性的隐藏变量**：logprob 差异压到 1e-7 量级（99.99%+ 缩减）换来的是对采样/训练/教师信号更细粒度的控制——比调 reward 更基础
4. **能力安全分离发布**：前沿能力模型先发布能力、延后发布权重（两周安全窗口），配套公开漏洞披露台账——攻防能力越强，越需要把"披露-修复"做成制度化流程
