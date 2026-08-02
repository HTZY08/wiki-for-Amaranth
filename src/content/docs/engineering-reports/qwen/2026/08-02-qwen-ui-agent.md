---
title: Qwen-UI-Agent — 真实设备中心的 Foundation GUI Agent
date: 2026-08-02
source: https://arxiv.org/abs/2607.28227
---

# Qwen-UI-Agent — 真实设备中心的 Foundation GUI Agent

**发布日期：** 2026年7月底（arXiv 2607.28227）
**来源：** https://arxiv.org/abs/2607.28227
**工程范式：** 环境即能力边界——把 GUI Agent 的开发重心从模拟 benchmark 整体迁移到真实设备运行时，用"真实设备数据飞轮 + 混合 GUI/CLI 动作空间 + 万级并发在线 RL"把 27B 模型推到移动端闭源前沿模型之上

## 设计哲学

核心约束：现有 GUI Agent 在模拟 benchmark 上分数很高，但真实设备上的应用功能、UI 布局、权限弹窗、网络中断、CAPTCHA 等环境不确定性使模拟训练的模型大面积失效。Qwen 团队（MAI-UI Team, Alibaba）识别出六条关键转变：

1. 从模拟环境到真实设备执行——模拟与真实之间的鸿沟在移动端尤其严重
2. 从孤立域到跨域跨平台工作流——真实任务横跨手机、电脑、Web
3. 从纯 GUI 动作到 GUI+CLI 混合与批处理动作——结构化工作用 CLI 比视觉点击高效一个数量级
4. 从短程任务到可靠长程任务——需要持续的规划、状态跟踪、中间验证、错误恢复
5. 从人工密集型训练管线到 AutoResearch 式自动化——任务生成、环境构建、验证器合成、失败分析全部 agent 化
6. 从被动执行到主动服务——手机通知是"何时该主动介入"的高价值信号源

设计选择：**环境是系统的一等公民**。团队没有先训模型再适配环境，而是先建 100+ 物理设备、150+ 应用的真实设备运行时，用健康感知调度器管理设备/应用/账号/网络/显示的可用性，再用虚拟屏幕机制把单台物理机拆成多路并行执行环境（rollout 吞吐提升约 20×）。

放弃了什么：
- 放弃"一个 benchmark 一个专用模型"的路线，坚持一个模型覆盖 mobile/computer/web/DeepSearch 四域
- 放弃人工逐条标注任务和验证（成本不可扩展），改用 agent 合成 + VLM 判定 + AutoJudge 多数投票
- 放弃完全由 GUI 完成所有交互的纯净性，接受 CLI 作为一等动作类型（OSWorld 轨迹中 CLI 占比 40.7%–55.1%）

## 关键架构决策

### 统一动作空间：GUI + CLI + API + ask_user

- GUI 动作：click / double_click / long_press / type / open / drag / system_button / wait
- CLI 动作：cli_command 直接执行 bash（VM 内经非交互 shell，返回 stdout/stderr/exit status）
- API 动作：api_call 调用外部服务（如搜索 API）
- 控制动作：ask_user（敏感操作前请求确认）、terminate
- **批处理**：一个决策步可以输出 K>1 个有序动作序列（平均 batch 3.1 个 primitive actions），相邻动作中间状态可预测时不再等环境反馈，显著压缩 observation-reasoning-execution 循环

### 环境基础设施：沙箱 + 真实设备双轨

- 沙箱：MobileWorld 重建到 redroid（容器化 Android，无 QEMU/KVM 嵌套），OSWorld VM 扩展 bash 执行，Playwright/Chromium 浏览器运行时（每 episode 全新 BrowserContext），DeepSearch 用 Serper + Jina Reader
- 真实设备：100+ 物理设备 × 150+ 应用，健康感知调度器维护设备黑名单，虚拟屏幕让单机多会话并发，VLM judge 区分任务成功/模型失败/环境失败
- 统一环境接口：acquire / reset / step / evaluate / tear_down / release 生命周期，坐标归一化 + 中间表示做平台适配

### 训练策略：SFT → Action RL → Online RL 三级

**SFT（域条件专家 + 模型合并）**：每个域训一个专家（主要用本域数据 + 受控跨域混合），再把专家 checkpoint 合并为统一模型。同时用"起始模型自己能解对的问题"（in-distribution data）保护通用能力——比用难题做能力保留更有效。长轨迹用滑动窗口训练（窗口 n=5、步进 4、单步重叠），每个后续窗口监督 4 个新动作，重叠步 loss 屏蔽，避免相邻动作高度重叠的上下文被重复处理。

**Action RL（修正重复性动作错误）**：识别六类跨应用共现的错误模式——易混元素定位、排序/排名误读、数量与多目标不完整、提前完成（准备完结果但没执行最终状态变更动作）、重复动作循环、长尾动作选择失败（该用 open/ask_user/long_press 时回退到 click）。针对这些模式构造定向数据（历史轨迹挖掘 + agent 主动探索环境补稀有模式），reward 公式：

$$r_t = F_t(w_{type} C_t + w_{arg} C_t Q_t - \lambda_{sens} S_t - \lambda_{rep} L_t)$$

（F=格式有效性，C=动作类型正确性，Q=参数质量，S=敏感动作惩罚，L=重复惩罚）。训练中观察到 token 熵下降和推理链缩短，故加熵正则 + 推理长度上下界防策略坍缩。

**Online RL（长程决策，verifier-guided GRPO）**：约 10,000 个经自动合成 + 执行验证的 task–verifier 对。GRPO 组内相对优势，terminal verifier 给二元结果 reward。**模型自适应课程**：中等成功率任务进 active pool 拿满 rollout 预算，当前不可解任务留 monitoring pool 用小预算探测，一旦开始出成功 rollout 就晋升——防止"太难直接删"错过任务进入学习前沿的时机，也防止已掌握任务退化后无人监控。

### Harness 层：主动服务 + 跨平台执行

- 主动服务基于手机通知：事件解析器 → affair（持久化的"正在进行中的现实事务"抽象）→ affair 级推理 → 任务生成（评估紧迫性/后果/证据/省用户力）→ 低风险预执行 → 决策就绪提案，支付/改签/发消息等高后果操作保留用户确认
- 跨平台：OpenClaw 式 planner + 设备寻址动作 + 共享执行状态，独立子任务并行（虚拟屏幕隔离），GUI/CLI/API 混合执行，移动子任务跑在虚拟屏上不阻塞用户本人使用设备

### 评测：AutoJudge 轨迹级判定

真实设备无法用确定性 state verifier（第三方 App 不暴露内部状态）。AutoJudge 用 5 个独立 VLM judge 多数投票判定 pass / failed / env_error，env_error 从分母剔除。在 666 条轨迹上与人类专家标注的 exact-match 准确率达 92.8%。

## 关键结果

**移动端（MobileWorld 117 任务，50 步预算）：** Qwen-UI-Agent-27B 82.1%，超 GPT-5.6 Sol（70.1%）12.0pp、Claude Opus 4.8（67.5%）14.6pp、Seed 2.1 Pro（73.2%）8.9pp；最强专用 GUI 基线 GUI-Owl-1.5-32B（43.9%）+38.2pp。100 步预算下 27B 升至 85.5%。

**真实设备（MobileWorld-Real 409 任务/104 App / 7 域）：** 92.2%，超 Seed 2.1 Pro（88.7%）、Gemini 3.1 Pro（86.2%）、GPT-5.6 Sol（85.4%）。AndroidDaily 97.5%，第一。35B-A3B 变体 87.4%/93.9%，每 token 仅激活 3B 参数。

**电脑端：** OSWorld-Verified 79.5%（第二，仅次 Opus 4.8 83.4%）；OSWorld-v2 partial 40.0% / binary 13.9%，binary 超 GPT-5.5（13.0%）0.9pp，partial 超 MiniMax M3 17.7pp、Qwen 3.7 Plus 18.5pp，且每任务仅 135.8 步（MiniMax M3 326.7 步）。

**浏览器与 DeepSearch：** WebArena 73.6%（所有对比模型第一，超 Opus 4.8 1.7pp、GPT-5.5 4.1pp；人类 78.2%）；BrowseComp 64.1%、BrowseComp-ZH 75.0%（第二，超 Qwen3.5-397B-A17B）。

**GUI grounding：** ScreenSpot-Pro zoom-in 81.5%（第一）、ScreenSpot-V2 97.5%、MMBench-GUI L2 92.6%、OSWorld-G-Refined 78.5%、UI-Vision 70.0%（均第一或最佳）。

**通用/agentic 能力保留：** MMLU-Pro 86.5、IFEval 90.2 与 Qwen3.5-27B 持平；Terminal-Bench 2.0 50.1（base 41.1）、Claw-Eval 73.5（base 66.9）、BFCL-v4 74.2——GUI 后训练反而增强 agentic 能力，同时远优于专用 GUI 模型（UI-Venus/GUI-Owl 等多数低于 10）。

**CLI/batch 行为：** OSWorld-Verified 上 CLI 占 40.7% 动作（92.0% 任务用过）、batch 占 39.6%；OSWorld-v2 上 CLI 55.1%、batch 41.6%。batch 中 GUI-only 65-76%、CLI-only 13-15%、混合 11-20%。

**Action RL 效果（五类错误模式专项集）：** 易混元素 72.8→79.1、排序 76.6→80.4、多目标 80.0→84.4、提前完成 81.0→86.2、重复循环 72.9→82.4。

## 范式对比

| 维度 | Qwen-UI-Agent | 主流闭源模型（Opus/GPT/Gemini/Seed） | 专用 GUI 模型（GUI-Owl/UI-Venus 等） |
|------|--------------|--------------------------------------|--------------------------------------|
| 训练重心 | 真实设备运行时 + 数据飞轮 | 通用能力为主，GUI 为附属 | 模拟 benchmark 专项优化 |
| 动作空间 | GUI+CLI+API 混合 + batch | 主要 GUI（部分有浏览器/终端工具） | 纯 GUI 单步 |
| 规模 | 27B dense 打到闭源前沿 | 数百 B~T 级 | 2B-32B |
| 评测 | AutoJudge 轨迹级（真实设备） | 官方 benchmark + 自评 | 模拟 benchmark |

关键差异：闭源前沿模型（如 Qwen 3.7 Plus 397B-A17B）在真实设备上失败率高，论文行为分析显示失败根因集中在训练经验缺失——UI 误读 24.7%、探索失败 19.5%、弹窗干扰 18.2%、错误动作循环 14.3%——这些恰恰是"干净的模拟器"刻意排除的现象。Qwen-UI-Agent 用真实设备训练数据直接覆盖这些分布。

## 社区评价

（HN/Reddit 上的讨论未在此次扫描中独立核实，暂不引用外部评价。可观察的信号：论文将 27B 参数模型在移动端全面压过 1T 级闭源模型，这一"规模逆袭"的组合（真实设备 + 混合动作 + 在线 RL）是 GUI Agent 领域 2026 年下半年的核心话题。）

## 可复用的工程经验

1. **模拟器刻意排除的干扰正是真实世界的主要失败源**——弹窗、占位符误读、滑块超调。如果目标域有 sim-to-real 鸿沟，把真实设备纳入训练分布比调大模型更直接。Qwen 3.7 Plus 的失败分析表（Table 10）可作任何 GUI Agent 团队的失败模式 checklist。
2. **CLI 是搜索空间缩减器，不是替代 GUI 的捷径**——模型用 CLI 把多张图片拼成 contact sheet 一次目检、用脚本批量处理结构化数据，再用 GUI 做最终验证。混合动作空间 + batch 让长程任务步数减半以上（vs 单步模型 326.7→135.8 步）。
3. **Action RL 与 Online RL 分层**：动作级 reward 修局部错误（类型/参数/敏感/重复），轨迹级 verifier 修延迟后果。先做动作级再上在线 RL，避免在线 RL 直接被高频低质错误淹没。
4. **模型自适应课程胜过固定难度过滤**：全失败/全成功的任务在 GRPO 组内相对 advantage 下没有学习信号，但"现在学不会"不等于"永远学不会"。用 monitoring pool 小预算探测学习前沿，比一刀切删难任务更高效。
5. **AutoJudge 五 VLM 多数投票 + env_error 单列**是真实设备评测的可复制方案——第三方 App 无程序化验证器时，轨迹级判定 + 环境错误剔除让结果可复现且噪声可控（92.8% 与人类一致）。
6. **in-distribution 数据保留通用能力**：用"起始模型自己能解对"的样本做能力保留，比喂难题更有效——难题把优化信号引向能力获取，与 GUI 训练目标竞争。

> 交叉引用：与 MAI-UI (arXiv 2512.22047) 一脉相承；与 MiniMax M3、Kimi K2.6 的 OSWorld 对比见本目录 minimax/、moonshot/ 对应分析。
