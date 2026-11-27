---
title: Laminar — 把 RL 后训练里最后那只"--慢的乌龟"拆掉：轨迹级异步 + 权重当分布式服务
date: 2026-11-24
source: "https://arxiv.org/abs/2510.12633"
---

# Laminar: A Scalable Asynchronous RL Post-Training Framework

**发布日期：** 代码与工程发布 2026-11-24；论文 arXiv:2510.12633
**作者单位：** 香港大学（Guangming Sheng、Borui Wan、Chuan Wu）× ByteDance Seed（Yuxuan Tong、Wang Zhang、Chaobo Jia、Xibin Wu、Yuqi Wu、Xiang Li、Chi Zhang、Yanghua Peng、Haibin Lin、Xin Liu）
**来源：** https://arxiv.org/abs/2510.12633
**工程发布报道：** https://www.marktechpost.com/2026/11/24/bytedance-seed-laminar-async-rl-post-training-framework （2026-11-24）
**工程范式：** 不在算法层找突破，而是在数据面找。把 RL 后训练拆成四个互不阻塞的循环，用一层 CPU relay 把模型权重变成"随时可拉取的分布式参数服务"，再用 bin-packing 把长尾轨迹压到少数副本上——用系统工程把 GPU 空转吃掉。

## 设计哲学

论文开篇给的是一个极其具体的瓶颈量化：**在推理性任务里，生成阶段占总执行时间的最高 83.1%**（数据引自 DAPO/Yu et al.）。生成阶段之所以吃掉八成时间，是因为轨迹长度与环境延迟都是重尾分布——**99 分位轨迹长度可达中位数的十倍**（AIME 与代码沙箱延迟）。

这里有一个物理约束决定了"加卡不管用"：LLM 解码是 memory-bound 的，吞吐靠大 batch 撑着。长尾阶段只剩几条未完成轨迹时，decode batch 掉到个位数，而**解码一个极小的 batch 和 decode 一个 64 条的 batch 延迟几乎一样**。所以多买卡只会让更多卡一起空转。

已有的两条解法都被否掉：

1. **k-step 有界 staleness + 全局权重同步**：所有 rollout 每轮跟 actor 对齐一次，形成一个刚性的更新节拍。k 小则掩盖不住长尾，k 大则数据策略与训练策略偏离，损害收敛——k 成了必须手调的旋钮。
2. **Partial rollout（中途切权重）**：到点就打断所有进行中的轨迹，用新权重续写。长尾气泡是小了，但**一条轨迹变成由多个策略版本拼接**，带来 off-policy 误差，而且每次切换都要重新 prefill，长序列下这个代价是三次方量级的。

于是 Laminar 的选择是：**取消全局屏障，让每条轨迹按自己的节奏生成与消费**。代价是必须自己解决三件事——权重怎么同步、长尾怎么收、故障怎么不扩散。这三件事构成了全文的架构。

## 关键架构决策

### 1. 四循环全解耦

| 循环 | 职责 |
| --- | --- |
| Rollout loop | 驱动 agent 交互与环境调用，跨推理副本做生成 |
| Experience buffer（数据面） | 把"生产轨迹"和"训练消费"分开，按需供 batch |
| Training loop | 采样、算 advantage、做 off-policy 修正、发布权重 |
| Weight relay（权重面） | 训练器把权重推进每节点共享内存即返回；副本按自己的时间表拉取 |

关键是把**参数依赖**从"全局同步事件"降级成"一次可随时发生的读操作"。这时 staleness 不再是一个全局配置项，而是每条轨迹的**内在属性**：若轨迹在版本 K 下生成、完成时 actor 已到版本 M，则它的 staleness 就是 M−K。系统仍然限制最大 staleness（论文的对照实验里设到 4），但它不再是调度器的节拍器。

### 2. Relay：把权重同步做成分布式参数服务

- 每个 rollout 机器上一个 **CPU 进程**做 relay，不再是 NFS 或 Redis 这类存储中转（论文专门批评了用存储系统传权重的老路：模型还在 MB 级时还行，几十 GB 时延迟不可接受）。
- 训练器只把新权重交给**一个 master relay 就立即返回训练**，广播延迟被藏起来；master 重新分片后沿 **RDMA 流水线链式广播**下去。
- 论文给了广播延迟模型：`T(p,k) = M·T_byte + (p−2)·T_start + k·T_start + (p−2)M·T_byte/k`，并证明最优分片数 `k* = sqrt((p−2)·M·T_byte / T_start)`，总延迟由**带宽项 `M·T_byte` 主导**，对 relay 数量 p 近似不敏感（延迟项线性但系数极小，流水项只随 √p 增长）。这就是"链式广播可以扩到几千节点"的论证依据。
- 工程发布侧的说法（二手，见口径声明）：72B 模型推到 127 个 relay 用时不到 1.6 秒。

### 3. Repack：把长尾收拢，把副本放出来

- 触发条件两条：周期性检查（例如每 5 秒）发现副本困在长尾、KV cache 使用率掉到 idle 区；以及**每次全局 batch 权重更新之后立刻触发**，尽快把副本腾出来跑新版本的 on-policy 轨迹。
- 判据不是"还剩几条轨迹"，而是 **KV cache 利用率生命周期**：先爬升到阈值 C_max，维持平台期，最后随剩余轨迹减少而下降——下降段就是 idle 段。论文用 32B 模型、512 条轨迹、H800 TP=4 给出了这条曲线。
- 收拢被建模成 bin-packing：闲置 rollout = 待装物品，目标 rollout = 箱子，容量由 KV cache 上限 C_max 与 batch 上限 B 共同约束，目标是**最大化被释放的源副本数**、同时让搬移开销可忽略。
- 实测（32B、128 GPU、16 个 rollout）：生成吞吐 **+26%**，平均 KV cache 利用率 **71.6% → 82.2%（+14.8%）**，单次 repack 开销 **0.69 秒**，且不增加轨迹生成延迟。

### 4. 版本一致的轨迹（version-consistent rollout）

这是与 partial rollout 的正面分歧点：**Laminar 让每条轨迹在一个策略版本下跑完**，副本各自独立升级，没有全局换权重的关卡。好处是 prefix KV cache 可以完整保留，不需要反复 re-prefill。系统同时保留了版本混合的 partial 模式作为可选项，但默认路线是"轨迹内单一策略"。

### 5. 容错是设计的一部分，不是补丁

生产级 RL 任务动辄上千卡、跑数周到数月，硬件故障是必然事件。原有系统里一台 rollout 挂了，该节点上所有进行中的轨迹全部丢失——而复杂 agent 任务单条轨迹可能要跑几小时。

Laminar 的做法：heartbeat 发现故障 → 先在同一批 GPU 上重建副本，失败则整机驱逐 → **进行中的轨迹状态留在 partial response pool 里**，由 rollout manager 重定向到健康副本继续。训练器侧 checkpoint 对齐三样东西：模型状态、prompt 游标、已发布的权重版本号。

## 关键结果

### 测试床

128 台机器 / 共 1024 张 H800-80GB；机内 NVLink 400GB/s；机间 8×400Gbps；CUDA 12.6、PyTorch 2.7.1、NCCL 2.26.2、vLLM 0.9.0。

### 吞吐

- 端到端最高 **5.48×**（7B 档的相对增益区间为 1.12×–5.48×）。
- **最大集群规模下相对全部基线与模型尺寸平均 3.34×**。论文的解释是：verl、one-step staleness、stream generation 都被全局权重同步卡住，长尾一出现，加卡不再增加吞吐，而 Laminar 的吞吐随副本数继续线性走。

### 收敛

论文的收敛对照用 Qwen2.5-Math-7B 与 Qwen2.5-32B、GRPO 算法，Laminar 的最大 staleness 设为 4（AReaL 用其 Decoupled PPO 的建议值 4；stream generation 基线用 staleness < 1）。异步系统统一把 mini-batch 提到 2048 以稳定 off-policy 训练。

### SWE agent RL（来自工程发布侧，非论文实验章节）

Qwen3-Coder-30B-A3B-Instruct，在 SWE-rebench 上训练，SWE-bench Verified 全部 500 题、贪心解码：

| 配置 | 分数 | 样本数 | GPU 小时 |
| --- | --- | --- | --- |
| 基线模型 | 46.6%（233/500） | — | — |
| 对照峰值（step 150，64×H100） | 51.4% | 76.4k | 5,085 |
| Laminar 同分（step 320，64×H800） | 51.4% | 41.0k（−46%） | 1,450（−71%） |
| Laminar 峰值（step 400，64×H800） | 52.2% | 51.2k（−33%） | 1,843（−64%） |

**这张表有一个必须点出来的缺陷：对照组跑在 H100 上，Laminar 跑在 H800 上。** 硬件不匹配，所以"少 64% GPU 小时"里混进了卡型差异，不能当成纯系统收益。真正的系统收益应该看论文里同构集群的 5.48× / 3.34×。

## 范式对比

- **vs verl（同门，ByteDance Seed 参与）**：verl 默认同步，异步能力（fully async、1-step off-policy）标为实验性。Laminar 把异步做成默认路径，并自建了权重面与容错层。两者的关系更像"verl 提供算力后端，Laminar 提供集群级编排"——发布侧说 Laminar 就是 built on verl + Uni-Agent。
- **vs AReaL（清华 IIIS + 蚂蚁）**：AReaL 是完全异步 + Decoupled PPO，用算法修正 off-policy 偏差，staleness 建议值 4。Laminar 的路线是用**系统结构**（轨迹内单版本 + repack）而不是算法项去控偏差。前者是"接受偏差再用 PPO 修"，后者是"少制造偏差"。
- **vs partial rollout 系（Stream Generation、slime 等）**：那些系统的关键动作是"到点切权重"，Laminar 的关键动作是"到点换副本"。方向相反：一个改轨迹的策略归属，一个改轨迹的宿主机器。
- **vs 字节自家的另一条线**：9 月的 DSec（sandbox 基础设施，arXiv:2609.22978）解决的是"环境怎么大规模供给"，Laminar 解决的是"环境反馈回来之后 GPU 怎么不空转"。同一家公司在一个月内把 agent RL 的供给端与消费端各补了一块，方向一致：**把 agent 训练当数据中心问题，而不是当算法问题。**
- **vs MiniMax 的 Forge**：Forge 也是 agent-native RL + 调度优化（windowed-FIFO、prefix-tree merging），思路接近，但 Laminar 把"权重同步"单独做成一层可独立扩展的服务，并给了广播延迟的解析模型——这是更彻底的解耦。
- **vs 前沿实验室的闭源栈**：OpenAI / Anthropic / Google 的 RL 系统不公开；这一层的公开可比对象只有 verl / AReaL / slime / Laminar 四个 Apache-2.0 项目。Laminar 的差异点集中在权重面与容错，而非采样算法。

## 社区评价

- 发布侧的分析（MarkTechPost，11-24）给出的评价很平衡：优点是"更少样本、更少 GPU 小时拿到更高 SWE-bench 分"，缺点是"仓库刚开（launch 时 1 个 commit）、只有 vLLM 一种推理后端、分步异步 checkpoint 仍在做"。
- 最集中的技术质疑就是上面那条硬件错配：headline 对比混了 H800 与 H100。这一点在发布侧文章里被明确标为 "Worst"，不是外部吹毛求疵。
- 另一类讨论来自 RL infra 圈：轨迹级异步把"公平性"从全局调度问题变成局部装箱问题，代价是需要一个能精确感知 KV cache 生命周期的判据。有观点认为这个判据对模型尺寸与张量并行度敏感（论文的曲线是在 TP=4 上测的），跨配置迁移需要重新标定阈值。
- 未检索到第三方对 5.48× 或 SWE-bench 数字的独立复现。

## 可复用的工程经验

1. **先量清楚 GPU 时间花在哪，再动手。** "生成阶段占 83.1%"这一句决定了整篇论文的方向。没有这个数字，任何异步化都只是信仰。
2. **把全局屏障换成数据面缓冲。** 一旦轨迹生产与训练消费之间有一个按需供 batch 的缓冲区，staleness 就从"全局配置"退化成"每条轨迹的属性（M−K）"，调度器不再需要节拍器。这是本文最可迁移的一条。
3. **权重同步值得单独一层。** 用 NFS/Redis 传几十 GB 权重是历史遗留；一个 master relay + 链式 RDMA 广播、训练器交完就返回，能把广播延迟完全藏起来。而且广播延迟对节点数近似不敏感，这是它能扩到千卡的原因。
4. **长尾副本要"搬家"，不要"等待"。** 内存受限的解码里，小 batch 与大 batch 延迟接近——所以把散落在多个副本上的残余轨迹塞进少数副本几乎不增加延迟，却能一次释放大量 GPU。这是物理性质带来的免费优化，但前提是能准确判定"该副本已经 idle"（KV cache 生命周期阈值）。
5. **轨迹内单一策略 + 副本独立升级，比中途换权重便宜。** 反复 re-prefill 在长序列下是三次方代价；版本一致换来 prefix cache 的完整复用。
6. **容错要在架构层解决，不要在任务层重跑。** 上千卡跑数周，故障是常态。把进行中的轨迹状态存进 partial response pool、让健康副本接着跑，比"丢弃+重生成"便宜一个量级。
7. **效率宣称必须同构硬件对比。** 这张 SWE-bench 表的最大问题不是收益不真实，而是对照组卡型不同，导致"−64% GPU 小时"无法归因。任何效率类结论都该附测试床对照；跨卡型的比较只能作为方向性参考。
8. **早开源的项目要按"早期"读。** 1 个 commit、单一推理后端、异步 checkpoint 未完成——这些不否定架构，但意味着把它接进生产要自己补工程量。

---

**口径声明：** 论文侧数字（83.1% 生成占比、p99≈10× 中位数、5.48×、最大规模平均 3.34×、repack 的 +26% / 71.6%→82.2% / 0.69 秒、1024 卡测试床配置、广播延迟模型与 k* 推导、最大 staleness 4、收敛实验用 Qwen2.5-Math-7B/32B + GRPO）均取自 arXiv:2510.12633 正文。**SWE-bench Verified 那张表、三层栈划分（verl / Uni-Agent / Laminar）、"72B 到 127 个 relay < 1.6 秒"来自 MarkTechPost 对该项目工程发布（launch blog）的解读，未在论文实验章节中逐项核对。** 发布事件日期 2026-11-24 为 MarkTechPost 文章日期。开源协议 Apache-2.0、推理后端仅 vLLM、仓库早期状态亦据该报道。**未披露项**：relay 的 CPU 内存开销、repack 的 KVCache 迁移带宽成本、千卡规模下的具体故障率统计、vLLM 之外后端的支持时间表。
