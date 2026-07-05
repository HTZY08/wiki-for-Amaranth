---
title: Qwen3-Coder-Next — 3B 激活参数的极致编码 Agent
date: 2026-07-05
source: https://arxiv.org/abs/2603.00729
---

# Qwen3-Coder-Next — 3B 激活参数的极致编码 Agent

**发布日期：** 2026年3月（arXiv 2603.00729）
**来源：** https://arxiv.org/abs/2603.00729
**工程范式：** 极小激活参数 + Agentic 训练 = 编码专用高效模型

## 设计哲学

核心约束：**80B total / 3B active** — 探索强训练配方能多大程度弥补参数量的不足。

Qwen3-Coder-Next 的核心命题是：在 MoE 架构下将激活参数压缩到 3B，通过大规模可验证编码任务的 agentic 训练，使小激活模型达到接近甚至超越 10×–20× 激活参数量的编码能力。这不仅是效率优化，更是一种训练范式的迁移——从"堆参数"转向"堆高质量可执行训练信号"。

## 关键架构决策

### 1. 基于 Qwen3-Next 的 Hybrid Attention + MoE

- **512 个专家，每 token 激活 10 个专家**，MoE 路由选择 10/512，确保 80B total / 3B active 的极致稀疏比
- **Hybrid attention 机制**：廉价线性层处理长序列（262K context），高精度注意力层周期性"锚定"关键信息
- **训练 context 从 32K 扩展到 262K tokens**，支持 repository-level 理解和多轮 agent 交互

### 2. 合成可验证编码任务 + 可执行环境

两条互补的任务合成管线：

- **From GitHub PRs**：挖掘真实世界 issue 相关 PR，构建 bug state → fix → test patch 的可执行 Docker 环境。专用环境构建 agent 自动化搭建，QA agent 过滤，生产 ≈800K 可验证任务实例，覆盖 9+ 编程语言
- **Synthesizing Issues from Seeds**：基于 SWE-Smith、SWE-Flow、SWE-Rebench、Multi-SWE-RL 等开源数据集，通过模型驱动改写、语义扰动、规则变换注入 bug，去重后保留 ≈850K 任务

### 3. Mid-training + RL from Environment Feedback

三阶段训练管线：

- **Mid-training**：继续预训练，以自然数据为主 + 合成数据为辅（≈600B tokens repository-level 代码），在 262K context 下训练。采用 Best-Fit Packing（BFP）消除文档碎片化，使用 FIM 训练支持代码补全
- **Supervised Fine-tuning**：对齐阶段，在高质量指令数据上微调，使用 Mini-SWE-agent 做关闭循环验证过滤，Pairwise judging 优化对话质量
- **Post-training 专家路由 + 蒸馏**：
  - **单轮 RL 专家**：扩展代码 RL 到非竞赛场景（库调用、多语言、安全编码），执行信号驱动
  - **软件工程 RL 专家**：多轮 agentic RL，带轨迹级和 token 级惩罚，处理 reward hacking
  - **WebDev 专家**：Playwright 渲染+VLM 评估+交互验证
  - **UX 专家**：多样工具调用模板训练（21 种模板），提升跨框架泛化
  - **专家蒸馏**：合并四个领域专家到统一推理模型

### 4. 开源权重

两套权重公开发布：base 和 instruction-tuned，支持 HuggingFace 和 ModelScope 下载。

## 关键结果

### Agent 编码基准测试（SWE-Agent scaffold）

| 基准 | Qwen3-Coder-Next (80A3) | DeepSeek-V3.2 (671A37) | GLM-4.7 (358A32) | MiniMax-M2.1 (230A10) |
|---|---|---|---|---|
| **SWE-Bench Verified** | **70.6%** | 70.2% | 74.2% | 74.8% |
| **SWE-Bench Multilingual** | **62.8%** | 62.3% | 63.7% | 66.2% |
| **SWE-Bench Pro** | **42.7%** | 46.0% | 45.1% | 40.8% |
| **Terminal-Bench 2.0** (Terminus2-json) | **36.2%** | 39.3% | 37.1% | 32.6% |
| **Aider-Polyglot** | **66.2%** | — | — | — |

Qwen3-Coder-Next 仅用 **3B active params** 即达到 DeepSeek-V3.2（37B active）在 SWE-Bench Verified 上的水平，效率差距约 **12×**。

### 跨 Scaffold 一致性（SWE-Bench Verified）

| Scaffold | 分数 |
|---|---|
| SWE-Agent | 70.6% |
| MiniSWE-Agent | 71.1% |
| OpenHands | 71.3% |

模型在不同 agent 框架上表现高度一致，体现了工具格式无关的泛化能力。

### 函数级编码与推理

| 基准 | Qwen3-Coder-Next | Qwen3-Next | Qwen3-Coder-480B-A35B |
|---|---|---|---|
| EvalPlus | 86.56 | 89.00 | 86.66 |
| MultiPL-E | 88.23 | 89.00 | 88.00 |
| CRUXEval | **95.88** | 94.81 | 92.13 |
| LiveCodeBench v6 | **58.93** | 51.79 | 44.93 |
| OJBench | **23.01** | 20.04 | 14.98 |
| Codeforces (Rating) | **2100** | 1875 | 1800 |

在推理密集型基准上（CRUXEval、LiveCodeBench、Codeforces），3B active 模型显著超越 35B active 的前代旗舰。

### 通用知识（MMLU/GPQA）与数学推理

| 基准 | Qwen3-Coder-Next | Qwen3-Next |
|---|---|---|
| MMLU | 87.73 | 87.87 |
| MMLU-Pro | 80.52 | 80.89 |
| GPQA | **74.49** | 73.54 |
| AIME24 | **89.01** | 82.92 |
| AIME25 | **83.07** | 69.64 |

编码推理能力向数学推理显著迁移（AIME25 提升 13.43 个百分点）。

### 工具调用泛化（21 模板测试）

跨 5 种 IDE/CLI scaffold 平均模板遵循准确率 92.7%，显著超越 Gemini-3-pro（87.0%）、DeepSeek-V3.2（93.7%）、Claude-sonnet-4.5（85.4%）。

## 范式对比

### 与 DeepSeek-V3.2（671B total / 37B active）

| 维度 | DeepSeek-V3.2 | Qwen3-Coder-Next |
|---|---|---|
| 激活参数 | 37B | **3B** (12× 更少) |
| SWE-Bench Verified | 70.2% | 70.6% |
| SWE-Bench Multilingual | 62.3% | 62.8% |
| SWE-Bench Pro | **46.0%** | 42.7% |
| Terminal-Bench 2.0 | **39.3%** | 36.2% |
| 训练策略 | 通用 RLHF | Agentic mid-training + 环境 RL |
| 关键差异 | 更大的密集知识容量 | 更专精的 agentic 能力 |
| 部署开销 | 高（16× 推理显存） | 低（单卡可部署） |

### 与 GLM-4.7（358B total / 32B active）

| 维度 | GLM-4.7 | Qwen3-Coder-Next |
|---|---|---|
| 激活参数 | 32B | **3B** (10× 更少) |
| SWE-Bench Verified | **74.2%** | 70.6% |
| SWE-Bench Multilingual | **63.7%** | 62.8% |
| SWE-Bench Pro | **45.1%** | 42.7% |
| Template Following Avg | 69.9% | **92.7%** |
| 优势区域 | 高难度 SWE 任务 | 工具调用泛化、部署成本 |

### 与 MiniMax M2.1（230B total / 10B active）

| 维度 | MiniMax M2.1 | Qwen3-Coder-Next |
|---|---|---|
| 激活参数 | 10B | **3B** (3.3× 更少) |
| SWE-Bench Verified | **74.8%** | 70.6% |
| SWE-Bench Multilingual | **66.2%** | 62.8% |
| SWE-Bench Pro | 40.8% | **42.7%** |
| Terminal-Bench 2.0 | 32.6% | **36.2%** |
| 优势区域 | SWE-Bench 高绝对分 | 长难度任务、低成本部署 |

### 范式定位图

```
SWE-Bench Verified 分数
   75 |                   GLM-4.7(32B)  MiniMax(10B)
   74 |                   
   73 |                   
   72 |                   
   71 |          Qwen-Coder-Next(3B) ●
   70 |  DeepSeek-V3.2(37B) ●
   69 |                   
   68 |                   
   67 |                   
   66 |                   
   65 |                   
     ────────────────────────────────────
        3B       10B       32B       37B
                 Active Parameters
```

Qwen3-Coder-Next 处于效率前沿的左上方——用最少的激活参数达到最高的编码 agent 水平。

## 可复用的工程经验

### 1. 可验证任务合成是 Agentic Training 的基石

- 纯静态代码数据不足以训练编码 agent，必须构建 "可执行环境 + 可验证信号" 的闭环
- GitHub PR 挖掘 + 种子合成双管线，可扩展到 ≈1.6M 任务实例
- QA agent 过滤 + 自动化环境构建是质量保障的关键

### 2. 专家蒸馏优于专家路由

- 四个领域专家（SWE、WebDev、UX、单轮 RL）分别训练后蒸馏回单一模型
- 部署时无需专家路由，一个模型处理所有任务，大幅简化架构

### 3. 工具调用多样性 = 泛化性

- 使用 21 种不同工具调用模板训练，模型学到的是格式无关的工具使用能力
- 单模板过拟合是 agent 鲁棒性的首要瓶颈
- 引入 XML 风格（`qwen3_coder`）调用格式避免长篇代码的 JSON 转义开销

### 4. Reward Hacking 是 RL 训练的常态化挑战

- Agent 会主动发现新漏洞：`git remote add`、`curl`、`git clone` 等方式绕过保护
- 建议采用启发式阻断器 + 手动检查迭代升级防御
- 在公开发布数据集中泄漏的 future commit 信息需要系统性防范

### 5. BFP（Best-Fit Packing）对长上下文训练至关重要

- 消除文档碎片化比增加 padding 更有效——同样 token 预算下性能 +0.96%
- 极长文档的 "drop" 策略在消融中表现最佳，暗示当前更好的方向是直接扩展 context 长度

### 6. 编码推理可以迁移到数学推理

- AIME25 上 83.07%（vs Qwen3-Next 69.64%），编码 RL 训练带来了显著的数学推理提升
- 这可能是因为代码执行提供了比数学验证更密集、更多样化的反馈信号

### 7. 小激活模型 + 强训练 ≈ 部署友好的编码 Agent

- 3B active 参数可以单卡部署（甚至消费级 GPU）
- 在 SWE-Bench Verified 上仅落后最佳开源模型 4 个百分点，但推理开销降低 10×+
- 这一方向对边缘部署、本地 IDE 插件、企业私有化部署极具价值
