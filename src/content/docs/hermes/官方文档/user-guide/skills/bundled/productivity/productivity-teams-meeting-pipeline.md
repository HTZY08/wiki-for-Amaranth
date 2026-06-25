--- frontmatter ---
---
title: "Teams 会议流水线"
sidebar_label: "Teams 会议流水线"
description: "通过 Hermes CLI 操作 Teams 会议摘要流水线 — 汇总会议、检查流水线状态、重放任务、管理 Microsoft Graph 订阅"
---

--- body ---
{/* 此页面由 website/scripts/generate-skill-docs.py 从技能（Skill）的 SKILL.md 自动生成。请编辑源 SKILL.md，而非此页面。 */}

# Teams 会议流水线

通过 Hermes CLI 操作 Teams 会议摘要流水线 — 汇总会议、检查流水线状态、重放任务、管理 Microsoft Graph 订阅。

## 技能（Skill）元数据

| | |
|---|---|
| 来源 | 捆绑（默认安装） |
| 路径 | `skills/productivity/teams-meeting-pipeline` |
| 版本 | `1.1.0` |
| 作者 | Hermes 代理（Agent）+ Teknium |
| 许可证 | MIT |
| 标签 | `Teams`、`Microsoft Graph`、`Meetings`、`Productivity`、`Operations` |

## 参考：完整 SKILL.md

:::info
以下为当此技能（Skill）被触发时 Hermes 加载的完整技能定义。此即该技能激活时代理（Agent）所看到的指令。
:::

# Teams 会议流水线

当用户询问关于 Microsoft Teams 会议摘要、转录、录制、行动项、Graph 订阅或任何与 Teams 会议流水线相关的操作问题时，请使用此技能。支持任何语言 — 以下触发词仅为示例，并非完整列表。

所有面向运维人员的操作均通过终端工具运行 `hermes teams-pipeline` 子命令完成。此流水线无需新增模型工具 — CLI 即为操作界面。

## 何时使用此技能

用户在请求：
- 汇总 Teams 会议 / 提取行动项 / 获取会议笔记
- 检查流水线状态、查看已存储的会议任务或最近会议
- 重放 / 重新运行已失败或需新摘要的已存储任务
- 更改环境或配置后验证 Microsoft Graph 设置
- 排查“会议摘要未到达”或“无新会议摄入”问题
- 管理 Graph Webhook 订阅（创建、续期、删除、检查）
- 设置自动订阅续期（参见下方陷阱）

多语言触发词示例（非完整）：
- 英语："summarize the Teams meeting"、"pipeline status"、"replay job X"
- 土耳其语："Teams meeting özetle"、"action item çıkar"、"toplantı notu"、"pipeline durumu"、"replay job"

## 前提条件

使用流水线前，请验证 `${HERMES_HOME:-~/.hermes}/.env` 中已设置以下内容：

```bash
MSGRAPH_TENANT_ID=...
MSGRAPH_CLIENT_ID=...
MSGRAPH_CLIENT_SECRET=...
```

若有缺失，请引导用户参考 Azure 应用注册指南（`/docs/guides/microsoft-graph-app-registration`）—— 他们需要创建一个已获取管理员同意的 Graph 应用程序权限的 Azure AD 应用注册，流水线才能正常工作。

## 命令参考

### 状态与检查（从此处开始）

```bash
hermes teams-pipeline validate              # 配置快照 — 任何更改后首先运行
hermes teams-pipeline token-health          # Graph 令牌状态
hermes teams-pipeline token-health --force-refresh   # 强制获取新令牌
hermes teams-pipeline list                  # 最近的会议任务
hermes teams-pipeline list --status failed  # 仅失败的任务
hermes teams-pipeline show <job-id>         # 单个任务的完整详情
hermes teams-pipeline subscriptions         # 当前 Graph Webhook 订阅
```

### 重放 / 调试

```bash
hermes teams-pipeline run <job-id>          # 重放已存储任务（重新摘要、重新投递）
hermes teams-pipeline fetch --meeting-id <id>   # 试运行：解析会议 + 转录但不持久化
hermes teams-pipeline fetch --join-web-url "<url>"   # 通过加入 URL 试运行
```

### 订阅管理

```bash
hermes teams-pipeline subscribe \
  --resource communications/onlineMeetings/getAllTranscripts \
  --notification-url https://<your-public-host>/msgraph/webhook \
  --client-state "$MSGRAPH_WEBHOOK_CLIENT_STATE"

hermes teams-pipeline renew-subscription <sub-id> --expiration <iso-8601>
hermes teams-pipeline delete-subscription <sub-id>
hermes teams-pipeline maintain-subscriptions            # 续期即将过期的订阅
hermes teams-pipeline maintain-subscriptions --dry-run  # 显示将被续期的订阅
```

## 常见问题的决策树

- 用户问“为何今天会议的摘要未到达？”→ 先运行 `list --status failed`，然后对相关行执行 `show <job-id>`。若任务根本不存在，检查 `subscriptions`——Webhook 可能已过期（见下方陷阱）。
- 用户问“设置是否正常？”→ 运行 `validate`，然后 `token-health`，再 `subscriptions`。若三者均通过，请求一个测试会议并检查 `list` 中是否有新行。
- 用户问“重新运行会议 X 的摘要”→ 通过 `list` 查找任务 ID，然后 `run <job-id>` 重放。若再次失败，用 `show <job-id>` 检查错误，并用 `fetch --meeting-id` 试运行工件解析。
- 用户问“将会议 X 添加到流水线”→ 通常不需要 —— 流水线由订阅驱动，而非按会议配置。若他们希望对某个特定历史会议进行摘要，可使用 `fetch` 拉取转录，然后在任务创建后使用 `run`。

## 关键陷阱：Graph 订阅 72 小时过期

Microsoft Graph 将 Webhook 订阅上限设为 72 小时，且**不会自动续期**。若未安排 `maintain-subscriptions`，则在手动创建订阅 3 天后，会议通知将静默停止到达。

当用户反馈“流水线昨天还能用，但今天什么也没收到”时：
1. 运行 `hermes teams-pipeline subscriptions` —— 若为空或所有条目 `expirationDateTime` 均为过去时间，则为原因。
2. 按上方所示使用 `subscribe` 重新创建。
3. **立即通过** `hermes cron add`、systemd 定时器或普通 crontab 设置自动续期。运维手册 `/docs/guides/operate-teams-meeting-pipeline#automating-subscription-renewal-required-for-production` 提供了全部三种方式。12 小时间隔是安全的（72 小时限制下留有 6 倍余量）。

## 其他陷阱

- **转录尚未就绪。** Teams 在会议结束后需要一些时间生成转录工件。对刚结束的会议执行 `fetch --meeting-id` 可能返回空结果。等待 2-5 分钟后重试，或让 Graph Webhook 自然驱动摄入。
- **投递模式不匹配。** 若摘要已生成（`list` 显示成功）但未出现在 Teams 中，请检查 `platforms.teams.extra.delivery_mode` 及对应的目标配置（`incoming_webhook_url` 或 `chat_id` 或 `team_id`+`channel_id`）。写入器会从 config.yaml 或 `TEAMS_*` 环境变量中读取这些内容。
- **Graph 应用权限。** 令牌获取正常（`token-health` 通过），但 Graph API 调用返回 401/403 —— 可能是因为权限已添加但未重新授予管理员同意。请用户重新访问 Azure 门户中的应用注册，并再次点击“授予管理员同意”。

## 相关文档

当用户需要比此技能（Skill）更深入的信息时，请引导其参考以下文档：
- Azure 应用注册指南：`/docs/guides/microsoft-graph-app-registration`
- 完整流水线设置：`/docs/user-guide/messaging/teams-meetings`
- 运维手册（续期自动化、故障排查、上线检查清单）：`/docs/guides/operate-teams-meeting-pipeline`
- Webhook 监听器设置：`/docs/user-guide/messaging/msgraph-webhook`