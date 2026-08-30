---
title: Qwen3.8-2.4T-A95B — Max 级旗舰首次开源：编码与协同的 2.4T 尺度验证
date: 2026-08-12
source: https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B
---

# Qwen3.8-2.4T-A95B — Max 级旗舰首次开源：编码与协同的 2.4T 尺度验证

**发布日期：** 2026年8月3日（Qwen3.8-Max 产品发布）；2026年8月12日开放权重（Hugging Face / ModelScope）
**来源：** https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B | https://qwen.ai/blog?id=qwen3.8 | https://github.com/QwenLM/Qwen3.8
**工程范式：** 首次把 Qwen-Max 级旗舰以开放权重交付——在 Qwen3.5 架构基础上（Gated DeltaNet 混合注意力 + 稀疏 MoE）做 2.4T 总参数 / 95B 激活的规模化验证，主打编码与长程协同（cowork）

## 设计哲学

Qwen3.8 系列的核心约束：**开源社区需要的不是"缩小版旗舰"，而是真正的旗舰本身。** "For the first time, Qwen3.8 brings a Qwen-Max-class model to open release"——这是 Qwen 开源史上第一次把 Max 级模型权重交出来。

架构上 Qwen3.8 不做激进革命，而是延续 Qwen3.5 已验证的骨架（Gated DeltaNet + Gated Attention 混合注意力、稀疏 MoE），把重心放在三件事：

1. **规模化**：2.4T 总参数 / 95B 激活，92 层，512 专家——是 Qwen 开源家族迄今最大
2. **长程 agentic 能力**：不只是"回答更难的问题"，而是"把复杂多步任务可靠地做到完成"（carry complex, multi-step tasks through to completion）
3. **生态兼容**：Claude Code / Qoder / QwenWork / OpenCode 等 harness 的全套支持，`reasoning_effort`（xhigh/medium/low）+ `preserve_thinking` 的推理控制

**放弃了什么：** 2.4T-A95B 开源权重是 **text-only** 模型——必须 thinking 模式，不支持多模态输入，thinking 不可关闭（多模态能力留给 Qwen3.8-Max API 版）。这是开源权重的刻意裁剪：先保编码与协同这一条主线。

## 关键架构决策

### 模型规格
- 总参数 2.4T，激活 95B/token
- Hidden dim 8192，92 层
- Hidden layout：23 × (3 × (Gated DeltaNet → MoE) → 1 × (Gated Attention → MoE))
- MoE：512 专家，每 token 激活 10 routed + 1 shared，专家中间维度 2048
- 上下文：262,144 原生，可扩展至 1,010,000
- 输出：131,072 tokens

### 注意力选型
- **Gated DeltaNet（线性注意力）为主，Gated Attention（软注意力）为辅**，比例 3:1——延续 Qwen3.5 的混合注意力路线
- Gated DeltaNet：128 V-heads / 16 QK-heads，head dim 128
- Gated Attention：64 Q-heads / 4 KV-heads，head dim 256，RoPE dim 64
- 这种布局的工程意图：在长上下文下用线性注意力压低 prefill 成本，用稀疏的软注意力层保留精确检索能力

### 训练策略
- Pre-training + Post-training 双阶段（原文未披露具体 token 量与数据配比）
- MTP（Multi-Token Prediction）多步训练——既提能力又加速推理
- 推理控制：`reasoning_effort` 三档 + `preserve_thinking` 默认开启（历史推理上下文保留，跨轮次维持）

### 推理优化
- 原生 262K 上下文，1M 靠 YaRN 类扩展（官方提供 SGLang/vLLM/TokenSpeed 的 1M 配置）
- text-only 设计本身即推理优化：无视觉 token 开销，专注编码 agent 吞吐

## 关键结果

（均为原文 model card 数字，对比模型为 Opus 4.8 / Fable 5 / GPT-5.6 Sol (max) / Qwen3.7-Max）

### 编码 Agent
| Benchmark | Qwen3.8-Max | Qwen3.7-Max | GPT-5.6 Sol |
|---|---|---|---|
| Terminal Bench 2.1 | 86.6 | 74.5 | 88.8 |
| SWE-bench Pro | 67.7 | 60.6 | 64.6 |
| DeepSWE 1.1 | 56.6 | 21.6 | 73.0 |
| NL2Repo-Bench | 55.9 | 47.2 | -- |
| FrontierSWE | 73.5 | 40.7 | -- |
| PaperBench | 93.0 | 64.8 | 90.5 |
| QwenSWEBench | 80.7 | 63.4 | 73.5 |

### 通用 Agent / 能力
| Benchmark | Qwen3.8-Max | Qwen3.7-Max | GPT-5.6 Sol |
|---|---|---|---|
| CoWorkBench | 74.8 | 64.6 | 71.5 |
| JobBench | 53.4 | 31.3 | 45.4 |
| SkillsBench | 70.2 | 61.2 | 73.5 |
| Agents' Last Exam (Pass/Score) | 27.0 / 52.4 | 11.8 / 31.1 | 30.6 / 53.6 |
| Toolathlon Verified | 72.5 | 49.7 | 74.9 |
| HLE w/ tools | 56.2 | 53.5 | 58.0 |
| GPQA Diamond | 92.6 | 92.4 | 94.1 |
| IFBench | 82.8 | 79.1 | 72.7 |
| $OneMillion-Bench (expert) | 52.5 | 44.4 | 53.8 |
| MRCR v2 256K (8-needle) | 92.9 | 86.7 | 93.8 |

观察：相比 Qwen3.7-Max 全面提升（尤其 FrontierSWE +32.8、PaperBench +28.2、Agents' Last Exam Score +21.3）；对 GPT-5.6 Sol 在 SWE-bench Pro、PaperBench、IFBench、OneMillion-Bench 上领先，在 DeepSWE、HLE、TB2.1 上落后——闭源前沿在"最难的端到端长程"上仍有优势。

## 范式对比

- **vs GLM-5.3 / DeepSeek-V4-Pro-0813（同期开源旗舰）**：Qwen 走"家族矩阵"路线——2.4T 旗舰 + 27B 密集 + Flash-Next 架构预览三线并进，覆盖从消费级到数据中心的全部部署形态；GLM 走"单轴 post-training 极致"，DeepSeek 走"架构持续推新 + 极致定价"（峰值/非峰值分段定价）
- **vs 闭源**：Qwen3.8-Max 的定位是"开源里最能打的编码旗舰"，但在 DeepSWE 这类需要多步长程执行的任务上与 GPT-5.6 Sol 仍有 ~16 分差距——差距集中在"环境交互的持久性与探索深度"
- **开源策略差异**：GLM-5.3 权重延后两周（安全窗口），Qwen3.8-Max 权重 9 天内开放——开源节奏本身成为竞争变量

## 社区评价

原文未提供 HN/Reddit 讨论数据，未独立核实，暂不引用。公开可见信号：8 月 4 日有第三方对 Qwen3.8-Max 做过 Hugging Face 权重审计（"2.4T parameters, open weights"），下载量与生态接入（SGLang/vLLM/llama.cpp/MLX 全套）均为 Qwen 家族最高水平。

## 可复用的工程经验

1. **开源旗舰 = 能力裁剪 + 生态对冲**：text-only 权重保主线（编码/协同），多模态留给 API——开源发布不必全能力开放，砍掉高成本能力换主场景极致
2. **推理控制是 agent 场景的隐藏刚需**：`reasoning_effort` 三档 + `preserve_thinking` 跨轮保留，直接影响长程任务的 token 成本与成功率——发布模型时把推理预算控制做成一等公民
3. **家族矩阵优于单品**：同一架构栈出 2.4T/27B/架构预览三档，让用户在生态内迁移而非外流——覆盖密度本身就是护城河
4. **自建 benchmark 防污染**：QwenSWEBench/QwenQoderBench/QwenReactBench 等内部基准（judge 用多模态自动渲染 + Elo）对冲公开测试集污染风险——旗舰模型评测必须建私有用例
