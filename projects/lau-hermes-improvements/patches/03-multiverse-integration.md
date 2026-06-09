# Multiverse集成补丁说明

## 论文
**Multiverse: Your Language Models Secretly Decide How to Parallelize and Merge Generation**
- 会议: NeurIPS 2025
- 核心发现: 98%+的推理轨迹中存在可并行分支
- 源码: https://github.com/Infini-AI-Lab/Multiverse

## 映射关系

| Multiverse概念 | Hermes映射 |
|---------------|-----------|
| 三阶段范式(Map→Process→Reduce) | 分解→delegate_task并行→合并 |
| 特殊标记分割(<Parallel>/<Goal>/<Outline>) | 关键词触发的规则分解器 |
| 并行Attention掩码 | tasks数组并行执行（独立上下文） |
| Reduce阶段合并 | merge_results结构化合成 |

## 代码

- `plugins/multiverse_mapreduce.py` — 分解+归并逻辑
- `skills/multiverse-mapreduce/SKILL.md` — skill描述

## 预期效果

- 多角度调研 2-3x加速
- 多文件分析 3-5x加速
- 对比分析任务质量提升（信息更全面）

## 风险

- 子任务间可能有隐含依赖未被检测到
- 并行执行消耗更多总token（但wall-clock时间更短）
- 结果合并可能丢失子任务间的关联信息
