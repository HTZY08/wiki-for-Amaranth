---
title: DeepSeek DSpark — 半自回归投机解码 + 负载感知验证调度
date: 2026-08-01
source: https://arxiv.org/abs/2607.05147
---

# DeepSeek DSpark — 半自回归投机解码 + 负载感知验证调度

**发布日期：** 2026-07-06（arXiv 2607.05147，DeepSeek-AI + 北京大学）
**来源：** https://arxiv.org/abs/2607.05147
**工程范式：** 把投机解码从"draft 质量算法"升级为"系统级吞吐优化问题"——算法与 serving 引擎协同设计

---

## 设计哲学

### 核心约束

DSpark 面对的生产矛盾：**并行 drafter 的 draft 速度快但 suffix decay 严重，自回归 drafter 的接受率高但 draft 延迟随块长线性增长**。而高并发 serving 系统中，验证预算的边际成本取决于实时负载——在轻负载下多验证几个 token 几乎免费，在重负载下每个被拒绝的 token 都在抢占其他请求的 batch 容量。

论文把问题拆成两个层次：
1. **质量层**：draft 块内 token 间缺乏依赖建模 → 多模态碰撞（"of course" 被生成成 "of problem"）
2. **系统层**：固定长度验证浪费算力 → 需要按请求动态裁剪验证长度

### 架构选择的权衡

| 约束 | 应对策略 | 放弃的选项 |
|------|----------|-----------|
| 并行 drafter suffix decay | 半自回归：并行 backbone + 轻量顺序 head | 纯并行（DFlash）的简单性 |
| 自回归 drafter 延迟线性增长 | 并行 backbone 承担主要计算，顺序 head 只注入局部依赖 | 纯自回归的高建模容量 |
| 固定验证长度浪费算力 | confidence-scheduled verification，按请求动态定长 | 静态阈值启发式 |
| 静态阈值忽略系统负载 | 硬件感知前缀调度器，用实时 SPS 吞吐曲线做全局吞吐最大化 | 每请求独立最优 |

---

## 关键架构决策

### 半自回归生成（Semi-Autoregressive Generation）

两个阶段：
- **并行阶段**：以 DFlash 为 backbone（MoE 层 + mHC + 128 滑动窗口注意力），单次前向生成 γ 个 draft logits。做了小修改：anchor token 本身作为第一个预测位置（γ 个输入 token 产生 γ 个 draft logits），减少计算量。
- **顺序阶段**：在 base logits 上加 prefix-dependent transition bias。两种实例化：
  - **Markov head**：只依赖前一个 token，低秩分解 B = W₁W₂（r=256 默认），存储和每步计算都小
  - **RNN head**：维护循环状态累积块内完整前缀历史，门控更新

关键洞察：顺序阶段必须极轻量（T_sequential ≪ T_parallel），使总 draft 延迟仍由并行阶段主导。draft 块长从 4 扩到 16 只增加 0.2%–1.3% 全轮延迟，却带来最多 30% 的接受长度提升。

### Confidence Head + Sequential Temperature Scaling

- confidence head 输出 c_k ∈ (0,1)，建模"给定块内前面 token 全部被接受时，位置 k 的 draft token 能通过验证"的条件概率
- 监督信号来自解析解：c*_k = 1 − ½‖p_draft − p_target‖₁（TV distance 与接受率的关系）
- **STS（Sequential Temperature Scaling）**：因为置信度是条件概率，联合概率是累积乘积 ∏cᵢ。用留出验证集从左到右逐位置 1D 网格搜索温度，最小化累积乘积的 ECE。原始模型过自信（ECE 3–8%），校准后降到 ~1%。这对调度器是必须的——调度器需要的是精确的绝对概率值，不只是排序。

### Hardware-Aware Prefix Scheduler

把验证长度选择形式化为**全局吞吐最大化问题**：Θ = τ·SPS(B)，其中 τ 是期望接受 token 数，SPS(B) 是引擎在 batch size B 下的吞吐曲线（启动时 profile 一次存成 cost table）。

- 因 a_{r,j}（前缀存活概率）随 j 单调不增，边际增益恰好是 a_{r,j}，所以排序后贪心可达全局最优
- **严格因果性**：贪心搜索在吞吐下降时立即 early-stop，保证 admission 决策不依赖未来 token，维持 lossless 保证（论文 Appendix A 给出了不 early-stop 会导致选择偏差的反例——输出分布从 (0.7,0.3) 偏到 (0.85,0.15)）

### 生产化适配（Section 5.2 — 系统与算法冲突的解决）

真实部署暴露两个矛盾：
1. SPS(B) 曲线实际是离散锯齿状，不是平滑单峰 → 单调性假设破裂
2. 动态变长验证与 CUDA graph replay / ZOS（Zero-Overhead Scheduling）冲突，ZOS 要求下一轮 batch size 在本轮完成前已知

解法：**异步化**。用两步前的 confidence 输出预测下一轮容量上限 K，当前步的候选仍按最新累计置信度严格排序，admission 变成动态 top-K 选择。历史预测只决定截断长度，不决定 token 排序 → 保持 lossless + 隐藏调度延迟。

### 训练目标与系统级训练优化

三损失加权：L = α_ce·L_ce + α_tv·L_tv + α_conf·L_conf（默认 0.1 / 0.9 / 1.0），位置权重 w_k = exp(−(k−1)/γ) 强调块前部。L_tv 直接最小化 draft-target 分布的 TV 距离（接受率代理）。

训练两大系统优化（HAI-LLM 框架）：
- **Hidden state communication**：目标模型全词表 logits（V≈10⁵）跨 worker 传输是带宽瓶颈 → 只传 LM head 前的 hidden states（O(d)），LM head 投影在 draft worker 本地按采样位置执行
- **Anchor-bounded sequence packing**：从训练序列采样固定数量 draft anchors，用 token 级 attention indices 打包成 dense batch，避免 padding 开销

---

## 关键结果

### 离线基准（accepted length τ，越高越好）

Qwen3-4B/8B/14B 目标模型上，相对提升：
- vs Eagle3（自回归）：**+30.9% / +26.7% / +30.0%**
- vs DFlash（并行）：**+16.3% / +18.4% / +18.3%**
- Gemma4-12B 上也一致领先，跨模型族泛化

### 消融洞察

- **"一点自回归走很远"**：2 层 DSpark 超过 5 层 DFlash 基线——顺序建模的参数效率远高于堆并行层
- 块长 γ=7 时 DSpark 相对 DFlash 提升 math 16% / code 15% / chat 18%；γ=15 时扩大到 30% / 26% / 22%
- 位置级分析：并行 drafter 在位置 1 有容量优势（深层网络），但后续位置快速衰减（code 0.87→0.78，chat 0.72→0.63）；DSpark 继承高初始接受率（math 0.93）同时缓解衰减
- 静态阈值扫描：chat 接受率从 45.7% 提到 95.7%（阈值升高时裁剪低置信 suffix），math 76.9%→92.5%，code 67.6%→92.0%
- RNN head 相对 Markov head 增益边际，仅在长块下明显 → 默认用 Markov head

### 生产部署（DeepSeek-V4-Flash/Pro preview，真实用户流量）

对比 MTP-1 生产基线（单 token drafter，历史上多 token drafter 会严格降低高并发吞吐）：

| 指标 | V4-Flash | V4-Pro |
|------|----------|--------|
| 匹配吞吐下每用户生成加速 | **60%–85%** | **57%–78%** |
| 中等 SLA（80 / 35 tok/s）聚合吞吐提升 | +51% | +52% |
| 严格 SLA（120 / 50 tok/s） | 基线接近运行边界，DSpark 名义 +661%（实质是扩展可达交互性前沿，非代表性倍率） | 名义 +406% |

负载动态：并发 <200（Flash）/ <150（Pro）时调度器分配 4–6 token 验证预算（基线固定 2）；并发升高后平滑收缩，低置信 token 在占用关键 batch 容量前被裁剪。

---

## 范式对比

- **vs MTP 家族（DeepSeek 自身演进）**：MTP-1 单 token 是保守选择——静态多 token drafter（MTP-3/5）在高并发下因过度验证严格降低聚合吞吐。DSpark 用置信度调度"安全解锁"了大块验证的潜力，是 DeepSeek 服务栈从 V3 时代 MTP 到 V4 时代 DSpark 的范式跃迁。
- **vs 静态阈值置信度验证（Huang et al. 2024 等）**：静态阈值在单请求下有效，但忽略系统负载。DSpark 把验证预算看作全局资源分配问题，负载感知是核心差异。
- **vs 树状投机解码（EAGLE-3 等）**：树验证增加验证 token 数、降低 serving 吞吐。DSpark 保持链式验证 + 动态裁剪，与高并发 serving 更兼容。
- **vs 纯并行 drafter（Medusa/PARD/DFlash）**：DSpark 是"并行骨架 + 顺序修正"的折中，论文用位置级条件接受率证明这种混合结构优于任一端。

---

## 社区评价

（HN/Reddit 无显著技术讨论帖——该论文 2026-07-06 上线，社区讨论热度集中于 DeepSeek-V4 GA 本身。以下为论文自身披露的定位信息）

- 开源承诺：DSpark checkpoints（V4-Flash/Pro preview）+ DeepSpec 训练仓库（含 Eagle3、DFlash、DSpark）一并发布
- 论文明确指出 limitation：draft 侧固定成本不可恢复——对低接受率的复杂 query，整块生成的 upfront 计算是浪费，未来可用 difficulty-aware early exiting 解决

---

## 可复用的工程经验

1. **把 serving 问题当系统问题而非算法问题**：投机解码的验证长度不是"每请求最优"，而是"全局吞吐最优"。用引擎 SPS 曲线做成本表，把验证预算变成可调度的资源。
2. **半自回归是性价比极高的折中**：2 层顺序修正即可超过 5 层纯并行。顺序 head 的延迟开销可控制在 1% 以内（batch 128 实测）。"一点顺序性走很远"。
3. **调度器对概率校准有硬需求**：排序型置信度（静态阈值）只要相对序正确，但吞吐优化需要绝对概率值。顺序温度缩放（STS）把 ECE 从 3–8% 压到 ~1%，是生产可用的关键一步。
4. **严格因果性有理论反例**：回顾式搜索会泄漏未来 token 信息导致分布偏置——不是工程瑕疵而是理论破坏。early-stop 或两步前预测的异步屏障是 lossless 的两种正确实现。
5. **与 CUDA graph / ZOS 兼容的异步化**：用历史预测定容量、最新置信度排序，既隐藏调度延迟又保持 rank-preserving，是"系统兼容性 vs 算法纯度"的典型工程解法。
6. **大模型训练的通信优化**：不传全词表 logits，传 hidden states + 本地投影，把跨 worker 通信降到 O(d)。anchor-bounded packing 用 attention index 避免 padding。
