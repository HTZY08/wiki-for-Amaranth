# Amaranth /learn 内容源清单

> 面向 Amaranth 的 `/learn` 指令，高质量教科书 + 工程范式内容源
> 按优先级排列

---

## P0 — 工程范式（最优先，Hermes 日常用得最多）

工程范式是 Hermes 最核心的能力提升——直接影响代码分析、架构设计、排错推理的质量。

### 0.1 经典设计模式

```bash
# GoF 设计模式全系（创建型/结构型/行为型）
/learn https://refactoring.guru/design-patterns

# 企业集成模式（EIP）— 消息路由、转换、端点
/learn https://www.enterpriseintegrationpatterns.com/patterns/messaging/

# 重构模式
/learn https://refactoring.guru/refactoring
/learn https://martinfowler.com/books/refactoring.html

# 反模式 — 知道什么不该做比知道该做什么更重要
/learn https://sourcemaking.com/antipatterns
```

### 0.2 架构模式

```bash
# 系统设计
/learn https://github.com/donnemartin/system-design-primer
/learn https://microservices.io/patterns/index.html
/learn https://martinfowler.com/architecture/

# 领域驱动设计（DDD）
/learn https://www.dddcommunity.org/resources/
/learn https://martinfowler.com/tags/domain%20driven%20design.html

# 云架构模式
/learn https://learn.microsoft.com/en-us/azure/architecture/patterns/
/learn https://aws.amazon.com/architecture/well-architected/
/learn https://cloudpatterns.io/

# CQRS + 事件溯源
/learn https://martinfowler.com/bliki/CQRS.html
/learn https://microservices.io/patterns/data/event-sourcing.html

# 事件驱动架构
/learn https://www.enterpriseintegrationpatterns.com/patterns/messaging/
```

### 0.3 分布式系统

```bash
# 分布式系统模式
/learn https://www.patternsofdistributedsystems.com/
/learn https://github.com/aphyr/distsys-class  # Jepsen 分布式系统课程

# 共识算法
/learn https://raft.github.io/
/learn https://lamport.azurewebsites.net/pubs/paxos-simple.pdf

# 分布式计算
/learn https://book.mixu.net/distsys/
/learn https://www.allthingsdistributed.com/
```

### 0.4 并发 & 并行

```bash
# 并发模式（Go）
/learn https://go.dev/blog/pipelines
/learn https://go.dev/talks/2012/concurrency.slide

# Actor 模型
/learn https://www.brianstorti.com/the-actor-model/

# 无锁数据结构
/learn https://preshing.com/archives/
```

### 0.5 API & 协议设计

```bash
# REST 成熟度模型
/learn https://martinfowler.com/articles/richardsonMaturityModel.html

# GraphQL 设计
/learn https://graphql.org/learn/

# gRPC 模式
/learn https://grpc.io/docs/guides/

# HTTP API 设计指南
/learn https://github.com/microsoft/api-guidelines
/learn https://opensource.zalando.com/restful-api-guidelines/
```

### 0.6 测试 & 质量

```bash
# 测试金字塔
/learn https://martinfowler.com/articles/practical-test-pyramid.html

# 契约测试
/learn https://docs.pact.io/

# 混沌工程
/learn https://principlesofchaos.org/

# 属性基测试
/learn https://hypothesis.works/articles/what-is-property-based-testing/
```

### 0.7 安全模式

```bash
# OWASP Top 10
/learn https://owasp.org/www-project-top-ten/

# 身份认证模式
/learn https://oauth.net/2/
/learn https://openid.net/connect/

# 安全架构
/learn https://www.oswap.org/
```

### 0.8 AI/ML 工程范式

```bash
# RAG 架构
/learn https://docs.llamaindex.ai/
/learn https://www.langchain.com/

# Agent 架构
/learn https://blog.langchain.dev/agentic-design-patterns/

# Prompt 模式
/learn https://github.com/dair-ai/Prompt-Engineering-Guide

# MCP 协议
/learn https://modelcontextprotocol.io/
```

### 0.9 工程哲学 & 方法

```bash
# Unix 哲学
/learn https://catb.org/~esr/writings/taoup/html/

# Google SRE
/learn https://sre.google/books/

# 12 Factor App
/learn https://12factor.net/

# 事后剖析文化
/learn https://sre.google/sre-book/postmortem-culture/

# 工程管理
/learn https://www.oreilly.com/radar/topics/software-architecture/
```

### 0.10 系统基础

```bash
# 操作系统（OSTEP）
/learn https://pages.cs.wisc.edu/~remzi/OSTEP/

# 数据库模式
/learn https://db-book.com/
/learn https://www.postgresql.org/docs/current/

# 网络核心
/learn https://book.systemsapproach.org/

# 编译原理
/learn https://www.dragonbook.com/
```

**为什么先学这些：** Hermes 日常工作（分析/设计/排错/写代码）直接受益于这些范式。设计模式帮助理解代码结构，系统设计帮助推理大规模架构，Unix 哲学是工程判断力的底层。建议按 0.1 → 0.8 → 0.2 → 0.5 → 0.9 → 0.3 → 0.6 → 0.7 → 0.4 → 0.10 的顺序吃。

---

## P1 — 计算机科学核心

```bash
# 算法
/learn https://jeffe.cs.illinois.edu/teaching/algorithms/
/learn https://www.cs.princeton.edu/~wayne/kleinberg-tardos/

# 计算机系统（CMU 15-213）
/learn https://www.cs.cmu.edu/~213/

# 计算机网络
/learn https://book.systemsapproach.org/

# 数据库
/learn https://db-book.com/   # 或找打孔机的免费章节
/learn https://www.postgresql.org/docs/current/

# 编译原理
/learn https://www.dragonbook.com/
```

---

## P2 — 数学基础

```bash
# 数学全系列（OpenStax）
/learn https://openstax.org/subjects/math

# MIT OCW 数学
/learn https://ocw.mit.edu/search/?q=mathematics

# 线性代数
/learn https://openstax.org/details/books/intermediate-algebra-2e
/learn https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab

# 概率与统计
/learn https://openstax.org/details/books/introductory-statistics-2e
/learn https://probabilitycourse.com/
```

---

## P3 — 物理与工程

```bash
# OpenStax 物理
/learn https://openstax.org/details/books/college-physics-2e
/learn https://openstax.org/details/books/university-physics-volume-1
/learn https://openstax.org/details/books/university-physics-volume-2
/learn https://openstax.org/details/books/university-physics-volume-3

# MIT OCW 物理
/learn https://ocw.mit.edu/search/?q=physics
```

---

## P4 — 生物学 & 医学

```bash
# OpenStax 生物
/learn https://openstax.org/details/books/biology-2e
/learn https://openstax.org/details/books/anatomy-and-physiology-2e

# 默沙东诊疗手册（免费版）
/learn https://www.msdmanuals.com/professional
```

---

## P5 — 经济 & 社科

```bash
/learn https://openstax.org/details/books/principles-economics-3e
/learn https://openstax.org/details/books/principles-microeconomics-3e
/learn https://openstax.org/details/books/principles-macroeconomics-3e
/learn https://openstax.org/details/books/psychology-2e
```

---

## 方法论 & 写作

```bash
# 写作
/learn https://owl.purdue.edu/owl/purdue_owl.html   # Purdue OWL 写作指南
/learn https://www.chicagomanualofstyle.org/home.html

# 学习方法
/learn https://fs.blog/mental-models/
/learn https://commoncog.com/
```

---

## 使用建议

### 批量学习
每次打开一个 `/learn` 会话，喂一个源：

```
/learn https://refactoring.guru/design-patterns
```

Hermes 会提取核心知识存成 skill。以后相关语境下自动调取。

### 优先级
1. **P0 工程范式** — 先跑完这 7 条，工作质量提升最明显
2. **P1 计算机核心** — 算法+系统+网络+数据库
3. **P2-P5** — 按需补充广度

### 注意事项
- `/learn` 一次处理一个源，给足够时间消化
- 国内网络可能访问 OpenStax/MIT OCW 慢，考虑走代理
- 喂完后用 `/skills` 确认 skill 已生成

---

*Generated by Begonia @ 2026-06-25*
*For Amaranth's post-upgrade learning session*
