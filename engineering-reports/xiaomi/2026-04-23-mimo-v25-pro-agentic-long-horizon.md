---
title: MiMo-V2.5-Pro — 长程代理任务的 MoE 放缩法则
date: 2026-04-23
source: https://mimo.xiaomi.com/mimo-v2-5-pro
---

# MiMo-V2.5-Pro — 长程代理任务的 MoE 放缩法则

**发布日期：** 2026-04-22（模型发布）/ 2026-04-27（博客）
**来源：** https://mimo.xiaomi.com/mimo-v2-5-pro | https://huggingface.co/XiaomiMiMo/MiMo-V2.5-Pro
**工程范式：** 延续 MiMo-V2-Flash 的混合注意力 + MoE + MTP 架构，通过参数量放大（1.02T/42B）和三阶段后训练（MOPD）将 agentic 长程任务能力推向新层级

## 设计哲学

**核心约束：** 在保持经济推理成本的前提下，将 agentic 长程任务（千级工具调用、百万级 token 上下文）的能力推向 frontier 水平。

**架构选择：**
- 参数量从 310B/15B（Flash）放大到 1.02T/42B，路由专家数从 256 增至 384
- 延续 V2-Flash 已验证的混合注意力（6:1 SWA:GA） + GQA + MTP 结构，不做架构创新，走 scale-up 路线
- 三阶段后训练（SFT → Domain-Specialized RL → MOPD）是核心差异化竞争力——通过多教师蒸馏将不同领域的专长合并到单一模型

**放弃了什么：**
- 放弃了极致的推理效率（Flash 定位）；V2.5-Pro 更侧重 agentic 长程能力而非单次推理速度
- 未采用 encoder-free、线性注意力等激进方案，选择了已有工程验证的路线
- 未发布 arXiv 正式技术报告（仅有 HuggingFace 模型卡和产品页），技术细节披露不如 Flash 完整

## 关键架构决策

### 注意力机制

- **混合注意力**：60 层 SWA（window=128） + 10 层 GA，6:1 比例（Flash 为 5:1）
- **目的**：SWA 将 KV cache 减少约 7×，GA 维持全局信息流通
- **可学习的 attention-sink bias**：缓解长上下文中的注意力坍塌
- **GQA**：128 注意力头，8 KV heads（QK dim 192 / V dim 128）

### MoE 设计

| 参数 | V2.5-Pro | V2-Flash | V2.5 |
|------|----------|----------|------|
| 总参数量 | 1.02T | 309B | 310B |
| 激活参数量 | 42B | 15B | 15B |
| 隐藏维度 | 6144 | 4096 | 4096 |
| 层数 | 70 (1 dense + 69 MoE) | 48 (1+47) | 48 (1+47) |
| 路由专家数 | 384 | 256 | 256 |
| 每 token 专家 | 8 | 8 | 8 |
| MoE 中间维度 | 2048 | 2048 | 2048 |

### 训练策略

- **预训练**：27T tokens，FP8 混合精度，原生 32K 序列长度
- **上下文扩展**：可达 1M tokens
- **后训练（三阶段）**：
  1. **SFT**：建立基础指令跟随能力
  2. **Domain-Specialized RL**：多个教师模型各自在特定领域（数学、安全、agentic 工具使用等）通过领域专用 RL 优化
  3. **MOPD（Multi-Teacher On-Policy Distillation）**：学生模型在自己的 rollout 上迭代学习，同时接收多教师的 token 级指导，将多领域能力合并到单一模型

### 推理优化

- **MTP（Multi-Token Prediction）**：3 层轻量 MTP 模块，使用密集 FFN
- **效果**：推理输出速度约提升 3×，同时加速 RL rollout
- **用量化**：FP8（E4M3）混合精度

### 部署配置

```python
# SGLang 部署关键参数
--quantization fp8
--speculative-algorithm EAGLE
--speculative-num-steps 3
--enable-multi-layer-eagle
--context-length 1048576
--reasoning-parser mimo
--tool-call-parser mimo
```

## 关键结果

### Base 模型评估（与竞品 base 模型对比）

| Benchmark | 设置 | V2.5-Pro Base | V2.5 Base | DeepSeek V4 Pro Base | Kimi-K2 Base |
|-----------|------|:---:|:---:|:---:|:---:|
| 激活/总参数 | - | 42B/1.02T | 15B/310B | 49B/1.6T | 32B/1.04T |
| **MMLU** | 5-shot | **89.4** | 86.3 | **90.1** | 87.8 |
| **MMLU-Pro** | 5-shot | 68.5 | 65.8 | **73.5** | 69.2 |
| **BBH** | 3-shot | 88.4 | 87.2 | 87.5 | 88.7 |
| **GSM8K** | 8-shot | **99.6** | 83.3 | 92.6 | 92.1 |
| **MATH** | 4-shot | **86.2** | 67.7 | 64.5 | 70.2 |
| **GPQA-Diamond** | 5-shot | **66.7** | 58.1 | - | 48.1 |
| **AIME 24&25** | 2-shot | **37.3** | 36.9 | - | 31.6 |
| **HumanEval+** | 1-shot | 75.6 | 71.3 | - | 84.8 |
| **MBPP+** | 3-shot | 74.1 | 70.9 | - | 73.8 |
| **LiveCodeBench v6** | 1-shot | **39.6** | 35.5 | - | 26.3 |
| **HellaSwag** | 10-shot | 89.8 | 88.6 | 88.0 | **94.6** |
| **C-Eval** | 5-shot | 91.5 | 88.6 | 93.1 | 92.5 |
| **GlobalMMLU** | 5-shot | **83.6** | 77.4 | - | 80.7 |

### Instruct 模型评估（HF Eval Results）

| Benchmark | Score |
|-----------|:---:|
| GSM8K | 99.6 |
| SWE-Bench Verified | 78.9 |
| SWE-Bench Pro | 57.2 |
| GPQA-Diamond | 66.7 |
| MMLU-Pro | 68.5 |
| Terminal-Bench 2.0 | 68.4 |

### 长上下文评估（GraphWalks）

| 上下文长度 | BFS 子任务 | Parents 子任务 |
|-----------|:--------:|:------------:|
| 32K | 0.88 | 0.96 |
| 128K | 0.80 | 0.94 |
| 512K | 0.56 | 0.92 |
| 1M | 0.37 | 0.62 |

对比：V2-Pro 在 128K 后快速退化，1M 时两个子任务均为 0.00。

### ClawEval Token 效率

- Pass³ = 64%，平均每个轨迹约 70K tokens
- 比 Claude Opus 4.6、Gemini 3.1 Pro、GPT-5.4 节省 40-60% tokens

### 应用级展示

- **SysY 编译器**：672 次工具调用 × 4.3 小时，233/233 测试通过
- **视频编辑器**：1,868 次工具调用 × 11.5 小时，8,192 行代码
- **FVF-LDO 模拟电路设计**：~1 小时闭环迭代（ngspice 仿真循环），所有指标达标

## 范式对比

| 维度 | MiMo-V2.5-Pro | DeepSeek V4 Pro | Kimi K2 |
|------|:-------------:|:----------------:|:-------:|
| 架构 | MoE + 混合注意力 | MoE + MLA | MoE + MLA |
| 总参数 | 1.02T | 1.6T | 1.04T |
| 激活参数 | **42B** | 49B | 32B |
| 专家数/路由 | 384/8 | 未披露 | 未披露 |
| KV cache 优化 | SWA 7× 压缩 | MLA 压缩 | MLA 压缩 |
| 上下文窗口 | 1M | 1M | 128K |
| 后训练特色 | MOPD（多教师蒸馏） | RL + 推理时控制 | 视觉 agentic |
| 技术报告形式 | HF 模型卡 | arXiv 论文 | arXiv 论文 |
| MTP | ✅ 3 层 | ✅ MTP | 未披露 |

**核心差异**：
1. 小米走**混合注意力**路线（SWA + GA），用局部注意力换 KV cache 效率；DeepSeek/Kimi 走 **MLA** 路线
2. MOPD 是独特优势——不是单一 RL 训练，而是多教师蒸馏合并
3. 小米强调长程 agentic 能力的 token 效率，而非纯 benchmark 分数

## 社区评价

- **Reddit r/LocalLLaMA**：有用户测试了 MiMo-V2.5-Pro 的自主编程能力，报告 301 次 commit、60+ 页产出、$70 API 成本。社区将其定位为"开源 agentic coding 的有力竞争者"。
- **Artificial Analysis**：MiMo-V2-Pro（前代）在 Intelligence Index 上得 49 分，与 GLM-5 和 Kimi K2.5 处于同一梯队。V2.5-Pro 的公开独立评测尚不充分。
- **YouTube**：有评测者测试了 V2.5-Pro 的长程推理能力，认为其在任务复杂度增加时仍保持良好稳定性。

## 可复用的工程经验

1. **三阶段后训练 > 单轮 RL**：SFT 奠基 → 领域专用 RL 深耕 → MOPD 合并。MOPD 的核心价值在于多教师的 token 级指导可以比单轮 RL 更好地保持各领域能力不退化。

2. **混合注意力的 6:1 经验值**：在 70 层模型中，10 层全局注意力足够维持全局长程依赖，60 层 SWA 提供绝大部分效率增益。这个比例可能随模型深度变化，但对于深 MoE 模型（70 层以上），6:1 是已验证的起点。

3. **MTP 的双重角色**：MTP 不仅加速推理（3× 吞吐量），还加速 RL rollout——在强化学习训练中，更快的 token 生成意味着更多的迭代次数，是海浦路斯的正反馈循环。

4. **长上下文评估要用结构化任务**：GraphWalks 比简单的"大海捞针"更有区分度。MiMo V2.5-Pro 在 1M 上下文上的 BFS 恢复率（0.37）说明了结构化的长程推理仍然是挑战，即便有 attention-sink bias 加持。

5. **FP8 部署栈**：MiMo-V2.5-Pro 的 SGLang 部署配置（DP+EP+TP 混合并行、EAGLE 投机解码、chunked prefill 32K）展示了 1T 参数 MoE 模型的工程部署标准。`--moe-a2a-backend deepep` 表明专家之间的 all-to-all 通信是性能瓶颈。
