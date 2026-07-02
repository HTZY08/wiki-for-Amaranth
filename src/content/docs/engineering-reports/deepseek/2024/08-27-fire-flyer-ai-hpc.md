---
title: Fire-Flyer AI-HPC — 软硬件协同设计，PCIe A100 集群逼近 DGX 性能
date: 2024-08-27
source: arXiv 2408.14158 (SC'24)
---

# Fire-Flyer AI-HPC

**发布日期：** 2024-08-27
**来源：** arXiv 2408.14158（SC'24 收录）
**工程范式：** 软硬件协同设计 — 用 PCIe A100（而非 SXM）+ 自研软件栈 + 密集网络拓扑，以 60% 成本实现 80% DGX-A100 性能。

## 设计哲学

Fire-Flyer 的核心理念可以概括为一句话：**AI 训练基础设施不应被 GPU 互联标准锁定**。DGX-A100 的 SXM 互联和 NVSwitch 虽然性能优异，但价格高昂（每节点价格约为 PCIe 方案的 1.67 倍）、功耗巨大（4200W vs 2500W）。Fire-Flyer 的设计者选择了一条更经济的路线：使用 **PCIe A100 GPU + 自研软件层补偿硬件短板**。

这个选择基于一个关键洞察：AI 计算需求的指数增长（每年 10×）远超硬件性能增长（FLOPs 每 2 年 3×、DRAM 带宽 1.6×、互联带宽 1.4×），因此**成本效益（cost-performance ratio）比绝对性能更重要**。Fire-Flyer 2 用 10,000 块 PCIe A100 GPU 构建了一个大规模集群，并通过 HFReduce、HaiScale、3FS 等软件创新弥补 PCIe 架构在通信带宽上的不足。

## 关键架构决策

### 节点设计：PCIe A100 + 单 NIC

每个节点配备 8× NVIDIA A100 PCIe 40GB GPU + 1× Mellanox CX6 200Gbps IB NIC。NIC 直连 CPU（独立的 PCIe root complex），不经过 PCIe switch。后续可选 NVLink Bridge（GPU 间 600 GB/s，用于需要高频通信的 LLM 训练）。

与 DGX-A100 的对比：
- TF32 GEMM: 107 vs 131 TFLOPS（83% 性能）
- 节点价格：60%
- 功耗：2500W vs 4200W（40% 降低）
- **成本性能比：1.38 vs 1.0**

### 两层 Fat-Tree 网络拓扑

Fire-Flyer 2 的网络采用两层 Fat-Tree（InfiniBand），分为两个 zone（各约 800 端口、~600 GPU 节点）。仅使用 **122 台交换机**——相比之下，相似的 DGX 集群需要 1320 台三层 Fat-Tree 交换机。存储服务器（180 节点）同时连接两个 zone，实现计算与存储的统一网络。

网络拓扑的关键创新是**计算-存储一体化网络（Computation-Storage Integrated Network）**，通过 InfiniBand Service Level（SL）/ Virtual Lanes（VL）实现流量隔离。静态路由策略确保跨 zone 任务一次仅并行一个，调度器保障通信效率。

### HFReduce：用 CPU 弥补 PCIe 通信瓶颈

HFReduce 是 Fire-Flyer 最具工程原创性的贡献。它的核心思想：**在 PCIe 架构下，用 CPU 做 allreduce 的中间节点比让 GPU 直接通信更高效**。

算法流程：
1. **节点内归约：** 异步 D2H 传输（小数据用 GDRCopy，大数据用 MemCpyAsync）→ CPU vector instructions 做 reduce-add
2. **节点间归约：** 双二叉树算法（Double Binary Tree）通过 RDMA verbs（ibverbs）实现，数据分块流水传输
3. **H2D 写回：** 使用 GDRCopy 直接写入同 NUMA 节点上的 4 块 GPU（比 MemCpyAsync 减少 3× 主机内存读取）

与 NCCL 在 PCIe 场景的对比：
- NCCL ring 每单位数据需要 2n-1 次传输（n 为 GPU 数），HFReduce 只需 1 次 D2H + 1 次 H2D
- 无 GPU kernel 开销——全部使用 Copy Engine，完全异步
- **186 MiB allreduce：HFReduce 6.3-8.1 GB/s vs NCCL 1.6-4.8 GB/s**
- 添加 NVLink 后：>10 GB/s

### HaiScale 分布式训练框架

HaiScale 是 DeepSeek 的自研训练框架，围绕 HFReduce 构建：

- **DDP：** HFReduce 作为 allreduce 后端，与反向传播计算重叠。VGG16 训练从 32→512 GPU 实现 **88% 可扩展性**，训练时间比 PyTorch DDP（使用 NCCL）缩短约 50%
- **流水线并行：** 配置 DP ranks 交错 PP 时序以避免 IB NIC 争用。LLaMa-13B 从 64→512 GPU 实现 **91% 并行效率**
- **MoE 训练：** DeepSeekMoE-16B 从 40→640 GPU 实现 76.14% 并行效率，320 GPU 时达 **92.92%**
- **FSDP（ZeRO-3）：** 优化内存管理，allgather/reduce-scatter 与计算重叠。GPT2-medium 从 16→128 GPU 实现 **95% 可扩展性**，训练时间比 PyTorch FSDP 缩短约 50%

### 3FS 分布式文件系统

自研的高吞吐分布式文件系统，基于 NVMe SSD + RDMA 网络。存储层由 180 节点组成，每个节点配备 16× PCIe 4.0 NVMe SSD（15.36TB）和 2× CX6 200Gbps 网卡。3FS 通过计算-存储一体化网络实现 GPU 对训练数据的高速直接访问。

## 关键结果

- **80% DGX-A100 性能，60% 成本，40% 能源节省**
- 网络交换机数量：122 vs 1320（DGX 三层 Fat-Tree）
- HFReduce vs NCCL：**通信带宽提升 2-4×**（6.3-8.1 vs 1.6-4.8 GB/s）
- DDP 可扩展性：32→512 GPU **88%**
- PP 可扩展性：64→512 GPU **91%**
- MoE 可扩展性：40→640 GPU **76.14%**（320 GPU **92.92%**）
- FSDP 可扩展性：16→128 GPU **95%**
- 成功训练了 **DeepSeek-V2（207B MoE）** 和 **DeepSeek-Coder-V2（236B MoE）** 等大模型

## 范式对比

| 维度 | Fire-Flyer 2（PCIe） | DGX-A100 集群 | Meta RSC |
|------|----------------------|---------------|----------|
| GPU 类型 | PCIe A100 × 10,000 | SXM A100 | A100 |
| 互联 | PCIe Gen4 + IB | NVSwitch + IB | IB/RoCE |
| 相对性能 | 80-83% | 100% | — |
| 相对成本 | ~50% | 100% | — |
| 功耗/节点 | 2500W | 4200W | — |
| 交换机数 | 122 | 1320 | — |
| 自研软件 | HFReduce+HaiScale+3FS | NCCL | NCCL+自研 |

Fire-Flyer 2 的范式意义在于：它证明**从成本和能效角度，PCIe 集群 + 深度软件优化可能是比 SXM 方案更可持续的大规模训练路径**。

## 可复用的工程经验

1. **PCIe 架构的通信瓶颈可以用软件突破**：HFReduce 通过 CPU 做中间节点，将 allreduce 效率从 NCCL 的 1.6-4.8 GB/s 提升到 6.3-8.1 GB/s（2-4×提升）。
2. **两层 Fat-Tree 是成本敏感场景的优秀折中**：122 台交换机 vs 1320 台，节省约 70% 网络成本，通过调度策略减少跨 zone 通信冲突。
3. **计算-存储一体化网络消除 IO 瓶颈**：存储和计算共享同一网络架构，避免传统 NAS/SAN 方案的额外跳数延迟。
4. **重叠通信与计算是分布式训练的核心工程杠杆**：DDP 和 FSDP 的可扩展性核心在于尽可能将 allreduce 与反向传播重叠，让通信时间"隐身"。
5. **成本性能比（cost-performance ratio）是比原始性能更好的设计指标**：1.38 的比率意味着每美元获得 1.38 倍 DGX 的计算量。
6. **系统级瓶颈排查比算法创新更重要**：HFReduce 的瓶颈被定位到 AMD EPYC Rome CPU 的 PCIe 根复合端口带宽不足（理论 12 GB/s，实际 ~8 GB/s）——这一发现直接指导了未来硬件选型。
