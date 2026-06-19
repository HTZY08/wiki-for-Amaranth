---
title: BigSet 集成指南
description: 将 BigSet 作为 Agent 的结构化数据层——搜索→入库→查询→定时刷新
---

BigSet 是一个"一句话构建数据集"的开源工具。将它的 Convex 后端集成到 Agent 系统中，就多了一个**结构化持久层**。

## 能干什么

```
你说话 → Agent 搜 → 整理表格 → 存 BigSet → 随时查
                                ↕
                        定时刷新 → 搜最新 → 更新
```

具体能力：

- **搜→存**：Agent 搜到的结构化信息直接入库，不用手动建表
- **跨 session 查询**：上次聊的数据下次还能查到
- **定时刷新**：设 cron 自动更新数据集
- **替代 populate**：Agent 自己的搜索能力 > BigSet 原生 Mastra 工作流（支持多搜索源）

## 不能干什么

- **Agent 的判断不是可靠的**——搜到了最新数据不等于入库的就是最新数据。Agent 可能在"筛选"步骤筛错。需要人工确认或规则约束。
- **不能替代原生 populate**的 agent 编排能力（并行子 agent、去重）。只适合 <100 行的中小规模数据集。
- **Admin Key 写入的数据不会出现在用户 UI 里**——除非设了 visibility=public。

## 关联 Skills

- `bigset-agent-integration` — Agent 集成模式完整指南
- `bigset-deployment` — BigSet 部署
- `self-hosted-convex-api` — Convex HTTP API 调用
