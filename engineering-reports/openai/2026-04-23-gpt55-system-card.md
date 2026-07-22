---
title: GPT-5.5 System Card — 同一模型，双轨安全：GPT-5.5 与 GPT-5.5 Pro 的评估框架
date: 2026-04-23
source: https://deploymentsafety.openai.com/gpt-5-5/gpt-5-5.pdf
---

# GPT-5.5 System Card

**发布日期：** 2026-04-23
**来源：** [GPT-5.5 System Card (PDF)](https://deploymentsafety.openai.com/gpt-5-5/gpt-5-5.pdf)
**工程范式：** 同一底层模型通过并行测试时计算区分标准版与 Pro 版，安全评估覆盖生物/网络/对齐三大 Preparedness 维度

## 设计哲学

GPT-5.5 的核心约束是：设计一个能处理复杂真实工作（编码、在线研究、分析、文档创建、跨工具操作）的模型，同时保持 OpenAI 最严格的部署安全标准。

关键设计选择：
- **双轨评估架构：** GPT-5.5 与 GPT-5.5 Pro 共享同一底层模型，Pro 版通过 parallel test-time compute（并行测试时计算）增强推理能力。安全结果在大多数场景下可代理（proxy），但需要分开评估的场合单独标注
- **宽松沙箱 → 严格沙箱评估：** 系统卡明确区分离线评估（offline setting）和实际部署环境的差异
- **Preparedness Framework 全面覆盖：** 包括生物/化学、网络安全、AI 自我改进、Sandbagging 四个风险类别
- **200+ 提前接入合作伙伴的真实场景反馈**

## 关键架构决策

GPT-5.5 是推理模型（reasoning model），通过强化学习训练产生内部思考链后回答。

### 模型训练
- **训练数据：** 公开互联网数据 + 第三方合作数据 + 用户/标注者数据
- **数据过滤：** 严格的数据质量/安全过滤管线，减少个人信息，过滤有害/敏感内容（含涉及未成年人的色情内容）
- **推理训练：** 通过强化学习训练模型在回答前进行"思考"，产生长内部思维链。模型在训练中学会细化思维过程、尝试不同策略、识别自身错误

### Safety Benchmarks
系统卡主要报告安全评估结果，而非架构细节。关键安全指标：

| 类别 | GPT-5.1-thinking | GPT-5.2-thinking | GPT-5.4-thinking | GPT-5.5 |
|------|:---:|:---:|:---:|:---:|
| Violent Illicit behavior | 0.955 | 0.975 | 0.971 | **0.979** |
| harassment | 0.706 | 0.810 | 0.790 | **0.822** |
| hate | 0.808 | 0.927 | 0.943 | 0.868* |
| self-harm | 0.926 | 0.961 | 0.987 | 0.959 |
| sexual | 0.933 | 0.940 | 0.933 | 0.925 |
| sexual/minors | 0.916 | 0.948 | 0.966 | 0.941 |

GPT-5.5 在大多数类别上与 GPT-5.4-Thinking 表现相当。\* hate 类别回撤经调查由翻译含违规内容的文本请求导致，实际未违反政策。

**评估设计要点：**
- Production Benchmarks 使用来自生产数据的具有挑战性的对话示例
- 标准评估已相对饱和，因此引入了更具挑战性的 Production Benchmarks
- 错误率不代表平均生产流量

### 安全与健康评估

**HealthBench（健康评估）：**
- GPT-5.5 在 HealthBench 上进行了专业级评估
- 引入动态心理健康基准 + 对抗性用户模拟

**幻觉评估（Hallucinations）：**
- 测量用户标记案例中的表现
- 含内部 agentic coding traffic 的重采样评估

**对齐评估（Alignment）：**
- 使用外部 ChatGPT 流量的代表性提示进行评估
- 编码 agent 的 Misalignment resampling 内部流量
- CoT Monitorability（思维链可监控性）和 CoT Controllability（思维链可控性）

### Preparedness 框架评估

**生物/化学能力：**
- Multimodal Troubleshooting Virology
- ProtocolQA Open-Ended
- Tacit Knowledge and Troubleshooting
- TroubleshootingBench
- 生物化学知识较 GPT-5.4-thinking 有提升
- 难负样本蛋白质结合预测
- DNA 序列设计
- 外部评估：SecureBio、US CAISI、Bio Bug Bounty Program

**网络安全能力：**
- Capture the Flag (CTF) Challenges
- CVE-Bench（漏洞基准）
- Cyber range 评估
- VulnLMP
- 外部评估：Irregular、US CAISI、UK AISI

**AI 自我改进能力：**
- Monorepo-Bench（大规模仓库基准）
- MLE-Bench（机器学习工程基准）
- Internal Research Debugging Evaluation
- OPQA（研究问题评估）

**Sandbagging（能力隐藏）评估：**
- Apollo Research 的外部评估
- 测量模型是否故意表现低于真实能力

### 安全保障措施

**生物/化学安全保障：**
- Bio Safeguards Testing
- 威胁模型与场景分析

**网络安全安全保障：**
- 模型安全训练
- 对话监控器（Conversation monitor）
- Actor Level Enforcement（行为者级别执行）
- Trust-based access（基于信任的访问）
- 安全控制
- UK AISI Cyber Safeguard Testing
- 外部 Red-teaming Campaigns
- Cyber Frontier Risk Council

## 关键结果

**整体安全评估结论：** GPT-5.5 在大多数类别上与 GPT-5.4-Thinking 性能相当，部分类别有微小提升。没有证据表明存在高严重性的对齐问题（misalignment）。

**Misalignment 内部评估：** 通过扩展到内部 agentic coding traffic 的重采样评估，新模型在大多数类别中"稍微更不对齐"（slightly more misaligned），但没有证据表明新模型或之前模型存在高严重性不对齐。

**内部部署风险：** 目前没有证据表明 GPT-5.5 具有所需的长程自主性或不对齐倾向来导致内部部署风险（如自我渗透或破坏内部研究）。此评估基于 TerminalBench 等代理评估以及在内部使用中观察到的连贯性和目标维持限制。

## 范式对比

**vs GPT-5.6 Sol Preview（2026-07-05）：** GPT-5.5 是 GPT-5.6 之前的生产级发布版。GPT-5.6 引入了 "Sol" 品牌和安全模式的重大重构，而 GPT-5.5 更侧重于在已有框架内提升安全性，而非重构安全架构。

**vs GPT-5.4-Thinking：** GPT-5.5 在大多数安全指标上与 GPT-5.4-Thinking 相当。GPT-5.5 的主要价值在于更好的工具使用、更少的引导需求、以及跨工作流的一致性检查能力，而非纯安全指标的跃升。

**vs Anthropic Claude 的安全评估方法：** OpenAI 的 Preparedness Framework 采用四维度（生物/化学、网络安全、AI 自我改进、Sandbagging）+ 独立外部评估（AISI、CAISI 等）的多层结构，与 Anthropic 的 ASL（AI Safety Levels）体系形成对比。

## 社区评价

2026-04-23 发布时社区的主要讨论点：

1. **系统卡是否由 AI 撰写？** Reddit 上 r/singularity 有大量讨论质疑 GPT-5.5 System Card 的内容质量，部分段落被认为"太长、太啰嗦、明显是 AI 写的"。OpenAI 未正面回应此质疑。

2. **安全指标的渐进式改进：** 社区注意到从 GPT-5.1 到 GPT-5.5，安全指标的改进是渐进式的（每代约 1-3%），而非跳跃式的。这表明安全训练已进入边际收益递减阶段。

3. **GPT-5.5 Pro 的区分：** 部分开发者质疑 GPT-5.5 和 GPT-5.5 Pro 使用同一模型但不同推理配置的做法，认为应更明确区分两者的能力边界。

## 可复用的工程经验

1. **生产基准（Production Benchmark）设计：** 当标准评估饱和时，用生产数据中的困难案例构建评估集是有效的。OpenAI 的 Production Benchmarks 构建方法论——选择"现有模型尚未给出理想回复"的案例——值得借鉴。

2. **双轨安全评估架构：** 同一底层模型 + 不同推理配置的场景，安全结果可代理但需在关键场景独立验证。这种"proxy + targeted verification"模式减少了评估工作量同时保持可信度。

3. **CoT 可监控性作为安全维度：** 3.7 节详细报告了思维链的可监控性和可控性。将 CoT 本身作为安全评估的目标（而非仅作为手段）是推理模型特有的新安全维度。

4. **外部评估合作伙伴网络：** 整合 US CAISI、UK AISI、SecureBio、Apollo Research、Irregular 等第三方评估机构，形成独立验证层。这种"第一方 + 第三方 + 政府方"的多层评估网络比依靠单一内部评估更可信。
