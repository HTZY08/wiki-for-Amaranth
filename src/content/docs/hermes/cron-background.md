---
title: 定时任务与后台
description: Cron 调度与长任务后台执行机制
---

Hermes Agent 内置 cron 调度系统，支持定时任务、周期性执行和长任务后台化。

## Cron 任务管理

通过 `cronjob` 工具管理：

```bash
# 创建定时任务（每 30 分钟）
cronjob action=create schedule='30m' prompt='检查系统状态'

# 创建每日简报（9:00）
cronjob action=create schedule='0 9 * * *' prompt='生成今日简报'

# 列出全部任务
cronjob action=list

# 暂停/恢复/删除
cronjob action=pause job_id=<id>
cronjob action=resume job_id=<id>
cronjob action=remove job_id=<id>
```

### 调度格式

| 格式 | 示例 | 含义 |
|------|------|------|
| 自然语言 | `30m`, `every 2h` | 每 30 分钟 / 每 2 小时 |
| Cron 表达式 | `0 9 * * *` | 每天 9:00 |
| ISO 时间戳 | `2026-06-01T09:00:00` | 单次执行 |

### 无 Agent 模式

纯脚本定时执行，不启动 LLM 推理，适合监控和告警：

```bash
cronjob action=create schedule='5m' script=/path/to/check.sh no_agent=true
```

## 长任务后台化

耗时任务自动转入后台，释放前台会话：

```
用户发送长任务（如批量处理、模型训练、全量扫描）
    │
    ├── 自动判断：是否适合后台？
    │   ├── 是 → /background 后台执行
    │   └── 否 → 前台同步执行
    │
    ├── 后台任务完成后自动通知
    └── 用户可随时插话，不影响后台
```

触发条件：
- 用户明确要求后台（"慢慢跑"、"跑完告诉我"）
- 任务本质是批量/训练/全量扫描/构建部署
- 工具调用链天然漫长

不触发条件：
- 概念问答（"什么是 X"）
- 只写不执行（"给我命令"）
- 要求同步完成（"现在做"）

## 使用场景

| 场景 | 实现方式 |
|------|----------|
| 每日 AI+政经简报 | cronjob，加载 `daily-briefing` skill |
| RSS 监控 | cronjob，配合 blogwatcher |
| 系统健康检查 | cronjob no_agent 脚本模式 |
| 知识库同步 | 后台长任务 |
