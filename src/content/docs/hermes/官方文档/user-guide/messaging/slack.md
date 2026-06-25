--- frontmatter ---
---

## 按频道提示（Per-Channel Prompts）

为特定 Slack 频道分配临时系统提示。该提示在每次对话回合时注入，不会持久化到对话历史中，因此更改会立即生效。

```yaml
slack:
  channel_prompts:
    "C01RESEARCH": |
      You are a research assistant. Focus on academic sources,
      citations, and concise synthesis.
    "C02ENGINEERING": |
      Code review mode. Be precise about edge cases and
      performance implications.
```

键值为 Slack 频道 ID（可通过频道详情 → "关于" → 滚动到底部找到）。所有在匹配频道中的消息都会获得该提示作为临时系统指令注入。

## 按频道技能绑定（Per-Channel Skill Bindings）

每当在特定频道或私信中开启新会话时，自动加载某个技能。与按频道提示（每次对话回合注入）不同，技能绑定会在**会话开始时**将技能内容作为用户消息注入——这部分内容会成为对话历史的一部分，后续回合无需重新加载。

这对于具有特定用途的私信或频道（如闪卡、领域特定问答机器人、支持分类频道等）非常理想，这些场景下你不想让模型自身的技能选择器决定是否在每个简短回复时加载技能。

```yaml
slack:
  channel_skill_bindings:
    # 私信频道（DM）——始终以"german-flashcards"模式运行
    - id: "D0ATH9TQ0G6"
      skills:
        - german-flashcards
    # 研究频道——按顺序预加载多个技能
    - id: "C01RESEARCH"
      skills:
        - arxiv
        - writing-plans
    # 简写形式：单个技能用字符串表示
    - id: "C02SUPPORT"
      skill: hubspot-on-demand
```

注意：
- 绑定通过频道 ID 匹配。对于绑定频道中的线程消息，线程继承父频道的绑定。
- 技能仅在会话开始时加载（新会话或自动重置后）。如果更改了绑定，请运行 `/new` 或等待会话自动重置以生效。
- 可与 `channel_prompts` 结合使用，在技能指令之上为频道设置语气/约束。

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 机器人不响应私信 | 确认 `message.im` 已在事件订阅中，并重新安装应用 |
| 机器人能在私信中工作，但无法在频道中工作 | **最常见问题。** 在事件订阅中添加 `message.channels` 和 `message.groups`，重新安装应用，并使用 `/invite @Hermes Agent` 邀请机器人到频道 |
| 机器人在频道中不响应 @提及 | 1) 检查是否订阅了 `message.channels` 事件。2) 必须邀请机器人到频道。3) 确保添加了 `channels:history` 范围。4) 在修改范围/事件后重新安装应用 |
| 机器人忽略私密频道中的消息 | 添加 `message.groups` 事件订阅和 `groups:history` 范围，然后重新安装应用并使用 `/invite` 邀请机器人 |
| 私信中显示"与此应用发送消息的功能已关闭" | 在应用主页设置中启用**消息选项卡**（见第5步） |
| 出现 "not_authed" 或 "invalid_auth" 错误 | 重新生成机器人令牌和应用令牌，更新 `.env` |
| 机器人能够响应但无法在频道中发帖 | 使用 `/invite @Hermes Agent` 邀请机器人到频道 |
| 机器人可以聊天但无法读取上传的图片/文件 | 添加 `files:read`，然后**重新安装**应用。Hermes 现在会在 Slack 返回范围/授权/权限失败时，在聊天界面显示附件访问诊断信息。 |
| 出现 `missing_scope` 错误 | 在 OAuth 与权限中添加所需范围，然后**重新安装**应用 |
| Socket 频繁断开 | 检查网络；Bolt 会自动重连，但不稳定的连接会导致延迟 |
| 更改了范围/事件但无变化 | 在修改范围或事件订阅后，**必须重新安装**应用到你的工作区 |

### 快速检查清单

如果机器人在频道中不工作，请验证以下**所有**项：

1. ✅ 已订阅 `message.channels` 事件（针对公开频道）
2. ✅ 已订阅 `message.groups` 事件（针对私密频道）
3. ✅ 已订阅 `app_mention` 事件
4. ✅ 已添加 `channels:history` 范围（针对公开频道）
5. ✅ 已添加 `groups:history` 范围（针对私密频道）
6. ✅ 在添加范围/事件后**重新安装**了应用
7. ✅ 已**邀请**机器人到频道（`/invite @Hermes Agent`）
8. ✅ 在消息中**@提及**了机器人

---

--- body ---
## 安全

:::warning
**始终设置 `SLACK_ALLOWED_USERS`**，填入授权用户的成员 ID。如果没有此设置，网关将默认**拒绝所有消息**作为安全措施。切勿分享你的机器人令牌——请像对待密码一样对待它们。
:::

- 令牌应存储在 `~/.hermes/.env` 中（文件权限设置为 `600`）
- 通过 Slack 应用设置定期轮换令牌
- 审计有权访问你的 Hermes 配置目录的人员
- Socket 模式意味着没有公开端点暴露——减少了一个攻击面