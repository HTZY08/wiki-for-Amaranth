---
title: Anthos：设计、迭代与方法论
description: Anthos 独立 agent 系统的完整设计迭代史——四维共振引擎、五阶段 Pipeline、信号飞轮方法论
---
# Anthos：设计、迭代与方法论

> 归档日期：2026-07-19
> 类别：工程范式 / 架构
> 标签：anthos, 架构设计, agent系统, 信号飞轮, 方法论

---

## 一、为什么做 Anthos

### 出发点：不修别人的框架

Anthos 不做 Hermes 的 fork，做的是完全独立的 agent 系统。

| 系统 | 问题 |
|------|------|
| **Hermes** | 别人的框架。技能注册制、state.db 黑盒、插件笨重。改核心逻辑等上游更新。 |
| **OpenClaw** | 换壳类似品。不是自己的不能按自己意愿改。 |
| **现有工具链** | 搜索分散（单一 web_search）、状态无感知、记忆靠 LLM 上下文窗口。 |

**核心意志：** 所有 agent-core/ 代码是 Anthos 原生模块，不是 Hermes 插件。不读 Hermes state.db，不依赖 Hermes 主循环。存储走 `~/.anthos/` 路径。LLM/网络/工具/定时器全部自建。

### 设计目标

- 一个"不人机"的 agent 系统——自然对话，工具调用流畅，记忆和状态自主
- 四维共振替代 LLM 硬选工具——用图结构传播信息，不是靠 prompt 枚举
- 完全自持的存储和状态——不依赖外部框架的数据库和生命周期
- 渐进脱离——先在 Hermes 沙箱里建，数据在 `~/.anthos/`，模块全是 Anthos 自己的，逐步替换外部依赖

---

## 二、原型阶段：共振引擎与图搜索（v0.1-v0.12）

### 核心概念：四维共振

非 LLM 硬选工具——图结构传播共振：

```
v_{t+1} = α·M·v_t + (1-α)·v₀

查询 → v₀ 初始化(中英同义词)
     → PageRank 迭代(共现图+hub-penalty+跨平面折扣)
     → 四维排序输出: skill / tool / session / state
```

四维指的是：技能（skills）、工具（tools）、会话（sessions）、状态（state）。查询时不是让 LLM 从列表里选，而是图在四个维度上同时共振，相关性最高的节点自然浮现。

### 初始架构

```
agent-core/
├── anthos/resonance/   ← 四维共振引擎
│   ├── graph.py        共现图 + PageRank + hub-penalty
│   ├── index.py        四维索引器 (skill/tool/session/state)
│   ├── cluster.py      双路径分簇
│   ├── resonance.py    共振查询接口 (4-7ms)
│   ├── session.py      AnthosSessionStore (SQLite, ~/.anthos/data/sessions.db)
│   ├── state.py        AnthosStateMonitor (三态: 进程/服务/网络)
│   └── store.py        原子写入持久化 (~/.anthos/data/resonance/)
├── graph_search/       ← 图搜索引擎 (SearXNG+Bing+DDG+Archive 四后端聚合)
└── agent.py            主循环骨架
```

### Pipeline：五阶段契约管线

```
Resonate → Filter → Decide → Execute → Feedback
```

每个阶段都是纯函数，输入输出由 dataclass 契约约束。Runner 做编排，Trace 做审计。50 行一个 stage，整个 pipeline 约 200 行。

### 阶段说明

| 阶段 | 功能 | 关键设计 |
|------|------|----------|
| Resonate | 查询 + 上下文 → 四维排序输出 | 共振图 + 同义词扩展 |
| Filter | 工具 + 状态快照 → 移除宕机/降级工具 | 硬约束——宕机工具不进 LLM prompt |
| Decide | 过滤后的工具 + 技能 + 状态 → LLM 选择 | 给 LLM 的选项经过共振排序和状态过滤 |
| Execute | 工具 + 参数 → 执行结果 + 回退链 | 预定义回退链：web_search→web_extract→... |
| Feedback | 查询 + 工具 + 状态 → 图边更新 | 每次执行后更新共现图权重 |

### 回退链设计

```python
FALLBACK_MAP = {
    "web_search": ["web_search", "web_extract"],
    "web_extract": ["web_extract", "browser_navigate"],
    "read_file": ["read_file", "terminal"],
    "execute_code": ["execute_code", "terminal"],
}
```

关键：不在 stage 内部写 try-except，而是通过预定义的链式回退处理失败。失败信息写入 trace 不吞没。

### 评估指标

- 64 节点 / 333 边共现图
- 8/8 查询正确
- 共振查询 4.7-7.0ms
- 全 Python 标准库，零外部依赖

### 诞生

**2026-07-17** —— 连续数小时的设计对话，从看到 Hermes 搜索"不善于联网"的痛点出发，逐步推导出四维共振的设计。用户和 Iris 反复讨论、修正、推翻，从 12 点到凌晨。最终产出的 v0.1 设计覆盖了共振引擎、图搜索、状态监控、会话存储等核心模块。这是 Anthos 的原点。

---

## 三、Phase 2：运行时与工具系统（v0.13）

### 设计目标

从原型到可运行的 agent 系统——添加 WorkflowEngine、工具注册、能力模型、网关。

### 核心组件

**WorkflowEngine —— 单一持久化状态机**

WorkflowEngine 是整个系统的唯一编排层。在产生外部效果之前持久化状态。把运行时分割成 5 个阶段（Plan → Approve → Decide → Execute → Reflect），每个阶段由独立的 stage 处理。状态机确保任务在崩溃后可从最近的保存点恢复。

**能力模型（CapabilityProfile）**

每个工具注册时带有不可变的 CapabilityProfile，包含路径/域名/命令/速率/审批等约束。PipelineRunner 在执行前加一个能力检查钩子，未批准的调用不会产生任何外部效果。

**工具注册（ToolRegistry）**

```
ToolDef = {fn, schema, capability_profile, timeout, rate_limit}
```

所有工具都是 `dict → dict` 函数，注册时携带完整的元数据。Registry 提供类型验证、去重、注册、查找功能。

**网关层（GatewayManager）**

CLI 网关和 Feishu HTTP API。网关只做协议转换，不修改任务语义。GatewayManager 统一管理任务提交、审批回复解析、结果下发和阻塞监听。

### 架构总览

```
                    ┌─────────────┐
                    │  Gateway    │ CLI / Feishu / Matrix
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │WorkflowEngine│ 持久化状态机
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │PipelineRunner│ 5 阶段执行
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼────┐ ┌────▼───┐ ┌─────▼────┐
        │ Planner  │ │ Stages │ │ Trace    │
        │ (能力检查)│ │(执行)  │ │ (审计)   │
        └──────────┘ └────────┘ └──────────┘
              │
        ┌─────▼───────┐
        │ ToolRegistry │ 统一工具注册
        └─────────────┘
```

### 关键决策

1. **状态先持久化再执行** —— 任何外部效果前，先把 RUNNING 状态写入 SQLite。保证崩溃后恢复。
2. **审批是不可绕过的能力检查** —— 审批依附于 CapabilityProfile，不是 UI 层。写死 `requires_approval=False` 才能绕过。
3. **CapabilityProfile 不可变** —— 工具注册后能力配置不可修改，防止运行时篡改。
4. **网关不修改任务语义** —— 只做协议适配，不添加/删除/修改任务内容。
5. **审计默认开启** —— 每个 turn 产生 PipelineTrace，记录每个阶段的时序、契约名和错误。

### 关键缺陷（后验发现）

1. **审批作为硬障碍 vs 用户期望** —— CapabilityProfile 默认 `requires_approval=True`。用户期望的是工具直接跑，不是弹窗审批。这导致了 v0.15 的核心修复之一。
2. **工具注册后不可变** —— 虽然安全，但运行时调试困难。需要热替换机制。
3. **Pipeline 是线性一次性的** —— 一个 turn 只执行一次 Decide → Execute，不会多次工具调用。

---

## 四、Phase 3：LLM 层、多提供商、MOA 与 Codex（v0.14）

### 设计目标

从一个同步 LLM 端点升级为凭证隔离、多提供商的运行时。增加 MOA（混合专家投票）、上下文压缩、工作流模式学习、Codex 配对。

### 核心组件

**加密凭证存储（SecretStore + KeyRotator）**

- AES-256-GCM 加密凭证文件
- 唯一 96-bit nonce + 提供商绑定 AAD
- 原子替换，原子轮转
- 健康状态 + 加权选择 + 日预算 + 熔断恢复

**多提供商 LLM（LLMRouter）**

```
SecretStore → KeyRotator → LLMRouter → OpenAICompatLLM(provider1)
                                    → OpenAICompatLLM(provider2)
                                    → Fallback...
```

- 兼容 OpenAI 格式的同步/流式/工具调用
- 提供商故障自动切换
- 熔断冷却期
- 失败不暴露凭证

**上下文压缩（ContextCompressor）**

创建不可变的会话前缀 + 有界的任务种子。自适应压缩比例，确定性缓存键。

**MOA（Mix of Agents）**

在 LLM 决策前加一个可选的专家投票层：
1. 触发启发式判断是否启用 MOA
2. 相同前缀并行发给多个"专家"模型
3. 收集部分成功结果
4. 主模型综合合成

MOA 是 Runtime 注入的可选组件，不是工具，不能绕过任务/能力状态。

**工作流模式学习（A11-A15 原子模块）**

```
A11  PatternStore      → 完成的任务变成模式
A12  PatternCluster    → 确定性序列/标签相似度分簇
A13  PatternScorer     → 打分排序
A14  PatternRecommend  → 推荐附加到任务上下文
A15  FailureChain      → 失败记录 + 有界因果窗口
```

**Codex 配对网关**

- HTTP 协议适配器
- 短期配对码（已哈希、一次性、可过期）
- 加密长期凭证
- 3 个审批控制工具
- 端点只允许 HTTP(S)

### 关键决策

1. **凭证不落地明文** —— 登录内存即加密，失败不暴露 API key。AES-256-GCM + 提供商绑定 AAD，防止跨提供商误用。
2. **LLM 路由层透明** —— LLMRouter 对上层表现为单一 LLM 接口，failover/熔断/重试全在图内部。
3. **MOA 不创建第二个状态机** —— MOA 是 Runtime 里可选的 advisory layer，不是独立的状态执行路径。不影响任务持久化和能力检查。
4. **模式学习是追加式的** —— 按 task_id 去重，SQLite 参数化查询，增量迁移。

---

## 五、v0.15：搜索修复与共振引擎重构

### 背景：系统上线后第一个巨坑

Phase 2 和 Phase 3 都是离线/半在线开发，实际部署上线后，核心用户体验问题暴露：**搜索不可用**。

用户说"搜索"时，系统回复"不善于联网"——这是诚实的，因为搜索链路两层都断了。

### 根因分析

**第一层：底层搜索 API 不对**

```
tools/web_search.py → DuckDuckGo Instant Answer API
                    （api.duckduckgo.com/?format=json）
```

这不是搜索引擎。这个 endpoint 只返回"零点击回答"（定义、天气之类），不是网页搜索结果。VPS 直连它 15 秒超时/空响应。

而 VPS 端口 8888 有现成的 SOCKS5 代理，搜索工具根本没用它。

**第二层：LLM 没有 tool calling 循环**

ChatSkill 的逻辑是：
```
如果用户输入包含"搜索"二字 → 调一次 search → 字符串拼进 prompt → 单次调用
```

LLM 根本不知道有搜索工具可用（没传 tools schema），不会主动说"我需要查一下这个"。搜索触发的唯一条件是用户说"搜索"。

而且即便传了 tools schema，也没有 tool calling 循环去处理 `tool_calls` 返回。

### 修复方案：三层改造

**1. 搜索后端更换**

从 DDG Instant Answer → SearXNG（自建 Docker 实例）

- SearXNG 支持多搜索引擎聚合（Google、Bing、DDG 等）
- 通过 SOCKS5 代理出海
- 返回标准化 JSON 格式，带标题/URL/摘要
- 本地部署无 API 费用

**2. 代理接入**

在 `config.py` 中恢复 `proxy_url` 字段。所有网络工具通过 SOCKS5 代理出海。

**3. tool calling 循环（未完成）**

Pipeline 需要从单次 Decide → Execute 改为循环：
- LLM 返回 tool_calls → 执行 → 结果写回 → LLM 再次推理 → 直到 LLM 返回自然语言
- 每次结果注入到下一次 LLM 调用的消息历史中
- 最大循环次数限制防止无限

### 共振引擎改进：阈值下调与中文适配

共振引擎的 `_build_v0` 方法中，共振阈值从 0.01 降至 0.001。因为中文场景下的共现权重天然低于英文（中文分词粒度和共现稀疏性不同）。

同时添加 CN_EN_MAP 标签映射，覆盖事实性问句（如"今天星期几"这类直接命中 web_search 但被共振阈值筛掉的问题）。

### SearXNG 中文引擎问题

SearXNG 默认的 Google CSE 引擎对中文查询返回质量差（"周杰伦"搜索返回 "Currency Converter"）。需要：
1. 调整 SearXNG 引擎权重——增加 Bing/Baidu/DDG 的中文排名
2. 或通过 SOCKS5 代理优先路由到 Bing
3. 或实现查询语言检测 + 中文专用引擎路由

---

## 六、信号飞轮：架构反思

### 从"工具链"到"信号链"

Phase 3 的调试过程暴露了一个深层问题：**我们一直在修工具链，但系统的问题出在信号链上。**

工具链思维是线性的：

```
用户输入 → LLM 理解 → 选择工具 → 执行工具 → 返回结果
```

信号链思维是网络化的：

```
用户输入进入共振图 → 激活关联节点 → 多路径信号传播 → 动态权重汇聚 → 决策涌现
```

工具链思维的结果是：每一环都要精确调优，一环断全链断（搜索 API 一层断，整个系统就不能搜索了）。

信号链思维的结果是：信号在图中自然扩散，即使一条路径弱了，其他路径的信号会补充。

### 类比：Claude 的数据飞轮 vs 高盛的信号飞轮

这个思路的灵感来自之前讨论过的两个模式：

- **Claude 的数据飞轮**——用户每次对话产生数据，数据训练模型，模型更好用，更多用户来用。闭环在数据层面。
- **高盛的信号飞轮**——各种来源的信号汇聚，噪声被过滤，有效信号增强，更好的信号吸引更多的数据源。闭环在信号层面。

Anthos 的共振引擎天然是信号飞轮的架构：工具/技能/会话/状态四类信号在同图上共振，每次查询和反馈都在增强或削弱连接权重。

### 关键启示

1. **不要替 LLM 选工具——让信号自己走通**
   - 之前的 pipeline 是在 Decide 阶段让 LLM 从过滤后的工具列表里硬选一个。现在是共振图把最相关的工具/技能推到前面，LLM 做最后确认。
   - 即使共振排名不完美，LLM 也有完整的上下文做判断，而不是从 20 个工具里选 1 个。

2. **失败也是信号——回退链不吞没错误**
   - 回退链不是错误处理，而是信号衰减路径。web_search 失败 → web_extract 尝试 → 信号在图上的权重自然降低。
   - 失败信息写入 trace，不吞没，不 try-except 隐身。

3. **状态监控是共振的一部分，不是单独的告警系统**
   - 服务宕机 → 状态节点权重归零 → 关联工具共振削减 50% → 工具自然不出现在决策上下文中。
   - 不是硬编码 `if service_down: skip tool`，而是信号层面的软衰减。

### 方法论总结

| 旧思维（工具链） | 新思维（信号链） |
|------------------|------------------|
| 线性管道，一环接一环 | 网络化共振，多路径并行 |
| 精确调优每一环 | 让信号在图中自然扩散 |
| 错误处理堆叠 try-except | 失败也是信号，写入 trace |
| 硬开关控制工具可见性 | 软衰减调整工具权重 |
| LLM 从列表中硬选 | 共振排序 + LLM 确认 |
| 修搜索 = 换 API + 加代理 | 修搜索 = 搜索节点 + 代理节点 + 中文引擎 = 复合修复 |
| 每一步需要人工标注 | 反馈自动更新图权重 |

---

## 七、设计原则与方法论

### 原则一：契约先行，而非实现先行

每个组件先定义输入输出契约（dataclass），实现之后补。Pipeline 的五个阶段、WorkflowEngine 的状态转换、工具函数的 `dict → dict` 签名——全是先有契约后有实现。

好处：
- 测试可以 mock 任何阶段
- 组件替换不影响接口
- 文档自动产生（契约即文档）

### 原则二：状态先于效果

WorkflowEngine：RUNNING 持久化之后，才执行工具。
SecretStore：凭证加密之后，才出站。
CapabilityProfile：安全检查通过之后，才执行。

这是电信行业的"write-ahead logging"原则在 agent 系统里的映射。

### 原则三：审计默认开启

每个 turn 产生 PipelineTrace，记录时序、契约名、错误。不是调试模式才开，是默认行为。Trace 数据既是调试依据，也是模式学习的输入。

### 原则四：回退链不吞没错误

回退链（web_search → web_extract → browser_navigate）不是兜底 try-except，是信号衰减路径。每一步失败写入 trace，L1/L2/L3 三级错误语义清晰：

| 级别 | 含义 | 行为 |
|------|------|------|
| L1 | 契约违规（类型不对） | 立即抛出 PipelineError |
| L2 | 阶段失败（工具超时、LLM 挂） | 回退链，下一个候选 |
| L3 | 不可恢复（DB 损坏、import 错误） | 返回错误 dict |

### 原则五：分层架构但避免层间泄露

```
Gateways → WorkflowEngine → PipelineRunner → ToolRegistry → 实际执行
```

网关不知道工具的 schema，WorkflowEngine 不知道网关的协议，工具不知道 WorkflowEngine 的状态。层间只通过契约（dataclass/typed dict）通信。

唯一例外：CapabilityProfile 的审批需求会穿透到 Gateway（需要用户确认），但能力检查逻辑本身在 PipelineRunner 层，Gateway 只做展示和回传。

### 原则六：调试优先于优化

"修复搜索链"远比"让共振引擎跑进 3ms"优先。每次迭代先保证系统可用，再追求性能。

### 原则七：信号链优于工具链

这个原则在第六部分详细展开。核心：不设计"精准的路径"，设计"信号可以在图里走通"。

### 与 Hermes/OpenClaw 的本质区别

| 维度 | Hermes | Anthos |
|------|--------|--------|
| 认知 | LLM prompt 编排 | 四维共振图 + PageRank |
| 知识 | 技能注册制 | 文件扫描 + 共现图谱 + 分簇 |
| 搜索 | web_search 单体 | graph_search 四后端聚合（后改为 SearXNG） |
| 会话 | state.db（黑盒） | SQLite 自有 Schema |
| 状态 | 无 | 三态监控 → 共振注入 |
| 存储 | Hermes 内部 | ~/.anthos/ 完全自持 |
| 可修改性 | 等上游更新 | 想改哪改哪 |

---

## 八、版本迭代记录

| 版本 | 日期 | 核心变化 | 状态 |
|------|------|----------|------|
| v0.1 | 2026-07-17 | 设计文档：四维共振、图搜索、五阶段 pipeline | ✅ 设计 |
| v0.12 | 2026-07-17 | P0-P2 缺陷修复、配置层、调度器、工具注册、CLI 入口 | ✅ 离线测试 |
| v0.13 | 2026-07-17 | Phase 2：WorkflowEngine、能力模型、审批、网关、6 核心工具 | ✅ 离线测试 |
| v0.14 | 2026-07-17 | Phase 3：加密凭证、多提供商 LLM、MOA、Codex、模式学习 | ✅ 离线测试 |
| v0.15 | 2026-07-18 | 搜索修复：SearXNG、代理接入、approval 绕过、共振阈值下调 | ⚠️ 生产部署（tool calling 未完成） |

### 当前状态（2026-07-19）

- 生产网关运行中（Feishu websocket）
- 搜索已验证可用（单次搜索返回真实新闻结果）
- 多轮工具调用未实现（一次消息只执行一个工具）
- 中文搜索质量待优化（SearXNG 中文引擎配置）
- Codex 规格书已出，等待落地

### 已知问题（待解决）

1. **多轮工具调用** —— Pipeline 需要 tool calling 循环，一次消息可触发多个工具。
2. **中文搜索质量** —— SearXNG 中文引擎须调整权重或换用 Baidu/Bing。
3. **搜索结果展示** —— 当前只展示 3/10 个结果，用户期望看全。
4. **Gateway 超时** —— 当前 1800 秒，多轮调用需要更长的代理级超时。
5. **模式学习离线** —— A11-A15 模块在 Phase 3 实现但未接入运行时。
6. **Wiki 内容同步** —— 这个文档需要定期 ingest 到 Anthos 的共振引擎。

---

## 九、留给后续的思考

### 共振引擎作为认知架构的潜力

当前的共振引擎只在工具选择阶段使用。理论上，它可以扩展到：

- **对话状态跟踪** —— 用户意图不是单次匹配，而是在图上持续追踪信号路径
- **长期记忆融合** —— session 节点随着时间推移权重自然衰减，但不遗忘
- **多 agent 协调** —— 每个"花"是一组独立节点，跨节点共振实现协调

### 信号飞轮作为工程哲学

工具链思维是工业时代的产物——流水线、精确、可预测。信号链思维是信息时代的产物——网络、涌现、自适应。

Anthos 的共振引擎碰巧实现了信号链架构，但真正的问题是：**我们能否用信号链思维设计整个系统？**

不只在工具选择阶段用共振图——在搜索、记忆、状态监控、模式学习、甚至用户交互层面都用信号传播替代线性管道。

### Codex 落地之后的预期

- tool calling 循环 → 一次消息可触发多个工具
- 搜索 + 共振 + 信号链 → 系统从"搜索工具"升格为"认知系统"
- 技能/引用/wiki 内容同步 → 共振图的节点和边持续生长
- 网关稳定 → 全链路自持，不再需要 Hermes 回退

---

> 本文档对应的代码仓库：`agent-core/`（soul-garden-sync）
> 最后更新：2026-07-19

