---
name: multiverse-mapreduce
description: >
  将复杂目标分解为并行子任务（Map），使用delegate_task并行执行，
  然后归并结果（Reduce）。基于Multiverse (NeurIPS'25) 的MapReduce并行推理范式。
version: 1.0.0
trigger: >
  任务包含多个独立子问题，或需要多角度研究/多文件分析
metadata:
  hermes:
    tags: [Research, Parallel, MapReduce, Efficiency]
---

# Multiverse MapReduce Skill

## 原理

基于Multiverse (NeurIPS 2025) "Your Language Models Secretly Decide How to 
Parallelize and Merge Generation" 的MapReduce范式：

```
Map（分解）→ Process（并行执行）→ Reduce（合并）
```

原始论文让LLM自动标记可并行分支，实现2x推理加速。此skill将相同思想
映射到Hermes的agent编排层——用delegate_task并行化独立子任务。

## 使用场景

| 场景 | 说明 | 预期加速 |
|------|------|---------|
| 多角度调研 | 同时从不同角度研究同一问题 | 2-3x |
| 多文件分析 | 并行分析多个代码文件/文档 | 3-5x |
| 多源验证 | 从多个数据源交叉验证事实 | 2x |
| 代码审查 | 并行检查多个模块 | 2-4x |
| 对比分析 | 同时研究多个选项 | 2x |

## 工作流

### Step 1: Map — 任务分解

分析用户请求，识别可并行执行的独立子任务。

判断标准（参考Multiverse论文的"可并行分支检测"）：
- 子任务之间**无数据依赖**（不依赖对方的输出）
- 子任务可以使用**不同的工具集**
- 每个子任务产生**结构化输出**（便于后续合并）

### Step 2: Process — 并行执行

对每个子任务调用 delegate_task()，并行执行：

```python
# 思路：用 delegate_task 的 tasks 参数并行
results = delegate_task(
    tasks=[{
        "goal": sub_task.goal,
        "context": f"主任务背景\n子问题: {sub_task.question}",
        "toolsets": sub_task.toolsets,
    } for sub_task in sub_tasks],
    # Hermes的 tasks 数组会并行执行
)
```

当前 Hermes 的 delegate_task 已支持 tasks 参数做并行（每轮最多3个并发）。
Multiverse增强版在此基础上增加"自动分解"和"归并合成"两阶段。

### Step 3: Reduce — 结果归并

收集所有并行结果，按以下策略合并：

1. **去重** — 识别并消除重叠信息
2. **冲突解决** — 如果子任务结果矛盾，标记差异点并二次验证
3. **结构化合成** — 按主题/时间/优先级顺序组织
4. **最终回答** — 生成统一的综合性回答

## 使用方式

### 方式A: 直接使用此skill（推荐）

此skill通过 `trigger` 条件自动激活。当检测到任务中有多个独立子问题时，
agent会自动采用MapReduce模式。

### 方式B: 手动调用

```
/run multiverse-mapreduce
目标: 研究Transformer架构的三大创新方向
```

### 方式C: 在自定义任务中引用

在任意Hermes会话中，提及"多角度"、"并行"、"同时分析"等关键词
即可触发此skill。

## 示例

### 示例1: 多角度调研

```
用户: 分析React 19、Vue 4和Svelte 5的主要改进
触发: multiverse-mapreduce

Map → 3个子任务:
  - 子任务1: 研究React 19核心改进
  - 子任务2: 研究Vue 4核心改进  
  - 子任务3: 研究Svelte 5核心改进
Process → 并行 delegate_task
Reduce → 合并为对比报告
```

### 示例2: 多文件分析

```
用户: 审查src/下所有新增Python文件的代码质量
触发: multiverse-mapreduce

Map → 按文件分组子任务
Process → 并行审查每个文件
Reduce → 汇总所有问题清单
```

## Multiverse思想参考

原始论文的核心发现：
- **98%+** 的推理轨迹中存在可并行分支
- 并行分支的**分解**由模型自动完成（通过特殊标记）
- **Reduce**阶段的冲突解决是关键挑战

此skill实现了同样的MapReduce三阶段范式，在Hermes编排层代理
实现"并行推理"的效果，而非修改底层LLM推理引擎。

## 参考

- Multiverse (NeurIPS 2025): https://arxiv.org/abs/2506.09991
- Hermes delegate_task: tools/delegate_tool.py
