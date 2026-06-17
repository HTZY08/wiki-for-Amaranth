---
title: Async Delegate Profile
description: 基于 Hermes Kanban 的异步任务委派系统
---

# Async Delegate System

> 基于 Hermes Kanban 的多 Profile 异步任务处理架构。大任务拆解后交给后台 Worker 执行，前台保持响应。解决 `delegate_task()` 同步阻塞的问题。

**GitHub 仓库：** [`HTZY08/wiki-for-Amaranth` → `static/skills/async-delegate/`](https://github.com/HTZY08/wiki-for-Amaranth/tree/main/static/skills/async-delegate)

**直接下载：** [`hermes-async-delegate.tar.gz`](https://github.com/HTZY08/wiki-for-Amaranth/raw/main/static/skills/async-delegate/hermes-async-delegate.tar.gz)（3.4KB）

**License：** CC BY-NC-SA 4.0

---

## 背景

Hermes Agent 内置的 `delegate_task()` 提供子 agent 能力，但问题是同步阻塞的——主 agent 派发子任务后必须等待所有子任务完成才能继续响应。社区对此的诉求体现在 GitHub issues 中，但尚未进入主分支。

Kanban 是 Hermes 内建的异步任务队列，支持多 profile 协作、依赖链、自动派发。这套 skill 封装了"前后台分离"的最佳实践。

## 包含的文件

| 文件 | 功能 |
|------|------|
| **delegate/SKILL.md** | 核心 Skill：架构说明、配置参数、行为规则、Profile 模板 |
| **delegate/references/worker-SOUL.md** | Worker Profile 的 SOUL.md 模板，含失败处理、路径限制、完成验证 |
| **kanban-worker/SKILL.md** | Kanban Worker 行为指南，含 Retry 诊断、Block 策略、Recitation 模式 |

## 快速开始

```bash
# 下载并解压
wget https://github.com/HTZY08/wiki-for-Amaranth/raw/main/static/skills/async-delegate/hermes-async-delegate.tar.gz
tar xzf hermes-async-delegate.tar.gz -C ~/.hermes/skills/

# 初始化 Kanban
hermes kanban init

# 创建 Worker Profile
hermes profile create worker --clone

# 使用参考 worker-SOUL.md 更新 worker 的行为定义
```

## 核心参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| dispatch_interval | 5s | Dispatcher 轮询间隔 |
| stale_timeout | 600s（10min） | Worker 崩溃后自动回收 |
| failure_limit | 3 | 失败重试次数 |
| max_concurrent | 3 | 每 Profile 并发任务数 |

## Profile 模板

| Profile | 主模型 | 副模型 | 专精 |
|---------|-------|-------|------|
| worker | 通用 | — | 不明确分类的任务 |
| compute | 执行模型 | 分析模型 | 计算化学 |
| code | 执行模型 | 架构模型 | 编码/Debug |
| writer | 写作模型 | 执行模型 | 文档/翻译 |
| researcher | 分析模型 | 执行模型 | 文献/深度研究 |

## 关键经验

- **前后台分离铁律**：先创建卡片再回复用户，禁止在回复前做调研
- **最小权限**：Worker .env 只保留必要的 API Key，移除所有第三方服务 Key
- **路径白名单**：限制 Worker 只能写入指定输出目录，防止覆盖系统配置
- **Stale Timeout**：Worker 崩溃后 10 分钟自动回收，避免任务永久卡死
- **分层模型**：执行用快速模型，复杂分析调高端模型（Gemini Pro / Claude）
- **🧠 Recitation 模式（新增）**：复杂任务中 worker 自动在 workspace 维护 `todo.md`，每步更新全局目标到上下文末尾，对抗 "lost in the middle"。详见 kanban-worker/SKILL.md

## 链接

| 资源 | 链接 |
|------|------|
| GitHub 仓库 | [github.com/HTZY08/wiki-for-Amaranth](https://github.com/HTZY08/wiki-for-Amaranth) |
| Skill 文件目录 | [static/skills/async-delegate/](https://github.com/HTZY08/wiki-for-Amaranth/tree/main/static/skills/async-delegate) |
| 直接下载 tar.gz | [hermes-async-delegate.tar.gz](https://github.com/HTZY08/wiki-for-Amaranth/raw/main/static/skills/async-delegate/hermes-async-delegate.tar.gz) |
| License | CC BY-NC-SA 4.0 |
