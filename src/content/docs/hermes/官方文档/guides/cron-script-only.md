---
title: "Cron Script Only"
---

--- body ---
# 仅脚本定时任务（无 LLM）

有时你已经确切知道要发送什么消息。你不需要代理（Agent）来推理——你只需要一个脚本按定时运行，并将其输出（如果有）发送到 Telegram / Discord / Slack / Signal。

Hermes 将此称为**无代理模式（no-agent mode）**。它是移除了 LLM 的定时任务系统。

```
   ┌──────────────────┐          ┌──────────────────┐
   │ 调度器触发       │  每隔    │ 运行脚本          │
   │ （每 N 分钟）    │ ──────▶ │ （bash 或 python）│
   └──────────────────┘          └──────────────────┘
                                          │
                                          │ stdout
                                          ▼
                                 ┌──────────────────┐
                                 │ 投递路由器       │
                                 │ (telegram/disc…) │
                                 └──────────────────┘
```

- **无 LLM 调用。** 零 Token，零代理循环，零模型消耗。
- **脚本即任务。** 脚本决定是否告警。输出内容 → 消息发送。无输出 → 静默触发。
- **Bash 或 Python。** `.sh` / `.bash` 文件在 `/bin/bash` 下运行；任何其他扩展名在当前 Python 解释器下运行。`~/.hermes/scripts/` 中的任何脚本都可接受。
- **相同调度器。** 与 LLM 任务一起存在于 `cronjob` 中——暂停、恢复、列出、日志和投递目标设置都相同。

## 何时使用

在以下场景使用无代理模式：

- **内存 / 磁盘 / GPU 看门狗。** 每 5 分钟运行一次，仅在阈值被突破时告警。
- **CI 钩子。** 部署完成 → 发布提交 SHA。构建失败 → 发送最后 100 行日志。
- **周期性指标。** “早上 9 点每日 Stripe 收入”作为简单的 API 调用 + 格式化输出。
- **外部事件轮询器。** 检查 API，在状态变化时告警。
- **心跳。** 每 N 分钟向仪表盘发送一次 ping，以证明主机存活。

当你需要代理（Agent）**决定**说什么时——比如总结长文档、从信息流中挑选有趣项目、起草友好提醒——则使用正常的（LLM 驱动的）定时任务。无代理路径适用于脚本的 stdout 本身已经是消息的情况。

## 通过对话创建

无代理模式的真正优势在于，代理本身可以为你设置看门狗——无需编辑器、无需 Shell、无需记住 CLI 标志。你描述需求，Hermes 编写脚本、调度它，并告知你何时触发。

### 示例对话记录

> **你：** 每 5 分钟在 Telegram 上 ping 我，如果 RAM 超过 85%
>
> **Hermes：** *（写入 `~/.hermes/scripts/memory-watchdog.sh`，然后调用 `cronjob(...)` 并设置 `no_agent=true`）*
>
> 设置完成。每 5 分钟运行一次，仅在 RAM 超过 85% 时通过 Telegram 告警。脚本：`memory-watchdog.sh`。任务 ID：`abc123`。

在底层，代理会进行两次工具调用：

```python
# 1. 编写检查脚本
write_file(
    path="~/.hermes/scripts/memory-watchdog.sh",
    content='''#!/usr/bin/env bash
ram_pct=$(free | awk '/^Mem:/ {printf "%d", $3 * 100 / $2}')
if [ "$ram_pct" -ge 85 ]; then
  echo "RAM ${ram_pct}% on $(hostname)"
fi
# 空的 stdout = 静默触发；不发送消息。
''',
)

# 2. 调度它——no_agent=True 跳过每次触发时的 LLM
cronjob(
    action="create",
    schedule="every 5m",
    script="memory-watchdog.sh",
    no_agent=True,
    deliver="telegram",
    name="memory-watchdog",
)
```

从那一刻起，每次触发都是免费的：调度器运行脚本，如果 stdout 非空则通过管道传递给 Telegram，且从不触及模型。

### 代理为你决定的内容

当你提出诸如“当 X 发生时提醒我”或“每 N 分钟检查 Y 并告诉我是否 Z”之类的请求时，Hermes 的 `cronjob` 工具描述会告诉它在消息内容完全由脚本确定时使用 `no_agent=True`。当请求需要推理（“总结新问题”、“挑选最有趣的标题”、“起草友好提醒”）时，它会回退到正常的 LLM 驱动路径。

你无需自己指定 `--no-agent`。只需描述行为即可。

### 通过对话管理看门狗

代理可以像创建任务一样暂停、恢复、编辑和删除任务：

> **你：** 今晚停止内存看门狗
>
> **Hermes：** *（调用 `cronjob(action='pause', job_id='abc123')`）*
>
> 已暂停。使用“重新打开”或通过 `hermes cron resume abc123` 恢复。

> **你：** 改为每 15 分钟
>
> **Hermes：** *（调用 `cronjob(action='update', job_id='abc123', schedule='every 15m')`）*

完整的生命周期（创建 / 列出 / 更新 / 暂停 / 恢复 / 立即运行 / 删除）都可供代理使用，你无需学习任何 CLI 命令。

## 通过 CLI 创建

更喜欢 Shell？CLI 路径通过三个命令也能得到相同结果：

```bash
# 1. 编写脚本
cat > ~/.hermes/scripts/memory-watchdog.sh <<'EOF'
#!/usr/bin/env bash
# 当 RAM 使用率超过 85% 时告警。否则静默。
RAM_PCT=$(free | awk '/^Mem:/ {printf "%d", $3 * 100 / $2}')
if [ "$RAM_PCT" -ge 85 ]; then
  echo "⚠ RAM ${RAM_PCT}% on $(hostname)"
fi
# 空的 stdout = 静默运行；不发送消息。
EOF
chmod +x ~/.hermes/scripts/memory-watchdog.sh

# 2. 调度它
hermes cron create "every 5m" \
  --no-agent \
  --script memory-watchdog.sh \
  --deliver telegram \
  --name "memory-watchdog"

# 3. 验证
hermes cron list
hermes cron run <job_id>    # 触发一次测试
```

就这样。无需提示、无需技能（Skill）、无需模型。

## 脚本输出如何映射到投递

| 脚本行为                          | 结果                           |
|----------------------------------|--------------------------------|
| 退出码 0，stdout 非空            | stdout 原样投递                |
| 退出码 0，stdout 为空            | 静默触发——不投递               |
| 退出码 0，stdout 最后一行包含 `{"wakeAgent": false}` | 静默触发（与 LLM 任务共享门控） |
| 非零退出码                        | 错误告警被投递（坏掉的看门狗不会静默失败） |
| 脚本超时                          | 错误告警被投递                 |

“静默当空”的行为是经典看门狗模式的关键：脚本可以每分钟运行，但通道只在需要关注的事情发生时才能看到消息。

## 脚本规则

脚本必须位于 `~/.hermes/scripts/` 中。这在任务创建时和运行时都会强制执行——绝对路径、`~/` 展开和路径遍历模式（`../`）都会被拒绝。该目录与 LLM 任务使用的预检查脚本门控共享。

解释器的选择依据文件扩展名：

| 扩展名        | 解释器                     |
|--------------|----------------------------|
| `.sh`, `.bash` | `/bin/bash`                |
| 其他任何扩展名  | `sys.executable`（当前 Python） |

我们故意不尊重 `#!/...` shebangs——保持解释器设置明确且范围较小，可减少调度器信任的攻击面。

## 调度语法

与所有其他定时任务相同：

```bash
hermes cron create "every 5m"        # 间隔
hermes cron create "every 2h"
hermes cron create "0 9 * * *"       # 标准 cron：每天上午 9 点
hermes cron create "30m"             # 一次性：30 分钟后运行一次
```

完整语法请参阅[定时任务功能参考](/user-guide/features/cron)。

## 投递目标

`--deliver` 接受网关（gateway）已知的所有目标。一些常见形式：

```bash
--deliver telegram                       # 平台主频道
--deliver telegram:-1001234567890        # 特定聊天
--deliver telegram:-1001234567890:17585  # 特定 Telegram 论坛话题
--deliver discord:#ops
--deliver slack:#engineering
--deliver signal:+15551234567
--deliver local                          # 仅保存到 ~/.hermes/cron/output/
```

对于机器人令牌平台（Telegram, Discord, Slack, Signal, SMS, WhatsApp），脚本运行时无需运行网关（gateway）——工具会使用 `~/.hermes/.env` / `~/.hermes/config.yaml` 中已有的凭据直接调用每个平台的 REST 端点。

## 编辑与生命周期

```bash
hermes cron list                                    # 查看所有任务
hermes cron pause <job_id>                          # 停止触发，保留定义
hermes cron resume <job_id>
hermes cron edit <job_id> --schedule "every 10m"    # 调整节奏
hermes cron edit <job_id> --agent                   # 切换到 LLM 模式
hermes cron edit <job_id> --no-agent --script …     # 切换回来
hermes cron remove <job_id>                         # 删除它
```

所有适用于 LLM 任务的操作（暂停、恢复、手动触发、更改投递目标）也适用于无代理任务。

## 完整示例：磁盘空间告警

```bash
cat > ~/.hermes/scripts/disk-alert.sh <<'EOF'
#!/usr/bin/env bash
# 当 / 或 /home 超过 90% 时告警。
THRESHOLD=90
df -h / /home 2>/dev/null | awk -v t="$THRESHOLD" '
  NR > 1 && $5+0 >= t {
    printf "⚠ 磁盘 %s 在 %s 上已满\n", $5, $6
  }
'
EOF
chmod +x ~/.hermes/scripts/disk-alert.sh

hermes cron create "*/15 * * * *" \
  --no-agent \
  --script disk-alert.sh \
  --deliver telegram \
  --name "disk-alert"
```

当两个文件系统都低于 90% 时静默；当其中一个文件系统满时，为每个超过阈值的文件系统触发一行告警。

## 与其他模式的比较

| 方法                              | 运行内容                     | 何时使用                                           |
|----------------------------------|-----------------------------|----------------------------------------------------|
| `cronjob --no-agent`（本页）       | 你的脚本按 Hermes 调度       | 不需要推理的周期性看门狗/告警/指标                  |
| `cronjob`（默认，LLM）            | 代理（Agent）带可选的预检查脚本 | 消息内容需要对数据进行推理时                        |
| 操作系统 cron + `curl` 到[网络钩子订阅](/user-guide/messaging/webhooks) | 你的脚本按操作系统调度       | 当 Hermes 可能不健康时（你正在监控的东西）          |

对于关键系统健康看门狗，必须在**网关（gateway）宕机时**也能触发，请使用操作系统级 cron 配合简单的 `curl` 调用 Hermes 网络钩子订阅（或任何外部告警端点）——这些作为独立的操作系统进程运行，不依赖 Hermes 是否运行。当被监控的东西是外部时，网关内调度器是正确的选择。

## 相关

- [使用 Cron 自动化一切](/guides/automate-with-cron) —— LLM 驱动的定时任务模式。
- [计划任务（Cron）参考](/user-guide/features/cron) —— 完整的调度语法、生命周期、投递路由。
- [网络钩子订阅](/user-guide/messaging/webhooks) —— 供外部调度器使用的即发即忘型 HTTP 入口点。
- [网关内部原理](/developer-guide/gateway-internals) —— 投递路由器内部机制。