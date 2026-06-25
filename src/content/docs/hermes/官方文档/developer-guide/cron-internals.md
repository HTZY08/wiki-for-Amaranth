---
sidebar_position: 11
title: "Cron 内部机制"
description: "Hermes 如何存储、调度、编辑、暂停、加载技能（Skill）并投递 cron 任务"
---

# Cron 内部机制

Cron 子系统提供计划任务执行——从简单的单次延迟到带有技能注入和跨平台投递的重复 cron 表达式任务。

## 关键文件

| 文件 | 用途 |
|------|------|
| `cron/jobs.py` | 任务模型、存储、对 `jobs.json` 的原子读写 |
| `cron/scheduler.py` | 调度器循环——到期任务检测、执行、重复跟踪 |
| `tools/cronjob_tools.py` | 面向模型的 `cronjob` 工具注册与处理器 |
| `gateway/run.py` | 网关集成——长期运行循环中的 cron 滴答 |
| `hermes_cli/cron.py` | CLI `hermes cron` 子命令 |

## 调度模型

支持四种调度格式：

| 格式 | 示例 | 行为 |
|------|------|------|
| **相对延迟** | `30m`, `2h`, `1d` | 单次触发，在指定时长后执行 |
| **间隔** | `every 2h`, `every 30m` | 重复触发，按固定间隔执行 |
| **Cron 表达式** | `0 9 * * *` | 标准 5 字段 cron 语法（分钟、小时、日、月、星期） |
| **ISO 时间戳** | `2025-01-15T09:00:00` | 单次触发，在精确时间执行 |

面向模型的接口是一个单一的 `cronjob` 工具，支持动作式操作：`create`、`list`、`update`、`pause`、`resume`、`run`、`remove`。

## 任务存储

任务存储在 `~/.hermes/cron/jobs.json` 中，采用原子写入语义（先写入临时文件，再重命名）。每个任务记录包含：

```json
{
  "id": "a1b2c3d4e5f6",
  "name": "每日简报",
  "prompt": "总结今日 AI 新闻与融资轮次",
  "schedule": {
    "kind": "cron",
    "expr": "0 9 * * *",
    "display": "0 9 * * *"
  },
  "skills": ["ai-funding-daily-report"],
  "deliver": "telegram:-1001234567890",
  "repeat": {
    "times": null,
    "completed": 42
  },
  "state": "scheduled",
  "enabled": true,
  "next_run_at": "2025-01-16T09:00:00Z",
  "last_run_at": "2025-01-15T09:00:00Z",
  "last_status": "ok",
  "created_at": "2025-01-01T00:00:00Z",
  "model": null,
  "provider": null,
  "script": null
}
```

### 任务生命周期状态

| 状态 | 含义 |
|------|------|
| `scheduled` | 激活状态，将在下次计划时间触发 |
| `paused` | 暂停状态——恢复前不会触发 |
| `completed` | 重复次数耗尽，或单次任务已触发 |
| `running` | 正在执行（瞬态状态） |

### 向后兼容性

旧任务可能有一个单独的 `skill` 字段而非 `skills` 数组。调度器在加载时会规范化——将单个 `skill` 提升为 `skills: [skill]`。

## 调度器运行时

### 滴答周期

调度器按周期性滴答运行（默认：每 60 秒）：

```text
tick()
  1. 获取调度器锁（防止重叠滴答）
  2. 从 jobs.json 加载所有任务
  3. 筛选到期任务（next_run <= 当前时间 且 state == "scheduled"）
  4. 对每个到期任务：
     a. 设置状态为 "running"
     b. 创建全新的 AIAgent 会话（无对话历史）
     c. 按顺序加载附加的技能（作为用户消息注入）
     d. 通过代理运行任务提示词
     e. 将响应投递到配置的目标
     f. 更新 run_count，计算下次执行时间
     g. 如果重复次数耗尽 → state = "completed"
     h. 否则 → state = "scheduled"
  5. 将更新后的任务写回 jobs.json
  6. 释放调度器锁
```

### 网关集成

在网关模式下，cron **触发器**（决定何时触发到期任务的部分——"轴 B"）通过可插拔的 `CronScheduler` 提供者选择。网关调用 `resolve_cron_scheduler()`（`cron/scheduler_provider.py`），并在专用后台线程中运行已解析提供者的 `start()`，同时还有一个独立的网关维护线程。

活动提供者由 `cron.provider` 配置键选择：

- **空（默认）** → 内置的 `InProcessCronScheduler`，运行传统进程内循环，每 60 秒调用 `scheduler.tick()`。这与提供者出现前的行为完全一致。
- **命名提供者**（例如 `chronos`，一种用于缩容至零部署的管理型 cron 提供者）→ 从 `plugins/cron/<name>/` 或 `$HERMES_HOME/plugins/<name>/` 发现。

如果命名提供者缺失、加载失败或报告 `is_available() == False`，解析器会回退到内置提供者并发出警告——**cron 绝不缺少触发器。**内置提供者位于核心代码（`cron/scheduler_provider.py`），而非 `plugins/` 中，因此无法被意外移除。

"触发"的含义（任务执行 + 投递）保持不变，且由所有提供者共享——它保留在 `scheduler.run_job()` / `scheduler._deliver_result()` 中。提供者仅控制触发器，不控制执行过程。

在 CLI 模式下，cron 任务仅在运行 `hermes cron` 命令或活跃的 CLI 会话期间触发。

### 用于缩容至零的管理型 cron (Chronos)

托管网关可以运行 **Chronos** 提供者（`cron.provider: chronos`）替代内置滴答器。Chronos 允许空闲网关**缩容至零**，同时仍然触发 cron 任务：它不会使用 60 秒进程内循环（这会保持进程唤醒），而是要求 Nous 基础设施为该任务的真实下次触发时间精确地布置**一个托管的一次性触发**。触发时，Nous 通过经过身份验证的 webhook（`POST /api/cron/fire`）回调网关；网关通过相同的 `run_one_job` 路径运行任务（与内置提供者相同），然后重新布置下一次一次性触发。在触发间隔期间，进程可以完全停止——仅在真正触发时唤醒，不会周期性定时唤醒。

流程（托管调度器由 Nous 提供；代理不持有调度器凭据）：

```
创建/更新 cron 任务
  → Chronos 要求 Nous 在任务的 next_run_at 布置一次性触发
      （使用代理现有的 Nous 令牌进行身份验证）
  → 触发时，Nous 调用网关：POST {callback_url}/api/cron/fire
      （使用 Nous 颁发的短期、特定用途的 JWT 进行身份验证）
  → 网关验证令牌，认领任务（使用存储的 compare-and-set 实现多副本部署的至多一次触发），运行任务，并重新布置下一次一次性触发
```

配置（全部非秘密；在托管代理上，Nous 在配置时设置这些）：

| 键 | 含义 |
|---|---|
| `cron.provider` | 设置为 `chronos` 以激活（空值 = 内置滴答器） |
| `cron.chronos.portal_url` | Nous 基础 URL（布置 + 触发令牌签发者） |
| `cron.chronos.callback_url` | 网关自身的公共基础 URL，用于接收传入触发 |
| `cron.chronos.expected_audience` | 此代理的触发令牌受众 |
| `cron.chronos.nas_jwks_url` | 用于验证传入触发令牌的密钥集 |

如果 Chronos 配置错误或代理未登录 Nous，`resolve_cron_scheduler()` 会回退到内置滴答器（记录警告）——cron 绝不丢失其触发器。重复任务在每次触发后重新布置；`repeat`-N 任务在次数耗尽时干净停止（不会遗留未触发的一次性任务）。完整的代理↔Nous 连线协议见 `docs/chronos-managed-cron-contract.md`。

### 全新会话隔离

每个 cron 任务在完全全新的代理会话中运行：

- 无先前运行的对话历史
- 无先前 cron 执行的记忆（除非持久化到内存/文件）
- 提示词必须自包含——cron 任务不能提出澄清问题
- `cronjob` 工具集被禁用（递归防护）

## 技能支持的任务

cron 任务可以通过 `skills` 字段附加一个或多个技能。执行时：

1. 按指定顺序加载技能
2. 每个技能的 SKILL.md 内容作为上下文注入
3. 任务的提示词作为任务指令附加
4. 代理处理组合的技能上下文 + 提示词

这允许重用经过测试的工作流，而无需将完整指令粘贴到 cron 提示词中。例如：

```
创建每日资金报告 → 附加 "ai-funding-daily-report" 技能
```

### 脚本支持的任务

任务还可以通过 `script` 字段附加一个 Python 脚本。脚本在代理每次轮次*之前*运行，其标准输出作为上下文注入到提示词中。这支持数据收集和变更检测模式：

```python
# ~/.hermes/scripts/check_competitors.py
import requests, json
# 获取竞争对手发布说明，与上次运行进行比较
# 将摘要打印到标准输出——代理分析并报告
```

脚本超时默认 120 秒。`_get_script_timeout()` 通过三层链解析限制：

1. **模块级覆盖**——`_SCRIPT_TIMEOUT`（用于测试/猴子补丁）。仅在不同于默认值时使用。
2. **环境变量**——`HERMES_CRON_SCRIPT_TIMEOUT`
3. **配置**——`cron.script_timeout_seconds` 在 `config.yaml` 中（通过 `load_config()` 读取）
4. **默认值**——120 秒

### 提供者恢复

`run_job()` 将用户配置的回退提供者和凭据池传递给 `AIAgent` 实例：

- **回退提供者**——从 `config.yaml` 读取 `fallback_providers`（列表）或 `fallback_model`（旧版字典），匹配网关的 `_load_fallback_model()` 模式。作为 `fallback_model=` 传递给 `AIAgent.__init__`，后者将两种格式规范化为回退链。
- **凭据池**——通过 `load_pool(provider)` 从 `agent.credential_pool` 加载，使用解析的运行时提供者名称。仅在池中有凭据时传递（`pool.has_credentials()`）。在 429/限速错误时启用同一提供者的密钥轮换。

这模仿了网关的行为——没有它，cron 代理会在遇到限速时而不尝试恢复就失败。

## 投递模型

Cron 任务结果可以投递到任何支持的平台：

| 目标 | 语法 | 示例 |
|------|------|------|
| 原始聊天 | `origin` | 投递到创建该任务的聊天 |
| 本地文件 | `local` | 保存到 `~/.hermes/cron/output/` |
| Telegram | `telegram` 或 `telegram:<chat_id>` | `telegram:-1001234567890` |
| Discord | `discord` 或 `discord:#channel` | `discord:#engineering` |
| Slack | `slack` | 投递到 Slack 首页频道 |
| WhatsApp | `whatsapp` | 投递到 WhatsApp 首页 |
| Signal | `signal` | 投递到 Signal |
| Matrix | `matrix` | 投递到 Matrix 首页房间 |
| Mattermost | `mattermost` | 投递到 Mattermost 首页 |
| Email | `email` | 通过邮件投递 |
| SMS | `sms` | 通过短信投递 |
| Home Assistant | `homeassistant` | 投递到 HA 对话 |
| DingTalk | `dingtalk` | 投递到钉钉 |
| Feishu | `feishu` | 投递到飞书 |
| WeCom | `wecom` | 投递到企业微信 |
| Weixin | `weixin` | 投递到微信 |
| BlueBubbles | `bluebubbles` | 通过 BlueBubbles 投递到 iMessage |
| QQ Bot | `qqbot` | 通过官方 API v2 投递到 QQ |

对于 Telegram 话题，使用格式 `telegram:<chat_id>:<thread_id>`（例如，`telegram:-1001234567890:17585`）。

### 响应包装

默认情况下（`cron.wrap_response: true`），cron 投递会被包装为：
- 头部标识 cron 任务名称和任务描述
- 尾部提示代理无法在对话中看到已投递的消息

cron 响应中的 `[SILENT]` 前缀会完全抑制投递——对于仅需要写入文件或执行副作用的任务很有用。

### 会话隔离

cron 投递**不会**镜像到网关会话的对话历史中。它们仅存在于 cron 任务自身的会话中。这防止了目标聊天对话中的消息交替违规。

## 递归防护

Cron 运行的会话禁用了 `cronjob` 工具集。这防止了：
- 计划任务创建新的 cron 任务
- 可能导致令牌使用量暴增的递归调度
- 从任务内部意外修改任务调度

## 锁定

调度器使用跨进程的基于文件的锁定（Unix 上为 `fcntl.flock`，Windows 上为 `msvcrt.locking`）以防止重叠滴答重复执行同一批到期任务——即使在网关的进程内滴答器和独立的 `hermes cron` / 手动 `tick()` 调用之间也是如此。如果无法获取锁，`tick()` 会立即返回 0。

## CLI 接口

`hermes cron` CLI 提供直接的任务管理：

```bash
hermes cron list                    # 显示所有任务
hermes cron create                  # 交互式创建任务（别名：add）
hermes cron edit <job_id>           # 编辑任务配置
hermes cron pause <job_id>          # 暂停运行中的任务
hermes cron resume <job_id>         # 恢复暂停的任务
hermes cron run <job_id>            # 立即触发执行
hermes cron remove <job_id>         # 删除任务
```

## 相关文档

- [Cron 功能指南](/user-guide/features/cron)
- [网关内部机制](./gateway-internals.md)
- [代理循环内部机制](./agent-loop.md)