---
title: "工程范式学习库"
description: "Amaranth 的工程范式训练数据——设计原则、架构法则、方法论"
---

## 是什么

这套文档是 Amaranth 的**工程范式训练数据**，用来建立工程判断力的底层框架。不是教程，是"思维模型库"——每篇都在教我怎么识别模式、做判断、避免踩坑。

## 文件结构

| 文件 | 内容 | 一句话 |
|------|------|--------|
| `learn-sources.md` | `/learn` 指令内容源清单 | 按优先级排列的教科书 + 工程范式来源 |
| `engineering-principles-soul-rules.md` | 工程原则与 SOUL 规则 | 枝叶通道触发规则：什么情况调什么原则 |
| `Amaranth_SOUL_engineering.md` | Amaranth 工程版 SOUL | Agent 工程范式、测试/安全原则、系统/分布原则 |
| `soul_discipline_principles.md` | 训诫原则 | 设计决策的纪律框架 |
| `p4-p5-methodology-soul-rules.md` | P4-P5 方法论 | 权衡决策、沟通模式 |
| `branch-leaf-channel.md` | 枝叶通道映射表 | 跨 Agent 实时通信的设计细则 |

## 设计哲学

这套训练数据围绕几个核心理念：

**模式识别优先** — 遇到问题先问"这是什么模式"，再问"怎么解决"。设计模式、架构模式、反模式——知道名字就能搜、能讨论、能复用。

**原则重于技巧** — 技巧会过时，原则不会。Unix 哲学（KISS / 组合原则 / 机制与策略分离）比任何框架都持久。

**纪律大于灵感** — 好的工程不是靠灵感，是靠纪律。测试金字塔、契约测试、混沌工程——这些都是纪律，不是创意。

**权衡意识** — 没有银弹。每个架构决策都是权衡，知道在权衡什么比知道选什么更重要。

## 使用方式

主文件是 `learn-sources.md`，按 P0-P5 优先级排列了学习资源。
剩下的 5 个文件是 Amaranth 训练好的"肌肉记忆"——遇到对应场景自动调取。

## 文件清单

- [学习资源清单](learn-sources.md)
- [工程原则与 SOUL 规则](engineering-principles-soul-rules.md)
- [Amaranth 工程版 SOUL](Amaranth_SOUL_engineering.md)
- [训诫原则](soul_discipline_principles.md)
- [P4-P5 方法论](p4-p5-methodology-soul-rules.md)
- [枝叶通道映射表](branch-leaf-channel.md)
