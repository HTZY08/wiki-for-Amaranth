--- frontmatter ---
---
title: "操作 Teams 会议管道"
description: "Microsoft Teams 会议管道的操作手册、上线检查清单和运维人员工作表"
---

--- body ---
# 操作 Teams 会议管道

在已从 [Teams 会议](/user-guide/messaging/teams-meetings) 启用该功能后，请使用本指南。

本页内容涵盖：
- 操作者 CLI 流程
- 例行订阅维护
- 故障排查
- 上线检查
- 部署工作表

## 核心操作命令

### 验证配置快照

```bash
hermes teams-pipeline validate
```

在对配置进行任何更改后，首先运行此命令。

### 检查令牌健康状态

```bash
hermes teams-pipeline token-health
hermes teams-pipeline token-health --force-refresh
```

当怀疑认证状态过时时，使用 `--force-refresh`。

### 检查订阅

```bash
hermes teams-pipeline subscriptions
```

### 续订即将过期的订阅

```bash
hermes teams-pipeline maintain-subscriptions
hermes teams-pipeline maintain-subscriptions --dry-run
```

### 自动化订阅续订（生产环境必需）

**Microsoft Graph 订阅最长在 72 小时内过期。** 如果没有续订机制，会议通知将在 3 天后静默停止，管道看起来会“损坏”。这是任何基于 Graph 集成的首要操作失败模式。

您必须按计划运行 `maintain-subscriptions`。从以下三个选项中选择一个：

#### 选项 1：Hermes cron（如果已运行 Hermes 网关，推荐使用）

Hermes 内置了 cron 调度器。`--no-agent` 模式将脚本作为任务运行（而非使用 LLM），并且 `--script` 必须指向 `~/.hermes/scripts/` 下的文件。首先创建脚本：

```bash
mkdir -p ~/.hermes/scripts
cat > ~/.hermes/scripts/maintain-teams-subscriptions.sh <<'EOF'
#!/usr/bin/env bash
exec hermes teams-pipeline maintain-subscriptions
EOF
chmod +x ~/.hermes/scripts/maintain-teams-subscriptions.sh
```

然后注册一个每 12 小时运行一次的纯脚本 cron 任务（为 72 小时过期窗口提供 6 倍余量）：

```bash
hermes cron create "0 */12 * * *" \
  --name "teams-pipeline-maintain-subscriptions" \
  --no-agent \
  --script maintain-teams-subscriptions.sh \
  --deliver local
```

验证任务已注册并检查下次运行时间：

```bash
hermes cron list
hermes cron status        # 调度器状态
```

#### 选项 2：systemd 定时器（推荐用于 Linux 生产部署）

创建 `/etc/systemd/system/hermes-teams-pipeline-maintain.service`：

```ini
[Unit]
Description=Hermes Teams 管道订阅维护
After=network-online.target

[Service]
Type=oneshot
User=hermes
EnvironmentFile=/etc/hermes/env
ExecStart=/usr/local/bin/hermes teams-pipeline maintain-subscriptions
```

以及 `/etc/systemd/system/hermes-teams-pipeline-maintain.timer`：

```ini
[Unit]
Description=每 12 小时运行 Hermes Teams 管道订阅维护

[Timer]
OnBootSec=5min
OnUnitActiveSec=12h
Persistent=true

[Install]
WantedBy=timers.target
```

启用：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now hermes-teams-pipeline-maintain.timer
systemctl list-timers hermes-teams-pipeline-maintain.timer
```

#### 选项 3：纯 crontab

```cron
0 */12 * * * /usr/local/bin/hermes teams-pipeline maintain-subscriptions >> /var/log/hermes/teams-pipeline-maintain.log 2>&1
```

确保 cron 环境包含 `MSGRAPH_*` 凭据。最简单的修复方法：在 crontab 调用的包装脚本顶部 source `~/.hermes/.env`。

#### 验证续订是否正常工作

设置好计划后，在第一次计划运行后检查续订活动：

```bash
hermes teams-pipeline subscriptions   # 应显示 expirationDateTime 已推进
hermes teams-pipeline maintain-subscriptions --dry-run   # 多数情况下应显示 "0 expiring soon"
```

如果您发现 Graph webhook 在大约 72 小时后神秘地“停止工作”，首先要检查的是：续订任务是否真的运行了？

### 检查最近的任务

```bash
hermes teams-pipeline list
hermes teams-pipeline list --status failed
hermes teams-pipeline show <job-id>
```

### 重放已存储的任务

```bash
hermes teams-pipeline run <job-id>
```

### 模拟会议工件抓取

```bash
hermes teams-pipeline fetch --meeting-id <meeting-id>
hermes teams-pipeline fetch --join-web-url "<join-url>"
```

## 例行操作手册

### 首次设置后

按顺序运行这些命令：

```bash
hermes teams-pipeline validate
hermes teams-pipeline token-health --force-refresh
hermes teams-pipeline subscriptions
```

然后触发或等待一个真实的会议事件，并确认：

```bash
hermes teams-pipeline list
hermes teams-pipeline show <job-id>
```

### 日常或定期检查

- 运行 `hermes teams-pipeline maintain-subscriptions --dry-run`
- 检查 `hermes teams-pipeline list --status failed`
- 验证 Teams 投递目标是否仍是正确的聊天或频道

### 在更改 webhook URL 或投递目标之前

- 更新公共通知 URL 或 Teams 目标配置
- 运行 `hermes teams-pipeline validate`
- 续订或重新创建受影响的订阅
- 确认新事件会到达预期接收端

## 故障排查

### 没有创建任何任务

检查：
- `msgraph_webhook` 已启用
- 公共通知 URL 指向 `/msgraph/webhook`
- 订阅中的客户端状态与 `MSGRAPH_WEBHOOK_CLIENT_STATE` 匹配
- 订阅在远程仍然存在且未过期

### 任务停留在重试状态或在汇总前失败

检查：
- 转录权限和可用性
- 录制权限和工件可用性
- 如果启用了录制回退，检查 `ffmpeg` 是否可用
- Graph 令牌健康状态

### 生成了摘要但未投递到 Teams

检查：
- `platforms.teams.enabled: true`
- `delivery_mode`
- webhook 模式下的 `incoming_webhook_url`
- Graph 模式下的 `chat_id` 或 `team_id` 加上 `channel_id`
- 如果使用 Graph 发布，检查 Teams 认证配置

### 重复或意外的重放

检查：
- 是否手动使用 `hermes teams-pipeline run` 重放了任务
- 该会议是否已经存在接收端记录
- 是否在本地配置中故意启用了重新发送路径

## 上线检查清单

- [ ] Graph 凭据存在且正确
- [ ] `msgraph_webhook` 已启用且可从公共互联网访问
- [ ] `MSGRAPH_WEBHOOK_CLIENT_STATE` 已设置并与订阅匹配
- [ ] 已创建转录订阅
- [ ] 如果需要进行 STT 回退，已创建录制订阅
- [ ] 如果启用了录制回退，已安装 `ffmpeg`
- [ ] Teams 出站投递目标已配置并验证
- [ ] 仅当实际需要时才配置 Notion 和 Linear 接收端
- [ ] `hermes teams-pipeline validate` 返回 OK 快照
- [ ] `hermes teams-pipeline token-health --force-refresh` 成功
- [ ] **`maintain-subscriptions` 已调度**（Hermes cron、systemd 定时器或 crontab——参见[自动化订阅续订](#automating-subscription-renewal-required-for-production)）。否则，Graph 订阅将在 72 小时内静默过期。
- [ ] 已通过真实端到端会议事件产生一个存储的任务
- [ ] 至少有一个摘要已送达预期的投递接收端

## 投递模式决策指南

| 模式 | 适用场景 | 权衡 |
|------|----------|---------|
| `incoming_webhook` | 仅需简单地将消息发布到 Teams | 设置最简单，控制较少 |
| `graph` | 需要通过 Graph 进行频道或聊天发布 | 控制更多，需要更多认证和目标配置 |

## 运维人员工作表

部署前填写此表：

| 项目 | 值 |
|------|-------|
| 公共通知 URL | |
| Graph 租户 ID | |
| Graph 客户端 ID | |
| Webhook 客户端状态 | |
| 转录资源订阅 | |
| 录制资源订阅 | |
| Teams 投递模式 | |
| Teams 聊天 ID 或团队/频道 | |
| Notion 数据库 ID | |
| Linear 团队 ID | |
| 存储路径覆盖（如有） | |
| 日常检查负责人 | |

## 变更审查工作表

更改部署前使用此表：

| 问题 | 答案 |
|----------|--------|
| 我们是否更改了公共 webhook URL？ | |
| 我们是否轮换了 Graph 凭据？ | |
| 我们是否更改了 Teams 投递模式？ | |
| 我们是否迁移到了新的 Teams 聊天或频道？ | |
| 订阅是否需要重新创建或续订？ | |
| 我们是否需要一次全新的端到端验证运行？ | |

## 相关文档

- [Teams 会议设置](/user-guide/messaging/teams-meetings)
- [Microsoft Teams 机器人设置](/user-guide/messaging/teams)