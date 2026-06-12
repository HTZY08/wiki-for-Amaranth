---
title: 异步任务委派系统（Async Delegate）
description: 基于 Hermes Kanban 的多 profile 异步任务处理架构，将大任务拆解后后台执行，前台保持响应
---

## ① 演化脉络：从串行阻塞到异步委派

### 起点：delegate_task 的同步困境

Hermes Agent 内置的 `delegate_task()` 提供子 agent 能力，但问题是**同步阻塞的**——主 agent 派发子任务后必须等待所有子任务完成才能继续响应。这在以下场景中成为瓶颈：

- 复合任务拆解为 3+ 子任务时，总耗时 = 各子任务串行之和
- 用户派发任务后无法中途插话或提出新需求
- 子 agent 崩溃后无恢复机制，整个链路卡死

社区对此的诉求体现在 GitHub issues [#41889](https://github.com/NousResearch/Hermes-Agent/issues/41889)（delegate_task 跨 profile 支持）和 [#9459](https://github.com/NousResearch/hermes-agent/issues/9459)（profile 定义 + 委派集成）中，但截至当前尚未进入主分支。

### Kanban：内置的异步方案

Hermes 内建了 Kanban 系统——一个 SQLite 持久化的任务板，支持多 profile 协作、依赖链、自动派发。官方定位明确：

> "Kanban is a durable task board, shared across all your Hermes profiles, that lets multiple named agents collaborate on work without fragile in-process subagent swarms."

Kanban 的 dispatcher 运行在 gateway 进程中，按固定间隔轮询 `kanban.db`，将 `ready` 状态的任务派发给对应 profile 的 worker 进程。每个 worker 是一个独立 OS 进程，拥有完整的 Hermes 工具集。

### 从单 profile 到多 profile 特化

初始实现使用单一的万能 `worker` profile。但随着任务类型多样化（计算化学、文档写作、代码调试、研究分析），发现单 profile 在模型选择、行为规范、API key 权限上难以兼顾。解决方向是：

1. **按领域特化 profile**——每个 profile 持有精简后的 API key 集合（最小权限原则）
2. **双层模型架构**——执行层用快速模型（DeepSeek V4 Flash），分析层调用高端模型（Gemini 3.1 Pro / Claude Sonnet）
3. **前后台分离铁律**——主 agent 收到任务后先创建 kanban 卡片再回复用户，禁止在回复前做调研

## ② 瓶颈分类 vs 解决方向

### 瓶颈一：同步阻塞（P0）

**问题：** `delegate_task()` 同步等待，主 agent 被阻塞期间用户不可用。

**解决：** 全量迁移至 Hermes Kanban。任务通过 `hermes kanban create(title, body, assignee=worker, ...)` 创建，dispatcher 异步派发，主 agent 立即返回。任务状态通过 `kanban_show()` 查询，worker 通过 `kanban_comment()` 记录进度。

### 瓶颈二：Worker 崩溃无回收（P1）

**问题：** Worker 进程崩溃后任务卡在 `running` 状态，默认 4 小时后才回收。

**解决：** 调整 `dispatch_stale_timeout_seconds` 至 600（10 分钟），配合 `failure_limit: 3` 实现快速自动重试。超过超时的任务被 dispatcher 自动回收并重试或标记为 blocked。

### 瓶颈三：API Key 过权限（P0）

**问题：** Worker profile 克隆自主 profile，持有全部 API key（Tavily/Exa/GitHub/等），存在提示注入风险。

**解决：** 每个 profile 独立 .env，按最小权限原则保留仅执行任务必需的 key（DeepSeek / OpenRouter / SiliconFlow + 代理配置），其余全部移除。

### 瓶颈四：输出路径无限制（P0）

**问题：** Worker 可以写任意路径，存在覆盖系统配置的风险。

**解决：** 在 worker SOUL.md 中硬性约束 output_path 必须在白名单目录下，禁止写入 config.yaml / .env / SOUL.md / kanban.db 等关键文件。

### 瓶颈五：Shell 传参换行符丢失（P0）

**问题：** 通过 CLI 参数传递多行 body 时，shell 吃掉换行符，任务描述被压缩为一行。

**解决：** 创建辅助脚本通过 stdin 读取 body，保留原始换行符。

### 瓶颈六：Max Turns 耗尽卡死（P1）

**问题：** Worker 达到 `max_turns=90` 上限后进程被强制终止，任务卡在 `running` 状态。

**解决：** 在 SOUL.md 中要求 worker 在剩余 turns ≤ 5 时主动调用 `kanban_block()`，不能静默耗尽。同时 dispatcher 的 stale timeout 作为二级兜底。

### 瓶颈七：完成验证缺失（P1）

**问题：** `kanban_complete()` 不校验产出文件是否真实存在，summary 是 worker 自述的。

**解决：** 在 SOUL.md 中规定完成前必须检查 output_path 文件存在 + frontmatter 完整。配合独立的验证脚本 `verify_wiki_output.py` 做二次确认。

## ③ 性能边界表

### 系统参数

| 参数 | 值 | 说明 |
|------|-----|------|
| dispatch_interval | 5s | Dispatcher 轮询间隔 |
| max_concurrent | 3 | 每 profile 同时运行的任务数 |
| failure_limit | 3 | 失败重试次数，超限后标记为 failed |
| stale_timeout | 600s（10min） | 任务卡死后自动回收 |
| worker max_turns | 90 | 每 worker 最大对话轮数 |
| kanban DB | SQLite | 单文件持久化，WAL 模式 |
| DB 大小（实测 ~130KB） | 9 个历史任务 | ID 从 t_ 开始递增 |

### Profile 参数

| Profile | 主模型 | 副模型 | .env key 数 | 专精领域 |
|---------|-------|-------|-----------|---------|
| worker | DeepSeek V4 Flash | — | 5 | 通用任务 |
| compute | DeepSeek V4 Flash | Gemini 3.1 Pro | 5 | ORCA/xtb/docking |
| code | DeepSeek V4 Flash | Claude Sonnet | 5 | 脚本/coding/debug |
| writer | Claude Sonnet | DeepSeek V4 Flash | 5 | Wiki/翻译/润色 |
| researcher | Gemini 3.1 Pro | DeepSeek V4 Flash | 5 | 文献/深度分析 |

### 任务生命周期

```
创建（ready）→ 派发（running）→ 完成（done）
                                    → 阻塞（blocked，需人工介入）
                                    → 失败后重试（failure_limit 次内自动重试）
                                    → 超时回滚（stale_timeout 后重置为 ready）
```

### 实测基准

| 场景 | 耗时 | 说明 |
|------|------|------|
| 单文件创建任务 → 完成 | ~35s（含 5s dispatch + 30s worker） | 简单文件写入 |
| 5 个并行任务批量完成 | ~2min（并发 3，排队 2） | 目录重组测试 |
| worker 冷启动 | ~10-15s | MCP 连接 + skill 加载 |
| kanban create 单次 | <1s | CLI 调用 |
| kanban list | <0.5s | SQLite 查询 |

### 安全边界

| 维度 | 保障措施 |
|------|---------|
| API key 泄露 | Worker .env 精简至 5 key，无第三方支付/存储类 key |
| 文件系统越权 | Output path 白名单 `/opt/data/workflow/` |
| 提示注入 | Worker 不执行用户直接输入的 prompt，仅执行卡片 body |
| 任务隔离 | 每个 worker 独立进程，互不共享 memory/sessions |
| 崩溃恢复 | Stale timeout 600s + failure_limit 3 自动处理 |
