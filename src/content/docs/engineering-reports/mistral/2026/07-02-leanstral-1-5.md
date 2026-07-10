---
title: Leanstral 1.5 — 面向 Lean 4 形式化证明的开源代码智能体模型
date: 2026-07-10
source: https://mistral.ai/news/leanstral-1-5
---

# Leanstral 1.5：面向 Lean 4 形式化证明的开源代码智能体

**发布日期：** 2026-07-02
**来源：** [Mistral AI Blog](https://mistral.ai/news/leanstral-1-5) / [HuggingFace](https://huggingface.co/mistralai/Leanstral-1.5-119B-A6B) / [API 文档](https://docs.mistral.ai/models/model-cards/leanstral-1-5)
**工程范式：** Mistral 的垂直专业化策略——在定理证明这一狭窄领域用 MoE 模型实现极致性能，同时保持 Apache-2.0 完全开源

## 设计哲学

Leanstral 1.5 的核心约束是**自动化定理证明的成本与准确性矛盾**。现有方案（如 Seed-Prover 1.5 high setting）每个问题需 10 H20-days 的计算预算，成本约 $300+/问题。Leanstral 1.5 将成本降至约 $4/问题（~75x 降幅），同时保持或超越 SOTA。

关键权衡：
- **完全专注于 Lean 4 证明辅助语言**，不追求通用代码生成能力。这是 Mistral 继 Leanstral 原始版之后的第二次垂直化尝试
- **使用 128 专家 MoE（4 active/token）架构**，119B 总参数 / 6.5B 活跃参数，在推理效率与模型容量之间取得平衡
- **放弃"单次推理即正确"的幻想**，采用多轮（multiturn）交互式证明流程——模型提交证明，接收 Lean 编译器反馈，迭代修正
- **256K 上下文窗口**：一些证明链长达 270 万 token，需要 22 次上下文压缩（compaction）

## 关键架构决策

### MoE 设计
- 128 个专家，每 token 激活 4 个
- 119B 总参数，6.5B 活跃参数
- 属于 Mistral Small 4 模型系列
- Apache-2.0 许可证

### 训练策略
三阶段训练管线：

1. **Mid-training**：在 Lean 4 证明数据上继续进行预训练
2. **Supervised Fine-Tuning (SFT)**：使用经过验证的证明轨迹进行监督微调
3. **Reinforcement Learning with CISPO**：使用 CISPO（一种策略优化算法）进行强化学习

### 训练环境
两个互补的 RL 环境：

**Multiturn 环境**：
- 给定定理陈述，模型必须证明或证伪
- 提交证明 → 接收 Lean 编译器反馈 → 迭代修正
- 证明编译通过即成功，否则循环继续直至耗尽预算

**代码智能体环境**：
- 模型在原始文件系统中操作，如同开发者一样工作
- 可以编辑文件、运行 bash 命令、使用 Lean 语言服务器检查目标/错误/类型信息
- 适合处理长期任务：补全仓库中的部分证明、构建辅助引理、多轮上下文压缩
- 最终通过 SafeVerify 分支验证正确性

### 推理优化
- 256K 上下文窗口
- 支持通过 vLLM 本地部署
- 测试时计算（test-time compute）扩展表现出色——从 50k 到 4M token 预算，性能单调平滑提升

## 关键结果

### 定理证明基准

| Benchmark | Leanstral 1.5 | Seed-Prover 1.5 high | Goedel-Architect (no NL) |
|-----------|---------------|---------------------|-------------------------|
| miniF2F (val+test) | **100%** | - | - |
| PutnamBench (587/672) | **587** | 580 | - |
| FATE-H | **87** | 75 | - |
| FATE-X | **34** | 30 | - |

### 测试时计算扩展（PutnamBench Pass@8）

| Token Budget | 解决的问题数 |
|-------------|------------|
| 50k | 44 |
| 200k | 244 |
| 1M | 493 |
| 4M | **587** |

### FLTEval（真实代码验证）

| Metric | Leanstral 1.5 | Leanstral 原始版 | Opus 4.6 |
|--------|---------------|-----------------|----------|
| pass@1 | 28.9 | 21.9 | - |
| pass@8 | **43.2** | 31.9 | 39.6 |

### 成本对比（PutnamBench）
- **Leanstral 1.5**: ~$4/问题
- **Seed-Prover 1.5 high**: ~$300+/问题（10 H20-days/问题）
- **Aleph Prover**: $54-68/问题

### 代码验证：Bug 发现
在 57 个测试仓库中：
- 标记 47 个违反的属性
- 11 个指向真实 bug
- **5 个是 GitHub 上未报告的新 bug**
- 示例：datrs/varinteger 库的 zigzag decoding sign 函数在 `Std.U64.MAX` 输入下发生溢出

## 范式对比

| 维度 | Leanstral 1.5 | Seed-Prover 1.5 | Aleph Prover | Goedel-Architect |
|------|---------------|-----------------|-------------|-----------------|
| 开放权重 | ✅ Apache-2.0 | ❌ | ❌ | ❌ |
| 活跃参数 | 6.5B | 未公开 | 未公开 | 未公开 |
| 每问题成本 | ~$4 | ~$300+ | $54-68 | 未公开 |
| 自然语言指导 | 不需要 | 不需要 | 不需要 | 不需要 |
| Lean 4 支持 | ✅ | ✅ | ✅ | ✅ |
| 免费 API | ✅ | ❌ | ❌ | ❌ |

**关键差异：** Leanstral 1.5 是唯一完全开源且提供免费 API 的定理证明模型。成本仅为 Seed-Prover 的 1/75，这意味着定理证明从"研究专用"迈向"开发者日常工具"。

## 社区评价

- Hacker News 上讨论热烈，核心争议点：定理证明 AI 是否终于达到了实用阈值？
- 多条评论指出，$4/问题的成本使形式化验证可以融入 CI/CD 流程
- 有人认为 PutnamBench 的 587/672 成绩"令人印象深刻，但剩余 85 道题可能代表模型无法突破的难度上限"
- Mistral 社区对 Apache-2.0 许可证表示赞赏

## 可复用的工程经验

1. **成本-性能边界的前移**：Leanstral 1.5 证明，在不依赖超大计算预算的前提下，通过精巧的训练环境设计（multiturn + code agent 双环境）可以实现定理证明的 SOTA。这对其他垂直领域（如形式化验证、程序合成）有直接参考价值。

2. **CISPO 算法的选择**：相比于 PPO 或 GRPO，CISPO 在证明场景中的收敛效率更高。如果读者在做类似的形式化推理训练，建议从 CISPO 开始而不是 PPO。

3. **测试时计算的平滑缩放**：Leanstral 1.5 的 token budget 与 solved problems 呈单调关系（而非阶梯函数），这意味着可以针对不同场景动态分配推理预算——对成本敏感场景用低预算，对高难度证明用高预算。

4. **SafeVerify 验证管线**：Mistral 开源的 FLTEval 和 SafeVerify fork 可以直接用于其他形式化验证项目，无需从头构建验证环境。

5. **双环境 RL 框架**：multiturn 环境处理"证明/证伪"的二元判断，code agent 环境处理"文件编辑+bash+Lean LSP"的复合操作。这种"判断+操作"分离的设计适用于需要验证反馈的许多编码任务。
