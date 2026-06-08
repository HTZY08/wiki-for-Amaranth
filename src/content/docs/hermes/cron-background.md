---
title: 定时任务
description: 设置自动任务——每天定时执行，无需手动触发
---

Hermes 内置定时任务系统，可以设定在指定时间自动执行任务，比如每天早上推送新闻摘要。

---

## 创建定时任务

### 最简单的例子

每 30 分钟检查一次系统状态：

```bash
hermes cron create --schedule "30m" --prompt "检查系统运行状态"
```

### 自然语言格式

```bash
# 每 30 分钟
hermes cron create --schedule "30m" --prompt "..."

# 每 2 小时
hermes cron create --schedule "every 2h" --prompt "..."

# 每天 9:00
hermes cron create --schedule "0 9 * * *" --prompt "..."

# 每周一 9:00
hermes cron create --schedule "0 9 * * 1" --prompt "..."

# 指定日期执行一次
hermes cron create --schedule "2026-12-31T23:59:00" --prompt "..."
```

> `0 9 * * *` 是 cron 表达式格式，依次代表：分钟 小时 日 月 星期

## 实用案例

### 每日新闻简报

```bash
hermes cron create \
  --schedule "0 8 * * *" \
  --prompt "收集今天的科技新闻和行业动态，整理成简短的摘要" \
  --skill daily-briefing
```

### RSS 订阅监控

```bash
hermes cron create \
  --schedule "30m" \
  --prompt "检查我订阅的 RSS 有没有新文章，有的话列出标题和链接" \
  --skill blogwatcher
```

### 系统健康检查

```bash
hermes cron create \
  --schedule "0 * * * *" \
  --prompt "检查 Docker 容器状态、磁盘空间、内存使用，异常时告警"
```

## 管理定时任务

```bash
# 列出所有任务
hermes cron list

# 暂停某个任务
hermes cron pause <任务ID>

# 恢复暂停的任务
hermes cron resume <任务ID>

# 手动立即执行一次
hermes cron run <任务ID>

# 删除任务
hermes cron remove <任务ID>
```

## 无 Agent 模式（纯脚本）

对于不需要 AI 推理的监控任务，可以用脚本模式，节省 API 调用费用：

```bash
hermes cron create \
  --schedule "5m" \
  --script /path/to/check.sh \
  --no-agent
```

脚本的输出会直接作为消息发送，适合：
- 磁盘空间监控
- GPU 温度告警
- 网络连通性检查
- 进程存活检测

## 后台执行

当 Hermes 在执行一个耗时任务时（比如批量处理文件、模型训练），会自动转入后台执行，你可以继续聊天：

```
你：帮我下载这 100 张图片并压缩
Hermes：任务已转后台执行，完成后通知你，请继续其他操作
```

## 注意事项

- 定时任务的 prompt 要**自包含**——任务执行时没有上下文，不能依赖之前的对话
- 任务输出会自动发回给你的聊天窗口
- 不要创建递归的定时任务（定时任务中不要再创建定时任务）
