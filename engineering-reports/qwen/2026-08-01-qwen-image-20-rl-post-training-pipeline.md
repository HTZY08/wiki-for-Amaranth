---
title: Qwen-Image-2.0-RL — 扩散模型的 RLHF + On-Policy 蒸馏后训练管线
date: 2026-08-01
source: https://arxiv.org/abs/2606.27608
---

# Qwen-Image-2.0-RL — 扩散模型的 RLHF + On-Policy 蒸馏后训练管线

**发布日期：** 2026-06-25（arXiv 2606.27608，Qwen 团队）
**来源：** https://arxiv.org/abs/2606.27608
**工程范式：** 用"任务特化 RL 教师 + On-Policy 蒸馏统一"替代"多奖励联合 RL"——规避扩散模型多目标优化的 seesaw 效应

---

## 设计哲学

### 核心约束

Qwen-Image-2.0-RL 面对的约束：**监督训练的扩散模型优化的是 denoising score matching 目标，不直接反映人类审美偏好**（构图和谐、纹理、提示忠实度、风格连贯）。RLHF 在 LLM 上已验证有效，但扩展到扩散模型有三个独特挑战：

1. **奖励信号**：T2I 生成和图像编辑是两个根本不同的任务——全局美学 + 提示忠实度 vs 细粒度身份保持，需要复合的、任务感知的奖励设计
2. **规模化**：已有 RL 框架（Flow-GRPO 等）主要在 LoRA 微调设置下验证；多奖励信号、多任务类型、全参数训练的现实场景未被探索
3. **部署**：任务特化的 RL 策略必须合并成单一模型而不牺牲各任务质量——多奖励联合 RL 有 seesaw 效应（一个任务变好另一个变差）

### 架构选择的权衡

| 约束 | 应对策略 | 放弃的选项 |
|------|----------|-----------|
| 单一奖励无法覆盖多质量维度 | VLM 复合奖励：T2I 三层（alignment/aesthetic/portrait）+ 编辑两层（instruction/face ID） | 单一奖励模型的简单性 |
| 多奖励联合优化冲突 | 任务特化 RL 教师 + On-Policy 蒸馏（OPD）合并 | Mix-RL（混合数据单模型联合 RL） |
| pairwise 奖励训练信息量不足 | pointwise 绝对评分范式 | pairwise Bradley-Terry |
| CFG 在 RL 中的不稳定 | hybrid CFG：rollout 用 CFG、训练目标不用 | 全程 CFG / 全程无 CFG |
| 全 timestep 训练导致 reward hacking | 只训练 rollout 的 timestep 子集，偏重高噪声段 | 全部 40 步训练 |

---

## 关键架构决策

### VLM 复合奖励模型

- **训练范式**：pointwise 绝对评分（5 点 Likert 回归）优于 pairwise（Bradley-Terry）——绝对分数编码"有多好"而 pairwise 只编码"哪个更好"。RL 训练用 pointwise 奖励生成的图在视觉质量和伪影控制上显著更好。奖励输出为离散分数集 {1,2,3,4,5} 上的期望。
- **T2I 三层奖励**（分层设计，底层失败封顶）：
  1. **Alignment reward**：语义对应（对象存在/数量、属性正确、空间关系、动作姿态），不评价美学
  2. **Aesthetic reward**：构图平衡、光照真实、纹理保真、艺术连贯
  3. **Portrait reward**：面部吸引力、身份保持细节、皮肤/头发纹理真实，显式检查手指数量等常见失败模式
- **编辑两层奖励**：
  1. **Instruction-following reward**：VLM 接收（源图，指令，输出图）三元组，把指令分解为核心/非核心需求按结构化 rubric 评估
  2. **Face identity consistency reward**：model-based embedding 级身份打分器，弥补 VLM 检测不到细微面部身份漂移的缺陷

### GRPO-based RL 训练框架

- **Flow-GRPO 基础**：把 flow matching 的 ODE 生成等价为随机采样器（SDE），使 GRPO 的 importance sampling ratio 可计算
- **多奖励 advantage**：A = Σ w_k·(R_k − μ_k)/σ_k，per-prompt-group 归一化——保证复合奖励对绝对尺度不变，防止某一维度数值范围主导
- **Hybrid CFG 策略**（三方案对比后选定）：
  - 全程 CFG → 训练不稳定，最终图像崩塌
  - 全程无 CFG → 奖励稳步提升但模型逐渐丢失风格化能力和世界知识（base 模型依赖 CFG 表达预训练知识）
  - **rollout 用 CFG + 训练目标排除 unconditional 分支** → 稳定性 + 保留完整生成能力 + 降计算开销
- **异步奖励管线**：奖励模型是远程 API，同步等待会阻塞训练 → 后台线程异步提交图像、跨 rank 同步分数、per-prompt-group 归一化算 advantage，几乎完全隐藏奖励延迟
- **Timestep 子集训练**：40 步 ODE solver 全步训练导致快速 reward hacking，只训练子集且偏重高噪声段（t 接近 1，决定全局结构和语义布局）
- **Prompt curation**：用奖励模型过滤 prompt 池——只保留 intra-group reward range 超过阈值的 prompt（奖励全高或全低的 prompt 训练信号弱）
- **Per-category reward calibration**：prompt 按语义类别（portrait/landscape/typography/general）分配不同奖励权重向量，防止收敛到单一风格

### On-Policy Distillation（OPD）

- **动机**：任务特化 RL 教师（T2I 教师 + 编辑教师）各自最优，但部署需要单一模型
- **目标**：学生在自己的推理轨迹上匹配教师 velocity（trajectory-level velocity matching），从 W₂ 距离上界推导——最小化 Σ‖v_θ(x_tn) − v_θ*(x_tn)‖²
- **多教师动态激活**：每 batch 按任务类型选择教师，只加载活跃教师到 GPU，非活跃教师 offload 到 CPU——多大规模教师训练不按比例增加显存
- **CFG 处理**：教师原本用 CFG 训练，OPD 中教师 velocity 预测用 CFG、学生不用；蒸馏完成后 CFG 再集成进学生模型
- **对比 Mix-RL**：混合数据联合 RL 强迫模型同时满足竞争目标 → 次优权衡。OPD 分解式训练 + 蒸馏合并，规避 seesaw 效应，并消除奖励模型依赖

---

## 关键结果

### Qwen-Image-Bench（Q-Judger，80 位专业艺术家标注 130K+ 对）

| 模型 | Quality | Aesthetics | Alignment | Real-world Fidelity | Creative Gen. | Overall |
|------|---------|-----------|-----------|---------------------|---------------|---------|
| Qwen-Image-2.0-Base | 52.29 | 57.10 | 57.64 | 47.54 | 58.22 | 55.23 |
| **Qwen-Image-2.0-RL** | **54.39** | **58.67** | **59.28** | **51.83** | **64.94** | **57.84** |

- Overall +2.61（55.23 → 57.84），五个支柱全部提升
- 最大增益：**Creative Generation +6.72**、Real-world Fidelity +4.29
- 对比同业：超过 Seedream 5.0（57.22），低于 GPT Image 2（64.69）、Nano Banana 2.0（59.82）、GPT Image 1.5（59.65）——与 Nano Banana Pro（59.45）差距 1.61

### Human Preference Arena（用户匿名投票 Elo）

- T2I arena：1115 → **1193（+78）**，八个子类全部提升，最大增益 3D Modeling（+93）和 Photorealism（+91）
- Image edit arena：1256 → **1349（+93）**

### 定性结论

- Qwen-Image-2.0-Base → Mix-RL → OPD 质量递进：RL 提升纹理/构图/真实感，OPD 进一步超越 Mix-RL
- 编辑场景：OPD 模型面部身份保持和指令跟随精度最好；Mix-RL 在复杂指令下仍有身份漂移或不完整编辑

---

## 范式对比

- **vs Flow-GRPO / GRPO-Guard / DiffusionNFT（现有扩散 RL 框架）**：这些方法在 LoRA 或单奖励场景验证；Qwen-Image-2.0-RL 是全参数、多奖励、跨任务的大规模工程化——hybrid CFG、异步奖励、prompt curation、per-category calibration 都是规模化时的新问题
- **vs 直接 Mix-RL（多奖励联合训练）**：论文核心范式主张——任务特化 + OPD 合并严格优于联合训练。T2I 和编辑的奖励维度冲突（美学 vs 身份保持）是 seesaw 的根源，OPD 用"各自最优再蒸馏"绕开
- **vs 传统图像奖励（CLIP / ImageReward / HPSv3 / PickScore）**：这些是回归式标量预测器；Qwen 用 VLM + CoT 的 token 预测范式 + pointwise 绝对评分，信息量更丰富
- **vs 同期 Flow-OPD / DiffusionOPD**：两个并发工作只做单奖励 T2I 教师合并；Qwen 按任务类型特化教师（T2I vs 编辑），并从 W₂ 上界推导目标

---

## 社区评价

（HN/Reddit 无显著技术讨论帖——该论文 2026-06-25 上线，且 Qwen-Image 系列社区关注集中于 base 模型的可用性。以下为论文自述定位）

- 论文强调 OPD 的三个工程收益：规避跨任务优化冲突、消除奖励模型依赖（部署时不需要 RM）、多教师显存管理（动态激活/offload）
- 局限未在论文中单独列节，但可从方法推断：奖励模型质量直接决定 RL 上限；40 步 ODE 采样成本高；portrait 奖励依赖专门数据集

---

## 可复用的工程经验

1. **pointwise 绝对评分 > pairwise 偏好**：绝对分数携带"有多好"的校准信息，pairwise 只携带"哪个好"。对同一 VLM 架构、同一数据池，pointwise 训练出的奖励模型驱动的 RL 结果视觉质量显著更优。
2. **CFG 的混合策略是扩散 RL 的稳定器**：全程 CFG 训练崩塌、全程无 CFG 丢失预训练知识（风格、名人脸、世界知识）。rollout 用 CFG、目标排除 unconditional 分支，是"稳定 + 保知识"的甜点。
3. **防 reward hacking 要控训练信号**：全 timestep 训练几轮就退化——只训练 rollout 子集并偏重高噪声段（结构/布局由高噪声步决定）。
4. **多奖励必须 per-group 归一化**：不同奖励尺度（1-5 vs embedding 距离）直接加权会让数值范围主导；per-prompt-group 的 z-score 归一化保证尺度不变性。
5. **异步奖励管线规模化关键**：奖励模型是远程 API，同步等待会阻塞训练循环。后台异步提交 + 跨 rank 同步，几乎完全隐藏奖励延迟。
6. **任务特化 + 蒸馏 > 联合优化**：竞争目标（美学 vs 身份保持）联合优化必然 seesaw。先各自 RL 最优、再 OPD 合并（学生轨迹上匹配教师 velocity），既保留各任务质量又去掉奖励模型依赖。
7. **prompt 质量决定 RL 上限**：intra-group reward range 过滤掉信号弱的 prompt；按语义类别分配奖励权重防止单一风格收敛。
