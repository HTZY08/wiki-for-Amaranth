# MoR集成补丁说明

## 论文
**Mixture-of-Recursions: Learning Dynamic Recursive Depths for Adaptive Token-Level Computation**
- 会议: NeurIPS 2025
- 核心创新: 共享层复用 + 轻量路由器动态分配token级递归深度 + KV缓存减半
- 源码: https://github.com/raymin0223/mixture_of_recursions

## 映射关系

| MoR概念 | Hermes映射 |
|--------|-----------|
| 递归参数共享(参数量减半) | 同一组工具/skill库可递归复用 |
| 自适应递归深度 | 动态调整max_turns(5/15/30) |
| 轻量路由器(Router) | 输入特征复杂度评分 |
| Expert-Choice路由 | agent自动决定是否继续思考 |
| Early Exit | 满足条件时提前结束 |
| KV缓存优化 | 压缩不活跃的上下文中段 |

## 代码

`plugins/mor_context_engine.py` — 包含:
- MoRRouter: 复杂度评分器（规则驱动，无需模型）
- should_early_exit: 提前退出检测
- MoRContextEngine: context_engine插件接口

## 预期效果

- 简单问题减少40-60%工具调用
- 复杂问题获得更多推理轮次
- 整体token消耗降低20-40%

## 风险

- 复杂度评分可能误判（规则不够精细）
- 提前退出可能过早终止（需要调整敏感度）
