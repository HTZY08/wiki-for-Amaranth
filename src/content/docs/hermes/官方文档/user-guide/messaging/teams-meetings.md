---
sidebar_position: 6
title: "Teams 会议"
description: "使用 Microsoft Graph webhooks 设置 Microsoft Teams 会议摘要管道"
---

# Microsoft Teams 会议

当您希望 Hermes 摄取 Microsoft Graph 会议事件时，请使用 Teams 会议管道：首先获取转录（transcript），必要时回退到录像（recording）加语音转文字（STT），并将结构化摘要传递给下游接收端。

前置条件：参见 [Microsoft Teams](./teams.md) 了解底层机器人/凭据设置。

> 运行 `hermes gateway setup` 并选择 **Teams Meetings** 以获得引导式体验。

本页面聚焦于设置和启用：
- Graph 凭据
- webhook 监听器配置
- Teams 交付模式
- 管道配置结构

关于第 2 天操作、上线检查以及操作员工作表，请使用专门指南：[操作 Teams 会议管道](/guides/operate-teams-meeting-pipeline)。

## 此功能的作用

管道将：
1. 接收 Microsoft Graph webhook 事件
2. 解析会议并优先使用转录（transcript）制品
3. 当没有可用转录时，回退到下载录像并执行语音转文字（STT）
4. 在本地存储持久的任务状态和接收端记录
5. 可以将摘要写入 Notion、Linear 和 Microsoft Teams

操作员操作保持在 CLI 中（`teams-pipeline` 子命令由 `teams_pipeline` 插件注册 — 通过 `hermes plugins enable teams_pipeline` 启用，或在 `config.yaml` 中设置 `plugins.enabled: [teams_pipeline]`）：

```bash
hermes teams-pipeline validate
hermes teams-pipeline list
hermes teams-pipeline maintain-subscriptions
```

## 前置条件

在启用会议管道之前，请确保您已具备：

- 正常运行的 Hermes 安装
- 现有的 [Microsoft Teams 机器人设置](/user-guide/messaging/teams)（如果您需要 Teams 出站交付）
- Microsoft Graph 应用程序凭据，并拥有订阅会议资源所需的权限
- 一个可以让 Microsoft Graph 调用以进行 webhook 交付的公共 HTTPS URL
- 如果使用录像加语音转文字回退，则需要安装 `ffmpeg`

## 步骤 1：添加 Microsoft Graph 凭据

将 Graph 仅应用凭据添加到 `~/.hermes/.env`：

```bash
MSGRAPH_TENANT_ID=<租户ID>
MSGRAPH_CLIENT_ID=<客户端ID>
MSGRAPH_CLIENT_SECRET=<客户端密钥>
```

这些凭据用于：
- Graph 客户端基础
- 订阅维护命令
- 会议解析和制品获取
- 基于 Graph 的 Teams 出站交付（当您未提供专用的 Teams 访问令牌时）

## 步骤 2：启用 Graph Webhook 监听器

webhook 监听器是一个名为 `msgraph_webhook` 的网关平台。至少启用它并设置一个客户端状态值：

```bash
MSGRAPH_WEBHOOK_ENABLED=true
MSGRAPH_WEBHOOK_HOST=127.0.0.1
MSGRAPH_WEBHOOK_PORT=8646
MSGRAPH_WEBHOOK_CLIENT_STATE=<随机共享密钥>
MSGRAPH_WEBHOOK_ACCEPTED_RESOURCES=communications/onlineMeetings
```

监听器暴露以下端点：
- `/msgraph/webhook` 用于接收 Graph 通知
- `/health` 用于简单的健康检查

您需要将公共 HTTPS 端点路由到该监听器。例如，如果您的公共域是 `https://ops.example.com`，您的 Graph 通知 URL 通常为：

```text
https://ops.example.com/msgraph/webhook
```

## 步骤 3：配置 Teams 交付和管道行为

会议管道从现有的 `teams` 平台条目中读取其运行时配置。管道特定的旋钮位于 `teams.extra.meeting_pipeline` 下。Teams 出站交付保持在正常的 Teams 平台配置表面上。

示例 `~/.hermes/config.yaml`：

```yaml
platforms:
  msgraph_webhook:
    enabled: true
    extra:
      host: 127.0.0.1
      port: 8646
      client_state: "replace-me"
      accepted_resources:
        - "communications/onlineMeetings"

  teams:
    enabled: true
    extra:
      client_id: "your-teams-client-id"
      client_secret: "your-teams-client-secret"
      tenant_id: "your-teams-tenant-id"

      # 出站摘要交付
      delivery_mode: "graph" # 或 incoming_webhook
      team_id: "team-id"
      channel_id: "channel-id"
      # incoming_webhook_url: "https://..."

      meeting_pipeline:
        transcript_min_chars: 80
        transcript_required: false
        transcription_fallback: true
        ffmpeg_extract_audio: true
        notion:
          enabled: false
        linear:
          enabled: false
```

如果将监听器绑定到非回环主机（例如 `0.0.0.0`），则还必须设置 `allowed_source_cidrs` 为 Microsoft 的 webhook 出口范围。回环绑定（`127.0.0.1` / `::1`）适用于开发隧道和本地反向代理设置。

## Teams 交付模式

管道在现有 Teams 插件内支持两种 Teams 摘要交付模式。

### `incoming_webhook`

当您希望通过简单的 webhook 发布到 Teams，而不通过 Graph 创建频道消息时，使用此模式。

所需配置：

```yaml
platforms:
  teams:
    enabled: true
    extra:
      delivery_mode: "incoming_webhook"
      incoming_webhook_url: "https://..."
```

### `graph`

当您希望 Hermes 通过 Microsoft Graph 将摘要发布到 Teams 聊天或频道时，使用此模式。

支持的目标：
- `chat_id`
- `team_id` + `channel_id`
- `team_id` + `home_channel` 作为现有 Teams 平台的回退

示例：

```yaml
platforms:
  teams:
    enabled: true
    extra:
      delivery_mode: "graph"
      team_id: "team-id"
      channel_id: "channel-id"
```

## 步骤 4：启动网关

更新配置后正常启动 Hermes：

```bash
hermes gateway run
```

或者，如果您在 Docker 中运行 Hermes，请以与部署相同的方式启动网关。

检查监听器：

```bash
curl http://localhost:8646/health
```

## 步骤 5：创建 Graph 订阅

使用插件 CLI 创建和检查订阅。

示例：

```bash
hermes teams-pipeline subscribe \
  --resource communications/onlineMeetings/getAllTranscripts \
  --notification-url https://ops.example.com/msgraph/webhook \
  --client-state "$MSGRAPH_WEBHOOK_CLIENT_STATE"

hermes teams-pipeline subscribe \
  --resource communications/onlineMeetings/getAllRecordings \
  --notification-url https://ops.example.com/msgraph/webhook \
  --client-state "$MSGRAPH_WEBHOOK_CLIENT_STATE"
```

:::warning Graph 订阅在 72 小时后过期

Microsoft Graph 将 webhook 订阅限制为 72 小时，并且不会自动续订。您必须在投产前安排 `hermes teams-pipeline maintain-subscriptions`，否则在手动创建订阅三天后，通知将静默停止。有关三个选项（Hermes cron、systemd 定时器、纯 crontab），请参见操作员手册中的[自动化订阅续订](/guides/operate-teams-meeting-pipeline#automating-subscription-renewal-required-for-production)。

:::

有关订阅维护和第 2 天操作员流程，请继续阅读指南：[操作 Teams 会议管道](/guides/operate-teams-meeting-pipeline)。

## 验证

运行内置的验证快照：

```bash
hermes teams-pipeline validate
```

有用的辅助检查：

```bash
hermes teams-pipeline token-health
hermes teams-pipeline subscriptions
```

## 故障排除

| 问题 | 检查内容 |
|---------|---------------|
| Graph webhook 验证失败 | 确认公共 URL 正确且可达，并且 Graph 调用的是确切的 `/msgraph/webhook` 路径 |
| `hermes teams-pipeline list` 中未显示任务 | 确认 `msgraph_webhook` 已启用，并且订阅指向正确的通知 URL |
| 优先转录始终失败 | 检查 Transcript 资源的 Graph 权限，以及该会议的 Transcript 制品是否存在 |
| 录像回退失败 | 确认已安装 `ffmpeg`，且 Graph 应用可以访问录像制品 |
| Teams 摘要交付失败 | 重新检查 `delivery_mode`、目标 ID 和 Teams 认证配置 |

## 相关文档

- [Microsoft Teams 机器人设置](/user-guide/messaging/teams)
- [操作 Teams 会议管道](/guides/operate-teams-meeting-pipeline)