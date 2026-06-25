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

## 0.11 Hermes 场景设计（Agent 工程范式）

> 区别于通用工程范式，这部分专攻 **AI Agent 本身的设计模式**——Hermes 的架构哲学、Agent 工作流模式、skill/记忆/工具的设计策略。

### 0.11.1 Hermes 自身架构（先了解自己）

```bash
# Hermes 完整架构文档（1.8MB，一键喂入）
/learn https://hermes-agent.nousresearch.com/docs/llms-full.txt

# Hermes 架构总览
/learn https://hermes-agent.nousresearch.com/docs/contributing/architecture
```

这是最优先的一条——让 Hermes 完整理解自己的全部能力、限制和扩展点。

### 0.11.2 Agent 通用设计模式（Anthropic 框架）

```bash
# 构建有效 Agent（Anthropic — 2024年最权威的Agent设计文章）
/learn https://www.anthropic.com/research/building-effective-agents

# Agent 工作流模式
/learn https://github.com/anthropics/anthropic-cookbook/tree/main/patterns/agents
```

覆盖 7 种核心模式：Prompt Chaining / Routing / Parallelization / Orchestrator-Workers / Evaluator-Optimizer / Autonomous Agents / Augmented LLM

### 0.11.3 Hermes Skill 设计范式

```bash
# Hermes Skill 系统
/learn https://hermes-agent.nousresearch.com/docs/user-guide/features/skills

# Curator — 技能自动维护
/learn https://hermes-agent.nousresearch.com/docs/user-guide/features/curator
```

**Skill 设计原则：**
- 一个 skill 解决一个明确的问题域
- 触发条件要精准（不泛化不过窄）
- 包含验证步骤和常见陷阱
- 定期用 curator 清理过时的 skill

### 0.11.4 记忆策略

```bash
# Hermes 记忆系统
/learn https://hermes-agent.nousresearch.com/docs/user-guide/features/memory

# 记忆提供者
/learn https://hermes-agent.nousresearch.com/docs/user-guide/features/memory-providers
```

**记忆设计原则：**
- USER.md：存不可变事实（姓名/角色/环境）
- MEMORY.md：存习惯性偏好和约束
- 不存临时状态、任务进度、已完成的工作日志
- 定期用 curator 清理过时的记忆

### 0.11.5 工具组合模式

```bash
# Hermes 工具系统
/learn https://hermes-agent.nousresearch.com/docs/user-guide/features/tools
```

**典型组合模式：**
- 调研：`web_search` → `web_extract` → 综合分析
- 开发：`delegate_task` (并行子任务) → 汇总验证
- 排错：`terminal` → `read_file` → `search_files` → 根因定位

### 0.11.6 多 Agent 编排

```bash
# 多 Agent 配置与协调
/learn https://hermes-agent.nousresearch.com/docs/user-guide/profiles

# 代码工作流（Git Worktrees）
/learn https://hermes-agent.nousresearch.com/docs/user-guide/git-worktrees
```

**编排模式：**
- 主 Agent（Orchestrator）拆任务
- 子 Agent（Worker）并行执行
- 每个 Worker 走独立 session + 独立终端
- 适合：大型重构 / 多文件调研 / 多维度分析

### 0.11.7 SOUL.md 人格设计

```bash
# Hermes 人格与 SOUL.md
/learn https://hermes-agent.nousresearch.com/docs/user-guide/features/personality
```

**SOUL.md 设计原则：**
- Identity & Core Posture：明确你是谁、你的判断框架
- Hard Constraints：不可违反的硬约束
- Style：语言风格、输出结构偏好
- Context Awareness：任务模式切换（分析/创意/闲聊）

### 0.11.8 Platform & Gateway 模式

```bash
# 消息网关
/learn https://hermes-agent.nousresearch.com/docs/user-guide/messaging/
```

**多平台策略：**
- 飞书：深度工作 + 文档协作
- 微信：轻量通知 + 快速问答
- Telegram：后台任务 + 定时报告
- 每个平台绑定不同的 personality

---

### 0.11.x Agent 学习循环（进阶）

```bash
# /learn 指令本身
# 已经在你当前的 Hermes 里了

# 闭环学习模式：
# 1. 遇到新问题
# 2. 分析 → 解决 → 反思
# 3. /learn 存为 skill
# 4. 下次同类问题自动调取
# 5. Curator 定期优化 stale skill
```

---

**建议：这一整节只用跑前两条就够了：**

1. **Hermes 完整架构** → `/learn https://hermes-agent.nousresearch.com/docs/llms-full.txt`
2. **Anthropic Agent 模式** → `/learn https://www.anthropic.com/research/building-effective-agents`

这两个喂完之后，Hermes 对自己是谁、Agent 系统怎么设计就有了完整的认知框架。剩下的 section 11.3-11.8 是按需补充。

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

### 推荐喂食顺序

最优先（先跑这两条，Hermes 能力质变）：
```
/learn https://hermes-agent.nousresearch.com/docs/llms-full.txt
/learn https://www.anthropic.com/research/building-effective-agents
```

然后按 P0 子类顺序：
```
0.1 设计模式 → 0.8 AI工程 → 0.2 架构 → 0.5 API设计
→ 0.9 工程哲学 → 0.3 分布式 → 0.6 测试 → 0.7 安全
→ 0.4 并发 → 0.10 系统基础
```

接着 P1-P5 按需补充。

### 注意事项
- `/learn` 一次处理一个源，给足够时间消化
- Hermes 完整架构 (llms-full.txt) 约 1.8MB，消化可能需要 1-2 分钟
- 国内网络访问 OpenStax/MIT OCW 慢，考虑走代理
- 喂完后用 `/skills` 确认 skill 已生成
- 定期跑 `/curator` 清理过时 skill

---

*Generated by Begonia @ 2026-06-25*
*For Amaranth's post-upgrade learning session*
