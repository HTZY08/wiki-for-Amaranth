---
title: MiniMax-M2 系列 — Mini Activations, Max Intelligence
date: 2025-02-01
source: arXiv 2605.26494
---

# MiniMax-M2 系列

**发布日期：** 2025-02-01（M2 初始版本）  
**来源：** arXiv 2605.26494  
**工程范式：** 硬核系统协同设计——用极小激活参数（9.8B）撬动极大的真实世界智能。

## 设计哲学

M2 系列的核心信条是 **"mini activations can unleash maximum real-world intelligence"**。M2 的设计打破了"更大激活参数 = 更好性能"的惯例，追求 **每激活参数的高效率**。229.9B 总参数中仅激活 9.8B 每 token——一个极端的激活稀疏比（~23:1）。

整个 M2 系列从基座预训练（29.2T tokens）到后训练管线，再到 M2→M2.5→M2.7 的自我进化，都围绕这一核心理念。

## 关键架构决策

### 基座架构

| 属性 | 值 |
|------|-----|
| 架构 | 62 层 decoder-only MoE Transformer |
| 总参数 | 229.9B |
| 激活参数/token | **9.8B** |
| 专家数 | 256 细粒度专家，top-8 激活 |
| 门控 | Sigmoid gating + learnable expert bias（无 softmax） |
| 注意力 | Full multi-head attention，48 query heads，8 KV heads（GQA） |
| 上下文窗口 | 192K（原生） |
| 位置编码 | RoPE |
| 词表 | 200,064 |
| 预训练 | 29.2T tokens（19.9T 恒定 + 9.3T decay/长上下文阶段） |
| 多 token 预测 | MTP K=1→K=3（speculative decoding） |

### 关键设计决策

- **全量注意力（full attention）优于混合滑动窗口（hybrid SWA）**：大量实验表明 hybrid SWA 在检索、多跳推理和长上下文 agent 任务上都有退化
- **256 专家优于 32 专家**：MATH 从 19.6→24.1, HumanEval 29.7→32.5
- **MTP 持续提升推理密集型任务**

### 后训练三支柱

1. **Agent-driven Data Pipelines：** 可执行 workspace 中的可验证 trajectory，覆盖 Agentic Coding 和 Agentic Cowork
2. **Forge RL 系统：** 可扩展的 agent-native RL 系统，支持 windowed-FIFO scheduling、prefix-tree merging、inference optimization
3. **Self-Evolution（M2.7）：** 自主调试训练运行、修改自身的 scaffold

## 关键结果

### M2 → M2.5 → M2.7 进展

| 基准 | M2 | M2.5 | M2.7 |
|------|-----|------|------|
| SWE-bench Verified | - | **80.2%** | - |
| Multi-SWE-Bench | - | **51.3%** | - |
| BrowseComp | - | **76.3%** | - |
| 执行速度 | 基线 | +37% vs M2.1 | 匹配 Opus 4.6 |
| 运行成本 | - | $1/小时（100 tokens/s） | 约 Opus 4.6 的 7% |

### M2.5 关键定价

| 速率 | 每小时成本 |
|------|-----------|
| 100 tokens/s | **$1.00** |
| 50 tokens/s | **$0.30** |

## 范式对比

| 维度 | MiniMax M2 系列 | DeepSeek V3 | Llama 3 405B |
|------|----------------|-------------|--------------|
| 激活参数 | **9.8B** | 37B | 405B |
| 总参数 | 229.9B | 671B | 405B |
| 激活比 | **~23:1** | ~18:1 | 1:1（dense） |
| 专家数 | **256** | 256 | N/A |
| 上下文 | 192K | 128K | 128K |
| 后训练 | Agent-native + Forge RL | SFT + RL | SFT + RLHF |

## 可复用的工程经验

1. **极端的激活稀疏比（23:1）是可行的** —— 9.8B 激活可以匹敌数十倍激活参数的模型
2. **Full attention 在 agent 场景下不可替代** —— 不要为了效率牺牲核心检索和多跳推理能力
3. **Sigmoid gating 优于 softmax gating** —— 去除专家间的竞争性归一化可以提升效果
4. **Forge RL 系统是 Agent-native 训练的工程基础设施** —— 非算法的系统设计（scheduling、merging、decoupling）是核心竞争力
5. **Self-evolution（M2.7）是后训练的下一个前沿** —— 模型开始自主改进自己的训练和推理管线
