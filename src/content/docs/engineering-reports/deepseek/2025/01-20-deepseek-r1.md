---
title: DeepSeek-R1 — 纯 RL 推理训练，GRPO 首次实践
date: 2025-01-20
source: arXiv 2501.12948
---

# DeepSeek-R1

**发布日期：** 2025-01-20
**来源：** arXiv 2501.12948
**工程范式：** 纯强化学习涌现推理路线——不用人类标注推理路径，让模型自己学会思考。

## 设计哲学

DeepSeek-R1 是 AI 推理训练的一个范式级突破。它的核心假设：人类定义的推理模式（CoT 的几种固定写法）会限制模型的探索空间——让 RL 自由探索可能涌现更好的推理策略。

这个假设在 R1-Zero 上得到了验证：纯 RL 训练（无 SFT）的 R1-Zero 在 AIME 2024 上从 15.6% 飙升到 71.0%，并自发涌现了自我验证（self-verification）、反思（reflection）、长链推理（long CoT）等行为。其中最著名的是 "Aha Moment"——模型在推理中途突然说 "Wait, wait. Wait. That's an aha moment I can flag here."

关键舍弃：R1-Zero 的输出可读性差、语言混杂。为了生产可用，R1 引入了一些冷启动数据（数千条人工验证的 CoT 样本）和多阶段训练，但仍然坚持用 RL 作为核心训练手段。

## 关键架构决策

### GRPO（Group Relative Policy Optimization）

- 不需要 critic 模型（PPO 需要），advantage 从组内得分的均值和标准差计算
- Advantage = (r_i - mean(r_1...r_G)) / std(r_1...r_G)
- 损失函数含 clip 机制（防更新过大）和 KL 散度正则（防偏离 base model 太远）
- 计算量约为 PPO 的一半（省掉了 critic 的前向+后向）

### R1-Zero 训练

- Base model: DeepSeek-V3-Base
- Reward 只用规则：准确性（确定性答案匹配/编译器反馈）+ 格式（确保 <think> 和 <answer> 标签）
- 训练模板不含内容偏见，只规定输出结构

### R1 四阶段管线

1. **冷启动：** 收集数千条可读的长 CoT 样本（few-shot + 人工后处理），微调 V3-Base
2. **推理 RL：** 同 R1-Zero 的 GRPO，但增加语言一致性奖励（防语言混杂）
3. **拒绝采样 + SFT：** RL 收敛后，生成约 600K 推理轨迹（过滤正确性和可读性）+ 200K 非推理样本，重新训练 base model 2 epochs
4. **全场景 RL：** 推理任务用规则奖励 + 通用任务用 reward model（有用性+无害性）

### 蒸馏

- 从 R1 生成 800K 训练样本（推理轨迹），用 SFT 直接蒸馏到 Dense 小模型（Qwen/Llama 系列）
- 无需对蒸馏模型做 RL——SFT 就够
- 蒸馏 32B/70B 成为 Dense 推理模型新 SOTA

## 关键结果

- R1 AIME 2024: 79.8%（vs o1-1217 的 79.2%）— **首次开源模型追平闭源推理模型**
- R1 MATH-500: 97.3%
- R1 Codeforces: 2029 rating（96.3% percentile）
- R1-Zero AIME: 从 15.6% → 71.0%（纯 RL，无 SFT）
- 蒸馏 14B 超越 QwQ-32B-Preview

## 范式对比

vs OpenAI o1（闭源，2024.09 首发推理模型），R1 首次验证了纯 RL 路线的可行性。vs 传统 SFT+RL 路线，R1 证明 SFT 对推理能力的涌现不是必须的——但冷启动数据对输出质量是必要的。

## 可复用的工程经验

1. 规则奖励足够支撑推理能力涌现——不需要复杂的 reward model（最少可行奖励原则）
2. 纯 RL 训练会自然涌现自我验证和反思——这些行为不需要显式编程
3. 蒸馏比直接在大模型上跑 RL 更经济——小模型用 SFT 吸收推理能力就够
4. "Aha Moment" 现象说明模型学到了超越人类定义的推理策略——不要用自己的认知限制模型
5. 语言一致性奖励是 R1 相对 R1-Zero 的关键改进——没有它输出会混杂多语言
