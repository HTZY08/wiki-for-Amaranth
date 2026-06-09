---
title: 把论文写成代码——Lau博士云组会15篇论文的Hermes落地实践
description: 从64个视频中提取15篇核心论文，筛选出3个可直接集成到Hermes Agent的实现
---

## 起因

一直看[@Lau博士的云组会](https://space.bilibili.com/3546659109735216)的论文精读视频，
他逐段拆论文的方式很硬核，覆盖了从架构改进到训练算法的整条AI前沿。

某天突发奇想：**他讲的这些技术，能不能直接写成代码装进Hermes？**

于是花了半天做了个系统过滤：

## 流程

```
Lau博士64个B站视频 → 15篇核心论文入库
  → 并行问GPT-5.5/Claude Opus/Gemini Pro（御三家）
    → 共识: 9篇可映射, 3篇P0优先落地
      → 写代码 + README + 推博客
```

## 筛选结果

64个视频中，15篇是真正有技术深度的论文。其中：

- **7篇**与Hermes Agent不相关（模型架构/训练/视觉方向）
- **5篇**可作为思想参考（需较大适配）
- **3篇可直接落地**——这就是本文的重点

## 三个落地实现

### 1. SepLLM 压缩器（ICML 2025）

**核心发现**：自然语言里的分隔符（句号、换行、分段符）在模型注意力分数中占比异常高——它们在充当段落的"摘要节点"。把段落信息压缩到分隔符里，KV缓存能砍掉50%以上。

**代码实现**：一个纯规则驱动的context_engine插件，零LLM调用。

```python
# 三段式结构: Initial + Separator + Local
initial = messages[:3]          # 系统提示永远保留
middle = self.compress(middle)  # 中间段按分隔符压缩
tail = messages[-20:]           # 最近20条保留完整
```

长代码块、工具输出、枚举列表——每种都有独立的压缩策略。
预期token节省15-30%，而且是白送的（不花推理成本）。

### 2. MoR 自适应深度（NeurIPS 2025）

**核心发现**：Transformer推理时不同token需要的计算量不同——简单token可以浅处理提前退出，复杂token才走完整路径。

**代码实现**：给Hermes装了一个"复杂度路由器"，根据输入特征动态调整最大工具调用轮次。

| 深度 | 触发条件 | 最大轮次 |
|------|---------|---------|
| 浅层 | 简单事实问答 | 5轮 |
| 中层 | 标准推理 | 15轮 |
| 深度 | 调研/对比/架构 | 30轮 |

加上提前退出检测——收集到确凿答案就直接结束，不用走满所有轮次。

### 3. Multiverse MapReduce（NeurIPS 2025）

**核心发现**：超过98%的推理轨迹中存在可并行分支。将推理改造为MapReduce范式（分解→并行执行→合并），能实现2倍加速。

**代码实现**：一个规则驱动的任务分解器 + 结果归并器。

```python
# 输入: "研究React、Vue和Svelte的优缺点"
# 分解 → 3个独立子任务并行执行 → 合并为对比报告
sub_tasks = analyze_task(goal)  # 检测并列/对比/多角度模式
results = delegate_task(tasks=sub_tasks)  # 并行
final = merge_results(results)  # 结构化合并
```

## 代码位置

```
HTZY08/wiki-for-Amaranth → src/content/docs/projects/lau-hermes-improvements/
```

包含：
- `plugins/sepllm_compressor.py` — SepLLM context engine
- `plugins/mor_context_engine.py` — MoR自适应深度
- `plugins/multiverse_mapreduce.py` — Multiverse MapReduce
- `skills/multiverse-mapreduce/SKILL.md` — MapReduce skill
- `SPEC.md` — 集成指南，含Hermes补丁位置

## 没落地的（知识库里有）

还有7篇我评价为"不可落地"的论文（CTM、OverLoCK、vHeat、RAEv2、NoProp、DiC、MeanFlow），
以及5篇P1-P3待续的（FlyLoRA、AttnRes、MUDDFormer、分形生成、LoRI）。
它们都写好结构化笔记存在vault里了，以后需要再翻出来。

## 一点感受

论文落地到Agent框架，不是一个代码移植问题，而是一个**模式映射**问题。
没有一篇论文的代码能直接拿过来用——都是从机器学习架构模式翻译成Agent系统设计模式。

最有意思的是SepLLM——一篇做LLM稀疏注意力的大会论文，最直接的价值
竟然是它的**思想**（分隔符=天然压缩点）而不是它的代码。
一个好的抽象可以在不同层级重复生效。
