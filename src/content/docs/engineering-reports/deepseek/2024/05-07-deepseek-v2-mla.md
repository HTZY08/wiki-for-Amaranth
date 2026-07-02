---
title: DeepSeek-V2 — MLA 架构首次提出，KV Cache 压缩 93.3%
date: 2024-05-07
source: arXiv 2405.04434
---

# DeepSeek-V2

**发布日期：** 2024-05-07
**来源：** arXiv 2405.04434
**工程范式：** 推理效率革命路线——不是追求更低的训练 loss，而是追求更低的推理成本。

## 设计哲学

DeepSeek-V2 面对的核心约束：MoE 模型虽然训练效率高，但推理时 KV cache 随序列长度和 batch size 线性增长，成为部署瓶颈。DeepSeek 的选择是重新设计注意力机制——不是优化 softmax 计算（Flash Attention 做的是这个），而是压缩 KV cache 的存储。

这是 DeepSeek 第一次展示其标志性的工程直觉：在别人优化计算的地方优化存储。MLA 的 KV cache 压缩率 93.3% 意味着同样硬件条件下可以服务 15x 的并发量或 15x 的上下文长度。

关键舍弃：MLA 增加了解码时的计算量（需要解压缩 latent vector），这在前向推理时有一些开销。但计算量和存储量的 trade-off 在长上下文场景下压倒性地偏向存储优化。

## 关键架构决策

### Multi-Head Latent Attention (MLA)

- **核心思想：** 将 Key 和 Value 联合压缩到一个低维 latent 向量 c_t^KV ∈ R^{d_c}（d_c << d_h × n_h）
- **解耦 RoPE：** RoPE 与 KV 压缩不兼容——单独用一个 multi-head query 和一个 shared key 承载位置编码，其余 KV 走压缩路径
- **KV cache 对比：** MLA 每 token 仅缓存 d_c + n_h × d_h^RoPE ≈ (9/2)×d_h，而 MHA 缓存 2×n_h×d_h。MLA 用约 4-14% 的 KV cache 达到超越 MHA 的性能
- **Query 压缩：** query 也做了低秩压缩（降低激活内存，不降低 cache）

### DeepSeekMoE（V2 版本）

- 每 MoE 层：2 共享专家 + 160 路由专家（6 活跃/token）
- Device-limited routing：每 token 最多发送到 3 个设备，控制通信开销
- 三种辅助损失：专家均衡 + 设备均衡 + 通信均衡
- Token-dropping：capacity factor 1.0，丢弃最低亲和度 token（约 10% 序列从不被丢）

### 训练配置

- 236B 总参 / 21B 激活，60 层，hidden 5120，128 attention heads
- 8.1T tokens 训练数据（中英，更多中文数据）
- AdamW，batch size 从 2304 逐步增加到 9216
- 基础设施：HAI-LLM + 16-way zero-bubble pipeline + 8-way expert parallelism + ZeRO-1
- 长上下文扩展：YaRN on decoupled RoPE key，4K → 128K，fine-tune 1000 steps at 32K

### 对齐（GRPO 首次提出）

- SFT：150 万实例（120 万有用 + 30 万安全），2 epochs
- RL：GRPO（Group Relative Policy Optimization）——不需要 critic 模型，advantage 从组内样本得分计算
- 两阶段训练：推理对齐（代码/数学）→ 人类偏好对齐（有用性+安全性）

## 关键结果

- 训练成本比 DeepSeek 67B dense 降低 42.5%
- KV cache 减少 93.3%
- 生成吞吐 >50K tokens/sec（8×H800），是 DeepSeek 67B 的 5.76×
- 推理时 FP8 量化 + KV cache 6-bit 量化

## 范式对比

vs GQA（Google，用在 LLaMA 2 等），MLA 用更极致的 KV cache 压缩。vs MQA（Google，所有 head 共享一个 KV），MLA 保持多头多样性的同时压缩 cache。MLA 是 DeepSeek 整个技术路线的基石——V3 用了升级版 MLA，V4 虽然放弃 MLA 但继承了对推理效率的极致追求。

## 可复用的工程经验

1. KV cache 是长上下文推理的主要瓶颈——优化 cache 比优化计算性价比更高
2. 解耦 RoPE 是使位置编码与 KV 压缩兼容的关键工程技巧
3. Device-limited routing（每 token 最多 3 个设备）是控制 MoE 通信成本的有效手段
4. GRPO 省掉了 critic 模型，大幅降低 RL 训练的资源需求
5. Token-dropping（capacity factor 1.0）虽然是激进策略，但在实践中只有约 10% 序列受影响——性价比极高
